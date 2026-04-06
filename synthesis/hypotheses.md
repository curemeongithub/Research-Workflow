---
phase: 6
status: complete
timestamp: 2026-04-06T00:00:00Z
depends_on: [analysis/gap-analysis.md, analysis/review-notes.md, analysis/literature-map.md]
token_estimate: 4200
source_lookups_used: 3
---

# Hypotheses: Dual Convex Optimization in ReLU Neural Networks

## Hypothesis Formation Summary

Seven hypotheses are formulated from the validated gap analysis, adjusted by Phase 5 advisory
constraints. Three primary (Tier 1) hypotheses address the highest-confidence gaps: the duality
gap for standard deep ReLU restricted to the rank-1 / L=3 sub-case (Gaps 1.1 + 2.4, merged per
Phase 5), the polynomial-time approximation guarantee for RIP-satisfying non-Gaussian data (Gap
1.2), and end-to-end convergence for CRONOS-AM (Gap 1.3, treated as secondary Tier 1). Four
secondary (Tier 2) hypotheses address: generalization bounds via the Carathéodory group-sparse
structure (Phase 5 Missing Gap A — highest-impact omission), batch normalization integration (Gap
2.1), polynomial-time approximation for logistic loss (Gap 2.2), and a CIFAR-10-scale mechanistic
probe of NTK vs. convex duality predictions (Gap 2.3, rescoped per Phase 5). Gaps 3.1 and 3.2
(Tier 3) are excluded as infeasible for hypothesis formation. Gap 1.1 and Gap 2.4 are merged into
a single research thread (H1) per the Phase 5 advisory recommendation.

---

## Primary Hypotheses (Tier 1)

---

## Hypothesis 1: Zero-Gap Singular-Value Condition for Standard Three-Layer ReLU (Merged 1.1 + 2.4)

**Source gap:** Gap 1.1 (Duality Gap Characterization for Standard Deep ReLU, L ≥ 3) + Gap 2.4
(Minimal Structural Conditions for Zero Duality Gap) — merged per Phase 5 advisory.  
**Sanity check status:** LOW concern (gap confirmed); MEDIUM concern (feasibility of general case
overstated — hypothesis restricted to rank-1 data and L=3, per Phase 5).

**Statement:** For a standard (non-parallel) three-layer ReLU network trained on a rank-1 data
matrix $X = \mathbf{x}\mathbf{y}^T \in \mathbb{R}^{n \times d}$ with squared-loss weight-decay
regularization, the duality gap is zero if and only if the post-first-ReLU-layer effective data
matrix $\widetilde{X} = D_1 X$ satisfies an equal-singular-values condition on the subspace relevant
to the output layer, analogously to the exact characterization proven for deep linear networks in
\[Wang&Ergen&Pilanci2023\].

**Rationale:** The duality analysis of deep linear networks yields an exact formula for the duality
gap in terms of the singular values of $X^\dagger Y$ \[Wang&Ergen&Pilanci2023\]. For standard
three-layer ReLU networks, \[Wang&Ergen&Pilanci2023\] proves the zero-gap case only for rank-1 data
(scalar output), marking the general case as "Not Proven" in Table 1. The bi-dual equivalence
between standard and parallel architectures holds for deep linear networks; this hypothesis posits
that restricting to rank-1 data tames the tensor-product interaction between ReLU layers enough to
permit a direct transfer of the equal-singular-values criterion from the linear case. The
Carathéodory bound $m^* \leq n+1$ (confirmed in `arxiv-2002.10553/content.md:60`) ensures the
bi-dual is attained, which is the key starting point for the gap formula derivation. Merging Gap
2.4 is natural: setting the duality gap formula to zero yields the minimal structural condition.

**Measurable prediction:** Constructing the convex reformulation of the rank-1 three-layer standard
ReLU problem and enumerating the primal-dual optimal pair for small $(n, d)$ instances (e.g.,
$n = 20, d = 5$) should yield duality gap = 0 precisely when the equal-singular-values condition on
$\widetilde{X}$ is satisfied, and duality gap > 0 otherwise. The gap should be expressible as a
closed-form function of the deviation from equal singular values.

**Falsification condition:** Finding a rank-1, L=3 standard ReLU instance where the duality gap
is non-zero despite the equal-singular-values condition holding, or where the gap is zero despite
the condition failing, would falsify this hypothesis. Alternatively, finding that the gap depends
on a strictly different structural quantity (e.g., the arrangement pattern count rather than
singular value equality) would require revision.

