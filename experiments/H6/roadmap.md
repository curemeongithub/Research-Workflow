---
hypothesis: H6
title: "Elastic Net Regularization Breaks the Convex Reformulation for Two-Layer ReLU Networks"
type: empirical-verification
estimated_total_hours: 3
colab_gates: 0
---

# Experiment Roadmap: H6 -- Elastic Net Breaks Convex Reformulation

## 1. Objective

Determine whether adding an L1 penalty (elastic net) to the standard L2-squared weight decay breaks the rescaling lemma that underpins the convex reformulation of two-layer ReLU network training. We measure the gap between the non-convex elastic-net-regularized optimum and the convex L2-only reformulation optimum, expecting a significant gap (>10%) when lambda_1/lambda_2 = 1 and near-zero gap (<1%) when lambda_1 = 0 (pure L2 control).

## 2. Base Case (Pass/Fail Criteria)

- **PASS:** At lambda_1/lambda_2 = 1, the normalized gap (f_elastic - f_convex) / f_elastic exceeds 10% across all 20 seeds, AND the pure L2 control (lambda_1 = 0) yields gap < 1% across all seeds.
- **FAIL:** Gap < 5% at lambda_1/lambda_2 = 1, indicating the convex reformulation remains approximately valid even with elastic net.
- **INCONCLUSIVE:** Gap between 5% and 10% at the target ratio, or high variance across seeds (coefficient of variation > 0.5).
- **Minimum data for conclusion:** 6 lambda ratios x 20 seeds = 120 experimental runs.

## 3. Local Setup

All computation runs locally on Apple M4 Pro (12 cores, 24GB RAM). No VM, no SSH, no Colab.

```bash
# Project root
cd /Users/abhinavmallick/Github.nosync/Research-Workflow

# Install missing packages into project venv
.venv/bin/pip install cvxpy torch scikit-learn matplotlib

# Verify installations
.venv/bin/python -c "import cvxpy; import torch; import sklearn; import matplotlib; print('All packages OK')"

# Verify experiment directories exist
ls -la experiments/H6/{scripts,results,results/figures,colab,colab-results}
```

## 4. Repository Cloning

The SCNN repo provides reference code for two-layer convex ReLU solvers. However, for this experiment, we implement the convex program directly in CVXPY rather than importing SCNN as a library. The SCNN formulation is well-documented in [Mishkin2022SCNN] and [PilanciErgen2020], and a direct CVXPY implementation gives us full control over the regularizer and avoids dependency on SCNN's internal API.

**No external repo clone required.** All code is self-contained using CVXPY + PyTorch.

## 5. Implementation Steps

### Step 1: Shared Data Generation and Metrics Utilities

**Script:** `experiments/H6/scripts/utils.py`
**Inputs:** None (utility module)
**Outputs:** Importable module
**Compute:** N/A
**Purpose:** Provide reusable functions for data generation, seed management, and metric computation.

**Pseudocode:**
```python
import numpy as np
import torch
import random

def set_all_seeds(seed):
    """Set numpy, torch, and random seeds for reproducibility."""
    np.random.seed(seed)
    torch.manual_seed(seed)
    random.seed(seed)

def generate_gaussian_data(n, d, seed, noise_std=0.1):
    """
    Generate synthetic regression data.
    X ~ N(0, I_d) in R^{n x d}
    w_true ~ N(0, I_d)
    y = X @ w_true + noise, noise ~ N(0, noise_std)
    Returns: X (n,d), y (n,), w_true (d,) as numpy arrays
    """
    set_all_seeds(seed)
    X = np.random.randn(n, d)
    w_true = np.random.randn(d)
    noise = np.random.randn(n) * noise_std
    y = X @ w_true + noise
    return X, y, w_true

def normalized_gap(f_test, f_reference):
    """
    Compute (f_test - f_reference) / f_test.
    Positive means f_test > f_reference (test is worse).
    """
    if abs(f_test) < 1e-12:
        return 0.0
    return (f_test - f_reference) / f_test
```

---

### Step 2: Convex L2 Reformulation Solver

**Script:** `experiments/H6/scripts/convex_l2_solver.py`
**Inputs:** Data matrix X (n x d), target vector y (n,), regularization strength beta, hidden width P (number of hyperplane arrangements to sample)
**Outputs:** Optimal convex objective value f_convex, optimal convex weights
**Compute:** CPU, ~1-2 minutes per (seed, lambda_ratio) pair
**Purpose:** Solve the convex reformulation of a two-layer ReLU network with pure L2-squared regularization using CVXPY. This implements the Pilanci-Ergen (2020) convex program.

