# H6 — Skipped Iteration Report

**Status:** Skipped after iteration 1 failure of the pre-flight ablation.
**Base case met:** No (base case not evaluated — main experiment never launched).
**Decision:** User-directed skip to preserve compute for H5 and H3.

## Hypothesis (abbreviated)

H6 predicts a specific scaling relationship between the duality gap in the Pilanci–Ergen convex reformulation of two-layer ReLU networks and the overparameterization ratio n/width, with a threshold base case of `normalized_gap_at_ratio_1 ≤ 0.10`. Full statement in [synthesis/hypotheses.md](../../synthesis/hypotheses.md).

## What was attempted

Iteration 1 drafted six scripts under [experiments/H6/scripts/](scripts/):
- `convex_l2_solver.py` — cvxpy formulation of the group-L1 convex program over P=200 randomly sampled activation patterns, width=100.
- `nonconvex_elastic_net.py` — PyTorch two-layer ReLU trained with L2 regularization and the β = 2·√λ₂ mapping from the rescaling lemma.
- `ablation_l2_nonconvex.py` — pre-flight validation that the convex and non-convex solvers agree on objective value (Step 6 of the roadmap; mandatory before the main sweep).
- `run_experiment.py`, `analyze.py`, `utils.py` — sweep driver and analysis helpers (drafted but never run beyond the ablation).

## What happened

The Step 6 ablation failed on all 5 seeds with ~89–90% relative difference in objective values (tolerance: 5%):

| Seed | f_convex | f_nonconvex | rel_diff |
|-----:|---------:|------------:|---------:|
| 0 | 1.2653 | 0.1225 | 90.3% |
| 1 | 1.0212 | 0.1035 | 89.9% |
| 2 | 0.8308 | 0.0939 | 88.7% |
| 3 | 1.0391 | 0.1195 | 88.5% |
| 4 | 1.2064 | 0.1184 | 90.2% |

Raw results: [experiments/H6/results/ablation_l2_nonconvex.json](results/ablation_l2_nonconvex.json).

## Root cause (documentable finding)

The β-mapping is applied correctly and the convex program is internally consistent (data_loss + group_L1 ≈ 1.265 on seed 0). The non-convex solver reaches data_loss ≈ 0.004 while the convex solver is stuck at data_loss ≈ 0.168. In the overparameterized regime (n=200, d=10, width=100), the non-convex optimizer trains activation patterns that achieve near-zero training loss on the particular data. Those patterns are not in the random P=200 sample that the convex program uses, so the convex program **cannot express** the non-convex optimum.

This is not a bug — it is a **coverage failure**: random pattern sampling does not approximate the full activation-pattern cone when the network is expressive enough to interpolate. Full enumeration has size 2·Σ_{k=0}^d C(n-1,k), which is polynomial in n for fixed d but quickly becomes intractable (d=10, n=200 ⇒ ≈10⁷ patterns).

## Why this is still a finding

The failure itself is informative for the H6 research question. The convex reformulation's duality gap is often presented as asymptotically zero (Pilanci & Ergen, 2020); practitioners compute it with random pattern sampling. The iteration-1 data show that in even mildly overparameterized regimes, **random-sample convex relaxations can underestimate the non-convex optimum by nearly an order of magnitude on the training objective**, purely from pattern coverage rather than from any gap in the reformulation itself. A proper H6 study must either (a) work in regimes where pattern coverage is dense (small d, small width, small n), (b) use full enumeration via SCNN, or (c) explicitly separate "true" duality gap from pattern-sampling error.

## Reviewer's proposed fix (deferred)

The Phase 13 reviewer recorded a concrete iteration-2 plan in [experiments/H6/review.md](review.md):
1. Switch ablation to an underparameterized regime (width 100 → 10).
2. Add same-objective evaluation via rescaling-lemma reconstruction of equivalent non-convex weights from convex (u,v) pairs.
3. Bump convex pattern count 200 → 500.
4. Tighten non-convex optimization: 200 restarts, 8000 epochs, two-stage LR schedule.
5. Add prediction-distance as a diagnostic (not the gate).

This fix was not executed in this run. It is a candidate for Phase 16 reiteration.

## Outputs

- Scripts: [experiments/H6/scripts/](scripts/)
- Raw ablation results: [experiments/H6/results/ablation_l2_nonconvex.json](results/ablation_l2_nonconvex.json)
- Reviewer decision: [experiments/H6/review.md](review.md)
- Error log: [experiments/H6/error.log](error.log)
- Status: [experiments/H6/status.yaml](status.yaml) (status: `skipped`)

## What to report in the final paper

H6 should appear in the paper with:
- The hypothesis statement.
- A "negative / methodological" result: random activation-pattern sampling is insufficient for the control check in overparameterized regimes, making it a confound for any practical duality-gap measurement. Report the ~89–90% objective gap and the coverage-failure explanation.
- An explicit statement that the main H6 base case was not evaluated and that the reviewer's proposed iteration-2 fix is a recommended future direction.
