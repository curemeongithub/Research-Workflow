---
phase: 4
status: complete
timestamp: 2026-04-07T19:30:00Z
depends_on: [analysis/literature-map.md]
token_estimate: 6800
---

# Research Gap Analysis: Duality Gap in Dual Convex Optimization in ReLU Neural Networks

## Summary

The convex duality framework for ReLU neural networks is remarkably well-developed for two-layer networks and parallel deep architectures, but leaves significant open territory for standard (non-parallel) deep networks. The single most consequential gap is the unknown status of the duality gap for standard deep ReLU networks with L>=3 and general data -- explicitly marked as open in Wang et al. (2021) Table 1. Practically, a disconnect exists between the strong theoretical guarantees for two-layer convex programs and the heuristic (alternating minimization) approach used for deep networks at scale, where no optimality bounds exist. Cross-theme gaps emerge at the intersection of duality theory and generalization, regularizer sensitivity, and finite-sample behavior. The field's concentration within a single research group (Pilanci Lab) means these gaps are unlikely to be artifacts of missed external work.

## Tier 1 -- Fundamental Gaps

### Gap 1.1: Empirical Characterization of the Duality Gap for Standard Deep ReLU Networks (L>=3)

**Claim:** The duality gap for standard (non-parallel) deep ReLU networks with 3 or more layers and general data has never been empirically measured or theoretically characterized. It is unknown whether the gap is always non-zero, how large it is, or what data/architecture properties control it.

**Evidence from literature:**
- Wang et al. [WangErgenPilanci2021] (arxiv-2110.06482), Table 1, rows for "standard networks / ReLU activation / L=3 and L>3": both cells show "X" (unknown), explicitly indicating no characterization exists even after their paper. (Source verified: lines 56-66 of sources/arxiv-2110.06482/content.md.)
- Wang et al. prove the duality gap is non-zero for standard deep *linear* networks with L>=3, but the ReLU case remains open except under rank-1 data restrictions [WangErgenPilanci2021].
- The paper's central framing question is "Does strong duality hold for deep neural networks?" (line 86), and for standard ReLU the answer is left unresolved.

**Scoring:**
- Confidence of Existence: 9/10 -- Multiple indicators confirm this gap: Table 1 explicitly marks it as unknown; the authors frame it as their motivating question but resolve it only for linear activations and parallel architectures.
- Potential Impact: 9/10 -- Characterizing whether the duality gap is always non-zero for standard deep ReLU networks would either (a) show that standard deep networks are fundamentally different from two-layer ones, closing the theoretical possibility of exact convex reformulations, or (b) identify conditions under which strong duality holds, enabling new algorithmic approaches.
- Feasibility: 7/10 -- Empirical measurement of the gap requires computing both primal and dual values for deep ReLU networks. The primal is standard non-convex training; the dual can be computed for moderate-sized networks using existing convex solvers. New code is needed to systematically vary depth, width, data rank, and measure the gap.
- Verifiability: 9/10 -- The duality gap $P - D$ is a scalar quantity that can be computed numerically. Success threshold is clear: characterize the gap as a function of depth $L$, data rank $r$, and sample size $n$.
- Empirical Testability: 7/10 -- Requires writing experiment code (~500-1000 lines) to set up primal/dual problems for 3+ layer standard ReLU networks, solve them, and measure the gap. Can be done on CPU for small/moderate instances using existing SCNN/convex_nn libraries as building blocks, though adapting them to deep standard architectures requires new implementation.
- **Composite: (9x2 + 9 + 7 + 9 + 7) / 6 = 8.3/10**

**Source lookup used:** Yes -- "Table 1, standard ReLU duality gap L>=3" in sources/arxiv-2110.06482/content.md, lines 56-66.

**Proposed research direction:** Numerically compute primal and dual values for standard 3-layer and 4-layer ReLU networks across synthetic datasets with varying rank, measuring $P - D$ as a function of depth, width, data rank, and regularization strength. Compare against the closed-form gap expressions derived for linear networks.

---

### Gap 1.2: Optimality Gap of CRONOS-AM (Alternating Minimization for Deep Convex Networks)

**Claim:** The alternating minimization approach used by CRONOS-AM to train deep ReLU networks via convex reformulation has no convergence guarantee or optimality gap bound. The quality of solutions relative to the global optimum is entirely unknown.

