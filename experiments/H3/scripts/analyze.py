"""H3 Analysis Script.

Reads experiments/H3/results/raw_results.json, computes per-rank statistics,
generates figures, evaluates the base case, and writes
experiments/H3/results/base_case_evaluation.json.

Usage:
    python experiments/H3/scripts/analyze.py [--results_dir PATH] [--status_file PATH]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


def parse_args():
    parser = argparse.ArgumentParser(description="H3 Analysis")
    parser.add_argument("--results_dir", type=str,
                        default="experiments/H3/results")
    parser.add_argument("--status_file", type=str,
                        default="experiments/H3/status.yaml")
    return parser.parse_args()


def load_results(results_dir: str) -> list:
    path = os.path.join(results_dir, "raw_results.json")
    with open(path) as f:
        return json.load(f)


def aggregate_per_rank(results: list) -> dict:
    """Return dict: rank -> {n, mean, std, min, max, q1, q3, median, cv}"""
    agg = {}
    ranks = sorted(set(r["rank"] for r in results))
    for r in ranks:
        gaps = np.array([x["gap_normalized"] for x in results if x["rank"] == r])
        mean = float(gaps.mean())
        std = float(gaps.std(ddof=1)) if len(gaps) > 1 else 0.0
        agg[r] = {
            "n": int(len(gaps)),
            "mean": mean,
            "std": std,
            "min": float(gaps.min()),
            "max": float(gaps.max()),
            "q1": float(np.quantile(gaps, 0.25)),
            "q3": float(np.quantile(gaps, 0.75)),
            "median": float(np.median(gaps)),
            "cv": float(std / abs(mean)) if abs(mean) > 1e-12 else float("inf"),
        }
    return agg


def evaluate_base_case(results: list, agg: dict) -> dict:
    ranks = sorted(agg.keys())
    rank1_gaps = [x["gap_normalized"] for x in results if x["rank"] == 1]
    rank1_max_abs = max(abs(g) for g in rank1_gaps) if rank1_gaps else float("inf")
    rank1_mean_abs = float(np.mean([abs(g) for g in rank1_gaps])) if rank1_gaps else float("inf")

    # Positive control: gap ~ 0 at r=1
    positive_control_ok = (rank1_max_abs < 1e-4 and rank1_mean_abs < 1e-6)

    # Spearman correlation across ALL (rank, seed) pairs
    all_ranks = np.array([x["rank"] for x in results])
    all_gaps = np.array([x["gap_normalized"] for x in results])
    rho, p_spearman = stats.spearmanr(all_ranks, all_gaps)

    # Monotonicity in the means
    means = [agg[r]["mean"] for r in ranks]
    monotone_means = all(means[i + 1] >= means[i] - 1e-8 for i in range(len(means) - 1))

    # Magnitude growth r=5 vs r=2
    if 5 in agg and 2 in agg:
        mag_ratio = agg[5]["mean"] / max(agg[2]["mean"], 1e-12)
    else:
        mag_ratio = float("nan")

    # Primal-dual validity sanity check
    invalid = [x for x in results if not x.get("primal_valid", True)]
    primal_valid_fraction = 1.0 - (len(invalid) / len(results))

    # Verdict
    pass_conditions = (
        positive_control_ok
        and rho > 0.8
        and p_spearman < 0.05
        and monotone_means
        and mag_ratio >= 2.0
        and primal_valid_fraction > 0.95
    )
    fail_conditions = (
        (not positive_control_ok)
        or (abs(rho) < 0.3)
        or (not monotone_means)
    )

    if pass_conditions:
        verdict = "PASS"
    elif fail_conditions:
        verdict = "FAIL"
    else:
        verdict = "INCONCLUSIVE"

    _means_str = str([round(agg[r]["mean"], 4) for r in ranks])
    _details_str = (
        "Spearman rho=" + format(rho, ".4f") + " (p=" + format(p_spearman, ".4e") + "). "
        + "r=1 max|gap|=" + format(rank1_max_abs, ".2e") + ". "
        + "Means by rank: " + _means_str + ". "
        + "Monotone: " + str(monotone_means) + ". r5/r2=" + format(mag_ratio, ".2f") + ". "
        + "Primal valid: " + format(primal_valid_fraction * 100, ".1f") + "%."
    )

    return {
        "pass": verdict == "PASS",
        "verdict": verdict,
        "metric_name": "spearman_rho_rank_vs_gap",
        "metric_value": float(rho),
        "threshold": 0.8,
        "comparison": "greater_than",
        "spearman_p_value": float(p_spearman),
        "rank1_max_abs_gap": float(rank1_max_abs),
        "rank1_mean_abs_gap": float(rank1_mean_abs),
        "positive_control_ok": bool(positive_control_ok),
        "monotone_in_means": bool(monotone_means),
        "magnitude_ratio_r5_over_r2": float(mag_ratio),
        "primal_valid_fraction": float(primal_valid_fraction),
        "per_rank_mean_gap": {int(r): agg[r]["mean"] for r in ranks},
        "n_cells": int(len(results)),
        "details": _details_str,
    }


def write_summary_csv(agg: dict, path: str) -> None:
    ranks = sorted(agg.keys())
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank", "n_seeds", "mean_gap", "std_gap",
                    "median_gap", "q1_gap", "q3_gap",
                    "min_gap", "max_gap", "cv"])
        for r in ranks:
            a = agg[r]
            w.writerow([r, a["n"], f"{a['mean']:.6e}", f"{a['std']:.6e}",
                        f"{a['median']:.6e}", f"{a['q1']:.6e}",
                        f"{a['q3']:.6e}", f"{a['min']:.6e}",
                        f"{a['max']:.6e}", f"{a['cv']:.4f}"])


def plot_gap_vs_rank(results: list, agg: dict, fig_dir: str) -> None:
    ranks = sorted(agg.keys())
    means = [agg[r]["mean"] for r in ranks]
    q1s = [agg[r]["q1"] for r in ranks]
    q3s = [agg[r]["q3"] for r in ranks]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.fill_between(ranks, q1s, q3s, alpha=0.25, color="#2c7bb6", label="IQR (Q1--Q3)")
    ax.plot(ranks, means, "o-", color="#2c7bb6", linewidth=2,
            markersize=9, label="Mean normalized gap")
    ax.axhline(y=1e-4, color="green", linestyle="--", alpha=0.6,
               label="1e-4 positive control tolerance")
    ax.set_xlabel("Data matrix rank $r$", fontsize=13)
    ax.set_ylabel(
        r"Normalized gap $(P_{\mathrm{standard}} - D_{\mathrm{parallel}}) / P_{\mathrm{standard}}$",
        fontsize=12,
    )
    ax.set_title("H3: Rank-Dependent Duality Gap (Standard 3-Layer ReLU)", fontsize=13)
    ax.set_xticks(ranks)
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    out = os.path.join(fig_dir, "gap_vs_rank.png")
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"Saved: {out}")


def plot_violin(results: list, fig_dir: str) -> None:
    ranks = sorted(set(x["rank"] for x in results))
    data = [[x["gap_normalized"] for x in results if x["rank"] == r] for r in ranks]

    fig, ax = plt.subplots(figsize=(8, 5))
    parts = ax.violinplot(data, positions=ranks, widths=0.6,
                          showmeans=True, showmedians=True)
    for pc in parts["bodies"]:
        pc.set_facecolor("#b2d8d8")
        pc.set_edgecolor("#2c7bb6")
        pc.set_alpha(0.8)
    ax.set_xlabel("Data matrix rank $r$", fontsize=13)
    ax.set_ylabel("Normalized gap", fontsize=13)
    ax.set_title("Gap Distribution per Rank Level", fontsize=13)
    ax.set_xticks(ranks)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    out = os.path.join(fig_dir, "gap_distribution_violin.png")
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"Saved: {out}")


def plot_rank1_control(results: list, fig_dir: str) -> None:
    rank1 = [x for x in results if x["rank"] == 1]
    seeds = [x["seed"] for x in rank1]
    gaps = [x["gap_normalized"] for x in rank1]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(seeds, gaps, color="#2c7bb6", alpha=0.75)
    ax.axhline(y=1e-4, color="red", linestyle="--", label="1e-4 tolerance")
    ax.axhline(y=-1e-4, color="red", linestyle="--")
    ax.set_xlabel("Seed", fontsize=13)
    ax.set_ylabel("Normalized gap at r=1", fontsize=13)
    ax.set_title(r"Rank-1 Positive Control (expected: gap $\approx 0$)", fontsize=13)
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    out = os.path.join(fig_dir, "rank1_positive_control.png")
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"Saved: {out}")


def plot_primal_vs_dual(results: list, fig_dir: str) -> None:
    fig, ax = plt.subplots(figsize=(6, 6))
    ranks = sorted(set(x["rank"] for x in results))
    cmap = plt.cm.viridis
    for i, r in enumerate(ranks):
        sub = [x for x in results if x["rank"] == r]
        P = [x["P_standard"] for x in sub]
        D = [x["D_parallel"] for x in sub]
        ax.scatter(D, P, color=cmap(i / max(len(ranks) - 1, 1)),
                   s=40, alpha=0.75, label=f"r={r}")
    lo = min(min(x["P_standard"] for x in results),
             min(x["D_parallel"] for x in results))
    hi = max(max(x["P_standard"] for x in results),
             max(x["D_parallel"] for x in results))
    ax.plot([lo, hi], [lo, hi], "k--", alpha=0.5, label="P = D")
    ax.set_xlabel(r"$D_{\mathrm{parallel}}$ (lower bound)", fontsize=12)
    ax.set_ylabel(r"$P_{\mathrm{standard}}$ (primal)", fontsize=12)
    ax.set_title("Primal vs. Dual Lower Bound (all cells)", fontsize=13)
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    out = os.path.join(fig_dir, "primal_vs_dual_scatter.png")
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"Saved: {out}")


def update_status(status_path: str, verdict: str) -> None:
    import yaml, time
    import os

    existing = {}
    if os.path.exists(status_path):
        with open(status_path) as f:
            existing = yaml.safe_load(f) or {}

    base_case_met = verdict in ("PASS", "INCONCLUSIVE")
    status = "base_case_met" if base_case_met else "base_case_failed"

    existing.update({
        "status": status,
        "base_case_met": base_case_met,
        "steps_completed": 5,
        "current_step": 5,
        "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })

    tmp = status_path + ".tmp"
    with open(tmp, "w") as f:
        yaml.safe_dump(existing, f)
    os.replace(tmp, status_path)
    print(f"Updated status.yaml: status={status}")


def main():
    args = parse_args()
    results_dir = args.results_dir
    fig_dir = os.path.join(results_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)

    results = load_results(results_dir)
    print(f"Loaded {len(results)} result cells.")

    agg = aggregate_per_rank(results)
    print(f"Ranks present: {sorted(agg.keys())}")
    for r, a in sorted(agg.items()):
        print(f"  rank={r}: mean_gap={a['mean']:.4e} std={a['std']:.4e} n={a['n']}")

    write_summary_csv(agg, os.path.join(results_dir, "summary_table.csv"))
    print("Written: summary_table.csv")

    plot_gap_vs_rank(results, agg, fig_dir)
    plot_violin(results, fig_dir)
    plot_rank1_control(results, fig_dir)
    plot_primal_vs_dual(results, fig_dir)

    ev = evaluate_base_case(results, agg)
    out_path = os.path.join(results_dir, "base_case_evaluation.json")
    with open(out_path, "w") as f:
        json.dump(ev, f, indent=2)
    print(f"\nVerdict: {ev['verdict']}")
    print(ev["details"])

    update_status(args.status_file, ev["verdict"])


if __name__ == "__main__":
    main()
