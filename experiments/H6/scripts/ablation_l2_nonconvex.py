"""
H6 Ablation: Non-Convex L2 vs Convex L2 Validation.

Verifies that the non-convex training with pure L2 (no L1 component)
converges to the same optimum as the convex solver. This validates the
pipeline and the beta mapping before running the main experiment.

Expected result: |f_convex - f_nonconvex| / max(|f_convex|, 1e-12) < 5%
for all seeds (using a relaxed threshold since perfect matching is hard
with gradient descent).

Run from project root:
    .venv/bin/python experiments/H6/scripts/ablation_l2_nonconvex.py
"""
import json
import os
import sys
import time
import traceback

import numpy as np

# Add scripts dir to path for local imports
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

from utils import set_all_seeds, generate_gaussian_data, normalized_gap
from convex_l2_solver import solve_convex_l2
from nonconvex_elastic_net import train_elastic_net

RESULTS_DIR = os.path.join(
    os.path.dirname(SCRIPTS_DIR), 'results'
)

# Parameters
N = 200
D = 10
LAMBDA_2 = 0.01
LAMBDA_1 = 0.0  # Pure L2 (no elastic net)
N_SEEDS = 5
WIDTH = 100
N_RESTARTS = 100  # More restarts for ablation reliability
N_EPOCHS = 5000
LR = 0.001
MAX_PATTERNS = 200

# Beta mapping: convex group-L1 = 2 * sqrt(lambda_2)
BETA_CONVEX = 2.0 * np.sqrt(LAMBDA_2)
TOLERANCE = 0.05  # 5% -- relaxed for non-convex optimizer


def main():
    print("=" * 60)
    print("H6 Ablation: Non-Convex L2 vs Convex L2 Validation")
    print("=" * 60)
    print(f"Parameters: n={N}, d={D}, lambda_2={LAMBDA_2}, beta_convex={BETA_CONVEX:.6f}")
    print(f"Seeds: {N_SEEDS}, Restarts: {N_RESTARTS}, Epochs: {N_EPOCHS}")
    print(f"Tolerance: {TOLERANCE*100:.0f}%")
    print()

    ablation_results = []
    all_passed = True

    for seed in range(N_SEEDS):
        print(f"--- Seed {seed} ---")
        set_all_seeds(seed)
        X, y, w_true = generate_gaussian_data(N, D, seed)

        t0 = time.time()

        # --- Convex L2 solution ---
        try:
            f_convex, convex_weights = solve_convex_l2(
                X, y, beta=BETA_CONVEX, max_patterns=MAX_PATTERNS, seed=seed
            )
            print(f"  Convex f={f_convex:.6f} (status={convex_weights['status']}, "
                  f"patterns={convex_weights['n_patterns']})")
        except Exception as e:
            print(f"  CONVEX SOLVER FAILED: {e}")
            traceback.print_exc()
            all_passed = False
            continue

        # --- Non-convex L2-only solution ---
        try:
            f_nonconvex, nonconvex_weights = train_elastic_net(
                X, y, d=D, width=WIDTH,
                lambda_1=LAMBDA_1, lambda_2=LAMBDA_2,
                n_restarts=N_RESTARTS, n_epochs=N_EPOCHS, lr=LR, seed_base=seed
            )
            print(f"  NonConvex f={f_nonconvex:.6f}")
        except Exception as e:
            print(f"  NON-CONVEX TRAINING FAILED: {e}")
            traceback.print_exc()
            all_passed = False
            continue

        # --- Compute relative difference ---
        rel_diff = abs(f_nonconvex - f_convex) / max(abs(f_convex), 1e-12)
        gap = normalized_gap(f_nonconvex, f_convex)

        wall_time = time.time() - t0
        passed = rel_diff < TOLERANCE

        if not passed:
            all_passed = False

        status = "PASS" if passed else "FAIL"
        print(f"  Gap={gap:.4f} ({gap*100:.2f}%), RelDiff={rel_diff:.4f} "
              f"({rel_diff*100:.2f}%) | {status} | {wall_time:.1f}s")

        ablation_results.append({
            'seed': seed,
            'f_convex': float(f_convex),
            'f_nonconvex': float(f_nonconvex),
            'normalized_gap': float(gap),
            'relative_difference': float(rel_diff),
            'passed': passed,
            'wall_time_seconds': float(wall_time),
            'convex_status': convex_weights['status'],
            'n_patterns': convex_weights['n_patterns'],
        })

    print()
    print("=" * 60)
    print(f"ABLATION SUMMARY: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    print("=" * 60)

    if ablation_results:
        rel_diffs = [r['relative_difference'] for r in ablation_results]
        gaps = [r['normalized_gap'] for r in ablation_results]
        print(f"Relative differences: mean={np.mean(rel_diffs):.4f}, "
              f"max={np.max(rel_diffs):.4f}, min={np.min(rel_diffs):.4f}")
        print(f"Normalized gaps: mean={np.mean(gaps):.4f}, "
              f"max={np.max(gaps):.4f}, min={np.min(gaps):.4f}")

    # Save results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    output = {
        'passed': all_passed,
        'tolerance': TOLERANCE,
        'beta_convex': float(BETA_CONVEX),
        'lambda_2': LAMBDA_2,
        'parameters': {
            'n': N, 'd': D, 'width': WIDTH, 'n_restarts': N_RESTARTS,
            'n_epochs': N_EPOCHS, 'lr': LR, 'max_patterns': MAX_PATTERNS,
        },
        'per_seed': ablation_results,
    }

    out_path = os.path.join(RESULTS_DIR, 'ablation_l2_nonconvex.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nAblation results saved to: {out_path}")

    if not all_passed:
        print("\nWARNING: Ablation FAILED. Debug before running main experiment.")
        print("Possible causes:")
        print("  1. Incorrect beta mapping (should be 2*sqrt(lambda_2))")
        print("  2. Insufficient restarts or epochs for non-convex solver")
        print("  3. Convex solver numerical issues")
        sys.exit(1)
    else:
        print("\nAblation PASSED. Pipeline validated. Ready for main experiment.")
        sys.exit(0)


if __name__ == '__main__':
    main()
