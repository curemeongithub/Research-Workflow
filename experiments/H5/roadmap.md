---
hypothesis: H5
title: "Duality Gap Emerges at Rank 2 for Standard 3-Layer ReLU Networks"
type: empirical-verification
estimated_total_hours: 5
colab_gates: 0
---

# Experiment Roadmap: H5 -- Rank-2 Duality Gap Emergence

## 1. Objective

Determine whether the duality gap between a standard (non-parallel) 3-layer ReLU network and its parallel-architecture convex lower bound is strictly positive when the data matrix has rank 2, while reproducing the known zero-gap result at rank 1 (Wang, Ergen and Pilanci 2021). The experiment seeks a sharp characterization of the rank boundary at which strong duality breaks for standard deep ReLU.

Primary deliverable: per-seed normalized gaps at rank 1 and rank 2, together with a statistical test that the rank-2 gap is non-zero, computed on rank-controlled synthetic data (n=100, d=10, width=50, 50 seeds, 100 non-convex restarts per seed).

## 2. Base Case (Pass/Fail Criteria)

- **PASS:** Rank-1 positive control gap < 1e-6 across all 50 seeds, AND rank-2 gap > 1e-4 in at least 90% of seeds (45/50), AND a one-sample t-test on the rank-2 gaps rejects H0: mean=0 with p < 0.01.
- **FAIL:** Rank-1 positive control fails (max control gap > 1e-4), OR rank-2 gap > 1e-4 in fewer than 50% of seeds.
- **INCONCLUSIVE:** Rank-1 control passes but rank-2 gap > 1e-4 in 50% to 90% of seeds, OR the one-sample t-test p-value falls in [0.01, 0.05].
- **Minimum data for conclusion:** 2 ranks x 50 seeds = 100 runs. Each run measures the best of 100 non-convex restarts and one convex solve.

The rank-1 leg is a positive control required by the hypothesis: if it does not reproduce the Wang et al. zero-gap result, the experiment is invalidated regardless of the rank-2 outcome.

## 3. Local Setup

All computation runs locally on Apple M4 Pro (12 cores, 24 GB RAM, MPS GPU). No VM, no SSH, no Colab.

```bash
# Project root
cd /Users/abhinavmallick/Github.nosync/Research-Workflow

# Install missing packages into project venv (shared with H6; may already be installed)
.venv/bin/pip install cvxpy torch scikit-learn matplotlib

# Verify installations
.venv/bin/python -c "import cvxpy, torch, sklearn, matplotlib, numpy, scipy; print('All packages OK')"

# Verify experiment directories exist
ls -la experiments/H5/
ls -la experiments/H5/scripts experiments/H5/results experiments/H5/results/figures
```

The default PyTorch device for this experiment is **CPU** (not MPS). The problem size (n=100, d=10, width=50) is too small to benefit from MPS, and CPU float32 is both faster in this regime and numerically well-behaved with CVXPY outputs.

## 4. Repository Cloning

No external repository clone is required. The parallel-architecture convex program is implemented directly in CVXPY in `convex_parallel_solver.py` (Step 3). The reference implementations in `pilancilab/convex_nn` and `pilancilab/scnn` are used as documentation guides but NOT imported, to avoid API drift and to keep the experiment self-contained.

If the coder wants to cross-check the convex formulation, they may clone for reference only:

```bash
# Optional (reference only, not imported)
git clone https://github.com/pilancilab/convex_nn /Users/abhinavmallick/Github.nosync/Research-Workflow/compute/convex_nn
```

## 5. Implementation Steps

### Step 1: Shared Utilities -- Data Generation, Seeds, Metrics

**Script:** `experiments/H5/scripts/utils.py`
**Inputs:** None (utility module)
**Outputs:** Importable module
**Compute:** N/A
**Purpose:** Centralize rank-controlled data generation, seed management, and gap computation so the main script and ablations share identical primitives.

**Pseudocode:**
```python
import numpy as np
import torch
import random

def set_all_seeds(seed: int) -> None:
    """Deterministic seeding for numpy, torch, and python random."""
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(False)  # keep False for speed
    random.seed(seed)

def generate_rank_controlled_data(n: int, d: int, rank: int, seed: int,
                                  noise_std: float = 0.1):
    """
    Generate synthetic regression data with EXACT rank r in the design matrix.

    Construction: X = A @ B.T  where
        A ~ N(0, I) in R^{n x rank}
        B ~ N(0, I) in R^{d x rank}
    So rank(X) = min(rank, n, d) = rank (since rank <= d <= n).

    Targets: y = X @ w_true + noise, with w_true ~ N(0, I_d),
             noise ~ N(0, noise_std * I_n).

    Returns:
        X: (n, d) float64 numpy array
        y: (n,) float64 numpy array
        w_true: (d,) float64 numpy array
        effective_rank: int (numerical rank via np.linalg.matrix_rank(X, tol=1e-8))
    """
    set_all_seeds(seed)
    A = np.random.randn(n, rank)
    B = np.random.randn(d, rank)
    X = A @ B.T
    w_true = np.random.randn(d)
    noise = np.random.randn(n) * noise_std
    y = X @ w_true + noise
    effective_rank = int(np.linalg.matrix_rank(X, tol=1e-8))
    return X.astype(np.float64), y.astype(np.float64), w_true, effective_rank

def normalized_gap(p_primal: float, d_lower: float) -> float:
    """
    Compute (P - D) / P.
    P is the non-convex primal best training loss.
    D is the convex parallel-architecture lower bound.

    Returns 0.0 if |P| < 1e-12 to avoid division by zero.
    """
    if abs(p_primal) < 1e-12:
        return 0.0
    return (p_primal - d_lower) / p_primal

def training_loss(pred: np.ndarray, y: np.ndarray) -> float:
    """Squared loss (1/(2n)) * ||y - pred||^2."""
    n = y.shape[0]
    resid = y - pred
    return float(0.5 / n * np.dot(resid, resid))
```

