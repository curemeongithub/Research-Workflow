---
phase: 7
status: complete
timestamp: 2026-04-06T00:00:00Z
depends_on: [synthesis/hypotheses.md, analysis/literature-map.md, analysis/gap-analysis.md]
token_estimate: 5800
source_lookups_used: 3
---

# Experimental Methodology: Dual Convex Optimization in ReLU Neural Networks

## Methodology Summary

This document specifies a seven-experiment research program testing the hypotheses
developed in Phase 6. Three experiments are primarily **theoretical** (proof-oriented):
E1 (zero-gap singular-value condition for rank-1 three-layer ReLU), E2 (RIP extension
of the $O(\sqrt{\log n})$ bound), and E6 (self-concordance extension to logistic loss).
Two experiments are **numerical / small-scale empirical**: E3 (CRONOS-AM Lyapunov
descent), E5 (fixed-point BN convex equivalence). Two experiments are **medium-scale
empirical benchmarks**: E4 (generalization bound from Carathéodory complexity) and E7
(CIFAR-10 NTK vs. convex duality mechanistic probe). The primary solver throughout is
CVXPY (small instances) / CRONOS-JAX (large instances); PyTorch is reserved for the
non-convex baselines and CIFAR-10 runs. All experiments are designed to be runnable
on a single modern GPU (RTX-4090 or A100) or, for the small-scale proofs-by-enumeration,
on CPU alone.

---

## E1: Testing H1 — Zero-Gap Singular-Value Condition for Rank-1 Three-Layer ReLU

**Hypothesis:** For a rank-1 data matrix $X = \mathbf{x}\mathbf{y}^T$ with $L=3$ standard
ReLU and squared-loss weight decay, the duality gap is zero *if and only if* the
post-first-ReLU effective data matrix $\widetilde{X} = D_1 X$ satisfies an
equal-singular-values condition on the output-relevant subspace.

### Experimental Design

**Type:** Theoretical proof + exhaustive numerical verification  
**Primary method:** Exact primal-dual computation via CVXPY interior-point solver over
all hyperplane arrangement patterns, supplemented by a closed-form derivation of the
duality-gap formula for rank-1 data.

### Variables

| Variable | Type | Values / Range |
|----------|------|----------------|
| $n$ (sample count) | Independent | $\{10, 15, 20, 30\}$ |
| $d$ (feature dim) | Independent | $\{3, 5, 8\}$ |
| Singular value deviation $\Delta\sigma(\widetilde{X})$ | Independent | Continuous, controlled by data perturbation |
| Duality gap $p^* - d^*$ | Dependent | $\geq 0$ (measured via CVXPY) |
| Equal-singular-values condition satisfied | Dependent | Boolean indicator |
| Regularization $\beta$ | Control | $\{0.01, 0.1, 1.0\}$ |
| Data rank | Control | Fixed at 1 (rank-1, $X = \mathbf{x}\mathbf{y}^T$) |
| Network depth | Control | Fixed at $L=3$ |

### Baselines

- **Wang, Ergen & Pilanci (2023), deep linear case:** The gap formula $p^* - d^* > 0$ iff
  singular values of $X^\dagger Y$ are unequal is the direct analogue; any rank-1 ReLU
  result must reduce to this for identity activations.
- **Pilanci & Ergen (2020), $L=2$ benchmark:** The two-layer case always has zero gap
  (Table 1 in [Wang&Ergen&Pilanci2023]); the rank-1 $L=3$ formula must preserve this
  when the second ReLU layer is ablated.
- **Ablation — random data (no equal-SV constraint):** Random rank-1 Gaussian data
  matrices that generically violate the equal-singular-values condition; the gap should
  be non-zero.

### Success Criteria

- **Confirmation:** For all $(n, d, \beta)$ combinations, duality gap = 0 $\Leftrightarrow$ equal-SV
  condition on $\widetilde{X}$ holds, with zero exceptions across $\geq 200$ random rank-1
  instances.
- **Falsification:** Any single rank-1, $L=3$ instance where gap = 0 despite unequal SVs,
  or gap > 0 despite equal SVs, constitutes a counterexample.

### Reproducibility Checklist

- [ ] **Dataset(s):** Synthetic rank-1 random Gaussian matrices; $n \leq 30$, $d \leq 8$.
      No external datasets required.
- [ ] **Code framework:** CVXPY (interior-point, SCS backend) for exact primal-dual;
      NumPy for arrangement enumeration. Python 3.10+.
- [ ] **Hardware:** CPU sufficient; total runtime < 2 hours for full enumeration grid.
- [ ] **Random seeds:** 50 random seeds per $(n, d, \beta)$ cell; fixed with `np.random.seed(i)`.
- [ ] **Expected runtime:** ~30 min CPU for $n \leq 20$; ~2 h CPU for $n = 30$.