**Pseudocode:**
```python
import numpy as np
import cvxpy as cp
from itertools import combinations

def enumerate_sign_patterns(X, max_patterns=None):
    """
    Enumerate hyperplane arrangements for ReLU activation patterns.
    For small d, enumerate sign patterns of X @ v for random v.
    For tractability, sample P random hyperplanes.
    
    Args:
        X: (n, d) data matrix
        max_patterns: maximum number of patterns to sample
    Returns:
        D_list: list of (n, n) diagonal matrices with 0/1 entries,
                each representing a ReLU activation pattern
    """
    n, d = X.shape
    if max_patterns is None:
        max_patterns = 200  # sufficient for n=200, d=10
    
    D_list = []
    seen = set()
    
    # Sample random hyperplanes to generate activation patterns
    for _ in range(max_patterns * 10):  # oversample, deduplicate
        v = np.random.randn(d)
        pattern = tuple((X @ v > 0).astype(int))
        if pattern not in seen:
            seen.add(pattern)
            D_list.append(np.diag(np.array(pattern, dtype=float)))
            if len(D_list) >= max_patterns:
                break
    
    return D_list

def solve_convex_l2(X, y, beta, max_patterns=200, solver_eps=1e-8):
    """
    Solve the convex reformulation of two-layer ReLU network training
    with L2-squared (weight decay) regularization.
    
    The convex program (from Pilanci-Ergen 2020):
        min_{u_j, v_j} (1/2n) ||y - sum_j D_j X (u_j - v_j)||^2 
                        + beta * sum_j (||u_j|| + ||v_j||)
        s.t. u_j >= 0, v_j >= 0 for all j
    
    where D_j are diagonal matrices encoding ReLU activation patterns,
    and beta is the group-L1 regularization (equivalent to L2-squared
    weight decay via the rescaling lemma).
    
    Args:
        X: (n, d) data matrix
        y: (n,) target vector
        beta: regularization strength (corresponds to L2 weight decay
              via the rescaling lemma: beta_convex = 2 * sqrt(lambda_2))
        max_patterns: number of hyperplane patterns to sample
        solver_eps: SCS solver tolerance
    Returns:
        f_convex: optimal objective value (training loss + regularization)
        weights: dict with optimal u, v arrays
    """
    n, d = X.shape
    
    # Enumerate activation patterns
    D_list = enumerate_sign_patterns(X, max_patterns=max_patterns)
    P = len(D_list)
    
    # Decision variables: u_j, v_j in R^d for each pattern j
    u = [cp.Variable(d, nonneg=True) for _ in range(P)]
    v = [cp.Variable(d, nonneg=True) for _ in range(P)]
    
    # Prediction: sum_j D_j X (u_j - v_j)
    pred = sum(D_list[j] @ X @ (u[j] - v[j]) for j in range(P))
    
    # Objective: (1/2n)||y - pred||^2 + beta * sum_j (||u_j||_2 + ||v_j||_2)
    loss = (1.0 / (2 * n)) * cp.sum_squares(y - pred)
    reg = beta * sum(cp.norm(u[j], 2) + cp.norm(v[j], 2) for j in range(P))
    
    objective = cp.Minimize(loss + reg)
    prob = cp.Problem(objective)
    
    prob.solve(solver=cp.SCS, eps=solver_eps, max_iters=50000, verbose=False)
    
    if prob.status not in ['optimal', 'optimal_inaccurate']:
        raise RuntimeError(f"CVXPY solver failed with status: {prob.status}")
    
    f_convex = prob.value
    weights = {
        'u': [u_j.value for u_j in u],
        'v': [v_j.value for v_j in v],
    }
    
    return f_convex, weights
```

**Key implementation notes for the coder:**
1. The `beta` parameter in the convex program relates to the original L2 weight decay `lambda_2` via the rescaling lemma: `beta = 2 * sqrt(lambda_2)`. The coder must ensure this mapping is correct.
2. The D_j matrices are n x n diagonal and can be memory-intensive. For n=200, each is 200x200. With P=200 patterns, the total CVXPY problem has 2 * 200 * 10 = 4000 scalar variables. This is well within CVXPY/SCS capability.
3. SCS solver with eps=1e-8 and max_iters=50000 should converge. If it does not, fall back to ECOS or MOSEK.

---

### Step 3: Non-Convex Elastic Net Training

**Script:** `experiments/H6/scripts/nonconvex_elastic_net.py`
**Inputs:** Data matrix X, target y, lambda_1, lambda_2, network width, number of restarts
**Outputs:** Best training loss f_elastic (including elastic net penalty), best model weights
**Compute:** CPU, ~2-3 minutes per (seed, lambda_ratio) pair with 50 restarts x 3000 epochs
**Purpose:** Train a two-layer ReLU network with elastic net regularization using Adam optimizer with multiple random restarts, keeping the best solution.

