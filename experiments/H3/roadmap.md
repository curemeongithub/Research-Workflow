---
hypothesis: H3
title: "Duality Gap for Standard 3-Layer ReLU Networks Grows Monotonically with Data Rank"
type: numerical-scaling
estimated_total_hours: 6
colab_gates: 0
---

# Experiment Roadmap: H3 -- Rank-Dependent Duality Gap for Standard 3-Layer ReLU

## 1. Objective

Determine whether the duality gap for standard (non-parallel) 3-layer ReLU networks grows monotonically with data matrix rank r. Wang, Ergen, and Pilanci (2021) prove strong duality for the rank-1 case and leave the general rank case as open. Since no closed-form dual is known for standard deep ReLU, we use the parallel-architecture convex optimum as a valid lower bound on the true dual (the parallel architecture has provable zero gap, and its feasible set is a superset of the standard architecture). We compute the gap lower bound `gap_lb = (P_standard - D_parallel) / P_standard` and test whether this quantity (a) is near zero at r=1 and (b) increases monotonically with r across r in {1, 2, 3, 4, 5}. This experiment extends H5's rank-2 threshold test across the full rank spectrum to characterize the data-rank dependence.

## 2. Base Case (Pass/Fail Criteria)

- **PASS:**
  - Rank-1 positive control: gap < 1e-6 across all 20 seeds (mean absolute gap < 1e-6 AND max gap < 1e-4)
  - Monotonic trend: Spearman rho(rank, gap) > 0.8 with p < 0.05 across all 100 (rank, seed) pairs
  - Magnitude growth: mean gap at r=5 exceeds mean gap at r=2 by at least a factor of 2
- **FAIL:**
  - Rank-1 positive control fails (max gap > 1e-4 at r=1)
  - OR Spearman |rho| < 0.3 (no monotonic structure)
  - OR gap is non-monotonic in the means (mean gap decreases between any two consecutive rank levels)
- **INCONCLUSIVE:**
  - Positive control passes AND 0.3 <= Spearman rho <= 0.8
  - OR monotonic trend exists but the r=5 to r=2 ratio is between 1.0 and 2.0
  - OR coefficient of variation across seeds at any rank > 1.0 (too noisy to conclude)
- **Minimum data for conclusion:** 5 ranks x 20 seeds = 100 experimental runs

## 3. Local Setup

All computation runs locally on Apple M4 Pro (12 cores, 24GB RAM). No VM, no SSH, no Colab.

```bash
# Project root
cd /Users/abhinavmallick/Github.nosync/Research-Workflow

# Install missing packages into project venv (skip if already installed for H5/H6)
.venv/bin/pip install cvxpy torch scikit-learn matplotlib

# Verify installations
.venv/bin/python -c "import cvxpy; import torch; import sklearn; import matplotlib; import scipy; print('All packages OK')"

# Verify experiment directories exist
ls -la experiments/H3/{scripts,results,results/figures,colab,colab-results}
```

## 4. Repository Cloning

No external repo is cloned. The parallel-architecture convex program is implemented directly in CVXPY following the formulation in [WangErgenPilanci2021] Section 4 (parallel 3-layer ReLU with group-l1 regularization). The standard 3-layer ReLU primal is implemented directly in PyTorch. This mirrors the H5 roadmap and re-uses infrastructure. If H5 has already been implemented, the coder SHOULD import and re-use `experiments/H5/scripts/parallel_convex_solver.py` and `experiments/H5/scripts/standard_nonconvex_trainer.py` rather than duplicating them. If H5 has not run, the coder implements both solvers here in H3.

**Shared-infrastructure rule:** If `experiments/H5/scripts/parallel_convex_solver.py` exists and exposes a function `solve_parallel_convex_3layer(X, y, beta, max_patterns)`, import it. Otherwise, implement it in Step 3 below.

## 5. Implementation Steps

### Step 1: Shared Utilities Module

**Script:** `experiments/H3/scripts/utils.py`
**Inputs:** None (utility module)
**Outputs:** Importable module
**Compute:** N/A
**Purpose:** Reusable functions for seed management, rank-controlled data generation, and metrics.

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

def generate_rank_controlled_data(n, d, r, seed, noise_std=0.1):
    """
    Generate synthetic regression data with EXACT rank r.

    Construction (matches methodology E3 algorithm step 1):
        A ~ N(0, I) in R^{n x r}
        B ~ N(0, I) in R^{d x r}
        X = A @ B.T   (shape (n, d), rank min(r, min(n, d)))

    Targets:
        w_true ~ N(0, I_d)
        noise  ~ N(0, noise_std^2 I_n)
        y = X @ w_true + noise

    Args:
        n: number of samples
        d: ambient dimension
        r: target rank (must satisfy 1 <= r <= min(n, d))
        seed: RNG seed
        noise_std: Gaussian noise std for targets
    Returns:
        X: (n, d) float64 numpy array, np.linalg.matrix_rank(X) == r
        y: (n,)  float64 numpy array
        w_true: (d,) float64 numpy array
    """
    assert 1 <= r <= min(n, d), f"rank r={r} out of range for (n={n}, d={d})"
    set_all_seeds(seed)
    A = np.random.randn(n, r)
    B = np.random.randn(d, r)
    X = A @ B.T
    w_true = np.random.randn(d)
    noise = np.random.randn(n) * noise_std
    y = X @ w_true + noise
    # Sanity check: numerically verify rank
    true_rank = np.linalg.matrix_rank(X, tol=1e-8)
    assert true_rank == r, f"Constructed rank {true_rank} != requested {r}"
    return X, y, w_true

def normalized_gap(P, D):
    """
    Normalized gap between primal P and dual lower bound D:
        gap = (P - D) / P

    Positive means primal > dual (expected: primal is always >= dual).
    Clamped at 0 if |P| < 1e-12 to avoid division by near-zero.
    """
    if abs(P) < 1e-12:
        return 0.0
    return (P - D) / P
