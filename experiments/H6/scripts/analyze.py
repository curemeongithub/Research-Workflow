"""
H6 Analysis: Figures and Base Case Evaluation.

Reads raw_results.json and produces:
- gap_vs_ratio.png
- gap_distribution_boxplot.png
- control_validation.png
- base_case_evaluation.json

Run from project root:
    .venv/bin/python experiments/H6/scripts/analyze.py experiments/H6/results
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from scipy import stats


def load_results(results_dir):
    """Load raw_results.json and filter to valid (non-error) results."""
    path = os.path.join(results_dir, 'raw_results.json')
    with open(path) as f:
        data = json.load(f)
    valid = [r for r in data if r.get('gap') is not None]
    errored = [r for r in data if r.get('gap') is None]
    if errored:
        print(f"WARNING: {len(errored)} errored results excluded from analysis.")
    return valid


def evaluate_base_case(results):
    """
    Evaluate PASS/FAIL/INCONCLUSIVE based on:
    - PASS: gap > 10% for ALL seeds at ratio=1, AND gap < 1% for ALL seeds at ratio=0
    - FAIL: gap < 5% at ratio=1 (mean)
    - INCONCLUSIVE: gap between 5%-10%, or high variance
    """
    control_results = [r for r in results if abs(r['lambda_ratio'] - 0.0) < 1e-9]
    target_results = [r for r in results if abs(r['lambda_ratio'] - 1.0) < 1e-9]

    if not target_results:
        return {
            'pass': False,
            'verdict': 'ERROR - no results for lambda_ratio=1',
            'metric_name': 'normalized_gap_at_ratio_1',
            'metric_value': None,
            'threshold': 0.10,
            'comparison': 'greater_than',
        }

    control_gaps = [r['gap'] for r in control_results]
    target_gaps = [r['gap'] for r in target_results]

    control_max = max(abs(g) for g in control_gaps) if control_gaps else float('inf')
    target_mean = float(np.mean(target_gaps))
    target_min = float(min(target_gaps))
    target_max = float(max(target_gaps))
    target_std = float(np.std(target_gaps))
    target_cv = target_std / abs(target_mean) if abs(target_mean) > 1e-12 else float('inf')

    # Statistical test: one-sample t-test, H0: mean gap == 0.10
    t_stat, p_value_two_sided = stats.ttest_1samp(target_gaps, 0.10)
    # One-sided p-value: H0: gap <= 0.10, H1: gap > 0.10
    p_value_one_sided = p_value_two_sided / 2 if t_stat > 0 else 1 - p_value_two_sided / 2

    # Paired t-test: compare target vs control
    t_paired = float('nan')
    p_paired = float('nan')
    if control_gaps and len(control_gaps) == len(target_gaps):
        t_paired, p_paired = stats.ttest_rel(target_gaps, control_gaps)
        t_paired = float(t_paired)
        p_paired = float(p_paired)

    # Spearman rho: monotonicity of gap vs ratio (nonzero ratios only)
    nonzero_results = [r for r in results if r['lambda_ratio'] > 0]
    if nonzero_results:
        nr_ratios = [r['lambda_ratio'] for r in nonzero_results]
        nr_gaps = [r['gap'] for r in nonzero_results]
        spearman_rho, spearman_p = stats.spearmanr(nr_ratios, nr_gaps)
    else:
        spearman_rho, spearman_p = float('nan'), float('nan')

    # Determine verdict
    control_ok = control_max < 0.01 if control_gaps else False

    if control_ok and target_min > 0.10:
        verdict = "PASS"
    elif target_mean < 0.05:
        verdict = "FAIL"
    elif not control_ok:
        verdict = (f"INCONCLUSIVE - control validation failed "
                   f"(max|gap|={control_max:.4f} >= 1% at ratio=0)")
    elif target_cv > 0.5:
        verdict = f"INCONCLUSIVE - high variance across seeds (CV={target_cv:.2f})"
    elif 0.05 <= target_mean <= 0.10:
        verdict = f"INCONCLUSIVE - gap between 5% and 10% (mean={target_mean:.4f})"
    else:
        # target_mean > 10% but not all seeds > 10%
        fraction_above_10 = sum(1 for g in target_gaps if g > 0.10) / len(target_gaps)
        verdict = f"PARTIAL PASS - {fraction_above_10*100:.0f}% of seeds above 10%"

    details = (
        f"Control (ratio=0): {len(control_gaps)} seeds, max|gap|={control_max:.6f} "
        f"({'OK' if control_ok else 'FAILED'}). "
        f"Target (ratio=1): {len(target_gaps)} seeds, "
        f"mean gap={target_mean:.4f}, std={target_std:.4f}, "
        f"min={target_min:.4f}, max={target_max:.4f}. "
        f"One-sided t-test p={p_value_one_sided:.4e}. "
        f"Spearman rho (nonzero ratios)={spearman_rho:.3f} (p={spearman_p:.4e})."
    )

    return {
        'pass': verdict == "PASS",
        'verdict': verdict,
        'metric_name': 'normalized_gap_at_ratio_1',
        'metric_value': target_mean,
        'threshold': 0.10,
        'comparison': 'greater_than',
        'control_max_gap': float(control_max),
        'control_ok': bool(control_ok),
        'control_n_seeds': len(control_gaps),
        'target_mean_gap': target_mean,
        'target_std_gap': target_std,
        'target_min_gap': target_min,
        'target_max_gap': target_max,
        'target_cv': float(target_cv),
        't_statistic': float(t_stat),
        'p_value_one_sided': float(p_value_one_sided),
        'paired_t_statistic': t_paired,
        'paired_p_value': p_paired,
        'spearman_rho': float(spearman_rho),
        'spearman_p': float(spearman_p),
        'n_seeds': len(target_gaps),
        'details': details,
    }


def plot_gap_vs_ratio(results, fig_dir):
    """
    Plot mean gap +/- std as a function of lambda_1/lambda_2 ratio.
    """
    ratios = sorted(set(r['lambda_ratio'] for r in results))
    means = []
    stds = []
    for ratio in ratios:
        gaps = [r['gap'] for r in results if abs(r['lambda_ratio'] - ratio) < 1e-9]
        means.append(np.mean(gaps))
        stds.append(np.std(gaps))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(ratios, means, yerr=stds, fmt='o-', capsize=4,
                color='#2c7bb6', linewidth=2, markersize=8, label='Mean gap ± std')
    ax.axhline(y=0.01, color='green', linestyle='--', alpha=0.7, label='1% (control threshold)')
    ax.axhline(y=0.05, color='orange', linestyle='--', alpha=0.7, label='5% (fail threshold)')
    ax.axhline(y=0.10, color='red', linestyle='--', alpha=0.7, label='10% (pass threshold)')
    ax.set_xlabel(r'$\lambda_1 / \lambda_2$ ratio', fontsize=13)
    ax.set_ylabel(r'Normalized gap $(f_{\mathrm{elastic}} - f_{\mathrm{convex}}) / f_{\mathrm{elastic}}$',
                  fontsize=12)
    ax.set_title('H6: Elastic Net vs. Convex L2 Reformulation Gap', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    out = os.path.join(fig_dir, 'gap_vs_ratio.png')
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"Saved: {out}")


def plot_boxplots(results, fig_dir):
    """Box plot of gap distribution at each ratio."""
    ratios = sorted(set(r['lambda_ratio'] for r in results))
    data = []
    labels = []
    for ratio in ratios:
        gaps = [r['gap'] for r in results if abs(r['lambda_ratio'] - ratio) < 1e-9]
        data.append(gaps)
        labels.append(f"{ratio}")

    fig, ax = plt.subplots(figsize=(9, 5))
    bp = ax.boxplot(data, labels=labels, patch_artist=True,
                    boxprops=dict(facecolor='#b2d8d8', color='#2c7bb6'),
                    medianprops=dict(color='red', linewidth=2))
    ax.axhline(y=0.10, color='red', linestyle='--', alpha=0.7, label='10% pass threshold')
    ax.axhline(y=0.01, color='green', linestyle='--', alpha=0.7, label='1% control threshold')
    ax.set_xlabel(r'$\lambda_1 / \lambda_2$ ratio', fontsize=13)
    ax.set_ylabel('Normalized gap', fontsize=13)
    ax.set_title('Gap Distribution per Lambda Ratio', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    out = os.path.join(fig_dir, 'gap_distribution_boxplot.png')
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"Saved: {out}")


def plot_control_validation(results, fig_dir):
    """Scatter of control (ratio=0) gaps across seeds."""
    control = [r for r in results if abs(r['lambda_ratio'] - 0.0) < 1e-9]
    if not control:
        print("WARNING: No control results (ratio=0) found. Skipping control validation plot.")
        return

    seeds = [r['seed'] for r in control]
    gaps = [r['gap'] for r in control]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(seeds, gaps, color='#2c7bb6', alpha=0.7)
    ax.axhline(y=0.01, color='red', linestyle='--', label='+1% threshold')
    ax.axhline(y=-0.01, color='red', linestyle='--', label='-1% threshold')
    ax.set_xlabel('Seed', fontsize=13)
    ax.set_ylabel('Normalized gap', fontsize=13)
    ax.set_title('Control Validation: Pure L2 (ratio=0)', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    out = os.path.join(fig_dir, 'control_validation.png')
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"Saved: {out}")


def main():
    results_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results'
    )
    fig_dir = os.path.join(results_dir, 'figures')
    os.makedirs(fig_dir, exist_ok=True)

    print(f"Loading results from: {results_dir}")
    results = load_results(results_dir)
    print(f"Loaded {len(results)} valid results")

    # Generate figures
    plot_gap_vs_ratio(results, fig_dir)
    plot_boxplots(results, fig_dir)
    plot_control_validation(results, fig_dir)

    # Evaluate base case
    evaluation = evaluate_base_case(results)
    eval_path = os.path.join(results_dir, 'base_case_evaluation.json')
    with open(eval_path, 'w') as f:
        json.dump(evaluation, f, indent=2)
    print(f"\nBase case evaluation saved to: {eval_path}")
    print(f"Verdict: {evaluation['verdict']}")
    print(f"Details: {evaluation['details']}")


if __name__ == '__main__':
    main()
