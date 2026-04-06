---
title: "Dual Convex Optimization in ReLU Neural Networks: A Research Agenda"
date: 2026-04-06
topic: Dual Convex Optimization in ReLU Neural Networks
pipeline_run: run-01/convex-nn
---

# Dual Convex Optimization in ReLU Neural Networks: A Research Agenda

---

## Executive Summary

Training ReLU neural networks is, on its face, a non-convex optimization problem. The piecewise-linear structure of the rectified linear unit introduces an exponential number of linear regions, and the multiplicative interaction between layers renders gradient-based convergence guarantees fragile. The prevailing practice — stochastic gradient descent and its variants — works empirically but provides no polynomial-time guarantee of reaching the global minimum.

A line of work initiated by Pilanci and Ergen [Pilanci&Ergen2020] overturns this picture for regularized networks. The central result is that training a two-layer ReLU network with weight-decay regularization is *exactly equivalent* to solving a finite convex program — a group-sparse linear model indexed by hyperplane arrangement patterns — and that this equivalence is tight (zero duality gap) whenever the network is wide enough, which requires at most $n+1$ hidden units for $n$ training samples. By 2024, the framework has been extended to deep parallel architectures [Ergen&Pilanci2021global; Wang&Ergen&Pilanci2023], structurally characterized [Ergen&Pilanci2021reveal], scaled to ImageNet resolution via a GPU-accelerated ADMM solver [Feng&Frangella&Pilanci2023], and furnished with a polynomial-time approximation guarantee under Gaussian data [Kim&Pilanci2024].

Three open problems dominate the frontier. First, the zero-duality-gap result does not extend to standard (non-parallel) deep ReLU networks with $L \geq 3$ layers and general data — the duality gap formula for this case is explicitly marked as "Not Proven" in [Wang&Ergen&Pilanci2023]. Second, the only polynomial-time $O(\sqrt{\log n})$ relative error bound [Kim&Pilanci2024] assumes Gaussian i.i.d. data; whether it holds for structured, non-Gaussian distributions (e.g., those satisfying restricted isometry) is unresolved. Third, CRONOS-AM — the practical deep-network solver — lacks end-to-end convergence guarantees for its alternating minimization procedure [Feng&Frangella&Pilanci2023].

This document proposes seven hypotheses to address these gaps, organized into three primary (Tier 1) hypotheses and four secondary (Tier 2) hypotheses. The primary hypotheses are: (H1) for rank-1 data and $L=3$, the duality gap of a standard ReLU network is zero if and only if the post-first-ReLU effective data matrix satisfies an equal-singular-values condition; (H2) the $O(\sqrt{\log n})$ bound extends to any data satisfying the restricted isometry property on the hyperplane arrangement feature map; and (H3) CRONOS-AM satisfies monotone Lyapunov descent when early-layer step sizes are bounded by a gradient-norm-scaled tolerance $\varepsilon$. An experimental program of seven experiments — three theoretical proof-plus-validation studies and four empirical benchmarks — is specified for all seven hypotheses.

---

## 1. Literature Review

### 1.1 The Non-Convex Barrier and Its Circumvention

The standard two-layer network training problem is:

$$p^* := \min_{\{u_j, \alpha_j\}_{j=1}^m} \frac{1}{2}\left\|\sum_{j=1}^m (Xu_j)_+ \alpha_j - y\right\|_2^2 + \frac{\beta}{2}\sum_{j=1}^m(\|u_j\|_2^2 + \alpha_j^2)$$

where $X \in \mathbb{R}^{n \times d}$, $y \in \mathbb{R}^n$, $(t)_+ = \max(t, 0)$, and $\beta > 0$ is the weight-decay parameter [Pilanci&Ergen2020]. The products $u_j^T x_i$ inside the ReLU create the non-convexity responsible for the difficulty of the general problem.

The circumvention discovered by Pilanci and Ergen is a two-step duality argument. The first step exploits a rescaling equivalence: squared weight decay on $(u_j, \alpha_j)$ is equivalent to an $\ell_1$ penalty on the output weights $\alpha_j$ with the hidden weights $u_j$ constrained to the unit sphere [Pilanci&Ergen2020]. The second step takes the Lagrangian dual with respect to the output weights $\alpha_j$ to obtain a semi-infinite dual problem:

$$d^* := \max_{v \in \mathbb{R}^n} -\frac{1}{2}\|y - v\|_2^2 + \frac{1}{2}\|y\|_2^2 \quad \text{s.t.} \quad |v^T(Xu)_+| \le \beta \;\; \forall u \in \mathcal{B}_2$$

This dual is convex in $v$ but has infinitely many constraints — one for each unit-norm direction $u$. The decisive technical step is showing that this infinite constraint set is determined by *hyperplane arrangement diagonal matrices* $D_i = \text{diag}(\mathbf{1}[Xu_i \geq 0])$: patterns recording which neurons activate for a given weight vector $u_i$. For data of rank $r$, the number of distinct patterns is at most $P = O((n/r)^r)$ [Pilanci&Ergen2020]. The resulting **finite** convex program has $2dP$ variables and $2nP$ constraints, and can be solved in $O(d^3 r^3 (n/r)^{3r})$ time — polynomial for fixed rank $r$.

**Strong duality** $p^* = d^*$ follows from an application of Carathéodory's theorem to the bi-dual, which is an infinite-dimensional total-variation minimization problem over Radon measures on the unit sphere. The theorem guarantees the bi-dual is attained at a sparse measure supported on at most $n+1$ atoms, which corresponds to a network with at most $n+1$ hidden units [Pilanci&Ergen2020]. Geometrically, the minimum-norm interpolant is the gauge function of the convex hull of the *rectified ellipsoid* $\mathcal{Q}_X = \{(Xu)_+: \|u\|_2 \leq 1\}$ [Pilanci&Ergen2020].

### 1.2 Deep and Parallel Architectures

The two-layer result does not extend directly to sequential deep networks, because composing ReLU layers produces tensor-product interactions between activation patterns at each layer that have no natural convex analog. Two distinct research threads address this.

The first, due to Ergen and Pilanci [Ergen&Pilanci2021global], considers architectures with $K$ *parallel* three-layer ReLU sub-networks trained with group-$\ell_{2,1}$ regularization. The key observation is that the training loss for this ensemble is jointly convex in the output of each sub-network's first layer, and the dualization proceeds as before. The resulting convex program involves feature maps of the form $D_{2,l}D_{1,ij}X$ — products of two diagonal activation matrices — indexed by pairs of hyperplane arrangements from the two ReLU layers [Ergen&Pilanci2021global]. Strong duality holds when $K \geq n+1$ sub-networks are used, proven via the same Carathéodory argument applied to the bi-dual over pairs of patterns [Ergen&Pilanci2021global]. ResNets appear as a special case: setting $K=2$ with the identity shortcut reduces the architecture to a standard residual block [Ergen&Pilanci2021global].

