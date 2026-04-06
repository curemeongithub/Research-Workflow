---
phase: 4
status: complete
timestamp: 2026-04-06T00:00:00Z
depends_on: [analysis/literature-map.md]
token_estimate: 4800
source_lookups_used: 4
---

# Gap Analysis: Dual Convex Optimization in ReLU Neural Networks

## Executive Summary

The convex duality framework for ReLU networks has matured into a coherent body of results covering two-layer exact reformulations, deep parallel architectures, a GPU-scale solver (CRONOS), and polynomial-time approximation guarantees. However, the framework rests on three structural pillars that have not been fully removed: the requirement for parallel (rather than standard sequential) architecture to guarantee zero duality gap, the Gaussian data distribution assumption needed for polynomial approximation bounds, and the absence of end-to-end convergence guarantees for the most practical solver (CRONOS-AM). Each of these constitutes a well-evidenced, high-impact gap directly acknowledged by the source papers. A second tier of gaps concerns the incomplete integration of batch normalization, the extension of polynomial guarantees to non-squared losses, the outstanding NTK-vs.-convex-duality empirical question at scale, and the lack of minimal structural conditions that restore zero duality gap without full parallelism. Two speculative, low-evidence gaps concern transformer attention and adaptive optimizers, neither of which is addressed in the corpus.

---

## Tier 1 Gaps (High Priority)

### Gap 1.1: Duality Gap Characterization for Standard Deep ReLU Networks (L ≥ 3) with General Data

- **Description:** For standard (non-parallel) deep ReLU networks with three or more layers and general (non-rank-1) data matrices, neither the zero-gap condition nor the explicit duality gap formula has been proven. This is the single most prominent open problem in the corpus.

- **Evidence from literature:**
  - [Wang&Ergen&Pilanci2023] Table 1 explicitly marks the entry for "standard deep ReLU networks, L ≥ 3" as "Not Proven." The abstract of the same paper states: "extending this result [strong duality for two-layer ReLU] to deeper networks remains to be an open problem."
  - [Wang&Ergen&Pilanci2023] proves the non-zero gap *only* for deep linear networks (not ReLU), and separately proves zero gap for the rank-1 / scalar-output three-layer ReLU case. The general ReLU case with L ≥ 3 falls outside both results.
  - [Ergen&Pilanci2021global] establishes zero gap for the *parallel* three-layer architecture, which implicitly highlights the open question for the sequential counterpart.

- **Source lookup used:** Yes — query: "duality gap ReLU standard deep open future"; `sources/user-2110.06482v3/content.md` line 18 and line 386: "A limitation of our work is that we primarily focus on minimum norm interpolation problems."

- **Scores:** Confidence: 3/3, Impact: 3/3, Feasibility: 2/3, Verifiability: 3/3, **Total: 11/12**
- **Tier:** 1

- **Proposed research direction:** Extend the Lagrangian duality analysis from deep linear networks to the deep ReLU case for general data matrices. The bi-dual relationship between standard and parallel architectures (established for linear networks) may provide the key: showing that the bi-dual of the standard deep ReLU problem equals a parallel deep ReLU problem, then deriving the duality gap as the difference in optimal values.

---

### Gap 1.2: Polynomial-Time Approximation Guarantees for General (Non-Gaussian) Data Distributions

- **Description:** The only polynomial-time approximation guarantee for the convex relaxation — the O(√log n) relative optimality bound — is proven under a Gaussian i.i.d. data assumption (A1) in [Kim&Pilanci2024]. Whether this bound extends to real-world data distributions (structured, non-Gaussian, correlated) is explicitly unresolved.

- **Evidence from literature:**
  - [Kim&Pilanci2024] Assumption (A1): "Throughout the paper, we assume that the data distribution follows X_ij ~ N(0,1) i.i.d." and adds: "a connection to restricted isometry property (RIP) could be a key to extending the result to different distributions. Here, we assume Gaussianity for simplicity."
  - The proof technique relies on Gordon's comparison inequality from random matrix theory, which currently requires Gaussian structure.
  - All practical datasets (MNIST, CIFAR, ImageNet) are manifestly non-Gaussian; the empirical success of CRONOS on ImageNet [Feng&Frangella&Pilanci2023] lacks theoretical coverage under A1.

- **Source lookup used:** Yes — query: "Gaussian RIP restricted isometry general data assumption"; `sources/user-2402.03625v3/content.md` line 105.

- **Scores:** Confidence: 3/3, Impact: 3/3, Feasibility: 2/3, Verifiability: 3/3, **Total: 11/12**
- **Tier:** 1

