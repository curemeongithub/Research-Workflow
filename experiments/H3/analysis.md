---
hypothesis: H3
title: "Duality Gap for Standard 3-Layer ReLU Networks Grows Monotonically with Data Rank"
phase: 14
verdict: FAIL
result_class: negative_result_methodological
timestamp: "2026-04-07T18:00:00Z"
---

# Experimental Analysis: H3 — Rank-Dependent Duality Gap for Standard 3-Layer ReLU

## 1. Executive Summary

H3 predicted that the normalized gap between a standard three-layer ReLU primal and a parallel-architecture group-L1 convex lower bound would be numerically zero at rank one and monotonically increasing with input data rank. Across 100 cells (5 ranks × 20 seeds), the measured gap sat at a flat ~73% at every rank, with rank-1 cells violating the positive-control bound by more than four orders of magnitude (max |gap| = 0.815 vs. threshold 1e-4) and Spearman rho coming out negative (rho = -0.219, p = 0.029). The base case fails on every criterion. The failure is methodological: the two-layer parallel group-L1 convex program is not a valid lower bound on the three-layer standard ReLU primal, so the experiment measures a rank-invariant architectural distance between two distinct optimization problems rather than any duality gap. As a negative result, this experiment establishes that the Wang-Ergen-Pilanci (2021) two-layer convex reformulation cannot be repurposed as an empirical instrument for probing the three-layer duality gap, even at rank one where strong duality is theoretically guaranteed for the matched architecture.

---

## 2. Experimental Setup

**Architecture under test (primal).** Standard three-layer fully connected ReLU, no biases:
- Shape: d=10 → width=50 → width=50 → 1
- Objective: `(1/2n) ||y - net(X)||² + beta * ||theta||_F²` with `beta = 0.01`
- Optimizer: Adam, lr = 1e-3, 2000 epochs, 50 random restarts per cell (best retained)