**Pseudocode:**
```python
import torch
import torch.nn as nn
import numpy as np

class TwoLayerReLU(nn.Module):
    """Two-layer ReLU network: input -> Linear(d, width) -> ReLU -> Linear(width, 1)"""
    def __init__(self, d, width):
        super().__init__()
        self.layer1 = nn.Linear(d, width, bias=False)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(width, 1, bias=False)
    
    def forward(self, x):
        return self.layer2(self.relu(self.layer1(x))).squeeze(-1)

def elastic_net_penalty(model, lambda_1, lambda_2):
    """
    Compute elastic net penalty: lambda_1 * sum|w| + lambda_2 * sum(w^2)
    Applied to ALL weights in the network (both layers).
    """
    l1_term = 0.0
    l2_term = 0.0
    for param in model.parameters():
        l1_term += torch.sum(torch.abs(param))
        l2_term += torch.sum(param ** 2)
    return lambda_1 * l1_term + lambda_2 * l2_term

def train_elastic_net(X, y, d, width, lambda_1, lambda_2, 
                      n_restarts=50, n_epochs=3000, lr=0.001, seed_base=0):
    """
    Train two-layer ReLU with elastic net regularization.
    Multiple random restarts; return best (lowest total loss).
    
    Args:
        X: (n, d) numpy array
        y: (n,) numpy array
        d: input dimension
        width: hidden layer width
        lambda_1: L1 regularization strength
        lambda_2: L2-squared regularization strength
        n_restarts: number of random initializations
        n_epochs: training epochs per restart
        lr: Adam learning rate
        seed_base: base seed (restart i uses seed_base + i)
    Returns:
        best_loss: float, best total loss (data + regularization)
        best_state_dict: model weights achieving best loss
    """
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32)
    n = X.shape[0]
    
    best_loss = float('inf')
    best_state_dict = None
    
    for restart in range(n_restarts):
        torch.manual_seed(seed_base * 1000 + restart)
        model = TwoLayerReLU(d, width)
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        
        for epoch in range(n_epochs):
            optimizer.zero_grad()
            pred = model(X_t)
            data_loss = (1.0 / (2 * n)) * torch.sum((y_t - pred) ** 2)
            reg_loss = elastic_net_penalty(model, lambda_1, lambda_2)
            total_loss = data_loss + reg_loss
            total_loss.backward()
            optimizer.step()
        
        final_loss = total_loss.item()
        if final_loss < best_loss:
            best_loss = final_loss
            best_state_dict = {k: v.clone() for k, v in model.state_dict().items()}
    
    return best_loss, best_state_dict
```

**Key implementation notes for the coder:**
1. The elastic net penalty is applied to ALL weights in both layers. This matches the hypothesis formulation which says "lambda_1 ||w||_1 + lambda_2 ||w||_2^2" over all weights.
2. 50 restarts with 3000 epochs each is the primary configuration. On Apple M4 Pro, a single restart for (n=200, d=10, width=100) takes ~0.5-1 second, so 50 restarts take ~30-50 seconds per configuration.
3. The learning rate 0.001 with Adam is a standard choice. If convergence is poor (loss not decreasing), the coder should try lr=0.01 and lr=0.0001 as alternatives.
4. Use `torch.float32` (not float64) for speed. The M4 Pro is fast at float32.

---

### Step 4: Main Experiment Script

**Script:** `experiments/H6/scripts/run_experiment.py`
**Inputs:** Command-line arguments: `--n 200 --d 10 --lambda_ratios 0,0.1,0.5,1.0,2.0,5.0 --lambda2 0.01 --seeds 20 --width 100 --restarts 50`
**Outputs:**
  - `experiments/H6/results/raw_results.json` -- all per-seed, per-ratio results
  - `experiments/H6/results/summary_table.csv` -- aggregated statistics
**Compute:** CPU, ~2-3 hours total (6 ratios x 20 seeds, parallelizable across seeds)
**Purpose:** Run the full experimental grid, computing the convex L2 solution and non-convex elastic net solution for each (seed, lambda_ratio) pair, then computing the normalized gap.

