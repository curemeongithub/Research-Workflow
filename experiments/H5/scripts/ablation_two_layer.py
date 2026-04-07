"""Two-layer ReLU ablation: gap MUST be ~0 at both rank 1 and rank 2.

This is the gate for the main H5 sweep. Runs quickly (5 seeds x 2 ranks) in parallel.
"""
from __future__ import annotations

import json
import os
import sys
import time
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from utils import generate_rank_controlled_data, get_logger, normalized_gap
from standard_primal_solver import train_standard_primal
from convex_parallel_solver import solve_convex_parallel

N = 100
D = 10
WIDTH = 20
BETA = 0.01
SEEDS = 5
RANKS = (1, 2)
RESTARTS = 60
EPOCHS = 3000
MAX_PATTERNS = 200


def run_one(task):
    rank, seed = task
    X, y, _, _ = generate_rank_controlled_data(n=N, d=D, rank=rank, seed=seed)
    primal = train_standard_primal(
        X, y, d=D, width=WIDTH, beta=BETA, n_restarts=RESTARTS, n_epochs=EPOCHS,
        lr=1e-3, seed_base=seed, arch="two_layer", device="cpu",
    )
    lower = solve_convex_parallel(X, y, beta=BETA, max_patterns=MAX_PATTERNS,
                                  pattern_seed=seed)
    gap = normalized_gap(primal["p_standard"], lower["d_parallel"])
    return {
        "rank": rank, "seed": seed,
        "p_standard": primal["p_standard"],
        "d_parallel": lower["d_parallel"],
        "gap_absolute": primal["p_standard"] - lower["d_parallel"],
        "gap_normalized": gap,
        "num_patterns": lower["num_patterns"],
    }


def main():
    out_dir = "experiments/H5/results"
    os.makedirs(out_dir, exist_ok=True)
    logger = get_logger("H5.ablation", log_file=os.path.join(out_dir, "ablation.log"))
    tasks = [(r, s) for r in RANKS for s in range(SEEDS)]
    logger.info(f"Two-layer ablation: {len(tasks)} cells")
    start = time.time()
    results = []
    ctx = get_context("spawn")
    with ctx.Pool(processes=min(8, len(tasks))) as pool:
        for i, rec in enumerate(pool.imap_unordered(run_one, tasks), 1):
            logger.info(
                f"[{i}/{len(tasks)}] rank={rec['rank']} seed={rec['seed']} "
                f"gap={rec['gap_normalized']:.3e}"
            )
            results.append(rec)

    # Verdict
    max_gap = max(r["gap_normalized"] for r in results)
    passed = max_gap < 1e-3
    verdict = {
        "passed": bool(passed),
        "max_gap": float(max_gap),
        "threshold": 1e-3,
        "per_cell": results,
        "wall_clock_sec": time.time() - start,
    }
    with open(os.path.join(out_dir, "ablation_two_layer.json"), "w") as f:
        json.dump(verdict, f, indent=2)
    logger.info(
        f"Ablation verdict: {'PASS' if passed else 'FAIL'} (max gap = {max_gap:.3e})"
    )
    if not passed:
        sys.exit(2)


if __name__ == "__main__":
    main()
