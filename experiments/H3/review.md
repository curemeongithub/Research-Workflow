---
iteration: 1
timestamp: 2026-04-07T17:30:00Z
verdict: base_case_failed
---

# Experiment Review: H3, Iteration 1

## Status Assessment

The coder completed all 5 implementation steps and ran the full 100-cell sweep (5 ranks x 20 seeds) with the final hyperparameters specified in the roadmap (width=50, restarts=50, epochs=2000, n=100, d=10, beta=0.01). No crashes occurred; all 100 cells converged and reported `primal_valid == True`. The base case was evaluated honestly against all three criteria and failed on every one.

Before the full sweep the coder discovered a sign issue: with the roadmap's prescribed rescaling `beta_convex = 2 * sqrt(beta)`, the convex program's objective value exceeded the non-convex primal's, producing a negative gap and violating the "D is a lower bound" invariant. The coder changed the rescaling to `beta_convex = beta` to restore `P_standard >= D_parallel`. This patch makes the gap numerically non-negative but does not address the underlying problem. Additional debugging (widths 30 to 500, restarts 20 to 100, epochs 2000 to 5000, betas 0.01 down to 1e-5) did not move the rank-1 gap below ~10 percent.

## Results So Far

| Rank | Mean gap_lb | Std | Notes |
|------|-------------|-----|-------|
| 1    | 0.7409      | 0.036 | Positive control requires < 1e-6 |
| 2    | 0.7483      | 0.026 | |
| 3    | 0.7439      | 0.029 | |
| 4    | 0.7278      | 0.026 | |
| 5    | 0.7292      | 0.041 | |

- Spearman rho(rank, gap) = -0.219, p = 0.029 (wrong sign; required +0.80)
- Rank-1 positive control: max|gap| = 0.8145 (required < 1e-4) -- FAILED
- Monotonicity in means: False (means drift DOWN from r=2 to r=4)
- Magnitude ratio gap(r=5)/gap(r=2) = 0.97 (required >= 2.0)
- Primal validity (P >= D) holds for 100/100 cells after the beta patch

All three base-case criteria fail. Two of them (positive control and Spearman sign) fail catastrophically, not marginally.

## Root Cause Analysis

This is NOT a convergence, hyperparameter, or numerical issue. It is a methodological mismatch baked into the roadmap:

1. **Hypothesis class mismatch.** The primal is a STANDARD 3-LAYER ReLU with objective
   `(1/(2n))||y - net_3(X)||^2 + beta * ||theta||_F^2` and compositional structure `d -> w -> w -> 1`.
   The "dual lower bound" D_parallel is the Wang-Ergen-Pilanci 2021 convex program for a TWO-LAYER
   parallel ReLU with a group-L1 penalty. These are fundamentally different function classes.
   Strong duality in WEP 2021 is proved for the two-layer case; the three-layer case is explicitly
   left open (that is what makes H3 interesting, and that is also why no closed-form tight dual
   exists for the roadmap to use).

2. **The "superset" argument in the roadmap is wrong.** The roadmap (Section 1) argued that the
   parallel-architecture feasible set is a superset of the standard 3-layer feasible set, so its
   optimum is a valid lower bound. This is incorrect. A two-layer parallel ReLU cannot represent
   all functions realizable by a three-layer composition (nested ReLU compositions produce function
   classes that are NOT contained in two-layer sums). The parallel convex value is a lower bound
   on a DIFFERENT optimization problem (two-layer with group-L1), not on the three-layer primal.
   It is neither an upper nor a lower bound in general; in this experiment it happens to lie below
   P_standard only after the ad-hoc `beta_convex = beta` patch, and that is coincidence, not theory.

3. **What the 73 percent gap is actually measuring.** It is the ARCHITECTURAL gap between a
   three-layer ReLU with L2-squared weight decay and a two-layer group-L1 convex program on the
   same data, not the DUALITY gap of either architecture. Architectural gaps have no reason to
   depend on data rank, which is exactly what the sweep shows: the gap is essentially flat at
   ~73 percent across all five ranks, with a tiny negative drift driven by the group-L1 program
   getting slightly more efficient at higher ranks (more sign patterns = more expressive dual
   variables).

