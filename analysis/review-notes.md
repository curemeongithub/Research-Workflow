---
phase: 5
status: complete
timestamp: 2026-04-07T19:50:00Z
depends_on: [analysis/literature-map.md, analysis/gap-analysis.md]
advisory: true
---

# Sanity Check Review Notes: Duality Gap in Dual Convex Optimization in ReLU Neural Networks

> **Advisory only.** These notes inform the next phases but do not block the pipeline.
> Phase 6 (Hypothesis Formation) should treat HIGH CONCERN flags as strong signals to downweight those gaps.

## Overall Assessment

The gap analysis is generally well-grounded and demonstrates careful source verification. The Tier 1 gaps are genuine open problems confirmed by direct inspection of Table 1 in Wang et al. (2021) and the CRONOS conclusion. The main concerns are: (1) several Tier 2 gaps conflate "not studied in this corpus" with "not studied anywhere," which risks re-discovering known results from adjacent fields; (2) the feasibility of Gap 1.1 may be underestimated because computing the dual value for standard deep ReLU networks requires formulating the dual problem itself, which does not yet exist in closed form; and (3) the scoring feels slightly inflated for gaps that are primarily empirical characterization exercises rather than theoretical advances.

## Per-Gap Review

### Gap 1.1: Empirical Characterization of the Duality Gap for Standard Deep ReLU Networks (L>=3)
**Concern level:** MEDIUM
**Issue:** The gap is real -- Table 1 confirms it with "X" for standard ReLU at L=3 and L>3. However, the feasibility rating of 7/10 may be optimistic. Computing the duality gap requires both the primal optimal value (standard non-convex training, feasible) and the dual optimal value. For standard deep ReLU networks, the dual problem has not been explicitly formulated -- Wang et al. only derive the dual for linear activations and parallel architectures. The gap analysis assumes existing convex solvers can compute the dual, but no existing solver handles the standard deep ReLU dual. The researcher would need to either (a) derive the dual formulation themselves (a theoretical contribution, not just an experiment) or (b) use bounds/relaxations, which would only give one-sided estimates of the gap.
**Recommendation:** Proceed, but reframe -- this may require theoretical derivation of the dual for standard deep ReLU before empirical measurement is possible. The feasibility score should be mentally downweighted to 5-6/10 given this prerequisite.
**Source lookup result:** Table 1 at lines 56-66 of sources/arxiv-2110.06482/content.md confirmed: standard ReLU L=3 and L>3 both marked "X" (no characterization exists). Rank-1 case is treated in appendix (line 991).

### Gap 1.2: Optimality Gap of CRONOS-AM (Alternating Minimization for Deep Convex Networks)
**Concern level:** LOW
**Issue:** This is a well-identified gap. The CRONOS paper explicitly asks for convergence guarantees in its conclusion (line 366). One minor nuance: CRONOS does claim "convergence guarantees to global minimum under mild assumptions" for the two-layer case (line 46 of the paper), so the gap is specifically about the alternating minimization extension to deep networks, not CRONOS itself. The gap analysis correctly identifies this distinction. The feasibility rating of 8/10 is reasonable since the CRONOS codebase is public and the experiment design (compare AM solution to exact convex solution on small instances) is straightforward.
**Recommendation:** Proceed as-is. This is the strongest gap for empirical investigation.
**Source lookup result:** Line 366 of sources/user-8652-CRONOS/content.md confirmed the open question. Line 46 confirms two-layer guarantees exist.

### Gap 2.1: Effect of Regularizer Choice on the Duality Gap
**Concern level:** MEDIUM
**Issue:** The gap is genuine within the corpus, but the broader optimization literature may contain relevant results. The rescaling lemma (converting L2 weight decay to L1 on output weights) is specific to the L2 regularizer structure. With elastic net or spectral norm, this rescaling does not apply, meaning the entire convex reformulation pipeline breaks at step 1. This makes the gap less about "does the duality gap change?" and more about "can the reformulation even be constructed?" -- which is a harder, more fundamental question than the gap analysis suggests. The feasibility of "substituting different regularizers into the convex reformulation framework" is lower than implied because the framework itself may not accommodate them.
**Recommendation:** Reframe -- the research direction should first ask whether the reformulation is possible at all, not just whether the gap changes. Feasibility should be downweighted to 5-6/10.

### Gap 2.2: Relationship Between Duality Gap and Generalization
**Concern level:** MEDIUM
**Issue:** The grep for "generalization" across all sources returned zero matches, confirming this is unstudied within the corpus. However, the broader machine learning theory literature extensively studies the relationship between optimization error and generalization (e.g., stability-based generalization bounds, algorithmic regularization). The gap analysis appropriately notes this caveat (Confidence 7/10, mentioning "external work may exist"), but the proposed research direction does not engage with the existing optimization-generalization literature. A researcher pursuing this would need to position against that external body of work, which increases the effort and risk of re-discovery.
**Recommendation:** Proceed with caution. The empirical experiment is feasible, but the theoretical framing needs engagement with the generalization theory literature beyond this corpus.

### Gap 2.3: Scalability of Kim et al.'s Approximation Guarantee
**Concern level:** LOW
**Issue:** This is a clean, well-scoped empirical gap. The theoretical bound exists but empirical tightness is untested. The feasibility rating of 8/10 is fair. One concern: implementing the randomized relaxation from the paper may require understanding the proof construction to set up the correct random projection, which could be non-trivial. But the experiment design is otherwise straightforward.
**Recommendation:** Proceed as-is. Good candidate for a tractable empirical contribution.

