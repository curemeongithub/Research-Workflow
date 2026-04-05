---
phase: 7
status: complete
timestamp: 2026-04-06T01:30:00Z
depends_on: [synthesis/hypotheses.md, analysis/literature-map.md]
hypotheses_covered: 6
source_lookups_used: 3
token_estimate: 6800
---

# Experimental Methodology: Dual Convex Optimization in ReLU Neural Networks

## Methodology Summary

This experimental program tests six hypotheses spanning three Tier 1 foundational gaps (full-rank tractability, recurrent architectures, duality gap bounds) and three Tier 2 extensions (adversarial robustness, multi-head attention, quantized weights). The methodology prioritizes falsifiability over confirmatory bias: every experiment specifies explicit rejection criteria, ablation baselines, and multiple statistical validation runs. Methodological precedents from Pilanci-Ergen (2020), Wang et al. (2023), and CRONOS (2024) establish the baseline convex solvers, while experimental protocols follow established benchmarks (CIFAR-10, MNIST, sequential MNIST) with standard train/val/test splits. The experiments span computational scales from tractable two-layer networks (E6) to intractable deep 3-layer serial networks (E3), with runtime budgets ranging from GPU-hours (E1, E4) to GPU-days (E2, E5). Risk mitigation strategies include staged execution (test simplified cases before full experiments), ablation studies to isolate confounds, and reproducibility checklists ensuring independent verification.

---

## Experiment E1: Testing H1 — Polynomial-Time Certified Approximation for Full-Rank Data

**Hypothesis:**
> If a hierarchical zonotope subsampling tree is constructed over nested hyperplane arrangements for an $L$-layer ReLU network trained on rank-$r$ data with $r = \min(n,d)$ (full-rank), and the sampling budget per layer is $B_\ell = C \cdot d^2 \log(1/\delta)$ for constant $C$, then the resulting approximate solution achieves training loss within $(1 + \epsilon)$ of the global convex optimum $L^*$ with probability $\geq 1 - \delta$, as measured by the ratio $L_{\text{approx}} / L^*$ on CIFAR-10 (rank-2688), under a wall-clock time budget $\leq 10 \times$ the CRONOS runtime.

### Experimental Setup

**System:** Two-layer ReLU network with $m = 512$ neurons trained on CIFAR-10 (downsampled to $32 \times 32 \times 3 = 3072$ dimensions, $n = 5000$ training samples, full rank $r = \min(5000, 3072) = 3072$).

**Intervention:** Hierarchical zonotope subsampling with sampling budget $B_\ell \in \{10^3, 10^4, 10^5, 10^6\}$ patterns per layer (logarithmic sweep to identify scaling threshold).

**Control condition:** Exact convex solver on a rank-reduced subset ($r = 50$) to obtain ground-truth global optimum $L^*_{\text{exact}}$.

### Variables

| Type | Variable | Values / Range |
|------|----------|---------------|
| Independent | Sampling budget $B_\ell$ | $\{10^3, 10^4, 10^5, 10^6\}$ |
| Independent | Network depth $L$ | $\{2, 3\}$ layers |
| Dependent | Approximation ratio $L_{\text{approx}} / L^*$ | Real-valued $\geq 1$ |
| Dependent | Runtime (seconds) | Positive real |
| Controlled | Data rank $r$ | 3072 (CIFAR-10 full rank) |
| Controlled | Training set size $n$ | 5000 samples |
| Controlled | Network width $m$ | 512 neurons |
| Controlled | Duality gap tolerance | $< 10^{-4}$ (verified via complementary slackness) |

### Baselines

1. **CRONOS (Klusowski et al. 2024)**: GPU-accelerated randomized hyperplane sampling without approximation certificates. CRONOS achieves $\approx 90\%$ validation accuracy on CIFAR-10 in $\sim 3$ seconds per epoch. **Why this baseline:** Current state-of-the-art for scalable convex training, lacks optimality guarantees.

2. **Exact convex solver on rank-50 data**: Full hyperplane enumeration on a rank-reduced version ($r = 50$) of CIFAR-10 (via PCA projection). **Why this baseline:** Provides ground-truth $L^*$ for computing approximation ratio; infeasible on full-rank data.

3. **Ablation: uniform random sampling**: Sample $B_\ell$ patterns uniformly at random from the full $O(n^r)$ arrangement without hierarchical tree structure. **Why this baseline:** Isolates the value of hierarchical sampling vs. brute-force randomization.

### Data Requirements

- **Dataset:** CIFAR-10 [Krizhevsky 2010], 32×32 RGB images, 10 classes
- **Split:** Train/Val/Test = 5000/1000/4000 (standard CIFAR-10 subset from CRONOS experiments)
- **Preprocessing:** Mean subtraction, no whitening (to preserve full rank)
- **Compute:** Rank enumeration: ~$10^5$ patterns requires $\sim 10$ GB GPU memory; training conv ex solver: $\sim 1$ GPU-hour per trial (estimated from CRONOS scaling)
- **Accessibility:** CIFAR-10 is public domain

### Evaluation Protocol

