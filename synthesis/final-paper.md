---
phase: 15
status: complete
timestamp: 2026-04-07T00:00:00Z
depends_on: [analysis/literature-map.md, analysis/gap-analysis.md, synthesis/hypotheses.md, synthesis/methodology.md, experiments/triage.md, experiments/H3/analysis.md, sources/manifest.yaml]
token_estimate: 9800
---

# Duality Gap in Dual Convex Optimization of ReLU Neural Networks: An Empirical Analysis

## 1. Abstract

Training ReLU neural networks is NP-hard in general, yet a line of work originating with Pilanci and Ergen (2020) shows that two-layer ReLU networks with squared loss and weight decay are equivalent to finite-dimensional convex programs, with strong duality holding whenever the network is sufficiently wide. For deeper networks the picture is more complex: parallel architectures preserve zero duality gap at any depth, but standard (non-parallel) architectures with three or more layers are known to have non-zero duality gap for linear activations, while the ReLU case is explicitly marked as open in the literature.

This paper reports results from three empirical experiments designed to probe the boundary of this theory. We selected three hypotheses from a systematic gap analysis: H3 (whether the duality gap for standard three-layer ReLU grows monotonically with data rank), H5 (whether the gap emerges sharply at rank two), and H6 (whether elastic net regularization breaks the convex reformulation). H3 was executed to completion across 100 experimental cells spanning five ranks and twenty random seeds. H5 and H6 were not completed in this pipeline run due to scope limitations; their methodological status is documented.

The H3 experiment yields a methodological negative result of scientific value. The most natural empirical instrument for probing the three-layer duality gap—using the two-layer parallel group-$\ell_1$ convex program as a lower bound on the three-layer primal—is invalid. Across all 100 cells, the normalized proxy gap is rank-invariant at approximately 73% (Spearman $\rho = -0.219$, $p = 0.029$), and the rank-one positive control fails by a factor of $8 \times 10^3$. Three independent lines of evidence confirm the instrument failure is structural: the two-layer and three-layer feasible sets are not nested, no valid cross-architecture rescaling lemma exists, and the proxy gap measures an architectural distance that is independent of data rank. The H3 hypothesis itself remains untested; this experiment establishes that the most natural workaround does not function, and precisely why.

---

## 2. Introduction

Deep learning's practical success rests on optimization procedures—stochastic gradient descent and its variants—that are not guaranteed to find global optima. The non-convex landscape of neural network training can, in principle, contain many local minima and saddle points that trap gradient-based methods. A natural question follows: is the training problem secretly convex, or at least equivalent to some tractable program?

Pilanci and Ergen (2020) gave a precise affirmative answer for the simplest nontrivial case [PilanciErgen2020]. Two-layer ReLU networks with $\ell_2^2$ weight decay are exactly equivalent to group $\ell_1$-regularized convex programs in a lifted variable space. The equivalence is not an approximation: primal and dual optimal values coincide (strong duality holds), and the convex program's global minimizer corresponds directly to optimal network weights. This foundational result launched a program—concentrated at Stanford's Pilanci Lab—extending convex reformulations to CNNs [ErgenPilanci2020CNN], vector-output networks [Sahiner2020], batch-normalized networks [Ergen2021BN], polynomial activations [BartanPilanci2021], and deep parallel architectures of arbitrary depth [WangErgenPilanci2021, ErgenPilanci2023Path].

The question of whether the same tractability extends to standard (non-parallel) deep networks remains open. Wang, Ergen, and Pilanci (2021) prove that for standard deep linear networks with three or more layers and vector outputs, the duality gap is strictly positive [WangErgenPilanci2021]. For standard deep ReLU networks, their Table 1 explicitly marks the $L=3$ and $L>3$ cases as unknown—the only exception being rank-one data, where strong duality is proven. This is the central open question motivating the present work.

Understanding this gap matters for both theory and practice. Theoretically, a non-zero duality gap for standard deep ReLU would establish that the convex equivalence program cannot extend to the most commonly used architectures without structural modifications (such as parallelism). Practically, it would imply that the global optimum of the regularized training problem is genuinely inaccessible by primal methods alone, making the question of whether SGD finds near-optimal solutions even more pressing.

This paper makes three contributions:

1. A systematic gap analysis identifying seven open questions in the convex duality literature, scored on confidence, impact, feasibility, verifiability, and empirical tractability.

2. A triage selecting three hypotheses (H3, H5, H6) for empirical testing on an Apple M4 Pro, with documented rationale for eliminating four others (H1, H2, H4, H7).

3. A fully executed experiment for H3 (100 cells, five ranks, twenty seeds) that produces a methodological negative result: the two-layer parallel group-$\ell_1$ convex program cannot serve as an empirical lower bound on the three-layer standard ReLU primal. This negative result is itself scientifically informative, ruling out the most natural instrumentation strategy and characterizing why.

---

## 3. Background and Related Work

### 3.1 Convex Reformulation of Two-Layer ReLU Networks

The foundational result of this research program concerns a two-layer ReLU network with $m$ neurons and squared-loss plus weight-decay regularization:

$$p^* = \min_{\{u_j, \alpha_j\}} \frac{1}{2} \left\|\sum_{j=1}^{m} (Xu_j)_+ \alpha_j - y\right\|_2^2 + \frac{\beta}{2}\sum_{j=1}^{m}\left(\|u_j\|_2^2 + \alpha_j^2\right) \tag{1}$$

Pilanci and Ergen (2020) show that this non-convex program is equivalent to a second-order cone program (SOCP) in a lifted variable space [PilanciErgen2020]. The derivation follows three steps: rescaling neuron weights to convert $\ell_2^2$ weight decay into an $\ell_1$ penalty on output weights (exploiting the positive homogeneity of ReLU); taking the convex dual with respect to output weights; and applying semi-infinite duality with Carathéodory's theorem to convert the resulting infinite-dimensional program into a finite one over the set of hyperplane arrangement patterns $D_1, \ldots, D_P$ induced by the data matrix $X$ [PilanciErgen2020].

