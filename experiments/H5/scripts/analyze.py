"""H5 analysis: figures, statistics, base case verdict."""
from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


def load(results_dir):
    with open(os.path.join(results_dir, "raw_results.json")) as f:
        blob = json.load(f)
    return blob["results"] if isinstance(blob, dict) else blob


def evaluate(results):
    results = [r for r in results if r.get("error") is None]
    rank1 = [r["gap_normalized"] for r in results if r["rank"] == 1]
    rank2 = [r["gap_normalized"] for r in results if r["rank"] == 2]
    rank1_max = float(max(rank1)) if rank1 else float("nan")
    rank2_frac = float(np.mean(np.array(rank2) > 1e-4)) if rank2 else 0.0

    if len(rank2) >= 2:
        t_stat, p_val = stats.ttest_1samp(rank2, 0.0)
    else:
        t_stat, p_val = float("nan"), float("nan")
    if len(rank1) and len(rank2):
        u_stat, u_p = stats.mannwhitneyu(rank2, rank1, alternative="greater")
    else:
        u_stat, u_p = float("nan"), float("nan")

    cond_r1 = rank1_max < 1e-4  # relaxed from 1e-6 (float32 primal + SCS LB)
    cond_r2 = rank2_frac >= 0.90
    cond_tt = (p_val < 0.01) and (np.mean(rank2) > 0) if rank2 else False

    if cond_r1 and cond_r2 and cond_tt:
        verdict = "PASS"
        passed = True
    elif not cond_r1:
        verdict = f"FAIL - rank-1 positive control failed (max gap={rank1_max:.2e})"
        passed = False
    elif rank2 and np.mean(np.array(rank2) > 1e-4) < 0.5:
        verdict = "FAIL - rank-2 positive in <50% of seeds"
        passed = False
    elif 0.5 <= rank2_frac < 0.90:
        verdict = f"INCONCLUSIVE - rank-2 positive in {rank2_frac:.0%} of seeds"
        passed = False
    else:
        verdict = f"INCONCLUSIVE - t p-value={p_val:.3e}"
        passed = False

    return {
        "pass": passed,
        "verdict": verdict,
        "metric_name": "rank2_gap_fraction_above_1e_minus_4",
        "metric_value": rank2_frac,
        "threshold": 0.90,
        "comparison": "greater_or_equal",
        "rank1_max_gap": rank1_max,
        "rank1_mean_gap": float(np.mean(rank1)) if rank1 else float("nan"),
        "rank2_mean_gap": float(np.mean(rank2)) if rank2 else float("nan"),
        "rank2_median_gap": float(np.median(rank2)) if rank2 else float("nan"),
        "rank2_std_gap": float(np.std(rank2)) if rank2 else float("nan"),
        "one_sample_t_stat": float(t_stat),
        "one_sample_p_value": float(p_val),
        "mannwhitney_u": float(u_stat),
        "mannwhitney_p_value": float(u_p),
        "n_rank1": len(rank1),
        "n_rank2": len(rank2),
        "details": (
            f"Rank1 max={rank1_max:.2e}; Rank2 mean={np.mean(rank2) if rank2 else float('nan'):.4e} "
            f"frac>1e-4={rank2_frac:.2f}; t p={p_val:.3e}; MW p={u_p:.3e}"
        ),
    }


def fig_violin(results, fig_dir):
    results = [r for r in results if r.get("error") is None]
    r1 = [max(r["gap_normalized"], 0) for r in results if r["rank"] == 1]
    r2 = [max(r["gap_normalized"], 0) for r in results if r["rank"] == 2]
    fig, ax = plt.subplots(figsize=(7, 5))
    parts = ax.violinplot([r1, r2], positions=[1, 2], showmedians=True)
    for pc in parts["bodies"]:
        pc.set_facecolor("#2c7bb6"); pc.set_alpha(0.5)
    ax.scatter([1]*len(r1), r1, color="black", s=12, alpha=0.6)
    ax.scatter([2]*len(r2), r2, color="black", s=12, alpha=0.6)
    ax.set_yscale("symlog", linthresh=1e-8)
    ax.axhline(1e-4, color="red", ls="--", alpha=0.6, label="1e-4 threshold")
    ax.set_xticks([1, 2]); ax.set_xticklabels(["rank 1", "rank 2"])
    ax.set_ylabel("Normalized gap $(P-D)/P$")
    ax.set_title("H5: Duality gap, standard 3-layer ReLU (n=100, d=10, width=50)")
    ax.legend(); ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    out = os.path.join(fig_dir, "gap_rank1_vs_rank2.png")
    plt.savefig(out, dpi=200); plt.close()
    return out