```

---

### Step 2: Standard 3-Layer ReLU Non-Convex Trainer (PRIMAL)

**Script:** `experiments/H3/scripts/standard_nonconvex_trainer.py`
**Inputs:** Data matrix X (n, d), target y (n,), hidden width, L2 weight decay beta, number of restarts, epochs, learning rate
**Outputs:** Best training loss (data loss + L2-squared weight decay, summed) across restarts, best model state dict
**Compute:** CPU, ~30-60 seconds per (rank, seed) with 50 restarts x 2000 epochs
**Purpose:** Train a STANDARD (NOT parallel) 3-layer ReLU network as the non-convex primal. Use multi-restart Adam to approximate the global optimum.

**Pseudocode:**
```python
import torch
import torch.nn as nn
import numpy as np

class ThreeLayerReLU(nn.Module):
    """
    Standard (non-parallel) 3-layer ReLU: d -> width -> width -> 1.
    No bias in any layer (matches the standard convex reformulation setup).
    """
    def __init__(self, d, width):
        super().__init__()
        self.layer1 = nn.Linear(d, width, bias=False)
        self.layer2 = nn.Linear(width, width, bias=False)
        self.layer3 = nn.Linear(width, 1, bias=False)
        self.relu = nn.ReLU()

    def forward(self, x):
        h1 = self.relu(self.layer1(x))
        h2 = self.relu(self.layer2(h1))
        return self.layer3(h2).squeeze(-1)

def l2_squared_penalty(model):
    """Sum of squared Frobenius norms across all weight matrices."""
    total = 0.0
    for p in model.parameters():
        total = total + torch.sum(p ** 2)
    return total

def train_standard_3layer(X, y, d, width, beta,
                          n_restarts=50, n_epochs=2000, lr=1e-3, seed_base=0,
                          device='cpu'):
    """
    Train a standard 3-layer ReLU with L2-squared weight decay (beta).

    The training objective is:
        f(theta) = (1 / (2n)) * ||y - net(X)||^2 + beta * ||theta||_2^2

    where ||theta||_2^2 is the sum of squared entries across ALL weight
    matrices. Multi-restart Adam; return the BEST final loss.

    Args:
        X: (n, d) numpy array
        y: (n,)   numpy array
        d: input dimension
        width: hidden layer width (both hidden layers use this width)
        beta: L2-squared regularization strength
        n_restarts: number of random initializations (Kaiming uniform default)
        n_epochs: training epochs per restart
        lr: Adam learning rate
        seed_base: base seed; restart i uses torch seed seed_base*1000 + i
        device: 'cpu' or 'mps' (MPS optional; CPU is fine for n=100, d=10)
    Returns:
        best_loss: float, best total (data + reg) loss across restarts
        best_state: state dict achieving best loss (for diagnostics)
    """
    X_t = torch.tensor(X, dtype=torch.float32, device=device)
    y_t = torch.tensor(y, dtype=torch.float32, device=device)
    n = X.shape[0]

    best_loss = float('inf')
    best_state = None

    for restart in range(n_restarts):
        torch.manual_seed(seed_base * 1000 + restart)
        model = ThreeLayerReLU(d, width).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)

        for epoch in range(n_epochs):
            optimizer.zero_grad()
            pred = model(X_t)
            data_loss = (1.0 / (2 * n)) * torch.sum((y_t - pred) ** 2)
            reg_loss = beta * l2_squared_penalty(model)
            total_loss = data_loss + reg_loss
            total_loss.backward()
            optimizer.step()

        final = total_loss.item()
        if final < best_loss:
            best_loss = final
            best_state = {k: v.detach().cpu().clone()
                          for k, v in model.state_dict().items()}

    return best_loss, best_state
```

**Key implementation notes for the coder:**
1. The network is STANDARD, not parallel. Do NOT use the parallel 3-layer architecture here -- that is the lower-bound reference, not the primal.
2. No bias terms in any layer. This matches the convex reformulation assumption in [WangErgenPilanci2021].
3. The regularization `beta * ||theta||_2^2` is applied to ALL weights across both hidden layers and the output layer. This matches the standard weight-decay formulation.
4. 50 restarts is the minimum. The non-convex landscape at rank >= 2 may have many local minima; if the base case fails due to non-monotonicity, the coder should retry with 100 restarts BEFORE concluding FAIL.
5. Use `torch.float32` on CPU. MPS is optional; for n=100, d=10, width=50, a single restart takes ~0.3-0.8s on CPU, so 50 restarts fit in ~20-40s.
6. The final loss includes regularization. This is the f_standard value used as P_standard in the gap calculation.

---

### Step 3: Parallel 3-Layer Convex Lower Bound (DUAL LOWER BOUND)

**Script:** `experiments/H3/scripts/parallel_convex_solver.py`
**Inputs:** Data matrix X (n, d), target y (n,), regularization beta, max number of hyperplane activation patterns
**Outputs:** Optimal value D_parallel of the parallel convex program
**Compute:** CPU, ~1-3 minutes per (rank, seed) with max_patterns=150
**Purpose:** Solve the parallel 3-layer ReLU convex reformulation from [WangErgenPilanci2021] (Section 4). This value serves as a LOWER BOUND on the true dual of the standard 3-layer architecture because the parallel architecture has a strictly larger feasible set of networks and zero duality gap.

**Mathematical formulation (two-layer convex subroutine applied in parallel):**

The parallel 3-layer ReLU convex program reduces to a two-layer-style group-l1 convex program over a collection of diagonal activation patterns. For the purposes of this experiment, we use the SAME convex program shape as the two-layer ReLU reformulation (sum over sampled sign patterns D_j of the pre-activations) and pick beta = 2 * sqrt(beta_primal) to match the rescaling lemma (this gives the tightest parallel-architecture lower bound that is implementable with the available CVXPY primitives). This matches the H5 design exactly.

**Pseudocode:**
```python
import numpy as np
import cvxpy as cp