**Pseudocode:**
```python
import argparse
import json
import csv
import time
import os
import sys
import numpy as np

# Import from local modules
from utils import set_all_seeds, generate_gaussian_data, normalized_gap
from convex_l2_solver import solve_convex_l2
from nonconvex_elastic_net import train_elastic_net

def parse_args():
    parser = argparse.ArgumentParser(description='H6: Elastic Net Breaks Convex Reformulation')
    parser.add_argument('--n', type=int, default=200, help='Number of samples')
    parser.add_argument('--d', type=int, default=10, help='Input dimension')
    parser.add_argument('--lambda_ratios', type=str, default='0,0.1,0.5,1.0,2.0,5.0',
                        help='Comma-separated lambda_1/lambda_2 ratios')
    parser.add_argument('--lambda2', type=float, default=0.01, help='L2 regularization strength')
    parser.add_argument('--seeds', type=int, default=20, help='Number of random seeds')
    parser.add_argument('--width', type=int, default=100, help='Hidden layer width')
    parser.add_argument('--restarts', type=int, default=50, help='Non-convex restarts per config')
    parser.add_argument('--max_patterns', type=int, default=200, 
                        help='Max hyperplane patterns for convex solver')
    parser.add_argument('--results_dir', type=str, 
                        default='experiments/H6/results',
                        help='Output directory')
    return parser.parse_args()

def run_single_config(X, y, seed, lambda_ratio, lambda2, width, restarts, 
                      max_patterns, d):
    """
    Run one (seed, lambda_ratio) configuration.
    
    Returns dict with:
        seed, lambda_ratio, lambda1, lambda2,
        f_convex, f_elastic, gap, wall_time
    """
    lambda1 = lambda_ratio * lambda2
    
    # --- Convex L2 solution ---
    # beta in convex program = 2 * sqrt(lambda2) per rescaling lemma
    beta_convex = 2.0 * np.sqrt(lambda2)
    f_convex, convex_weights = solve_convex_l2(
        X, y, beta=beta_convex, max_patterns=max_patterns
    )
    
    # --- Non-convex elastic net solution ---
    f_elastic, elastic_weights = train_elastic_net(
        X, y, d=d, width=width, 
        lambda_1=lambda1, lambda_2=lambda2,
        n_restarts=restarts, seed_base=seed
    )
    
    # --- Compute gap ---
    gap = normalized_gap(f_elastic, f_convex)
    
    return {
        'seed': seed,
        'lambda_ratio': lambda_ratio,
        'lambda1': lambda1,
        'lambda2': lambda2,
        'f_convex': f_convex,
        'f_elastic': f_elastic,
        'gap': gap,
    }

def main():
    args = parse_args()
    lambda_ratios = [float(r) for r in args.lambda_ratios.split(',')]
    
    results = []
    total_configs = len(lambda_ratios) * args.seeds
    completed = 0
    start_time = time.time()
    
    for ratio in lambda_ratios:
        for seed in range(args.seeds):
            set_all_seeds(seed)
            X, y, w_true = generate_gaussian_data(args.n, args.d, seed)
            
            t0 = time.time()
            result = run_single_config(
                X, y, seed, ratio, args.lambda2, args.width,
                args.restarts, args.max_patterns, args.d
            )
            result['wall_time_seconds'] = time.time() - t0
            results.append(result)
            
            completed += 1
            elapsed = time.time() - start_time
            eta = (elapsed / completed) * (total_configs - completed)
            print(f"[{completed}/{total_configs}] ratio={ratio}, seed={seed}, "
                  f"gap={result['gap']:.4f}, time={result['wall_time_seconds']:.1f}s, "
                  f"ETA={eta/60:.1f}min")
    
    # Save raw results
    os.makedirs(args.results_dir, exist_ok=True)
    raw_path = os.path.join(args.results_dir, 'raw_results.json')
    with open(raw_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Raw results saved to {raw_path}")
    
    # Save summary table
    summary_path = os.path.join(args.results_dir, 'summary_table.csv')
    # Group by lambda_ratio, compute mean/std/min/max of gap
    with open(summary_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['lambda_ratio', 'mean_gap', 'std_gap', 'min_gap', 
                         'max_gap', 'mean_f_convex', 'mean_f_elastic', 
                         'n_seeds', 'all_positive'])
        for ratio in lambda_ratios:
            ratio_results = [r for r in results if r['lambda_ratio'] == ratio]
            gaps = [r['gap'] for r in ratio_results]
            writer.writerow([
                ratio,
                f"{np.mean(gaps):.6f}",
                f"{np.std(gaps):.6f}",
                f"{np.min(gaps):.6f}",
                f"{np.max(gaps):.6f}",
                f"{np.mean([r['f_convex'] for r in ratio_results]):.6f}",
                f"{np.mean([r['f_elastic'] for r in ratio_results]):.6f}",
                len(ratio_results),
                all(g > 0 for g in gaps),
            ])
    print(f"Summary saved to {summary_path}")
    
    total_time = time.time() - start_time
    print(f"Total wall-clock time: {total_time/60:.1f} minutes")

if __name__ == '__main__':
    main()
```