The second thread, due to Wang, Ergen, and Pilanci [Wang&Ergen&Pilanci2023], provides a complete taxonomy of which architectures admit zero duality gap. For **standard deep linear networks** with $L \geq 3$ layers, the duality gap is provably non-zero whenever the singular values of the effective data matrix $X^\dagger Y$ are not all equal. The gap formula depends on the Schatten-$2/L$ quasi-norm: the primal optimal value is $\|W\|_{S_{2/L}}^{2/L}$ while the dual optimal value involves the nuclear norm, and these coincide only when all singular values are equal [Wang&Ergen&Pilanci2023]. For general singular value distributions, depth strictly increases the regularization effect, amplifying low-rank implicit bias. The closed-form optimal weight matrices are $W_l^* = U_{l-1}\Sigma^{1/L}U_l^T$ where the matrices $U_l$ are orthonormal and $\Sigma$ comes from the SVD of $X^\dagger Y$ [Wang&Ergen&Pilanci2023].

For **standard deep ReLU networks** with $L \geq 3$ and general data, the duality gap remains uncharacterized: [Wang&Ergen&Pilanci2023] Table 1 explicitly marks this case as "Not Proven." The zero-gap case is resolved only for rank-1 data (scalar outputs), while **parallel** deep ReLU networks at any depth $L$ admit zero duality gap with appropriate regularization [Wang&Ergen&Pilanci2023]. The central technical insight connecting the two cases is a bi-dual equivalence: the bi-dual of the standard deep network's minimum-norm problem equals the minimum-norm problem for a parallel architecture, so the duality gap measures the cost of parallelism [Wang&Ergen&Pilanci2023].

### 1.3 Structural Characterization of Optimal Weights

Given that the convex reformulation can be solved globally, a natural follow-up is: what do the resulting primal (network weight) solutions look like? Ergen and Pilanci [Ergen&Pilanci2021reveal] characterize the optimal weights via dual optimality conditions.

The main structural result is that the optimal hidden layer weights are the *extreme points of a convex set determined by the dual solution* [Ergen&Pilanci2021reveal]. Dual optimality conditions identify the active constraints — the hyperplane arrangements that carry nonzero dual weight — and the weight vectors $u_j^*$ at the primal solution are precisely the unit-norm vectors realizing these active arrangements. This converts the non-convex primal problem into a structured extraction: solve the convex dual, identify active patterns, read off the primal weights.

For rank-1 or whitened data, optimal weights obey an exact **alignment property**: the singular vectors of $W_l^*$ match those of the adjacent layer's weights, i.e., $W_l^* = U_{l-1}\Sigma^{1/L}U_l^T$ [Wang&Ergen&Pilanci2023; Ergen&Pilanci2021reveal]. For one-dimensional or rank-1 data at any depth, the optimal neural network function is the linear spline interpolator — piecewise linear, regardless of depth — extending results from two-layer networks to all depths [Ergen&Pilanci2021reveal].

A structurally striking corollary involves batch normalization. When batch normalization is applied before the final linear layer, it acts as a whitening transform on the intermediate representations, removing the rank-1 or whitened-data restriction from the structural results. This BN-induced whitening, combined with weight-decay regularization, forces the class means to collapse to a *simplex equiangular tight frame* (ETF): the most spread-out geometric configuration of $K$ points in $K-1$ dimensions [Ergen&Pilanci2021reveal]. This provides the first theoretical explanation of **neural collapse** — the empirically observed convergence of class representations to an ETF structure in the late stages of training — deriving it as a consequence of dual optimality under BN and weight decay [Ergen&Pilanci2021reveal].

Throughout this structural analysis, a recurring theme is that weight decay — a simple isotropic prior over parameters — induces **group sparsity** in the convex-equivalent feature space. In the two-layer case, the group-$\ell_1$ regularizer selects a sparse subset of hyperplane arrangement patterns; in the three-layer case, the group-$\ell_{2,1}$ norm selects a sparse subset of sub-networks [Ergen&Pilanci2021global]. This is an exact equivalence, not an approximation [Pilanci&Ergen2020].

### 1.4 Computational Tractability: From Theory to GPU Scale

The exact convex reformulation of [Pilanci&Ergen2020] has $O((n/r)^r)$ variables — exponential in the data rank $r$ — making it intractable for full-rank datasets. Two tracks address this in parallel.

The first track, formalized by Kim and Pilanci [Kim&Pilanci2024], samples $m = O(\log n)$ hyperplane arrangement patterns from random Gaussian vectors $g_i \sim \mathcal{N}(0, I_d)$ rather than enumerating all $P = O((n/r)^r)$ patterns. The resulting smaller convex program is solvable in polynomial time. Under the Gaussian data assumption (A1), with $m = \kappa\max\{m^*, O(\log n)\}$ sampled patterns, the relative optimality gap satisfies $p^* \leq \tilde{p}^* \leq C\sqrt{\log 2n} \cdot p^*$ with high probability [Kim&Pilanci2024]. This is the first polynomial-time approximation guarantee for regularized ReLU networks; the dependence on $\log n$ is essentially tight given the NP-Hardness of unregularized training [Kim&Pilanci2024]. A coupling lemma further implies that SGD stationary points — reached by standard gradient descent with random initialization — achieve $O(\sqrt{\log n})$ relative training error with respect to the true global minimum [Kim&Pilanci2024].

The second track, pursued by Feng, Frangella, and Pilanci [Feng&Frangella&Pilanci2023], develops a GPU-accelerated solver called **CRONOS**. The convex program is reformulated as a linearly constrained generalized linear model with group lasso structure (Proposition 3.1), then solved with the Alternating Direction Method of Multipliers (ADMM). The key algorithmic contribution is **Nyström preconditioning** of the conjugate gradient sub-solver: standard CG requires $O(\kappa)$ iterations proportional to the condition number $\kappa$ of the data kernel; Nyström approximation of the dominant kernel subspace reduces this to $O(\log(1/\delta))$ iterations independent of $\kappa$ [Feng&Frangella&Pilanci2023]. Implemented in JAX with JIT compilation on a single RTX-4090, CRONOS achieves the first successful application of convex neural network training to ImageNet-scale data ($512 \times 512 \times 3$ images) and IMDb text classification [Feng&Frangella&Pilanci2023]. For deeper networks, **CRONOS-AM** alternates between CRONOS applied to the last two convex layers and DAdapted-Adam applied to earlier non-convex layers, matching or exceeding tuned SGD/Adam on held-out accuracy [Feng&Frangella&Pilanci2023].

### 1.5 Relationship to Adjacent Frameworks

The neural tangent kernel (NTK) framework [Jacot et al. 2018; Lilianweng2022] provides an alternative account of neural network training: in the infinite-width limit, gradient dynamics become linear and the network engages in *lazy training* — its weights change negligibly from initialization, and the effective model is a kernel machine with the NTK as its kernel. The convex duality approach makes a fundamentally different prediction: at any finite width, training selects a sparse subset of hyperplane arrangement patterns from the exponentially large library, and this feature selection is the mechanism behind neural networks' modeling capacity [Pilanci&Ergen2020]. The NTK explanation, which cannot capture this finite-width feature learning, is explicitly identified as insufficient in [Pilanci&Ergen2020], which states that "the kernel approximation as the width tends to infinity is unable to fully explain the success of non-convex neural network models." Empirically, [Ergen&Pilanci2021global] shows that the loss landscape becomes progressively more convex as the number of parallel sub-networks increases (Figure 2), consistent with the convex duality prediction at finite widths — but no large-scale empirical comparison of the two frameworks' representational predictions exists in the corpus.