### Gap 2.4: Convex Duality Beyond Rank-1 for Standard Deep ReLU
**Concern level:** LOW
**Issue:** This is closely related to Gap 1.1 and faces the same dual-formulation challenge -- without the dual problem for standard deep ReLU networks, measuring the duality gap requires bounding rather than exact computation. However, for rank-2 and rank-3, the problem is small enough that brute-force approaches (e.g., enumerating hyperplane arrangements) might be feasible. The gap is real and well-supported by Table 1.
**Recommendation:** Proceed as-is, but note the dependency on Gap 1.1's feasibility. If the dual cannot be formulated for standard deep ReLU, this gap inherits the same limitation. Consider combining with Gap 1.1 as a single research thrust.

### Gap 2.5: Finite-Sample Scaling of Convex Equivalence
**Concern level:** MEDIUM
**Issue:** The Confidence score of 6/10 is appropriate -- this feels more like "no one bothered to study this" than "this is a meaningful open question." The scaling of hyperplane arrangements with n is already given by the combinatorial bound $P \leq 2r(e(n-1)/r)^r$, so the theoretical scaling is known. The proposed experiment (vary n and measure P, solve time, etc.) would primarily confirm known bounds rather than discover new phenomena. The impact score of 6/10 may be generous.
**Recommendation:** Downweight. This is the weakest Tier 2 gap -- it is more of a computational benchmark than a research question. If resources are limited, skip this in favor of Gaps 2.3 or 2.4.

### Gap 3.1: Gated ReLU Equivalence Beyond Two Layers
**Concern level:** LOW
**Issue:** Well-identified, appropriately tiered. The impact score of 5/10 is fair given that parallel architectures already provide an alternative path to deep convex training.
**Recommendation:** Proceed as-is for Tier 3.

### Gap 3.2: Robustness of Convex Optimum to Data Perturbation
**Concern level:** LOW
**Issue:** Clean empirical question, appropriately tiered. The experimental design is straightforward using existing tools.
**Recommendation:** Proceed as-is for Tier 3.

### Gap 3.3: Solution Sparsity Comparison
**Concern level:** LOW
**Issue:** The impact score of 4/10 is honest and appropriate. This is confirmatory work rather than discovery. The composite score of 7.8/10 seems high for a Tier 3 gap with 4/10 impact -- the high feasibility/verifiability scores pull it up, which may mislead prioritization.
**Recommendation:** Proceed as-is, but note that the composite score overweights feasibility relative to impact for this gap.

## Feasibility Flags

1. **Gap 1.1 (Standard Deep ReLU Duality Gap):** The dual problem for standard deep ReLU networks has not been derived. Computing the duality gap requires knowing both primal and dual values. This is a prerequisite theoretical contribution, not just an experiment. Feasibility is lower than rated.

2. **Gap 2.1 (Regularizer Choice):** The entire convex reformulation pipeline depends on the L2-to-L1 rescaling lemma, which is specific to L2 regularization. Alternative regularizers may break the reformulation at step 1, making the question more fundamental than "how does the gap change."

3. **Gap 2.4 (Beyond Rank-1):** Inherits the dual-formulation challenge from Gap 1.1 for standard deep architectures.

## Consistency Issues

1. **Literature map and gap analysis are well-aligned.** The contested areas in Section 6 of the literature map (duality gap for standard deep ReLU, practical relevance of convex formulations, role of activation function) map directly to Gaps 1.1, 1.2, and 2.1 respectively.

2. **Citation consistency is good.** All citations in the gap analysis appear in the literature map's Key Papers Summary (Section 9). No phantom citations detected.

3. **Minor inconsistency in Gap 2.4:** The literature map states "Ergen and Pilanci prove strong duality for three-layer standard ReLU networks given rank-1 data matrices [WangErgenPilanci2021]" but the citation should be attributed to Wang, Ergen, and Pilanci jointly. This is cosmetic, not substantive.

4. **Score calibration:** The composite scores cluster between 6.8 and 8.5, which is a reasonable spread. However, the scoring formula double-weights Confidence of Existence (multiplied by 2), which inflates gaps that are obviously open but may not be impactful or feasible. Gap 3.3 (sparsity comparison, impact 4/10) scores 7.8/10 composite while Gap 2.2 (generalization relationship, impact 7/10) scores only 6.8/10 -- the calibration seems to penalize uncertainty about existence more than low impact.

## Prioritization Recommendation

**Recommended gap to pursue first:** Gap 1.2 (Optimality Gap of CRONOS-AM) -- This gap has the highest composite score (8.5/10), the strongest feasibility profile (public codebase, clear experimental protocol), and directly addresses the most practically important open question: whether the only method that scales convex training to real datasets actually preserves any optimality guarantees. Unlike Gap 1.1, it does not require deriving a new dual formulation. The experiment can produce meaningful results on CPU for small instances and on GPU for realistic scale, giving a natural progression from proof-of-concept to publication-quality results.

## Confidence Assessment

**Overall confidence: MEDIUM-HIGH.** The gap analysis is thorough, well-sourced, and demonstrates genuine engagement with the primary literature. The Tier 1 gaps are unambiguously real. The main risk factors are: (1) feasibility of Gap 1.1 is overstated due to the missing dual formulation for standard deep ReLU; (2) some Tier 2 gaps (2.2, 2.5) may be less novel than they appear when viewed against the broader ML theory literature outside this corpus; (3) the composite scoring formula slightly overweights existence-confidence relative to impact. None of these concerns are disqualifying -- they are calibration issues that Phase 6 should account for when selecting hypotheses.