The resulting convex program has $2dP$ variables and $2nP$ constraints, where $P \leq 2r(e(n-1)/r)^r$ and $r = \text{rank}(X)$. Strong duality ($p^* = d^*$) holds whenever the network width $m \geq m^*$, where $m^* \leq n+1$ [PilanciErgen2020]. This polynomial complexity in $n$ and $d$ (for fixed rank) is the sense in which two-layer ReLU training is "tractable."

A geometric interpretation accompanies the algebraic result: the minimum-norm interpolation limit connects the problem to the gauge function of a "Neural Gauge"—the convex hull of a rectified ellipsoidal set $\mathcal{Q}_X = \{(Xu)_+ : u \in \mathcal{B}_2\}$ [PilanciErgen2020]. This connection to classical convex geometry via polar gauge duality illuminates why the rescaling step works.

An exact characterization of all global optima (without using duality) was provided by Wang, Lacotte, and Pilanci (2020) [WangLacottePilanci2020], who show that Clarke stationary points of the non-convex objective correspond to global optima of subsampled convex programs. The set of all optimal solutions forms a polyhedral set, later studied in detail by Mishkin and Pilanci (2023) [Mishkin2023Optimal].

### 3.2 Strong Duality and Its Limits: The Depth Question

The passage from two-layer to deeper networks is where the story becomes subtle. Ergen and Pilanci (2021) extend convex duality to architectures composed of multiple three-layer ReLU sub-networks [ErgenPilanci2021Deep]. By treating such architectures as parallel compositions, they prove polynomial-time trainability via convex programs with group $\ell_1$-norm regularization. The crucial structural insight is that the parallel composition admits a convex relaxation that the standard (serially composed) architecture does not.

Wang, Ergen, and Pilanci (2021) provide the definitive theoretical picture for deep networks [WangErgenPilanci2021]. Their central result is a dichotomy: standard deep networks with $L \geq 3$ layers have non-zero duality gap (proven for linear activations with vector outputs), while parallel deep networks of arbitrary depth have zero duality gap with ReLU or linear activations. Table 1 of that paper summarizes the state of knowledge: for standard networks with ReLU activation and $L = 3$ or $L > 3$ with general data, the duality gap status is marked "X"—unknown. The rank-one exception is proven in their appendix: standard three-layer ReLU networks on rank-one data satisfy strong duality.

This dichotomy has architectural implications. Parallel architectures—multi-branch networks like ResNets, Inception, and SqueezeNet—are precisely those for which the convex equivalence extends to arbitrary depth [WangErgenPilanci2021]. Standard architectures, the simplest and most common design, occupy the unknown territory. Path regularization [ErgenPilanci2023Path] (NeurIPS 2023) provides yet another route to convexity for parallel networks, showing that pathwise regularized training admits exact convex reformulations with group sparsity. But for standard architectures beyond rank-one data, the theoretical status is open.

### 3.3 Algorithmic Advances and Scalability

Even where strong duality is proven, the computational complexity of the exact convex program scales as $O(n^r)$ in the data rank, making exact solutions impractical for high-dimensional data. This exponential dependence motivates algorithmic work on efficient approximations.

Mishkin, Sahiner, and Pilanci (2022) develop the SCNN framework, showing that the unregularized two-layer problem is equivalent to an unconstrained "gated ReLU" model—a standard group-$\ell_1$ regularized generalized linear model [Mishkin2022SCNN]. This equivalence enables accelerated proximal gradient methods that improve iteration complexity from $O(1/\epsilon^2)$ to $O(1/\sqrt{\epsilon})$, and augmented Lagrangian solvers that outperform commercial interior-point solvers. The SCNN solver scales to MNIST and CIFAR-10, a significant advance over prior work restricted to synthetic data [Mishkin2022SCNN].

Feng, Frangella, and Pilanci (2023) introduce CRONOS, an ADMM-based solver implemented in JAX with GPU acceleration [Feng2023CRONOS]. CRONOS is the first convex neural network solver to scale to ImageNet. For multi-layer networks, CRONOS uses an alternating minimization extension (CRONOS-AM) that decomposes the problem into non-convex inner-layer subproblems (solved by Adam) and convex last-two-layer subproblems (solved by CRONOS). CRONOS-AM achieves comparable or better validation accuracy than tuned SGD and Adam on vision and language tasks including GPT-2 fine-tuning [Feng2023CRONOS]. Critically, the alternating minimization scheme has no convergence guarantee or optimality gap bound—the CRONOS paper explicitly identifies this as open future work.

Kim and Pilanci (2024) provide a theoretical bridge between exact and approximate solutions [Kim2024]. They prove that Gaussian random relaxations of the exact convex reformulation achieve a relative optimality gap bounded by $O(\sqrt{\log n})$ under Gaussian data assumptions, yielding a tractable polynomial-time algorithm with global optimality guarantees. The tightness of this bound on typical instances is, however, empirically untested.

### 3.4 Architectural Extensions

The scope of convex reformulation has been extended well beyond the canonical two-layer fully connected ReLU network.

For CNNs, Ergen and Pilanci (2020) prove that two- and three-layer CNNs can be globally optimized in polynomial time via convex programs [ErgenPilanci2020CNN]. A key finding is that architectural choices—pooling method, connectivity pattern—correspond to different implicit convex regularizers, ranging from $\ell_1$ and $\ell_2$ norms to nuclear norm. Different CNN designs are not merely different parameterizations of the same problem; they implicitly solve different regularized convex programs.

For vector-output networks, Sahiner et al. (2020) discover a connection to copositive programming and completely positive matrices [Sahiner2020]. Optimal weights have closed-form expressions via soft-thresholded SVD under certain data-label conditions.

For batch normalization, Ergen et al. (2021) show that BN effectively whitens the data in the equivalent convex formulation, and that gradient descent on BN networks induces an implicit regularization that preferentially learns high-singular-value directions [Ergen2021BN].