---

## 2. Key Paper Summaries

### [Pilanci&Ergen2020] — Neural Networks are Convex Regularizers

**Pilanci & Ergen. ICML 2020 (arXiv 2002.10553).**

The founding paper proves that training a two-layer ReLU network with weight-decay regularization equals a finite group-sparse convex program parameterized by hyperplane arrangement diagonal matrices $D_i = \text{diag}(\mathbf{1}[Xu_i \geq 0])$. The central theorem establishes strong duality ($p^* = d^*$) via Carathéodory's theorem applied to the total-variation bi-dual; the minimal sufficient network width is $m^* \leq n+1$. Computational complexity is $O(d^3r^3(n/r)^{3r})$ for data of rank $r$. The convex equivalent is a group-lasso in a high-dimensional feature space, providing the first exact polynomial-time training algorithm for regularized two-layer ReLU networks. A limitation, acknowledged in the paper, is that the exponential dependence on rank $r$ renders the exact reformulation intractable for full-rank data; this motivates subsequent approximation work.

---

### [Ergen&Pilanci2021global] — Global Optimality Beyond Two Layers

**Ergen & Pilanci. ICML 2021 (arXiv ergen21b).**

Extends the convex reformulation to $K$ parallel three-layer ReLU sub-networks with group-$\ell_{2,1}$ regularization. The equivalent convex program involves feature maps $D_{2,l}D_{1,ij}X$ — products of two diagonal activation matrices indexing pairs of hyperplane arrangements. Strong duality holds when $K \geq n+1$. A key structural insight is that ResNets are a special case ($K=2$, identity shortcut). The implicit regularization is group $\ell_1$: weight decay in parameter space maps to group-lasso in the arrangement-pair feature space, selecting a minimal set of sub-network patterns. Loss landscape convexity increases with $K$ (Figure 2 experiment). The result applies to ensemble (parallel) architectures only; the standard sequential three-layer case is not covered.

---

### [Wang&Ergen&Pilanci2023] — Parallel Deep Neural Networks Have Zero Duality Gap

**Wang, Ergen & Pilanci. ICLR 2023 (arXiv 2110.06482v3).**

Provides Table 1, the first complete taxonomy of duality gaps across architecture types. Standard deep linear networks with $L \geq 3$ layers have a provably non-zero duality gap whenever the singular values of $X^\dagger Y$ are unequal; the gap formula is expressed via the Schatten-$2/L$ quasi-norm. Parallel architectures at any depth $L$ have zero duality gap. The optimal standard linear network weights are $W_l^* = U_{l-1}\Sigma^{1/L}U_l^T$ in closed form. The status of standard deep ReLU networks with $L \geq 3$ and non-rank-1 data is explicitly marked "Not Proven" in Table 1, defining the primary open problem in the field.

---

### [Ergen&Pilanci2021reveal] — Revealing the Structure of Deep Neural Networks via Convex Duality

**Ergen & Pilanci. NeurIPS 2021 (arXiv 2110.05518v2).**

Uses dual optimality conditions to prove that optimal hidden weights are extreme points of a convex set determined by the dual solution, establishing the **weight alignment** property: optimal weight matrices share singular vector structure across layers. For rank-1 or 1D data at any depth, the optimal network function is the linear spline interpolator. Batch normalization before the final layer whitens intermediate representations, rendering exact structural results data-distribution-agnostic. A corollary is neural collapse: BN + weight decay forces class means to a simplex equiangular tight frame at convergence, providing the first theoretical derivation of this empirically observed phenomenon. The BN results apply only to the last linear layer; the full multi-layer BN case is not resolved.

---

### [Feng&Frangella&Pilanci2023] — CRONOS: Scalable GPU-Accelerated Convex Neural Networks

**Feng, Frangella & Pilanci. NeurIPS 2023 (arXiv 8652_CRONOS).**

Introduces CRONOS, the first convex neural network solver to scale to ImageNet ($512 \times 512 \times 3$ images) and IMDb text classification. Reformulates the convex program as a linearly constrained group-lasso and applies ADMM with Nyström preconditioning, reducing CG iterations from $O(\kappa)$ (condition number dependent) to $O(\log(1/\delta))$ (condition number independent). CRONOS-AM extends this to arbitrary-depth networks via alternating minimization, interleaving CRONOS for the last two convex layers with DAdapted-Adam for earlier layers. Theorem 6.4 proves CRONOS converges to the global convex minimum; no end-to-end guarantee exists for CRONOS-AM, which the authors explicitly flag as future work.

---

### [Kim&Pilanci2024] — Convex Relaxations Approximate Global Optima in Polynomial Time

**Kim & Pilanci. ICML 2024 (arXiv 2402.03625v3).**

Proves the first polynomial-time approximation guarantee for regularized ReLU network training. Under Gaussian i.i.d. data (Assumption A1) with $n/d \geq 1$, sampling $m = O(\log n)$ hyperplane arrangement patterns from random Gaussian vectors yields a convex relaxation with relative optimality gap at most $C\sqrt{\log(2n)} \cdot p^*$ with high probability. The proof uses Gordon's comparison inequality and a cone-sharpness bound. A coupling lemma further shows that SGD stationary points correspond to global minima of the Gaussian-relaxed program, implying that SGD with random initialization achieves $O(\sqrt{\log n})$ relative training error. The Gaussian assumption is acknowledged as a limitation; the RIP connection is identified as the natural extension path.

---

### [Lilianweng2022] — Some Math behind Neural Tangent Kernel

**Lilian Weng. Blog post, 2022.**

An accessible exposition of the NTK framework: in the infinite-width limit, gradient descent dynamics linearize around initialization, the NTK becomes a deterministic fixed kernel, and the network engages in lazy training with no feature learning. This framing contextualizes the contrast with the convex duality approach, which predicts active feature selection via group-sparse arrangement patterns at any finite width. The blog highlights the strength of NTK (guaranteed convergence in the infinite-width limit) and its principal weakness (the lazy training assumption does not capture finite-width feature learning), motivating the alternative convex duality account.

---

## 3. Research Gap Analysis

### Tier 1 Gap Scoring

| Gap ID | Description | Confidence | Impact | Feasibility | Verifiability | Total | Tier |
|--------|-------------|:----------:|:------:|:-----------:|:-------------:|:-----:|:----:|
| 1.1 | Duality gap formula, standard deep ReLU ($L \geq 3$, general data) | 3/3 | 3/3 | 2/3 | 3/3 | **11/12** | **1** |
| 1.2 | Poly-time $O(\sqrt{\log n})$ bound for non-Gaussian data | 3/3 | 3/3 | 2/3 | 3/3 | **11/12** | **1** |
| 1.3 | End-to-end convergence guarantees for CRONOS-AM | 3/3 | 2/3 | 2/3 | 3/3 | **10/12** | **1** |
| 2.1 | Layer-wise BN integration with full convex duality | 2/3 | 3/3 | 2/3 | 2/3 | 9/12 | 2 |
| 2.2 | Poly-time approximation for non-squared losses | 2/3 | 2/3 | 2/3 | 3/3 | 9/12 | 2 |
| 2.3 | NTK vs. convex duality mechanistic probe (CIFAR-10 scale) | 2/3 | 3/3 | 2/3 | 2/3 | 9/12 | 2 |
| 2.4 | Minimal structural conditions restoring zero gap | 2/3 | 3/3 | 2/3 | 2/3 | 9/12 | 2 |