**Key implementation notes for the coder:**
1. The CRITICAL detail is the mapping between lambda_2 (weight decay in the non-convex problem) and beta (group-L1 strength in the convex program). The rescaling lemma states that for a two-layer ReLU network with L2-squared weight decay lambda_2 on both layers, the equivalent convex program has group-L1 regularization with strength beta = 2 * sqrt(lambda_2). The coder MUST verify this mapping by running the lambda_ratio=0 control and confirming gap < 1%.
2. If the beta mapping is wrong, the lambda_ratio=0 control will show a large gap, immediately signaling a bug.
3. The experiment runs sequentially over (ratio, seed) pairs. To speed up, the coder MAY parallelize across seeds using Python multiprocessing (up to 4 workers per the compute profile), but sequential execution is the default for debuggability.
4. Expected wall-clock: each (ratio, seed) pair takes ~1-2 minutes (convex solve ~30-60s, non-convex training ~30-60s for 50 restarts). Total: 120 pairs x 1.5 min = ~3 hours.

---

### Step 5: Analysis and Visualization

**Script:** `experiments/H6/scripts/analyze.py`
**Inputs:** `experiments/H6/results/raw_results.json`
**Outputs:**
  - `experiments/H6/results/figures/gap_vs_ratio.png` -- main result figure
  - `experiments/H6/results/figures/gap_distribution_boxplot.png` -- box plots per ratio
  - `experiments/H6/results/figures/control_validation.png` -- lambda_ratio=0 gaps
  - `experiments/H6/results/base_case_evaluation.json` -- pass/fail determination
**Compute:** CPU, ~2 minutes