**Evidence from literature:**
- Feng et al. [Feng2023CRONOS] (user-8652-CRONOS), Section 8 (Conclusion, line 366): "Can we provide a convergence guarantee for CRONOS-AM that shows an advantage over stochastic first-order methods?" -- explicitly stated as open future work.
- CRONOS-AM decomposes the deep network into non-convex (inner layers) and convex (last two layers) subproblems, alternating between Adam and the convex CRONOS solver (line 194). Convergence theory exists for CRONOS on the two-layer subproblem (Section 6), but not for the alternating scheme.
- The literature map Section 6 notes: "CRONOS relies on alternating minimization for multi-layer networks, which loses the global optimality guarantee of the pure convex formulation."

**Scoring:**
- Confidence of Existence: 9/10 -- The paper's own authors identify this as open future work in their conclusion.
- Potential Impact: 8/10 -- CRONOS-AM is currently the only method scaling convex neural network training to ImageNet. If the optimality gap is large, the claimed advantage of convex training over SGD is undermined for deep networks. If the gap is small, it validates the alternating minimization approach as a practical substitute for exact convex optimization.
- Feasibility: 8/10 -- Can be investigated empirically by comparing CRONOS-AM solutions against (a) the best SGD solutions and (b) exact convex solutions on smaller instances where the exact solution is computable. The CRONOS codebase is public (github.com/pilancilab/CRONOS) and implemented in JAX.
- Verifiability: 9/10 -- The optimality gap is directly measurable: compare CRONOS-AM's training loss to the exact convex optimum (for small instances) or to Kim et al.'s approximation bounds.
- Empirical Testability: 8/10 -- CRONOS is open-source with JAX implementation. Can run CRONOS-AM on small-to-moderate problems where the exact convex solution is also computable, then measure the gap. Requires GPU for realistic-scale experiments but can be done on CPU for proof-of-concept with small networks.
- **Composite: (9x2 + 8 + 8 + 9 + 8) / 6 = 8.5/10**

**Source lookup used:** Yes -- "CRONOS-AM convergence guarantee, optimality gap" in sources/user-8652-CRONOS/content.md, line 366.

**Proposed research direction:** Run CRONOS-AM on datasets of increasing size (from synthetic to MNIST subsets), and for each, also compute the exact two-layer convex optimum and the best SGD solution. Plot the ratio of CRONOS-AM loss to convex optimum as a function of depth, width, and dataset size. Test whether the gap grows, shrinks, or stabilizes with scale.

---

## Tier 2 -- Extensions

### Gap 2.1: Effect of Regularizer Choice on the Duality Gap in Deep ReLU Networks

**Claim:** The entire convex duality framework for ReLU networks assumes $\ell_2^2$ weight decay regularization. How alternative regularizers (elastic net, spectral norm, dropout-as-regularization) affect the duality gap -- or whether convex reformulation is even possible with them -- has not been studied for ReLU networks.

**Evidence from literature:**
- Bartan and Pilanci [BartanPilanci2021] (arxiv-2101.02429) show that for polynomial activations, the regularizer is critical: $\ell_2^2$ weight decay makes the problem NP-hard while cubic regularization makes it tractable. But this result is specific to polynomial activations.
- All ReLU network papers in the corpus [PilanciErgen2020, ErgenPilanci2021Deep, WangErgenPilanci2021, Mishkin2022SCNN, Feng2023CRONOS] exclusively use $\ell_2^2$ weight decay as the regularizer.
- Source lookup confirmed: no paper in the corpus mentions elastic net, spectral norm regularization, or dropout in the context of convex duality.

**Scoring:**
- Confidence of Existence: 7/10 -- Verified by source lookup: no paper addresses alternative regularizers for ReLU duality. The Bartan result for polynomial activations strongly suggests the regularizer matters but this specific question for ReLU is unstudied.
- Potential Impact: 7/10 -- Practical neural network training uses diverse regularization strategies. If convex equivalence requires $\ell_2^2$ weight decay specifically, this limits the practical scope of the theory. Conversely, finding regularizers that improve (or eliminate) the duality gap for deep networks would be significant.
- Feasibility: 7/10 -- Can be tested by substituting different regularizers into the convex reformulation framework and checking if strong duality still holds. Requires modifying existing convex solvers.
- Verifiability: 8/10 -- For each regularizer, the duality gap is a measurable quantity. Can also check whether the reformulation steps (rescaling, semi-infinite duality) still apply.
- Empirical Testability: 7/10 -- Requires modifying the SCNN or convex_nn codebase to support alternative regularizers, then solving both primal and dual. Moderate implementation effort (~500 lines of modifications to existing code).
- **Composite: (7x2 + 7 + 7 + 8 + 7) / 6 = 7.2/10**