### Gap 1.1 — Duality Gap Characterization for Standard Deep ReLU Networks ($L \geq 3$)

This is the primary open problem in the field. For standard (non-parallel) deep ReLU networks with three or more layers and general (non-rank-1) data, neither the zero-gap condition nor an explicit duality gap formula has been proven. [Wang&Ergen&Pilanci2023] Table 1 marks the entry for "standard deep ReLU, $L \geq 3$" explicitly as "Not Proven." The abstract states: *"extending this result to deeper networks remains to be an open problem."* The same paper proves the non-zero gap only for deep *linear* networks, and proves zero gap only for the rank-1 scalar-output case of standard three-layer ReLU — leaving the general case entirely open [Wang&Ergen&Pilanci2023]. The contrast with the parallel architecture result makes the gap structural: it is full parallelism that enables zero-gap convex equivalence, and identifying the minimal architectural condition weaker than full parallelism that still admits zero gap requires resolving this problem.

The Phase 5 advisory note flags that the full general case (arbitrary $L$, arbitrary rank) may require a decade-scale research program; the feasibility score 2/3 applies to the restricted sub-case of rank-1 data and $L=3$, which is the actionable near-term target. The bi-dual equivalence between standard and parallel architectures, proven for linear networks in [Wang&Ergen&Pilanci2023], provides the technical scaffold: showing that the bi-dual of the standard three-layer ReLU problem equals a parallel three-layer problem, then deriving the gap as the difference in optimal values.

**Note:** Gap 2.4 (minimal conditions restoring zero gap) is a sub-problem of Gap 1.1 — the zero-gap condition is precisely the formula from Gap 1.1 set to zero. Both are addressed by the same research thread (Hypothesis H1).

### Gap 1.2 — Polynomial-Time Approximation Guarantees for General (Non-Gaussian) Data

The $O(\sqrt{\log n})$ relative optimality bound of [Kim&Pilanci2024] rests on Assumption (A1): $X_{ij} \sim \mathcal{N}(0, 1)$ i.i.d. The paper states this assumption explicitly: *"we assume that the data distribution follows $X_{ij} \sim \mathcal{N}(0,1)$ i.i.d., $n/d = c \geq 1$"* and adds *"here, we assume Gaussianity for simplicity"* [Kim&Pilanci2024]. The proof technique — Gordon's comparison inequality applied to the cone sharpness constant — depends on Gaussianity through the Gaussian minimax theorem. All practical datasets (MNIST, CIFAR, ImageNet) are manifestly non-Gaussian; the empirical success of CRONOS on ImageNet [Feng&Frangella&Pilanci2023] is therefore unaccompanied by theoretical coverage.

The RIP extension path is explicitly identified by the authors: *"a connection to restricted isometry property could be a key to extending the result to different distributions"* [Kim&Pilanci2024]. The key technical step is bounding $\lambda_{\min}$ of the Gram matrix of the hyperplane arrangement feature map $\Phi$; RIP of order $s$ on $\Phi$ directly provides a $\lambda_{\min} \geq 1-\delta$ lower bound, which is the quantity Gordon's inequality needs. Alternatively, Mendelson (2007) provides an empirical process bound applicable to sub-Gaussian distributions without Gordon's inequality, offering a fallback route.

### Gap 1.3 — End-to-End Convergence Guarantees for CRONOS-AM

CRONOS (the two-layer convex solver) has a proven convergence guarantee: Theorem 6.4 in [Feng&Frangella&Pilanci2023] establishes convergence to the global minimum of the convex reformulation under mild assumptions. CRONOS-AM, which handles deeper networks by alternating between CRONOS (last two layers) and DAdapted-Adam (earlier layers), has no such guarantee. The paper's future work section raises this explicitly: *"Can we provide a convergence guarantee for CRONOS-AM that shows an advantage over stochastic first-order methods?"* [Feng&Frangella&Pilanci2023]. Alternating minimization on jointly non-convex objectives is known to get stuck at stationary points [Bai et al. 2023, cited in Feng&Frangella&Pilanci2023]; the DAdapted-Adam update's effect on the convex sub-problem's feasibility constraints is the critical uncontrolled quantity.

The Phase 5 advisory notes that this gap's impact is somewhat lower than Gaps 1.1 and 1.2: a theoretical guarantee for CRONOS-AM would not change empirical practice substantially, since CRONOS already matches SGD/Adam on ImageNet accuracy. The gap is nonetheless genuine and the Lyapunov approach is the correct framing for the near-term hypothesis.

### Tier 2 Gaps (Brief)

**Gap 2.1 — Layer-wise BN integration.** [Ergen&Pilanci2021reveal] establishes BN results only for "*the last linear layer with BN*"; extending the full convex duality framework — hyperplane arrangement parameterization, group-sparse equivalent program, strong duality — to architectures with BN at every intermediate layer is partially open. The key technical obstacle is that BN introduces inter-sample coupling (normalization over the batch) that breaks the independent per-sample structure used in the semi-infinite duality derivation.

**Gap 2.2 — Non-squared loss approximation.** [Pilanci&Ergen2020] extends the *exact* convex reformulation to arbitrary convex losses (Appendix A.7: "*All of our results immediately extend to vector outputs, tensor inputs, arbitrary convex classification and regression loss functions*"). [Kim&Pilanci2024] restricts the *polynomial-time approximation guarantee* exclusively to squared loss. No equivalent of Theorem 2.1 for logistic or hinge loss appears in the corpus.

**Gap 2.3 — NTK vs. convex duality at CIFAR-10 scale.** The NTK and convex duality frameworks make opposite predictions about what networks learn: NTK predicts lazy training and high CKA alignment with the initialization kernel; convex duality predicts active hyperplane arrangement selection and sparse dual support. No large-scale empirical test of these predictions using modern representational similarity tools exists in the corpus. The Phase 5 advisory rescopes this from ImageNet to CIFAR-10, where [Ergen&Pilanci2021reveal] already validates the $L=3$ convex program implementation.

**Gap 2.4 — Minimal structural conditions for zero gap.** [Wang&Ergen&Pilanci2023] shows that full parallelism is *sufficient* for zero gap at any depth. The minimal sufficient condition — weaker than full parallelism but stronger than sequential depth — is not characterized for ReLU networks. The linear network case provides a hint: equal singular values of $X^\dagger Y$ is the threshold, suggesting data-dependent rather than purely architectural conditions govern the gap. This gap is addressed jointly with Gap 1.1 in Hypothesis H1.

### Rejected Candidates