**Lower-bound instrument (proxy dual).** Two-layer parallel group-L1 convex program:
- Sign patterns sampled by drawing random hyperplane normals over X
- `beta_convex = beta` (the roadmap's `2*sqrt(beta)` formula caused D > P and was patched; see Section 5)
- CVXPY + SCS, max_iters = 10000, eps = 1e-8

**Normalized gap metric:**
```
gap = (P_standard - D_parallel) / P_standard
```

**Data generation.** Rank-controlled synthetic regression: `X = A B^T` with `A ∈ R^{n×r}`, `B ∈ R^{d×r}` IID standard Gaussian, exact rank verified numerically. `y = X w_true + 0.1 ε`, `w_true, ε ~ N(0, I)`.

**Sweep.** n=100, d=10, ranks ∈ {1,2,3,4,5}, seeds ∈ {0,...,19}, total 100 cells. All 100 solved to completion with `primal_valid = True` (P ≥ D in every cell after the beta patch).

---

## 3. Results

### 3.1 Per-Rank Gap Statistics

| Rank | N  | Mean gap | Std    | Min    | Max    | Median |
|------|----|----------|--------|--------|--------|--------|
| 1    | 20 | 0.7409   | 0.0365 | 0.6611 | 0.8145 | 0.7465 |
| 2    | 20 | 0.7483   | 0.0257 | 0.6985 | 0.7905 | 0.7514 |
| 3    | 20 | 0.7439   | 0.0287 | 0.6727 | 0.8110 | 0.7419 |
| 4    | 20 | 0.7278   | 0.0264 | 0.6856 | 0.7804 | 0.7218 |
| 5    | 20 | 0.7292   | 0.0412 | 0.6660 | 0.8167 | 0.7302 |

Per-rank confidence intervals almost completely overlap; the weak trend from ranks 2–4 is slightly *decreasing*, opposite to the prediction.

### 3.2 Primal vs. Dual Values Per Rank

| Rank | Mean P_standard | Mean D_parallel | Ratio P/D |
|------|-----------------|-----------------|-----------|
| 1    | 0.05804         | 0.01461         | 3.97      |
| 2    | 0.07575         | 0.01897         | 3.99      |
| 3    | 0.10234         | 0.02599         | 3.94      |
| 4    | 0.09784         | 0.02689         | 3.64      |
| 5    | 0.12954         | 0.03403         | 3.81      |

Both P and D grow ~2.2× from r=1 to r=5 at the same rate; their ratio is rank-invariant.

### 3.3 Base Case Metrics

| Metric | Threshold | Observed | Result |
|--------|-----------|----------|--------|
| Spearman rho (p < 0.05) | > 0.80 | -0.219 (p = 0.029) | FAIL — wrong sign |
| Rank-1 mean abs gap | < 1e-6 | 0.741 | FAIL — ~7.4×10⁵× over threshold |
| Rank-1 max abs gap | < 1e-4 | 0.815 | FAIL — ~8.1×10³× over threshold |
| Monotone in per-rank means | non-decreasing | False (drops r=3→4) | FAIL |
| Magnitude ratio gap(r=5)/gap(r=2) | ≥ 2.0 | 0.975 | FAIL — essentially 1 |
| Primal validity (P ≥ D) | 100% | 100% | PASS |

### 3.4 Figures

All figures are in `experiments/H3/results/figures/`:

- `gap_vs_rank.png` — mean normalized gap vs. rank with seed scatter; shows flat ~0.73 baseline and slight downward drift at ranks 4–5
- `gap_distribution_violin.png` — per-rank violin plots; all five distributions overlap almost completely
- `primal_vs_dual_scatter.png` — scatter of (D_parallel, P_standard) across 100 cells color-coded by rank; near-linear scaling (slope ~3.9) is the direct cause of rank-invariant ratio
- `rank1_positive_control.png` — per-seed gap at rank 1 with the 1e-4 threshold; every seed is ~4 orders of magnitude above the line

---

## 4. Base Case Evaluation

**Formal verdict:** `FAIL` (`base_case_met: false`)

All three necessary conditions for PASS failed simultaneously:
1. Rank-1 positive control — failed by ~8,000×
2. Spearman rho > 0.8 — observed rho = -0.22 (negative)
3. Magnitude ratio ≥ 2.0 — observed 0.97 (no growth)

Two of the three failures are catastrophic (off by many orders of magnitude or wrong direction), not marginal. The reviewer classified this `failed_irrecoverable` after confirming no hyperparameter sweep can fix these failures.

---

## 5. Root Cause Analysis

The failure traces to a single incorrect claim in the H3 roadmap (Section 1):

> "The parallel architecture has zero duality gap, and its feasible set is a superset of the standard architecture. Hence any minimizer over the parallel feasible set achieves a value ≤ any standard primal minimum."

This is wrong when applied across different depth architectures. A two-layer parallel ReLU sum does not contain every function realizable by a stacked three-layer ReLU composition. The feasible sets differ in depth and structure; neither is a superset of the other.

Three independent lines of evidence confirm this:

**1. The "lower bound" was not naturally a lower bound.** The roadmap's prescribed `beta_convex = 2*sqrt(beta)` (the L2-squared ↔ group-L1 conversion lemma for matched two-layer architectures) caused D_parallel > P_standard. The coder patched to `beta_convex = beta`, restoring P ≥ D in all 100 cells, but this patch is theoretically unjustified — no valid cross-architecture rescaling lemma exists.

**2. Rank-1 positive control fails by ~8,000×.** Wang-Ergen-Pilanci (2021) prove zero duality gap at rank 1 for the two-layer architecture with its own matched convex program — not for the three-layer standard primal tested here. At rank 1, the two-layer program achieves lower objective (~0.015) than the three-layer primal (~0.058) because it faces less regularization burden (one matrix penalized via group-L1 vs. three matrices via L2-squared). Hyperparameter sweeps (widths 30–500, restarts 20–100, epochs 2000–5000, beta 0.01–1e-5) confirm this is structural, not a convergence failure.

**3. The gap is rank-invariant.** Both P and D scale ~2.2× from r=1 to r=5 at nearly the same rate (Table 3.2). Their ratio is approximately constant, because the sign-pattern enumeration that determines D_parallel becomes *more* expressive at higher rank (more distinct patterns are accessible), which if anything slightly tightens the bound at higher ranks — producing the slight negative drift visible in Table 3.1 and the negative Spearman rho.

---

## 6. Scientific Interpretation (Negative Result)

The core finding is:

> The two-layer parallel group-L1 convex program is not a valid empirical lower bound on the three-layer standard ReLU primal, even at rank one where strong duality is zero for the matched (two-layer) case. The normalized "gap" from this proxy is rank-invariant at ~73% and correlates negatively with rank. The proxy measures the architectural distance between a three-layer L2-squared problem and a two-layer group-L1 problem — a distance that is essentially independent of data rank.

**Why this matters for the literature on convex reformulations.** Wang-Ergen-Pilanci (2021) prove zero duality gap for parallel two-layer ReLU, and for standard three-layer ReLU only at rank one. It is tempting to use the parallel two-layer program as a numerical stand-in for the three-layer dual at higher ranks. Our experiment shows this stand-in is invalid in both directions: the rank-one zero-gap theorem is a property of the two-layer program's own feasible set, not of a comparison across architectures. Future work using "a convex relaxation from a different architecture" as a proxy dual for deep ReLU needs to confront this.

**Why no closed-form three-layer dual has been derived.** The H3 hypothesis is interesting precisely because it targets the open three-layer case. Our negative result is evidence that the natural workaround (reuse the two-layer convex program) does not function as a measurement instrument. A proper test of H3 requires either a closed-form dual for the three-layer compositional primal (an open theoretical problem) or exhaustive enumeration of sign-pattern *products* across both hidden layers (exponential in the number of patterns, intractable beyond toy scale).

**What is not falsified.** The H3 hypothesis itself — that the three-layer duality gap grows monotonically with data rank — is untested, not falsified. It may be true, false, or rank-independent; we cannot say. What we have shown is that the most natural empirical workaround fails, and exactly why.

**Value as a negative result.** A reader encountering H3 would naturally try the Wang-Ergen-Pilanci two-layer convex program as a lower bound. We have done this carefully (100 cells, four hyperparameter sweeps, two beta-rescaling formulas, multi-restart Adam at the primal) and shown it fails, with a characterization of why. This rules out the most obvious instrumental approach.

---

## 7. Limitations

- One architectural shape (10→50→50→1) and one data scale (n=100, d=10). The structural failure is unlikely to depend on scale, but was not tested at larger n or d.
- Only ranks 1–5 were swept; the rank-1 positive-control failure made higher-rank runs uninformative.
- Only Adam was used for the non-convex primal. Alternative optimizers (L-BFGS, SGD-with-momentum) would tighten P_standard, increasing the measured gap but not resolving the rank-invariance.
- No three-layer sign-pattern enumeration was attempted (computationally intractable at n=100).

---

## 8. Connection to Literature

H3 was constructed from Gaps 1.1 (Duality Gap for Standard Deep ReLU) and 2.4 (Beyond Rank-1) in `analysis/gap-analysis.md`. This negative result connects to three threads:

1. **Supports the Phase 5 sanity-check concern.** The review-notes flagged "no closed-form dual for standard deep ReLU" as a feasibility risk. H3 tried to work around it with a proxy and failed; the sanity-check concern is confirmed in concrete numerical terms.
2. **Consistent with Pilanci & Ergen (2020).** That paper establishes the two-layer reformulation for matched architectures and makes no claim about cross-architecture validity. H3 closes the door on a natural-but-unjustified extension.
3. **Complement to H5.** H5 tests the rank-2 boundary with a matched two-layer primal and matched convex program. H3's failure shows that scaling H5's instrument to deeper architectures by changing only the primal (leaving the convex program as-is) does not work.

---

## 9. Conclusion

H3 is recorded as a methodological negative result. The experiment was executed competently — 100 clean cells, four diagnostic hyperparameter sweeps, an explicit positive control, primal validity verified in 100/100 cells — and produced an internally consistent dataset. But the dataset rules out the instrument rather than testing the hypothesis. The two-layer parallel group-L1 convex program measures a rank-invariant architectural distance between two distinct optimization problems; it does not measure the three-layer duality gap. Testing the actual H3 hypothesis requires a genuinely tight three-layer dual, either derived in closed form or computed by exhaustive cross-layer sign-pattern enumeration — neither is currently available. H3 remains untested; what this experiment has established is that the most natural empirical workaround does not work, and why.