**Source lookup used:** Yes -- "regularizer duality gap, elastic net, different regularizers" across all sources/.

**Proposed research direction:** Systematically modify the two-layer convex reformulation to use elastic net ($\ell_1 + \ell_2$), group Lasso, and spectral norm regularizers. For each, check whether the rescaling lemma still applies, compute the duality gap, and compare to the standard $\ell_2^2$ case.

---

### Gap 2.2: Relationship Between Duality Gap Magnitude and Generalization Performance

**Claim:** No paper in the corpus studies whether the size of the duality gap (when non-zero) correlates with, bounds, or predicts generalization error. The connection between optimization gap and statistical gap is entirely unexplored.

**Evidence from literature:**
- Source lookup confirmed: the term "generalization" does not appear in any source file in the corpus.
- Papers measure training loss (primal-dual gap) and test accuracy separately but never relate them. CRONOS [Feng2023CRONOS] reports both training and validation metrics but does not analyze their relationship through the lens of duality.
- The theoretical papers [PilanciErgen2020, WangErgenPilanci2021] characterize the optimization gap but do not connect it to statistical learning theory.

**Scoring:**
- Confidence of Existence: 7/10 -- Verified by source lookup that "generalization" is absent from the corpus. However, the connection between optimization gaps and generalization is studied in the broader optimization theory literature (outside this specific field), so external work may exist that we cannot verify from our sources alone.
- Potential Impact: 7/10 -- If the duality gap bounds or predicts generalization, this would provide a new theoretical tool for understanding deep network behavior. However, the impact depends on whether the relationship is tight enough to be useful.
- Feasibility: 6/10 -- Requires computing both the duality gap and generalization error across many configurations, then testing for correlation. The statistical framework for relating these quantities would need to be developed.
- Verifiability: 7/10 -- Correlation between duality gap and test error is measurable. However, establishing a causal or theoretical relationship is harder to verify.
- Empirical Testability: 7/10 -- Can be tested by training networks with known duality gaps (using the convex solvers) and measuring test performance across multiple datasets. Requires running convex and non-convex training, measuring gaps, and computing test metrics.
- **Composite: (7x2 + 7 + 6 + 7 + 7) / 6 = 6.8/10**

**Source lookup used:** Yes -- "generalization, duality gap magnitude" across all sources/.

**Proposed research direction:** For two-layer ReLU networks on standard benchmarks (MNIST, CIFAR-10 subsets), compute the exact convex optimum and various suboptimal SGD solutions. Measure both the optimization gap (distance from convex optimum) and the generalization gap (train vs test error). Test whether networks closer to the convex optimum generalize better or worse.

---

### Gap 2.3: Scalability of Kim et al.'s $O(\sqrt{\log n})$ Approximation Guarantee to Practice

**Claim:** Kim and Pilanci's [Kim2024] polynomial-time approximation result guarantees a relative optimality gap of $O(\sqrt{\log n})$ under Gaussian data assumptions, but the tightness of this bound and its behavior on real (non-Gaussian) data have not been empirically evaluated.

**Evidence from literature:**
- Kim and Pilanci [Kim2024] (arxiv-2402.03625) prove the theoretical bound under Gaussian data assumptions. The paper discusses the theoretical guarantee but experiments (if any) focus on verifying convergence of local methods, not on measuring how tight the $O(\sqrt{\log n})$ bound is.
- The literature map notes this as ICML 2024 work introducing the "relative optimality gap $p^*/\tilde{p}^*$ as a metric for relaxation quality."
- No other paper in the corpus empirically tests how tight this approximation is or whether it holds beyond Gaussian data.

**Scoring:**
- Confidence of Existence: 7/10 -- The paper provides a theoretical bound but the empirical tightness question is not addressed within the corpus. It is possible that supplementary materials or concurrent work address this, but we see no evidence.
- Potential Impact: 6/10 -- If the bound is loose by orders of magnitude, the practical value of the approximation is limited. If it is tight, it validates a practical algorithm for large-scale convex training.
- Feasibility: 8/10 -- Straightforward to test: compute exact solutions on small instances, apply the randomized relaxation, measure the actual ratio, and compare to the theoretical bound.
- Verifiability: 9/10 -- The relative optimality gap $p^*/\tilde{p}^*$ is a directly computable scalar.
- Empirical Testability: 8/10 -- Can use the existing convex_nn or SCNN code to compute exact solutions on small instances, implement the Gaussian relaxation, and measure the gap. Primarily CPU-feasible for moderate instances.
- **Composite: (7x2 + 6 + 8 + 9 + 8) / 6 = 7.5/10**