- **Proposed research direction:** Replace Gordon's comparison inequality with a generic empirical process bound (e.g., via Bernstein/RIP-type conditions). The authors already identify this path: proving that data matrices satisfying a restricted isometry condition on the hyperplane arrangement feature map inherit the O(√log n) relative error bound from the Gaussian case. A key step is showing the count of distinct hyperplane arrangement patterns scales like O((n/r)^r) for RIP matrices as it does for Gaussian matrices.

---

### Gap 1.3: End-to-End Convergence Guarantees for CRONOS-AM on Multi-Layer Networks

- **Description:** CRONOS provides proven convergence to the global minimum of the convex reformulation on a 2-layer sub-problem. CRONOS-AM extends this to arbitrary-depth networks via alternating minimization (CRONOS for the last two convex layers; DAdapted-Adam for earlier non-convex layers), but there is no end-to-end convergence guarantee for the full CRONOS-AM procedure.

- **Evidence from literature:**
  - [Feng&Frangella&Pilanci2023] Section 6 covers convergence only for CRONOS (Theorem 6.4), not for CRONOS-AM: "Our theoretical analysis proves that CRONOS converges to the global minimum of the convex reformulation under mild assumptions."
  - The paper's future work section explicitly asks: "Can we provide a convergence guarantee for CRONOS-AM that shows an advantage over stochastic first-order methods?"
  - DAdapted-Adam is applied to the early layers of CRONOS-AM without global convergence guarantees; alternating minimization on jointly non-convex objectives is known to get stuck in stationary points [Bai et al. 2023, cited in Feng&Frangella&Pilanci2023].

- **Source lookup used:** Yes — query: "CRONOS-AM convergence limitation future work"; `sources/user-8652_CRONOS_Enhancing_Deep_Lea/content.md` line 366.

- **Scores:** Confidence: 3/3, Impact: 2/3, Feasibility: 2/3, Verifiability: 3/3, **Total: 10/12**
- **Tier:** 1

- **Proposed research direction:** Develop a two-block alternating minimization convergence theory for the CRONOS-AM split. One promising direction is to show that when the non-convex early layers are trained with a bounded step size, the CRONOS-solved sub-problem's optimal value decreases monotonically, establishing a Lyapunov-function argument for convergence. Bounding the DAdapted-Adam step's disturbance to the convex sub-problem's feasibility constraints is the key technical challenge.

---

## Tier 2 Gaps (Moderate Priority)

### Gap 2.1: Integration of Layer-Wise Batch Normalization with the Full Convex Duality Framework

- **Description:** [Ergen&Pilanci2021reveal] shows that batch normalization before the final layer removes the whitened/rank-1 data requirement and implies neural collapse. However, the full convex duality framework (strong duality, group-sparse equivalent program, hyperplane arrangement parameterization) for architectures with BN at every intermediate layer is not established.

- **Evidence from literature:**
  - [Ergen&Pilanci2021reveal] explicitly states its BN results apply to "the last linear layer with BN" and Section 6 (Contested Areas, Literature Map) notes: "whether the full convex duality framework extends seamlessly to architectures with batch normalization at every layer remains partially open."
  - BN's population normalization across the batch introduces data-example coupling that breaks the independent per-sample structure assumed in the semi-infinite duality derivation.

- **Source lookup used:** No (confirmed from literature map directly).

- **Scores:** Confidence: 2/3, Impact: 3/3, Feasibility: 2/3, Verifiability: 2/3, **Total: 9/12**
- **Tier:** 2

- **Proposed research direction:** Formulate the BN layer as an affine transformation parameterized by running statistics, then incorporate this as an additional constraint in the semi-infinite dual. The key challenge is that BN statistics depend on the entire mini-batch, making the effective data matrix dynamic during training; analyzing the fixed-point of BN statistics and the convex sub-problem simultaneously may yield a decoupled formulation amenable to duality.

---

### Gap 2.2: Polynomial-Time Approximation Guarantees for Non-Squared Loss Functions

- **Description:** The O(√log n) approximation guarantee of [Kim&Pilanci2024] is proven exclusively for squared loss. Cross-entropy (logistic) loss dominates classification practice. While [Pilanci&Ergen2020] claims extension to "arbitrary convex loss functions" in an appendix, no polynomial-time approximation guarantee is proven for non-squared losses.