4. **Rank-1 does not save us.** The roadmap (Section 5.3, note 5) predicts that at r=1 the convex
   program returns a "trivial" bound matching the primal. Empirically it does NOT, because the
   two-layer convex optimum on rank-1 data (~0.008) is much smaller than the three-layer primal
   optimum on the same data (~0.026). The coder verified this directly. The two-layer program is
   simply a better fit than the three-layer primal at rank-1, because the three-layer primal pays
   extra L2-squared regularization on two stacked weight matrices while the two-layer program only
   pays group-L1 on one layer. This has nothing to do with rank.

5. **Beta rescaling is a symptom, not a fix.** The roadmap's `beta_convex = 2 sqrt(beta)` lemma is
   the correct rescaling between L2-squared and group-L1 regularization FOR A TWO-LAYER STANDARD
   primal. Applied to a three-layer standard primal it overshoots (making D > P because the
   "equivalent" two-layer penalty is too weak relative to the three-layer compositional penalty).
   The coder's patch `beta_convex = beta` happens to restore D <= P but has no theoretical
   justification and does not recover a tight bound.

The conclusion is that the experimental design cannot test the hypothesis. The instrument (D_parallel as a proxy dual for a three-layer primal) is measuring the wrong quantity.

## Decision

**Verdict: base_case_failed (failed_irrecoverable)**

## Scientific Statement

The H3 hypothesis -- "the duality gap of a standard three-layer ReLU network grows monotonically with data rank" -- remains UNTESTED by this experiment. The hypothesis may still be true, false, or vacuous; we cannot say. What we can say, with high confidence from 100 runs, is:

> Using the two-layer parallel group-L1 convex program as a proxy "dual lower bound" for a standard three-layer ReLU primal produces a rank-invariant architectural gap of ~73 percent, not a rank-dependent duality gap. The proxy is theoretically inadmissible (the two-layer hypothesis class is not a superset of the three-layer class) and empirically flat in rank. Therefore, no signal about the rank dependence of the true three-layer duality gap can be extracted from this instrument.

Why this is irrecoverable within the roadmap's scope:

- **Option A (relative gap trend)** from the coder's error log: the data shows no such trend
  (means drift the wrong way). Re-defining the base case cannot rescue what the data does not show.
- **Option B (switch to two-layer standard + exact convex reformulation)**: this collapses H3 into
  H5's territory. H3 was selected precisely because it targets the THREE-LAYER open case in
  Wang-Ergen-Pilanci 2021. Switching to two layers destroys the scientific contribution and
  duplicates H5's setup.
- **Option C (drop positive control, keep relative trend)**: pointless, since the relative trend is
  absent anyway.
- Building a genuinely tight lower bound for three-layer ReLU would require either (a) a new
  theoretical result that does not currently exist in the literature, or (b) a computationally
  intractable enumeration over products of sign patterns across two hidden layers (exponential in n
  times exponential in the first hidden width). Neither is feasible within a Phase 13 iteration
  budget, and neither was scoped in the roadmap.

The coder performed the experiment competently. The ablation and full sweep are internally consistent, the numerics are clean, and the debugging (beta, widths, restarts, epochs) was thorough. The failure is upstream, in Phase 12's roadmap, which assumed a lower-bound relationship that does not hold.

## Implications for Downstream Phases

- Mark H3 `failed_irrecoverable`. Do NOT retry in the current iteration.
- Phase 14 analysis for H3 should document the NEGATIVE RESULT as a genuine scientific finding:
  the two-layer parallel convex program is NOT a valid proxy dual for three-layer ReLU at any
  rank, and any future attempt to probe the three-layer duality gap needs a different instrument.
- Phase 15 (final paper) should report H3 as a failed experiment with the above explanation and
  cite it as a boundary condition on the applicability of WEP-style convex reformulations.
- Phase 16 (critique) should flag the "superset argument" in the H3 roadmap (Section 1) as the
  upstream error and recommend that any reiteration targeting three-layer duality either (i) uses
  a tight lower bound from a different technique (e.g., Lagrangian relaxation over both layers'
  sign patterns at small n, d <= 4) or (ii) reformulates the hypothesis around the TWO-layer case
  where strong duality is known.

## Instructions for Next Coder Run

None. Do not launch another coder iteration for H3. Proceed directly to Phase 14 (experiment-analyst)
for H3 with the instruction to write up this as a negative result.