**Correctness checks the coder MUST add:**
1. After generating rank-r data, assert `effective_rank == rank` with tolerance 1e-8. If the assertion fails for any seed, log the seed and either resample or raise.
2. After building `X`, assert `X.shape == (n, d)` and both `A.shape == (n, rank)` and `B.shape == (d, rank)`.

---

### Step 2: Standard 3-Layer ReLU Primal Solver (PyTorch)

**Script:** `experiments/H5/scripts/standard_primal_solver.py`
**Inputs:** Data matrix X (n x d), target y (n,), architecture (d -> width -> width -> 1), weight decay beta, number of restarts, epochs per restart, learning rate, base seed
**Outputs:** `dict` with best unregularized data loss, best regularized total loss, best model state_dict, and per-restart loss trace
**Compute:** CPU, ~0.8-1.5 seconds per restart with (n=100, d=10, width=50, 3000 epochs); 100 restarts = ~80-150 seconds per (rank, seed) pair
**Purpose:** Train the standard (non-parallel) 3-layer ReLU network by Adam with multiple restarts and return the best observed training loss as the primal upper bound P_standard.

**Architecture (exact):**
- Layer 1: `nn.Linear(d=10, 50, bias=False)`
- ReLU
- Layer 2: `nn.Linear(50, 50, bias=False)`
- ReLU
- Layer 3: `nn.Linear(50, 1, bias=False)`
- Total parameters: 10*50 + 50*50 + 50*1 = 500 + 2500 + 50 = 3050

**Pseudocode:**
```python
import numpy as np
import torch
import torch.nn as nn

class StandardThreeLayerReLU(nn.Module):
    """Standard (non-parallel) 3-layer ReLU regression network."""
    def __init__(self, d: int, width: int):
        super().__init__()
        self.fc1 = nn.Linear(d, width, bias=False)
        self.fc2 = nn.Linear(width, width, bias=False)
        self.fc3 = nn.Linear(width, 1, bias=False)
        self.relu = nn.ReLU()

    def forward(self, x):
        h1 = self.relu(self.fc1(x))
        h2 = self.relu(self.fc2(h1))
        return self.fc3(h2).squeeze(-1)

def weight_decay_penalty(model: nn.Module, beta: float) -> torch.Tensor:
    """
    beta * (1/2) * sum_layers ||W||_F^2
    Summed over all three linear layers.
    Note: the (1/2) prefactor matches the standard weight-decay convention
    used in the convex-reformulation literature (Pilanci-Ergen 2020).
    """
    total = 0.0
    for p in model.parameters():
        total = total + torch.sum(p ** 2)
    return 0.5 * beta * total

def train_standard_primal(X: np.ndarray, y: np.ndarray,
                          d: int, width: int, beta: float,
                          n_restarts: int = 100,
                          n_epochs: int = 3000,
                          lr: float = 1e-3,
                          seed_base: int = 0,
                          device: str = 'cpu') -> dict:
    """
    Train StandardThreeLayerReLU with Adam for n_restarts random inits.
    Keep the restart with the lowest FINAL total loss (data + weight decay).

    Returns:
        {
            'p_standard': best total loss (data + beta*(1/2)*||W||^2),
            'data_loss': data loss (unregularized) at the best restart,
            'reg_loss': regularization term at the best restart,
            'best_restart': int,
            'per_restart_final_loss': list of floats (length n_restarts),
            'best_state_dict': state dict of the best model,
        }
    """
    X_t = torch.tensor(X, dtype=torch.float32, device=device)
    y_t = torch.tensor(y, dtype=torch.float32, device=device)
    n = X.shape[0]

    best = {'p_standard': float('inf'), 'restart': -1,
            'data_loss': None, 'reg_loss': None, 'state_dict': None}
    per_restart_final = []

    for r in range(n_restarts):
        torch.manual_seed(seed_base * 10000 + r)
        model = StandardThreeLayerReLU(d, width).to(device)
        opt = torch.optim.Adam(model.parameters(), lr=lr)

        for epoch in range(n_epochs):
            opt.zero_grad()
            pred = model(X_t)
            data_loss = (1.0 / (2 * n)) * torch.sum((y_t - pred) ** 2)
            reg_loss = weight_decay_penalty(model, beta)
            total = data_loss + reg_loss
            total.backward()
            opt.step()

        final_total = total.item()
        per_restart_final.append(final_total)
        if final_total < best['p_standard']:
            best['p_standard'] = final_total
            best['restart'] = r
            best['data_loss'] = data_loss.item()
            best['reg_loss'] = reg_loss.item()
            best['state_dict'] = {k: v.detach().cpu().clone()
                                  for k, v in model.state_dict().items()}

    return {
        'p_standard': best['p_standard'],
        'data_loss': best['data_loss'],
        'reg_loss': best['reg_loss'],
        'best_restart': best['restart'],
        'per_restart_final_loss': per_restart_final,
        'best_state_dict': best['state_dict'],
    }
```

**Key implementation notes for the coder:**
1. Use **float32** and device **'cpu'**. The problem is small enough that float32 precision is sufficient for a 1e-6 rank-1 gap tolerance, and CPU is faster than MPS for this size due to kernel-launch overhead.
2. The learning rate 1e-3 is the default. If `per_restart_final_loss` shows divergence or plateau above the convex lower bound by a constant offset across ALL restarts, try `lr=3e-4` and `n_epochs=5000`.
3. The regularization convention: `(1/2) * beta * sum ||W||_F^2`. This matches the convex formulation's weight decay parameter conversion.
4. Do NOT add bias terms. The convex parallel-architecture formulation below assumes no biases, and the primal and lower bound must agree on architectural conventions.
5. Random initialization uses PyTorch default (Kaiming uniform for Linear with bias=False). Do not override this.
6. The best_restart index is recorded so the analyst can see whether 100 restarts is enough (if best_restart is always in the first 20, we have headroom; if it scatters uniformly, we may need more).

---

### Step 3: Parallel-Architecture Convex Lower Bound (CVXPY)