**Pseudocode:**
```python
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os
import sys

def load_results(results_dir):
    """Load raw_results.json."""
    with open(os.path.join(results_dir, 'raw_results.json')) as f:
        return json.load(f)

def evaluate_base_case(results):
    """
    Evaluate PASS/FAIL/INCONCLUSIVE based on:
    - PASS: gap > 10% for ALL seeds at ratio=1, AND gap < 1% for ALL seeds at ratio=0
    - FAIL: gap < 5% at ratio=1 (mean)
    - INCONCLUSIVE: gap between 5%-10%, or high variance
    """
    control_results = [r for r in results if r['lambda_ratio'] == 0.0]
    target_results = [r for r in results if r['lambda_ratio'] == 1.0]
    
    control_gaps = [r['gap'] for r in control_results]
    target_gaps = [r['gap'] for r in target_results]
    
    control_max = max(abs(g) for g in control_gaps)
    target_mean = np.mean(target_gaps)
    target_min = min(target_gaps)
    target_cv = np.std(target_gaps) / abs(target_mean) if abs(target_mean) > 1e-12 else float('inf')
    
    # Statistical test: one-sample t-test, H0: gap <= 0.10
    t_stat, p_value_two_sided = stats.ttest_1samp(target_gaps, 0.10)
    p_value_one_sided = p_value_two_sided / 2 if t_stat > 0 else 1 - p_value_two_sided / 2
    
    # Paired t-test: control vs target
    # (need matched seeds)
    if len(control_gaps) == len(target_gaps):
        t_paired, p_paired = stats.ttest_rel(target_gaps, control_gaps)
    else:
        t_paired, p_paired = float('nan'), float('nan')
    
    # Determine verdict
    control_ok = control_max < 0.01  # all control gaps < 1%
    
    if control_ok and target_min > 0.10:
        verdict = "PASS"
    elif target_mean < 0.05:
        verdict = "FAIL"
    elif not control_ok:
        verdict = "INCONCLUSIVE - control validation failed (gap >= 1% at ratio=0)"
    elif target_cv > 0.5:
        verdict = "INCONCLUSIVE - high variance across seeds"
    elif 0.05 <= target_mean <= 0.10:
        verdict = "INCONCLUSIVE - gap between 5% and 10%"
    else:
        # target_mean > 10% but not all seeds > 10%
        fraction_above_10 = sum(1 for g in target_gaps if g > 0.10) / len(target_gaps)
        verdict = f"PARTIAL PASS - {fraction_above_10*100:.0f}% of seeds above 10%"
    
    return {
        'pass': verdict == "PASS",
        'verdict': verdict,
        'metric_name': 'normalized_gap_at_ratio_1',
        'metric_value': float(target_mean),
        'threshold': 0.10,
        'comparison': 'greater_than',
        'control_max_gap': float(control_max),
        'control_ok': control_ok,
        'target_mean_gap': float(target_mean),
        'target_std_gap': float(np.std(target_gaps)),
        'target_min_gap': float(target_min),
        'target_max_gap': float(max(target_gaps)),
        'target_cv': float(target_cv),
        't_statistic': float(t_stat),
        'p_value_one_sided': float(p_value_one_sided),
        'paired_t_statistic': float(t_paired),
        'paired_p_value': float(p_paired),
        'n_seeds': len(target_gaps),
        'details': f"Control (ratio=0): max|gap|={control_max:.6f}. "
                   f"Target (ratio=1): mean gap={target_mean:.4f}, "
                   f"std={np.std(target_gaps):.4f}, "
                   f"min={target_min:.4f}, max={max(target_gaps):.4f}. "
                   f"One-sided t-test p={p_value_one_sided:.4e}."
    }

def plot_gap_vs_ratio(results, fig_dir):
    """
    Plot mean gap +/- std as a function of lambda_1/lambda_2 ratio.
    X-axis: lambda_ratio (log scale for nonzero).
    Y-axis: normalized gap.
    Include horizontal lines at 1%, 5%, 10% thresholds.
    """
    ratios = sorted(set(r['lambda_ratio'] for r in results))
    means = []
    stds = []
    for ratio in ratios:
        gaps = [r['gap'] for r in results if r['lambda_ratio'] == ratio]
        means.append(np.mean(gaps))
        stds.append(np.std(gaps))
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(ratios, means, yerr=stds, fmt='o-', capsize=4, 
                color='#2c7bb6', linewidth=2, markersize=8)
    ax.axhline(y=0.01, color='green', linestyle='--', alpha=0.7, label='1% (control threshold)')
    ax.axhline(y=0.05, color='orange', linestyle='--', alpha=0.7, label='5% (fail threshold)')
    ax.axhline(y=0.10, color='red', linestyle='--', alpha=0.7, label='10% (pass threshold)')
    ax.set_xlabel('$\\lambda_1 / \\lambda_2$ ratio', fontsize=13)
    ax.set_ylabel('Normalized gap $(f_{elastic} - f_{convex}) / f_{elastic}$', fontsize=13)
    ax.set_title('H6: Elastic Net vs. Convex L2 Reformulation Gap', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'gap_vs_ratio.png'), dpi=300)
    plt.close()
    print(f"Saved: {fig_dir}/gap_vs_ratio.png")

def plot_boxplots(results, fig_dir):
    """Box plot of gap distribution at each ratio."""
    ratios = sorted(set(r['lambda_ratio'] for r in results))
    data = []
    labels = []
    for ratio in ratios:
        gaps = [r['gap'] for r in results if r['lambda_ratio'] == ratio]
        data.append(gaps)
        labels.append(f"{ratio}")
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.boxplot(data, labels=labels, patch_artist=True,
               boxprops=dict(facecolor='#b2d8d8', color='#2c7bb6'),
               medianprops=dict(color='red'))
    ax.axhline(y=0.10, color='red', linestyle='--', alpha=0.7)
    ax.axhline(y=0.01, color='green', linestyle='--', alpha=0.7)
    ax.set_xlabel('$\\lambda_1 / \\lambda_2$ ratio', fontsize=13)
    ax.set_ylabel('Normalized gap', fontsize=13)
    ax.set_title('Gap Distribution per Lambda Ratio', fontsize=14)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'gap_distribution_boxplot.png'), dpi=300)
    plt.close()
    print(f"Saved: {fig_dir}/gap_distribution_boxplot.png")

def plot_control_validation(results, fig_dir):
    """Scatter of control (ratio=0) gaps across seeds."""
    control = [r for r in results if r['lambda_ratio'] == 0.0]
    seeds = [r['seed'] for r in control]
    gaps = [r['gap'] for r in control]
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(seeds, gaps, color='#2c7bb6', alpha=0.7)
    ax.axhline(y=0.01, color='red', linestyle='--', label='1% threshold')
    ax.axhline(y=-0.01, color='red', linestyle='--')
    ax.set_xlabel('Seed', fontsize=13)
    ax.set_ylabel('Normalized gap', fontsize=13)
    ax.set_title('Control Validation: Pure L2 (ratio=0)', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'control_validation.png'), dpi=300)
    plt.close()
    print(f"Saved: {fig_dir}/control_validation.png")

def main():
    results_dir = sys.argv[1] if len(sys.argv) > 1 else 'experiments/H6/results'
    fig_dir = os.path.join(results_dir, 'figures')
    os.makedirs(fig_dir, exist_ok=True)
    
    results = load_results(results_dir)
    
    # Generate figures
    plot_gap_vs_ratio(results, fig_dir)
    plot_boxplots(results, fig_dir)
    plot_control_validation(results, fig_dir)
    
    # Evaluate base case
    evaluation = evaluate_base_case(results)
    eval_path = os.path.join(results_dir, 'base_case_evaluation.json')
    with open(eval_path, 'w') as f:
        json.dump(evaluation, f, indent=2)
    print(f"\nBase case evaluation saved to {eval_path}")
    print(f"Verdict: {evaluation['verdict']}")
    print(f"Details: {evaluation['details']}")

if __name__ == '__main__':
    main()
```