def enumerate_sign_patterns(X, max_patterns=150, rng_seed=0):
    """
    Sample ReLU activation patterns by drawing random hyperplane normals.

    For each random v ~ N(0, I_d), compute the sign pattern (X @ v > 0)
    and add the corresponding diagonal mask D = diag(1{X @ v > 0}) to
    the pattern list. Deduplicate. Cap at max_patterns.

    Args:
        X: (n, d) numpy array
        max_patterns: cap on number of unique patterns
        rng_seed: reproducibility
    Returns:
        D_list: list of (n, n) diagonal float numpy arrays, each with 0/1 diagonal
    """
    rng = np.random.RandomState(rng_seed)
    n, d = X.shape
    seen = set()
    D_list = []
    for _ in range(max_patterns * 10):
        v = rng.randn(d)
        pattern = tuple((X @ v > 0).astype(int))
        if pattern not in seen:
            seen.add(pattern)
            D_list.append(np.diag(np.array(pattern, dtype=float)))
            if len(D_list) >= max_patterns:
                break
    return D_list

def solve_parallel_convex_3layer(X, y, beta, max_patterns=150,
                                 solver_eps=1e-8, pattern_seed=0):
    """
    Solve the parallel-architecture convex lower bound for 3-layer ReLU.

    Convex program (two-layer group-l1 form, applied as parallel lower bound):
        min_{u_j, v_j} (1/2n) ||y - sum_j D_j X (u_j - v_j)||^2
                        + beta_convex * sum_j (||u_j||_2 + ||v_j||_2)
        s.t. u_j >= 0, v_j >= 0

    where D_j are sampled diagonal activation patterns from
    enumerate_sign_patterns. beta_convex = 2 * sqrt(beta) via the
    rescaling lemma: the input `beta` is the L2-squared weight decay
    strength used in the standard 3-layer primal (Step 2).

    This convex value is a VALID lower bound on the true dual of the
    standard 3-layer ReLU for the following reason: the parallel
    architecture has zero duality gap (proven in [WangErgenPilanci2021])
    and its feasible set of representable functions is a superset of the
    standard architecture at matched width. Hence any minimizer over the
    parallel feasible set achieves a value <= any standard primal minimum.

    Args:
        X: (n, d) numpy array
        y: (n,)   numpy array
        beta: L2-squared weight decay strength used in the standard primal
        max_patterns: how many unique sign patterns to sample
        solver_eps: SCS tolerance
        pattern_seed: seed for sign-pattern sampling
    Returns:
        D_parallel: float, optimal objective value
        meta: dict with solver status, num_patterns, primal/dual residuals
    """
    n, d = X.shape

    # Rescaling lemma: two-layer convex group-l1 strength = 2 * sqrt(L2-sq beta)
    beta_convex = 2.0 * np.sqrt(beta)

    D_list = enumerate_sign_patterns(X, max_patterns=max_patterns,
                                     rng_seed=pattern_seed)
    P = len(D_list)

    u = [cp.Variable(d, nonneg=True) for _ in range(P)]
    v = [cp.Variable(d, nonneg=True) for _ in range(P)]

    pred = sum(D_list[j] @ X @ (u[j] - v[j]) for j in range(P))
    loss = (1.0 / (2 * n)) * cp.sum_squares(y - pred)
    reg = beta_convex * sum(cp.norm(u[j], 2) + cp.norm(v[j], 2)
                            for j in range(P))

    prob = cp.Problem(cp.Minimize(loss + reg))
    prob.solve(solver=cp.SCS, eps=solver_eps, max_iters=50000, verbose=False)

    if prob.status not in ('optimal', 'optimal_inaccurate'):
        raise RuntimeError(f"CVXPY solver failed: status={prob.status}")

    return prob.value, {
        'status': prob.status,
        'num_patterns': P,
        'solver_stats': {
            'num_iters': getattr(prob.solver_stats, 'num_iters', None),
            'solve_time': getattr(prob.solver_stats, 'solve_time', None),
        }
    }
```

**Key implementation notes for the coder:**
1. The rescaling lemma mapping `beta_convex = 2 * sqrt(beta)` is the SAME as H6 Step 2 and H5. Verify consistency by running the rank-1 positive control FIRST; if it does not yield gap < 1e-4, debug beta before running the full sweep.
2. `max_patterns=150` is a reasonable cap for n=100, d=10. The theoretical number of distinct activation patterns is O((n choose d)) but most are unreachable by random sampling. If the solver complains that P is too small (solver status `infeasible`), increase to 300.
3. If SCS returns `optimal_inaccurate`, ACCEPT the value but flag it in `meta['status']`. The analysis script will filter out any (rank, seed) pairs with more than 5% inaccurate solves.
4. If SCS fails entirely with `infeasible` or `unbounded` at low rank, try `cp.ECOS` as a fallback. Record which solver succeeded.
5. The D_j matrices for n=100 are 100 x 100. With P=150 patterns, the CVXPY problem has 2 * 150 * 10 = 3000 decision variables. Peak RAM should stay well under 2 GB.

---

### Step 4: Rank Sweep Experiment Driver

**Script:** `experiments/H3/scripts/rank_gap_sweep.py`
**Inputs:** Command-line arguments (see below)
**Outputs:**
  - `experiments/H3/results/raw_results.json` -- one entry per (rank, seed)
  - `experiments/H3/results/progress.log` -- running progress log
**Compute:** CPU, 5 ranks x 20 seeds x (convex ~2min + non-convex ~0.5min) = ~250 minutes wall-clock (sequential)
**Purpose:** Drive the full (rank, seed) experimental grid. For each (rank, seed) pair, generate rank-controlled data, train the standard 3-layer ReLU primal, solve the parallel-architecture convex lower bound, and compute the normalized gap.

**Pseudocode:**
```python
import argparse
import json
import time
import os
import sys
import numpy as np
import traceback