- **Evidence from literature:**
  - [Pilanci&Ergen2020] line 33: "All of our results immediately extend to vector outputs, tensor inputs, arbitrary convex classification and regression loss functions (see Appendix)." — but this is for the *exact* reformulation, not for the *polynomial-time approximation* result.
  - [Kim&Pilanci2024] restricts exclusively to squared loss throughout its main theoretical development; no equivalent Theorem 2.1 for logistic or hinge loss appears in the paper.
  - [Wang&Pilanci2023, cited in Kim&Pilanci2024] provides some hinge-loss analysis, suggesting the direction is tractable.

- **Source lookup used:** Yes (partial) — query: "multi-class vector output logistic cross-entropy loss extension"; `sources/user-2002.10553v2/content.md` line 33 confirmed the exact-reformulation extension exists but not the approximation guarantee.

- **Scores:** Confidence: 2/3, Impact: 2/3, Feasibility: 2/3, Verifiability: 3/3, **Total: 9/12**
- **Tier:** 2

- **Proposed research direction:** Extend the coupling lemma and Gordon comparison argument of [Kim&Pilanci2024] from squared loss to logistic loss by leveraging self-concordance. The key step is bounding the change in optimal hyperplane arrangement patterns when the loss function is perturbed; for logistic loss, Lipschitz continuity of the gradient in the output space may provide the necessary coupling.

---

### Gap 2.3: Empirical Scale Test of NTK vs. Convex Duality Feature Learning Predictions

- **Description:** The NTK regime (lazy training, no feature learning) and the convex duality regime (non-trivial hyperplane arrangement selection) make different predictions about what practical networks learn. No paper in the corpus provides a large-scale (CIFAR-100 or ImageNet-scale) comparison of these predictions using modern representational similarity tools.

- **Evidence from literature:**
  - Literature map Section 6 explicitly identifies this as an "active, unresolved debate."
  - [Ergen&Pilanci2021global] Figure 2 provides small-scale evidence that loss landscape convexity increases with number of sub-networks, but at widths far smaller than modern networks.
  - [Pilanci&Ergen2020] explicitly contrasts the NTK view as unable to "fully explain the success of non-convex neural network models," but provides no empirical comparison to confirm predictions differ in practice.

- **Source lookup used:** No (confirmed from literature map directly).

- **Scores:** Confidence: 2/3, Impact: 3/3, Feasibility: 2/3, Verifiability: 2/3, **Total: 9/12**
- **Tier:** 2

- **Proposed research direction:** At ImageNet scale, train a ResNet-50 with (a) standard SGD with weight decay and (b) CRONOS-AM with equivalent regularization. Measure the Centered Kernel Alignment (CKA) between learned representations and the NTK-predicted kernel vs. the convex-dual-predicted group-sparse features. If the convex duality framework is active, the sparse hyperplane arrangement support structure predicted by the dual solution should be observable in the learned weights.

---

### Gap 2.4: Minimal Structural Conditions on Standard Deep ReLU Networks that Restore Zero Duality Gap

- **Description:** [Wang&Ergen&Pilanci2023] proves that full parallelism restores zero duality gap at any depth. However, full parallelism is a sufficient condition — the minimal sufficient condition (weaker than full parallelism but stronger than sequential depth) for zero duality gap in standard ReLU networks is not characterized.

- **Evidence from literature:**
  - [Wang&Ergen&Pilanci2023] proves zero gap for rank-1 data on standard three-layer ReLU networks, suggesting rank is a relevant structural parameter.
  - The linear network analysis shows that equal singular values of X†Y is the threshold — hinting that data-dependent structural conditions, not pure architectural ones, may govern the gap.
  - No paper characterizes a minimal architectural intervention on standard deep networks that recovers zero duality gap without full parallelism.

- **Source lookup used:** No (confirmed from literature map directly).

- **Scores:** Confidence: 2/3, Impact: 3/3, Feasibility: 2/3, Verifiability: 2/3, **Total: 9/12**
- **Tier:** 2

- **Proposed research direction:** Parametrize architectures between fully sequential and fully parallel (e.g., ResNet-style skip connections with varying multiplicity) and characterize at which point the duality gap transitions from non-zero to zero. The linear network case provides an exact formula (equal singular values); deriving an analogous condition for ReLU networks via the Carathéodory argument on the bi-dual is the natural path.

---

## Tier 3 Gaps (Speculative)

### Gap 3.1: Extension of the Convex Duality Framework to Attention Mechanisms

- **Description:** The semi-infinite duality framework is built entirely on ReLU's piecewise-linear structure parameterized by hyperplane arrangement diagonal matrices. Softmax attention — the core operation of transformers — involves exponential nonlinearities and queries/keys/values that cannot be cast as a hyperplane arrangement. No paper in the corpus addresses this.