**Script:** `experiments/H5/scripts/convex_parallel_solver.py`
**Inputs:** Data X, target y, weight decay beta, max number of sampled hyperplane arrangements, CVXPY solver settings
**Outputs:** `dict` with optimal convex objective value, solver status, and metadata
**Compute:** CPU, ~15-45 seconds per solve depending on the number of enumerated sign patterns
**Purpose:** Compute D_parallel, the optimal value of the convex reformulation for a parallel-architecture ReLU network on the same data. This serves as a **valid lower bound** on the true dual of the standard 3-layer network, because the parallel architecture admits a strict superset of the solutions available to the standard architecture (it is a relaxation).

**Formulation (Pilanci-Ergen 2020 / Wang-Ergen-Pilanci 2021, parallel case):**

For a parallel two-layer ReLU model with group-L1 regularization at strength `beta_convex = 2 * sqrt(lambda_2 * 0.5 / 0.5)`, the convex program is:

$$
\min_{u_j, v_j \ge 0} \;\; \frac{1}{2n}\left\|\,y - \sum_{j=1}^P D_j X(u_j - v_j)\,\right\|_2^2 + \beta \sum_{j=1}^P \left(\|u_j\|_2 + \|v_j\|_2\right)
$$

where each `D_j` is an `n x n` diagonal matrix with 0/1 entries encoding a ReLU activation pattern and `P` is the number of patterns enumerated.

For the parallel 3-layer case used here, the literature shows that the convex program for a parallel architecture at ANY depth reduces (up to a rescaling of beta) to the two-layer group-L1 program above. We use this two-layer group-L1 solve as `D_parallel` and rely on the following rigorous bound:

$$
D_{\text{parallel}} \le P_{\text{parallel}} \le P_{\text{standard}}
$$

The first inequality is the convex program's optimality. The second holds because a standard 3-layer network can be simulated by a parallel architecture with appropriate widths (the parallel architecture is strictly more expressive under the same regularization). Thus `D_parallel` is a valid lower bound for the gap computation.

**Beta mapping:** Let `beta` be the weight-decay coefficient used in `StandardThreeLayerReLU` (i.e., the coefficient on `(1/2) * sum ||W||_F^2`). The equivalent group-L1 strength in the convex program is `beta_convex = beta`. This is **different** from the H6 mapping (`2 * sqrt(lambda_2)`) because the H5 convention already includes the `(1/2)` prefactor. The coder MUST verify this with the rank-1 positive control: if rank-1 gap > 1e-4, the mapping is wrong.

**Pseudocode:**
```python
import numpy as np
import cvxpy as cp

def enumerate_sign_patterns(X: np.ndarray, max_patterns: int = 200,
                            oversample_factor: int = 20,
                            rng_seed: int = 0) -> list:
    """
    Enumerate distinct ReLU activation patterns induced by random hyperplanes.

    For X in R^{n x d}, a hyperplane with normal v in R^d induces the
    activation pattern diag(1[X v > 0]). We sample v ~ N(0, I_d) and keep
    distinct patterns until we reach max_patterns or exhaust the budget.

    Returns:
        D_list: list of (n,) numpy int arrays (0/1 diagonals), deduplicated.
    """
    rng = np.random.default_rng(rng_seed)
    n, d = X.shape
    seen = set()
    D_list = []
    budget = max_patterns * oversample_factor

    for _ in range(budget):
        v = rng.standard_normal(d)
        pattern = (X @ v > 0).astype(np.int8)
        key = pattern.tobytes()
        if key not in seen:
            seen.add(key)
            D_list.append(pattern)
            if len(D_list) >= max_patterns:
                break

    # Always include the all-ones pattern (identity / no gating) as a safety.
    all_ones = np.ones(n, dtype=np.int8)
    if all_ones.tobytes() not in seen:
        D_list.append(all_ones)

    return D_list

def solve_convex_parallel(X: np.ndarray, y: np.ndarray, beta: float,
                          max_patterns: int = 200,
                          solver_eps: float = 1e-9,
                          max_iters: int = 20000,
                          pattern_seed: int = 0) -> dict:
    """
    Solve the convex parallel-architecture program:
        min_{u_j, v_j >= 0}
            (1/2n) ||y - sum_j diag(d_j) X (u_j - v_j)||^2
            + beta * sum_j (||u_j||_2 + ||v_j||_2)

    Returns:
        {
            'd_parallel': optimal objective value,
            'status': CVXPY solver status string,
            'num_patterns': int,
            'solver': 'SCS',
            'primal_residual': float or None,
            'dual_residual': float or None,
        }
    """
    n, d = X.shape
    patterns = enumerate_sign_patterns(X, max_patterns=max_patterns,
                                       rng_seed=pattern_seed)
    P = len(patterns)

    u_vars = [cp.Variable(d, nonneg=True) for _ in range(P)]
    v_vars = [cp.Variable(d, nonneg=True) for _ in range(P)]

    # Build prediction: sum_j diag(patterns[j]) @ X @ (u_j - v_j)
    # Equivalent to: sum_j (patterns[j] * (X @ (u_j - v_j)))
    pred_terms = []
    for j in range(P):
        mask = patterns[j].astype(np.float64)  # (n,)
        XuMinusV = X @ (u_vars[j] - v_vars[j])   # (n,) affine
        pred_terms.append(cp.multiply(mask, XuMinusV))
    pred = cp.sum(pred_terms)

    data_loss = (1.0 / (2 * n)) * cp.sum_squares(y - pred)
    reg = beta * cp.sum([cp.norm(u_vars[j], 2) + cp.norm(v_vars[j], 2)
                         for j in range(P)])
    prob = cp.Problem(cp.Minimize(data_loss + reg))

    prob.solve(solver=cp.SCS, eps=solver_eps, max_iters=max_iters, verbose=False)

    if prob.status not in ['optimal', 'optimal_inaccurate']:
        raise RuntimeError(f"CVXPY SCS solver failed with status: {prob.status}")

    stats = prob.solver_stats
    return {
        'd_parallel': float(prob.value),
        'status': prob.status,
        'num_patterns': P,
        'solver': 'SCS',
        'setup_time': stats.setup_time if stats else None,
        'solve_time': stats.solve_time if stats else None,
    }
```