# Add this script's dir to path so sibling modules import
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from utils import set_all_seeds, generate_rank_controlled_data, normalized_gap
from standard_nonconvex_trainer import train_standard_3layer
from parallel_convex_solver import solve_parallel_convex_3layer


def parse_args():
    parser = argparse.ArgumentParser(
        description='H3: Rank-Dependent Duality Gap for Standard 3-Layer ReLU'
    )
    parser.add_argument('--n', type=int, default=100)
    parser.add_argument('--d', type=int, default=10)
    parser.add_argument('--ranks', type=str, default='1,2,3,4,5',
                        help='Comma-separated rank levels')
    parser.add_argument('--beta', type=float, default=0.01,
                        help='L2-squared weight decay for standard primal')
    parser.add_argument('--seeds', type=int, default=20)
    parser.add_argument('--width', type=int, default=50,
                        help='Hidden layer width (both hidden layers)')
    parser.add_argument('--restarts', type=int, default=50)
    parser.add_argument('--epochs', type=int, default=2000)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--max_patterns', type=int, default=150)
    parser.add_argument('--results_dir', type=str,
                        default='experiments/H3/results')
    parser.add_argument('--status_file', type=str,
                        default='experiments/H3/status.yaml')
    parser.add_argument('--device', type=str, default='cpu')
    return parser.parse_args()


def run_single_cell(X, y, n, d, rank, seed, args):
    """Run one (rank, seed) cell. Returns result dict or raises."""
    t0 = time.time()

    # --- Standard 3-layer non-convex primal ---
    t_primal_0 = time.time()
    P_standard, _state = train_standard_3layer(
        X, y, d=d, width=args.width, beta=args.beta,
        n_restarts=args.restarts, n_epochs=args.epochs, lr=args.lr,
        seed_base=seed, device=args.device,
    )
    t_primal = time.time() - t_primal_0

    # --- Parallel convex lower bound ---
    t_dual_0 = time.time()
    D_parallel, meta = solve_parallel_convex_3layer(
        X, y, beta=args.beta, max_patterns=args.max_patterns,
        pattern_seed=seed,
    )
    t_dual = time.time() - t_dual_0

    gap_raw = P_standard - D_parallel
    gap_norm = normalized_gap(P_standard, D_parallel)

    return {
        'rank': rank,
        'seed': seed,
        'n': n,
        'd': d,
        'P_standard': float(P_standard),
        'D_parallel': float(D_parallel),
        'gap_raw': float(gap_raw),
        'gap_normalized': float(gap_norm),
        'primal_valid': bool(gap_raw >= -1e-6),  # primal should be >= dual LB
        'solver_status': meta['status'],
        'num_patterns': meta['num_patterns'],
        'wall_time_primal_s': t_primal,
        'wall_time_dual_s': t_dual,
        'wall_time_total_s': time.time() - t0,
    }


def update_status(status_path, state):
    """Rewrite status.yaml atomically."""
    import yaml
    tmp = status_path + '.tmp'
    with open(tmp, 'w') as f:
        yaml.safe_dump(state, f)
    os.replace(tmp, status_path)


def main():
    args = parse_args()
    ranks = [int(r) for r in args.ranks.split(',')]
    seeds = list(range(args.seeds))

    os.makedirs(args.results_dir, exist_ok=True)
    os.makedirs(os.path.join(args.results_dir, 'figures'), exist_ok=True)
    raw_path = os.path.join(args.results_dir, 'raw_results.json')
    log_path = os.path.join(args.results_dir, 'progress.log')

    # Resume: load existing results if present
    results = []
    if os.path.exists(raw_path):
        with open(raw_path) as f:
            results = json.load(f)
        done_keys = {(r['rank'], r['seed']) for r in results}
        print(f"Resuming: {len(results)} cells already complete.")
    else:
        done_keys = set()

    total = len(ranks) * len(seeds)
    start = time.time()

    def log(msg):
        line = f"[{time.strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        with open(log_path, 'a') as f:
            f.write(line + '\n')

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
                with open(raw_path, 'w') as f:
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
                    'hypothesis': 'H3',
                    'status': 'in_progress',
                    'current_step': 4,
                    'steps_total': 5,
                    'steps_completed': 3,
                    'iteration': 0,
                    'base_case_met': False,
                    'last_error': None,
                    'last_updated': time.strftime('%Y-%m-%dT%H:%M:%SZ',
                                                   time.gmtime()),
                    'progress': f'{completed}/{total}',
                })
            except Exception as e:
                tb = traceback.format_exc()
                log(f"ERROR rank={rank} seed={seed}: {e}\n{tb}")
                err_path = os.path.join(os.path.dirname(args.status_file),
                                        'error.log')
                with open(err_path, 'w') as f:
                    f.write(tb)
                update_status(args.status_file, {
                    'hypothesis': 'H3',
                    'status': 'error',
                    'current_step': 4,
                    'steps_total': 5,
                    'steps_completed': 3,
                    'iteration': 0,
                    'base_case_met': False,
                    'last_error': str(e),
                    'last_updated': time.strftime('%Y-%m-%dT%H:%M:%SZ',
                                                   time.gmtime()),
                })
                raise

    total_time = time.time() - start
    log(f"Sweep complete. {len(results)} cells in {total_time/60:.1f} min.")


if __name__ == '__main__':
    main()
