---
phase: 16
pipeline_run: reiteration-0
overall_score: 6.4/10
weakest_phase: 12
timestamp: 2026-04-07T22:30:00Z
depends_on: [synthesis/final-paper.md, experiments/H3/analysis.md, experiments/H3/review.md]
---

# Pipeline Critique: Duality Gap in Dual Convex Optimization in ReLU Neural Networks

## Overall Assessment

This pipeline produced a competently researched and honestly written paper, but its empirical contribution is severely limited because only one of three planned experiments ran to completion, and that one experiment was a methodological failure traceable to an upstream design error in Phase 12. The research-phase artifacts (Phases 1–7) are strong: 20 sources mapped, citations consistently grounded, gaps tied to verifiable evidence in the corpus (Wang-Ergen-Pilanci Table 1 was directly inspected and quoted), and the sanity check (Phase 5) explicitly anticipated the exact failure mode that later occurred ("the dual problem for standard deep ReLU networks has not been derived; computing the duality gap requires both primal and dual values"). The pipeline executed Phases 10–11 cleanly, selecting three CPU-feasible hypotheses from a defensible composite-score table.

The experiment phase is where the run breaks down. H6 stalled at the ablation gate on a sampling-coverage issue and was not retried. H5 was not executed at all. H3 was run to 100 cells but used a theoretically invalid lower-bound instrument — the two-layer parallel group-L1 convex program does not bound the three-layer standard ReLU primal, which the H3 roadmap claimed via a false "feasible-set superset" argument. The Phase 13 coder/reviewer pair caught the failure cleanly and Phase 14 wrote it up as a scientifically informative negative result. The final paper (Phase 15) is honest about scope, structurally sound, and uses the negative result well, but the underlying empirical contribution is "we ruled out the most natural instrument for an open question." That is publishable as a workshop note, not as a full conference paper. The weakest single phase is Phase 12 (roadmaps), because its incorrect superset claim propagated all the way to the final paper without being caught until 100 cells of compute had been spent.

## Per-Phase Scores