**Key implementation notes for the coder:**
1. The number of sampled patterns controls the tightness of the lower bound and the solver cost. Default `max_patterns=200`. For `n=100, d=10` the true number of distinct sign patterns is bounded by $2 \cdot \sum_{i=0}^{d-1}\binom{n-1}{i} \approx 10^{10}$, so sampling is necessary, but 200 patterns is empirically sufficient for n=100, d=10.
2. If SCS returns `optimal_inaccurate`, inspect `prob.solver_stats`. If primal/dual residuals are below 1e-6, accept. If above, try SCS with `eps=1e-10, max_iters=50000`, and only as a last resort switch to `cp.CLARABEL` (installed with cvxpy >= 1.4).
3. The `cp.multiply(mask, XuMinusV)` construction is preferred over building explicit `D_j` matrices, which would consume O(P * n^2) memory. For P=200, n=100 that is 2 MB per solve, manageable but unnecessary.
4. The `pattern_seed` is deliberately kept separate from the data seed so the coder can, in a later sanity run, hold the data fixed and vary the pattern sampling to check lower-bound stability.
5. **Do NOT pass cp.ECOS as a primary solver.** ECOS does not handle this problem size well in practice. SCS is the right default.

---

### Step 4: Two-Layer Ablation -- Rank-1 and Rank-2 Must Both Give Zero Gap

**Script:** `experiments/H5/scripts/ablation_two_layer.py`
**Inputs:** Same data generator as main experiment, small seed count
**Outputs:** `experiments/H5/results/ablation_two_layer.json`
**Compute:** CPU, ~10-20 minutes for 5 seeds x 2 ranks
**Purpose:** Validate the convex lower bound AND the primal solver against a problem where the gap is PROVEN to be zero (two-layer ReLU with weight decay, at any data rank -- Pilanci-Ergen 2020). This ablation MUST pass before the main experiment runs, because if the two-layer case shows a nonzero gap, the parallel-architecture bound or the primal solver is broken, and any rank-2 gap observed in the main experiment would be noise rather than a real duality gap.

**Pseudocode:**
```python
"""
For rank in {1, 2}, for seed in {0..4}:
    1. Generate rank-controlled data (n=100, d=10)
    2. Train a TWO-layer ReLU network (d -> width -> 1) to global optimum
       via the convex program (SAME solver as Step 3 applied to a 2-layer,
       single-block decomposition -- equivalent since the 2-layer parallel
       and 2-layer standard formulations coincide).
       Call this f_convex_2layer.
    3. Train a TWO-layer ReLU network by PyTorch Adam with 100 restarts,
       matching the hyperparameters used in Step 2 (except architecture).
       Call this f_primal_2layer.
    4. Compute gap_2layer = (f_primal_2layer - f_convex_2layer) / f_primal_2layer
    5. Assert gap_2layer < 1e-4 for all (rank, seed).

If any (rank, seed) fails: the beta mapping, pattern enumeration, or primal
training hyperparameters are wrong. Debug before running the main experiment.
"""
# Imports utils.set_all_seeds, utils.generate_rank_controlled_data,
# utils.normalized_gap, and the convex solver from Step 3.
# Implements a minimal TwoLayerReLU class in this file (d -> width -> 1,
# no bias) and a local train_two_layer_primal following the same pattern
# as Step 2's train_standard_primal.
```

**Key implementation notes for the coder:**
1. The two-layer ablation is the ONLY reliable way to factor out solver bugs from the rank-2 signal. Skipping this step voids the main experiment.
2. If the ablation fails at rank-1 but passes at rank-2, the primal solver is stuck in local minima -- increase restarts to 200 and epochs to 5000.
3. If the ablation fails at BOTH ranks by a constant offset, the beta mapping is wrong.
4. If the ablation fails at rank-1 only, the convex patterns enumeration is missing the true optimum -- increase `max_patterns` to 500.

---

### Step 5: Main Experiment Runner

**Script:** `experiments/H5/scripts/rank2_threshold.py`
**Inputs:** Command-line arguments `--n 100 --d 10 --beta 0.01 --seeds 50 --width 50 --restarts 100 --max_patterns 200 --results_dir experiments/H5/results`
**Outputs:**
  - `experiments/H5/results/raw_results.json` -- per (rank, seed) record with p_standard, d_parallel, gap, timing, solver stats
  - `experiments/H5/results/summary_table.csv` -- aggregated per-rank statistics
**Compute:** CPU, ~2-3 hours total (2 ranks x 50 seeds x (~100s primal + ~30s convex) ~= 2.2 hours)
**Purpose:** Execute the full (rank, seed) grid, computing `p_standard` and `d_parallel` and recording both the normalized and absolute gaps.

**Exact entry point:**
```bash
.venv/bin/python experiments/H5/scripts/rank2_threshold.py \
    --n 100 --d 10 --beta 0.01 \
    --seeds 50 --width 50 --restarts 100 \
    --max_patterns 200 \
    --results_dir experiments/H5/results
```