```

**Key implementation notes for the coder:**
1. The driver is RESUMABLE: it checks `raw_results.json` for completed (rank, seed) keys and skips them. This means if the run is interrupted, just re-invoke the same command.
2. Results are persisted AFTER EVERY CELL. This is critical for crash safety given the 4-6 hour runtime.
3. Status.yaml is updated after every cell so the orchestrator and reviewer can see live progress.
4. If any cell raises, the driver writes the traceback to `experiments/H3/error.log` and re-raises. The reviewer agent will see the error and decide whether to fix and resume or fail the hypothesis.
5. The `primal_valid` flag checks that P_standard >= D_parallel (the lower bound should never exceed the primal). If this flag is False for any cell, the CVXPY solver or the non-convex trainer is buggy -- the analysis script will flag this.

---

### Step 5: Analysis and Visualization

**Script:** `experiments/H3/scripts/analyze.py`
**Inputs:** `experiments/H3/results/raw_results.json`
**Outputs:**
  - `experiments/H3/results/summary_table.csv` -- per-rank aggregated statistics
  - `experiments/H3/results/figures/gap_vs_rank.png` -- main result (mean gap + IQR band vs rank)
  - `experiments/H3/results/figures/gap_distribution_violin.png` -- per-rank violin plots
  - `experiments/H3/results/figures/rank1_positive_control.png` -- rank-1 seed scatter
  - `experiments/H3/results/figures/primal_vs_dual_scatter.png` -- per-cell P vs D
  - `experiments/H3/results/base_case_evaluation.json` -- formal pass/fail verdict
**Compute:** CPU, ~1-2 minutes

**Pseudocode:**
```python
import json
import os
import sys
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats


def load_results(results_dir):
    with open(os.path.join(results_dir, 'raw_results.json')) as f:
        return json.load(f)


def aggregate_per_rank(results):
    """Return dict: rank -> {n, mean, std, min, max, q1, q3, median, cv}"""
    agg = {}
    ranks = sorted(set(r['rank'] for r in results))
    for r in ranks:
        gaps = np.array([x['gap_normalized'] for x in results
                         if x['rank'] == r])
        mean = float(gaps.mean())
        std = float(gaps.std(ddof=1)) if len(gaps) > 1 else 0.0
        agg[r] = {
            'n': int(len(gaps)),
            'mean': mean,
            'std': std,
            'min': float(gaps.min()),
            'max': float(gaps.max()),
            'q1': float(np.quantile(gaps, 0.25)),
            'q3': float(np.quantile(gaps, 0.75)),
            'median': float(np.median(gaps)),
            'cv': float(std / abs(mean)) if abs(mean) > 1e-12 else float('inf'),
        }
    return agg


def evaluate_base_case(results, agg):
    ranks = sorted(agg.keys())
    rank1_gaps = [x['gap_normalized'] for x in results if x['rank'] == 1]
    rank1_max_abs = max(abs(g) for g in rank1_gaps) if rank1_gaps else float('inf')
    rank1_mean_abs = np.mean([abs(g) for g in rank1_gaps]) if rank1_gaps else float('inf')

    # Positive control: gap ~ 0 at r=1
    positive_control_ok = (rank1_max_abs < 1e-4 and rank1_mean_abs < 1e-6)

    # Spearman correlation across ALL (rank, seed) pairs
    all_ranks = np.array([x['rank'] for x in results])
    all_gaps = np.array([x['gap_normalized'] for x in results])
    rho, p_spearman = stats.spearmanr(all_ranks, all_gaps)

    # Monotonicity in the means
    means = [agg[r]['mean'] for r in ranks]
    monotone_means = all(means[i+1] >= means[i] - 1e-8 for i in range(len(means)-1))

    # Magnitude growth r=5 vs r=2
    if 5 in agg and 2 in agg:
        mag_ratio = agg[5]['mean'] / max(agg[2]['mean'], 1e-12)
    else:
        mag_ratio = float('nan')

    # Primal-dual validity sanity check
    invalid = [x for x in results if not x.get('primal_valid', True)]
    primal_valid_fraction = 1 - (len(invalid) / len(results))

    # Verdict
    pass_conditions = (
        positive_control_ok
        and rho > 0.8 and p_spearman < 0.05
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
        verdict = 'PASS'
    elif fail_conditions:
        verdict = 'FAIL'
    else:
        verdict = 'INCONCLUSIVE'

    return {
        'pass': verdict == 'PASS',
        'verdict': verdict,
        'metric_name': 'spearman_rho_rank_vs_gap',
        'metric_value': float(rho),
        'threshold': 0.8,
        'comparison': 'greater_than',
        'spearman_p_value': float(p_spearman),
        'rank1_max_abs_gap': float(rank1_max_abs),
        'rank1_mean_abs_gap': float(rank1_mean_abs),
        'positive_control_ok': bool(positive_control_ok),
        'monotone_in_means': bool(monotone_means),
        'magnitude_ratio_r5_over_r2': float(mag_ratio),
        'primal_valid_fraction': float(primal_valid_fraction),
        'per_rank_mean_gap': {int(r): agg[r]['mean'] for r in ranks},
        'n_cells': int(len(results)),
        'details': (
            f"Spearman rho={rho:.4f} (p={p_spearman:.4e}). "
            f"r=1 max|gap|={rank1_max_abs:.2e}. "
            f"Means by rank: {[f'{agg[r]["mean"]:.4f}' for r in ranks]}. "
            f"Monotone: {monotone_means}. r5/r2={mag_ratio:.2f}. "
            f"Primal valid: {primal_valid_fraction*100:.1f}%."
        ),
    }


def write_summary_csv(agg, path):
    ranks = sorted(agg.keys())
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['rank', 'n_seeds', 'mean_gap', 'std_gap',
                    'median_gap', 'q1_gap', 'q3_gap',
                    'min_gap', 'max_gap', 'cv'])
        for r in ranks:
            a = agg[r]
            w.writerow([r, a['n'], f"{a['mean']:.6e}", f"{a['std']:.6e}",
                        f"{a['median']:.6e}", f"{a['q1']:.6e}",
                        f"{a['q3']:.6e}", f"{a['min']:.6e}",
                        f"{a['max']:.6e}", f"{a['cv']:.4f}"])