- **Evidence from literature:** Entirely absent from the corpus. Inferred from the universal restriction to ReLU throughout all papers. [Pilanci&Ergen2020] explicitly restricts to ReLU in constraints as "an essential ingredient."

- **Source lookup used:** No.

- **Scores:** Confidence: 1/3, Impact: 3/3, Feasibility: 1/3, Verifiability: 2/3, **Total: 7/12**
- **Tier:** 3

- **Proposed research direction:** Begin with a restricted attention variant — e.g., hard attention (argmax) or ReLU attention — that is piecewise-constant rather than softmax-smooth. Derive a hyperplane-arrangement analog for the attention pattern selection and ask whether the resulting training problem admits a group-sparse convex equivalent. This connects to recent work on convex formulations of self-attention under ReLU.

---

### Gap 3.2: Implicit Regularization of Adaptive Gradient Optimizers (Adam) in the Convex Framework

- **Description:** The entire convex duality framework assumes weight decay as the regularizer and characterizes its implicit group-sparse bias. Adam (the dominant practical optimizer) does not have an equivalent convex characterization in this framework; its implicit bias is not captured by any group-norm or Schatten-norm regularization known to be compatible with the semi-infinite dual.

- **Evidence from literature:** Entirely absent. All papers use weight decay (ℓ₂) as the sole regularizer. Adam's implicit regularization is uncharacterized even outside this framework. Inferred absence.

- **Source lookup used:** No.

- **Scores:** Confidence: 1/3, Impact: 3/3, Feasibility: 1/3, Verifiability: 2/3, **Total: 7/12**
- **Tier:** 3

- **Proposed research direction:** Empirically identify the effective regularization of Adam by measuring the dual solution structure (hyperplane arrangement support sparsity) when training the same network with Adam vs. SGD+weight-decay. A parameterized family of regularizers (interpolating between ℓ₂ weight decay and ℓ₁ reparameterizations) could be fit to Adam's effective bias, yielding a "convex equivalent under Adam" as an empirical characterization before attempting a theoretical one.

---

## Rejected Candidates

### Rejected: Multi-Class / Vector Output Extension for Two-Layer Exact Convex Reformulation

**Reason:** [Pilanci&Ergen2020] explicitly extends all results to vector outputs in Appendix A.7: "All of our results immediately extend to vector outputs, tensor inputs, arbitrary convex classification and regression loss functions." CIFAR-10 binary classification experiments are also included. This is addressed in the founding paper.

**Source addressing it:** `sources/user-2002.10553v2/content.md` line 33 and Appendix A.7 (vector output linear CNN dual).

---

### Rejected: Extension to Non-ReLU Activations (GELU, SiLU) for Exact Reformulation

**Reason:** While no paper addresses GELU, the restriction to ReLU is load-bearing in the hyperplane arrangement construction — it is not a gap of omission but a deliberate architectural assumption that enables the exact reformulation. Extending to smooth activations would require a fundamentally different technical apparatus and is more a new research direction than a gap in the existing framework.

---

### Rejected: "Larger Benchmark Evaluations" for CRONOS

**Reason:** Resources, not intellectual problems. CRONOS already reports ImageNet-scale results. Scaling to a larger dataset is a compute/engineering question, not a theoretical gap.

---

## Source Coverage Note

The gap analysis draws on six user-provided PDFs corresponding to the core corpus papers: [Pilanci&Ergen2020] (user-2002.10553v2), [Wang&Ergen&Pilanci2023] (user-2110.06482v3), [Kim&Pilanci2024] (user-2402.03625v3), [Ergen&Pilanci2021global] (user-ergen21b), [Feng&Frangella&Pilanci2023] (user-8652_CRONOS_Enhancing_Deep_Lea), and [Ergen&Pilanci2021reveal] (user-2110.05518v2). All Tier 1 gaps are verified via direct source lookups against these files.

**Phase 1 acquisition note:** 17 sources listed in the manifest are arXiv sources that were Phase 1 acquisition mismatches (they correspond to adjacent work — matrix factorization implicit regularization, NTK, gradient descent theory — rather than the core Pilanci/Ergen duality papers). These were excluded from Phase 3 analysis per the literature map. Their absence does not affect the gap analysis: the gaps identified here are gaps *within the convex duality framework* as represented by the six core papers, and the adjacent-work sources would only potentially address Tier 3 speculative gaps (which are scored at Confidence 1 precisely because they fall outside the core corpus).