---

### Step 6: Ablation -- Non-Convex L2 Training Validation

**Script:** `experiments/H6/scripts/ablation_l2_nonconvex.py`
**Inputs:** Same data as main experiment, lambda_ratio=0, 5 seeds
**Outputs:** `experiments/H6/results/ablation_l2_nonconvex.json`
**Compute:** CPU, ~15 minutes
**Purpose:** Verify that the non-convex training with pure L2 (no L1 component) converges to the same optimum as the convex solver. This validates that both solvers are working correctly and that the gap in the main experiment is due to the elastic net, not solver bugs.

**Pseudocode:**
```python
"""
For seeds 0..4:
  1. Generate data (n=200, d=10)
  2. Solve convex L2 program -> f_convex
  3. Train non-convex L2-only (lambda1=0, lambda2=0.01) -> f_nonconvex
  4. Compute relative difference: |f_convex - f_nonconvex| / f_convex
  5. Assert relative difference < 1% for all seeds

If any seed fails: the convex-to-nonconvex mapping is broken; debug before
running the main experiment.
"""
# Uses same functions from convex_l2_solver.py and nonconvex_elastic_net.py
# with lambda1 = 0
```

**Key implementation notes for the coder:**
1. This ablation MUST be run and pass BEFORE the main experiment. It validates the entire pipeline.
2. If f_nonconvex and f_convex differ by more than 1% for pure L2, the likely causes are:
   - Incorrect beta mapping (beta should be 2*sqrt(lambda_2))
   - Insufficient non-convex restarts (increase from 50 to 200)
   - Insufficient convex solver tolerance (decrease eps from 1e-8 to 1e-10)
   - Insufficient training epochs (increase from 3000 to 10000)

---

## 6. Analysis Steps

**Script:** `experiments/H6/scripts/analyze.py` (Step 5 above)
**Reads:** `experiments/H6/results/raw_results.json`
**Produces:**
  - `experiments/H6/results/summary_table.csv` -- mean/std/min/max gap per ratio
  - `experiments/H6/results/figures/gap_vs_ratio.png` -- main result
  - `experiments/H6/results/figures/gap_distribution_boxplot.png` -- per-ratio distributions
  - `experiments/H6/results/figures/control_validation.png` -- control check
  - `experiments/H6/results/base_case_evaluation.json` -- formal pass/fail verdict

**Statistical tests performed:**
1. One-sample t-test at ratio=1: H0: mean gap <= 10%, one-sided
2. Paired t-test: ratio=0 gaps vs ratio=1 gaps
3. Monotonicity check: Spearman rho of gap vs. ratio for the 5 nonzero ratios

## 7. Expected Timeline

| Step | Description | Estimated Time | Compute |
|------|-------------|---------------|---------|
| Setup | Install packages, verify environment | 5 min | -- |
| Step 1 | Write utils.py | 5 min | -- |
| Step 2 | Write convex_l2_solver.py | 15 min | -- |
| Step 3 | Write nonconvex_elastic_net.py | 15 min | -- |
| Step 4 | Write run_experiment.py | 15 min | -- |
| Step 5 | Write analyze.py | 10 min | -- |
| Step 6 | Run ablation_l2_nonconvex.py (5 seeds) | 15 min | CPU |
| Step 6b | Debug if ablation fails | 0-30 min | CPU |
| Run | Execute run_experiment.py (120 configs) | 120-180 min | CPU |
| Analyze | Execute analyze.py | 2 min | CPU |
| **Total** | | **~3 hours** | |

## 8. Execution Commands (Exact)

Run from project root: `/Users/abhinavmallick/Github.nosync/Research-Workflow`

```bash
# 1. Install dependencies (once)
.venv/bin/pip install cvxpy torch scikit-learn matplotlib

# 2. Run ablation first (validates pipeline)
.venv/bin/python experiments/H6/scripts/ablation_l2_nonconvex.py

# 3. Run main experiment
.venv/bin/python experiments/H6/scripts/run_experiment.py \
    --n 200 --d 10 \
    --lambda_ratios 0,0.1,0.5,1.0,2.0,5.0 \
    --lambda2 0.01 \
    --seeds 20 \
    --width 100 \
    --restarts 50 \
    --max_patterns 200

# 4. Run analysis
.venv/bin/python experiments/H6/scripts/analyze.py experiments/H6/results
```

## 9. Troubleshooting

