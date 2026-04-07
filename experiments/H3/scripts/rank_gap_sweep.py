"""H3: Rank-Dependent Duality Gap Sweep.

Runs the full (rank, seed) experimental grid:
  - 5 ranks in {1,2,3,4,5} x 20 seeds = 100 cells (full run)
  - For each cell: generate rank-controlled data, train standard 3-layer
    ReLU primal, solve parallel convex lower bound, compute normalised gap.
  - Resumable: skips cells already recorded in raw_results.json.
  - Writes raw_results.json and progress.log to results_dir.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from utils import generate_rank_controlled_data, normalized_gap, set_all_seeds
from standard_nonconvex_trainer import train_standard_3layer
from parallel_convex_solver import solve_parallel_convex_3layer


def parse_args():
    parser = argparse.ArgumentParser(
        description="H3: Rank-Dependent Duality Gap for Standard 3-Layer ReLU"
    )
    parser.add_argument("--n", type=int, default=100,
                        help="Number of data samples")
    parser.add_argument("--d", type=int, default=10,
                        help="Input dimension")
    parser.add_argument("--ranks", type=str, default="1,2,3,4,5",
                        help="Comma-separated rank levels")
    parser.add_argument("--beta", type=float, default=0.01,
                        help="L2-squared weight decay for standard primal")
    parser.add_argument("--seeds", type=int, default=20,
                        help="Number of seeds (0..seeds-1)")
    parser.add_argument("--width", type=int, default=50,
                        help="Hidden layer width (both hidden layers)")
    parser.add_argument("--restarts", type=int, default=50,
                        help="Non-convex restarts per cell")
    parser.add_argument("--epochs", type=int, default=2000,
                        help="Training epochs per restart")
    parser.add_argument("--lr", type=float, default=1e-3,
                        help="Adam learning rate")
    parser.add_argument("--max_patterns", type=int, default=150,
                        help="Max CVXPY activation patterns")
    parser.add_argument("--results_dir", type=str,
                        default="experiments/H3/results",
                        help="Directory for raw_results.json and progress.log")
    parser.add_argument("--status_file", type=str,
                        default="experiments/H3/status.yaml",
                        help="Path to status.yaml to update during run")
    parser.add_argument("--device", type=str, default="cpu",
                        help="Torch device: cpu or mps")
    return parser.parse_args()


def run_single_cell(X, y, n, d, rank, seed, args) -> dict:
    """Run one (rank, seed) cell. Returns result dict or raises."""
    t0 = time.time()

    # --- Standard 3-layer non-convex primal ---
    t_primal_0 = time.time()
    P_standard, _state = train_standard_3layer(
        X, y,
        d=d, width=args.width, beta=args.beta,
        n_restarts=args.restarts, n_epochs=args.epochs, lr=args.lr,
        seed_base=seed, device=args.device,
    )
    t_primal = time.time() - t_primal_0

    # --- Parallel convex lower bound ---
    t_dual_0 = time.time()
    D_parallel, meta = solve_parallel_convex_3layer(
        X, y, beta=args.beta,
        max_patterns=args.max_patterns,
        pattern_seed=seed,
    )
    t_dual = time.time() - t_dual_0

    gap_raw = P_standard - D_parallel
    gap_norm = normalized_gap(P_standard, D_parallel)

    return {
        "rank": rank,
        "seed": seed,
        "n": n,
        "d": d,
        "P_standard": float(P_standard),
        "D_parallel": float(D_parallel),
        "gap_raw": float(gap_raw),
        "gap_normalized": float(gap_norm),
        "primal_valid": bool(gap_raw >= -1e-6),
        "solver_status": meta["status"],
        "num_patterns": meta["num_patterns"],
        "wall_time_primal_s": t_primal,
        "wall_time_dual_s": t_dual,
        "wall_time_total_s": time.time() - t0,
    }


def update_status(status_path: str, state: dict) -> None:
    """Rewrite status.yaml atomically."""
    import yaml
    tmp = status_path + ".tmp"
    os.makedirs(os.path.dirname(os.path.abspath(status_path)), exist_ok=True)
    with open(tmp, "w") as f:
        yaml.safe_dump(state, f)
    os.replace(tmp, status_path)


def main():
    args = parse_args()
    ranks = [int(r) for r in args.ranks.split(",")]
    seeds = list(range(args.seeds))

    os.makedirs(args.results_dir, exist_ok=True)
    os.makedirs(os.path.join(args.results_dir, "figures"), exist_ok=True)
    raw_path = os.path.join(args.results_dir, "raw_results.json")
    log_path = os.path.join(args.results_dir, "progress.log")

    # Resume: load existing results if present
    results = []
    if os.path.exists(raw_path):
        with open(raw_path) as f:
            results = json.load(f)
        done_keys = {(r["rank"], r["seed"]) for r in results}
        print(f"Resuming: {len(results)} cells already complete.", flush=True)
    else:
        done_keys = set()

    total = len(ranks) * len(seeds)
    start = time.time()

    def log(msg: str) -> None:
        line = f"[{time.strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        with open(log_path, "a") as f:
            f.write(line + "\n")

    log(f"Starting sweep: ranks={ranks} seeds={list(seeds)} n={args.n} d={args.d} "
        f"width={args.width} restarts={args.restarts} epochs={args.epochs} "
        f"max_patterns={args.max_patterns} beta={args.beta}")

    for rank in ranks:
        for seed in seeds:
            if (rank, seed) in done_keys:
                continue
            try:
                X, y, _ = generate_rank_controlled_data(
                    args.n, args.d, rank, seed, noise_std=0.1
                )
                result = run_single_cell(X, y, args.n, args.d, rank, seed, args)
                results.append(result)
                done_keys.add((rank, seed))

                # Persist after every cell (crash safety)
                with open(raw_path, "w") as f:
                    json.dump(results, f, indent=2)

                completed = len(results)
                elapsed = time.time() - start
                eta_min = (elapsed / max(completed, 1)) * (total - completed) / 60.0
                log(
                    f"[{completed}/{total}] rank={rank} seed={seed} "
                    f"P={result['P_standard']:.5f} D={result['D_parallel']:.5f} "
                    f"gap_norm={result['gap_normalized']:.5f} "
                    f"status={result['solver_status']} "
                    f"t={result['wall_time_total_s']:.1f}s ETA={eta_min:.1f}min"
                )

                update_status(args.status_file, {
                    "hypothesis": "H3",
                    "status": "in_progress",
                    "current_step": 4,
                    "steps_total": 5,
                    "steps_completed": 3,
                    "iteration": 0,
                    "base_case_met": False,
                    "last_error": None,
                    "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "progress": f"{completed}/{total}",
                })

            except Exception as e:
                tb = traceback.format_exc()
                log(f"ERROR rank={rank} seed={seed}: {e}\n{tb}")
                err_path = os.path.join(
                    os.path.dirname(os.path.abspath(args.status_file)), "error.log"
                )
                with open(err_path, "w") as f:
                    f.write(tb)
                update_status(args.status_file, {
                    "hypothesis": "H3",
                    "status": "error",
                    "current_step": 4,
                    "steps_total": 5,
                    "steps_completed": 3,
                    "iteration": 0,
                    "base_case_met": False,
                    "last_error": str(e),
                    "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                })
                raise

    total_time = time.time() - start
    log(f"Sweep complete. {len(results)} cells in {total_time / 60:.1f} min.")


if __name__ == "__main__":
    main()