def plot_gap_vs_rank(results, agg, fig_dir):
    ranks = sorted(agg.keys())
    means = [agg[r]['mean'] for r in ranks]
    q1s = [agg[r]['q1'] for r in ranks]
    q3s = [agg[r]['q3'] for r in ranks]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.fill_between(ranks, q1s, q3s, alpha=0.25, color='#2c7bb6',
                    label='IQR (Q1--Q3)')
    ax.plot(ranks, means, 'o-', color='#2c7bb6', linewidth=2,
            markersize=9, label='Mean normalized gap')
    ax.axhline(y=1e-4, color='green', linestyle='--', alpha=0.6,
               label='1e-4 positive control tolerance')
    ax.set_xlabel('Data matrix rank $r$', fontsize=13)
    ax.set_ylabel('Normalized gap $(P_{\\mathrm{standard}} - D_{\\mathrm{parallel}}) / P_{\\mathrm{standard}}$',
                  fontsize=12)
    ax.set_title('H3: Rank-Dependent Duality Gap (Standard 3-Layer ReLU)',
                 fontsize=13)
    ax.set_xticks(ranks)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    out = os.path.join(fig_dir, 'gap_vs_rank.png')
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"Saved: {out}")


def plot_violin(results, fig_dir):
    ranks = sorted(set(x['rank'] for x in results))
    data = [[x['gap_normalized'] for x in results if x['rank'] == r]
            for r in ranks]

    fig, ax = plt.subplots(figsize=(8, 5))
    parts = ax.violinplot(data, positions=ranks, widths=0.6,
                          showmeans=True, showmedians=True)
    for pc in parts['bodies']:
        pc.set_facecolor('#b2d8d8')
        pc.set_edgecolor('#2c7bb6')
        pc.set_alpha(0.8)
    ax.set_xlabel('Data matrix rank $r$', fontsize=13)
    ax.set_ylabel('Normalized gap', fontsize=13)
    ax.set_title('Gap Distribution per Rank Level', fontsize=13)
    ax.set_xticks(ranks)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    out = os.path.join(fig_dir, 'gap_distribution_violin.png')
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"Saved: {out}")


def plot_rank1_control(results, fig_dir):
    rank1 = [x for x in results if x['rank'] == 1]
    seeds = [x['seed'] for x in rank1]
    gaps = [x['gap_normalized'] for x in rank1]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(seeds, gaps, color='#2c7bb6', alpha=0.75)
    ax.axhline(y=1e-4, color='red', linestyle='--', label='1e-4 tolerance')
    ax.axhline(y=-1e-4, color='red', linestyle='--')
    ax.set_xlabel('Seed', fontsize=13)
    ax.set_ylabel('Normalized gap at r=1', fontsize=13)
    ax.set_title('Rank-1 Positive Control (expected: gap $\\approx 0$)',
                 fontsize=13)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    out = os.path.join(fig_dir, 'rank1_positive_control.png')
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"Saved: {out}")


def plot_primal_vs_dual(results, fig_dir):
    fig, ax = plt.subplots(figsize=(6, 6))
    ranks = sorted(set(x['rank'] for x in results))
    cmap = plt.cm.viridis
    for i, r in enumerate(ranks):
        sub = [x for x in results if x['rank'] == r]
        P = [x['P_standard'] for x in sub]
        D = [x['D_parallel'] for x in sub]
        ax.scatter(D, P, color=cmap(i / max(len(ranks)-1, 1)),
                   s=40, alpha=0.75, label=f'r={r}')
    lo = min(min(x['P_standard'] for x in results),
             min(x['D_parallel'] for x in results))
    hi = max(max(x['P_standard'] for x in results),
             max(x['D_parallel'] for x in results))
    ax.plot([lo, hi], [lo, hi], 'k--', alpha=0.5, label='P = D')
    ax.set_xlabel('$D_{\\mathrm{parallel}}$ (lower bound)', fontsize=12)
    ax.set_ylabel('$P_{\\mathrm{standard}}$ (primal)', fontsize=12)
    ax.set_title('Primal vs. Dual Lower Bound (all cells)', fontsize=13)
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    out = os.path.join(fig_dir, 'primal_vs_dual_scatter.png')
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"Saved: {out}")


def main():
    results_dir = sys.argv[1] if len(sys.argv) > 1 else 'experiments/H3/results'
    fig_dir = os.path.join(results_dir, 'figures')
    os.makedirs(fig_dir, exist_ok=True)

    results = load_results(results_dir)
    agg = aggregate_per_rank(results)

    write_summary_csv(agg, os.path.join(results_dir, 'summary_table.csv'))
    plot_gap_vs_rank(results, agg, fig_dir)
    plot_violin(results, fig_dir)
    plot_rank1_control(results, fig_dir)
    plot_primal_vs_dual(results, fig_dir)

    ev = evaluate_base_case(results, agg)
    with open(os.path.join(results_dir, 'base_case_evaluation.json'), 'w') as f:
        json.dump(ev, f, indent=2)
    print(f"\nVerdict: {ev['verdict']}")
    print(ev['details'])


if __name__ == '__main__':
    main()
