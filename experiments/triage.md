---
phase: 11
status: complete
timestamp: 2026-04-07T21:30:00Z
selected_hypotheses: [H6, H5, H3]
---

# Hypothesis Triage: Duality Gap in Dual Convex Optimization in ReLU Neural Networks

## Compute Context

All experiments run locally on Apple M4 Pro (12 cores, 24GB RAM, MPS GPU via Metal Performance Shaders). No VM, no Colab. Workspace: `/Users/abhinavmallick/Github.nosync/Research-Workflow/compute`. Packages cvxpy, torch, scikit-learn, matplotlib need installation. JAX availability for MPS backend is uncertain (relevant to H1, H2).

## Hard Filter Results

| Hypothesis | Type | Hardware Check | Dependency Check | Outcome |
|-----------|------|----------------|------------------|---------|
| H1 | numerical-scaling | WARN: JAX on MPS uncertain; COLAB_GATE for full run | Independent | Passes (with risk) |
| H2 | empirical-verification | FAIL at full scale: d=784 CRONOS needs GPU; COLAB_GATE | Shares CRONOS infra with H1 | Deprioritized |
| H3 | numerical-scaling | Passes: CPU-feasible, n=100 d=10 | Shares infrastructure with H5 | Passes |
| H4 | numerical-scaling | Passes: CPU-feasible; n=1000 d=20 may be slow | Independent | Passes |
| H5 | empirical-verification | Passes: CPU-feasible, smallest problem size | Subset of H3 (cheaper) | Passes |
| H6 | empirical-verification | Passes: CPU-feasible, smallest dimensions | Independent | Passes |
| H7 | empirical-verification | WARN: SCNN on d=784 needs COLAB_GATE | Independent | Deprioritized |

No hypothesis is `theoretical-proof` type. No hypothesis requires multi-node hardware. H2 and H7 are deprioritized due to COLAB_GATE requirements at full scale (d=784 with CRONOS/SCNN generates large constraint matrices). H1 carries JAX-on-MPS risk.

## Triage Scores

| Hypothesis | Code | Compute | Data | Time | Impact | **Composite** | Selected |
|-----------|------|---------|------|------|--------|------------|----------|
| H1: CRONOS-AM depth scaling | 5 | 5 | 10 | 5 | 9 | **6.8** | No (JAX/MPS risk, COLAB_GATE for full run) |
| H2: CRONOS-AM vs SGD on MNIST | 4 | 3 | 8 | 3 | 7 | **5.0** | No (COLAB_GATE, 10-16h CPU, d=784 bottleneck) |
| H3: Rank-dependent duality gap | 5 | 7 | 10 | 6 | 9 | **7.4** | Yes |
| H4: Kim et al. bound tightness | 6 | 6 | 10 | 5 | 7 | **6.8** | No (lower impact than H3/H5/H6; n=1000 CVXPY risk) |
| H5: Rank-2 gap emergence | 7 | 8 | 10 | 8 | 8 | **8.2** | Yes |
| H6: Elastic net breaks reformulation | 8 | 9 | 10 | 9 | 8 | **8.8** | Yes |
| H7: Convex optimum generalization | 4 | 4 | 8 | 4 | 6 | **5.2** | No (COLAB_GATE, MEDIUM sanity-check concern) |

### Scoring Rationale

**Code complexity (1-10):**
- H6 (8): ~400 lines, simple two-layer setup, SCNN solver handles the convex side, PyTorch elastic net is straightforward custom regularizer.
- H5 (7): ~500 lines, shares data generation with H3 but only tests 2 ranks (r=1 and r=2). Parallel-architecture convex program construction in CVXPY is the main complexity.
- H3 (5): ~700 lines, same infrastructure as H5 but 5 rank levels, and requires robust multi-restart non-convex optimization (50 restarts per seed).
- H4 (6): ~500 lines, requires implementing Kim et al.'s Gaussian relaxation construction from the paper, which is non-trivial but self-contained.
- H1 (5): ~400 lines of new code, but CRONOS JAX installation and integration is a significant hidden cost. The CRONOS API may not be straightforward.
- H2 (4): ~500 lines plus CRONOS-on-MNIST integration at d=784, which the methodology flags as a bottleneck.
- H7 (4): ~500 lines plus SCNN at d=784 with width 200, generating very large constraint matrices.