**Multi-class / vector output for exact two-layer reformulation:** Addressed in the founding paper. [Pilanci&Ergen2020] Appendix A.7 proves the exact reformulation extends immediately to vector outputs and arbitrary convex losses.

**Extension to non-ReLU activations (GELU, SiLU):** The restriction to ReLU is load-bearing — the hyperplane arrangement construction depends on ReLU's piecewise-linear indicator structure. This is a deliberate architectural assumption enabling the framework, not an oversight or gap.

**Larger benchmarks for CRONOS:** CRONOS already reports ImageNet-scale results. Scaling to larger data is a compute/engineering question, not a theoretical gap.

---

## 4. Research Hypotheses

### H1 (Tier 1, Primary): Zero-Gap Singular-Value Condition for Standard Three-Layer ReLU

**Source gaps:** Gap 1.1 + Gap 2.4 (merged per Phase 5 advisory)

**Statement.** For a standard (non-parallel) three-layer ReLU network trained on a rank-1 data matrix $X = \mathbf{x}\mathbf{y}^T \in \mathbb{R}^{n \times d}$ with squared-loss weight-decay regularization, the duality gap $p^* - d^*$ is zero if and only if the post-first-ReLU effective data matrix $\widetilde{X} = D_1 X$ satisfies an equal-singular-values condition on the subspace relevant to the output layer — analogously to the exact characterization proven for deep linear networks in [Wang&Ergen&Pilanci2023].

**Rationale.** The linear network duality gap formula in [Wang&Ergen&Pilanci2023] depends on whether the Schatten-$2/L$ quasi-norm equals the nuclear norm; this holds iff the singular values of $X^\dagger Y$ are all equal. The bi-dual equivalence between standard and parallel architectures is proven for linear networks in the same paper; this hypothesis posits that restricting to rank-1 data tames the tensor-product interaction between successive ReLU layers enough to permit a direct transfer of the equal-singular-values criterion. The Carathéodory bound $m^* \leq n+1$ (established in [Pilanci&Ergen2020]) guarantees bi-dual attainment, which is the starting point for the gap formula derivation.

**Measurable prediction.** Constructing the convex reformulation for rank-1, $L=3$ standard ReLU instances and computing primal-dual pairs via CVXPY for small $(n, d)$ (e.g., $n = 20, d = 5$) should yield duality gap = 0 precisely when the equal-singular-values condition on $\widetilde{X}$ holds, across $\geq 200$ random instances. The gap should be expressible as a closed-form function of the deviation from equal singular values.

**Falsification.** A rank-1, $L=3$ instance where the gap is zero despite unequal singular values of $\widetilde{X}$, or nonzero despite equal singular values, would falsify the hypothesis. A finding that the gap depends on a different structural quantity (e.g., arrangement pattern count rather than singular value equality) would require revision.

---

### H2 (Tier 1, Primary): $O(\sqrt{\log n})$ Bound Extends to RIP-Satisfying Data

**Source gap:** Gap 1.2

**Statement.** The $O(\sqrt{\log n})$ relative optimality bound of [Kim&Pilanci2024] for the convex relaxation of two-layer ReLU network training extends from Gaussian i.i.d. data to any data matrix $X \in \mathbb{R}^{n \times d}$ satisfying $(s, \delta)$-restricted isometry property on the hyperplane arrangement feature map $\Phi: \mathbb{R}^d \to \mathbb{R}^P$ with $\delta < 1/2$, achieving the same $O(\log n)$ relaxation width and $O(\sqrt{\log n})$ relative error with an RIP-dependent constant $C(\delta)$.

**Rationale.** Gordon's comparison inequality in [Kim&Pilanci2024] Lemma 21 requires bounding $\lambda_{\min}(\mathcal{M})$ — the minimum eigenvalue of the arrangement feature map's Gram matrix. RIP with parameter $\delta < 1/2$ directly implies $\lambda_{\min}(\Phi^T\Phi) \geq 1-\delta > 1/2$ for sparse subsets of arrangement patterns; substituting this into the cone-sharpness bound yields the same $O(\sqrt{\log n})$ rate [Kim&Pilanci2024]. The paper's explicit suggestion — *"a connection to restricted isometry property could be a key to extending the result to different distributions"* — identifies this as the authors' own intended extension path.

**Measurable prediction.** For data matrices drawn from Bernoulli$(\pm 1)$ distributions (sub-Gaussian, satisfies RIP with high probability for $d = O(s \log n)$), the relative optimality gap $(\tilde{p}^* - p^*)/p^*$ for an $O(\log n)$-width relaxation should scale as $O(\sqrt{\log n})$ with $n$, matching the Gaussian baseline slope in a log-log regression ($\leq 0.6$) across $n \in \{50, 100, 200, 500, 1000\}$.

**Falsification.** A Bernoulli data matrix verified to satisfy RIP with $\delta < 1/2$ on the arrangement feature map, yet exhibiting $\omega(\sqrt{\log n})$ relative gap scaling, would falsify the hypothesis.

---

### H3 (Tier 1, Secondary): CRONOS-AM Satisfies Monotone Lyapunov Descent Under Bounded Step Size

**Source gap:** Gap 1.3

**Statement.** When CRONOS-AM's early-layer DAdapted-Adam step size satisfies $\eta_t \leq \varepsilon / \|\nabla \mathcal{L}_t\|$ for a feasibility-disturbance tolerance $\varepsilon > 0$, the optimal value of the CRONOS-solved convex sub-problem $f_t^*$ decreases weakly monotonically across alternating minimization iterations, establishing a Lyapunov descent certificate for at least $90\%$ of iterations across UCI regression benchmarks.

**Rationale.** [Feng&Frangella&Pilanci2023] explicitly asks whether a convergence guarantee for CRONOS-AM can be proven. The Lyapunov strategy applies to two-block alternating minimization where one block is convex (CRONOS) and one is not (DAdapted-Adam). The step-size bound $\eta_t \leq \varepsilon / \|\nabla \mathcal{L}_t\|$ limits the shift in the effective data distribution presented to the convex sub-problem to $\varepsilon$ in gradient-norm units, potentially ensuring the sub-problem's optimal value cannot increase. The theoretical scaffold follows Xu & Yin (2013) for block coordinate descent with mixed convex/non-convex structure.

**Measurable prediction.** On UCI Concrete, Energy, and Wine datasets ([Feng&Frangella&Pilanci2023] Table 2), the CRONOS sub-problem optimal value trace $\{f_t^*\}$ should be non-increasing in $\geq 90\%$ of iterations under the bounded step-size rule, with monotonicity violated at most by discrete solver noise of $< 10^{-6}$ relative.

**Falsification.** Any dataset / $\varepsilon$ combination where $f_t^*$ increases across $>3$ consecutive iterations by a net amount $> 0.1\%$ relative, while the bounded step-size rule is satisfied, falsifies the Lyapunov property.

---

### H4 (Tier 2): Generalization Bound from Carathéodory Complexity $k^*$

**Source gap:** Phase 5 Missing Gap A (absent from corpus; identified as high-impact by Phase 5 advisory)