**Priority:** Tier 1

**FATS check:**
- Falsifiable: YES — the equal-singular-values condition is checkable; a counterexample in a
  small exact computation would suffice.
- Actionable: YES — the rank-1 / L=3 sub-case is computationally tractable; exact enumeration
  of all $O((n/r)^r)$ hyperplane arrangement patterns is feasible for $r=1$.
- Testable: YES — duality gap is computable as primal minus dual optimal value for small instances.
- Specific: YES — rank-1 data, L=3 architecture, squared loss, weight decay, equal-singular-values
  condition on $\widetilde{X} = D_1 X$ are all named precisely.

---

## Hypothesis 2: O(√log n) Approximation Bound Extends to RIP-Satisfying Data

**Source gap:** Gap 1.2 (Polynomial-Time Approximation Guarantees for General Non-Gaussian Data)  
**Sanity check status:** LOW concern — gap confirmed, feasibility appropriate at 2/3.

**Statement:** The $O(\sqrt{\log n})$ relative optimality bound of \[Kim&Pilanci2024\] for the
convex relaxation of two-layer ReLU network training extends from Gaussian i.i.d. data to any data
matrix $X \in \mathbb{R}^{n \times d}$ satisfying the $(s, \delta)$-restricted isometry property
on the hyperplane arrangement feature map $\Phi: \mathbb{R}^d \to \mathbb{R}^P$ (where $P$ counts
distinct arrangements), with the same relaxation width $m = O(\log n)$ and the same $O(\sqrt{\log n})$
relative error, provided the cone sharpness condition underlying \[Kim&Pilanci2024\] Lemma 21 holds
for RIP matrices with parameter $\delta < 1/2$.

**Rationale:** \[Kim&Pilanci2024\] uses Gordon's comparison inequality \[Thrampoulidis2014\] to
bound the cone sharpness and thereby prove Theorem 2.1. The paper explicitly identifies RIP as the
extension path: "a connection to restricted isometry property could be a key to extending the result
to different distributions. Here, we assume Gaussianity for simplicity"
(`arxiv-2402.03625/content.md:62`). The RIP condition is a well-established surrogate for
Gaussianity in compressed sensing theory; the fact that the cone-sharpness argument requires bounding
$\lambda_{\min}(\mathcal{M})$ (where $\mathcal{M}$ is the Gram matrix of the arrangement feature
map) is precisely the quantity that RIP controls. The Mendelson \[2007\] empirical process result,
also cited in the paper, provides an alternative route that avoids Gordon's inequality entirely and
applies to sub-Gaussian distributions, potentially yielding RIP as a special case.

**Measurable prediction:** For a data matrix $X$ drawn from a sub-Gaussian distribution whose
covariance satisfies the RIP condition with $\delta < 1/2$ on the size-$s$ subsets of arrangement
patterns, the convex relaxation with $m = O(\log n)$ width should achieve relative training error
at most $C\sqrt{\log n}$ for a constant $C$ independent of the distribution (differing from the
Gaussian constant only in the RIP-dependent prefactor). Empirically, running CRONOS on data from a
structured distribution (e.g., Bernoulli$(\pm 1)$ entries, which satisfies RIP with high
probability) and measuring the relative gap to the full convex reformulation should yield
$O(\sqrt{\log n})$ scaling consistent with the Gaussian case.

**Falsification condition:** Constructing a data matrix satisfying RIP on the arrangement feature
map with $\delta < 1/2$, yet for which the relative optimality gap of the $O(\log n)$-width
relaxation scales as $\omega(\sqrt{\log n})$, would falsify this hypothesis.

**Priority:** Tier 1

**FATS check:**
- Falsifiable: YES — the $O(\sqrt{\log n})$ scaling is empirically testable for RIP-satisfying
  distributions.
- Actionable: YES — RIP-satisfying matrices (Bernoulli, Haar random orthogonal) are constructible;
  the RIP condition on the arrangement map is verifiable for small $(n, d)$.
- Testable: YES — relative optimality gap is a directly computable scalar, measurable by comparing
  width-$m$ relaxation to full reformulation.
- Specific: YES — $(s, \delta)$-RIP with $\delta < 1/2$, width $m = O(\log n)$, $O(\sqrt{\log n})$
  relative error, two-layer ReLU, squared loss are all specified.

---

