"""H5 main sweep: rank 1 vs rank 2 duality gap for standard 3-layer ReLU.

Multi-process driver (8 workers by default). Resume-safe: cells already present
in raw_results.json are skipped. Each cell is logged to both stdout and file.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from multiprocessing import Pool, get_context

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from utils import generate_rank_controlled_data, get_logger, normalized_gap
from standard_primal_solver import train_standard_primal
from convex_parallel_solver import solve_convex_parallel


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=100)
    p.add_argument("--d", type=int, default=10)
    p.add_argument("--beta", type=float, default=0.01)
    p.add_argument("--seeds", type=int, default=50)
    p.add_argument("--width", type=int, default=50)
    p.add_argument("--restarts", type=int, default=100)
    p.add_argument("--epochs", type=int, default=3000)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--max_patterns", type=int, default=200)
    p.add_argument("--ranks", type=str, default="1,2")
    p.add_argument("--results_dir", type=str, default="experiments/H5/results")
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--status_file", type=str, default="experiments/H5/status.yaml")
    return p.parse_args()


def run_one(task):
    """Worker: run one (rank, seed) cell. Must be top-level for pickling."""
    rank, seed, args_dict = task
    import numpy as np  # noqa: F401
    try:
        X, y, _, eff = generate_rank_controlled_data(
            n=args_dict["n"], d=args_dict["d"], rank=rank, seed=seed
        )
        t0 = time.time()
        primal = train_standard_primal(
            X, y, d=args_dict["d"], width=args_dict["width"],
            beta=args_dict["beta"], n_restarts=args_dict["restarts"],
            n_epochs=args_dict["epochs"], lr=args_dict["lr"],
            seed_base=seed, arch="three_layer", device="cpu",
        )
        primal_time = time.time() - t0

        t0 = time.time()
        lower = solve_convex_parallel(
            X, y, beta=args_dict["beta"], max_patterns=args_dict["max_patterns"],
            pattern_seed=seed,
        )
        convex_time = time.time() - t0

        p_std = primal["p_standard"]
        d_par = lower["d_parallel"]
        gap = normalized_gap(p_std, d_par)

        return {
            "rank": rank,
            "seed": seed,
            "effective_rank": eff,
            "p_standard": p_std,
            "p_standard_data_loss": primal["data_loss"],
            "p_standard_reg_loss": primal["reg_loss"],
            "best_restart": primal["best_restart"],
            "d_parallel": d_par,
            "num_patterns": lower["num_patterns"],
            "solver_status": lower["status"],
            "gap_absolute": p_std - d_par,
            "gap_normalized": gap,
            "primal_ge_lower_bound": bool(p_std >= d_par - 1e-8),
            "primal_time_sec": primal_time,
            "convex_time_sec": convex_time,
            "error": None,
        }
    except Exception as e:
        return {
            "rank": rank, "seed": seed,
            "error": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc(),
        }


def update_status(path, state):
    import yaml
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        yaml.safe_dump(state, f, sort_keys=False)
    os.replace(tmp, path)


def main():
    args = parse_args()
    ranks = [int(r) for r in args.ranks.split(",")]
    os.makedirs(args.results_dir, exist_ok=True)
    log_dir = args.results_dir
    logger = get_logger("H5.sweep", log_file=os.path.join(log_dir, "progress.log"))

    raw_path = os.path.join(args.results_dir, "raw_results.json")
    results = []
    done = set()
    if os.path.exists(raw_path):
        with open(raw_path) as f:
            blob = json.load(f)
        results = blob.get("results", []) if isinstance(blob, dict) else blob
        done = {(r["rank"], r["seed"]) for r in results if r.get("error") is None}
        logger.info(f"Resuming: {len(done)} cells already complete")

    args_dict = vars(args)
    tasks = [(rk, s, args_dict) for rk in ranks for s in range(args.seeds)
             if (rk, s) not in done]
    total_tasks = len(tasks)
    total_grid = len(ranks) * args.seeds
    logger.info(
        f"Running {total_tasks}/{total_grid} cells with {args.workers} workers; "
        f"ranks={ranks} seeds={args.seeds} restarts={args.restarts} epochs={args.epochs} "
        f"max_patterns={args.max_patterns}"
    )

    start = time.time()
    ctx = get_context("spawn")  # safe with torch
    with ctx.Pool(processes=args.workers) as pool:
        for i, rec in enumerate(pool.imap_unordered(run_one, tasks), 1):
            if rec.get("error"):
                logger.error(
                    f"[{i}/{total_tasks}] rank={rec['rank']} seed={rec['seed']} ERROR: {rec['error']}"
                )
            else:
                logger.info(
                    f"[{i}/{total_tasks}] rank={rec['rank']} seed={rec['seed']} "
                    f"gap={rec['gap_normalized']:.3e} P={rec['p_standard']:.5f} "
                    f"D={rec['d_parallel']:.5f} best_restart={rec['best_restart']} "
                    f"t_primal={rec['primal_time_sec']:.1f}s t_cvx={rec['convex_time_sec']:.1f}s"
                )
            results.append(rec)

            # persist after every cell
            with open(raw_path, "w") as f:
                json.dump({"args": args_dict, "results": results}, f, indent=2)

            completed = sum(1 for r in results if r.get("error") is None)
            elapsed = time.time() - start
            rate = i / max(elapsed, 1e-6)
            eta = (total_tasks - i) / max(rate, 1e-6) / 60
            update_status(args.status_file, {
                "hypothesis": "H5",
                "status": "in_progress",
                "current_step": 5,
                "steps_total": 6,
                "steps_completed": 4,
                "iteration": 1,
                "base_case_met": False,
                "base_case_metric": "rank2_gap_fraction_above_1e_minus_4",
                "base_case_threshold": 0.90,
                "progress": f"{completed}/{total_grid}",
                "last_error": None,
                "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "eta_minutes": round(eta, 1),
            })

    total_time = time.time() - start
    logger.info(f"Sweep complete. Wall-clock: {total_time/60:.2f} min")


if __name__ == "__main__":
    main()