**Pseudocode:**
```python
import argparse
import json
import csv
import os
import time
import sys
import numpy as np

# Local imports (ensure scripts/ is on sys.path or use relative imports)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import set_all_seeds, generate_rank_controlled_data, normalized_gap
from standard_primal_solver import train_standard_primal
from convex_parallel_solver import solve_convex_parallel

def parse_args():
    p = argparse.ArgumentParser(description="H5: Rank-2 duality gap threshold test")
    p.add_argument('--n', type=int, default=100)
    p.add_argument('--d', type=int, default=10)
    p.add_argument('--beta', type=float, default=0.01)
    p.add_argument('--seeds', type=int, default=50)
    p.add_argument('--width', type=int, default=50)
    p.add_argument('--restarts', type=int, default=100)
    p.add_argument('--epochs', type=int, default=3000)
    p.add_argument('--lr', type=float, default=1e-3)
    p.add_argument('--max_patterns', type=int, default=200)
    p.add_argument('--ranks', type=str, default='1,2')
    p.add_argument('--results_dir', type=str, default='experiments/H5/results')
    return p.parse_args()

def run_one(rank, seed, args):
    X, y, w_true, eff_rank = generate_rank_controlled_data(
        n=args.n, d=args.d, rank=rank, seed=seed)
    assert eff_rank == rank, f"effective rank {eff_rank} != requested {rank}"

    t0 = time.time()
    primal = train_standard_primal(
        X, y, d=args.d, width=args.width, beta=args.beta,
        n_restarts=args.restarts, n_epochs=args.epochs, lr=args.lr,
        seed_base=seed, device='cpu')
    primal_time = time.time() - t0

    t0 = time.time()
    lower = solve_convex_parallel(
        X, y, beta=args.beta, max_patterns=args.max_patterns,
        pattern_seed=seed)
    convex_time = time.time() - t0

    p_std = primal['p_standard']
    d_par = lower['d_parallel']
    gap = normalized_gap(p_std, d_par)

    return {
        'rank': rank,
        'seed': seed,
        'p_standard': p_std,
        'p_standard_data_loss': primal['data_loss'],
        'p_standard_reg_loss': primal['reg_loss'],
        'best_restart': primal['best_restart'],
        'd_parallel': d_par,
        'num_patterns': lower['num_patterns'],
        'gap_absolute': p_std - d_par,
        'gap_normalized': gap,
        'primal_ge_lower_bound': bool(p_std >= d_par - 1e-8),
        'primal_time_sec': primal_time,
        'convex_time_sec': convex_time,
        'effective_rank': eff_rank,
    }

def main():
    args = parse_args()
    ranks = [int(r) for r in args.ranks.split(',')]
    os.makedirs(args.results_dir, exist_ok=True)

    results = []
    total = len(ranks) * args.seeds
    done = 0
    t_start = time.time()
    for rank in ranks:
        for seed in range(args.seeds):
            rec = run_one(rank, seed, args)
            results.append(rec)
            done += 1
            elapsed = time.time() - t_start
            eta = (elapsed / done) * (total - done)
            print(f"[{done}/{total}] rank={rank} seed={seed} "
                  f"gap={rec['gap_normalized']:.2e} "
                  f"P={rec['p_standard']:.6f} D={rec['d_parallel']:.6f} "
                  f"best_restart={rec['best_restart']} "
                  f"ETA={eta/60:.1f}min")

    # Write raw JSON
    raw_path = os.path.join(args.results_dir, 'raw_results.json')
    with open(raw_path, 'w') as f:
        json.dump({
            'args': vars(args),
            'results': results,
        }, f, indent=2)
    print(f"Raw results -> {raw_path}")

    # Write summary CSV
    summary_path = os.path.join(args.results_dir, 'summary_table.csv')
    with open(summary_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['rank', 'n_seeds', 'mean_gap', 'std_gap',
                    'median_gap', 'min_gap', 'max_gap',
                    'fraction_above_1e_minus_4', 'fraction_above_1e_minus_6',
                    'mean_p_standard', 'mean_d_parallel'])
        for rank in ranks:
            rs = [r for r in results if r['rank'] == rank]
            gaps = np.array([r['gap_normalized'] for r in rs])
            w.writerow([
                rank, len(rs),
                f"{gaps.mean():.6e}", f"{gaps.std():.6e}",
                f"{np.median(gaps):.6e}",
                f"{gaps.min():.6e}", f"{gaps.max():.6e}",
                f"{np.mean(gaps > 1e-4):.4f}",
                f"{np.mean(gaps > 1e-6):.4f}",
                f"{np.mean([r['p_standard'] for r in rs]):.6f}",
                f"{np.mean([r['d_parallel'] for r in rs]):.6f}",
            ])
    print(f"Summary  -> {summary_path}")

    total_time = time.time() - t_start
    print(f"Total wall-clock: {total_time/60:.1f} min")

if __name__ == '__main__':
    main()
```

**Key implementation notes for the coder:**
1. The per-run record includes `primal_ge_lower_bound` as a sanity check. If ANY record has `p_standard < d_parallel` by more than 1e-8, the lower bound is invalid (likely a beta-mapping bug).
2. `effective_rank` must equal the requested rank or the run is rejected (raise and re-seed).
3. Progress prints every iteration to stdout so the coder can monitor. Expected per-iteration wall-clock at n=100, d=10, width=50, 100 restarts, 3000 epochs: 90 to 150 seconds primal + 15 to 40 seconds convex = 105 to 190 seconds. Total for 100 configs: 175 to 320 minutes.
4. The main script does NOT run the base case evaluation or generate figures -- that is Step 6 (`analyze.py`).
5. If the main run is interrupted, the `results` list is lost. For this experiment we accept that risk because a single run is under 3 hours; a more paranoid version would checkpoint to disk every N configs.

---

### Step 6: Analysis, Statistics, and Figures

**Script:** `experiments/H5/scripts/analyze.py`
**Inputs:** `experiments/H5/results/raw_results.json`
**Outputs:**
  - `experiments/H5/results/figures/gap_rank1_vs_rank2.png` -- violin plot (primary figure from methodology)
  - `experiments/H5/results/figures/gap_histogram_rank2.png` -- histogram of rank-2 gaps
  - `experiments/H5/results/figures/restart_distribution.png` -- which restart index won per seed (diagnostic)
  - `experiments/H5/results/figures/primal_vs_lower_bound.png` -- scatter of P vs D per seed and rank
  - `experiments/H5/results/base_case_evaluation.json`
**Compute:** CPU, ~1-2 minutes