**Statement.** A two-layer ReLU network trained to the global minimum of the weight-decay-regularized convex program achieves test error bounded by $O(\sqrt{k^*/n})$, where $k^* \leq n+1$ is the number of active hyperplane arrangement patterns in the group-sparse dual solution (Carathéodory bound), derived via a compression argument treating the dual-selected arrangement patterns as the effective hypothesis class.

**Rationale.** The Carathéodory bound $m^* \leq n+1$ is established in [Pilanci&Ergen2020], and [Kim&Pilanci2024] notes empirically that *"$m^*$ is much smaller than $n+1$ in practice."* A network supported on $k^*$ patterns from the $P$-pattern library is a compressed model with $O(k^* d)$ effective parameters. Compression-based generalization bounds (Arora et al. 2018) yield test error $O(\sqrt{(\text{description length})/n})$; the description length here is $k^* d$, giving the stated $O(\sqrt{k^*/n})$ rate up to logarithmic factors.

**Measurable prediction.** Across a $(n, r, \beta)$ grid with $n \in \{50, 100, 200, 500\}$, Spearman correlation between empirical test MSE and $\sqrt{k^*/n}$ should exceed $\rho > 0.7$, with log-log slope close to 0.5. For $k^* < n/4$ cells, the bound should be within $2\times$ the empirical test error using an OLS-calibrated constant.

**Falsification.** $\rho < 0.3$ across the grid, or $k^*/n \to 1$ universally (making the bound vacuous), would falsify the hypothesis.

---

### H5 (Tier 2): Fixed-Point BN Admits a Convex Equivalent with BN-Adjusted Group-Norm Regularizer

**Source gap:** Gap 2.1

**Statement.** When batch normalization is evaluated at its running-statistics fixed point, the BN normalization acts as an affine transformation $\text{BN}(X) = \hat{\sigma}^{-1}(X - \hat{\mu}\mathbf{1}^T)$ of the data matrix, and the resulting training problem is equivalent to the standard convex program of [Pilanci&Ergen2020] with $\text{BN}(X)$ substituted for $X$, with strong duality preserved.

**Rationale.** At the fixed point, BN is a linear operator on the data matrix, preserving the per-sample independence structure that the semi-infinite duality derivation requires. The only change to the convex program is that the effective data matrix is $\hat{X} = \text{BN}(X)$ rather than $X$; the hyperplane arrangement structure, group-norm regularizer, and Carathéodory bi-dual argument are unchanged [Ergen&Pilanci2021reveal]. The fixed-point condition is the key: online (non-converged) BN introduces dynamic statistics that do couple samples and would break the duality.

**Measurable prediction.** For $n=50$, $d=10$, training a two-layer ReLU network with fixed-point BN via 10 random SGD initializations should yield a best training loss matching the CVXPY convex program's global minimum (with $\hat{X}$ as data) to within $10^{-4}$ absolute, with primal-dual gap $< 10^{-6}$.

**Falsification.** A gap $> 0.1\%$ relative between best-of-SGD and CVXPY convex minimum, replicated across all 10 initializations, would indicate the fixed-point substitution breaks duality.

---

### H6 (Tier 2): Self-Concordance Extends the $O(\sqrt{\log n})$ Bound to Logistic Loss

**Source gap:** Gap 2.2

**Statement.** The $O(\sqrt{\log n})$ relative optimality bound of [Kim&Pilanci2024] (Theorem 2.1) extends to logistic loss under the same Gaussian data assumption (A1), with Gordon's comparison step replaced by a self-concordance coupling argument: logistic loss's Lipschitz gradient $\nabla_{\hat{y}}\ell = \sigma(-y\hat{y})$ bounds the perturbation in the dual variable when transitioning from squared to logistic loss, preserving the $O(\sqrt{\log n})$ rate with a modified constant.

**Rationale.** Self-concordance of logistic loss implies that Newton's method converges in $O(\log\log(1/\varepsilon))$ steps, providing a local quadratic approximation whose curvature is bounded by the sigmoid Lipschitz constant. If the perturbation in the output-space dual variable when the loss changes from squared to logistic is bounded by this Lipschitz constant, the cone-sharpness argument of [Kim&Pilanci2024] Lemma 21 transfers with a constant-factor modification. The Phase 5 advisory identifies self-concordance as the *"more concrete and actionable hypothesis"* for this gap.

**Measurable prediction.** Log-log regression slope of logistic-loss relative gap vs. $n$ should be $\leq 0.6$ for Gaussian binary classification data across $n \in \{50, 100, 200, 500, 1000\}$, within $3\times$ the constant of the squared-loss baseline.

**Falsification.** Slope $> 0.8$ for logistic loss while the squared-loss baseline achieves $\leq 0.5$, under identical data and relaxation width, would falsify the extension.

---

### H7 (Tier 2): Active Arrangement Sparsity Anti-Correlates with NTK Alignment at CIFAR-10 Scale

**Source gap:** Gap 2.3 (rescoped from ImageNet to CIFAR-10 per Phase 5 advisory)

**Statement.** On CIFAR-10 with a three-layer ReLU network (width $m \in \{100, 200, 500\}$), the relative dual support sparsity $k^*/m$ of the convex dual solution is negatively correlated (Spearman $\rho < -0.5$) with the Centered Kernel Alignment (CKA) between learned intermediate representations and the NTK-predicted kernel, across varying width and regularization strength $(m, \lambda) \in \{100, 200, 500\} \times \{10^{-4}, 10^{-3}, 10^{-2}\}$.

**Rationale.** The NTK regime predicts lazy training: features stay close to initialization (high NTK-CKA) and the dual is dense (all arrangements equally active). The convex duality regime predicts active feature selection: features depart from initialization (low NTK-CKA) and the dual is sparse (few arrangements carry weight). As regularization increases, the group-lasso in the convex program produces sparser duals; simultaneously, stronger regularization keeps weights close to zero, increasing NTK alignment. This anti-correlation is the mechanistic signature of the convex duality regime being active. The $L=3$ convex program on CIFAR-10 is already validated in [Ergen&Pilanci2021reveal] ($n = 5 \times 10^4$).

**Falsification.** Spearman $|\rho| < 0.2$ across the $(m, \lambda)$ grid, or $k^*$ uniformly close to $m$ (always dense, consistent with NTK regime), would falsify the hypothesis.

---

## 5. Experimental Methodology

Three experiments (E1, E2, E3) are primary and detailed in full below. Four additional experiments (E4–E7) are summarized in the Tier 2 table.

### E1 — Testing H1: Zero-Gap Singular-Value Condition for Rank-1 Three-Layer ReLU

**Type:** Theoretical proof + exhaustive numerical verification  
**Solver:** CVXPY (SCS backend) for exact primal-dual computation; NumPy for arrangement enumeration

**Experimental design.** For each $(n, d, \beta) \in \{10, 15, 20, 30\} \times \{3, 5, 8\} \times \{0.01, 0.1, 1.0\}$, generate 50 random rank-1 data matrices $X = \mathbf{x}\mathbf{y}^T$ with $\mathbf{x} \sim \mathcal{N}(0, I_n)$, $\mathbf{y} \sim \mathcal{N}(0, I_d)$. For each instance: (1) enumerate all at-most-$n$ distinct hyperplane arrangement matrices $D_1 = \text{diag}(\mathbf{1}[X\mathbf{u} \geq 0])$ for rank-1 data; (2) formulate the three-layer standard ReLU convex program; (3) solve via CVXPY to obtain $p^*$ and $d^*$; (4) compute the duality gap $p^* - d^*$; (5) check the equal-singular-values condition on $\widetilde{X} = D_1 X$ for the active arrangement. 