```

---

## 6. Analysis Steps

**Script:** `experiments/H3/scripts/analyze.py` (Step 5 above)
**Reads:** `experiments/H3/results/raw_results.json`
**Produces:**
  - `experiments/H3/results/summary_table.csv`
  - `experiments/H3/results/figures/gap_vs_rank.png` (main result)
  - `experiments/H3/results/figures/gap_distribution_violin.png`
  - `experiments/H3/results/figures/rank1_positive_control.png`
  - `experiments/H3/results/figures/primal_vs_dual_scatter.png`
  - `experiments/H3/results/base_case_evaluation.json`

**Statistical tests performed:**
1. Spearman rank correlation between data rank r and normalized gap (across all 100 cells). H0: rho <= 0.8, one-sided.
2. Per-rank summary statistics (mean, std, median, IQR, CV) with 20 seeds each.
3. Positive control at r=1: max |gap| < 1e-4 and mean |gap| < 1e-6.
4. Monotonicity in means: means[r+1] >= means[r] for all consecutive pairs.
5. Magnitude growth ratio: mean_gap(r=5) / mean_gap(r=2) >= 2.
6. Primal-dual validity sanity: P_standard >= D_parallel for >= 95% of cells.

---

## 7. Expected Timeline

| Step | Description | Estimated Time | Compute |
|------|-------------|---------------|---------|
| Setup | Install packages (cvxpy, torch, sklearn, matplotlib); verify imports | 5-10 min | -- |
| Step 1 | Write utils.py (rank-controlled data gen + metrics) | 5 min | -- |
| Step 2 | Write standard_nonconvex_trainer.py | 15 min | -- |
| Step 3 | Write parallel_convex_solver.py (or import from H5) | 15 min | -- |
| Step 4 | Write rank_gap_sweep.py | 15 min | -- |
| Step 5 | Write analyze.py | 10 min | -- |
| Smoke | Run sweep with --ranks 1 --seeds 2 (positive control only) | 5-10 min | CPU |
| Sweep | Run full sweep: 5 ranks x 20 seeds = 100 cells, ~2.5-3 min/cell | 250-300 min | CPU |
| Analyze | Run analyze.py on raw_results.json | 2 min | CPU |
| **Total** | | **~5.5-6 hours** | CPU |

Parallelization note: Up to 4 cells can run in parallel per the compute profile (`max_parallel_jobs: 4`). The default driver in Step 4 is sequential for crash-safety and debuggability. If the reviewer decides to parallelize, wrap `run_single_cell` in a `multiprocessing.Pool(processes=4)` and the wall-clock drops to ~70-90 minutes.

---

## 8. Execution Commands (Exact)

Run from project root: `/Users/abhinavmallick/Github.nosync/Research-Workflow`

```bash
# 1. Install dependencies (once; skip if already installed for H5/H6)
.venv/bin/pip install cvxpy torch scikit-learn matplotlib scipy pyyaml

# 2. Verify directory structure
mkdir -p experiments/H3/scripts experiments/H3/results/figures experiments/H3/colab experiments/H3/colab-results

# 3. Smoke test: rank-1 positive control only (should finish in ~5-10 minutes)
.venv/bin/python experiments/H3/scripts/rank_gap_sweep.py \
    --n 100 --d 10 \
    --ranks 1 --seeds 2 \
    --beta 0.01 --width 50 \
    --restarts 20 --epochs 1000 \
    --max_patterns 100 \
    --results_dir experiments/H3/results_smoke \
    --status_file experiments/H3/status_smoke.yaml

# If smoke test shows rank-1 gap < 1e-4, proceed. Otherwise debug.

# 4. Full experimental sweep (primary run)
.venv/bin/python experiments/H3/scripts/rank_gap_sweep.py \
    --n 100 --d 10 \
    --ranks 1,2,3,4,5 \
    --beta 0.01 \
    --seeds 20 \
    --width 50 \
    --restarts 50 \
    --epochs 2000 \
    --lr 0.001 \
    --max_patterns 150

