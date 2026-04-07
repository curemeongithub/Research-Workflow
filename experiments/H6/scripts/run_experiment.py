"""
H6 Main Experiment: Elastic Net Breaks Convex Reformulation.

Runs the full experimental grid (lambda_ratios x seeds) computing:
- Convex L2 reformulation objective f_convex
- Non-convex elastic net objective f_elastic
- Normalized gap (f_elastic - f_convex) / f_elastic (primary)
- f_convex_elastic: convex-solution weights evaluated under elastic net objective
- gap_secondary: (f_convex_elastic - f_elastic) / f_elastic

Parallelizes over seeds per ratio using joblib.

Run from project root:
    .venv/bin/python experiments/H6/scripts/run_experiment.py \\
        --n 200 --d 10 \\
        --lambda_ratios 0,0.1,0.5,1.0,2.0,5.0 \\
        --lambda2 0.01 \\
        --seeds 20 \\
        --width 100 \\
        --restarts 50
"""
import argparse
import json
import csv
import time
import os
import sys
import traceback

import numpy as np
from joblib import Parallel, delayed

# Add scripts dir to path for local imports
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)


def parse_args():
    parser = argparse.ArgumentParser(
        description='H6: Elastic Net Breaks Convex Reformulation'
    )
    parser.add_argument('--n', type=int, default=200, help='Number of samples')
    parser.add_argument('--d', type=int, default=10, help='Input dimension')
    parser.add_argument(
        '--lambda_ratios', type=str, default='0,0.1,0.5,1.0,2.0,5.0',
        help='Comma-separated lambda_1/lambda_2 ratios'
    )
    parser.add_argument('--lambda2', type=float, default=0.01,
                        help='L2 regularization strength')
    parser.add_argument('--seeds', type=int, default=20,
                        help='Number of random seeds')
    parser.add_argument('--width', type=int, default=100,
                        help='Hidden layer width')
    parser.add_argument('--restarts', type=int, default=50,
                        help='Non-convex restarts per config')
    parser.add_argument('--epochs', type=int, default=3000,
                        help='Training epochs per restart')
    parser.add_argument('--lr', type=float, default=0.001,
                        help='Adam learning rate')
    parser.add_argument('--max_patterns', type=int, default=200,
                        help='Max hyperplane patterns for convex solver')
    parser.add_argument('--n_jobs', type=int, default=-1,
                        help='Parallel jobs (-1 = all CPUs). Applied per ratio.')
    parser.add_argument(
        '--results_dir', type=str,
        default=os.path.join(os.path.dirname(SCRIPTS_DIR), 'results'),
        help='Output directory'
    )
    return parser.parse_args()


def _compute_convex_elastic_loss(X, y, convex_weights, lambda_1, lambda_2):
    """
    Evaluate the convex solution's weights under the elastic net objective.

    The convex solution (u_j, v_j) encodes first-layer weights w_j = u_j - v_j.
    We reconstruct network output as sum_j D_j X (u_j - v_j) using stored D_list,
    then evaluate the elastic net loss using all weight magnitudes.

    Returns float or nan if D_list not available.
    """
    n = X.shape[0]
    u_list = convex_weights.get('u', [])
    v_list = convex_weights.get('v', [])
    D_list = convex_weights.get('D_list', None)

    if not u_list or D_list is None:
        return float('nan')

    # Reconstruct prediction
    pred = np.zeros(n)
    for u_j, v_j, D_j in zip(u_list, v_list, D_list):
        if u_j is not None and v_j is not None:
            pred += D_j @ X @ (u_j - v_j)

    data_loss = float(np.sum((y - pred) ** 2) / (2 * n))

    # All weights (u_j and v_j are nonneg vectors)
    all_weights = []
    for u_j, v_j in zip(u_list, v_list):
        if u_j is not None and v_j is not None:
            all_weights.append(u_j)
            all_weights.append(v_j)

    if not all_weights:
        return float('nan')

    all_w = np.concatenate(all_weights)
    l1_term = float(lambda_1 * np.sum(np.abs(all_w)))
    l2_term = float(lambda_2 * np.sum(all_w ** 2))

    return data_loss + l1_term + l2_term