**Source lookup used:** No.

**Proposed research direction:** Implement Kim et al.'s randomized relaxation algorithm for two-layer ReLU networks. On synthetic Gaussian data, measure the actual relative optimality gap and compare to the $O(\sqrt{\log n})$ upper bound across varying $n$ and $d$. Then repeat on non-Gaussian data (e.g., structured image features) to test robustness of the guarantee.

---

### Gap 2.4: Convex Duality for Standard Deep ReLU Networks with Rank Conditions Beyond Rank-1

**Claim:** Strong duality for standard (non-parallel) three-layer ReLU networks has been proven only for rank-1 data matrices. Whether strong duality holds for rank-2, rank-3, or bounded-but-greater-than-1 rank data in standard deep architectures is unknown.

**Evidence from literature:**
- Wang et al. [WangErgenPilanci2021] prove strong duality for three-layer standard ReLU networks with rank-1 data (mentioned in literature map Section 3).
- For rank > 1, the same paper's Table 1 marks the standard ReLU L=3 case as "X" (unknown).
- Ergen and Pilanci [ErgenPilanci2021Structure] prove results for whitened data and deep networks but through the parallel/sub-network architecture, not standard networks.

**Scoring:**
- Confidence of Existence: 8/10 -- Table 1 of [WangErgenPilanci2021] explicitly shows this is unresolved. The rank-1 result is the only positive result for standard deep ReLU.
- Potential Impact: 7/10 -- Understanding the rank threshold at which the duality gap appears (or disappears) for standard deep ReLU networks would delineate the exact boundary of convex equivalence theory.
- Feasibility: 7/10 -- Can be studied empirically by generating data matrices of controlled rank (2, 3, 4, ...) and computing primal/dual values for three-layer standard ReLU networks.
- Verifiability: 9/10 -- The duality gap is a directly computable quantity for each rank condition.
- Empirical Testability: 7/10 -- Requires adapting the convex reformulation code for three-layer standard architectures (not parallel) and computing both primal and dual. Moderate implementation effort using existing codebases as starting points.
- **Composite: (8x2 + 7 + 7 + 9 + 7) / 6 = 7.7/10**

**Source lookup used:** Partially (reuses Lookup 1 findings on Table 1).

**Proposed research direction:** Generate synthetic data matrices $X \in \mathbb{R}^{n \times d}$ with controlled rank $r \in \{1, 2, 3, ..., \min(n,d)\}$. For each rank, train standard 3-layer ReLU networks and compute the duality gap. Identify whether there is a sharp rank threshold above which the gap becomes non-zero, or if the gap grows continuously with rank.

---

### Gap 2.5: Finite-Sample Scaling of Convex Equivalence Results

**Claim:** All convex equivalence results in the corpus are stated for a fixed dataset $(X, y)$. How the convex reformulation properties (duality gap, solution structure, number of required hyperplane arrangements $P$) change as the sample size $n$ grows is not studied.

**Evidence from literature:**
- Source lookup confirmed: no paper uses the terms "population," "finite sample," "sample size" (in the scaling sense), or "asymptotic" as a primary analysis concept.
- The hyperplane arrangement count $P$ is bounded by $P \leq 2r(e(n-1)/r)^r$ [PilanciErgen2020], which depends on $n$. As $n$ grows, the convex program grows exponentially in effective rank. But the practical behavior of this scaling has not been studied empirically.
- The $O(\sqrt{\log n})$ approximation guarantee [Kim2024] involves $n$ but is a theoretical worst-case bound.

**Scoring:**
- Confidence of Existence: 6/10 -- The absence of finite-sample scaling analysis is verified from our sources, but this may be considered outside the scope of the optimization-focused papers rather than a true gap.
- Potential Impact: 6/10 -- Understanding how convex equivalence degrades or strengthens with sample size bridges optimization theory and statistical learning, but the practical impact depends on whether the scaling reveals surprises.
- Feasibility: 8/10 -- Can systematically vary $n$ on synthetic data, compute the number of active hyperplane arrangements, duality gap, and solution quality.
- Verifiability: 8/10 -- All quantities ($P$, gap, training loss) are directly computable.
- Empirical Testability: 8/10 -- Straightforward computational experiment using existing SCNN code with varying sample sizes. CPU-feasible for moderate $n$.
- **Composite: (6x2 + 6 + 8 + 8 + 8) / 6 = 7.0/10**