- **Primary metric:** Approximation ratio $\rho = L_{\text{approx}} / L^*$, where $L_{\text{approx}}$ is training cross-entropy loss of the hierarchically sampled solution and $L^*$ is the exact convex optimum on rank-50 data (scaled to full-rank via Lagrangian relaxation bound).
- **Success criterion:** $\rho \leq 1.1$ for $\epsilon = 0.1$, $\delta = 0.05$ across $\geq 95\%$ of trials.
- **Secondary metrics:**
  - Test accuracy (ensure approximation doesn't degrade generalization)
  - Runtime relative to CRONOS baseline
  - Zonotope generator matrix condition number (detect degeneracy)
- **Significance test:** Paired t-test comparing $\rho$ distributions between hierarchical and uniform sampling, $\alpha = 0.05$.
- **Runs:** 20 random train/val splits with different random seeds for zonotope sampling; report mean $\pm$ standard deviation.

### Expected Results

**If H1 is confirmed:**
- For $B_\ell \geq 10^5$, approximation ratio $\rho \in [1.0, 1.1]$ with probability $> 0.95$.
- Runtime scales as $O(B_\ell \cdot d \cdot m)$, approximately linear in sampling budget.
- Hierarchical sampling achieves tighter ratios than uniform sampling at equal budget.

**If H1 is rejected:**
- $\rho > 1.1$ for $> 5\%$ of trials even at maximum budget $B_\ell = 10^6$, indicating hierarchical sampling fails to capture critical rare patterns.
- Or runtime exceeds $10 \times$ CRONOS ($> 30$ seconds), indicating polynomial scaling breaks down.

**Partial confirmation:**
- If $\rho \leq 1.1$ holds only for $L = 2$ but fails for $L = 3$, this suggests nested arrangements require super-polynomial sampling budgets in depth.

### Effort and Risk Assessment

- **Effort:** MEDIUM (2-3 weeks)
  - Week 1: Implement hierarchical zonotope subsampling tree (extend scipy.spatial KDTree to arrangement partitioning)
  - Week 2: Run exact solver on rank-50 baseline to establish $L^*$; run 20 trials of hierarchical sampling
  - Week 3: Ablation studies and sensitivity analysis
- **Primary risk:** Zonotope sampling overhead dominates runtime, making even $B_\ell = 10^5$ intractable.
  - **Mitigation:** Start with $L = 2$, $B_\ell = 10^3$ pilot study; if runtime exceeds 1 hour, pivot to approximate zonotope bounds (axis-aligned bounding boxes).
- **Secondary risk:** Rank-50 ground truth $L^*$ may not extrapolate to full-rank regime due to nonlinear dependence on data structure.
  - **Mitigation:** Validate extrapolation by testing on synthetic data with controllable rank $r \in \{10, 50, 100\}$ and verifying $L^*(r)$ follows predicted scaling law.

---

## Experiment E2: Testing H2 — Convex Reformulation for Unrolled Recurrent Networks via Temporal Hyperplane Coupling

**Hypothesis:**
> If a vanilla RNN with shared recurrent weight matrix $\mathbf{W}_{\text{rec}} \in \mathbb{R}^{h \times h}$ is unrolled for $T$ time steps, and the recurrent connections are reformulated as linear equality constraints $\mathbf{z}_t = \mathbf{W}_{\text{rec}} \sigma(\mathbf{z}_{t-1})$ with auxiliary variables $\mathbf{z}_t$ treated as independent neuron activations subject to cross-time coupling, then the resulting lifted convex program over $\{(\mathbf{w}_t, \mathbf{v}_t)\}_{t=1}^T$ achieves training loss equal to the SGD-trained RNN baseline $\pm 5\%$ on sequential MNIST, while guaranteeing global optimality via zero duality gap verified by complementary slackness conditions.

### Experimental Setup

**System:** Vanilla RNN with $h = 128$ hidden units, unrolled for $T \in \{50, 100, 200, 784\}$ time steps on sequential MNIST (28×28 images read pixel-by-pixel).

**Intervention:** Lifted convex program with $(T \cdot h)$-dimensional neuron variables and linear equality constraints $\mathbf{w}_t = \mathbf{w}_{t+1}$ enforcing weight sharing across time.

**Control condition:** Standard SGD-trained RNN with identical architecture ($h = 128$, same $T$).

### Variables

| Type | Variable | Values / Range |
|------|----------|---------------|
| Independent | Unrolling depth $T$ | $\{50, 100, 200, 784\}$ timesteps |
| Independent | Hidden size $h$ | $\{64, 128, 256\}$ neurons |
| Dependent | Training loss $L_{\text{convex}}$ | Cross-entropy (real-valued) |
| Dependent | Duality gap $\|P^* - D^*\| / P^*$ | Real-valued $\geq 0$ |
| Dependent | Solver iterations to convergence | Integer |
| Controlled | Initialization (SGD only) | Xavier uniform, 10 random seeds |
| Controlled | Learning rate (SGD only) | Grid search $\{10^{-4}, 10^{-3}, 10^{-2}\}$ |
| Controlled | Gradient clipping (SGD) | Threshold $= 1.0$ (standard for RNN training) |

### Baselines

1. **SGD-trained vanilla RNN (unclipped)**: Standard backpropagation through time (BPTT) without gradient clipping. **Why:** Tests whether convex formulation matches expressive power of nonconvex RNN in stable regime.

2. **SGD-trained vanilla RNN (clipped)**: BPTT with gradient norm clipping at threshold 1.0 (standard practice). **Why:** RNN training is notoriously unstable; clipping is the de facto baseline in practice.

3. **Ablation: independent per-timestep convex programs**: Solve $T$ separate two-layer convex programs (one per timestep) without weight-sharing constraints. **Why:** Isolates whether constraint coupling breaks strong duality or merely increases computational cost.

### Data Requirements

- **Dataset:** Sequential MNIST (permuted pixel order for temporal dependency), 60K training + 10K test images
- **Split:** Train/Val = 50K/10K (standard MNIST split)
- **Sequence encoding:** Flatten 28×28 image to 784-pixel sequence, feed one pixel per timestep
- **Compute:**
  - For $T = 784$, $h = 128$: lifted program has $\approx 10^5$ neurons (comparable to CRONOS-scale)
  - Convex solver: CVXPY with Mosek backend, estimated $\sim 10$ GPU-hours per $T = 784$ trial (extrapolated from Pilanci-Ergen two-layer scaling)
  - SGD baseline: $\sim 1$ GPU-hour for 100 epochs
- **Accessibility:** MNIST is public domain; CVXPY/Mosek free for academic use

### Evaluation Protocol

- **Primary metric:** Loss parity $L_{\text{convex}} / L_{\text{SGD-clipped}}$ (expect $\in [0.95, 1.05]$ if H2 holds)
- **Duality gap verification:** $|P^* - D^*| / P^* < 10^{-3}$ (strong duality threshold)
- **Secondary metrics:**
  - Test accuracy (generalization check)
  - Solver convergence: iterations to duality gap $< 10^{-3}$
  - Constraint violation: $\max_t \|\mathbf{w}_t - \mathbf{w}_{t+1}\|_2$ (should be $< 10^{-6}$ at optimum)
- **Significance test:** Wilcoxon signed-rank test (non-parametric) comparing convex vs. SGD loss distributions, $\alpha = 0.05$.
- **Runs:** 10 random initializations for SGD baseline; 5 convex solver runs with different constraint formulation orderings (to verify solver robustness).

### Expected Results

**If H2 is confirmed:**
- Duality gap $< 10^{-3}$ for all $T \in \{50, 100, 200, 784\}$, confirming strong duality holds despite weight sharing.
- Loss ratio $\in [0.95, 1.05]$ for $T \leq 200$; may degrade for $T = 784$ if solver hits iteration limit.
- Solver converges within 1000 iterations for $T \leq 100$.

**If H2 is rejected:**
- Duality gap $> 10^{-3}$, indicating constraint interaction breaks strong duality (Slatercondition fails).
- Or runtime scales as $O(T^3)$ (exponential in sequence length), making $T > 50$ intractable.

**Partial confirmation:**
- If strong duality holds for $T \leq 100$ but fails for $T = 784$, suggests depth-dependent breakdown (analogous to Wang et al.'s serial network duality gap for $L \geq 3$).

### Effort and Risk Assessment

- **Effort:** HIGH (4-6 weeks)
  - Week 1-2: Formulate lifted program with equality constraints in CVXPY; verify solver can handle $(T \cdot h)$-dimensional problem on toy data
  - Week 3-4: Run full experiments for $T \in \{50, 100\}$ (tractable regime)
  - Week 5-6: Attempt $T \in \{200, 784\}$; if intractable, report scaling threshold
- **Primary risk:** Constraint matrix becomes ill-conditioned, causing solver to fail or converge slowly.
  - **Mitigation:** Add Tikhonov regularization $\lambda \|\mathbf{w}_t\|_2^2$ to stabilize; if this breaks strong duality, report as negative result.
- **Secondary risk:** $T = 784$ may exceed available GPU memory (10^5 neurons × 10K samples ≈ 1B constraint coefficients).
  - **Mitigation:** Test $T = 784$ on downsampled MNIST (14×14 images, $T = 196$) as intermediate case.

---

## Experiment E3: Testing H3 — Width-Dependent Duality Gap Bound for Serial Deep Networks via Bidual Sandwiching

**Hypothesis:**
> If a standard serial $L$-layer ReLU network is trained with width $m$ neurons per layer, and the bidual construction of Wang et al. [WangErgenPilanci2023] is used to compute the dual lower bound $D^* = P^*_{\text{parallel}}$, then the duality gap $\Delta = P^*_{\text{serial}} - D^*$ is upper-bounded by $\Delta \leq (L-1) \cdot \exp(-(m - m^*)/(2m^*))$ where $m^* = (r+1)d$ is the Carathéodory bound, as measured by training a 3-layer network ($L=3$) on synthetic rank-2 data with varying width $m \in \{m^*, 2m^*, 5m^*, 10m^*\}$ and verifying the gap decays exponentially.

### Experimental Setup

**System:** 3-layer serial ReLU network ($L = 3$) trained on synthetic Gaussian data with controlled rank $r = 2$, input dimension $d = 10$.

**Intervention:** Vary network width $m \in \{m^*, 2m^*, 5m^*, 10m^*\}$ where $m^* = (r+1)d = 30$.

**Control condition:** Parallel 3-layer network with $K = 3$ branches (equal total width) to compute $P^*_{\text{parallel}} = D^*_{\text{serial}}$ (Wang et al. bidual construction).

### Variables

| Type | Variable | Values / Range |
|------|----------|---------------|
| Independent | Width $m$ (neurons per layer) | $\{30, 60, 150, 300\}$ ($= \{m^*, 2m^*, 5m^*, 10m^*\}$) |
| Independent | Network depth $L$ | $\{3, 4, 5\}$ layers |
| Independent | Data rank $r$ | $\{2, 5, 10\}$ |
| Dependent | Duality gap $\Delta = P^*_{\text{serial}} - D^*$ | Real-valued $\geq 0$ |
| Dependent | Exponential decay rate $B$ | Fitted parameter |
| Controlled | Data distribution | $\mathcal{N}(0, \mathbf{I})$ Gaussian |
| Controlled | Sample size $n$ | 1000 (ensures $n > m$ for all $m$) |
| Controlled | Solver precision | Duality gap tolerance $< 10^{-5}$ |

### Baselines

1. **Wang et al. bidual parallel network**: 3-layer parallel architecture with $K = 3$ branches, each with width $m/3$ (total width $m$). **Why:** Provides constructive lower bound $D^* = P^*_{\text{parallel}}$ per Wang et al. Theorem 4.

2. **Ablation: uniform data (rank $n$)**: Train on rank-$n$ Gaussian data (no low-rank structure) to verify gap bound only holds in low-rank regime.

3. **Ablation: deeper network ($L = 5$)**: Test whether gap bound coefficient $(L-1)$ tightens or loosens for deeper networks.

### Data Requirements

- **Dataset:** Synthetic rank-$r$ Gaussian: Generate $\mathbf{X} = \mathbf{U}\mathbf{V}^T$ where $\mathbf{U} \in \mathbb{R}^{n \times r} \sim \mathcal{N}(0, 1)$, $\mathbf{V} \in \mathbb{R}^{r \times d} \sim \mathcal{N}(0, 1)$
- **Split:** Train/Val = 800/200 (20% holdout for solver convergence validation)
- **Compute:**
  - Serial 3-layer: $O(d^3 m^3 n^{3(m+1)r})$ — for $r = 2$, $m = 30$, $n = 1000$: ~10 GPU-hours (extrapolated from Ergen-Pilanci 2021 scaling)
  - Parallel 3-layer: polynomial in $n, d, K$ (tractable via Wang et al. formulation)
- **Accessibility:** Fully synthetic (no external data dependency)

### Evaluation Protocol

- **Primary metric:** Fit exponential decay model $\Delta(m) = A \cdot \exp(-B(m - m^*))$ to observed gaps at $m \in \{m^*, 2m^*, 5m^*, 10m^*\}$.
  - **Hypothesis verification:** $B \geq 1/(2m^*) = 1/60$ and $R^2 > 0.9$ (goodness of fit).
- **Secondary metrics:**
  - Intrinsic data dimensionality via PCA (verify rank matches design)
  - Primal-dual objective difference: $|P^*_{\text{serial}} - \text{dual}_{\text{obj}}|$ (verify solver found optimum)
- **Significance test:** Bootstrap confidence interval for fitted $B$ parameter ($10^4$ resamples), verify $CI_{95\%}$ excludes zero.
- **Runs:** 10 different random data generations; report mean gap $\pm$ standard error.

### Expected Results

**If H3 is confirmed:**
- Gap decays exponentially: $\Delta(m^*) \gg \Delta(2m^*) > \Delta(5m^*) \approx \Delta(10m^*)$.
- Fitted decay rate $B \geq 1/(2m^*) = 1/60$ with $R^2 > 0.9$.
- Coefficient scales with depth: gap at $L = 5$ is $\approx (5-1)/(3-1) = 2\times$ larger than $L = 3$ at equal $m$.

**If H3 is rejected:**
- Gap does not decay exponentially (e.g., polynomial $\Delta(m) \propto 1/m$ or logarithmic $\propto 1/\log m$), indicating width-dependence is weaker than conjectured.
- Or fitted $B < 1/(2m^*)$, suggesting decay rate slower than predicted.

**Partial confirmation:**
- If bound holds for $r = 2$ but fails for $r = 10$, suggests rank-dependence not captured by simple $(L-1) \cdot \exp(\cdot)$ form.

### Effort and Risk Assessment

- **Effort:** MEDIUM (2-3 weeks)
  - Week 1: Implement serial and parallel 3-layer convex solvers; validate on toy data
  - Week 2: Run width sweep $m \in \{m^*, \ldots, 10m^*\}$ for $L = 3$, $r = 2$ baseline
  - Week 3: Ablation studies ($L \in \{4,5\}$, $r \in \{5, 10\}$, uniform data)
- **Primary risk:** Gap magnitude $\Delta$ may be smaller than solver numerical precision ($\approx 10^{-5}$), making exponential fit unstable.
  - **Mitigation:** Use higher-precision solver (e.g., CVXOPT with quad precision) or scale up problem size ($d = 100$, $r = 10$) to amplify gap.
- **Secondary risk:** Serial 3-layer solver may not converge to duality gap $< 10^{-5}$ due to constraint degeneracy.
  - **Mitigation:** Report "gap $\geq$ solver tolerance" as censored observation; fit exponential to uncensored subset only.

---

## Experiment E4: Testing H4 — Exact Adversarial Training via $\ell_\infty$-Constrained Hyperplane Arrangements

**Hypothesis:**
> If $\ell_\infty$-ball robustness constraints $\|\mathbf{x}' - \mathbf{x}\|_\infty \leq \epsilon$ are incorporated into the group-LASSO convex program for a parallel 3-layer network by expanding each training point $\mathbf{x}_i$ into a zonotope $\mathcal{Z}_i = \mathbf{x}_i + [-\epsilon, \epsilon]^d$, and requiring the learned function to satisfy $|f(\mathbf{x}) - y| \leq \tau$ for all $\mathbf{x} \in \mathcal{Z}_i$, then the resulting convex program yields a classifier with certified robust accuracy (PGD-40 attack) matching or exceeding IBP+CROWN bounds on MNIST $\epsilon = 0.3$, while guaranteeing global optimality via zero duality gap.

### Experimental Setup

**System:** Parallel 3-layer ReLU network with $K = 3$ branches, width $m = 256$ per branch, trained on MNIST with adversarial robustness constraints.

**Intervention:** Add $\ell_\infty$-zonotope constraints: for each sample $(\mathbf{x}_i, y_i)$, enumerate vertices of $\mathcal{Z}_i = \{\mathbf{x}_i + \boldsymbol{\delta} : \|\boldsymbol{\delta}\|_\infty \leq \epsilon\}$ (at most $2^d$ vertices for $d$-dimensional input; use vertex subsampling for MNIST $d = 784$).

**Control condition:** Parallel 3-layer network without robustness constraints (standard accuracy baseline).

### Variables

| Type | Variable | Values / Range |
|------|----------|---------------|
| Independent | Perturbation budget $\epsilon$ | $\{0.1, 0.2, 0.3\}$ (standard MNIST benchmarks) |
| Independent | Network depth $L$ | $\{2, 3\}$ layers (parallel architecture) |
| Dependent | Certified robust accuracy (PGD-40) | Percentage $\in [0, 100]$ |
| Dependent | Clean accuracy (unperturbed test) | Percentage $\in [0, 100]$ |
| Dependent | Duality gap $|P^* - D^*| / P^*$ | Real-valued $\geq 0$ |
| Controlled | Zonotope sampling budget | 1000 vertices per $\mathcal{Z}_i$ (vertex subsampling via adversarial direction prioritization) |
| Controlled | Attack iteration budget (PGD) | 40 iterations |

### Baselines

1. **IBP + CROWN (Interval Bound Propagation + CROWN)**: State-of-the-art certified robustness method using convex relaxations. Reported MNIST $\epsilon = 0.3$ certified accuracy $\approx 85\%$. **Why:** Gold-standard comparison for certified robustness; existing benchmark numbers.

2. **PGD-trained standard network**: Adversarially trained serial 3-layer network using PGD-40 adversarial training (non-convex). **Why:** Standard adversarial training baseline without optimality guarantees.

3. **Ablation: axis-aligned box constraints**: Replace $\ell_\infty$-zonotope with simpler axis-aligned bounding box $\prod_{j=1}^d [x_{i,j} - \epsilon, x_{i,j} + \epsilon]$ (over-approximation). **Why:** Isolates whether exact zonotope vertex enumeration is necessary or bounding box suffices.

### Data Requirements

- **Dataset:** MNIST, 28×28 grayscale images, 10 classes
- **Split:** Train/Val/Test = 50K/10K/10K (standard MNIST split)
- **Preprocessing:** Normalize pixel values to $[0, 1]$
- **Compute:**
  - Zonotope vertex enumeration: For $\epsilon = 0.3$, prioritize worst-case adversarial directions via gradient of loss; sample 1000 vertices per $\mathcal{Z}_i$
  - Convex solver: Wang et al. parallel network formulation with $K = 3$ branches + robustness constraints: estimated ~5 GPU-hours (3× two-layer baseline due to depth penalty)
  - Certification: PGD-40 attack on 10K test set: ~30 minutes on GPU
- **Accessibility:** MNIST public domain; IBP+CROWN code available (open-source)

### Evaluation Protocol

- **Primary metric:** Certified robust accuracy = fraction of test samples correctly classified under PGD-40 attack with $\epsilon = 0.3$.
  - **Success criterion:** $\geq$ IBP+CROWN baseline ($\approx 85\%$)
- **Secondary metrics:**
  - Clean accuracy $\geq 97\%$ (ensure robustness doesn't collapse solution)
  - Duality gap $< 10^{-3}$ (verify strong duality holds)
  - AutoAttack validation (stronger adversary than PGD-40)
- **Significance test:** McNemar's test comparing convex-optimal vs. IBP+CROWN on per-sample robustness, $\alpha = 0.05$.
- **Runs:** 5 random train/val splits; report mean certified accuracy $\pm$ standard error.

### Expected Results

**If H4 is confirmed:**
- Certified accuracy $\geq 85\%$ (matching IBP+CROWN) at $\epsilon = 0.3$.
- Duality gap $< 10^{-3}$ (confirming global optimality).
- Clean accuracy $\geq 97\%$ (no trivial collapse).

**If H4 is rejected:**
- Certified accuracy $< 85\%$, indicating zonotope constraints are too conservative (over-constrain function class) or under-specified (insufficient vertex sampling).
- Or duality gap $> 10^{-3}$, suggesting robustness constraints break strong duality for parallel networks.

**Partial confirmation:**
- If $L = 2$ achieves $\geq 85\%$ but $L = 3$ fails, suggests depth-dependent breakdown analogous to serial network duality gap.

### Effort and Risk Assessment

- **Effort:** MEDIUM (2-3 weeks)
  - Week 1: Implement zonotope vertex enumeration and constraint encoding in CVXPY
  - Week 2: Run experiments at $\epsilon \in \{0.1, 0.2, 0.3\}$ for $L = 2$
  - Week 3: Extend to $L = 3$, run AutoAttack validation
- **Primary risk:** Zonotope vertex enumeration is exponential in dimension ($2^{784}$ vertices for MNIST); even sampling 1000 vertices may miss critical adversarial directions.
  - **Mitigation:** Use adversarial direction prioritization: compute gradient of loss w.r.t. input, sample vertices along top-$k$ gradient directions.
- **Secondary risk:** Certified accuracy may be lower than IBP+CROWN due to expressive power gap (parallel vs. serial architecture).
  - **Mitigation:** Compare equal-width parallel vs. serial networks at $\epsilon = 0$ (no robustness) to isolate architecture effect from robustness method effect.

---

## Experiment E5: Testing H5 — Multi-Head Attention Convex Formulation via Parallel Branch Decomposition

**Hypothesis:**
> If a Vision Transformer (ViT) block with $H$ attention heads and residual connection $\mathbf{z}_{\text{out}} = \mathbf{z}_{\text{in}} + \text{MHA}(\mathbf{z}_{\text{in}})$ is reformulated as $H$ independent single-head convex programs (one per head) with a shared output constraint $\mathbf{z}_{\text{out}} = \mathbf{z}_{\text{in}} + \sum_{h=1}^H \mathbf{z}_h$, and each head's convex program is constructed via the attention transformation $\mathbf{z}_h = \text{Attention}(\mathbf{Q}_h, \mathbf{K}_h, \mathbf{V}_h)$ following Sahiner et al. [2205.08078], then the joint optimization over $H$ coupled programs with residual coupling yields training loss within 10\% of a standard AdamW-trained ViT-Tiny on CIFAR-10, as measured by cross-entropy loss, under sequential coordinate ascent optimization.

### Experimental Setup

**System:** Single ViT block with $H = 4$ attention heads, embedding dimension $d = 192$, trained on CIFAR-10 (32×32 RGB images tokenized into 16 patches of size 8×8).

**Intervention:** Decompose multi-head attention into $H = 4$ independent single-head convex programs, couple via residual constraint $\mathbf{z}_{\text{out}} = \mathbf{z}_{\text{in}} + \sum_{h=1}^H \mathbf{z}_h$.

**Control condition:** AdamW-trained ViT-Tiny (standard PyTorch implementation with $H = 4$ heads, same architecture).

### Variables

| Type | Variable | Values / Range |
|------|----------|---------------|
| Independent | Number of heads $H$ | $\{1, 2, 4, 8\}$ |
| Independent | Residual normalization | $\{\text{with LayerNorm}, \text{without}\}$ |
| Dependent | Training loss $L_{\text{convex}}$ | Cross-entropy (real-valued) |
| Dependent | Loss ratio $L_{\text{convex}} / L_{\text{AdamW}}$ | Real $\geq 0$ |
| Dependent | Duality gap $|P^* - D^*| / P^*$ | Real $\geq 0$ |
| Dependent | Coordinate ascent iterations to convergence | Integer |
| Controlled | Coordinate ascent learning rate | 0.001 (standard for ADMM-style coordinate descent) |
| Controlled | Convergence criterion | Objective change $< 10^{-4}$ between iterations |

### Baselines

1. **AdamW-trained ViT-Tiny**: Standard training with AdamW optimizer, learning rate 0.001, 100 epochs. **Why:** Defacto baseline for transformer training; establishes loss target $L_{\text{AdamW}}$.

2. **Sahiner et al. single-head convex attention** (no residual): Single attention head ($H = 1$) without residual connection. **Why:** Isolates whether multi-head coupling or residual coupling causes issues.

3. **Ablation: ADMM instead of coordinate ascent**: Use Alternating Direction Method of Multipliers (ADMM) with augmented Lagrangian to handle residual coupling constraints. **Why:** Tests whether coordinate ascent convergence is slow due to coupling; ADMM may accelerate.

### Data Requirements

- **Dataset:** CIFAR-10, 32×32 RGB images
- **Split:** Train/Val = 45K/5K (90/10 split of 50K training set)
- **Preprocessing:** Normalize to mean 0, std 1; patchify into 16 tokens of dimension $d = 192$
- **Compute:**
  - Single-head convex program: ~1 GPU-hour (based on Sahiner et al. reported runtimes)
  - $H = 4$ heads × 500 coordinate ascent iterations: ~2000 GPU-hours (if sequential); parallelizable across heads to ~500 GPU-hours
  - AdamW baseline: ~30 minutes for 100 epochs
- **Accessibility:** CIFAR-10 public domain; ViT-Tiny implementation in timm library

### Evaluation Protocol

- **Primary metric:** Loss ratio $L_{\text{convex}} / L_{\text{AdamW}} \leq 1.10$ (within 10% of AdamW baseline).
- **Secondary metrics:**
  - Duality gap $< 10^{-2}$ (moderate tolerance given coupling complexity)
  - Head diversity: correlation matrix of attention weights across heads (off-diagonal $< 0.5$ indicates diverse heads)
  - Test accuracy (generalization check)
- **Significance test:** Paired t-test comparing convex vs. AdamW loss on 10 random data orderings, $\alpha = 0.05$.
- **Runs:** 10 random initializations of coordinate ascent (different head ordering); report mean loss ratio $\pm$ std dev.

### Expected Results

**If H5 is confirmed:**
- Loss ratio $\in [1.0, 1.1]$ for $H \in \{1, 2, 4\}$.
- Duality gap $< 10^{-2}$ (or provable zero gap if coupling doesn't break strong duality).
- Coordinate ascent converges within 500 iterations.

**If H5 is rejected:**
- Loss ratio $> 1.10$, indicating multi-head convex formulation loses expressiveness vs. standard ViT.
- Or duality gap $> 10^{-2}$, suggesting residual coupling breaks convex structure.
- Or coordinate ascent fails to converge (oscillates or diverges).

**Partial confirmation:**
- If $H = 1$ succeeds but $H \geq 2$ fails, suggests multi-head coupling (not residual) is the issue.
- If "without LayerNorm" succeeds but "with LayerNorm" fails, indicates normalization interaction with convexity.

### Effort and Risk Assessment

- **Effort:** HIGH (4-6 weeks)
  - Week 1-2: Implement single-head convex attention following Sahiner et al.; validate on toy data
  - Week 3-4: Implement multi-head coupling and coordinate ascent solver
  - Week 5-6: Full CIFAR-10 experiments and ADMM ablation
- **Primary risk:** Coordinate ascent may converge very slowly (thousands of iterations) due to tight coupling between heads and residual.
  - **Mitigation:** If no convergence after 1000 iterations, terminate and report as partial failure; try ADMM as alternative solver.
- **Secondary risk:** Residual connection may break convexity of the coupled program (even if individual heads are convex).
  - **Mitigation:** Verify convexity analytically by checking Hessian of the Lagrangian; if non-convex, report as theoretical negative result.

---

## Experiment E6: Testing H6 — Quantization-Aware Convex Training via Mixed-Integer Group-LASSO Relaxation

**Hypothesis:**
> If integer weight constraints $\mathbf{w}_j \in \{-127, -126, \ldots, 127\}$ (INT8 quantization) are incorporated into the two-layer convex group-LASSO program via a rounding-based convex relaxation — where the continuous relaxation is solved, then weights are rounded to the nearest integer and the objective is re-evaluated — the resulting quantized network achieves test accuracy within 2\% of a post-training quantization (PTQ) baseline on CIFAR-10, while maintaining training loss within 5\% of the unquantized convex optimum, as measured by cross-entropy loss on a two-layer network with $m = 512$ neurons.

### Experimental Setup

**System:** Two-layer ReLU network with $m = 512$ neurons on CIFAR-10; weights quantized to INT8 $= \{-127, \ldots, 127\}$.

**Intervention:** Solve continuous convex group-LASSO, then round weights $\mathbf{w}_j^* \to \text{round}(\mathbf{w}_j^*)$ to nearest INT8 value, re-evaluate objective.

**Control condition:** Post-training quantization (PTQ) applied to an AdamW-trained two-layer network (train with float32, then quantize to INT8).

### Variables

| Type | Variable | Values / Range |
|------|----------|---------------|
| Independent | Quantization bitwidth | $\{\text{INT4}, \text{INT8}\}$ (4-bit = 16 levels, 8-bit = 256 levels) |
| Independent | Quantization scheme | $\{\text{symmetric}, \text{asymmetric}\}$ |
| Dependent | Test accuracy $\text{Acc}_{\text{convex-INT8}}$ | Percentage $\in [0, 100]$ |
| Dependent | Accuracy gap vs. PTQ | $\text{Acc}_{\text{PTQ}} - \text{Acc}_{\text{convex-INT8}}$ |
| Dependent | Loss ratio $L_{\text{INT8}} / L_{\text{continuous}}^*$ | Real $\geq 1$ |
| Dependent | KKT residual of rounded solution | $\max_j \|\nabla L(\mathbf{w}^{\text{round}}) + \lambda \partial \|\mathbf{w}_j\|_2\|$ |
| Controlled | Continuous convex optimum $L_{\text{continuous}}^*$ | Computed via standard group-LASSO solver |
| Controlled | Calibration data (for PTQ) | 1000 samples from training set |

### Baselines

1. **Post-Training Quantization (PTQ)**: Train float32 network with AdamW, quantize weights to INT8 using calibration set (standard PyTorch quantization workflow). **Why:** Industry-standard quantization method.

2. **Quantization-Aware Training (QAT) - nonconvex**: Train with fake quantization (simulate INT8 during training via straight-through estimator). **Why:** Better baseline than PTQ, but lacks optimality guarantees.

3. **Ablation: uniform quantization grid**: Use INT8 values as $\{-127, \ldots, 127\}$ uniformly spaced; vs. learned quantization grid (optimize grid points jointly with rounding). **Why:** Tests whether fixed grid is sufficient or adaptive grid needed.

### Data Requirements

- **Dataset:** CIFAR-10
- **Split:** Train/Val/Calibration/Test = 40K/5K/1K/4K
- **Compute:**
  - Continuous convex solver: ~1 GPU-hour (two-layer network, $m = 512$)
  - Rounding and re-evaluation: negligible (<1 minute)
  - PTQ baseline: ~30 minutes for training + 1 minute for quantization
- **Accessibility:** CIFAR-10 public domain; PyTorch quantization API available

### Evaluation Protocol

- **Primary metric:** Accuracy gap $\Delta_{\text{acc}} = \text{Acc}_{\text{PTQ}} - \text{Acc}_{\text{convex-INT8}} \leq 2\%$ (e.g., if PTQ = 88%, convex ≥ 86%).
- **Secondary metrics:**
  - Loss ratio $L_{\text{INT8}} / L_{\text{continuous}}^* \leq 1.05$ (rounding degradation bounded)
  - KKT residual $< 10^{-2}$ (optimality certificate for rounded solution)
  - Weight histogram: distribution of quantized values (detect clustering or anomalies)
- **Significance test:** Paired t-test on accuracy difference across 10 random calibration sets, $\alpha = 0.05$.
- **Runs:** 10 random calibration sets for PTQ baseline; 5 random initializations of convex solver (to verify solver robustness).

### Expected Results

**If H6 is confirmed:**
- Accuracy gap $\leq 2\%$ for INT8 symmetric quantization.
- Loss ratio $\leq 1.05$ (rounding penalty is small due to over-parameterization $m = 512 > m^*$).
- KKT residual $< 10^{-2}$ (rounded solution is near-optimal for discrete problem).

**If H6 is rejected:**
- Accuracy gap $> 2\%$, indicating continuous-relaxation-then-round heuristic loses critical information.
- Or loss ratio $> 1.05$, suggesting rounding degradation is larger than continuous solution's margin.

**Partial confirmation:**
- If INT8 succeeds but INT4 fails, indicates bitwidth threshold below which relaxation breaks down.
- If symmetric fails but asymmetric succeeds, suggests quantization scheme choice matters more than convex method.

### Effort and Risk Assessment

- **Effort:** LOW (1-2 weeks)
  - Week 1: Implement rounding post-processing and KKT residual computation; run INT8 experiments
  - Week 2: Ablation studies (INT4, asymmetric, learned grid)
- **Primary risk:** Rounding may violate constraints of the convex program (e.g., group-LASSO structure), causing large loss increase.
  - **Mitigation:** Project rounded solution back onto feasible set (closest point in $\ell_2$ norm); report projection cost.
- **Secondary risk:** PTQ baseline may use advanced calibration (e.g., Kullback-Leibler divergence minimization) that simple rounding cannot match.
  - **Mitigation:** Compare both simple rounding and KL-calibration rounding; report both as baselines.

---

## DOE Summary Table

| Hypothesis | Independent Variables | Primary Dependent Variable | Primary Baseline | Expected Effort |
|------------|----------------------|----------------------------|------------------|-----------------|
| H1 (Full-rank) | Sampling budget $B_\ell \in \{10^3, \ldots, 10^6\}$, depth $L \in \{2,3\}$ | Approximation ratio $L_{\text{approx}} / L^*$ | CRONOS runtime baseline | MEDIUM (2-3 weeks) |
| H2 (Recurrent) | Unrolling depth $T \in \{50, \ldots, 784\}$, hidden size $h \in \{64, 128, 256\}$ | Duality gap $\|P^* - D^*\| / P^*$ | SGD-trained RNN | HIGH (4-6 weeks) |
| H3 (Duality gap bound) | Width $m \in \{m^*, \ldots, 10m^*\}$, depth $L \in \{3, 4, 5\}$, rank $r \in \{2, 5, 10\}$ | Duality gap $\Delta = P^*_{\text{serial}} - D^*$ | Wang et al. bidual parallel network | MEDIUM (2-3 weeks) |
| H4 (Adversarial) | Perturbation $\epsilon \in \{0.1, 0.2, 0.3\}$, depth $L \in \{2, 3\}$ | Certified robust accuracy (PGD-40) | IBP+CROWN baseline | MEDIUM (2-3 weeks) |
| H5 (Multi-head attention) | Heads $H \in \{1, 2, 4, 8\}$, LayerNorm $\{\text{yes}, \text{no}\}$ | Loss ratio $L_{\text{convex}} / L_{\text{AdamW}}$ | AdamW-trained ViT-Tiny | HIGH (4-6 weeks) |
| H6 (Quantization) | Bitwidth $\{\text{INT4}, \text{INT8}\}$, scheme $\{\text{sym}, \text{asym}\}$ | Accuracy gap vs. PTQ | Post-training quantization (PTQ) | LOW (1-2 weeks) |

---

## Reproducibility Checklist

To enable independent replication, all experiments will adhere to the following:

### Software and Environment

- **Python version:** 3.10
- **Key dependencies:**
  - CVXPY 1.4 (convex optimization modeling)
  - Mosek 10.0 (commercial solver, free academic license)
  - PyTorch 2.1 (for SGD/AdamW baselines and data loading)
  - NumPy 1.24, SciPy 1.11
  - scikit-learn 1.3 (for PCA, train/val splitting)
- **Hardware:**
  - GPU: NVIDIA A100 (40GB) or equivalent
  - CPU: 32 cores minimum (for parallel solvers)
  - RAM: 64 GB minimum
- **Containerization:** Docker image with frozen dependencies (Dockerfile provided in repository)

### Random Seeds and Initialization

- **Data splits:** Use `np.random.seed(42)` for train/val/test splits; report split indices
- **Solver initialization:** CVXPY warm-start from zero (default); for coordinate ascent (H5), initialize heads randomly with seed sequence `[100, 101, 102, ...]`
- **SGD/AdamW initialization:** PyTorch default (Kaiming uniform for weights, zeros for biases); seed `torch.manual_seed(42 + trial_idx)` where `trial_idx ∈ [0, 9]`

### Dataset Versioning

- **CIFAR-10:** Use torchvision.datasets.CIFAR10 version 1.0 (canonical version)
- **MNIST:** Use torchvision.datasets.MNIST version 1.0
- **Sequential MNIST:** Apply deterministic pixel permutation (seed 123) to standard MNIST
- **Synthetic data:** Provide data generation script with seeds; archive generated datasets

### Hyperparameters

| Experiment | Hyperparameter | Value(s) | Justification |
|------------|---------------|----------|---------------|
| All | Duality gap tolerance | $10^{-4}$ (H1, H6), $10^{-3}$ (H2, H4), $10^{-5}$ (H3), $10^{-2}$ (H5) | Tighter for theoretical bounds (H3); relaxed for coupled problems (H5) |
| H1 | Sampling budget $C$ | $\{1, 10, 100, 1000\}$ | Logarithmic sweep to identify scaling threshold |
| H2 | SGD learning rate | Grid search $\{10^{-4}, 10^{-3}, 10^{-2}\}$ | Standard RNN learning rate range |
| H2 | Gradient clipping threshold | 1.0 | Standard practice for RNN training |
| H4 | PGD attack iterations | 40 | Community standard for certified robustness evaluation |
| H4 | Zonotope vertex budget | 1000 per sample | Balance between accuracy and tractability |
| H5 | Coordinate ascent LR | 0.001 | Tuned on toy problem; sensitive parameter (report tuning curve) |
| H6 | Quantization calibration samples | 1000 | PyTorch default for PTQ |

### Solver Configuration

- **CVXPY solver:** Mosek for all experiments (most reliable for group-LASSO)
- **Solver parameters:**
  - `mosek_params = {'MSK_DPAR_INTPNT_CO_TOL_DFEAS': 1e-8}` (dual feasibility tolerance)
  - `mosek_params = {'MSK_IPAR_INTPNT_MAX_ITERATIONS': 10000}` (iteration limit)
- **Warm-start:** Not used (cold start from zero) unless ablation explicitly tests warm-start effect
- **Parallel solve:** Use Mosek's multi-threading (set `MSK_IPAR_NUM_THREADS = 16`)

### Evaluation Metrics Computation

- **Approximation ratio (H1):** $\rho = L_{\text{approx}} / L^*_{\text{rank-50}}$ where $L^*_{\text{rank-50}}$ is exact optimum on PCA-projected data; report extrapolation uncertainty estimate
- **Duality gap (H2, H3, H4, H5):** Complement slackness error $\max_j |\mathbf{w}_j^T (\nabla L + \lambda \mathbf{v}_j)|$ where $\mathbf{v}_j \in \partial \|\mathbf{w}_j\|_2$
- **Certified accuracy (H4):** Run PGD-40 with 10 random initializations per sample; report worst-case accuracy over initializations
- **KKT residual (H6):** $\|\nabla L(\mathbf{w}^{\text{round}}) + \lambda \sum_j \mathbf{v}_j\|_2$ where $\mathbf{v}_j \in \partial \|\mathbf{w}_j\|_2$

### Code and Data Availability

- **Code repository:** GitHub (MIT license), with branch per experiment (e.g., `exp-h1-full-rank`)
- **Data:** CIFAR-10/MNIST automatically downloaded; synthetic data generation scripts in `data/` directory
- **Pretrained baselines:** Upload SGD/AdamW checkpoints to Hugging Face model hub for reproducibility
- **Experiment logs:** Weights & Biases (wandb) project with hyperparameters, metrics, and stdout logs

### Reporting Standards

- **Negative results:** Report all experiments where hypothesis is rejected; do not selectively publish only confirmations
- **Numerical precision:** Report all metrics to 2 decimal places (e.g., accuracy = 87.43%); loss values to 4 significant figures
- **Confidence intervals:** Bootstrap 95% CI for all primary metrics (10K resamples)
- **Runtime:** Report wall-clock time + GPU-hours + solver iterations; use `time.perf_counter()` for precise timing

---

## Risk Assessment

### Per-Hypothesis Risk Table

| Hypothesis | Primary Risk | Probability | Impact | Mitigation Strategy |
|------------|-------------|-------------|--------|---------------------|
| H1 | Zonotope sampling overhead dominates; $B_\ell = 10^5$ intractable | MEDIUM | HIGH (blocks full experiment) | Pilot with $B_\ell = 10^3$ on $L=2$; pivot to axis-aligned boxes if needed |
| H2 | Constraint matrix ill-conditioned; solver fails for $T > 100$ | HIGH | HIGH (core hypothesis untestable) | Add Tikhonov regularization; test on downsampled MNIST ($T = 196$) first |
| H3 | Duality gap magnitude below solver precision ($< 10^{-5}$) | MEDIUM | MEDIUM (fit unstable) | Use quad-precision solver or scale up problem size ($d = 100$, $r = 10$) |
| H4 | Vertex enumeration exponential; 1000 vertices insufficient | MEDIUM | MEDIUM (certification loose) | Prioritize adversarial directions via loss gradient |
| H5 | Coordinate ascent diverges or converges very slowly ($> 1000$ iter) | HIGH | HIGH (intractable runtime) | Terminate after 1000 iter; try ADMM as alternative; report as partial negative |
| H6 | Rounding violates convex program constraints; loss increases $> 5\%$ | LOW | MEDIUM (hypothesis rejected) | Project rounded solution back onto feasible set; report projection cost |

### Cross-Experiment Dependencies

- **H3 depends on H1 (weak):** If H1 shows zonotope sampling is infeasible even for $L = 2$, this undermines confidence in H3's ability to handle $L = 3$ serial networks with nested arrangements. However, H3 uses exact solver on rank-2 data (not sampling), so dependency is advisory only.
  
- **H5 depends on H4 (weak):** Both use parallel network formulations; if H4 discovers parallel architecture with constraints breaks strong duality, this raises risk for H5. Mitigation: prioritize H4 before H5.

### Computational Budget Allocation

Total estimated GPU-hours: 
- H1: 100 GPU-hours (20 trials × 5 hours)
- H2: 200 GPU-hours (intractable regime exploration)
- H3: 50 GPU-hours (synthetic data fast)
- H4: 100 GPU-hours (certification overhead)
- H5: 500 GPU-hours (coordinate ascent iterations)
- H6: 20 GPU-hours (two-layer only)

**Total: ~970 GPU-hours (~40 GPU-days on single A100)**

Recommended execution order (risk-adjusted):
1. **H6** (1 week, LOW risk) — Validate experimental infrastructure
2. **H3** (2 weeks, MEDIUM risk) — Theoretical result, smaller scale
3. **H1** (2-3 weeks, MEDIUM risk) — Pilot with small $B_\ell$ before scaling
4. **H4** (2-3 weeks, MEDIUM risk) — Test parallel architecture robustness before H5
5. **H2** (4-6 weeks, HIGH risk) — Staged: test $T \in \{50, 100\}$ before attempting 784
6. **H5** (4-6 weeks, HIGH risk) — Most computationally intensive; run last to incorporate lessons from H4

---

## Alignment with Methodological Precedents

All experimental designs build on established methodologies from the literature:

### From Pilanci & Ergen (2020) [sources/user-2002.10553v2]:
- **Group-LASSO formulation** for two-layer networks (baseline for H1, H6)
- **Hyperplane arrangement enumeration** complexity $O(n^r)$ (motivates H1's sampling approach)
- **CVXPY + Mosek solver stack** (adopted for all experiments)

### From Wang, Ergen & Pilanci (2023) [sources/user-2110.06482v3]:
- **Bidual construction** $D^*_{\text{serial}} = P^*_{\text{parallel}}$ (core method for H3)
- **Parallel network zero duality gap** (enables H4 and H5 parallel formulations)

### From CRONOS (2024) [sources/user-cronos]:
- **CIFAR-10 and ImageNet benchmarking** (standard datasets for H1, H4, H6)
- **Runtime baselines:** CRONOS reports $\sim 3$ seconds/epoch on CIFAR-10 (H1's $10\times$ budget = 30 seconds)
- **AdamW baseline comparisons** (adopted for H5 ViT experiment)
- **Alternating minimization (CRONOS-AM)** approach (informs H5's coordinate ascent strategy)

### From Sahiner et al. (2023) [arxiv-2205.08078]:
- **Single-head attention convex formulation** (foundation for H5 multi-head extension)
- **ViT-Tiny on CIFAR-10** experimental protocol (directly adopted for H5)

### From Ergen & Pilanci (2021) [sources/user-2110.05518v2]:
- **Three-layer network complexity** $O(d^3 m^3 n^{3(m+1)r})$ (informs H3 computational budget)
- **Duality gap existence for serial deep networks** (motivation for H3)

### From Mishkin et al. (2022) [cited in arxiv-2205.08078]:
- **Adversarial robustness constraints** in two-layer convex programs (extended to parallel 3-layer in H4)
- **PGD-40 attack protocol** (adopted as certification standard for H4)

**No experiment deviates from established protocols without justification.** Novel contributions (hierarchical zonotope sampling in H1, RNN weight-sharing reformulation in H2, exponential gap bound in H3) are framed as extensions of proven baseline methods, minimizing risk of methodological errors.