def run_single_seed(seed, ratio, args_n, args_d, args_lambda2, args_width,
                    args_restarts, args_epochs, args_lr, args_max_patterns,
                    scripts_dir):
    """
    Run one (seed, lambda_ratio) configuration. Returns dict with all results.
    Fully self-contained so joblib can pickle it cleanly.
    """
    import time as _time
    import traceback as _tb
    import sys as _sys
    import numpy as _np

    _sys.path.insert(0, scripts_dir)
    from utils import set_all_seeds, generate_gaussian_data, normalized_gap
    from convex_l2_solver import solve_convex_l2
    from nonconvex_elastic_net import train_elastic_net

    lambda1 = ratio * args_lambda2
    beta_convex = 2.0 * _np.sqrt(args_lambda2)

    set_all_seeds(seed)
    X, y, _ = generate_gaussian_data(args_n, args_d, seed)

    t0 = _time.time()

    try:
        # Convex L2 solution (returns D_list in weights dict)
        f_convex, convex_weights = solve_convex_l2(
            X, y, beta=beta_convex, max_patterns=args_max_patterns, seed=seed
        )

        # Non-convex elastic net solution
        f_elastic, _ = train_elastic_net(
            X, y, d=args_d, width=args_width,
            lambda_1=lambda1, lambda_2=args_lambda2,
            n_restarts=args_restarts, n_epochs=args_epochs, lr=args_lr,
            seed_base=seed
        )

        # Primary gap: (f_elastic - f_convex) / f_elastic
        gap_primary = normalized_gap(f_elastic, f_convex)

        # Secondary gap: evaluate convex weights under elastic net objective
        n_pts = X.shape[0]
        u_list = convex_weights.get('u', [])
        v_list = convex_weights.get('v', [])
        D_list = convex_weights.get('D_list', None)

        if u_list and D_list is not None:
            pred = _np.zeros(n_pts)
            for u_j, v_j, D_j in zip(u_list, v_list, D_list):
                if u_j is not None and v_j is not None:
                    pred += D_j @ X @ (u_j - v_j)
            data_loss = float(_np.sum((y - pred) ** 2) / (2 * n_pts))
            all_w = _np.concatenate([
                w for u_j, v_j in zip(u_list, v_list)
                if u_j is not None and v_j is not None
                for w in [u_j, v_j]
            ])
            f_convex_elastic = data_loss + lambda1 * float(_np.sum(_np.abs(all_w))) + \
                               args_lambda2 * float(_np.sum(all_w ** 2))
            gap_secondary = normalized_gap(f_convex_elastic, f_elastic)
        else:
            f_convex_elastic = float('nan')
            gap_secondary = float('nan')

        wall_time = _time.time() - t0

        return {
            'seed': seed,
            'lambda_ratio': ratio,
            'lambda1': float(lambda1),
            'lambda2': float(args_lambda2),
            'beta_convex': float(beta_convex),
            'f_convex': float(f_convex),
            'f_elastic': float(f_elastic),
            'f_convex_elastic': None if (f_convex_elastic != f_convex_elastic) else float(f_convex_elastic),
            'gap': float(gap_primary),
            'gap_secondary': None if (gap_secondary != gap_secondary) else float(gap_secondary),
            'convex_solver_status': convex_weights.get('status', 'unknown'),
            'n_patterns': convex_weights.get('n_patterns', 0),
            'wall_time_seconds': float(wall_time),
            'error': None,
        }

    except Exception:
        wall_time = _time.time() - t0
        return {
            'seed': seed,
            'lambda_ratio': ratio,
            'lambda1': float(lambda1),
            'lambda2': float(args_lambda2),
            'f_convex': None,
            'f_elastic': None,
            'f_convex_elastic': None,
            'gap': None,
            'gap_secondary': None,
            'wall_time_seconds': float(wall_time),
            'error': _tb.format_exc(),
        }


def summarize_by_ratio(results, lambda_ratios):
    """Compute per-ratio summary statistics over valid (non-error) results."""
    summary = []
    for ratio in lambda_ratios:
        ratio_results = [r for r in results if abs(r['lambda_ratio'] - ratio) < 1e-9]
        gaps = [r['gap'] for r in ratio_results if r['gap'] is not None]
        f_convex_vals = [r['f_convex'] for r in ratio_results if r['f_convex'] is not None]
        f_elastic_vals = [r['f_elastic'] for r in ratio_results if r['f_elastic'] is not None]
        if not gaps:
            continue
        summary.append({
            'lambda_ratio': ratio,
            'mean_gap': float(np.mean(gaps)),
            'std_gap': float(np.std(gaps)),
            'min_gap': float(np.min(gaps)),
            'max_gap': float(np.max(gaps)),
            'mean_f_convex': float(np.mean(f_convex_vals)) if f_convex_vals else float('nan'),
            'mean_f_elastic': float(np.mean(f_elastic_vals)) if f_elastic_vals else float('nan'),
            'n_seeds': len(gaps),
            'all_positive': bool(all(g > 0 for g in gaps)),
        })
    return summary