**Variables:**

| Variable | Type | Range |
|----------|------|-------|
| $n$ | Independent | $\{10, 15, 20, 30\}$ |
| $d$ | Independent | $\{3, 5, 8\}$ |
| $\Delta\sigma(\widetilde{X})$ (SV deviation) | Independent | Continuous, controlled by data perturbation |
| Duality gap $p^* - d^*$ | Dependent | $\geq 0$ (CVXPY) |
| Equal-SV condition satisfied | Dependent | Boolean |
| $\beta$ | Control | $\{0.01, 0.1, 1.0\}$ |

**Baselines:**
- [Wang&Ergen&Pilanci2023] deep linear case: the closed-form equal-SV gap formula for identity activations, which any rank-1 ReLU result must reduce to when activations are ablated
- [Pilanci&Ergen2020] $L=2$ benchmark (always zero gap per Table 1 in [Wang&Ergen&Pilanci2023])
- Random rank-1 Gaussian instances (generically violating equal-SV), which should yield nonzero gaps

**Proof strategy.** Five steps mirror [Wang&Ergen&Pilanci2023]'s deep linear proof:
1. Rescaling reduction: express the rank-1 three-layer primal as a scalar composition $\min_{\mathbf{w}} \frac{1}{2}\|\sigma(X\mathbf{w}) - \mathbf{y}\|^2 + \frac{\beta}{2}\|\mathbf{w}\|^2$.
2. Dualization with respect to output weights; dual variable $\nu \in \mathbb{R}^n$.
3. Arrangement reduction: for rank-1 $X$, the distinct patterns $D_1$ number at most $n$ (data points along a 1D line).
4. Gap formula derivation: compute $p^* - d^*$ as a function of the singular values of $D_1 X$.
5. Criterion extraction: setting the gap to zero yields the equal-SV condition on $\widetilde{X}$.

**Success criteria.** Duality gap = 0 $\Leftrightarrow$ equal-SV condition holds, with zero exceptions across $\geq 200$ random rank-1 instances. Single counterexample falsifies.

**Reproducibility.** CPU sufficient; $\leq 2$ hours for the full grid at $n \leq 30$. 50 fixed random seeds per cell. CVXPY with SCS backend, Python 3.10+.

---

### E2 — Testing H2: $O(\sqrt{\log n})$ Approximation Extends to RIP-Satisfying Data

**Type:** Theoretical derivation + numerical scaling experiment  
**Solver:** CVXPY for full reformulation ($n \leq 100$); CRONOS-JAX for width-$m$ relaxation ($n > 100$)

**Experimental design.** For $n \in \{50, 100, 200, 500, 1000\}$ and data distributions (Gaussian baseline; Bernoulli$(\pm 1)$ as a proxy for RIP-satisfying data), compute the relative optimality gap $(\tilde{p}^* - p^*)/p^*$ for relaxation widths $m \in \{c \log n : c \in \{1, 2, 4\}\}$. Fit a log-log regression of gap vs. $n$ to extract the scaling exponent; compare to the $0.5$ slope ($\sqrt{\log n}$) predicted by [Kim&Pilanci2024] Theorem 2.1 for Gaussian data.

**Variables:**

| Variable | Type | Range |
|----------|------|-------|
| $n$ | Independent | $\{50, 100, 200, 500, 1000\}$ |
| Data distribution | Independent | Gaussian vs. Bernoulli$(\pm 1)$ |
| Relaxation width $m$ | Independent | $\{c \log n: c \in \{1, 2, 4\}\}$ |
| Relative gap $(\tilde{p}^* - p^*)/p^*$ | Dependent | $\geq 0$ |
| RIP parameter $\delta$ | Control | Verified $< 1/2$ via restricted eigenvalue condition |

**Baselines:**
- Gaussian data + [Kim&Pilanci2024] Theorem 2.1 (proved $O(\sqrt{\log n})$ bound, slope $\approx 0.5$)
- RIP data + full reformulation ($m = $ all arrangements): reference $p^*$ only for $n \leq 100$
- Non-RIP data (correlated features, $\delta > 1/2$): should break the $O(\sqrt{\log n})$ scaling

**Proof strategy.** Three modifications to [Kim&Pilanci2024] Section 4:
1. Replace Gaussianity (A1) with RIP in the two steps that use Gaussianity: bounding $\lambda_{\min}(\mathcal{M})$ and applying Gordon's comparison. RIP directly controls $\lambda_{\min}(\Phi^T\Phi)$.
2. Substitute $\lambda_{\min} \geq 1-\delta$ into Lemma 21 of [Kim&Pilanci2024] to obtain $O(\sqrt{\log n})$ rate with a modified constant $C(\delta)$.
3. If Gordon's inequality does not extend cleanly, use Mendelson (2007) Theorem 3 as a fallback: sub-Gaussian data yields the same $O(\sqrt{\log n})$ rate without Gaussianity.

**Success criteria.** Log-log regression slope $\leq 0.6$ for Bernoulli data, within $2\times$ the Gaussian baseline constant, $R^2 > 0.85$. RIP parameter $\delta < 1/2$ verified for all Bernoulli instances. Slope $> 0.8$ for non-RIP (correlated) data confirms RIP is load-bearing.

**Reproducibility.** 20 seeds per $(n, m, \text{distribution})$ cell. RTX-4090 or A100 GPU for $n > 200$; CPU for $n \leq 100$. Estimated $\sim 4$ GPU-hours for full grid.

---

### E3 — Testing H3: CRONOS-AM Lyapunov Descent Under Bounded Step Size

**Type:** Numerical empirical experiment  
**Solver:** CRONOS-JAX with bounded-step-size DAdapted-Adam modification

**Experimental design.** Implement a step-size-bounded variant of CRONOS-AM where the DAdapted-Adam update at each iteration is clipped to $\eta_t \leq \varepsilon / \|\nabla \mathcal{L}_t\|$ for $\varepsilon \in \{0.01, 0.1, 0.5\}$. Run this on UCI Concrete ($n=1030$), Energy ($n=768$), and Wine ($n=4898$) regression datasets from [Feng&Frangella&Pilanci2023] Table 2, with 5 random seeds per cell. Log the CRONOS sub-problem optimal value $f_t^*$ at each alternating minimization iteration. Compare against default CRONOS-AM (unconstrained DAdapted-Adam).

**Variables:**

| Variable | Type | Values |
|----------|------|--------|
| Step-size rule | Independent | Bounded ($\eta_t \leq \varepsilon / \|\nabla\mathcal{L}_t\|$) vs. default |
| Tolerance $\varepsilon$ | Independent | $\{0.01, 0.1, 0.5\}$ |
| $f_t^*$ (convex sub-problem optimum) | Dependent | Logged per AM iteration |
| Iterations to convergence | Dependent | Counted |
| Dataset | Control | UCI Concrete, Energy, Wine |
| Network depth | Control | $L=3$ |