## Hypothesis 3: CRONOS-AM Satisfies Monotone Lyapunov Descent Under Bounded Early-Layer Step Size

**Source gap:** Gap 1.3 (End-to-End Convergence Guarantees for CRONOS-AM)  
**Sanity check status:** LOW–MEDIUM concern (gap confirmed; theoretical convergence guarantee is
hard and has limited practical impact relative to H1/H2 — treated as secondary Tier 1).

**Statement:** When CRONOS-AM is applied to a multi-layer ReLU network such that the early-layer
DAdapted-Adam step size $\eta_t$ satisfies $\eta_t \leq \varepsilon / \|\nabla \mathcal{L}_t\|$
for a feasibility-disturbance tolerance $\varepsilon > 0$, the optimal value of the CRONOS-solved
convex sub-problem decreases (weakly) monotonically across alternating minimization iterations,
establishing a Lyapunov descent certificate for CRONOS-AM.

**Rationale:** \[Feng&Frangella&Pilanci2023\] (`arxiv-8652_CRONOS/content.md:366`) explicitly asks
whether a convergence guarantee for CRONOS-AM can be proven. The Lyapunov approach is the canonical
strategy for two-block alternating minimization where one block is convex (CRONOS on the last two
layers) and one is non-convex (DAdapted-Adam on earlier layers). The key technical obstacle is
bounding how much the early-layer update shifts the input distribution presented to the convex sub-
problem, which distorts the feasibility constraints. A step-size bound of the form $\eta_t \leq
\varepsilon / \|\nabla \mathcal{L}_t\|$ limits this disturbance to $\varepsilon$ in gradient-norm
units, potentially ensuring the convex sub-problem's optimal value cannot increase across
iterations.

**Measurable prediction:** Implementing CRONOS-AM with and without the bounded step-size rule on
a three-layer ReLU network (e.g., the UCI datasets in \[Feng&Frangella&Pilanci2023\] Table 2), the
convex sub-problem's optimal value sequence should be non-increasing in the bounded case and may
oscillate in the unbounded case. Convergence to a stationary point should be empirically faster
and more reliable in the bounded case.

**Falsification condition:** Demonstrating a benchmark where the CRONOS sub-problem's optimal value
increases across alternating minimization iterations even under the bounded step-size rule would
falsify the Lyapunov property. Alternatively, showing that the step-size bound required for
monotone descent is so small as to prevent any meaningful optimization of the early layers would
make the hypothesis vacuous.

**Priority:** Tier 1 (secondary)

**FATS check:**
- Falsifiable: YES — monotone descent is empirically verifiable; a counterexample run suffices.
- Actionable: YES — CRONOS is an existing codebase; the step-size modification is implementable.
- Testable: YES — convex sub-problem optimal values are logged per CRONOS-AM iteration.
- Specific: YES — step-size bound $\eta_t \leq \varepsilon / \|\nabla \mathcal{L}_t\|$, CRONOS-AM
  architecture split, monotone descent property are all specified.

---

## Secondary Hypotheses (Tier 2)

---

## Hypothesis 4: Generalization Bound from Group-Sparse Dual via Carathéodory Complexity

**Source gap:** Phase 5 Missing Gap A (Generalization Bounds from the Convex Dual Program) — new
Tier 2 gap identified in sanity check; absent from corpus.  
**Sanity check status:** HIGH concern (entirely absent from corpus) / but gap is genuine and
actionable — Phase 5 recommends treating as new Tier 2.

**Statement:** A two-layer ReLU network trained to the global minimum of the weight-decay
regularized problem (or to the $O(\sqrt{\log n})$ approximate minimum via the convex relaxation)
achieves generalization error bounded by $O\!\left(\sqrt{k^*/n}\right)$, where $k^* \leq n+1$ is
the number of active hyperplane arrangement patterns in the group-sparse dual solution (Carathéodory
bound), derived via a compression argument that treats the dual-selected arrangement patterns as the
effective hypothesis class.