For polynomial activations, Bartan and Pilanci (2021) prove a regularizer-sensitivity result: standard $\ell_2^2$ weight decay makes the problem NP-hard, but cubic regularization or unit-norm constraints render it polynomial-time solvable via semidefinite programming [BartanPilanci2021]. This result foreshadows the H6 hypothesis (Section 4): the choice of regularizer is not neutral.

### 3.5 A Different Perspective: Input Convexity

Gagneux et al. (2025) address a related but distinct question—when do ReLU networks implement convex functions (as functions of their inputs), rather than whether training is convex [Gagneux2025]. They prove that input convex neural networks (ICNNs) suffice to represent all convex functions implementable by one-hidden-layer ReLU networks, but for two or more hidden layers, there exist convex ReLU functions outside the ICNN class. This result about function-level convexity is orthogonal to the training-problem convexity studied above, and provides a useful conceptual boundary: not every notion of "convexity" in neural networks is the same.

---

## 4. Research Gaps and Hypotheses

### 4.1 Gap Analysis

From a systematic analysis of the literature, we identified six Tier 1 and Tier 2 gaps (gaps receiving composite scores above 6.5/10 on confidence, impact, feasibility, verifiability, and empirical testability). The three highest-priority gaps are:

**Gap 1.1 (score 8.3/10): Empirical characterization of the duality gap for standard deep ReLU networks ($L \geq 3$).** Table 1 of Wang et al. (2021) explicitly marks the standard ReLU $L=3$ and $L>3$ cases as unknown [WangErgenPilanci2021]. This is the central open question in the field: no empirical measurement, no theoretical characterization. The only positive result is the rank-one special case.

**Gap 1.2 (score 8.5/10): Optimality gap of CRONOS-AM.** The CRONOS paper explicitly asks "Can we provide a convergence guarantee for CRONOS-AM?" as open future work [Feng2023CRONOS]. CRONOS-AM is currently the only method that scales convex neural network training to ImageNet, yet its solution quality relative to the global optimum is entirely unknown for deep networks.

**Gap 2.1 (score 7.2/10): Effect of regularizer choice on convex reformulation.** All ReLU network convex duality results assume $\ell_2^2$ weight decay. The entire reformulation pipeline is built on the rescaling lemma, which is specific to the $\ell_2^2$ structure. Whether alternative regularizers (elastic net, spectral norm) break the reformulation at step one has not been studied [BartanPilanci2021 provides a precedent showing regularizer sensitivity for polynomial activations].

**Gap 2.4 (score 7.7/10): Strong duality beyond rank-one for standard three-layer ReLU.** Wang et al. prove strong duality for standard three-layer ReLU only at rank one. The rank-two, rank-three, and bounded-rank cases are marked unknown. Understanding where the rank threshold for strong duality lies would sharply characterize the boundary of the convex equivalence theory.

### 4.2 Selected Hypotheses

Phase 11 triage selected three hypotheses for empirical testing based on composite feasibility-impact scores and hardware constraints (Apple M4 Pro, 24GB RAM, no GPU dependency):

**H3 (composite score 7.4): Duality Gap for Standard 3-Layer ReLU Networks Is Bounded by a Data-Rank-Dependent Quantity.**

> If standard (non-parallel) 3-layer ReLU networks are trained on synthetic data matrices $X \in \mathbb{R}^{100 \times 10}$ with controlled rank $r \in \{1, 2, 3, 4, 5\}$, then the gap between the non-convex primal optimal value and the parallel-architecture group-$\ell_1$ convex optimum (used as a lower bound on the dual) will be zero for $r=1$ and will increase monotonically with rank, as measured by the normalized gap $(P_{\text{standard}} - D_{\text{parallel}}) / P_{\text{standard}}$.

The null hypothesis is that the gap does not increase monotonically, or is zero for all ranks tested, suggesting strong duality may hold more broadly. Success criteria require: (1) rank-one positive control gap $< 10^{-4}$, (2) Spearman $\rho > 0.8$ ($p < 0.05$) across 100 cells, and (3) mean gap at $r=5$ exceeding mean gap at $r=2$ by at least a factor of two.

**H5 (composite score 8.2): Duality Gap Emerges at Rank 2 for Standard 3-Layer ReLU Networks.**

> If standard 3-layer ReLU networks are trained on rank-2 data ($n=100$, $d=10$), the gap between the standard non-convex primal and the parallel-architecture convex lower bound will exceed $10^{-4}$ in at least 90% of random seeds, with the rank-one case yielding gap $< 10^{-6}$ across all seeds (positive control).

H5 is the sharpest possible test of whether rank-one is the exact boundary for strong duality in standard deep ReLU.

**H6 (composite score 8.8, highest): Elastic Net Regularization Breaks the Convex Reformulation for Two-Layer ReLU Networks.**

> If two-layer ReLU networks are trained with elastic net regularization ($\lambda_1 \|w\|_1 + \lambda_2 \|w\|_2^2$, $\lambda_1 / \lambda_2 = 1$), the gap between the non-convex elastic net optimal and the standard $\ell_2^2$ convex reformulation's optimal will exceed 10% of the non-convex optimum ($n=200$, $d=10$, Gaussian).

The rationale is that the rescaling lemma—which converts $\ell_2^2$ weight decay to $\ell_1$ on output weights by exploiting positive homogeneity of ReLU—does not apply when an $\ell_1$ term is present. H6 asks not whether the duality gap changes, but whether the reformulation can be constructed at all.

---

## 5. Experimental Setup

### 5.1 H3: Rank-Dependent Duality Gap — Setup

**Objective.** Determine whether the normalized gap between the standard three-layer ReLU primal and the parallel-architecture group-$\ell_1$ convex lower bound grows monotonically with data rank.

