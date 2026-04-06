---
phase: 7
status: complete
timestamp: 2026-04-07T21:00:00Z
depends_on: [synthesis/hypotheses.md, analysis/literature-map.md]
token_estimate: 12500
---

# Implementation Specifications: Duality Gap in Dual Convex Optimization in ReLU Neural Networks

## Summary

This document provides runnable implementation specifications for seven experiments (E1--E7) testing hypotheses H1--H7 on the duality gap in convex ReLU neural network optimization. All experiments use synthetic Gaussian data or MNIST subsets, and build on four public codebases: CRONOS (JAX/ADMM), SCNN (PyTorch/proximal gradient), convex_nn (Lasso equivalence), and standard PyTorch training loops. Compute is sized for a 4-vCPU, 16GB-RAM, no-GPU machine; experiments requiring GPU acceleration (H1 at larger scale, H2's SGD grid search) are flagged with COLAB_GATE. Of the seven, approximately three will survive Phase 11 triage. The recommended priority order places H5 first (cheapest, validates infrastructure for H3), then H6 (independent, fast), then H1 or H4 (strongest impact), with H3, H2, and H7 as resources allow.

---

## Shared Infrastructure

### Common Data Generation Module

**Filename:** `experiments/shared/data_generators.py`

```python
# Functions to implement:
# 1. generate_gaussian(n, d, seed) -> X, y
#    - X ~ N(0, I_d), y = X @ w_true + noise
#    - w_true drawn from N(0, I_d), noise ~ N(0, 0.1)
#
# 2. generate_rank_controlled(n, d, r, seed) -> X, y
#    - A ~ N(0, I) in R^{n x r}, B ~ N(0, I) in R^{d x r}
#    - X = A @ B^T (exact rank r)
#    - y = X @ w_true + noise
#
# 3. load_mnist_binary(digit_a, digit_b, n_train, n_test, seed) -> X_train, y_train, X_test, y_test
#    - Binary classification: digit_a -> +1, digit_b -> -1
#    - Flatten 28x28 to 784, normalize to [0,1]
#    - Random subsample of n_train / n_test with fixed seed
```

**Install:** `pip install numpy scikit-learn torch torchvision`

### Common Evaluation Module

**Filename:** `experiments/shared/metrics.py`

```python
# Functions to implement:
# 1. training_loss_ratio(f_method, f_reference) -> float
#    - Returns f_method / f_reference
#
# 2. normalized_gap(P_primal, D_dual) -> float
#    - Returns (P_primal - D_dual) / P_primal
#
# 3. power_law_fit(x_values, y_values) -> (alpha, R2, alpha_ci_low, alpha_ci_high)
#    - log-log linear regression: log(y) = alpha * log(x) + c
#    - Returns exponent, R^2, 95% CI on alpha via bootstrap
#
# 4. spearman_test(x_values, y_values) -> (rho, p_value)
#    - scipy.stats.spearmanr
```

**Install:** `pip install scipy numpy`

### Reproducibility Checklist

All experiments must:
- Set `numpy.random.seed(seed)`, `torch.manual_seed(seed)`, `random.seed(seed)` at script entry
- Use seeds 0..19 (20 seeds) unless otherwise specified
- Record: Python version, package versions (`pip freeze > versions.txt`), OS, CPU model
- Save raw results as JSON: `experiments/H{n}/results/raw_results.json`
- Save figures as PNG 300dpi: `experiments/H{n}/results/figures/`
- Log wall-clock time per run

### Package Dependencies (All Experiments)

```
numpy>=1.24
scipy>=1.10
scikit-learn>=1.3
torch>=2.0
torchvision>=0.15
cvxpy>=1.4
matplotlib>=3.7
pandas>=2.0
```

Additional per-experiment:
- H1, H2: `jax>=0.4.20 jaxlib>=0.4.20` (CRONOS)
- H4: No additional beyond base

---

## Experiment E1: Testing H1 -- CRONOS-AM Optimality Gap Grows Sub-linearly with Depth

**Hypothesis:**
> If CRONOS-AM is applied to train ReLU networks of increasing depth L in {2, 3, 4, 5} on fixed synthetic datasets (n=200, d=10, Gaussian), then the ratio of CRONOS-AM's achieved training loss to the exact two-layer convex optimum will increase sub-linearly with depth (i.e., the optimality ratio f_AM / f_exact scales as O(L^alpha) with alpha < 1).

**Type:** numerical-scaling

### Implementation Specification

**Repository setup:**
- Clone: `git clone https://github.com/pilancilab/CRONOS.git`
- Clone: `git clone https://github.com/pilancilab/scnn.git`
- Key files (CRONOS): `cronos/solvers/admm.py` (ADMM solver), `cronos/models/` (network definitions)
- Key files (SCNN): `scnn/` (two-layer exact convex solver)
- Install: `pip install jax jaxlib cvxpy numpy scipy matplotlib`
- Note: CRONOS requires JAX. On CPU-only machine, install `jaxlib` CPU-only wheel.

**Script to write:**
- Filename: `experiments/H1/scripts/depth_scaling.py`
- Inputs: `--n 200 --d 10 --depths 2,3,4,5 --beta 0.01 --seeds 20 --width 50`
- Outputs:
  - `experiments/H1/results/raw_results.json` (per-depth, per-seed training losses for CRONOS-AM, SGD, and exact two-layer convex)
  - `experiments/H1/results/figures/scaling_plot.png` (log-log plot of optimality ratio vs depth)
  - `experiments/H1/results/base_case_evaluation.json`
- Entry point: `.venv/bin/python experiments/H1/scripts/depth_scaling.py --n 200 --d 10 --depths 2,3,4,5 --beta 0.01 --seeds 20 --width 50`

**Algorithm per (depth L, seed s):**
1. Generate synthetic data: X ~ N(0, I) in R^{200x10}, y = X @ w_true + noise
2. Compute exact two-layer convex optimum f_exact using SCNN (CVXPY backend, MOSEK or SCS solver)
3. Train L-layer ReLU network using CRONOS-AM:
   - For L=2: use CRONOS directly (convex, global optimum)
   - For L=3,4,5: use CRONOS-AM (alternating minimization with DAdapted-Adam for inner layers, CRONOS for last two layers)
   - ADMM iterations: 200, PCG tolerance: k^{-1.2}, DAdapted-Adam: 1 epoch per alternation [Feng2023CRONOS]
   - Alternation rounds: 20
4. Train L-layer ReLU network using SGD+momentum:
   - Learning rates: {0.1, 0.01, 0.001}, momentum: 0.9, epochs: 500
   - Report best across learning rates
5. Record: f_AM, f_SGD_best, f_exact, wall_time

**Compute requirements:**
- CPU estimate: 6--10 hours on 4-core machine (4 depths x 20 seeds x 3 methods; CRONOS ADMM is compute-intensive on CPU)
- RAM peak: ~4GB
- GPU needed: Recommended but not required for proof-of-concept. COLAB_GATE for full-scale run if CPU takes >12 hours.
- Colab T4 estimate: 1--2 hours

**Data:**
- Source: synthetic (generated in script)
- Size: <1MB per run
- No download needed

### Base Case Definition

**Base case (pass/fail):**
- PASS if: Power-law fit O(L^alpha) yields alpha < 1 with R^2 > 0.8, AND the 95% CI on alpha excludes 1.0, AND the optimality ratio at L=5 is less than 2.5x the ratio at L=2
- FAIL if: alpha >= 1.0 (linear or super-linear growth), OR R^2 < 0.5 (no power-law fit)
- INCONCLUSIVE if: 0.8 <= alpha < 1.0 but CI includes 1.0, OR 0.5 <= R^2 < 0.8
- Minimum runs for conclusion: 20 seeds x 4 depths = 80 runs

### Variables

| Type | Variable | Values / Range |
|------|----------|---------------|
| Independent | Network depth L | {2, 3, 4, 5} |
| Dependent | Optimality ratio f_AM / f_exact | Continuous, >= 1.0 |
| Dependent | Scaling exponent alpha | Continuous |
| Controlled | Data (n, d) | n=200, d=10 |
| Controlled | Regularization beta | 0.01 |
| Controlled | Network width per layer | 50 |
| Controlled | ADMM iterations | 200 |
| Controlled | Alternation rounds | 20 |
| Controlled | Random seeds | 0..19 |

### Baselines

- **SGD + momentum** ([Feng2023CRONOS] comparison setup): Grid-searched learning rate from {0.1, 0.01, 0.001} with momentum 0.9. This is the standard non-convex baseline used by CRONOS authors themselves.
- **Exact two-layer convex optimum** ([Mishkin2022SCNN]): The provably globally optimal solution for L=2 via SCNN. Serves as the lower bound reference for all depths.
- **Ablation baseline:** CRONOS at L=2 only (no alternating minimization). This isolates the effect of depth from CRONOS solver quality.

### Evaluation Protocol

- **Primary metric:** Scaling exponent alpha from power-law fit of (optimality ratio) vs (depth)
- **Secondary metric:** Optimality ratio f_AM / f_exact at each depth
- **Significance test:** Bootstrap 95% CI on alpha (1000 bootstrap samples). Wilcoxon signed-rank test comparing ratios at adjacent depths.
- **Runs:** 20 seeds per depth for stability

### Expected Results

- If confirmed: alpha in (0.3, 0.8), R^2 > 0.8. The ratio grows from ~1.0 at L=2 to ~1.5--2.0 at L=5. SGD ratios are comparable or worse.
- If rejected: alpha >= 1.0. The ratio at L=5 exceeds 3x the ratio at L=2, indicating linear degradation with depth.
- If partial confirmation: Sub-linear up to L=4 but jumps at L=5, or high variance across seeds making the trend unreliable.

### Self-Consistency Check

The hypothesis specifies depths {2,3,4,5}, n=200, d=10, Gaussian data, and the metric f_AM / f_exact. The implementation uses exactly these parameters. The two-layer exact convex optimum (from SCNN/CVXPY) serves as f_exact. CRONOS-AM's alternating minimization scheme matches the hypothesis description of "non-convex inner-layer problem (Adam) and convex last-two-layer problem (CRONOS)." The power-law fit with exponent alpha directly tests "sub-linear" (alpha < 1) vs "linear or super-linear" (alpha >= 1). Consistent.

---

## Experiment E2: Testing H2 -- CRONOS-AM Solutions Within 1.5x of SGD on MNIST Subsets

**Hypothesis:**
> If CRONOS-AM and SGD (with grid-searched learning rate and momentum) are both applied to train 3-layer ReLU networks on MNIST digit-pair subsets (n in {500, 1000, 2000}), then CRONOS-AM will achieve training loss within a factor of 1.5x of the best SGD solution in at least 80% of configurations.

**Type:** empirical-verification

### Implementation Specification

**Repository setup:**
- Clone: `git clone https://github.com/pilancilab/CRONOS.git`
- Key files: `cronos/solvers/admm.py`, `cronos/models/`
- Install: `pip install jax jaxlib torch torchvision cvxpy numpy scipy matplotlib`

**Script to write:**
- Filename: `experiments/H2/scripts/cronos_vs_sgd_mnist.py`
- Inputs: `--n_values 500,1000,2000 --digit_pairs 0-1,3-8,4-9 --betas 0.001,0.01,0.1 --seeds 10 --width 50`
- Outputs:
  - `experiments/H2/results/raw_results.json`
  - `experiments/H2/results/figures/ratio_distribution.png`
  - `experiments/H2/results/base_case_evaluation.json`
- Entry point: `.venv/bin/python experiments/H2/scripts/cronos_vs_sgd_mnist.py --n_values 500,1000,2000 --digit_pairs 0-1,3-8,4-9 --betas 0.001,0.01,0.1 --seeds 10 --width 50`

**Algorithm per (n, digit_pair, beta, seed):**
1. Load MNIST binary subset: digit_a vs digit_b, n training samples, 200 test samples
2. Flatten to 784 dimensions, normalize to [0,1]
3. Train 3-layer ReLU (784 -> 50 -> 50 -> 1) using CRONOS-AM:
   - ADMM iterations: 200, alternation rounds: 20
   - DAdapted-Adam for layer 1, CRONOS for layers 2-3
   - Regularization: beta * ||w||_2^2
4. Train 3-layer ReLU (784 -> 50 -> 50 -> 1) using SGD:
   - Learning rate grid: {0.1, 0.01, 0.001, 0.0001}, momentum: {0.0, 0.9}
   - Weight decay: beta, epochs: 1000
   - Report best training loss across grid
5. Compute ratio: f_AM / f_SGD_best
6. Record: f_AM, f_SGD_best, ratio, test_accuracy_AM, test_accuracy_SGD, wall_time

**Compute requirements:**
- CPU estimate: 10--16 hours on 4-core (3 n-values x 3 digit-pairs x 3 betas x 10 seeds x 2 methods with grid search)
- RAM peak: ~6GB (MNIST fits in memory; CRONOS ADMM matrices for d=784 are large)
- GPU needed: COLAB_GATE -- JAX CRONOS on d=784 with n=2000 will be very slow on CPU. SGD grid search also benefits from GPU.
- Colab T4 estimate: 2--4 hours

**Data:**
- Source: MNIST via `torchvision.datasets.MNIST`
- Size: ~50MB download (one-time)
- Download: automatic via torchvision

### Base Case Definition

**Base case (pass/fail):**
- PASS if: Fraction of configurations where f_AM / f_SGD_best <= 1.5 exceeds 80%, AND median ratio across all configurations < 1.3
- FAIL if: Fraction where ratio <= 1.5 is below 60%, OR median ratio > 2.0
- INCONCLUSIVE if: Fraction between 60% and 80%, or median ratio between 1.3 and 2.0
- Minimum runs for conclusion: 3 n-values x 3 digit-pairs x 3 betas x 10 seeds = 270 configurations

### Variables

| Type | Variable | Values / Range |
|------|----------|---------------|
| Independent | Sample size n | {500, 1000, 2000} |
| Independent | Digit pair | {(0,1), (3,8), (4,9)} |
| Independent | Regularization beta | {0.001, 0.01, 0.1} |
| Dependent | Training loss ratio f_AM / f_SGD_best | Continuous, > 0 |
| Controlled | Network architecture | 3-layer, width 50 |
| Controlled | SGD grid | lr in {0.1, 0.01, 0.001, 0.0001}, momentum in {0.0, 0.9} |
| Controlled | SGD epochs | 1000 |
| Controlled | CRONOS-AM settings | 200 ADMM iters, 20 alternation rounds |
| Controlled | Random seeds | 0..9 |

### Baselines

- **SGD with grid search** ([Feng2023CRONOS]): The CRONOS paper itself uses SGD/Adam as the primary competitor with grid-searched learning rates from a logarithmic grid. We use a discrete grid of 8 configurations (4 LR x 2 momentum).
- **Ablation baseline:** CRONOS (two-layer only, no alternating minimization) on the same data, to isolate the contribution of the deep alternation.

### Evaluation Protocol

- **Primary metric:** Fraction of configurations where training loss ratio <= 1.5
- **Secondary metric:** Median training loss ratio with bootstrap 95% CI
- **Significance test:** One-sample binomial test: is the fraction > 0.8? (exact binomial CI)
- **Runs:** 10 seeds per configuration, 270 total configurations

### Expected Results

- If confirmed: >80% of configurations have ratio <= 1.5. Median ratio ~1.0--1.2. CRONOS-AM matches or beats SGD in most settings.
- If rejected: <60% of configurations meet the threshold. CRONOS-AM substantially worse than grid-searched SGD, especially at larger n.
- If partial confirmation: Success rate varies by n (worse at n=2000) or by beta (worse at low regularization), suggesting CRONOS-AM competitiveness depends on specific settings.

### Self-Consistency Check

The hypothesis specifies MNIST digit pairs, n in {500, 1000, 2000}, 3-layer ReLU, 1.5x threshold, 80% success rate. The implementation uses exactly these parameters plus three digit pairs and three beta values to create a grid of configurations. The SGD grid search uses matched architecture and regularization. The CRONOS-AM setup follows the paper's own alternating minimization protocol (DAdapted-Adam for inner layers, CRONOS for last two layers). Consistent.

---

## Experiment E3: Testing H3 -- Duality Gap Bounded by Data-Rank-Dependent Quantity

**Hypothesis:**
> If standard (non-parallel) 3-layer ReLU networks are trained on synthetic data matrices X in R^{n x d} with controlled rank r in {1, 2, 3, 5, d} (n=100, d=10), then the gap between the non-convex primal optimal value and the parallel-architecture convex optimum (used as a lower bound on the dual) will be zero for r=1 and will increase monotonically with rank r.

**Type:** numerical-scaling

### Implementation Specification

**Repository setup:**
- Clone: `git clone https://github.com/pilancilab/convex_nn.git`
- Key files: `convex_nn/` (convex neural network implementations)
- Install: `pip install torch cvxpy numpy scipy matplotlib`
- Note: For the parallel-architecture convex program, we construct it in CVXPY using the formulation from [WangErgenPilanci2021].

**Script to write:**
- Filename: `experiments/H3/scripts/rank_gap_sweep.py`
- Inputs: `--n 100 --d 10 --ranks 1,2,3,5,10 --beta 0.01 --seeds 20 --width 50 --restarts 50`
- Outputs:
  - `experiments/H3/results/raw_results.json`
  - `experiments/H3/results/figures/gap_vs_rank.png`
  - `experiments/H3/results/base_case_evaluation.json`
- Entry point: `.venv/bin/python experiments/H3/scripts/rank_gap_sweep.py --n 100 --d 10 --ranks 1,2,3,5,10 --beta 0.01 --seeds 20 --width 50 --restarts 50`

**Algorithm per (rank r, seed s):**
1. Generate rank-r data: A ~ N(0,I) in R^{100 x r}, B ~ N(0,I) in R^{10 x r}, X = A @ B^T
2. Generate targets: y = X @ w_true + noise (w_true ~ N(0,I_10), noise ~ N(0, 0.1))
3. **Standard 3-layer primal (non-convex):**
   - Architecture: 10 -> 50 -> 50 -> 1, ReLU activations
   - Train with PyTorch, Adam optimizer, lr=0.001, 2000 epochs
   - Multi-restart: 50 random initializations (Kaiming uniform), keep best
   - Record P_standard = best training loss across restarts
4. **Parallel-architecture convex lower bound:**
   - Construct the parallel 3-layer convex program from [WangErgenPilanci2021]:
     - K parallel sub-networks, each two-layer
     - Formulate as group-l1 regularized convex program
     - K = 2 * number_of_sign_patterns (enumerated or sampled)
   - Solve with CVXPY (SCS solver, max_iters=10000, eps=1e-8)
   - Record D_parallel = convex optimal value
5. Compute normalized gap: (P_standard - D_parallel) / P_standard
6. Verify: at r=1, gap should be < 1e-6 (positive control)

**Compute requirements:**
- CPU estimate: 4--8 hours on 4-core (5 ranks x 20 seeds x 50 restarts for non-convex + convex solve)
- RAM peak: ~3GB (small problem sizes)
- GPU needed: No. Problem is small enough for CPU.
- COLAB_GATE: No

**Data:**
- Source: synthetic (generated in script via SVD-controlled rank matrices)
- Size: <1MB per run
- No download needed

### Base Case Definition

**Base case (pass/fail):**
- PASS if: Gap < 1e-6 at r=1 (positive control), AND gap at r=d exceeds gap at r=2 by factor >= 2, AND Spearman rho > 0.8 with p < 0.05 across all (rank, seed) pairs
- FAIL if: Gap is NOT near zero at r=1 (positive control fails), OR Spearman |rho| < 0.3, OR gap is non-monotonic (decreases between consecutive ranks)
- INCONCLUSIVE if: Positive control passes but 0.3 <= rho <= 0.8, or monotonic trend exists but is not statistically significant
- Minimum runs for conclusion: 20 seeds x 5 ranks = 100 runs

### Variables

| Type | Variable | Values / Range |
|------|----------|---------------|
| Independent | Data matrix rank r | {1, 2, 3, 5, 10} |
| Dependent | Normalized gap (P_standard - D_parallel) / P_standard | Continuous, >= 0 |
| Controlled | Data dimensions (n, d) | n=100, d=10 |
| Controlled | Regularization beta | 0.01 |
| Controlled | Network width | 50 per hidden layer |
| Controlled | Non-convex restarts | 50 |
| Controlled | CVXPY solver tolerance | eps=1e-8 |
| Controlled | Random seeds | 0..19 |

### Baselines

- **Rank-1 positive control** ([WangErgenPilanci2021]): Known to have zero duality gap for standard 3-layer ReLU. Must reproduce this result to validate the experimental setup.
- **Parallel architecture at each rank** (self): The parallel convex optimum serves as the lower bound. This is not a baseline method but the reference value defining the gap.
- **Ablation baseline:** Two-layer network (no depth) at each rank. Should show zero gap at all ranks (strong duality proven for two-layer case [PilanciErgen2020]).

### Evaluation Protocol

- **Primary metric:** Spearman rank correlation between data rank r and normalized gap
- **Secondary metric:** Gap magnitude at each rank level (mean +/- std across seeds)
- **Significance test:** Spearman correlation test, alpha=0.05. Additionally, Mann-Whitney U test between gap distributions at r=1 vs r=d.
- **Runs:** 20 seeds per rank

### Expected Results

- If confirmed: Zero gap at r=1, small positive gap at r=2 (~0.01--0.05), increasing to r=d (~0.1--0.3). Clear monotonic trend with Spearman rho > 0.8.
- If rejected: Gap is near zero at all ranks (strong duality holds more broadly), or gap is non-monotonic (no rank dependence).
- If partial confirmation: Monotonic increase exists but is weak (small absolute gap values), or the relationship saturates at intermediate ranks.

### Self-Consistency Check

The hypothesis specifies standard (non-parallel) 3-layer ReLU, rank r in {1,2,3,5,d}, n=100, d=10, and the parallel-architecture convex optimum as lower bound. The implementation matches: standard 3-layer network trained with multi-restart Adam (non-convex primal), parallel-architecture convex program via CVXPY (lower bound). The normalized gap formula matches the hypothesis. The positive control at r=1 is included. Consistent.

---

## Experiment E4: Testing H4 -- Kim et al. O(sqrt(log n)) Bound Is Loose

**Hypothesis:**
> If the Gaussian randomized relaxation from Kim and Pilanci (2024) is applied to two-layer ReLU networks on synthetic Gaussian data with n in {50, 100, 200, 500, 1000} and d=20, then the actual relative optimality gap p_tilde/p* will be bounded by C * (log n)^{1/4} for some constant C < 1, which is strictly tighter than the proven O(sqrt(log n)) upper bound.

**Type:** numerical-scaling

### Implementation Specification

**Repository setup:**
- Clone: `git clone https://github.com/pilancilab/scnn.git`
- Key files: `scnn/` (two-layer exact convex solver)
- Install: `pip install torch cvxpy numpy scipy matplotlib`

**Script to write:**
- Filename: `experiments/H4/scripts/bound_tightness.py`
- Inputs: `--n_values 50,100,200,500,1000 --d 20 --beta 0.01 --seeds 20 --P_samples 500`
- Outputs:
  - `experiments/H4/results/raw_results.json`
  - `experiments/H4/results/figures/gap_vs_n.png` (log-log with theoretical bound overlay)
  - `experiments/H4/results/base_case_evaluation.json`
- Entry point: `.venv/bin/python experiments/H4/scripts/bound_tightness.py --n_values 50,100,200,500,1000 --d 20 --beta 0.01 --seeds 20 --P_samples 500`

**Algorithm per (n, seed s):**
1. Generate Gaussian data: X ~ N(0, I_d) in R^{n x 20}, y = X @ w_true + noise
2. **Exact convex solution (p*):**
   - Enumerate all sign patterns (for small n) or sample P_samples=500 random hyperplane arrangements
   - Solve the convex group-l1 program via CVXPY:
     - min_{v} 0.5 * ||sum_i D_i X v_i - y||^2 + beta * sum_i ||v_i||_2
     - where D_i are diagonal sign matrices
   - Use SCS solver, eps=1e-8
   - Record p*
3. **Gaussian relaxation (p_tilde):**
   - Implement Kim et al.'s randomized relaxation:
     - Sample Gaussian vectors g_1, ..., g_P from N(0, I_d)
     - Construct sign patterns D_i = diag(sign(X @ g_i))
     - Solve the same convex program restricted to these P patterns
   - P = ceil(C_0 * d * log(n)) per the theoretical prescription
   - Record p_tilde
4. Compute relative optimality gap: p_tilde / p*
5. Compute theoretical upper bound: C_theory * sqrt(log(n)) where C_theory is estimated from the n=50 case
6. Fit power law: gap = A * (log n)^gamma, estimate gamma

**Compute requirements:**
- CPU estimate: 6--12 hours on 4-core (5 n-values x 20 seeds, with CVXPY solve for each; n=1000 with d=20 is the bottleneck)
- RAM peak: ~8GB (CVXPY matrices grow as O(n * d * P))
- GPU needed: No for n <= 500. For n=1000, CVXPY/SCS may be slow but still CPU-feasible.
- COLAB_GATE: No (but n=1000 may take extended time; fallback: reduce to n=500 max)

**Data:**
- Source: synthetic Gaussian (generated in script)
- Size: <1MB per run
- No download needed

### Base Case Definition

**Base case (pass/fail):**
- PASS if: Power-law fit of gap vs log(n) yields exponent gamma < 0.5 with R^2 > 0.7, AND at n=1000 the measured gap is less than 50% of the theoretical upper bound
- FAIL if: gamma >= 0.5 (matches the theoretical rate), OR R^2 < 0.4 (no discernible scaling pattern)
- INCONCLUSIVE if: 0.4 <= gamma < 0.5 but CI includes 0.5, OR 0.4 <= R^2 < 0.7
- Minimum runs for conclusion: 20 seeds x 5 n-values = 100 runs

### Variables

| Type | Variable | Values / Range |
|------|----------|---------------|
| Independent | Sample size n | {50, 100, 200, 500, 1000} |
| Dependent | Relative optimality gap p_tilde / p* | Continuous, >= 1.0 |
| Dependent | Scaling exponent gamma | Continuous |
| Controlled | Dimensionality d | 20 |
| Controlled | Regularization beta | 0.01 |
| Controlled | Number of sampled patterns P_samples | 500 (for exact), d*log(n) (for relaxation) |
| Controlled | CVXPY solver | SCS, eps=1e-8 |
| Controlled | Random seeds | 0..19 |

### Baselines

- **Exact convex solution** ([PilanciErgen2020], [Mishkin2022SCNN]): The globally optimal training loss obtained by solving the full convex program. This is the reference p* against which the relaxation is measured.
- **Theoretical upper bound** ([Kim2024]): The proven O(sqrt(log n)) bound. Plotted as an overlay to show how tight it is.
- **Uniform random pattern baseline:** Instead of Gaussian-drawn patterns, use uniformly random sign patterns. Tests whether the Gaussian structure of the relaxation matters.

### Evaluation Protocol

- **Primary metric:** Scaling exponent gamma from power-law fit gap = A * (log n)^gamma
- **Secondary metric:** Ratio of measured gap to theoretical bound at each n
- **Significance test:** Bootstrap 95% CI on gamma (1000 samples). Two-sample Kolmogorov-Smirnov test between gap distributions at n=50 and n=1000.
- **Runs:** 20 seeds per n

### Expected Results

- If confirmed: gamma ~ 0.2--0.4 (tighter than sqrt(log n)), measured gap at n=1000 is <50% of theoretical bound. The Gaussian relaxation is much more practical than the worst case suggests.
- If rejected: gamma ~ 0.5, matching the theoretical bound. The bound is tight, meaning it accurately reflects typical-case behavior.
- If partial confirmation: gamma < 0.5 but the improvement is small (e.g., gamma=0.45), or the gap variance is very high across seeds.

### Self-Consistency Check

The hypothesis specifies n in {50,...,1000}, d=20, Gaussian data, the relative optimality gap p_tilde/p*, and the target scaling (log n)^{1/4}. The implementation computes p* via full convex solve and p_tilde via Gaussian relaxation following Kim et al.'s construction. The power-law fit on log(n) directly tests the exponent. The theoretical bound overlay provides visual validation. Consistent.

---

## Experiment E5: Testing H5 -- Duality Gap Emerges at Rank 2

**Hypothesis:**
> If standard 3-layer ReLU networks are trained on synthetic data with rank r=2 (n=100, d=10), then the gap between the standard non-convex primal optimum and the parallel-architecture convex lower bound will be strictly positive (exceeding numerical tolerance of 1e-4), with the rank-1 case yielding zero gap (positive control).

**Type:** empirical-verification

### Implementation Specification

**Repository setup:**
- Clone: `git clone https://github.com/pilancilab/convex_nn.git`
- Install: `pip install torch cvxpy numpy scipy matplotlib`

**Script to write:**
- Filename: `experiments/H5/scripts/rank2_threshold.py`
- Inputs: `--n 100 --d 10 --beta 0.01 --seeds 50 --width 50 --restarts 100`
- Outputs:
  - `experiments/H5/results/raw_results.json`
  - `experiments/H5/results/figures/gap_rank1_vs_rank2.png` (violin plots)
  - `experiments/H5/results/base_case_evaluation.json`
- Entry point: `.venv/bin/python experiments/H5/scripts/rank2_threshold.py --n 100 --d 10 --beta 0.01 --seeds 50 --width 50 --restarts 100`

**Algorithm per (rank r in {1, 2}, seed s):**
1. Generate rank-r data:
   - r=1: A ~ N(0,I) in R^{100 x 1}, B ~ N(0,I) in R^{10 x 1}, X = A @ B^T
   - r=2: A ~ N(0,I) in R^{100 x 2}, B ~ N(0,I) in R^{10 x 2}, X = A @ B^T
2. Generate targets: y = X @ w_true + noise
3. **Standard 3-layer primal:**
   - Architecture: 10 -> 50 -> 50 -> 1, ReLU
   - Train with PyTorch Adam, lr=0.001, 3000 epochs
   - 100 random restarts, keep best training loss P_standard
4. **Parallel-architecture convex lower bound:**
   - K parallel sub-networks with group-l1 regularization
   - CVXPY with SCS solver, eps=1e-9, max_iters=20000
   - Record D_parallel
5. Compute gap: (P_standard - D_parallel) / P_standard
6. Quality check: verify P_standard >= D_parallel (primal >= lower bound)

**Compute requirements:**
- CPU estimate: 3--5 hours on 4-core (2 ranks x 50 seeds x 100 restarts; but n=100, d=10 is small)
- RAM peak: ~2GB
- GPU needed: No
- COLAB_GATE: No

**Data:**
- Source: synthetic (rank-controlled via SVD construction)
- Size: <1MB
- No download needed

### Base Case Definition

**Base case (pass/fail):**
- PASS if: Rank-1 positive control gap < 1e-6 across all 50 seeds, AND rank-2 gap > 1e-4 in at least 90% of seeds (45/50), AND one-sample t-test on rank-2 gaps rejects zero mean (p < 0.01)
- FAIL if: Rank-1 positive control fails (gap > 1e-4), OR rank-2 gap < 1e-4 in more than 50% of seeds
- INCONCLUSIVE if: Rank-1 passes but rank-2 gap > 1e-4 in only 50%--90% of seeds, or t-test p-value between 0.01 and 0.05
- Minimum runs for conclusion: 50 seeds x 2 ranks = 100 runs

### Variables

| Type | Variable | Values / Range |
|------|----------|---------------|
| Independent | Data matrix rank r | {1, 2} |
| Dependent | Normalized gap (P_standard - D_parallel) / P_standard | Continuous, >= 0 |
| Controlled | Data dimensions (n, d) | n=100, d=10 |
| Controlled | Regularization beta | 0.01 |
| Controlled | Network width | 50 |
| Controlled | Non-convex restarts | 100 |
| Controlled | CVXPY solver tolerance | eps=1e-9 |
| Controlled | Random seeds | 0..49 |

### Baselines

- **Rank-1 positive control** ([WangErgenPilanci2021]): Known zero duality gap. Must reproduce.
- **Two-layer network control:** Same data, two-layer architecture. Should show zero gap at both ranks (proven by [PilanciErgen2020]). Validates that the gap at rank-2 (if found) is a depth phenomenon, not a data phenomenon.

### Evaluation Protocol

- **Primary metric:** Binary outcome per seed: gap > 1e-4 or not, at rank 2
- **Secondary metric:** Gap magnitude distribution at rank 2 (mean, median, std, IQR)
- **Significance test:** One-sample t-test on rank-2 gaps testing H0: mean=0 (alpha=0.01). Supplementary: Mann-Whitney U between rank-1 and rank-2 gap distributions.
- **Runs:** 50 seeds for high statistical power on binary outcome

### Expected Results

- If confirmed: Rank-1 gaps all < 1e-6. Rank-2 gaps in range [0.001, 0.1] with >90% positive. Sharp transition from zero to non-zero.
- If rejected: Rank-2 gaps indistinguishable from numerical noise (~1e-7), suggesting strong duality may hold at rank 2.
- If partial confirmation: Some rank-2 seeds show positive gaps but others do not, possibly depending on the specific data realization.

### Self-Consistency Check

The hypothesis specifies rank 2 as the test case, rank 1 as positive control, n=100, d=10, tolerance 1e-4, and 90% success rate across seeds. The implementation uses exactly these parameters with 50 seeds (matching the hypothesis specification of "50+ seeds") and 100 restarts for the non-convex solver (matching the hypothesis specification of "50+" restarts, actually exceeding it). The parallel-architecture convex program is the same proxy lower bound described in the hypothesis. Consistent.

---

## Experiment E6: Testing H6 -- Elastic Net Breaks Convex Reformulation

**Hypothesis:**
> If two-layer ReLU networks are trained with elastic net regularization (lambda_1 ||w||_1 + lambda_2 ||w||_2^2, with lambda_1/lambda_2 = 1) instead of pure l2^2 weight decay, then the gap between the non-convex training loss and the best achievable by the standard convex reformulation (applied with l2^2 only) will exceed 10% of the non-convex optimal value.

**Type:** empirical-verification

### Implementation Specification

**Repository setup:**
- Clone: `git clone https://github.com/pilancilab/scnn.git`
- Key files: `scnn/` (two-layer convex solver with l2^2 regularization)
- Install: `pip install torch cvxpy numpy scipy matplotlib`

**Script to write:**
- Filename: `experiments/H6/scripts/elastic_net_break.py`
- Inputs: `--n 200 --d 10 --lambda_ratios 0,0.1,0.5,1.0,2.0,5.0 --lambda2 0.01 --seeds 20 --width 100 --restarts 50`
- Outputs:
  - `experiments/H6/results/raw_results.json`
  - `experiments/H6/results/figures/gap_vs_ratio.png`
  - `experiments/H6/results/base_case_evaluation.json`
- Entry point: `.venv/bin/python experiments/H6/scripts/elastic_net_break.py --n 200 --d 10 --lambda_ratios 0,0.1,0.5,1.0,2.0,5.0 --lambda2 0.01 --seeds 20 --width 100 --restarts 50`

**Algorithm per (lambda_ratio, seed s):**
1. Generate Gaussian data: X ~ N(0, I) in R^{200 x 10}, y = X @ w_true + noise
2. Set lambda_1 = lambda_ratio * lambda_2, lambda_2 = 0.01
3. **Non-convex elastic net training (f_elastic):**
   - Two-layer ReLU: 10 -> 100 -> 1
   - Loss: 0.5 * ||f(X) - y||^2 + lambda_1 * sum(|w|) + lambda_2 * ||w||^2
   - Optimizer: Adam, lr=0.001, 3000 epochs
   - 50 random restarts, keep best
   - Record f_elastic = best training loss (including regularization)
4. **Convex l2^2 reformulation (f_convex):**
   - Solve the standard convex program from [PilanciErgen2020] with beta = lambda_2
   - Use SCNN or CVXPY with SCS solver
   - This gives the global optimum under pure l2^2 regularization
   - Evaluate this solution under the elastic net loss: f_convex_elastic = training_loss(convex_solution) evaluated with elastic net penalty
   - Record f_convex = convex optimal under l2^2, f_convex_elastic = same solution evaluated under elastic net
5. Compute gap: (f_elastic - f_convex) / f_elastic
   - Note: f_elastic uses elastic net penalty; f_convex uses l2^2 penalty
   - A large positive gap means the convex solution (optimized for l2^2) is much worse than the elastic net optimum
6. **Control:** lambda_ratio = 0 (pure l2^2) should yield gap < 1%

**Compute requirements:**
- CPU estimate: 2--4 hours on 4-core (6 ratios x 20 seeds x 50 restarts; n=200, d=10 is small)
- RAM peak: ~2GB
- GPU needed: No
- COLAB_GATE: No

**Data:**
- Source: synthetic Gaussian (generated in script)
- Size: <1MB
- No download needed

### Base Case Definition

**Base case (pass/fail):**
- PASS if: At lambda_1/lambda_2 = 1, the gap exceeds 10% across all 20 seeds, AND the pure l2^2 control (lambda_1 = 0) yields gap < 1% across all seeds
- FAIL if: Gap < 5% at lambda_1/lambda_2 = 1, suggesting the convex reformulation is approximately valid even with elastic net
- INCONCLUSIVE if: Gap between 5% and 10% at the target ratio, or high variance across seeds
- Minimum runs for conclusion: 6 ratios x 20 seeds = 120 runs

### Variables

| Type | Variable | Values / Range |
|------|----------|---------------|
| Independent | lambda_1 / lambda_2 ratio | {0, 0.1, 0.5, 1.0, 2.0, 5.0} |
| Dependent | Normalized gap (f_elastic - f_convex) / f_elastic | Continuous |
| Controlled | lambda_2 | 0.01 |
| Controlled | Data dimensions (n, d) | n=200, d=10 |
| Controlled | Network width | 100 |
| Controlled | Non-convex restarts | 50 |
| Controlled | CVXPY solver | SCS, eps=1e-8 |
| Controlled | Random seeds | 0..19 |

### Baselines

- **Pure l2^2 control** (lambda_1 = 0) ([PilanciErgen2020]): Known to have zero duality gap for two-layer ReLU. Must produce gap < 1%.
- **Ablation: Non-convex l2^2 training** (same non-convex optimizer but with l2^2 only): Verifies that the non-convex solver can find solutions matching the convex optimum when the theory applies.
- **Increasing lambda_1 sweep:** Tests whether the gap grows monotonically with the l1 component, which would support the hypothesis that the l1 term specifically breaks the rescaling lemma.

### Evaluation Protocol

- **Primary metric:** Gap magnitude at lambda_1/lambda_2 = 1, averaged across seeds
- **Secondary metric:** Gap as a function of lambda_1/lambda_2 (monotonicity of the breaking effect)
- **Significance test:** One-sample t-test on gaps at lambda_1/lambda_2 = 1 testing H0: gap <= 0.10 vs H1: gap > 0.10 (one-sided). Paired t-test between control (ratio=0) and test (ratio=1) gaps.
- **Runs:** 20 seeds per ratio

### Expected Results

- If confirmed: Control gap < 1%, test gap > 10% at ratio=1, gap increases monotonically with the ratio. Demonstrates that the l1 component breaks the convex reformulation.
- If rejected: Gap < 5% even at high ratios, suggesting the convex l2^2 solution is a surprisingly good approximation even for elastic net regularization.
- If partial confirmation: Gap increases with ratio but never reaches 10%, or is positive but highly variable across seeds.

### Self-Consistency Check

The hypothesis specifies elastic net with lambda_1/lambda_2 = 1, two-layer ReLU, n=200, d=10, Gaussian data, 10% threshold, and the comparison between non-convex elastic net and convex l2^2 reformulation. The implementation matches: non-convex training with custom elastic net penalty in PyTorch, convex solution via SCNN/CVXPY with l2^2 only, and the gap computed as described. The sweep over lambda_1/lambda_2 ratios extends beyond the hypothesis to provide additional context. The pure l2^2 control is included. Consistent.

---

## Experiment E7: Testing H7 -- Convex-Optimal Solutions Do Not Generalize Better Than SGD

**Hypothesis:**
> If two-layer ReLU networks are trained on MNIST binary classification (digits 3 vs 8, n=1000) using both the SCNN convex solver (achieving global training optimum) and SGD with early stopping (achieving a local minimum), then the convex-optimal solution will not achieve strictly better test accuracy than the best SGD solution.

**Type:** empirical-verification

### Implementation Specification

**Repository setup:**
- Clone: `git clone https://github.com/pilancilab/scnn.git`
- Clone: `git clone https://github.com/pilancilab/scnn_experiments.git`
- Key files (scnn): `scnn/` (convex solver)
- Key files (scnn_experiments): reference for MNIST setup
- Install: `pip install torch torchvision cvxpy numpy scipy matplotlib`

**Script to write:**
- Filename: `experiments/H7/scripts/generalization_comparison.py`
- Inputs: `--n_train 1000 --n_test 500 --digit_pairs 3-8,0-1,4-9,2-7,5-6 --betas 0.001,0.005,0.01,0.05,0.1 --seeds 10 --width 200`
- Outputs:
  - `experiments/H7/results/raw_results.json`
  - `experiments/H7/results/figures/accuracy_comparison.png`
  - `experiments/H7/results/figures/accuracy_vs_beta.png`
  - `experiments/H7/results/base_case_evaluation.json`
- Entry point: `.venv/bin/python experiments/H7/scripts/generalization_comparison.py --n_train 1000 --n_test 500 --digit_pairs 3-8,0-1,4-9,2-7,5-6 --betas 0.001,0.005,0.01,0.05,0.1 --seeds 10 --width 200`

**Algorithm per (digit_pair, beta, seed):**
1. Load MNIST binary subset: digit_a vs digit_b, n_train=1000, n_test=500
2. Flatten to 784, normalize to [0,1]
3. **Convex solver (SCNN):**
   - Two-layer ReLU: 784 -> 200 -> 1
   - Solve convex reformulation with CVXPY or SCNN augmented Lagrangian solver
   - Regularization: beta * group-l1 (equivalent to l2^2 weight decay via rescaling)
   - Record: f_convex (training loss), test_accuracy_convex
4. **SGD with early stopping:**
   - Same architecture: 784 -> 200 -> 1
   - SGD with momentum 0.9, lr from {0.1, 0.01, 0.001}, weight decay beta
   - Train for 2000 epochs, save model at epoch with best validation accuracy (use 20% of training data for validation)
   - Record: f_sgd (training loss), test_accuracy_sgd
5. **SGD without early stopping (full training):**
   - Same as above but report final-epoch model
   - Record: f_sgd_full, test_accuracy_sgd_full
6. Compute: accuracy_difference = test_accuracy_convex - test_accuracy_sgd
7. Compute: training_loss_ratio = f_sgd / f_convex (should be >= 1.0)

**Compute requirements:**
- CPU estimate: 6--10 hours on 4-core (5 digit-pairs x 5 betas x 10 seeds x 3 methods; SCNN on d=784 is the bottleneck)
- RAM peak: ~8GB (SCNN convex program for d=784 has large matrices)
- GPU needed: COLAB_GATE for SCNN on d=784. The convex program at width 200 with 784 input features generates very large constraint matrices. Consider reducing width to 50 for CPU-only feasibility.
- Colab T4 estimate: 2--3 hours
- **CPU fallback:** Reduce width to 50, n_train to 500. This weakens the experiment but makes it CPU-feasible.

**Data:**
- Source: MNIST via `torchvision.datasets.MNIST`
- Size: ~50MB download (one-time)
- Download: automatic via torchvision

### Base Case Definition

**Base case (pass/fail):**
- PASS if: Test accuracy of convex minus test accuracy of SGD is <= 0 (convex no better) in at least 70% of (beta, digit_pair) configurations, AND bootstrap 95% CI for mean accuracy difference includes zero or is negative
- FAIL if: Convex solution outperforms SGD by >= 2 percentage points in more than 50% of configurations, suggesting optimization quality does translate to generalization
- INCONCLUSIVE if: Mixed results with no clear pattern, or accuracy differences are all < 1 percentage point (both methods perform essentially identically)
- Minimum runs for conclusion: 5 digit-pairs x 5 betas x 10 seeds = 250 runs

### Variables

| Type | Variable | Values / Range |
|------|----------|---------------|
| Independent | Regularization beta | {0.001, 0.005, 0.01, 0.05, 0.1} |
| Independent | Digit pair | {(3,8), (0,1), (4,9), (2,7), (5,6)} |
| Dependent | Test accuracy difference (convex - SGD) | Continuous, in [-1, 1] |
| Dependent | Training loss ratio (SGD / convex) | Continuous, >= 1.0 |
| Controlled | Network architecture | Two-layer, width 200 (or 50 for CPU fallback) |
| Controlled | Training set size | n=1000 |
| Controlled | Test set size | n=500 |
| Controlled | SGD lr grid | {0.1, 0.01, 0.001} |
| Controlled | SGD epochs | 2000 |
| Controlled | Random seeds | 0..9 |

### Baselines

- **SCNN convex solver** ([Mishkin2022SCNN]): Global optimum of the convex reformulation. Achieves the best possible training loss under the regularized objective.
- **SGD with early stopping:** The standard practical approach. Early stopping provides implicit regularization that may benefit generalization.
- **SGD full training (no early stopping):** Ablation to test whether early stopping specifically (not just SGD) is what provides generalization benefit.

### Evaluation Protocol

- **Primary metric:** Test accuracy difference (convex - SGD) across configurations
- **Secondary metric:** Fraction of configurations where convex outperforms SGD
- **Significance test:** Paired t-test on accuracy differences across seeds within each (digit_pair, beta) configuration. Bootstrap 95% CI on overall mean accuracy difference. Bonferroni correction for 25 configuration tests.
- **Runs:** 10 seeds per configuration, 250 total

### Expected Results

- If confirmed: Convex solution test accuracy is comparable to or slightly worse than SGD with early stopping. Mean accuracy difference near zero or slightly negative. Training loss ratio > 1.3 for SGD, confirming SGD is suboptimal in training but not in generalization.
- If rejected: Convex solution consistently outperforms SGD by 2+ percentage points, suggesting that finding the true global optimum of the regularized problem does help generalization.
- If partial confirmation: Results depend strongly on beta -- at low beta (underfitting), convex wins; at high beta (overfitting), SGD with early stopping wins.

### Self-Consistency Check

The hypothesis specifies MNIST digits 3 vs 8, n=1000, two-layer ReLU, SCNN convex solver, SGD with early stopping, matched regularization, and test accuracy as the metric. The implementation expands to 5 digit pairs (for robustness) and 5 beta values (for sweep), which is compatible with the hypothesis while strengthening it. The "no strictly better" criterion is tested via the accuracy difference and the 70% threshold. Consistent.

---

## Implementation Priority Order

1. **E5 (H5: Rank-2 threshold test)** -- Cheapest experiment (2--3 hours CPU), validates the 3-layer standard network infrastructure and convex lower bound computation that E3 also needs. If the gap is zero at rank 2, it immediately informs H3's design. No GPU needed.

2. **E6 (H6: Elastic net breaks reformulation)** -- Independent, fast (2--4 hours CPU), no GPU needed. Tests a clean mechanistic question about whether the rescaling lemma breaks with l1 regularization. Uses simple two-layer setup with small dimensions.

3. **E4 (H4: O(sqrt(log n)) bound tightness)** -- Independent, moderate compute (6--12 hours CPU), no GPU needed. Clean numerical experiment comparing empirical gaps to theoretical bounds. Only risk is n=1000 with d=20 being slow in CVXPY.

4. **E1 (H1: CRONOS-AM depth scaling)** -- High impact (Tier 1 gap), but requires CRONOS JAX installation which may be finicky on CPU-only machine. COLAB_GATE for full-scale run. Run small-scale proof-of-concept on CPU first.

5. **E3 (H3: Rank-dependent gap bound)** -- Extends E5 across all ranks. Run after E5 validates infrastructure. Moderate compute.

6. **E2 (H2: CRONOS-AM vs SGD on MNIST)** -- COLAB_GATE (d=784 with CRONOS is GPU-intensive). Run after E1 validates CRONOS installation. Dependent on CRONOS infrastructure working.

7. **E7 (H7: Generalization comparison)** -- COLAB_GATE for SCNN on d=784. Lower priority per sanity check (MEDIUM concern about overlap with broader optimization-generalization literature). Run if resources allow after higher-priority experiments complete.

---

## Compute Budget Summary

| Experiment | CPU Hours (est.) | RAM Peak | GPU Needed | COLAB_GATE |
|-----------|-----------------|----------|------------|------------|
| E5 (H5)  | 3--5            | 2GB      | No         | No         |
| E6 (H6)  | 2--4            | 2GB      | No         | No         |
| E4 (H4)  | 6--12           | 8GB      | No         | No         |
| E1 (H1)  | 6--10 (small)   | 4GB      | Recommended| Yes (full) |
| E3 (H3)  | 4--8            | 3GB      | No         | No         |
| E2 (H2)  | 10--16          | 6GB      | Yes        | Yes        |
| E7 (H7)  | 6--10           | 8GB      | Yes        | Yes        |
| **Total** | **37--65**      | **8GB max** | 3 of 7 | 3 of 7   |

CPU-only feasible experiments (E5, E6, E4, E3) total 15--29 hours. GPU-requiring experiments (E1-full, E2, E7) add 18--36 hours but can be parallelized on Colab.