**Rationale:** The entire convex duality framework provides training optimality guarantees but is
silent on test error. The group-sparse structure of the dual solution — specifically, that the
optimal solution is supported on at most $k^* \leq n+1$ hyperplane arrangement patterns
(`arxiv-2002.10553/content.md:60`; `arxiv-2402.03625/content.md:56`) — directly limits the
effective complexity of the learned function. Compression-based generalization bounds (Arora et al.
2018; Gunasekar et al., cited as `arxiv-1710.10174` in the corpus) bound the test error by
$O(\sqrt{(\text{description length of compressed model}) / n})$. Here, $k^*$ is the description
length in arrangement-pattern units: a network supported on $k^*$ patterns from the exponentially
large pattern library is a compressed model with $O(k^* d)$ effective parameters. When $k^* \ll n$
(which holds empirically per \[Kim&Pilanci2024\] line 80: "as $m^*$ is much smaller than $n+1$ in
practice"), this would yield a non-trivial bound tighter than standard Rademacher complexity for the
full network class.

**Measurable prediction:** For a synthetic dataset of size $n$ with rank-$r$ input data, the
dual-optimal support size $k^*$ should scale as $o(n)$ (e.g., as $O(n^{1/2})$ or $O(r \log n)$),
and the empirical test error should correlate with $\sqrt{k^*/n}$ across varying $n$, consistent
with the compression bound's prediction. The bound should tighten as $k^*$ decreases (smaller
networks, stronger regularization, lower-rank data).

**Falsification condition:** Finding a family of datasets where $k^*/n \to 0$ (the bound predicts
improving generalization), yet test error does not decrease, would falsify the bound's tightness.
Alternatively, if $k^* = \Theta(n)$ universally (the Carathéodory bound is always tight), the bound
reduces to $O(1)$ and provides no information.

**Priority:** Tier 2

**FATS check:**
- Falsifiable: YES — the $\sqrt{k^*/n}$ scaling is testable by varying $n$ and measuring $k^*$
  from the dual solution.
- Actionable: YES — arithmetic and compression bound machinery is standard; the dual solution $k^*$
  is computable from CRONOS output.
- Testable: YES — $k^*$ is a directly readable scalar from the convex dual solution support; test
  error is the standard evaluation metric.
- Specific: YES — $k^* \leq n+1$ (Carathéodory), $O(\sqrt{k^*/n})$ rate, two-layer ReLU, weight
  decay, compression argument are all named.

---

## Hypothesis 5: Fixed-Point BN Admits a Convex Equivalent with BN-Adjusted Group-Norm Regularizer

**Source gap:** Gap 2.1 (Integration of Layer-Wise Batch Normalization with Full Convex Duality)  
**Sanity check status:** LOW concern — gap confirmed as genuine and partially open.

**Statement:** When batch normalization is applied at every intermediate layer of a two-layer ReLU
network and is evaluated at the fixed point of its running statistics $(\hat{\mu}, \hat{\sigma})$,
the resulting training problem is equivalent to a convex program with a BN-adjusted group-norm
regularizer whose group structure is identical to the standard (non-BN) convex reformulation, and
strong duality holds under the same hyperplane arrangement parameterization.

**Rationale:** \[Ergen&Pilanci2021reveal\] proves that BN before the final linear layer removes the
whitened/rank-1 data requirement and induces neural collapse. The mechanism is that, at the fixed
point, BN acts as an affine reparameterization of the pre-activation data matrix, replacing $X$
with $\text{BN}(X) = \hat{\sigma}^{-1}(X - \hat{\mu}\mathbf{1}^T)$. If the fixed-point BN
statistics can be incorporated as a deterministic affine transformation of the data matrix before
entering the semi-infinite dual, the per-sample independence structure assumed by the dual
derivation is preserved (since BN at fixed point is just a linear operator on $X$). The only
modification to the convex program is in the effective data matrix; the group-norm regularizer
derived from the hyperplane arrangement cone structure is unchanged.

**Measurable prediction:** Training a two-layer ReLU network with fixed-point BN using both
gradient descent and the proposed convex program (with $\text{BN}(X)$ substituting for $X$) should
yield the same training objective value at convergence, with the convex program's global minimum
matching the non-convex SGD optimum in a controlled small-scale experiment ($n = 50, d = 10$).

**Falsification condition:** Finding that the fixed-point BN convex program's optimal value differs
from the non-convex BN training problem's empirical minimum (confirmed across multiple random
initializations) would falsify the equivalence. This would indicate that the fixed-point
approximation breaks the duality or that inter-sample coupling from BN's batch normalization
statistics cannot be captured by a single affine substitution.

**Priority:** Tier 2

**FATS check:**
- Falsifiable: YES — primal–dual gap is computable; a non-zero gap at fixed-point BN would falsify.
- Actionable: YES — fixed-point BN is easily implemented; the BN-adjusted data matrix is a simple
  preprocessing step.