**Data generation.** Rank-controlled synthetic regression: $X = AB^T$ with $A \in \mathbb{R}^{100 \times r}$, $B \in \mathbb{R}^{10 \times r}$, entries IID standard Gaussian, yielding exact rank $r$. Targets $y = Xw_{\text{true}} + 0.1\varepsilon$ with $w_{\text{true}}, \varepsilon \sim \mathcal{N}(0, I)$. Ranks swept: $r \in \{1, 2, 3, 4, 5\}$; 20 random seeds per rank; 100 cells total.

**Primal architecture.** Standard three-layer fully connected ReLU with no biases: $\mathbb{R}^{10} \to \mathbb{R}^{50} \to \mathbb{R}^{50} \to \mathbb{R}^1$. Objective: $(1/2n)\|y - f_\theta(X)\|^2 + \beta\|\theta\|_F^2$ with $\beta = 0.01$. Optimizer: Adam, learning rate $10^{-3}$, 2000 epochs, 50 random restarts per cell (best retained).

**Proxy lower bound.** Two-layer parallel group-$\ell_1$ convex program. Activation sign patterns sampled by drawing random hyperplane normals over $X$; up to $P = 200$ patterns retained. Solved via CVXPY + SCS with 10,000 maximum iterations. Regularization parameter set to $\beta_{\text{convex}} = \beta$ (an empirical patch applied after the roadmap's prescribed formula $\beta_{\text{convex}} = 2\sqrt{\beta}$ caused the proxy dual to exceed the primal in early runs).

**Evaluation metric.** Normalized gap: $\text{gap} = (P_{\text{standard}} - D_{\text{parallel}}) / P_{\text{standard}}$.

**Base case criteria.** PASS requires all three: (1) rank-one mean absolute gap $< 10^{-6}$ and max gap $< 10^{-4}$; (2) Spearman $\rho > 0.8$ ($p < 0.05$) across all 100 cells; (3) mean gap at $r=5$ exceeds mean gap at $r=2$ by at least a factor of two.

### 5.2 H5: Rank-2 Gap Emergence — Setup (Planned, Not Executed)

H5 was designed as the sharpest binary test of whether rank-one is the exact boundary for strong duality in standard three-layer ReLU networks. The setup mirrors H3's infrastructure with two modifications: only ranks $r \in \{1, 2\}$ are tested, and 50 random seeds (rather than 20) are used per rank to provide higher statistical power for the binary outcome.

**Architecture.** Standard three-layer ReLU, $\mathbb{R}^{10} \to \mathbb{R}^{50} \to \mathbb{R}^{50} \to \mathbb{R}^1$, identical to H3.

**Instrument.** Same parallel-architecture group-$\ell_1$ convex program as H3, but with the matched two-layer formulation from Wang et al. (2021) for rank-one data [WangErgenPilanci2021].

**Success criterion.** Rank-one gap $< 10^{-6}$ across all seeds (positive control), and rank-two gap $> 10^{-4}$ in at least 90% of seeds (one-sample $t$-test, $p < 0.01$).

H5 was not executed in this pipeline run. The H3 results (Section 6.1) reveal that the proxy instrument used in both H5 and H3 is fundamentally invalid (the two-layer convex program is not a valid lower bound on the three-layer primal), which would cause H5 to fail its positive control in exactly the same way H3's did. H5 therefore requires a new instrument before execution is meaningful. The scientific design of H5 remains sound; only its instrumentation needs revision.

### 5.3 H6: Elastic Net and the Rescaling Lemma — Setup (Partial, Not Completed)

H6 was designed to test whether adding an $\ell_1$ component to the regularizer breaks the foundational rescaling step of the convex reformulation.

**Architecture.** Two-layer ReLU, $\mathbb{R}^{10} \to \mathbb{R}^{100} \to \mathbb{R}^1$, with elastic net regularization $\lambda_1\|W_1\|_1 + \lambda_2\|W_1\|_F^2 + \lambda_2\alpha^2$ at ratio $\lambda_1 / \lambda_2 = 1$.

**Planned comparison.** Non-convex elastic net training (PyTorch, Adam, multiple restarts) vs. the standard $\ell_2^2$ convex SCNN program (using the public pilancilab/scnn codebase), both on the same data ($n=200$, $d=10$, Gaussian).

**What was executed.** H6 reached the ablation gate in iteration one. The ablation revealed a methodological subtlety: in overparameterized regimes (network width much larger than $n$), a random sample of 200 activation patterns does not adequately cover the full convex cone. The $\ell_2^2$ control (which should show gap $< 1\%$) showed approximately 89% disagreement between the convex and non-convex solutions under this sampling regime—not because elastic net breaks anything, but because the random pattern sample was insufficient. The main experiment was not unlocked. The reviewer's proposed fix (underparameterized regime, width 10, pattern count 500, 200 restarts, 8000 epochs) was not executed in this run.

The H6 ablation failure is itself a documentable finding: random activation-pattern sampling does not adequately approximate the full convex cone in overparameterized regimes, a practical limitation of the random-sampling approach to the hyperplane arrangement problem.

---

## 6. Results

### 6.1 H3 Results: Rank-Invariant Proxy Gap

All 100 experimental cells solved to completion with $P_{\text{standard}} \geq D_{\text{parallel}}$ in every cell (primal validity fraction: 1.0). The base case verdict is **FAIL** on all three criteria.

**Per-rank gap statistics.** Table 1 reports the normalized gap $(P_{\text{standard}} - D_{\text{parallel}}) / P_{\text{standard}}$ for each rank level.

| Rank | $N$ | Mean gap | Std | Min | Max | Median |
|------|-----|----------|-----|-----|-----|--------|
| 1 | 20 | 0.741 | 0.037 | 0.661 | 0.815 | 0.747 |
| 2 | 20 | 0.748 | 0.026 | 0.699 | 0.790 | 0.751 |
| 3 | 20 | 0.744 | 0.029 | 0.673 | 0.811 | 0.742 |
| 4 | 20 | 0.728 | 0.026 | 0.686 | 0.780 | 0.722 |
| 5 | 20 | 0.729 | 0.041 | 0.666 | 0.817 | 0.730 |

The five distributions are essentially identical. The per-rank confidence intervals almost completely overlap. There is no increasing trend; if anything, the weak trend from rank 1 to rank 5 is slightly decreasing.

**Spearman correlation.** Computing Spearman $\rho$ between rank and normalized gap across all 100 cells yields $\rho = -0.219$ ($p = 0.029$). The correlation is statistically significant—but in the wrong direction. The hypothesis predicted $\rho > 0.8$; the observed value is negative.

**Base case evaluation summary.** Table 2 reports all base case metrics.

| Metric | Threshold | Observed | Verdict |
|--------|-----------|----------|---------|
| Spearman $\rho$ | $> 0.80$ | $-0.219$ ($p = 0.029$) | FAIL (wrong sign) |
| Rank-1 mean gap | $< 10^{-6}$ | $0.741$ | FAIL ($7.4 \times 10^5 \times$ over threshold) |
| Rank-1 max gap | $< 10^{-4}$ | $0.815$ | FAIL ($8.1 \times 10^3 \times$ over threshold) |
| Monotone in means | non-decreasing | False (drops ranks 3$\to$4) | FAIL |
| Ratio gap($r=5$)/gap($r=2$) | $\geq 2.0$ | $0.975$ | FAIL (essentially 1) |
| Primal validity ($P \geq D$) | 100\% | 100\% | PASS |

**Primal and dual values.** Table 3 reports the mean primal and dual objective values per rank.

| Rank | Mean $P_{\text{standard}}$ | Mean $D_{\text{parallel}}$ | Ratio $P/D$ |
|------|--------------------------|--------------------------|------------|
| 1 | 0.0580 | 0.0146 | 3.97 |
| 2 | 0.0758 | 0.0190 | 3.99 |
| 3 | 0.1023 | 0.0260 | 3.94 |
| 4 | 0.0978 | 0.0269 | 3.64 |
| 5 | 0.1295 | 0.0340 | 3.81 |

Both $P_{\text{standard}}$ and $D_{\text{parallel}}$ grow approximately 2.2× from $r=1$ to $r=5$, but they do so at nearly the same rate. Their ratio is approximately constant at $\sim 3.9$, making the normalized gap rank-invariant by construction.

**Diagnostic hyperparameter sweeps.** Four additional sweeps were conducted to rule out confounds: (1) network widths $\{30, 50, 100, 200, 500\}$—gap is width-invariant; (2) number of restarts $\{20, 50, 100\}$—more restarts reduce $P_{\text{standard}}$ slightly but do not approach $D_{\text{parallel}}$; (3) training epochs $\{2000, 5000\}$—no material change; (4) regularization $\beta \in \{0.01, 0.001, 10^{-4}, 10^{-5}\}$—the rank-invariance persists across all values. The failure is structural, not a hyperparameter issue.

**Figures.** Four figures are available in `experiments/H3/results/figures/`:
- `gap_vs_rank.png` — mean normalized gap vs. rank with per-seed scatter; shows flat ~0.73 baseline and slight downward drift at ranks 4–5.
- `gap_distribution_violin.png` — per-rank violin plots; all five distributions overlap almost completely.
- `primal_vs_dual_scatter.png` — scatter of $(D_{\text{parallel}}, P_{\text{standard}})$ across 100 cells color-coded by rank; near-linear scaling (slope ~3.9) is the direct cause of the rank-invariant ratio.
- `rank1_positive_control.png` — per-seed gap at rank 1 with the $10^{-4}$ threshold; every seed is approximately four orders of magnitude above the threshold line.

### 6.2 H5 Results: Not Executed

H5 was not executed in this pipeline run. Its status is `roadmap_complete` with zero experimental steps completed. As documented in Section 5.2, the H3 results reveal that H5's shared instrument (the two-layer parallel convex program as a lower bound on the three-layer primal) would fail H5's positive control in the same way. Running H5 without first developing a valid instrument would replicate H3's failure without additional scientific content.

### 6.3 H6 Results: Ablation Gate, Not Completed

H6 reached the ablation gate in iteration one and was not completed. The ablation revealed that in the overparameterized regime (width $= 100$, $n = 200$, $d = 10$), a random sample of $P = 200$ activation patterns does not adequately cover the full convex cone required by the group-$\ell_1$ convex reformulation. The $\ell_2^2$ control condition—which should have shown gap $< 1\%$ to confirm the baseline works—showed approximately 89% disagreement between the convex and non-convex solutions. This is a sampling problem, not a result about elastic net.

The reviewer's fix (underparameterized regime, width 10, pattern count 500, 200 restarts) was not executed due to scope constraints. H6's scientific question—whether elastic net breaks the convex reformulation—is well-posed and remains untested.

---

## 7. Discussion

### 7.1 What the H3 Negative Result Establishes

The H3 experiment was carefully designed but the instrument was flawed. Understanding why it failed is the experiment's primary contribution.

The roadmap's justification for using the two-layer parallel group-$\ell_1$ convex program as a lower bound on the three-layer standard ReLU primal rested on the following claim: "the parallel architecture has zero duality gap, and its feasible set is a superset of the standard architecture, so any minimizer over the parallel feasible set achieves a value $\leq$ any standard primal minimum." This claim is false when applied across different depth architectures. A two-layer parallel ReLU sum does not contain every function realizable by a stacked three-layer ReLU composition. The feasible sets are defined by different functional forms; neither is a subset of the other.

The numerical evidence confirms this in three ways. First, the $\beta_{\text{convex}} = 2\sqrt{\beta}$ rescaling formula prescribed in the roadmap—derived from the correct two-layer rescaling lemma applied to matched architectures—caused $D_{\text{parallel}} > P_{\text{standard}}$ in early runs, falsifying the lower-bound claim directly. The patch to $\beta_{\text{convex}} = \beta$ restored $P \geq D$ in all cells, but has no theoretical justification in the cross-architecture setting. Second, the rank-one positive control fails by a factor of $8 \times 10^3$: Wang, Ergen, and Pilanci (2021) prove zero gap at rank one for the two-layer architecture with its own matched convex program—not for a comparison between a three-layer primal and a two-layer dual [WangErgenPilanci2021]. At rank one, the two-layer program achieves a lower objective than the three-layer primal because it faces less regularization burden (one weight matrix under group-$\ell_1$ vs. three matrices under $\ell_2^2$). Third, the rank-invariance itself is mechanistically explained: higher-rank data allows more distinct hyperplane arrangement patterns to be sampled, making $D_{\text{parallel}}$ more expressive at higher ranks—which if anything tightens the bound, producing the slight negative Spearman correlation.

### 7.2 Implications for Probing the Three-Layer Duality Gap

The H3 negative result has a specific implication for any future attempt to empirically characterize the duality gap for standard deep ReLU networks. The natural workaround—repurposing the two-layer convex program as a proxy lower bound—does not work, even at rank one where theory guarantees zero gap for the matched architecture. A proper empirical test requires one of two things, neither of which is currently available: a closed-form dual for the three-layer compositional primal (an open theoretical problem), or exhaustive enumeration of sign-pattern products across both hidden layers (exponential in the number of sign patterns, intractable beyond toy scale for moderate network widths).

This is not merely a practical obstacle. The absence of a formulated dual for standard deep ReLU networks is itself theoretically significant. The derivation of the two-layer dual exploits the specific structure of the one-hidden-layer objective: the ReLU activation creates a bilinear form in the hidden and output weights, which can be handled by a single application of semi-infinite duality. A three-layer composition creates a trilinear form (hidden-to-hidden weights, hidden-to-output weights, output weights) that does not yield to the same technique. The sanity check (Phase 5) anticipated this difficulty; the H3 experiment confirms it concretely.

### 7.3 The H6 Ablation as a Scientific Finding

The H6 ablation failure—that random activation-pattern sampling does not adequately approximate the full convex cone in overparameterized regimes—is a meaningful practical finding. The group-$\ell_1$ convex program for two-layer ReLU networks is defined over the set of all possible hyperplane arrangement patterns induced by the data. The exact number of patterns is $P \leq 2r(e(n-1)/r)^r$, which is exponential in the data rank [PilanciErgen2020]. In practice, algorithms like SCNN and the approach used in H6 sample a subset of these patterns randomly and solve the resulting restricted program [Mishkin2022SCNN].

The ablation shows that with 200 patterns, $n = 200$, and an overparameterized network (width 100), the sampled patterns do not cover the activation patterns the non-convex solver uses during training. The convex program and the non-convex program are effectively solving different problems. This gap between "theoretically equivalent" and "numerically equivalent under random sampling" is an important practical caveat for any implementation of the convex reformulation framework.

### 7.4 Connection to the Broader Theoretical Framework

These results, negative as they are, connect coherently to the theoretical picture established by the literature. Wang, Ergen, and Pilanci (2021) leave the standard deep ReLU duality gap open because the theoretical tools for analyzing it—a formulated dual for the three-layer compositional primal—do not yet exist [WangErgenPilanci2021]. H3 tried the most natural empirical workaround and found it invalid. This is consistent with the theoretical difficulty: the gap in Table 1 is open not for lack of effort but because the problem is genuinely hard.

The parallel between H6's ablation and the Bartan-Pilanci result [BartanPilanci2021] is also instructive. Bartan and Pilanci show that for polynomial activations, the regularizer determines whether the training problem is NP-hard or polynomial-time solvable. The H6 ablation, while not completed, already suggests that implementation subtleties (overparameterization, sampling coverage) interact with regularizer choice in ways that are not captured by the theoretical equivalence alone.

---

## 8. Limitations and Future Work

**Scope limitations.** This pipeline run completed only one of three planned experiments. H5 and H6 were not executed to completion; H5 because the H3 results revealed its shared instrument is invalid, and H6 because the ablation gate revealed an overparameterization-sampling interaction that the recommended fix (underparameterized regime, higher pattern count) did not have time to address.

**Architectural scale.** H3 used a single architectural shape ($10 \to 50 \to 50 \to 1$) and a single data scale ($n=100$, $d=10$). The structural failure—that the two-layer proxy is not a valid lower bound—is unlikely to depend on scale, but this was not tested. Larger networks and datasets might expose additional phenomena.

**Optimizer coverage.** Only Adam was used for the non-convex three-layer primal. L-BFGS with full-batch gradients would provide tighter primal solutions, potentially smaller $P_{\text{standard}}$ values, but would not resolve the rank-invariance of the proxy gap.

**What would advance the science.** Three directions follow directly from these results:

1. *Theoretical dual derivation for standard three-layer ReLU.* The central missing ingredient is a formulated dual program for the three-layer standard architecture. Even an approximate dual (e.g., a convex relaxation of the trilinear structure) would enable the empirical characterization that H3 attempted. This is likely a theoretical contribution before it is an empirical one.

2. *H5 with a valid instrument.* Once a matched three-layer dual or a valid lower bound is available, H5's experimental design (rank-one positive control, rank-two test, 50 seeds) is well-posed and immediately executable. It would provide the sharpest possible characterization of the rank-one special case.

3. *H6 with underparameterized regime.* The reviewer's proposed fix for H6 is concrete: width 10, pattern count 500, 200 restarts, 8000 epochs. This is a small change to the experimental setup that directly addresses the ablation failure. The H6 question—whether elastic net breaks the convex reformulation—is the most cleanly testable of the three hypotheses and warrants a second attempt.

---

## 9. Conclusion

This paper reports an empirical investigation of the duality gap in convex reformulations of ReLU neural networks, focusing on three hypotheses (H3, H5, H6) selected from a systematic gap analysis of twenty sources.

The executed experiment (H3, 100 cells) establishes a negative result of methodological value: the two-layer parallel group-$\ell_1$ convex program cannot be used as an empirical lower bound on the three-layer standard ReLU primal. The normalized proxy gap is rank-invariant at approximately 73% across all five ranks tested (Spearman $\rho = -0.219$, $p = 0.029$), and the rank-one positive control—which should yield near-zero gap if the instrument were valid—fails by a factor of $8 \times 10^3$. Four diagnostic hyperparameter sweeps confirm the failure is structural: the two-layer and three-layer feasible sets are not nested, no valid cross-architecture rescaling lemma exists, and the proxy measures an architectural distance that is independent of data rank.

The H3 hypothesis itself—that the duality gap for standard three-layer ReLU grows monotonically with data rank—remains untested. What this experiment has established is the boundary of the most natural empirical approach. A valid test requires either a closed-form dual for the three-layer compositional primal (an open theoretical problem) or tractable enumeration of cross-layer sign-pattern products (computationally infeasible at present).

The unexecuted hypotheses (H5, H6) each have clear, concrete fixes documented in Section 8. Both are well-designed experiments that address genuine open questions in the convex reformulation literature. Their execution, with the methodological lessons from H3 and H6's ablation incorporated, is the natural next step for this research program.

---

## 10. References

- Bartan, B., & Pilanci, M. (2021). *Neural Spectrahedra and Semidefinite Lifts: Global Convex Optimization of Polynomial Activation Neural Networks in Fully Polynomial-Time*. arXiv:2101.02429. https://arxiv.org/abs/2101.02429

- Dwaraknath, R. V., Ergen, T., & Pilanci, M. (2023). *Fixing the NTK: From Neural Network Linearizations to Exact Convex Programs*. arXiv:2309.15096. https://arxiv.org/abs/2309.15096

- Ergen, T., & Pilanci, M. (2020). *Convex Geometry and Duality of Over-parameterized Neural Networks*. arXiv:2002.11219. https://arxiv.org/abs/2002.11219

- Ergen, T., & Pilanci, M. (2020). *Implicit Convex Regularizers of CNN Architectures: Convex Optimization of Two- and Three-Layer Networks in Polynomial Time*. arXiv:2006.14798. https://arxiv.org/abs/2006.14798 (ICLR 2021)

- Ergen, T., & Pilanci, M. (2021). *Global Optimality Beyond Two Layers: Training Deep ReLU Networks via Convex Programs*. arXiv:2110.05518. https://arxiv.org/abs/2110.05518

- Ergen, T., & Pilanci, M. (2021). *Path Regularization: A Convexity and Sparsity Inducing Regularization for Parallel ReLU Networks*. arXiv:2110.09548. https://arxiv.org/abs/2110.09548 (NeurIPS 2023)

- Ergen, T., & Pilanci, M. (2023). *The Convex Landscape of Neural Networks: Characterizing Global Optima and Stationary Points via Lasso Models*. arXiv:2312.12657. https://arxiv.org/abs/2312.12657

- Ergen, T., Pilanci, M. (2021). *Revealing the Structure of Deep Neural Networks via Convex Duality*. arXiv:2002.09773. https://arxiv.org/abs/2002.09773 (ICML 2021)

- Ergen, T., Sahiner, A., Ozturkler, B., Pauly, J., Mardani, M., & Pilanci, M. (2021). *Demystifying Batch Normalization in ReLU Networks: Equivalent Convex Optimization Models and Implicit Regularization*. arXiv:2103.01499. https://arxiv.org/abs/2103.01499

- Feng, M., Frangella, Z., & Pilanci, M. (2023). *CRONOS: Enhancing Deep Learning with Scalable GPU Accelerated Convex Neural Networks*. (user-8652-CRONOS). https://github.com/pilancilab/CRONOS

- Gagneux, A., Massias, M., Soubies, E., & Gribonval, R. (2025). *Convexity in ReLU Neural Networks: beyond ICNNs?* arXiv:2501.03017. https://arxiv.org/abs/2501.03017

- Kim, S., & Pilanci, M. (2024). *Convex Relaxations of ReLU Neural Networks Approximate Global Optima in Polynomial Time*. arXiv:2402.03625. https://arxiv.org/abs/2402.03625 (ICML 2024)

- Mishkin, A., & Pilanci, M. (2023). *Optimal Sets and Solution Paths of ReLU Networks*. arXiv:2306.00119. https://arxiv.org/abs/2306.00119

- Mishkin, A., Sahiner, A., & Pilanci, M. (2022). *Fast Convex Optimization for Two-Layer ReLU Networks: Equivalent Model Classes and Cone Decompositions*. arXiv:2202.01331. https://arxiv.org/abs/2202.01331 (ICML 2022)

- Pilanci, M., & Ergen, T. (2020). *Neural Networks are Convex Regularizers: Exact Polynomial-time Convex Optimization Formulations for Two-layer Networks*. arXiv:2002.10553. https://arxiv.org/abs/2002.10553

- Sahiner, A., Ergen, T., Pauly, J., & Pilanci, M. (2020). *Vector-output ReLU Neural Network Problems are Copositive Programs: Convex Analysis of Two Layer Networks and Polynomial-time Algorithms*. arXiv:2012.13329. https://arxiv.org/abs/2012.13329

- Wang, Y., Ergen, T., & Pilanci, M. (2021). *Parallel Deep Neural Networks Have Zero Duality Gap*. arXiv:2110.06482. https://arxiv.org/abs/2110.06482 (ICLR 2023)

- Wang, Y., Lacotte, J., & Pilanci, M. (2020). *The Hidden Convex Optimization Landscape of Two-Layer ReLU Neural Networks: an Exact Characterization of the Optimal Solutions*. arXiv:2006.05900. https://arxiv.org/abs/2006.05900

- Zeger, E., Wang, Y., Mishkin, A., Ergen, T., Candes, E., & Pilanci, M. (2024). *A Library of Mirrors: Deep Neural Nets in Low Dimensions are Convex Lasso Models with Reflection Features*. arXiv:2403.01046. https://arxiv.org/abs/2403.01046

---

## 11. Appendix: Additional Experimental Details

### A. H3 Full Results

**Raw per-cell results** are available in `experiments/H3/results/raw_results.json` (100 entries, one per (rank, seed) pair). Each entry contains: rank, seed, primal objective value ($P_{\text{standard}}$), dual objective value ($D_{\text{parallel}}$), normalized gap, number of training epochs, number of Adam restarts, number of sign patterns used, CVXPY solve status, and wall-clock time.

**Summary statistics** are in `experiments/H3/results/summary_table.csv`. Reproduced here for completeness:

| rank | n_seeds | mean_gap | std_gap | median_gap | min_gap | max_gap | cv |
|------|---------|----------|---------|------------|---------|---------|-----|
| 1 | 20 | 0.7409 | 0.0365 | 0.7465 | 0.6611 | 0.8145 | 0.049 |
| 2 | 20 | 0.7483 | 0.0257 | 0.7514 | 0.6985 | 0.7905 | 0.034 |
| 3 | 20 | 0.7439 | 0.0287 | 0.7419 | 0.6727 | 0.8110 | 0.039 |
| 4 | 20 | 0.7278 | 0.0264 | 0.7218 | 0.6856 | 0.7804 | 0.036 |
| 5 | 20 | 0.7292 | 0.0412 | 0.7302 | 0.6660 | 0.8167 | 0.057 |

The coefficient of variation (cv) ranges from 0.034 to 0.057, confirming that the distribution at each rank is tight relative to its mean. The near-constant means and low variance establish that the rank-invariance is not an artifact of noisy measurements.

**Formal verdict** from `experiments/H3/results/base_case_evaluation.json`:

```json
{
  "pass": false,
  "verdict": "FAIL",
  "metric_name": "spearman_rho_rank_vs_gap",
  "metric_value": -0.219,
  "threshold": 0.8,
  "spearman_p_value": 0.029,
  "rank1_max_abs_gap": 0.815,
  "positive_control_ok": false,
  "monotone_in_means": false,
  "magnitude_ratio_r5_over_r2": 0.975,
  "primal_valid_fraction": 1.0,
  "n_cells": 100
}
```

### B. H3 Hyperparameter Sweep Details

**Width sweep.** Standard three-layer ReLU widths $\{30, 50, 100, 200, 500\}$ tested at rank 1 and rank 5 (5 seeds each). The proxy gap ranged from 0.68 to 0.79 across all configurations. The primal objective decreases with width (wider networks find better solutions), but the dual objective decreases proportionally, keeping the normalized gap stable.

**Restart sweep.** Number of Adam restarts $\{20, 50, 100\}$ at rank 1 (10 seeds each). Additional restarts reduced the best-observed primal from approximately 0.060 to 0.052, but $D_{\text{parallel}}$ at rank 1 is approximately 0.015 regardless. The normalized gap narrows slightly with more restarts but remains far above the $10^{-4}$ threshold.

**Epoch sweep.** Training epochs $\{2000, 5000\}$ at rank 1 and rank 3 (5 seeds each). The 5000-epoch run showed marginal improvement in primal objective ($\sim 3\%$) and no material change in the normalized gap.

**Regularization sweep.** $\beta \in \{10^{-2}, 10^{-3}, 10^{-4}, 10^{-5}\}$ at ranks 1 and 5 (5 seeds each). The ratio $P_{\text{standard}} / D_{\text{parallel}}$ stays in the range $[3.5, 5.2]$ across all values, confirming that the rank-invariance is not a regularization artifact.

### C. H3 Root Cause: The Cross-Architecture Lower Bound Fallacy

The roadmap's core error was treating the parallel two-layer group-$\ell_1$ program as a lower bound on the standard three-layer $\ell_2^2$ primal based on an incorrect "feasible-set superset" argument. The argument fails because:

1. The two-layer parallel program optimizes over functions of the form $\sum_{j=1}^P \alpha_j (Xu_j)_+ D_j$ (a single-hidden-layer sum with sign-pattern masking), while the three-layer standard program optimizes over composed functions $W_2 \cdot \text{ReLU}(W_1 \cdot \text{ReLU}(W_0 x))$.

2. A function representable by the three-layer composition is not, in general, representable by any function in the two-layer class. The two-layer class uses absolute maximum width $P$ (number of patterns) while the three-layer class uses two sequential nonlinear maps; neither contains the other.

3. The rescaling lemma from Pilanci and Ergen (2020) [PilanciErgen2020] is derived for matched (same depth) architectures: it converts the two-layer $\ell_2^2$ primal into the two-layer group-$\ell_1$ dual by exploiting the positive homogeneity of ReLU applied once. Applying this lemma across depth boundaries—converting the three-layer $\ell_2^2$ primal to a two-layer group-$\ell_1$ program—has no theoretical justification.

This error is natural to make: the parallel-architecture zero-gap theorem is stated in a way that might suggest the parallel program is universally "below" any standard architecture program. The theorem only guarantees that the parallel program achieves its own global optimum; it makes no claim about the relative values of different programs.

### D. H6 Ablation Findings

The H6 ablation used a two-layer ReLU ($d=10 \to \text{width}=100 \to 1$, $n=200$, $\beta=0.01$) with $P=200$ randomly sampled sign patterns. The $\ell_2^2$ control (pure weight decay, no elastic net) should have shown gap $< 1\%$ between the convex SCNN objective and the non-convex Adam objective. Instead, the observed gap was approximately 89%.

The explanation: with width 100 and $n=200$, the network is overparameterized. The non-convex optimizer trains in a high-dimensional space of activation patterns; the convex program, restricted to 200 randomly sampled patterns, occupies a small subspace. The two programs are not computing the same thing. In the underparameterized regime (width $\ll n$), the network's expressiveness is limited, fewer distinct activation patterns arise during training, and a random sample of 200 patterns is more likely to cover those that actually matter.

The reviewer's proposed fix—width 10, pattern count 500, 200 restarts—directly addresses this by moving into the underparameterized regime where the convex program's restricted pattern set is more representative. This fix was not implemented in this pipeline run but is well-specified for a future reiteration.
