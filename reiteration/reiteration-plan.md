---
phase: 16
reiteration_target: experiment
target_phases: [12, 13]
estimated_time: "6-10 hours"
priority_order: [H6, H5, H3]
---

# Reiteration Plan

## Recommended Action

**Experiment re-run targeting H6 first, then H5, with H3 explicitly out of scope.**

This is a Phase-12-and-13 reiteration: rewrite two roadmaps and execute two experiments. Phases 1–11 do not need to change. Phase 14 (analyst) and Phase 15 (final paper) re-run automatically after the experiments.

**Why not a research re-run (Phases 1–7):** the research artifacts are sound. The literature map, gap analysis, hypotheses, and methodology are publishable as-is. Re-running them would not address the actual failure.

**Why not a document revision (Phase 15 only):** the document is already as honest as it can be given the underlying data. Revising the prose without adding experimental results would not change the verdict — one negative experiment does not make a paper.

**Why H6 first instead of H3:** H3's failure is structural and the fix (derive a closed-form three-layer dual) is a multi-year theoretical research program, not a Phase 13 iteration. H6's failure was an implementation bug with a concrete fix already specified by the reviewer. H5 is the second priority because it shares H3's broken instrument and needs that instrument replaced before it can run; the replacement is also out of scope for one reiteration. The realistic ordering is: fix H6 (ship a real positive or negative result), reframe H5 around the matched two-layer rather than three-layer setting (which makes it a sharper version of the existing two-layer theory), and leave H3 documented as a negative result.

## Justification

Three concrete reasons this is the right reiteration target:

1. **H6 is the highest-composite-score hypothesis (8.8) and the only one whose blocker is fixable in <8 hours of compute.** The ablation gate revealed an SCNN baseline implementation problem. The reviewer specified the fix line-by-line: width 10 (underparameterized), pattern count 500, 200 restarts, 8000 epochs. Executing this fix is mechanical, not exploratory.

2. **The H3 failure pattern is now characterized and recoverable as scientific value.** The negative result is genuinely useful as a methodological contribution. Adding even one positive (or honestly negative) H6 result alongside it pushes the paper from "one experiment, one negative" to "two experiments, one cautionary, one substantive." That is the difference between a workshop note and a conference paper.

3. **Phase 12's bug is correctable without re-doing Phase 6.** The H6 hypothesis itself is well-formed; only the implementation roadmap needs review. The fix is contained in one phase boundary.

## Specific Changes

### Change 1 (Phase 12 re-write — H6 roadmap)

Re-write `experiments/H6/roadmap.md` with the following modifications:

- **Underparameterized regime.** Set width = 10 (was 100), keeping n = 200, d = 10. This puts the network in the regime where random sign-pattern sampling is more likely to cover the patterns the non-convex optimizer actually visits.
- **Increase pattern count.** P_samples = 500 (was 200). This is still fully tractable for CVXPY at d=10.
- **Increase restarts.** restarts = 200 (was 50). The non-convex elastic net problem has more local minima than pure L2; the existing restart count was insufficient.
- **Increase epochs.** epochs = 8000 (was 2000). Elastic net's L1 component slows Adam convergence.
- **Add a sanity-check step before the main run.** Before running the elastic net experiment, verify that the L2 control reproduces the published SCNN result on the same data within 1% gap. This is the load-bearing assumption of the entire experiment; if it fails, stop and debug the SCNN re-implementation rather than proceeding to elastic net.
- **Add a source verification step.** Cross-check the rescaling lemma assumption against `sources/arxiv-2002.10553/content.md` (Pilanci-Ergen 2020). The rescaling step is the foundational claim H6 attacks; the roadmap should quote the lemma explicitly so any re-run can spot drift between assumed and actual formulations.

### Change 2 (Phase 12 re-write — H5 roadmap, contingent on H6 success)

H5 as currently specified inherits H3's broken instrument. Two options:

- **Option A (recommended): Reframe H5 as a two-layer test.** Test whether the rank-2 boundary effect appears in a matched two-layer setting using the standard SCNN convex program. This is a different question from the original H5 (which was three-layer-specific), but it is testable with a valid instrument and still informative about how rank governs the convex landscape. The reframed H5 does not require deriving any new dual.