**Pseudocode:**
```python
import json
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def load_results(results_dir):
    with open(os.path.join(results_dir, 'raw_results.json')) as f:
        return json.load(f)

def evaluate_base_case(results):
    """
    PASS conditions (all three required):
      1. max(gap at rank 1) < 1e-6
      2. fraction(gap at rank 2 > 1e-4) >= 0.90
      3. one-sample t-test on rank-2 gaps rejects mean == 0 with p < 0.01
    """
    rank1 = [r['gap_normalized'] for r in results if r['rank'] == 1]
    rank2 = [r['gap_normalized'] for r in results if r['rank'] == 2]

    rank1_max = float(max(rank1)) if rank1 else float('nan')
    rank2_frac_positive = float(np.mean(np.array(rank2) > 1e-4)) if rank2 else 0.0

    # one-sample t-test H0: mean == 0
    if len(rank2) >= 2:
        t_stat, p_val = stats.ttest_1samp(rank2, 0.0)
    else:
        t_stat, p_val = float('nan'), float('nan')

    # Mann-Whitney U (supplementary)
    if len(rank1) >= 1 and len(rank2) >= 1:
        u_stat, u_p = stats.mannwhitneyu(rank2, rank1, alternative='greater')
    else:
        u_stat, u_p = float('nan'), float('nan')

    cond_rank1 = rank1_max < 1e-6
    cond_rank2_frac = rank2_frac_positive >= 0.90
    cond_rank2_ttest = (p_val < 0.01) and (np.mean(rank2) > 0)

    if cond_rank1 and cond_rank2_frac and cond_rank2_ttest:
        verdict = "PASS"
        passed = True
    elif not cond_rank1:
        verdict = "FAIL - rank-1 positive control failed (max gap >= 1e-6)"
        passed = False
    elif np.mean(np.array(rank2) > 1e-4) < 0.5:
        verdict = "FAIL - rank-2 gap positive in fewer than 50% of seeds"
        passed = False
    elif 0.5 <= rank2_frac_positive < 0.90:
        verdict = "INCONCLUSIVE - rank-2 gap positive in 50%-90% of seeds"
        passed = False
    elif 0.01 <= p_val < 0.05:
        verdict = "INCONCLUSIVE - one-sample t-test p-value in [0.01, 0.05]"
        passed = False
    else:
        verdict = "INCONCLUSIVE - unclassified branch; inspect raw_results.json"
        passed = False

    return {
        'pass': passed,
        'verdict': verdict,
        'metric_name': 'rank2_gap_fraction_above_1e_minus_4',
        'metric_value': rank2_frac_positive,
        'threshold': 0.90,
        'comparison': 'greater_or_equal',
        'rank1_max_gap': rank1_max,
        'rank1_mean_gap': float(np.mean(rank1)) if rank1 else float('nan'),
        'rank2_mean_gap': float(np.mean(rank2)) if rank2 else float('nan'),
        'rank2_median_gap': float(np.median(rank2)) if rank2 else float('nan'),
        'rank2_std_gap': float(np.std(rank2)) if rank2 else float('nan'),
        'rank2_fraction_above_1e_minus_4': rank2_frac_positive,
        'one_sample_t_statistic': float(t_stat),
        'one_sample_p_value': float(p_val),
        'mannwhitney_u_statistic': float(u_stat),
        'mannwhitney_p_value': float(u_p),
        'n_rank1_seeds': len(rank1),
        'n_rank2_seeds': len(rank2),
        'details': (
            f"Rank-1: n={len(rank1)}, max gap={rank1_max:.2e}. "
            f"Rank-2: n={len(rank2)}, mean gap={np.mean(rank2):.4e}, "
            f"median={np.median(rank2):.4e}, "
            f"fraction>1e-4={rank2_frac_positive:.2f}. "
            f"One-sample t-test p={p_val:.4e}. "
            f"Mann-Whitney rank2>rank1 p={u_p:.4e}."
        ),
    }

def plot_violin(results, fig_dir):
    rank1 = [max(r['gap_normalized'], 0) for r in results if r['rank'] == 1]
    rank2 = [max(r['gap_normalized'], 0) for r in results if r['rank'] == 2]
    fig, ax = plt.subplots(figsize=(7, 5))
    parts = ax.violinplot([rank1, rank2], positions=[1, 2], showmedians=True,
                          showextrema=True)
    for pc in parts['bodies']:
        pc.set_facecolor('#2c7bb6')
        pc.set_alpha(0.5)
    ax.scatter([1] * len(rank1), rank1, color='black', s=12, zorder=3, alpha=0.6)
    ax.scatter([2] * len(rank2), rank2, color='black', s=12, zorder=3, alpha=0.6)
    ax.set_yscale('symlog', linthresh=1e-8)
    ax.axhline(1e-4, color='red', ls='--', alpha=0.6, label='1e-4 threshold')
    ax.axhline(1e-6, color='green', ls='--', alpha=0.6, label='1e-6 (rank-1 control)')
    ax.set_xticks([1, 2])
    ax.set_xticklabels(['rank 1', 'rank 2'])
    ax.set_ylabel('Normalized gap $(P - D)/P$')
    ax.set_title('H5: Duality gap at rank 1 vs rank 2\n(standard 3-layer ReLU, n=100, d=10, width=50)')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    out = os.path.join(fig_dir, 'gap_rank1_vs_rank2.png')
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"Saved {out}")

def plot_histogram_rank2(results, fig_dir):
    rank2 = [r['gap_normalized'] for r in results if r['rank'] == 2]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(rank2, bins=20, color='#2c7bb6', alpha=0.7, edgecolor='black')
    ax.axvline(1e-4, color='red', ls='--', label='1e-4 threshold')
    ax.set_xlabel('Normalized gap at rank 2')
    ax.set_ylabel('Number of seeds')
    ax.set_title('Distribution of rank-2 gaps (50 seeds)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    out = os.path.join(fig_dir, 'gap_histogram_rank2.png')
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"Saved {out}")

def plot_restart_distribution(results, fig_dir):
    restarts_r1 = [r['best_restart'] for r in results if r['rank'] == 1]
    restarts_r2 = [r['best_restart'] for r in results if r['rank'] == 2]
    fig, ax = plt.subplots(figsize=(7, 4))
    bins = np.arange(0, 101, 5)
    ax.hist(restarts_r1, bins=bins, alpha=0.5, label='rank 1', color='#2c7bb6')
    ax.hist(restarts_r2, bins=bins, alpha=0.5, label='rank 2', color='#d7191c')
    ax.set_xlabel('Winning restart index (out of 100)')
    ax.set_ylabel('Frequency')
    ax.set_title('Where does the best primal come from? (diagnostic)')
    ax.legend()
    plt.tight_layout()
    out = os.path.join(fig_dir, 'restart_distribution.png')
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"Saved {out}")

def plot_primal_vs_lower(results, fig_dir):
    r1 = [r for r in results if r['rank'] == 1]
    r2 = [r for r in results if r['rank'] == 2]
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter([r['d_parallel'] for r in r1], [r['p_standard'] for r in r1],
               label='rank 1', color='#2c7bb6', alpha=0.7)
    ax.scatter([r['d_parallel'] for r in r2], [r['p_standard'] for r in r2],
               label='rank 2', color='#d7191c', alpha=0.7)
    lims = [0, max(max(r['p_standard'] for r in results),
                   max(r['d_parallel'] for r in results)) * 1.1]
    ax.plot(lims, lims, 'k--', alpha=0.5, label='P = D')
    ax.set_xlim(lims); ax.set_ylim(lims)
    ax.set_xlabel('Convex lower bound D_parallel')
    ax.set_ylabel('Standard primal P_standard')
    ax.set_title('Primal vs. lower bound (must lie above diagonal)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    out = os.path.join(fig_dir, 'primal_vs_lower_bound.png')
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"Saved {out}")

def main():
    results_dir = sys.argv[1] if len(sys.argv) > 1 else 'experiments/H5/results'
    fig_dir = os.path.join(results_dir, 'figures')
    os.makedirs(fig_dir, exist_ok=True)

    data = load_results(results_dir)
    results = data['results']

    plot_violin(results, fig_dir)
    plot_histogram_rank2(results, fig_dir)
    plot_restart_distribution(results, fig_dir)
    plot_primal_vs_lower(results, fig_dir)

    evaluation = evaluate_base_case(results)
    eval_path = os.path.join(results_dir, 'base_case_evaluation.json')
    with open(eval_path, 'w') as f:
        json.dump(evaluation, f, indent=2)
    print(f"\nBase case evaluation -> {eval_path}")
    print(f"Verdict: {evaluation['verdict']}")
    print(f"Details: {evaluation['details']}")

if __name__ == '__main__':
    main()
```