- **If CVXPY solver fails (status "infeasible" or "unbounded"):** Try a different solver. Replace `cp.SCS` with `cp.ECOS` or install and use `cp.MOSEK`. Also try increasing `max_iters` to 100000 or relaxing `eps` to 1e-6.
- **If convex solve takes >5 minutes per config:** Reduce `max_patterns` from 200 to 100. The number of unique activation patterns may be small for low-dimensional data.
- **If non-convex training does not converge:** Check the loss curve. If loss plateaus early, increase epochs from 3000 to 5000. If loss is noisy, reduce learning rate to 0.0001. If all restarts converge to similar high loss, the problem may be poorly conditioned -- try normalizing X columns.
- **If ablation fails (L2 gap > 1%):** This is the most critical failure. Debug the beta mapping first: the convex beta should be `2 * sqrt(lambda_2)`. If this is correct, increase restarts to 200 and epochs to 5000 for the non-convex solver. If the convex solver is inaccurate, try MOSEK instead of SCS.
- **If memory exceeds limit:** The CVXPY problem with P=200 patterns, d=10 has ~4000 variables. This should not exceed 2GB. If it does, reduce max_patterns to 50.
- **If step takes >2x estimated time:** Reduce the seed count from 20 to 10 for a preliminary run. If results are clear (gap >> 10% or gap << 5%), the reduced run may be sufficient.
- **If SCS reports "inaccurate" solution:** The solution may still be usable if the residuals are small. Check `prob.solver_stats` for primal/dual residuals. If residuals < 1e-6, accept the solution. Otherwise, increase max_iters or switch solvers.

## 10. File Manifest

| File | Type | Purpose |
|------|------|---------|
| `experiments/H6/scripts/utils.py` | Python module | Data generation, seeds, metrics |
| `experiments/H6/scripts/convex_l2_solver.py` | Python module | CVXPY convex L2 reformulation |
| `experiments/H6/scripts/nonconvex_elastic_net.py` | Python module | PyTorch elastic net training |
| `experiments/H6/scripts/run_experiment.py` | Python script (main) | Full experiment grid runner |
| `experiments/H6/scripts/analyze.py` | Python script | Figures + base case evaluation |
| `experiments/H6/scripts/ablation_l2_nonconvex.py` | Python script | Pipeline validation ablation |
| `experiments/H6/results/raw_results.json` | JSON | Per-seed, per-ratio raw results |
| `experiments/H6/results/summary_table.csv` | CSV | Aggregated statistics |
| `experiments/H6/results/figures/gap_vs_ratio.png` | PNG 300dpi | Main result figure |
| `experiments/H6/results/figures/gap_distribution_boxplot.png` | PNG 300dpi | Per-ratio box plots |
| `experiments/H6/results/figures/control_validation.png` | PNG 300dpi | Control check |
| `experiments/H6/results/base_case_evaluation.json` | JSON | Formal pass/fail verdict |
| `experiments/H6/results/ablation_l2_nonconvex.json` | JSON | Ablation results |
| `experiments/H6/status.yaml` | YAML | Experiment status tracker |

## 11. Critical Correctness Checks

These checks MUST be satisfied for the experiment to be valid:

1. **Beta mapping:** The convex program's group-L1 regularization beta must equal `2 * sqrt(lambda_2)` where lambda_2 is the L2-squared weight decay in the non-convex formulation. This is the rescaling lemma.
2. **Control validation:** At lambda_ratio = 0 (pure L2), the gap between non-convex and convex must be < 1% for ALL seeds. If not, the experiment infrastructure is broken.
3. **Objective consistency:** Both the convex and non-convex formulations must use the same data loss: `(1/2n) ||y - f(X)||^2`. The regularization terms differ (convex uses group-L1; non-convex uses elastic net), but the data fidelity term must match.
4. **Gap direction:** The gap is computed as `(f_elastic - f_convex) / f_elastic`. A positive gap means the elastic net optimum has higher total loss than the convex L2 optimum. But this interpretation needs care: f_elastic includes L1 penalty while f_convex does not. The correct comparison is: given the elastic net objective, how well does the convex L2 solution perform? This means evaluating the convex solution's weights under the elastic net loss function. See the note below.

**Important clarification on gap computation:**
The methodology specifies: "gap = (f_elastic - f_convex) / f_elastic" where f_elastic is the non-convex elastic net optimum and f_convex is the convex L2 optimum. These are optimized under DIFFERENT objectives (elastic net vs. pure L2). The gap measures whether the convex L2 reformulation can approximate the elastic net solution. A large positive gap means the elastic net finds a fundamentally different (and better, under the elastic net objective) solution than the convex L2 framework can.

However, the coder should ALSO compute `f_convex_elastic = elastic_net_loss(convex_weights)` -- evaluating the convex solution under the elastic net objective. This gives a second gap: `(f_convex_elastic - f_elastic) / f_elastic`, which directly measures how suboptimal the convex L2 solution is when evaluated under the elastic net criterion. Record BOTH gaps in raw_results.json.