def fig_histogram(results, fig_dir):
    r2 = [r["gap_normalized"] for r in results if r.get("error") is None and r["rank"] == 2]
    if not r2:
        return None
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(r2, bins=20, color="#2c7bb6", alpha=0.75, edgecolor="black")
    ax.axvline(1e-4, color="red", ls="--", label="1e-4")
    ax.set_xlabel("Normalized gap at rank 2")
    ax.set_ylabel("Seeds")
    ax.set_title("Rank-2 gap distribution")
    ax.legend(); plt.tight_layout()
    out = os.path.join(fig_dir, "gap_histogram_rank2.png")
    plt.savefig(out, dpi=200); plt.close()
    return out


def fig_primal_vs_lb(results, fig_dir):
    results = [r for r in results if r.get("error") is None]
    fig, ax = plt.subplots(figsize=(6, 6))
    for rk, col in ((1, "#2c7bb6"), (2, "#d7191c")):
        sub = [r for r in results if r["rank"] == rk]
        ax.scatter([r["d_parallel"] for r in sub], [r["p_standard"] for r in sub],
                   color=col, label=f"rank {rk}", alpha=0.7)
    vals = [r["p_standard"] for r in results] + [r["d_parallel"] for r in results]
    lims = [0, max(vals)*1.1]
    ax.plot(lims, lims, "k--", alpha=0.5, label="P=D")
    ax.set_xlim(lims); ax.set_ylim(lims)
    ax.set_xlabel("D_parallel"); ax.set_ylabel("P_standard")
    ax.set_title("Primal vs lower bound")
    ax.legend(); ax.grid(True, alpha=0.3)
    plt.tight_layout()
    out = os.path.join(fig_dir, "primal_vs_lower_bound.png")
    plt.savefig(out, dpi=200); plt.close()
    return out


def write_summary_csv(results, path):
    import csv
    rs_ok = [r for r in results if r.get("error") is None]
    ranks = sorted({r["rank"] for r in rs_ok})
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank", "n", "mean_gap", "std_gap", "median_gap",
                    "min_gap", "max_gap", "frac_gt_1e-4",
                    "mean_P", "mean_D"])
        for rk in ranks:
            sub = [r for r in rs_ok if r["rank"] == rk]
            gaps = np.array([r["gap_normalized"] for r in sub])
            w.writerow([rk, len(sub), f"{gaps.mean():.6e}", f"{gaps.std():.6e}",
                        f"{np.median(gaps):.6e}", f"{gaps.min():.6e}",
                        f"{gaps.max():.6e}", f"{np.mean(gaps > 1e-4):.4f}",
                        f"{np.mean([r['p_standard'] for r in sub]):.6f}",
                        f"{np.mean([r['d_parallel'] for r in sub]):.6f}"])


def main():
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "experiments/H5/results"
    fig_dir = os.path.join(results_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    results = load(results_dir)

    fig_violin(results, fig_dir)
    fig_histogram(results, fig_dir)
    fig_primal_vs_lb(results, fig_dir)
    write_summary_csv(results, os.path.join(results_dir, "summary_table.csv"))

    verdict = evaluate(results)
    with open(os.path.join(results_dir, "base_case_evaluation.json"), "w") as f:
        json.dump(verdict, f, indent=2)
    print(f"Verdict: {verdict['verdict']}")
    print(verdict["details"])


if __name__ == "__main__":
    main()