**Compute fit (1-10):**
- H6 (9): 2-4h CPU, n=200 d=10, no GPU needed. Smallest compute footprint.
- H5 (8): 3-5h CPU, n=100 d=10, no GPU needed. Second smallest.
- H3 (7): 4-8h CPU, n=100 d=10, no GPU needed. Longer due to 5 rank levels and 50 restarts.
- H4 (6): 6-12h CPU, n up to 1000 with d=20. The CVXPY solve at n=1000 is the bottleneck; may need to cap at n=500.
- H1 (5): 6-10h on CPU (small scale). JAX CPU-only installation required; MPS support for JAX is experimental. COLAB_GATE for full run.
- H7 (4): 6-10h, COLAB_GATE. SCNN on d=784 generates large matrices; methodology suggests reducing width to 50 for CPU feasibility.
- H2 (3): 10-16h CPU estimate, COLAB_GATE. d=784 with CRONOS ADMM is the slowest experiment.

**Data availability (all high):**
- H1, H3, H4, H5, H6: 10 (synthetic, generated in-script).
- H2, H7: 8 (MNIST, publicly available via torchvision, ~50MB download).

**Time to result:**
- H6 (9): 2-4h total including coding. Simplest setup, smallest dimensions.
- H5 (8): 3-5h total. Only 2 rank levels, binary outcome.
- H3 (6): 4-8h. More complex analysis (Spearman correlation, 5 rank levels).
- H4 (5): 6-12h. n=1000 CVXPY solve may require extended time or fallback.
- H1 (5): 6-10h plus JAX debugging time.
- H7 (4): 6-10h, with SCNN-at-scale risk adding debugging overhead.
- H2 (3): 10-16h, longest wall-clock.

**Impact if confirmed:**
- H1 (9): Directly addresses the open convergence question for CRONOS-AM (Tier 1 gap, strongest per sanity check). Would characterize the practical reliability of the only convex deep network solver.
- H3 (9): Provides the first empirical characterization of how data rank governs the duality gap boundary for standard deep ReLU (Tier 1 gap). Sharp theoretical implications.
- H5 (8): Establishes whether rank-1 is the exact boundary for strong duality in standard 3-layer ReLU. If confirmed, this is a sharp characterization that directly extends Wang et al.'s Table 1.
- H6 (8): Tests whether the foundational rescaling lemma -- the engine of the entire convex reformulation program -- breaks under a common alternative regularizer. Mechanistically illuminating.
- H4 (7): Shows the Kim et al. approximation is tighter than proven. Useful but incremental (confirms a bound is loose, a common finding).
- H2 (7): Practical competitiveness comparison, but less novel since CRONOS paper already shows competitive validation accuracy.
- H7 (6): Optimization vs. generalization question is well-studied in the broader ML literature (MEDIUM concern from sanity check). Risk of re-discovering known results.

## Selected Hypotheses (in execution order)

### #1: H6 -- Elastic Net Regularization Breaks the Convex Reformulation for Two-Layer ReLU Networks

**Why selected:** Highest composite score (8.8). Tests a mechanistically fundamental question: does the rescaling lemma, which is the foundational step in converting weight decay to the convex group-$\ell_1$ formulation, break when an $\ell_1$ component is added to the regularizer? The experiment is self-contained (two-layer, n=200, d=10), requires no external repo dependencies beyond SCNN/CVXPY, and has the clearest binary outcome structure. The sanity check reframed this from "how does the gap change" to "can the reformulation even be constructed," which is the more fundamental and publishable question.

**Execution order rationale:** Fastest experiment (2-4h wall-clock). Uses the simplest architecture (two-layer) and smallest dimensions. Zero dependency on other hypotheses. Builds confidence in the CVXPY/PyTorch infrastructure before tackling more complex experiments. If the $\ell_2^2$ control fails to yield gap < 1%, this immediately signals a setup problem that would affect H5 and H3.

**COLAB_GATE:** Unlikely. Problem is fully CPU-feasible at n=200, d=10.

### #2: H5 -- Duality Gap Emerges at Rank 2 for Standard 3-Layer ReLU Networks

**Why selected:** Second highest composite (8.2). Tests the sharpest possible question about the duality gap boundary: does moving from rank-1 (where strong duality is proven) to rank-2 already break strong duality? The binary nature of the outcome (gap positive or not at rank 2) makes the result highly interpretable. The rank-1 positive control (known zero gap from Wang et al.) provides built-in validation. Computationally modest (3-5h, CPU-only, n=100, d=10).