- **Option B (defer): Leave H5 in the paper as "not executed" with the H3 explanation.** This is the cheaper option but adds nothing to the paper.

The recommendation is Option A only if H6 is fixed first and the reformulated H5 can run within the 6–10 hour budget for the entire reiteration. Otherwise defer H5.

### Change 3 (Phase 13 re-run — H6 execution)

After Phase 12 produces the corrected H6 roadmap:

- Run the L2 sanity check first. PASS criterion: gap < 1% between SCNN convex and Adam non-convex on identical (n=200, d=10, width=10, beta=0.01) Gaussian data. Block on this gate; do not proceed to elastic net if it fails.
- If the sanity check passes, run the full elastic net comparison: lambda1/lambda2 ratio sweep at {0.25, 0.5, 1.0, 2.0, 4.0}, 20 seeds per ratio.
- Base case (preserved from original): gap > 10% in at least 18/20 seeds at lambda1/lambda2 = 1.0.

### Change 4 (Phase 14 + Phase 15)

Re-run the analyst on H6, then re-assemble the final paper. The new paper structure:

- Section 6.1 keeps H3 negative result as-is.
- Section 6.2 becomes the H6 main result (whatever it is — confirmed, refuted, or partial).
- Section 6.3 either adds the reformulated H5 result (Option A) or merges into Section 8 future work (Option B).
- Update the abstract to lead with what was actually accomplished, not the original three-experiment plan.

## Expected Improvement

If H6 runs cleanly to completion (success or failure), the paper gains:

- A second empirical result, doubling the experimental contribution.
- A directly testable finding about whether the rescaling lemma is fragile to regularizer choice — which is mechanistically illuminating regardless of which way the result lands.
- Better balance in the final paper: the H3 negative result becomes a cautionary side note rather than the main contribution.

Quantitatively, the expected per-phase score lifts after a successful reiteration:

- Phase 12: 4 → 7 (assuming the source-verification step is added and used)
- Phase 13: 6 → 8 (two of three experiments completed)
- Phase 15: 7 → 8 (substantive empirical contribution)
- Overall pipeline score: 6.4 → 7.5

If H6 also fails (sanity check exposes a deeper SCNN bug, or the underparameterized regime still does not work), the paper gains less but still gains: it adds a second methodological negative result, which strengthens the cautionary framing without making the paper publishable as a conference submission.

## Risk

Three risks, in decreasing severity.

1. **Risk: The H6 L2 sanity check still fails.** This would mean the SCNN re-implementation is broken at a deeper level than the overparameterization explanation captures. Mitigation: if this happens, switch to importing the official `pilancilab/scnn` package directly instead of re-implementing the convex program, even though that adds a dependency. The methodology already lists this repo as the canonical implementation. This adds maybe 1 hour but eliminates the re-implementation risk.

2. **Risk: Reformulated H5 (Option A) overlaps with H6.** If H6 already tests the convex framework's robustness in a two-layer matched setting, a two-layer reformulated H5 may not add new information. Mitigation: pick Option B (defer H5) and use the time saved to do more thorough hyperparameter coverage on H6 instead.

3. **Risk: The reiteration runs out of compute budget (>10 hours).** The hardware is local Apple M4 Pro; the user is the one who watches the clock. Mitigation: the H6 sanity check is a hard gate (~30 minutes of compute). If it passes, the main sweep is well-bounded. If it fails, stop early rather than burning hours on a broken baseline.

## Out of Scope for This Reiteration

- **No re-execution of H3.** H3's failure mode is now well-characterized and the fix is a theoretical research program (closed-form three-layer dual), not an engineering iteration. H3 stays in the paper as the documented negative result.
- **No re-running of Phases 1–7.** The literature map, gap analysis, hypotheses, and methodology are sound. Re-running them would consume budget without changing the empirical contribution.
- **No new hypotheses.** The seven hypotheses already in the file are enough; the constraint is execution, not ideation.
- **No new sources.** The 20-source corpus is sufficient. Adding more would re-trigger Phases 1–4 and is not needed.
