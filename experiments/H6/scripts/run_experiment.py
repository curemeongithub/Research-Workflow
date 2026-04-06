"""
H6 Main Experiment: Elastic Net Breaks Convex Reformulation.

Runs the full experimental grid (lambda_ratios x seeds) computing:
- Convex L2 reformulation objective f_convex
- Non-convex elastic net objective f_elastic
- Normalized gap between them

Run from project root:
    .venv/bin/python experiments/H6/scripts/run_experiment.py \
        --n 200 --d 10 \
        --lambda_ratios 0,0.1,0.5,1.0,2.0,5.0 \
        --lambda2 0.01 \
        --seeds 20 \
        --width 100 \
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

# Add scripts dir to path for local imports
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

from utils import set_all_seeds, generate_gaussian_data, normalized_gap
from convex_l2_solver import solve_convex_l2
from nonconvex_elastic_net import train_elastic_net


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
    parser.add_argument(
        '--results_dir', type=str,
        default=os.path.join(os.path.dirname(SCRIPTS_DIR), 'results'),
        help='Output directory'
    )
    return parser.parse_args()


def run_single_config(X, y, seed, lambda_ratio, lambda2, width, restarts,
                      n_epochs, lr, max_patterns, d):
    """
    Run one (seed, lambda_ratio) configuration.

    Returns dict with all results including both gap measures.
    """
    lambda1 = lambda_ratio * lambda2

    # Beta in convex program = 2 * sqrt(lambda2) per rescaling lemma
    beta_convex = 2.0 * np.sqrt(lambda2)

    # --- Convex L2 solution ---
    f_convex, convex_weights = solve_convex_l2(
        X, y, beta=beta_convex, max_patterns=max_patterns, seed=seed
    )

    # --- Non-convex elastic net solution ---
    f_elastic, elastic_state = train_elastic_net(
        X, y, d=d, width=width,
        lambda_1=lambda1, lambda_2=lambda2,
        n_restarts=restarts, n_epochs=n_epochs, lr=lr, seed_base=seed
    )

    # --- Primary gap: (f_elastic - f_convex) / f_elastic ---
    # Measures how much worse the elastic net objective is vs the convex L2 value.
    # Positive = elastic net finds a higher-loss solution than convex L2 gave.
    # Note: these are under different objectives, so this measures the
    # "convex L2 solution is cheaper to achieve" phenomenon.
    gap_primary = normalized_gap(f_elastic, f_convex)

    return {
        'seed': seed,
        'lambda_ratio': lambda_ratio,
        'lambda1': float(lambda1),
        'lambda2': float(lambda2),
        'beta_convex': float(beta_convex),
        'f_convex': float(f_convex),
        'f_elastic': float(f_elastic),
        'gap': float(gap_primary),
        'convex_solver_status': convex_weights.get('status', 'unknown'),
        'n_patterns': convex_weights.get('n_patterns', 0),
    }


def summarize_by_ratio(results, lambda_ratios):
    """Compute per-ratio summary statistics."""
    summary = []
    for ratio in lambda_ratios:
        ratio_results = [r for r in results if abs(r['lambda_ratio'] - ratio) < 1e-9]
        if not ratio_results:
            continue
        gaps = [r['gap'] for r in ratio_results]
        f_convex_vals = [r['f_convex'] for r in ratio_results]
        f_elastic_vals = [r['f_elastic'] for r in ratio_results]
        summary.append({
            'lambda_ratio': ratio,
            'mean_gap': float(np.mean(gaps)),
            'std_gap': float(np.std(gaps)),
            'min_gap': float(np.min(gaps)),
            'max_gap': float(np.max(gaps)),
            'mean_f_convex': float(np.mean(f_convex_vals)),
            'mean_f_elastic': float(np.mean(f_elastic_vals)),
            'n_seeds': len(ratio_results),
            'all_positive': bool(all(g > 0 for g in gaps)),
        })
    return summary


def main():
    args = parse_args()
    lambda_ratios = [float(r) for r in args.lambda_ratios.split(',')]

    print("=" * 70)
    print("H6 Main Experiment: Elastic Net Breaks Convex Reformulation")
    print("=" * 70)
    print(f"n={args.n}, d={args.d}, lambda2={args.lambda2}")
    print(f"Lambda ratios: {lambda_ratios}")
    print(f"Seeds: {args.seeds}, Width: {args.width}")
    print(f"Restarts: {args.restarts}, Epochs: {args.epochs}, LR: {args.lr}")
    print(f"Max patterns: {args.max_patterns}")
    print(f"Results dir: {args.results_dir}")
    print(f"Beta convex (2*sqrt(lambda2)): {2.0 * np.sqrt(args.lambda2):.6f}")
    print()

    os.makedirs(args.results_dir, exist_ok=True)

    results = []
    total_configs = len(lambda_ratios) * args.seeds
    completed = 0
    errors = 0
    start_time = time.time()

    for ratio in lambda_ratios:
        print(f"\n--- Lambda ratio = {ratio} ---")
        for seed in range(args.seeds):
            set_all_seeds(seed)
            X, y, w_true = generate_gaussian_data(args.n, args.d, seed)

            t0 = time.time()
            try:
                result = run_single_config(
                    X, y, seed, ratio, args.lambda2, args.width,
                    args.restarts, args.epochs, args.lr, args.max_patterns, args.d
                )
                result['wall_time_seconds'] = float(time.time() - t0)
                result['error'] = None
                results.append(result)

                completed += 1
                elapsed = time.time() - start_time
                eta = (elapsed / completed) * (total_configs - completed) if completed > 0 else 0
                print(f"  [{completed}/{total_configs}] seed={seed}, "
                      f"f_convex={result['f_convex']:.4f}, "
                      f"f_elastic={result['f_elastic']:.4f}, "
                      f"gap={result['gap']:.4f} ({result['gap']*100:.1f}%), "
                      f"t={result['wall_time_seconds']:.1f}s, "
                      f"ETA={eta/60:.1f}min")

            except Exception as e:
                errors += 1
                wall_time = time.time() - t0
                err_str = traceback.format_exc()
                print(f"  [{completed+errors}/{total_configs}] seed={seed}, "
                      f"ERROR: {e} ({wall_time:.1f}s)")
                results.append({
                    'seed': seed,
                    'lambda_ratio': ratio,
                    'lambda1': ratio * args.lambda2,
                    'lambda2': args.lambda2,
                    'f_convex': None,
                    'f_elastic': None,
                    'gap': None,
                    'wall_time_seconds': float(wall_time),
                    'error': err_str,
                })

        # Save checkpoint after each ratio
        raw_path = os.path.join(args.results_dir, 'raw_results.json')
        with open(raw_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"  Checkpoint saved: {raw_path}")

    # Final save
    raw_path = os.path.join(args.results_dir, 'raw_results.json')
    with open(raw_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nRaw results saved to: {raw_path}")

    # Summary table (skip errored results)
    valid_results = [r for r in results if r['gap'] is not None]
    summary = summarize_by_ratio(valid_results, lambda_ratios)

    summary_path = os.path.join(args.results_dir, 'summary_table.csv')
    with open(summary_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'lambda_ratio', 'mean_gap', 'std_gap', 'min_gap', 'max_gap',
            'mean_f_convex', 'mean_f_elastic', 'n_seeds', 'all_positive'
        ])
        writer.writeheader()
        for row in summary:
            writer.writerow({k: f"{v:.6f}" if isinstance(v, float) else v
                             for k, v in row.items()})
    print(f"Summary saved to: {summary_path}")

    # Print summary
    print("\n--- Summary Table ---")
    print(f"{'ratio':>8} {'mean_gap':>10} {'std_gap':>10} {'min_gap':>10} "
          f"{'max_gap':>10} {'n_seeds':>8}")
    for row in summary:
        print(f"{row['lambda_ratio']:>8.3f} {row['mean_gap']:>10.4f} "
              f"{row['std_gap']:>10.4f} {row['min_gap']:>10.4f} "
              f"{row['max_gap']:>10.4f} {row['n_seeds']:>8d}")

    total_time = time.time() - start_time
    print(f"\nTotal time: {total_time/60:.1f} minutes")
    print(f"Completed: {completed}/{total_configs}, Errors: {errors}")


if __name__ == '__main__':
    main()