**Execution order rationale:** Second in line because it validates the 3-layer standard network training and parallel-architecture convex program infrastructure that H3 also needs. If H5 shows zero gap at rank 2, H3's monotonic-increase hypothesis needs revision before its full rank sweep runs. This sequencing avoids wasting compute on H3 under a potentially false premise.

**COLAB_GATE:** Unlikely. Problem is fully CPU-feasible.

### #3: H3 -- Duality Gap for Standard 3-Layer ReLU Networks Is Bounded by a Data-Rank-Dependent Quantity

**Why selected:** Third highest composite (7.4) and addresses a Tier 1 gap (Gap 1.1, the central open question in the field). Extends H5's rank-2 test across the full rank spectrum $r \in \{1, 2, 3, 5, d\}$ with Spearman correlation analysis. If confirmed, it provides the first empirical evidence that data rank governs the duality gap boundary for standard deep ReLU networks, directly filling the "X" entries in Wang et al.'s Table 1. The parallel-architecture convex optimum as a lower bound is a well-motivated proxy (per the hypothesis rationale and sanity check).

**Execution order rationale:** Third because it depends on H5's infrastructure being validated and on H5's rank-2 result informing H3's interpretation. If H5 shows no gap at rank 2, H3 must be redesigned (perhaps the gap only emerges at higher ranks, or the parallel-architecture bound is too loose). If H5 confirms a gap at rank 2, H3 extends this across ranks with statistical rigor. The 4-8h estimate is the longest of the three but still CPU-feasible.

**COLAB_GATE:** Unlikely. Problem is fully CPU-feasible at n=100, d=10.

## Eliminated Hypotheses

| Hypothesis | Composite | Reason |
|-----------|-----------|--------|
| H1: CRONOS-AM depth scaling | 6.8 | JAX-on-Apple-Silicon risk: JAX MPS support is experimental and may not work with CRONOS's ADMM solver. COLAB_GATE flagged in methodology for full-scale run. Installing JAX+CRONOS is a significant debugging overhead that could derail the timeline. High impact (9/10) but the compute and tooling risk (score 5/10 each) drag it below H3/H5/H6. **Would be the #4 pick if a fourth slot were available.** |
| H4: Kim et al. bound tightness | 6.8 | Tied with H1 on composite but lower impact (7 vs 9). The n=1000 with d=20 CVXPY solve is the main risk -- the methodology notes this as a potential bottleneck. The result (showing a bound is loose) is incremental relative to H3/H5/H6 which address more fundamental structural questions. |
| H2: CRONOS-AM vs SGD on MNIST | 5.0 | COLAB_GATE: d=784 with CRONOS is the slowest experiment (10-16h CPU). Shares CRONOS JAX dependency risk with H1. The CRONOS paper already shows competitive validation accuracy, so the incremental contribution of a training loss comparison is moderate. |
| H7: Convex optimum generalization | 5.2 | COLAB_GATE: SCNN on d=784 generates large constraint matrices. Sanity check flagged MEDIUM concern about overlap with the broad optimization-generalization literature. The methodology suggests reducing width from 200 to 50 for CPU feasibility, which weakens the experiment substantially. |

## Execution Summary

| Order | Hypothesis | Est. Wall-Clock | GPU Needed | COLAB_GATE |
|-------|-----------|----------------|------------|------------|
| 1 | H6 (Elastic net breaks reformulation) | 2-4h | No | No |
| 2 | H5 (Rank-2 gap emergence) | 3-5h | No | No |
| 3 | H3 (Rank-dependent duality gap) | 4-8h | No | No |
| **Total** | | **9-17h** | **No** | **No** |

All three selected experiments are fully CPU-feasible on the Apple M4 Pro with no COLAB_GATE risk. Total estimated wall-clock: 9-17 hours sequential, or 6-10 hours with parallelization (max 4 parallel jobs per compute profile). All use synthetic data (no downloads needed). The shared infrastructure (data generators, metrics, CVXPY parallel-architecture setup) is built incrementally: H6 validates the two-layer convex solver, H5 adds the 3-layer standard network and parallel-architecture program, and H3 extends H5's setup across ranks.