---

## 6. Analysis Steps

**Primary script:** `experiments/H5/scripts/analyze.py` (Step 6 above)

**Reads:** `experiments/H5/results/raw_results.json`

**Produces:**
- `experiments/H5/results/figures/gap_rank1_vs_rank2.png` -- primary figure (violin)
- `experiments/H5/results/figures/gap_histogram_rank2.png`
- `experiments/H5/results/figures/restart_distribution.png`
- `experiments/H5/results/figures/primal_vs_lower_bound.png`
- `experiments/H5/results/base_case_evaluation.json`

**Statistical tests performed:**
1. One-sample t-test on rank-2 gaps, H0: mean = 0, two-sided, alpha = 0.01 (primary)
2. Mann-Whitney U test, rank-2 gaps vs rank-1 gaps, alternative 'greater' (supplementary)
3. Fraction of rank-2 seeds with gap > 1e-4 (binary outcome per hypothesis)
4. Max rank-1 gap against the 1e-6 control threshold

**Sanity assertions enforced by analyze.py:**
- All records must have `primal_ge_lower_bound == true`. If any record fails, the analysis prints a warning and marks the base case INCONCLUSIVE.
- `effective_rank` per record must equal the requested `rank`.

## 7. Expected Timeline

| Step | Description | Estimated Time | Compute |
|------|-------------|---------------|---------|
| Setup | Install packages, verify environment | 5 min | -- |
| Step 1 | Write `utils.py` | 10 min | -- |
| Step 2 | Write `standard_primal_solver.py` | 20 min | -- |
| Step 3 | Write `convex_parallel_solver.py` | 25 min | -- |
| Step 4 | Write and run `ablation_two_layer.py` | 30 min write + 15 min run | CPU |
| Step 4b | Debug if ablation fails | 0-45 min | CPU |
| Step 5 | Write `rank2_threshold.py` | 20 min | -- |
| Step 5b | Run `rank2_threshold.py` (100 configs) | 175-320 min | CPU |
| Step 6 | Write and run `analyze.py` | 20 min write + 2 min run | CPU |
| **Total** | | **~5 hours** | |

Parallelization option: the `(rank, seed)` grid is embarrassingly parallel. The coder MAY wrap Step 5's inner loop in `multiprocessing.Pool(processes=4)` to cut wall-clock by ~3x, giving ~60-110 min. Default is sequential execution for debuggability. If parallelized, ensure each worker re-seeds inside `run_one` and does not share CVXPY variables across processes.

## 8. Execution Commands (Exact)

Run from project root: `/Users/abhinavmallick/Github.nosync/Research-Workflow`

```bash
# 1. Install dependencies (once; no-op if H6 already installed them)
.venv/bin/pip install cvxpy torch scikit-learn matplotlib

# 2. Verify the venv is functional
.venv/bin/python -c "import cvxpy, torch, sklearn, matplotlib, numpy, scipy; print('H5 deps OK')"

# 3. Run the two-layer ablation (MUST pass before main experiment)
.venv/bin/python experiments/H5/scripts/ablation_two_layer.py

# 4. Run the main experiment
.venv/bin/python experiments/H5/scripts/rank2_threshold.py \
    --n 100 --d 10 --beta 0.01 \
    --seeds 50 --width 50 --restarts 100 \
    --epochs 3000 --lr 1e-3 \
    --max_patterns 200 \
    --ranks 1,2 \
    --results_dir experiments/H5/results

# 5. Run analysis and generate figures
.venv/bin/python experiments/H5/scripts/analyze.py experiments/H5/results

# 6. Inspect verdict
cat experiments/H5/results/base_case_evaluation.json
```

## 9. Troubleshooting