# 5. Analysis + figures + base case evaluation
.venv/bin/python experiments/H3/scripts/analyze.py experiments/H3/results
```

---

## 9. Troubleshooting

- **Rank-1 positive control fails (max |gap| > 1e-4):** This is the most critical failure. Debug order:
  1. Verify the beta mapping: convex `beta_convex = 2 * sqrt(beta_primal)`. Print both values and double-check.
  2. Increase non-convex restarts from 50 to 100 and epochs from 2000 to 4000.
  3. Increase `max_patterns` from 150 to 300 (more patterns = tighter lower bound).
  4. Switch CVXPY solver from SCS to ECOS or MOSEK (if available).
  5. Tighten SCS tolerance: `eps=1e-9, max_iters=100000`.
- **CVXPY solver returns `infeasible` or `unbounded`:** Usually means the sampled sign patterns are insufficient. Increase `max_patterns` to 300 or 500. Fall back to ECOS if SCS persists.
- **CVXPY solve takes > 5 minutes per cell:** Reduce `max_patterns` from 150 to 100. The number of reachable unique sign patterns for rank-r data with r < d is often much smaller than d-dim full rank.
- **Non-convex training plateaus at high loss:** Increase `epochs` from 2000 to 4000. Try `lr=1e-4` instead of 1e-3 for smoother convergence. Confirm that loss is actually decreasing via the sweep progress log.
- **Primal-dual violation (P_standard < D_parallel) for many cells:** The parallel lower bound is not a valid lower bound because the sign-pattern sampling over-constrained the problem. This is a BUG in the convex solver, not a theoretical issue. Reduce beta (e.g., 0.001) and increase max_patterns.
- **Memory exceeds limit:** With n=100, d=10, P=150, the CVXPY problem has ~3000 decision variables and peak RAM of ~1.5 GB. If this exceeds the 8 GB per-job limit, reduce max_patterns to 75.
- **Step takes > 2x estimated time:** First, reduce `restarts` from 50 to 25 and run a preliminary 20-cell test. If the gap pattern is already clear (r=1 gap near zero, r=5 gap clearly positive), the reduced-restart run may be sufficient. Otherwise, enable the parallel driver (multiprocessing Pool).
- **Base case verdict is INCONCLUSIVE due to high CV at r=5:** The non-convex optimization is stuck in different local minima across seeds. Increase restarts to 100 and re-run r=5 only (the driver's resume feature makes this painless: delete only r=5 rows from raw_results.json and re-run).
- **Sign-pattern sampling is slow or produces few unique patterns at low rank:** At r=1, the data lies on a 1-D subspace, so there are at most 2 distinct sign patterns for (X @ v > 0) across random v. The solver may return a trivial lower bound. This is EXPECTED at r=1 -- the trivial lower bound should match the primal at r=1 (which is linear regression through the origin + ReLU).

---

## 10. File Manifest

| File | Type | Purpose |
|------|------|---------|
| `experiments/H3/scripts/utils.py` | Python module | Seed management, rank-controlled data gen, metrics |
| `experiments/H3/scripts/standard_nonconvex_trainer.py` | Python module | PyTorch 3-layer ReLU primal (non-convex) |
| `experiments/H3/scripts/parallel_convex_solver.py` | Python module | CVXPY parallel-architecture convex lower bound |
| `experiments/H3/scripts/rank_gap_sweep.py` | Python script (main) | (rank, seed) sweep driver |
| `experiments/H3/scripts/analyze.py` | Python script | Aggregation, figures, base case evaluation |
| `experiments/H3/results/raw_results.json` | JSON | Per-cell raw results (P, D, gap, timings, status) |
| `experiments/H3/results/summary_table.csv` | CSV | Per-rank aggregated statistics |
| `experiments/H3/results/progress.log` | text | Running progress log |
| `experiments/H3/results/figures/gap_vs_rank.png` | PNG 300dpi | Main result: mean gap + IQR band vs rank |
| `experiments/H3/results/figures/gap_distribution_violin.png` | PNG 300dpi | Per-rank distributions |
| `experiments/H3/results/figures/rank1_positive_control.png` | PNG 300dpi | r=1 seed scatter (positive control) |
| `experiments/H3/results/figures/primal_vs_dual_scatter.png` | PNG 300dpi | Per-cell P vs D validity check |
| `experiments/H3/results/base_case_evaluation.json` | JSON | Formal pass/fail verdict |
| `experiments/H3/status.yaml` | YAML | Experiment status tracker (live-updated) |
| `experiments/H3/error.log` | text | Latest error traceback (if any) |

---

## 11. Critical Correctness Checks

These MUST be satisfied for the experiment to be valid.

1. **Rank verification:** `np.linalg.matrix_rank(X, tol=1e-8)` must equal the requested rank r for every generated data matrix. The `generate_rank_controlled_data` function asserts this. If the assertion ever trips, the data generator is broken.
2. **Beta mapping:** The convex program's group-l1 strength is `beta_convex = 2 * sqrt(beta)` where beta is the L2-squared weight decay used in the standard primal. This mirrors H5 and H6. A mismatch here invalidates the rank-1 positive control.
3. **Primal-dual validity:** P_standard >= D_parallel for every (rank, seed) cell within numerical tolerance 1e-6. If this is violated for more than 5% of cells, the parallel convex program is NOT a valid lower bound and the experiment is invalid.
4. **Rank-1 positive control:** Must yield mean |gap| < 1e-6 and max |gap| < 1e-4 across all 20 seeds. This reproduces the known theoretical result from [WangErgenPilanci2021] and validates the entire pipeline. If it fails, STOP the sweep and debug before running r >= 2.
5. **Loss consistency:** Both the standard primal and the parallel lower bound use the SAME data loss: `(1/(2n)) * ||y - f(X)||^2`. The regularization terms differ in form but are calibrated via the rescaling lemma.
6. **No bias terms:** Neither the PyTorch standard network nor the CVXPY convex program includes bias parameters. This matches the theoretical formulation in [WangErgenPilanci2021]. If biases are introduced accidentally, the rescaling lemma no longer applies and the gap at r=1 will be nonzero.
7. **Deterministic data generation:** Running the same seed must produce the same (X, y) regardless of prior calls. The `set_all_seeds` call at the start of `generate_rank_controlled_data` ensures this.
8. **Resume safety:** If the sweep is interrupted and re-run, previously-computed (rank, seed) cells must not be re-executed. The driver's resume logic checks `done_keys` before each cell.

---

## 12. Relationship to H5 (shared infrastructure)

H5 tests the rank-2 threshold (2 ranks x 50 seeds = 100 cells). H3 extends to 5 ranks x 20 seeds = 100 cells. Both use:
- The SAME rank-controlled data generator (modulo the rank parameter)
- The SAME parallel-architecture convex solver
- The SAME standard 3-layer non-convex trainer

**Practical guidance for the coder:**
- If H5 has already been implemented and its scripts live in `experiments/H5/scripts/`, prefer to IMPORT from there rather than duplicate. Example:
  ```python
  import sys, os
  H5_SCRIPTS = os.path.abspath(os.path.join(
      os.path.dirname(__file__), '..', '..', 'H5', 'scripts'))
  if H5_SCRIPTS not in sys.path:
      sys.path.insert(0, H5_SCRIPTS)
  from parallel_convex_solver import solve_parallel_convex_3layer
  from standard_nonconvex_trainer import train_standard_3layer
  ```
- If H5 scripts are missing or named differently, implement the scripts described in Steps 2-3 from scratch in `experiments/H3/scripts/`.
- If H3 runs FIRST (before H5), its scripts become the canonical reference and H5 can later import from H3.

The two experiments are designed to cross-validate: if H5 reports a positive gap at r=2 AND H3's r=2 mean gap matches H5's (within 1 std), the results are mutually consistent.