### Proof Strategy

The derivation follows five steps, mirroring [Wang&Ergen&Pilanci2023]'s deep linear proof
but adapted for the rank-1 ReLU interaction:

1. **Rescaling reduction:** Express the rank-1 primal as $\min_{\mathbf{w}} \frac{1}{2}\| \sigma(X\mathbf{w}) - \mathbf{y}\|^2 + \frac{\beta}{2}\|\mathbf{w}\|^2$ (three-layer telescoping).
2. **Dualization:** Derive the semi-infinite dual with respect to the output layer weights; the dual variable is $\nu \in \mathbb{R}^n$.
3. **Arrangement reduction:** For rank-1 $X$, the number of distinct arrangements $D_1$ is at most $n$ (rather than $O((n/d)^d)$ for full rank); enumerate them exactly.
4. **Gap formula derivation:** Compute $p^* - d^*$ as a function of the singular values of $D_1 X$; identify when this quantity is zero.
5. **Criterion extraction:** Setting the gap formula to zero yields the equal-SV condition on $\widetilde{X} = D_1 X$, establishing the biconditional.

Numerical experiments serve as **proof validation**: they confirm the formula holds before
the symbolic derivation is complete, and they detect edge cases (degenerate arrangements,
zero singular values) that the proof must handle.

### Methodological Precedents from Literature

[Wang&Ergen&Pilanci2023] derives the exact duality gap for deep linear networks using the
Schatten-$2/L$ quasi-norm formula (Theorem 1), establishing the equal-singular-values
criterion for the linear case — this is the direct template for H1's derivation.
[Pilanci&Ergen2020] proves strong duality for $L=2$ via Carathéodory's theorem (Theorem 1,
proof in Appendix A.1); the rank-1 Carathéodory bound $m^* \leq n+1$ is the starting point
for the bi-dual attainment step in H1's proof.

---

## E2: Testing H2 — $O(\sqrt{\log n})$ Approximation Extends to RIP-Satisfying Data

**Hypothesis:** The $O(\sqrt{\log n})$ relative optimality bound of [Kim&Pilanci2024]
extends from Gaussian i.i.d. data to any data matrix satisfying $(s, \delta)$-RIP on the
hyperplane arrangement feature map with $\delta < 1/2$.

### Experimental Design

**Type:** Theoretical derivation + numerical scaling experiment  
**Primary method:** Extend Gordon's comparison argument in [Kim&Pilanci2024] Lemma 21 to
RIP matrices; validate empirically by measuring relative optimality gap on Bernoulli$(\pm 1)$
data matrices (sub-Gaussian, satisfies RIP with high probability for $d = O(s \log n)$).

### Variables

| Variable | Type | Values / Range |
|----------|------|----------------|
| $n$ (sample count) | Independent | $\{50, 100, 200, 500, 1000\}$ |
| Data distribution | Independent | Gaussian (baseline) vs. Bernoulli$(\pm 1)$ (RIP) |
| Relaxation width $m$ | Independent | $\{c\log n : c \in \{1, 2, 4\}\}$ |
| Relative optimality gap $(\tilde{p}^* - p^*)/p^*$ | Dependent | $\geq 0$ (measured) |
| RIP parameter $\delta$ | Control | Estimated via restricted eigenvalue condition; kept $< 1/2$ |
| Feature dimension $d$ | Control | $d = \lfloor 0.8 n \rfloor$ (so $n \approx d$, matching A1 regime) |

### Baselines

- **Gaussian data + [Kim&Pilanci2024] Theorem 2.1:** The proved $O(\sqrt{\log n})$ bound;
  relative gap plotted as reference.
- **RIP data + full convex reformulation ($m = $ all arrangements):** The $p^*$ reference
  against which $\tilde{p}^*$ is measured; computed via CVXPY for $n \leq 100$.
- **Ablation — non-RIP data (correlated features, $\delta > 1/2$):** Should break the
  $O(\sqrt{\log n})$ scaling, confirming that RIP is load-bearing.

### Success Criteria

- **Confirmation:** Log-log regression of relative gap vs. $n$ has slope $\leq 0.6$ (consistent
  with $O(\sqrt{\log n})$) for Bernoulli data, matching the Gaussian baseline slope within
  a $2\times$ constant; $R^2 > 0.85$ for the fit.
- **Falsification:** Slope significantly exceeds 0.5 (e.g., $> 0.8$) for Bernoulli data while
  Gaussian data achieves 0.5, indicating the RIP extension fails.

### Reproducibility Checklist