- Testable: YES — training objective equality is a directly measurable scalar comparison.
- Specific: YES — fixed-point BN statistics, affine substitution $X \to \text{BN}(X)$, two-layer
  ReLU, group-norm structure preserved are all specified.

---

## Hypothesis 6: Self-Concordance Extends the O(√log n) Bound to Logistic Loss

**Source gap:** Gap 2.2 (Polynomial-Time Approximation Guarantees for Non-Squared Loss Functions)  
**Sanity check status:** LOW concern — gap confirmed; Phase 5 notes logistic loss + self-
concordance is the most concrete path.

**Statement:** The $O(\sqrt{\log n})$ relative optimality bound for the convex relaxation of
two-layer ReLU network training (Theorem 2.1 of \[Kim&Pilanci2024\]) extends to logistic loss
under the same Gaussian data assumption (A1), with the Gordon's comparison step replaced by a
self-concordance coupling argument that bounds the change in optimal hyperplane arrangement
patterns when the squared loss is perturbed to logistic loss by a Lipschitz output-space mapping.

**Rationale:** \[Kim&Pilanci2024\] restricts exclusively to squared loss; its key technical step is
bounding the cone sharpness using Gordon's comparison on the output-space dual variable. For logistic
loss, the gradient is $\nabla \ell = \sigma(-y\hat{y}) \cdot \mathbf{1}$ where $\sigma$ is the
sigmoid — a bounded, Lipschitz function of the network output. Self-concordance of logistic loss
implies that Newton's method converges in $O(\log \log(1/\varepsilon))$ steps, providing a local
quadratic approximation that mirrors squared loss up to a multiplicative constant in the output
curvature. If the Lipschitz constant of $\nabla_{\hat{y}} \ell$ is bounded, the dual variable
perturbation from squared to logistic loss is bounded, and the arrangement patterns selected by the
dual do not change catastrophically. Phase 5 advisory (`review-notes.md`) explicitly identifies
self-concordance as the "more concrete and actionable hypothesis" for Gap 2.2.