def main():
    args = parse_args()
    lambda_ratios = [float(r) for r in args.lambda_ratios.split(',')]

    # Determine number of parallel jobs (cap at 4 per compute profile)
    cpu_count = os.cpu_count() or 4
    if args.n_jobs == -1:
        n_jobs = min(cpu_count, 4)
    else:
        n_jobs = min(args.n_jobs, 4)
    n_jobs = min(n_jobs, args.seeds)  # no more jobs than seeds

    print("=" * 70)
    print("H6 Main Experiment: Elastic Net Breaks Convex Reformulation")
    print("=" * 70)
    print(f"n={args.n}, d={args.d}, lambda2={args.lambda2}")
    print(f"Lambda ratios: {lambda_ratios}")
    print(f"Seeds: {args.seeds}, Width: {args.width}")
    print(f"Restarts: {args.restarts}, Epochs: {args.epochs}, LR: {args.lr}")
    print(f"Max patterns: {args.max_patterns}")
    print(f"Parallel jobs: {n_jobs} (CPUs available: {cpu_count})")
    print(f"Results dir: {args.results_dir}")
    print(f"Beta convex (2*sqrt(lambda2)): {2.0 * np.sqrt(args.lambda2):.6f}")
    print()

    os.makedirs(args.results_dir, exist_ok=True)

    all_results = []
    total_configs = len(lambda_ratios) * args.seeds
    start_time = time.time()

    for ratio in lambda_ratios:
        print(f"\n--- Lambda ratio = {ratio} "
              f"(parallelizing {args.seeds} seeds, {n_jobs} jobs) ---")
        ratio_start = time.time()

        # Parallel sweep over seeds for this ratio
        ratio_results = Parallel(n_jobs=n_jobs, verbose=0)(
            delayed(run_single_seed)(
                seed, ratio,
                args.n, args.d, args.lambda2, args.width,
                args.restarts, args.epochs, args.lr, args.max_patterns,
                SCRIPTS_DIR
            )
            for seed in range(args.seeds)
        )

        # Sort by seed for deterministic output order
        ratio_results = sorted(ratio_results, key=lambda r: r['seed'])

        valid = [r for r in ratio_results if r['gap'] is not None]
        ratio_elapsed = time.time() - ratio_start

        for r in ratio_results:
            if r['error'] is None:
                print(f"  seed={r['seed']:2d}: f_convex={r['f_convex']:.4f}, "
                      f"f_elastic={r['f_elastic']:.4f}, "
                      f"gap={r['gap']:.4f} ({r['gap']*100:.1f}%), "
                      f"t={r['wall_time_seconds']:.1f}s")
            else:
                short_err = r['error'].split('\n')[-2] if r['error'] else 'unknown'
                print(f"  seed={r['seed']:2d}: ERROR - {short_err[:100]}")

        if valid:
            gaps = [r['gap'] for r in valid]
            print(f"  >> mean_gap={np.mean(gaps):.4f}, std={np.std(gaps):.4f}, "
                  f"n_valid={len(valid)}/{args.seeds}, "
                  f"wall_time={ratio_elapsed:.1f}s")

        all_results.extend(ratio_results)

        # Checkpoint after each ratio
        raw_path = os.path.join(args.results_dir, 'raw_results.json')
        with open(raw_path, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"  Checkpoint saved: {raw_path}")

    # Final save of raw results
    raw_path = os.path.join(args.results_dir, 'raw_results.json')
    with open(raw_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nRaw results saved to: {raw_path}")

    # Summary CSV
    valid_results = [r for r in all_results if r['gap'] is not None]
    summary = summarize_by_ratio(valid_results, lambda_ratios)

    summary_path = os.path.join(args.results_dir, 'summary_table.csv')
    fieldnames = [
        'lambda_ratio', 'mean_gap', 'std_gap', 'min_gap', 'max_gap',
        'mean_f_convex', 'mean_f_elastic', 'n_seeds', 'all_positive'
    ]
    with open(summary_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in summary:
            writer.writerow({
                k: (f"{v:.6f}" if isinstance(v, float) else v)
                for k, v in row.items()
            })
    print(f"Summary saved to: {summary_path}")

    print("\n--- Summary Table ---")
    print(f"{'ratio':>8} {'mean_gap':>10} {'std_gap':>10} {'min_gap':>10} "
          f"{'max_gap':>10} {'n_seeds':>8}")
    for row in summary:
        print(f"{row['lambda_ratio']:>8.3f} {row['mean_gap']:>10.4f} "
              f"{row['std_gap']:>10.4f} {row['min_gap']:>10.4f} "
              f"{row['max_gap']:>10.4f} {row['n_seeds']:>8d}")

    total_time = time.time() - start_time
    completed = sum(1 for r in all_results if r['gap'] is not None)
    errors = sum(1 for r in all_results if r['error'] is not None)
    print(f"\nTotal time: {total_time/60:.1f} minutes")
    print(f"Completed: {completed}/{total_configs}, Errors: {errors}")


if __name__ == '__main__':
    main()