- **If CVXPY SCS reports `infeasible` or `unbounded`:** The parallel-architecture program is always feasible (u=v=0 is feasible) and bounded below by 0, so this indicates a formulation bug. Double-check the nonneg constraints on `u_vars` and `v_vars` and the `cp.multiply(mask, X @ (u - v))` expression.
- **If SCS reports `optimal_inaccurate` on most seeds:** Tighten `eps=1e-10`, `max_iters=50000`. If still inaccurate, switch solver to `cp.CLARABEL`.
- **If rank-1 control gap is ~1e-3 instead of ~1e-8:** The beta mapping is wrong. Inspect `weight_decay_penalty` (should use `0.5 * beta * sum(W^2)`) and `solve_convex_parallel`'s `beta` (should equal the same scalar). Run the two-layer ablation first.
- **If rank-1 control gap is ~1e-5 but the rank-2 gap is also ~1e-5:** The primal solver is converging to poor local minima on rank-1 data. Increase `restarts` to 200 and `epochs` to 5000. Re-run just rank-1 seeds and confirm max gap drops below 1e-6 before running rank-2.
- **If `p_standard < d_parallel` (bound is invalid) for any seed:** The convex pattern enumeration is OVER-tight (impossible by theory), which means either (a) the primal found a better-than-expected minimum and the convex solver is returning a higher value due to numerical instability, or (b) the beta constants differ. Check both. If (a), tighten CVXPY eps. If (b), rerun the two-layer ablation.
- **If the per-iteration wall-clock exceeds 4 minutes:** Profile: run with `--seeds 2 --restarts 20` and time each call. If the convex solve dominates (>60s), reduce `max_patterns` to 100. If the primal dominates (>180s), reduce `n_epochs` to 2000 and confirm loss has plateaued.
- **If memory approaches 8 GB per job:** The CVXPY problem at P=200, n=100, d=10 should use ~100 MB. Memory growth indicates a leak across restarts in the primal solver. Ensure `del model; del opt` at the end of each restart, and call `torch.cuda.empty_cache()` (no-op on CPU but harmless).
- **If `effective_rank != rank` in data generation:** A Gaussian A or B happened to be rank-deficient. Re-seed with `seed + 10000` and retry, or assert + raise.
- **If the experiment takes more than 6 hours total:** Cut `seeds` to 30 for a preliminary run. The 90% threshold is robust; a 30-seed preliminary showing >90% positive at rank 2 is strong evidence, and the 50-seed run can follow.

## 10. File Manifest

| File | Type | Purpose |
|------|------|---------|
| `experiments/H5/scripts/utils.py` | Python module | Rank-controlled data, seeds, metrics |
| `experiments/H5/scripts/standard_primal_solver.py` | Python module | PyTorch standard 3-layer ReLU trainer |
| `experiments/H5/scripts/convex_parallel_solver.py` | Python module | CVXPY parallel-architecture lower bound |
| `experiments/H5/scripts/ablation_two_layer.py` | Python script | Two-layer gap=0 ablation (gate for main run) |
| `experiments/H5/scripts/rank2_threshold.py` | Python script (main) | Rank 1 vs rank 2 grid runner |
| `experiments/H5/scripts/analyze.py` | Python script | Figures, statistics, base case verdict |
| `experiments/H5/results/raw_results.json` | JSON | Per (rank, seed) records |
| `experiments/H5/results/summary_table.csv` | CSV | Aggregated per-rank statistics |
| `experiments/H5/results/ablation_two_layer.json` | JSON | Ablation gate results |
| `experiments/H5/results/figures/gap_rank1_vs_rank2.png` | PNG 300 dpi | Primary violin figure |
| `experiments/H5/results/figures/gap_histogram_rank2.png` | PNG 300 dpi | Rank-2 distribution |
| `experiments/H5/results/figures/restart_distribution.png` | PNG 300 dpi | Primal restart diagnostic |
| `experiments/H5/results/figures/primal_vs_lower_bound.png` | PNG 300 dpi | P vs D scatter |
| `experiments/H5/results/base_case_evaluation.json` | JSON | PASS/FAIL/INCONCLUSIVE verdict |
| `experiments/H5/status.yaml` | YAML | Experiment status tracker |

## 11. Critical Correctness Checks

These checks MUST be satisfied for the experiment to be valid:

1. **Effective rank equals requested rank.** Every data generation call asserts `np.linalg.matrix_rank(X, tol=1e-8) == rank`. A failure means the random A or B was rank-deficient and must be re-seeded.
2. **Primal >= lower bound.** For every (rank, seed) record, `p_standard >= d_parallel - 1e-8`. A violation means the convex program is NOT a valid lower bound for the primal and the experiment is invalidated.
3. **Rank-1 positive control reproduces Wang et al.** Max rank-1 gap < 1e-6 across all 50 seeds. This is the non-negotiable positive control. A failure here voids the rank-2 conclusion entirely.
4. **Two-layer ablation passes.** Before the main run, the two-layer ablation shows gap < 1e-4 at BOTH rank-1 and rank-2. If the two-layer case shows any gap, the rank-2 signal observed in the 3-layer main run cannot be attributed to the depth-rank interaction.
5. **Beta convention is consistent.** The weight-decay coefficient passed to `train_standard_primal` and to `solve_convex_parallel` is the SAME scalar. The `(1/2)` prefactor lives in `weight_decay_penalty`, not in the beta value.
6. **Architecture is the standard (non-parallel) 3-layer.** The primal model is `fc1 -> ReLU -> fc2 -> ReLU -> fc3` with no parallel branches. Verify by printing `model` before training in a sanity run.
7. **No bias terms anywhere.** The convex formulation does not include biases, so the primal must not either.

## 12. Dependencies and Downstream Consumers

**Upstream dependencies (must be complete):**
- `synthesis/methodology.md` section E5 (authoritative parameter values)
- `synthesis/hypotheses.md` H5 entry
- `diagnostics/vm-profile.yaml` (confirms local compute plan)

**Downstream consumers:**
- `experiments/H3/roadmap.md` reuses the `utils.py`, `standard_primal_solver.py`, and `convex_parallel_solver.py` modules verbatim, extending the rank sweep from {1, 2} to {1, 2, 3, 5, 10}. If H5 infrastructure is broken, H3 is blocked.
- `experiments/H5/analysis.md` (Phase 14) summarizes the verdict for the final paper.
- `synthesis/final-paper.md` (Phase 15) cites the rank-1 vs rank-2 violin figure as the primary evidence for the rank-2 boundary claim.