- [ ] **Dataset(s):** Synthetic Bernoulli$(\pm 1)$ random matrices, $n \leq 1000$, $d \leq 800$.
      RIP verification: restricted eigenvalue condition via [numpy.linalg.eigh] on subsampled
      feature-map Gram matrix.
- [ ] **Code framework:** CVXPY (SCS backend) for full reformulation at $n \leq 100$; CRONOS-JAX
      for width-$m$ relaxation at $n > 100$.
- [ ] **Hardware:** GPU (RTX-4090 or A100) for $n > 200$; CPU sufficient for $n \leq 100$.
- [ ] **Random seeds:** 20 seeds per $(n, m, \text{distribution})$ cell; all seeds fixed and logged.
- [ ] **Expected runtime:** ~4 h GPU for the full grid; ~1 h CPU for $n \leq 100$ subset.

### Proof Strategy

The theoretical derivation parallels [Kim&Pilanci2024] Section 4 with three modifications:

1. **Replace Gaussian assumption (A1) with RIP:** Identify where Gaussianity enters the proof
   (Steps 2–3 of Theorem 2.1's proof: bounding $\lambda_{\min}(\mathcal{M})$ and applying
   Gordon's comparison). The RIP condition directly controls $\lambda_{\min}(\Phi^T\Phi)$ for
   the arrangement feature map $\Phi$, which is the quantity Gordon's inequality needs.
2. **Cone sharpness bound for RIP matrices:** RIP with parameter $\delta < 1/2$ implies
   $\lambda_{\min}(\mathcal{M}) \geq 1 - \delta > 1/2$; substitute this into Lemma 21 to
   obtain the same $O(\sqrt{\log n})$ upper bound with a modified constant $C(\delta)$.
3. **Mendelson's comparison as an alternative route:** If Gordon's inequality does not extend
   cleanly, Theorem 3 in Mendelson (2007) applies to sub-Gaussian processes and yields the
   same $O(\sqrt{\log n})$ rate for any sub-Gaussian distribution. Since Bernoulli$(\pm 1)$
   is sub-Gaussian with parameter 1, this is a fallback route.

Empirical experiments serve as both a consistency check and as a practical demonstration that
the extended bound is tight for natural RIP distributions.

### Methodological Precedents from Literature

[Kim&Pilanci2024] Theorem 2.1 is the direct template; the proof of Lemma 21 in that paper
(Gordon's comparison on the cone sharpness constant) is the exact step to modify.
The RIP extension is explicitly suggested as future work on p. 62 of arxiv-2402.03625:
"a connection to restricted isometry property could be a key to extending the result to
different distributions."

---

## E3: Testing H3 — CRONOS-AM Satisfies Monotone Lyapunov Descent Under Bounded Step Size

**Hypothesis:** When CRONOS-AM's early-layer step size satisfies
$\eta_t \leq \varepsilon / \|\nabla \mathcal{L}_t\|$, the convex sub-problem's optimal
value decreases monotonically across alternating minimization iterations.

### Experimental Design

**Type:** Numerical empirical experiment  
**Primary method:** Implement the bounded step-size variant of CRONOS-AM on UCI regression
benchmarks and compare convex sub-problem optimal value traces against the unbounded baseline.

### Variables

| Variable | Type | Values / Range |
|----------|------|----------------|
| Step-size rule | Independent | Bounded ($\eta_t \leq \varepsilon/\|\nabla\mathcal{L}_t\|$) vs. DAdapted-Adam default |
| Tolerance $\varepsilon$ | Independent | $\{0.01, 0.1, 0.5\}$ |
| Convex sub-problem optimal value $f_t^*$ at iteration $t$ | Dependent | Logged per AM iteration |
| Number of iterations to convergence | Dependent | Counted |
| Final training loss | Dependent | Scalar |
| Dataset | Control | UCI Concrete, Energy, Wine (as in [Feng&Frangella&Pilanci2023] Table 2) |
| Network depth | Control | $L = 3$ (two convex layers + one Adam layer) |

### Baselines

- **Default CRONOS-AM (DAdapted-Adam, no step-size bound):** From [Feng&Frangella&Pilanci2023]
  Table 2; establishes the baseline training loss and convergence curve.
- **Fixed small step size (hand-tuned):** Sets $\eta_t = 10^{-4}$ (constant), the
  over-conservative bound; verifies monotone descent is achievable but at slow convergence.
- **Ablation — $\varepsilon = \infty$ (no constraint):** Recovers the default CRONOS-AM,
  confirming the two code paths agree when unconstrained.

### Success Criteria

- **Lyapunov confirmation:** Across all 3 UCI datasets and all 3 $\varepsilon$ values, the
  sequence $f_t^*$ is non-increasing in $\geq 90\%$ of iterations (allowing discrete solver
  noise of $< 10^{-6}$ relative to $f_t^*$).
- **Falsification:** A single dataset / $\varepsilon$ combination where $f_t^*$ increases
  across $> 3$ consecutive iterations (net increase $> 0.1\%$ relative to $f_t^*$) while
  the bounded step-size rule is satisfied would falsify Lyapunov monotonicity.
- **Vacuity check:** If the bounded-rule step sizes are smaller than $10^{-6}$ at initialization,
  the hypothesis is vacuous; $\varepsilon$ is then too small and the experiment should be rerun
  with larger $\varepsilon$.

### Reproducibility Checklist

- [ ] **Dataset(s):** UCI Concrete ($n=1030$), Energy ($n=768$), Wine ($n=4898$). All public
      downloads from UCI ML Repository.
- [ ] **Code framework:** CRONOS-JAX (JAX + JIT, as in [Feng&Frangella&Pilanci2023]) with
      the bounded step-size modification in the DAdapted-Adam update rule.
- [ ] **Hardware:** Single GPU (RTX-4090 or A100); CPU fallback for $n < 1000$.
- [ ] **Random seeds:** 5 seeds per (dataset, $\varepsilon$) cell; all seeds fixed.
- [ ] **Expected runtime:** ~2 h GPU for the full 3×3 grid (3 datasets × 3 $\varepsilon$ values)
      × 5 seeds.

### Methodological Precedents from Literature

[Feng&Frangella&Pilanci2023] Table 2 uses UCI Concrete, Energy, and Wine as standard regression
benchmarks; the exact experimental setup (network depth, training epochs, evaluation metric)
is reproduced and extended with the step-size modification. The Lyapunov descent argument for
two-block alternating minimization follows the template of Xu & Yin (2013) "A Block Coordinate
Descent Method for Regularized Multiconvex Optimization," which the CRONOS-AM convergence
analysis should cite as its theoretical scaffold.

---

## E4: Testing H4 — Generalization Bound from Carathéodory Complexity $k^*$

**Hypothesis:** Test error is bounded by $O(\sqrt{k^*/n})$ where $k^* \leq n+1$ is the
Carathéodory dual support size; the bound tightens as $k^*/n$ decreases.

### Experimental Design

**Type:** Empirical benchmark — synthetic and semi-real data  
**Primary method:** Train two-layer ReLU networks via the exact convex reformulation (CVXPY)
on synthetic datasets of varying rank, regularization, and size; extract $k^*$ from the dual
solution support; compare $\sqrt{k^*/n}$ against empirical test error across settings.

### Variables

| Variable | Type | Values / Range |
|----------|------|----------------|
| $n$ (training size) | Independent | $\{50, 100, 200, 500\}$ |
| Data rank $r$ | Independent | $\{1, 3, 5, \lfloor d/2 \rfloor\}$ |
| Regularization $\beta$ | Independent | $\{10^{-3}, 10^{-2}, 10^{-1}\}$ |
| Dual support size $k^*$ | Dependent | Extracted from CVXPY dual solution (number of non-zero groups) |
| Empirical test error (hold-out) | Dependent | MSE on 20% hold-out |
| Predicted bound $C\sqrt{k^*/n}$ | Derived | Computed from $k^*$ and $n$ |

### Baselines

- **Standard VC-dimension bound:** $O(\sqrt{m \cdot d / n})$ where $m$ is network width; the
  proposed $k^*$-based bound should be tighter when $k^* \ll m \cdot d$.
- **Rademacher complexity bound for group lasso:** $O(\sqrt{s \log P / n})$ where $s$ is the
  group sparsity level and $P$ is the total number of arrangement patterns; directly related
  to $k^*$ but with an additional $\log P$ factor.
- **Ablation — $k^* = n$ (dense solution, Carathéodory bound tight):** If $k^* \to n$ always,
  the bound gives no improvement; test whether strong regularization reduces $k^*$ below $n/2$.

### DOE Table

| Factor | Low | High | # Levels |
|--------|-----|------|----------|
| $n$ | 50 | 500 | 4 |
| Data rank $r$ | 1 | $d/2$ | 4 |
| Regularization $\beta$ | $10^{-3}$ | $10^{-1}$ | 3 |
| Seeds | — | — | 20 per cell |

**Total runs:** $4 \times 4 \times 3 \times 20 = 960$ CVXPY solves.

### Success Criteria

- **Confirmation:** Spearman correlation between empirical test error and $\sqrt{k^*/n}$ is
  $\rho > 0.7$ across the full $(n, r, \beta)$ grid; log-log slope close to 0.5.
- **Bound tightness:** For $k^* < n/4$ cells, the bound $C\sqrt{k^*/n}$ is within $2\times$
  the empirical test error (using the best constant $C$ estimated by OLS).
- **Falsification:** $\rho < 0.3$ across the grid, or $k^*/n \to 1$ universally (bound vacuous).

### Reproducibility Checklist

- [ ] **Dataset(s):** Synthetic: $X \sim \mathcal{N}(0, I)$ projected to rank $r$ via
      $X = X_0 V_r^T$ where $V_r$ is random orthonormal; $y = X\mathbf{w}^* + \epsilon$ with
      $\|\mathbf{w}^*\|_2 = 1$, $\epsilon \sim \mathcal{N}(0, 0.1)$.
- [ ] **Code framework:** CVXPY (SCS backend, dual extraction via `.dual_value` attribute);
      NumPy for bound computation and correlation analysis.
- [ ] **Hardware:** CPU sufficient for $n \leq 200$; GPU for $n = 500$ cells (CRONOS-JAX).
- [ ] **Random seeds:** 20 per cell; seeded across outer loop.
- [ ] **Expected runtime:** ~6 h CPU for the 960-run grid at $n \leq 200$; ~2 h GPU for $n=500$.

### Methodological Precedents from Literature

[Pilanci&Ergen2020] establishes $k^* \leq n+1$ via Carathéodory's theorem (Theorem 1 proof
step); [Kim&Pilanci2024] notes empirically that $k^* \ll n$ in practice ("as $m^*$ is much
smaller than $n+1$ in practice", arxiv-2402.03625 line 80). Compression-based generalization
bounds following Arora et al. (2018) provide the blueprint for the $O(\sqrt{k^*/n})$ derivation.

---

## E5: Testing H5 — Fixed-Point BN Admits a Convex Equivalent

**Hypothesis:** A two-layer ReLU network with fixed-point batch normalization is equivalent
to the standard convex reformulation with $\text{BN}(X) = \hat{\sigma}^{-1}(X - \hat{\mu}\mathbf{1}^T)$
substituted for $X$; strong duality holds.

### Experimental Design

**Type:** Numerical exact equivalence test  
**Primary method:** Train a two-layer ReLU network with iteratively-converged BN statistics
(fixed-point iteration to convergence); compare training objective at the network's empirical
optimum (multi-run SGD) against the convex reformulation's global minimum with BN-substituted
data matrix $\hat{X} = \text{BN}(X)$.

### Variables

| Variable | Type | Values / Range |
|----------|------|----------------|
| BN evaluation mode | Independent | Fixed-point (iterated to convergence) vs. online (running stats) |
| Training method | Independent | SGD (10 random inits) vs. CVXPY convex reformulation |
| Training objective gap (SGD best vs. convex min) | Dependent | Absolute difference |
| Primal-dual gap of BN-adjusted convex program | Dependent | $p^* - d^*$ (should be 0) |
| $n$ | Control | $\{50\}$ (small; exact enumeration feasible) |
| $d$ | Control | $\{10\}$ |
| $\beta$ | Control | $\{0.01, 0.1\}$ |

### Baselines

- **No-BN convex reformulation ([Pilanci&Ergen2020]):** The standard program with raw $X$;
  its duality gap is 0 and serves as the structural template.
- **SGD with BN (10 random inits):** The minimum training loss across 10 runs approximates
  the true non-convex BN minimum; if the convex program matches this, equivalence is confirmed.
- **Ablation — online BN statistics (not fixed-point):** Should *not* match the convex program's
  optimum; confirms that fixed-point convergence is necessary.

### DOE Table

| Factor | Low | High | # Levels |
|--------|-----|------|----------|
| $\beta$ | $0.01$ | $0.1$ | 2 |
| SGD random init seed | 1 | 10 | 10 |
| BN convergence tolerance | $10^{-6}$ | $10^{-3}$ | 2 |

**Total runs:** $2 \times 10 \times 2 = 40$ SGD runs + $2 \times 2 = 4$ CVXPY solves.

### Success Criteria

- **Confirmation:** Absolute gap between best-of-10-SGD loss and CVXPY convex loss $< 10^{-4}$
  (relative tolerance $< 0.01\%$) for both $\beta$ values, across both BN convergence tolerances.
  Primal-dual gap of the BN-adjusted convex program $< 10^{-6}$.
- **Falsification:** Gap $> 0.1\%$ relative, or primal-dual gap $> 10^{-3}$, confirmed across
  all 10 SGD random initializations, would indicate the fixed-point substitution breaks duality.

### Reproducibility Checklist

- [ ] **Dataset(s):** Synthetic Gaussian, $n=50$, $d=10$; regression target $y = Xw^* + \epsilon$.
- [ ] **Code framework:** PyTorch (SGD + BN layer, fixed-point iteration via repeated forward
      passes until $\|\mu_t - \mu_{t-1}\| < \varepsilon_{\text{BN}}$); CVXPY (exact primal-dual
      for BN-substituted $\hat{X}$).
- [ ] **Hardware:** CPU sufficient; $n=50$, $d=10$ runs in under 1 minute.
- [ ] **Random seeds:** 10 SGD init seeds fixed; CVXPY is deterministic.
- [ ] **Expected runtime:** < 30 min total for all 44 runs.

### Methodological Precedents from Literature

[Ergen&Pilanci2021reveal] proves the BN fixed-point neural collapse result for the last linear
layer (Theorem 4); the methodological precedent is its constucting the BN-adjusted convex program
and verifying the simplex ETF structure follows. The fixed-point BN iteration protocol follows
standard practice in [Ioffe & Szegedy 2015], which is the original BN paper referenced implicitly
in [Ergen&Pilanci2021reveal]'s BN analysis.

---

## E6: Testing H6 — Self-Concordance Extends $O(\sqrt{\log n})$ to Logistic Loss

**Hypothesis:** The $O(\sqrt{\log n})$ relative optimality bound extends from squared loss
to logistic loss via a self-concordance coupling argument, with the same $O(\log n)$ relaxation
width and Gaussian data assumption.

### Experimental Design

**Type:** Theoretical derivation + numerical scaling validation  
**Primary method:** Derive the logistic-loss analog of [Kim&Pilanci2024] Theorem 2.1 via
self-concordance coupling; validate empirically by comparing relative optimality gaps for
squared vs. logistic loss on Gaussian binary classification data across $n \in \{50, 100, 500, 1000\}$.

### Variables

| Variable | Type | Values / Range |
|----------|------|----------------|
| $n$ (sample count) | Independent | $\{50, 100, 200, 500, 1000\}$ |
| Loss function | Independent | Squared loss vs. logistic loss |
| Relative optimality gap $(\tilde{p}^* - p^*)/p^*$ | Dependent | $\geq 0$ |
| Relaxation width $m$ | Control | $O(\log n)$ per [Kim&Pilanci2024] prescription |
| Data | Control | Gaussian i.i.d. (A1), $d = \lfloor 0.8n \rfloor$ |
| Task | Control | Binary classification ($y \in \{-1, +1\}$) |

### Baselines

- **Squared loss + [Kim&Pilanci2024] Theorem 2.1:** The proved $O(\sqrt{\log n})$ gap; the
  logistic loss curve should track this within a constant factor.
- **Logistic loss + full convex reformulation ($m$ = all arrangements):** Reference $p^*$;
  computed via CVXPY for $n \leq 100$, CRONOS for $n > 100$.
- **Ablation — heavy-tailed data (non-Gaussian):** The bound should break for Cauchy-distributed
  data (no sub-Gaussian moment bound); confirms Gaussianity remains necessary.

### Success Criteria

- **Confirmation:** Log-log regression slope for logistic-loss relative gap vs. $n$ is
  $\leq 0.6$ (consistent with $O(\sqrt{\log n})$), within $3\times$ the constant of the
  squared-loss baseline.
- **Falsification:** Slope $> 0.8$ for logistic loss while squared loss achieves slope $\leq 0.5$
  at the same $n$ values, indicating the self-concordance coupling is insufficient.

### Reproducibility Checklist

- [ ] **Dataset(s):** Synthetic Gaussian binary classification; $X_i \sim \mathcal{N}(0, I_d)$,
      $y_i = \text{sign}(X_i^T w^*) \in \{-1, +1\}$ with $\|w^*\|=1$.
- [ ] **Code framework:** CVXPY for full reformulation ($n \leq 100$); CRONOS-JAX with logistic
      loss plugin for $n > 100$. Loss verified via CVXPY's built-in `cp.logistic`.
- [ ] **Hardware:** GPU (RTX-4090) for $n > 200$.
- [ ] **Random seeds:** 20 seeds per $(n, \text{loss})$ cell.
- [ ] **Expected runtime:** ~4 h GPU for full grid.

### Proof Strategy

The derivation modifies [Kim&Pilanci2024] Section 4, Theorem 2.1 at three steps:

1. **Output-space Lipschitz coupling:** The map $\ell_{\text{sq}}(\hat{y}) \to \ell_{\text{logistic}}(\hat{y})$
   is Lipschitz on bounded outputs (the sigmoid gradient is bounded by $1/4$); bound the change
   in the dual variable $\nu$ under the loss substitution.
2. **Self-concordance Newton step:** Self-concordance of logistic loss implies a local quadratic
   approximation $\ell_{\text{logistic}}(\hat{y}) \approx \ell_{\text{sq,local}}(\hat{y})$ valid
   within a Newton step; identify the region where this approximation holds and its curvature constant.
3. **Gordon comparison transfer:** The cone sharpness quantity $\lambda_{\min}(\mathcal{M})$
   is determined by the data $X$ and the arrangement patterns, not the loss function directly;
   once the dual variable is bounded in Step 1, the same Gordon comparison applies, yielding
   the same $O(\sqrt{\log n})$ rate with a modified constant.

Empirical experiments serve as a litmus test: if the logistic-loss gap empirically scales as
$\omega(\sqrt{\log n})$, the theoretical derivation has an error that must be found.

### Methodological Precedents from Literature

[Kim&Pilanci2024] Theorem 2.1 (Gordon's comparison, Lemma 21) is the proof template.
The self-concordance framework follows Nesterov & Nemirovskii (1994) as applied to logistic
regression; the explicit suggestion to use self-concordance for this extension appears in
the Phase 5 review notes and aligns with standard practice in convex optimization theory.

---

## E7: Testing H7 — Active Arrangement Sparsity Anti-Correlates with NTK Alignment (CIFAR-10)

**Hypothesis:** On CIFAR-10 with a three-layer ReLU network, the dual support sparsity $k^*/m$
is negatively correlated (Spearman $\rho < -0.5$) with NTK-CKA alignment across the
$(m, \lambda) \in \{100, 200, 500\} \times \{10^{-4}, 10^{-3}, 10^{-2}\}$ grid.

### Experimental Design

**Type:** Empirical benchmark — medium scale (CIFAR-10)  
**Primary method:** Train three-layer ReLU networks on CIFAR-10 via both gradient descent
(for CKA measurement) and the CRONOS three-layer convex program (for $k^*$ extraction);
correlate $k^*/m$ against CKA$(\text{features}, \text{NTK})$ across the width/regularization grid.

### Variables

| Variable | Type | Values / Range |
|----------|------|----------------|
| Network width $m$ | Independent | $\{100, 200, 500\}$ |
| Regularization $\lambda$ | Independent | $\{10^{-4}, 10^{-3}, 10^{-2}\}$ |
| Relative dual support $k^*/m$ | Dependent | Extracted from CRONOS dual solution |
| NTK-CKA alignment | Dependent | CKA(learned features at layer 2, NTK-predicted kernel) |
| Spearman $\rho(k^*/m, \text{CKA})$ | Derived | Target: $< -0.5$ |
| Dataset | Control | CIFAR-10, 50k train / 10k test (standard split) |
| Architecture | Control | Three-layer ReLU, as validated in user-2110.05518v2 |

### Baselines

- **NTK baseline (infinite-width limit):** Random feature kernel $K_{\text{NTK}}(x, x') = \nabla_\theta f(x)^T \nabla_\theta f(x')$ at random initialization; CKA = 1 at initialization by definition.
- **SGD without regularization ($\lambda \to 0$):** Maximally feature-learning regime; expect
  lowest CKA and potentially lowest $k^*/m$ (or highest — the hypothesis predicts lowest $k^*/m$
  corresponds to highest feature learning, i.e., lowest CKA).
- **Ablation — random network (no training):** $k^*/m$ should be close to 1 (dense dual, no
  selection), CKA should be close to 1 (near NTK regime); confirms convergence distinguishes
  the two metrics.

### DOE Table

| Factor | Low | High | # Levels |
|--------|-----|------|----------|
| Width $m$ | 100 | 500 | 3 |
| Regularization $\lambda$ | $10^{-4}$ | $10^{-2}$ | 3 |
| Training method | GD (CKA) | CRONOS (dual $k^*$) | 2 (matched) |

**Total cells:** $3 \times 3 = 9$ (width × reg); each cell requires 1 CRONOS run + 1 SGD run.

### Success Criteria

- **Primary:** Spearman $\rho(k^*/m, \text{NTK-CKA}) < -0.5$ across the 9-cell grid (one-sided
  test, $\alpha = 0.05$; with 9 data points, $|\rho| > 0.60$ is needed for $p < 0.05$).
- **Directional:** Both $k^*$ increases with $\lambda$ (stronger regularization → sparser dual)
  AND CKA increases with $\lambda$ (stronger regularization → lazier training); independently
  testable before the correlation.
- **Falsification:** $|\rho| < 0.2$ across the grid, or $k^*$ is uniformly $\gtrsim 0.9m$
  (dense dual always), would falsify both the correlation hypothesis and the empirical
  activation of the convex duality regime.

### Reproducibility Checklist

- [ ] **Dataset(s):** CIFAR-10 (public, LeCun et al. 1993); standard 50k/10k split; standard
      normalization (mean=[0.4914,0.4822,0.4465], std=[0.247,0.243,0.261]).
- [ ] **Code framework:** CRONOS-JAX (three-layer convex program from user-2110.05518v2);
      PyTorch (SGD training for CKA computation); CKA implementation from Kornblith et al. (2019)
      (standard open-source implementation, GitHub: google/representation similarity).
- [ ] **Hardware:** GPU (A100 recommended for CIFAR-10 CRONOS); 2–3 h per width-$m$ setting.
- [ ] **Random seeds:** 3 seeds for SGD runs; CRONOS is deterministic.
- [ ] **Expected runtime:** ~18 h GPU total (9 cells × 2 methods × seed).

### Methodological Precedents from Literature

[Feng&Frangella&Pilanci2023] validates CRONOS on CIFAR-10 and CIFAR-100 (Table 1), providing
the exact experimental setup template (network depth, data preprocessing, evaluation metric).
[user-2110.05518v2] validates the three-layer convex program at CIFAR-10 scale ($n = 5 \times 10^4$,
line 353), confirming the implementation is feasible. CKA as the NTK alignment metric follows
Kornblith et al. (NeurIPS 2019), the standard tool for measuring representation similarity.

---

## Tier 3 Stress-Tests (Gap 3.1 and Gap 3.2)

The following are lightweight scoping experiments, not full hypothesis tests. They are included
to determine whether either Tier 3 gap is more tractable than Phase 6 assessed, without committing
full resources.

### ST1: Softmax Attention Arrangement Analog Scoping (Gap 3.1)

**Question:** Does softmax attention's attention pattern matrix $A = \text{softmax}(QK^T/\sqrt{d})$
admit a piecewise-constant structure analogous to ReLU hyperplane arrangements?

**Method:** Enumerate all distinct attention pattern matrices for $n \leq 5$, $d = 2$, across
random $(Q, K)$ pairs; check whether the number of distinct attention pattern matrices is
polynomial in $n$ or exponential.

**Decision rule:** If the number of distinct $A$ matrices is $O(n^c)$ for some $c$, the Tier 3
gap is more tractable than assessed; elevate to Tier 2 in the next iteration. If exponential,
confirm infeasibility and close the gap.

**Effort:** LOW (< 1 day, NumPy enumeration only).

### ST2: Adam Implicit Regularization Characterization (Gap 3.2)

**Question:** Does Adam with weight decay produce solutions with measurably different dual support
$k^*$ compared to SGD with weight decay on the same problem?

**Method:** On a small synthetic dataset ($n=100$, $d=10$), train the two-layer convex program
via (a) CVXPY global minimum, (b) SGD, (c) Adam; compute $k^*$ from each solution's dual.

**Decision rule:** If Adam solutions have consistently different $k^*$ from SGD solutions (gap
$> 10\%$), there is structure worth pursuing. If $k^*$ is indistinguishable, the Tier 3 gap
remains infeasible at theoretical depth.

**Effort:** LOW (< 0.5 day, single CVXPY + PyTorch run).

---

## Implementation Priority Order

1. **E3 (CRONOS-AM Lyapunov, H3)** — Lowest implementation barrier: CRONOS codebase exists,
   modification is a one-line step-size change, UCI benchmarks are ready. Provides immediate
   empirical insight and a demonstration that the framework is active.

2. **E1 (Rank-1 Duality Gap Formula, H1)** — Highest theoretical impact and uniquely enables H4.
   The numerical verification component runs on CPU with small CVXPY calls; start proof derivation
   in parallel with E3 implementation.

3. **E5 (Fixed-Point BN Equivalence, H5)** — Low effort (synthetic small-scale); validates a
   clean theoretical claim with minimal compute. Blocks no other experiment and can run quickly.

4. **E4 (Carathéodory Generalization Bound, H4)** — Medium effort; depends logically (but not
   computationally) on H1's Carathéodory bound. Start after E1 is under way.

5. **E2 (RIP Extension, H2)** — Medium-high effort; proof and numerical components are
   independent. Begin numerical scaling experiment early to detect whether the bound holds
   empirically, which guides whether to invest in the full theoretical derivation.

6. **E6 (Logistic Loss, H6)** — Parallel to E2 in proof structure; lower priority than E2 because
   the logistic loss is less fundamental to the core convex duality framework.

7. **E7 (CIFAR-10 NTK/sparsity probe, H7)** — Highest compute cost; schedule after E1–E6 are
   under way so that intermediate results can inform the experimental grid choices.