| Phase | Name | Score | Justification |
|-------|------|-------|---------------|
| 1 | Source Acquisition | 9 | 20 sources, all verified, full content extraction, balanced coverage of foundational and recent work; only critique is near-total Pilanci-group concentration but this is a property of the field, not the agent. |
| 2 | Source Extraction | 9 | char_counts in the 70k–110k range across primary papers (verified for arxiv-2110.06482), `identity_verified: true`, Mistral OCR pipeline; no readability gaps surfaced downstream. |
| 3 | Literature Map | 9 | MECE thematic structure (Theme A duality, Theme B architectures, Theme C scalability), correct timeline, 18+ Key Papers Summary entries with concrete attributions, cross-paper synthesis well-handled. Minor: Section 6 ("contested areas") could push harder on tensions; mostly descriptive. |
| 4 | Gap Analysis | 8 | Tier 1 gaps backed by direct source quotes; gap-analysis.md cites the exact line range (Wang Table 1, lines 56-66) verified independently in this phase. Composite scoring formula slightly over-weights Confidence-of-Existence. Gap 1.1's feasibility was rated 7/10, which proved generous. |
| 5 | Sanity Check | 9 | The single most prescient artifact in the pipeline. Explicitly flagged: "Computing the duality gap requires both the primal optimal value and the dual optimal value. For standard deep ReLU networks, the dual problem has not been explicitly formulated... The researcher would need to either (a) derive the dual formulation themselves or (b) use bounds/relaxations, which would only give one-sided estimates." This is exactly what destroyed H3. The score is held just below 10 because the warning was not propagated forcefully enough into the H3 roadmap. |
| 6 | Hypothesis Formation | 7 | Seven hypotheses, all FATES-checked, with the H3 reframe explicitly acknowledging the sanity-check feasibility flag ("Reframed to use bounding rather than exact dual computation"). The reframe was the right move conceptually but it adopted an instrument (parallel-architecture convex program as lower bound) without verifying the bound's validity. The H6 hypothesis is sharp and well-targeted; H5 is well-designed as a binary test. |
| 7 | Methodology | 7 | Detailed implementation specifications for all seven experiments with concrete script names, hyperparameters, base case definitions, COLAB_GATE annotations, shared infrastructure modules. The H3 spec carries forward the same lower-bound assumption from Phase 6 without adding a validation step. |
| 10 | Compute Probe | 8 | Correctly identified Apple M4 Pro 12-core/24GB MPS environment, flagged JAX-on-MPS uncertainty (which propagated correctly into H1's deprioritization in Phase 11), did not over-promise GPU access. |
| 11 | Triage | 8 | Composite scoring is reasonable; selected H6 (8.8), H5 (8.2), H3 (7.4) on a defensible mix of CPU-feasibility and impact. The execution-order rationale is explicit: H6 first because it validates two-layer infrastructure, then H5 (cheaper rank-2 binary test), then H3 (extends H5). H1 and H4 are sensibly listed as #4 candidates. |
| 12 | Roadmaps | 4 | **Weakest phase.** H3's roadmap stated that "the parallel architecture has zero duality gap, and its feasible set is a superset of the standard architecture, so any minimizer over the parallel feasible set achieves a value ≤ any standard primal minimum." This is the central error of the entire pipeline. The two-layer parallel ReLU class is not a superset of the three-layer standard ReLU class; the bi-dual of a standard 3-layer network is a parallel network (Wang-Ergen-Pilanci 2021, line 334), not the other way around. Phase 12 should have caught this — it had access to the same source. Additionally, the H3 roadmap prescribed `beta_convex = 2*sqrt(beta)` (a two-layer L2↔L1 conversion lemma) for a cross-architecture setup where it has no theoretical basis. |
| 13 | Experiments | 6 | H6 stopped at the ablation gate (correctly: the L2 control failed), but no retry was launched in this run despite the reviewer specifying a concrete fix (underparameterized regime, width 10, P=500, restarts 200). H5 was not started at all. H3 ran 100 clean cells, four diagnostic sweeps (widths 30-500, restarts 20-100, epochs 2000-5000, beta 0.01–1e-5), and the coder/reviewer pair recognized the failure correctly. The execution itself was competent; the scope (1/3 hypotheses completed) is the problem. |
| 14 | Analysis | 9 | The H3 analysis writeup is unusually good: it isolates the failure to a single false claim in the roadmap, walks through three independent confirming lines of evidence, distinguishes "instrument failure" from "hypothesis falsification," and explicitly states what is and is not learned. The negative-result framing is principled rather than face-saving. |
| 15 | Final Paper | 7 | Honest about the scope limitation in both the abstract and Section 6.2/6.3. Background and related-work sections are well-cited and read like a real conference paper. Section 7 (Discussion) extracts more value from the negative result than the raw analysis did. Weaknesses: only one experiment of substance is reported; the H6 ablation finding is presented as a "scientific finding" in 7.3 but is genuinely a setup bug, not a discovery; the abstract over-claims slightly by foregrounding "three empirical experiments" before disclosing two were not completed. |

## Weakest Phase: Phase 12 (Experiment Roadmaps)

The single counterfactual change that would most improve this pipeline run is fixing Phase 12's H3 roadmap. The error is precise and identifiable: the roadmap's Section 1 contains a one-sentence justification — that the parallel-architecture feasible set is a superset of the standard architecture's — that is logically false. This mistake was not present in Phase 5 (the sanity check correctly noted that no closed-form dual exists for standard deep ReLU). It was not present in Phase 6 (the hypothesis was reframed to use a "bounding" approach but did not specify the bound's source). It was introduced in Phase 12 when the roadmap had to commit to a concrete instrument and chose the wrong one without verification.

Three things made this catastrophic rather than merely wrong:

1. **The error was load-bearing.** Every downstream artifact for H3 (the script, the 100 cells, the four diagnostic sweeps, the analysis) is built on this single false premise. There is no smaller fix; the entire experimental design is wrong.

2. **The error was checkable in Phase 12 itself.** Wang-Ergen-Pilanci 2021 line 334 says explicitly: "the bi-dual problem corresponds to optimizing a parallel neural network instead of a standard neural network to fit the labels." This is the inverse of what the roadmap assumed. A single source lookup in Phase 12 — exactly the kind of grep-first verification the source-lookup skill exists for — would have caught it. The roadmap-writer did not perform that lookup.

3. **The error invalidates H5 too.** H5 is designed around the same instrument. Even if H5 had run, it would have failed its rank-1 positive control by a factor of ~8000x for the same reason. Phase 12 produced two roadmaps (H3 and H5) that share a fatal flaw, and the bug was not localized until 100 cells of compute were already burned.