**Source lookup used:** Yes (reuses Lookup 3 findings).

**Proposed research direction:** Using the SCNN solver for two-layer ReLU networks, systematically vary $n \in \{50, 100, 200, 500, 1000\}$ on synthetic data with fixed $d$ and measure: (a) number of active hyperplane arrangements, (b) solve time, (c) duality gap (if using relaxations), (d) ratio of SGD solution quality to convex optimum. Characterize the scaling regime.

---

## Tier 3 -- Stress-Tests

### Gap 3.1: Gated ReLU Equivalence Beyond Two Layers

**Claim:** Mishkin et al. [Mishkin2022SCNN] show that unregularized two-layer ReLU training is equivalent to a gated ReLU problem (a standard group-$\ell_1$ regularized GLM). Whether this equivalence extends to deeper architectures or to the regularized case has not been investigated.

**Evidence from literature:**
- Mishkin et al. [Mishkin2022SCNN] (arxiv-2202.01331) establish the two-layer gated ReLU equivalence and use it as the foundation for their fast solver.
- No paper in the corpus extends the gated ReLU equivalence to three or more layers, or studies whether the equivalence breaks down with regularization.
- CRONOS-AM [Feng2023CRONOS] uses the two-layer equivalence as a subroutine but does not extend the gated ReLU concept itself to deeper architectures.

**Scoring:**
- Confidence of Existence: 8/10 -- The two-layer result is clearly stated and no extension to deeper networks appears in any paper.
- Potential Impact: 5/10 -- The gated ReLU equivalence is an algorithmic convenience that enables fast solvers. Extending it could enable fast deep convex solvers, but the parallel architecture approach already provides a different path to deep network convex training.
- Feasibility: 6/10 -- Requires theoretical analysis of whether the unregularized deep network problem admits a gated ReLU interpretation. Empirical testing is possible by comparing gated and ungated formulations.
- Verifiability: 8/10 -- Can verify by checking whether the gated ReLU formulation achieves the same optimal value as the standard formulation for deep networks.
- Empirical Testability: 6/10 -- Requires implementing the gated ReLU formulation for 3+ layer networks and comparing solution quality. Moderate complexity.
- **Composite: (8x2 + 5 + 6 + 8 + 6) / 6 = 6.8/10**

**Source lookup used:** No.

**Proposed research direction:** Formulate the gated ReLU equivalent for three-layer standard ReLU networks (if it exists). Implement both the standard and gated formulations, solve on synthetic data, and check if the optimal values match. If they diverge, characterize where the equivalence breaks.

---

### Gap 3.2: Robustness of the Convex Optimum to Data Perturbation

**Claim:** The sensitivity of convex neural network solutions to data perturbations (noise, outliers, adversarial examples) has not been studied. It is unknown whether the global optimum found by convex methods is more or less robust than SGD solutions.

**Evidence from literature:**
- No paper in the corpus addresses robustness, adversarial examples, or sensitivity analysis of convex neural network solutions.
- Mishkin and Pilanci [Mishkin2023Optimal] characterize the *set* of optimal solutions as polyhedral, which could imply sensitivity results, but do not study perturbation behavior.
- The implicit regularization results [Ergen2021BN, ErgenPilanci2023Lasso] characterize what solutions are preferred but not their robustness properties.

**Scoring:**
- Confidence of Existence: 8/10 -- Verified absence of robustness analysis in the corpus. This is a natural stress-test of the convex framework.
- Potential Impact: 5/10 -- Robustness is important for deployment but this is an empirical characterization question rather than a theoretical advance.
- Feasibility: 8/10 -- Straightforward to test: train networks with convex solvers and SGD, then evaluate on perturbed inputs.
- Verifiability: 9/10 -- Robustness metrics (accuracy under perturbation, certified radius) are well-established.
- Empirical Testability: 8/10 -- Can directly use SCNN or CRONOS to train convex networks and compare robustness to SGD-trained networks. Existing adversarial attack libraries apply.
- **Composite: (8x2 + 5 + 8 + 9 + 8) / 6 = 7.7/10**

**Source lookup used:** No.

**Proposed research direction:** Train two-layer ReLU networks using both SCNN (convex) and SGD (non-convex) on MNIST/CIFAR-10 subsets. Compare robustness to (a) random noise perturbations, (b) FGSM adversarial attacks, (c) label noise. Test whether the convex global optimum is more or less robust than typical SGD stationary points.