**Measurable prediction:** For Gaussian data (satisfying A1) and binary classification with logistic
loss, the relative gap between the width-$O(\log n)$ relaxation and the full convex reformulation
should scale as $O(\sqrt{\log n})$ empirically, consistent with the squared-loss result. The
constant in the bound may change (proportional to the logistic loss's self-concordance parameter),
but the $\sqrt{\log n}$ scaling should be preserved across $n \in \{50, 100, 500, 1000\}$.

**Falsification condition:** Empirically observing that the relative optimality gap for logistic
loss scales as $\omega(\sqrt{\log n})$ on Gaussian data (where the squared-loss version provably
scales as $O(\sqrt{\log n})$), using the same relaxation width, would falsify the $\sqrt{\log n}$
extension to logistic loss.

**Priority:** Tier 2

**FATS check:**
- Falsifiable: YES — $O(\sqrt{\log n})$ vs. $\omega(\sqrt{\log n})$ scaling is empirically
  distinguishable by fitting a log-log regression across multiple $n$ values.
- Actionable: YES — the CRONOS codebase supports logistic loss; the full convex reformulation
  is computable for small $(n, d)$ to obtain the reference optimum.
- Testable: YES — relative optimality gap is a directly computable scalar from two runs of CRONOS.
- Specific: YES — logistic loss, Gaussian data (A1), width $O(\log n)$, self-concordance coupling,
  $O(\sqrt{\log n})$ rate, two-layer ReLU are all specified.

---

## Hypothesis 7: Active Arrangement Sparsity Anti-Correlates with NTK Alignment at CIFAR-10 Scale

**Source gap:** Gap 2.3 (Empirical Scale Test of NTK vs. Convex Duality Feature Learning) —
rescoped from ImageNet to CIFAR-10 per Phase 5 advisory (MEDIUM concern at ImageNet; 2/3
feasibility at CIFAR scale).

**Statement:** On CIFAR-10 with a three-layer ReLU network (width $m \in \{100, 200, 500\}$),
the relative dual support sparsity $k^*/m$ of the convex dual solution (fraction of active
hyperplane arrangement patterns) is negatively correlated (Spearman $\rho < -0.5$) with the
Centered Kernel Alignment (CKA) between learned intermediate representations and the NTK-predicted
kernel, across varying width and regularization strength, indicating that richer feature learning
(departing from the NTK regime) corresponds to sparser arrangement selection in the dual.

**Rationale:** The NTK regime corresponds to lazy training where features do not move from
initialization; the convex duality regime corresponds to active hyperplane arrangement selection
driven by the group-lasso dual program. These make opposite predictions about the learned feature
structure: NTK predicts high CKA alignment with the initialization kernel, while the convex duality
predicts low CKA alignment (features have departed from initialization) but also predicts sparse
support in the dual (the network uses only $k^*$ of the $O((n/r)^r)$ available patterns). The Phase
5 advisory narrows the research direction to a CIFAR-10-scale probe with a specified measurement
protocol: $k^*$ from the dual solution and CKA between learned features and the NTK kernel.
The [user-2110.05518v2] paper already validates the L=3 convex program on CIFAR-10 ($n = 5 \times
10^4$) (`user-2110.05518v2/content.md:353`), confirming the implementation is feasible.

**Measurable prediction:** For three-layer ReLU networks of increasing width on CIFAR-10, as
regularization strength (weight decay $\lambda$) decreases from large to small: (a) $k^*$ should
decrease (sparser solutions for stronger regularization, consistent with group lasso), (b) NTK-CKA
should increase (weaker regularization induces more feature movement away from initialization), and
(c) these two trends should be anti-correlated with Spearman $\rho < -0.5$ across
$(m, \lambda) \in \{100, 200, 500\} \times \{10^{-4}, 10^{-3}, 10^{-2}\}$.

**Falsification condition:** Finding that $k^*$ and NTK-CKA are uncorrelated (Spearman $|\rho| <
0.2$) across the $(m, \lambda)$ grid, or finding that $k^*$ is uniformly close to $m$ (the dual is
always dense, consistent with the NTK regime), would falsify the hypothesis that the convex duality
regime is empirically active at CIFAR-10 scale.

**Priority:** Tier 2

**FATS check:**
- Falsifiable: YES — Spearman correlation with a threshold of $\rho < -0.5$ is a well-defined
  falsification criterion.
- Actionable: YES — the three-layer convex program on CIFAR-10 is already validated in
  `user-2110.05518v2`; CKA is a standard metric with available implementations.
- Testable: YES — both $k^*$ (dual support) and CKA are computable scalars per experimental run.
- Specific: YES — CIFAR-10, three-layer ReLU, width 100–500, weight decay grid, Spearman $\rho$
  threshold, dual support $k^*$, NTK-CKA are all specified.

---

## Excluded Gaps and Reasoning

| Gap ID | Reason for Exclusion |
|--------|----------------------|
| Gap 3.1 (Attention / Transformer) | Tier 3; Feasibility 1/3 confirmed by Phase 5. The hyperplane arrangement construction is specific to piecewise-linear ReLU; softmax attention has no natural analog. Excluded as infeasible for near-term hypothesis formation. |
| Gap 3.2 (Adam implicit regularization) | Tier 3; Feasibility 1/3 confirmed by Phase 5. Adam's implicit regularization is uncharacterized even outside this framework. Empirical characterization is the correct first step; insufficient theoretical grounding for a testable hypothesis at this stage. |

---

## Hypothesis Dependency Map

```
H1 (rank-1 duality gap formula)
  └─→ H4 (generalization bound): H4 uses the Carathéodory bound k* ≤ n+1, which
        is established independently, but a tighter k* estimate may follow from
        the rank-1 gap formula in H1 (lower-rank data → fewer active patterns).
        H4 is semi-independent but benefits from H1's solution.

H2 (RIP extension of O(√log n) bound)
  └─→ H6 (logistic loss extension): Both share the same proof architecture
        (modifying Gordon's comparison in Kim&Pilanci2024 Theorem 2.1). H6 is
        parallel to H2, not dependent on it; the two modifications (RIP vs.
        self-concordance) can be pursued independently as alternative entry points
        into Theorem 2.1.

H7 (CIFAR-10 sparsity / NTK probe)
  └─→ H4 (generalization bound): If H7 confirms that k* < n empirically on CIFAR-10,
        this strengthens the motivation for H4's compression bound (a non-trivial
        k*/n ratio enables a meaningful generalization guarantee).

H3 (CRONOS-AM Lyapunov descent)
  Independent of all other hypotheses.

H5 (fixed-point BN)
  Independent of all other hypotheses.
```