The verdict is `verdict: FAIL` with `result_class: negative_result_methodological`. The experimentalists (Phase 13/14) handled it cleanly and turned a wasted run into a publishable cautionary finding, but the root cause is upstream.

## Strengths

- **Sanity check (Phase 5) was prescient.** The exact failure mode of H3 was anticipated in advance and recorded in `analysis/review-notes.md`. This is the protocol working as intended; the protocol was just not enforced when Phase 12 wrote the H3 roadmap.
- **Source verification was rigorous.** Gap analysis quotes Table 1 of Wang-Ergen-Pilanci with line numbers; the final paper's claims about CRONOS, SCNN, and Pilanci-Ergen 2020 are all consistent with the corpus on cross-check.
- **Honest reporting under pressure.** The H3 coder did not paper over the rank-1 positive control failure (8000x over threshold) or claim a partial result. The reviewer correctly classified it `failed_irrecoverable`. The Phase 14 analyst wrote a negative-result paper without fabricating a positive spin.
- **Triage matched the compute envelope.** The three selected hypotheses were all CPU-feasible on the actual hardware; no run hit a COLAB_GATE that hadn't been forecast in Phase 11.
- **Final paper is structurally publishable.** Sections 1–4 (abstract through gap/hypothesis statement) read like a normal conference paper. The negative result is positioned coherently in Section 7.

## Critical Issues

These would cause a reviewer to reject in current form.

1. **Only one experiment of three was executed, and it was a methodological negative result.** The empirical contribution is "we ruled out one possible instrument for one open question," which is too thin for a full paper. A conference reviewer would correctly ask why H5 and H6 were not retried after the H3 failure exposed the shared bug.

2. **The H3 roadmap's load-bearing claim was never source-checked.** Phase 12 had access to Wang-Ergen-Pilanci 2021 line 334 which directly contradicts the superset argument. A single grep of the source corpus for "bi-dual" or "parallel.*standard" would have surfaced this. The pipeline did not enforce a "verify-the-instrument-against-the-source" check before committing 100 cells of compute.

3. **H6's "ablation finding" is a setup bug, not a discovery.** The final paper Section 7.3 dresses up the H6 ablation failure as a "meaningful practical finding" about random pattern sampling. This is a stretch — the L2 control should have shown gap < 1% by construction (it is reproducing Mishkin-Sahiner-Pilanci 2022 directly), and the 89% disagreement means the SCNN re-implementation was wrong, not that random sampling fails in practice. The honest framing is "our two-layer convex baseline implementation is broken; H6 cannot be evaluated until the baseline matches published SCNN behavior."

## Minor Issues

- The abstract front-loads "three empirical experiments" before disclosing two were not completed; a one-sentence reorder would fix this.
- The composite scoring formula in the gap analysis double-weights Confidence-of-Existence, slightly inflating the rank of "obvious-but-not-very-impactful" gaps. Phase 5 noted this; Phase 6 did not adjust.
- Section 6.2 says H5 was "not executed" but the status YAML for H5 references partial scaffolding (smoke test plus ablation gate). The paper should distinguish "design complete, code partial, no full sweep" from "design only."
- Section 8's "future work" item 1 (theoretical dual derivation for standard 3-layer ReLU) is correctly identified as the missing ingredient but is presented as a research direction; it is in fact what the field has been blocked on for four years per Wang-Ergen-Pilanci Table 1. The framing should acknowledge this is a major open theoretical problem, not a tractable next step.
- The H3 roadmap's `beta_convex = 2*sqrt(beta)` patch story is told twice (Section 5.1 and Section 7.1). One mention with a back-reference would be cleaner.
- Reference list does not include `[Mishkin2022SCNN]` link to the SCNN repo even though the paper relies on it for the H6 baseline.

## What the Final Paper Actually Establishes

To be fair to the run: the paper does establish one concrete result that is not in the literature. Namely, that any future researcher attempting to characterize the standard 3-layer ReLU duality gap by repurposing the two-layer parallel convex program as a proxy lower bound will fail in a specific, mechanistically explained way (rank-invariant ~73% architectural distance, rank-1 positive control off by 8000x, cross-architecture rescaling lemma has no basis). This is a non-trivial cautionary finding. It is just much less than what the pipeline was designed to produce.