**Baselines:**
- Default CRONOS-AM from [Feng&Frangella&Pilanci2023] Table 2
- Fixed small step size ($\eta_t = 10^{-4}$): over-conservative, guarantees monotone descent but slow
- $\varepsilon = \infty$: recovers default CRONOS-AM, validating code-path equivalence

**Success criteria (Lyapunov confirmation).** $f_t^*$ is non-increasing in $\geq 90\%$ of iterations across all 3 datasets and all 3 $\varepsilon$ values, with violations $< 10^{-6}$ relative. **Vacuity check:** if bounded step sizes are smaller than $10^{-6}$ at initialization, $\varepsilon$ is too small and the experiment is redone with larger $\varepsilon$.

**Falsification.** $f_t^*$ increases across $>3$ consecutive iterations by $>0.1\%$ relative while the bounded rule is satisfied, on any dataset / $\varepsilon$ combination.

**Reproducibility.** 5 seeds per (dataset, $\varepsilon$) cell. Single RTX-4090 GPU; estimated $\sim 2$ GPU-hours for full 3×3 grid. CRONOS-JAX codebase modified with step-size clipping in the DAdapted-Adam update.

---

### Tier 2 Experiments (Summary)

| Experiment | Hypothesis | Type | Primary Method | Key Success Criterion |
|------------|-----------|------|----------------|-----------------------|
| **E4** | H4 (generalization bound) | Empirical benchmark | CVXPY + dual support extraction | Spearman $\rho > 0.7$ between $\sqrt{k^*/n}$ and test MSE across 960 runs |
| **E5** | H5 (fixed-point BN) | Numerical exact equivalence | PyTorch SGD + CVXPY convex (BN-adjusted $X$) | Training loss gap $< 10^{-4}$, primal-dual gap $< 10^{-6}$ |
| **E6** | H6 (logistic loss) | Theory + numerical scaling | CVXPY / CRONOS + logistic loss | Log-log slope $\leq 0.6$ matching Gaussian baseline within $3\times$ |
| **E7** | H7 (NTK vs. convex duality) | Medium-scale empirical | CIFAR-10, ResNet-3L, CKA + dual support | Spearman $\rho < -0.5$ between $k^*/m$ and NTK-CKA |

**E4 design.** Factor grid: $n \in \{50, 100, 200, 500\}$, rank $r \in \{1, 3, 5, d/2\}$, $\beta \in \{10^{-3}, 10^{-2}, 10^{-1}\}$, 20 seeds per cell = 960 CVXPY solves. Extract $k^*$ from CVXPY dual solution support (number of non-zero groups). Compare $\sqrt{k^*/n}$ to 20% hold-out MSE via Spearman correlation and log-log regression.

**E5 design.** $n=50$, $d=10$; 40 SGD runs (10 random inits $\times$ 2 BN convergence tolerances $\times$ 2 $\beta$ values) + 4 CVXPY solves with $\hat{X} = \text{BN}(X)$. Fixed-point BN via repeated forward passes until $\|\hat{\mu}_t - \hat{\mu}_{t-1}\| < \varepsilon_{\text{BN}} \in \{10^{-3}, 10^{-6}\}$.

**E6 design.** $n \in \{50, 100, 200, 500, 1000\}$, binary classification, Gaussian A1 data; measure relative gap for squared vs. logistic loss at relaxation width $O(\log n)$. Compare log-log scaling slopes; test Cauchy-data ablation to confirm Gaussianity is necessary.

**E7 design.** CIFAR-10 ($n = 5 \times 10^4$), three-layer ReLU, width $m \in \{100, 200, 500\}$, $\lambda \in \{10^{-4}, 10^{-3}, 10^{-2}\}$. Train with CRONOS-AM; extract dual support $k^*$ from CRONOS output. Compute CKA between learned intermediate representations and the NTK kernel at initialization. Spearman correlation test across the $(m, \lambda)$ grid.

---

## 6. References

Sources cited in this document, all accessible via the sources/ directory of this pipeline run.

- Pilanci, M. & Ergen, T. (2020). *Neural Networks are Convex Regularizers: Exact Polynomial-time Convex Optimization Formulations for Two-Layer Networks.* ICML 2020. [Pilanci&Ergen2020] — sources/user-2002.10553v2, sources/arxiv-2002.10553

- Ergen, T. & Pilanci, M. (2021). *Global Optimality Beyond Two Layers: Training Deep ReLU Networks via Convex Programs.* ICML 2021. [Ergen&Pilanci2021global] — sources/user-ergen21b, sources/arxiv-2110.06482

- Wang, B., Ergen, T. & Pilanci, M. (2023). *Parallel Deep Neural Networks Have Zero Duality Gap.* ICLR 2023. [Wang&Ergen&Pilanci2023] — sources/user-2110.06482v3

- Ergen, T. & Pilanci, M. (2021). *Revealing the Structure of Deep Neural Networks via Convex Duality.* NeurIPS 2021. [Ergen&Pilanci2021reveal] — sources/user-2110.05518v2, sources/arxiv-2110.05518

- Feng, J., Frangella, Z. & Pilanci, M. (2023). *CRONOS: Enhancing Deep Learning with Scalable GPU Accelerated Convex Neural Networks.* NeurIPS 2023. [Feng&Frangella&Pilanci2023] — sources/user-8652_CRONOS_Enhancing_Deep_Lea

- Kim, J. & Pilanci, M. (2024). *Convex Relaxations of ReLU Neural Networks Approximate Global Optima in Polynomial Time.* ICML 2024. [Kim&Pilanci2024] — sources/user-2402.03625v3, sources/arxiv-2402.03625

- Weng, L. (2022). *Some Math behind Neural Tangent Kernel.* Blog post, lilianweng.github.io. [Lilianweng2022]

- Jacot, A., Gabriel, F. & Hongler, C. (2018). *Neural Tangent Kernel: Convergence and Generalization in Neural Networks.* NeurIPS 2018. [Jacot2018] — referenced in [Lilianweng2022]

- Gunasekar, S., Woodworth, B., Bhojanapalli, S., Neyshabur, B. & Srebro, N. (2017). *Implicit Regularization in Matrix Factorization.* NeurIPS 2017. [Gunasekar2017] — sources/arxiv-1710.10174 (manifest entry)

- Mendelson, S. (2007). *Empirical processes with a bounded diameter.* Referenced in [Kim&Pilanci2024] as an alternative to Gordon's comparison inequality for sub-Gaussian data.

- Arora, S., Ge, R., Neyshabur, B. & Zhang, Y. (2018). *Stronger generalization bounds for deep nets via a compression approach.* ICML 2018. Referenced in Phase 5 advisory for compression-based generalization bounds.

- Xu, Y. & Yin, W. (2013). *A Block Coordinate Descent Method for Regularized Multiconvex Optimization with Applications to Nonnegative Tensor Factorization and Completion.* SIAM Journal on Imaging Sciences. Referenced in E3 methodology as the theoretical scaffold for Lyapunov two-block alternating minimization.