---

### Gap 3.3: Empirical Comparison of Solution Sparsity: Convex vs SGD Training

**Claim:** The convex formulation induces group $\ell_1$ regularization, which promotes sparsity in neuron activations. Whether convex-trained networks are empirically sparser than SGD-trained networks, and how this affects interpretability and pruning, has not been systematically studied.

**Evidence from literature:**
- Multiple papers note that group $\ell_1$ regularization induces sparsity [PilanciErgen2020, ErgenPilanci2021Deep, ErgenPilanci2023Lasso].
- Mishkin and Pilanci [Mishkin2023Optimal] develop optimal pruning algorithms for convex networks, showing that minimal-neuron representations can be computed from the polyhedral solution set.
- However, no paper provides a systematic empirical comparison of sparsity levels between convex-trained and SGD-trained networks across datasets.

**Scoring:**
- Confidence of Existence: 8/10 -- The sparsity-inducing property is well-established theoretically, but the empirical comparison to SGD is absent.
- Potential Impact: 4/10 -- Confirms a known theoretical property rather than advancing the theory. However, practical implications for model compression make this useful.
- Feasibility: 9/10 -- Straightforward comparison using existing tools.
- Verifiability: 9/10 -- Sparsity can be measured directly (number of active neurons, weight magnitudes).
- Empirical Testability: 9/10 -- Can use existing SCNN code and standard PyTorch SGD training, then count active neurons.
- **Composite: (8x2 + 4 + 9 + 9 + 9) / 6 = 7.8/10**

**Source lookup used:** No.

**Proposed research direction:** Train identical two-layer ReLU architectures on MNIST and CIFAR-10 using SCNN (convex) and SGD (non-convex) with matching regularization strength. Compare: number of active neurons, weight sparsity patterns, effect of pruning on accuracy, and whether convex solutions are closer to the minimal-neuron representations characterized by Mishkin and Pilanci.

---

## Rejected Candidates

### Rejected 1: "Convex Reformulation for Transformer Architectures"

**Reason for rejection:** While no paper in the corpus addresses transformers, this is outside the scope of the research field. The convex duality framework is built on the piecewise-linear structure of ReLU activations and does not naturally extend to the attention mechanism. This is a different research program entirely, not a gap in this one. Absence of transformer work in a ReLU duality corpus is expected, not a gap.

### Rejected 2: "Convex Training on Larger Datasets (Beyond ImageNet)"

**Reason for rejection:** This is a resource gap, not an intellectual gap. CRONOS [Feng2023CRONOS] already scales to ImageNet. "Apply the same method to more data" is not a research question -- it is an engineering challenge. The pipeline instructions explicitly prohibit listing "more data" or "better compute" as research gaps.

### Rejected 3: "Extending Convex Duality to Non-ReLU Smooth Activations (Sigmoid, Tanh)"

**Reason for rejection:** Partially addressed. Bartan and Pilanci [BartanPilanci2021] already extend beyond ReLU to polynomial activations. Ergen and Pilanci [ErgenPilanci2023Lasso] cover all piecewise linear activations (leaky ReLU, absolute value). For smooth non-piecewise-linear activations like sigmoid and tanh, the piecewise-linear structure that enables the reformulation does not exist, making this a fundamental limitation rather than an open gap. The field has already explored the boundary of where the technique applies.

### Rejected 4: "Tighter Bounds on the Number of Hyperplane Arrangements P"

**Reason for rejection:** This is partially addressed. Kim and Pilanci [Kim2024] show that Gaussian random relaxations avoid the exponential dependence on rank by achieving $O(\sqrt{\log n})$ approximation guarantees. Additionally, the hyperplane arrangement count is a combinatorial property of the data matrix that is well-studied in discrete geometry. The practical impact of tighter bounds is subsumed by the approximation algorithms.

### Rejected 5: "Convex Duality for Classification Losses (Cross-Entropy, Hinge)"

**Reason for rejection:** Partially addressed. Wang and Pilanci (cited in Kim2024, line 66 reference) analyze hinge loss through convex duality. The corpus focuses on squared loss for theoretical clarity, but the methodology has been applied to other losses. This is incremental extension work rather than a fundamental gap.

### Rejected 6: "Multi-GPU / Distributed Convex Training"

**Reason for rejection:** This is a systems engineering challenge, not a research gap. CRONOS is already implemented in JAX which supports multi-GPU via pmap. Scaling to distributed settings is an engineering concern about memory and communication, not about duality or convexity.
