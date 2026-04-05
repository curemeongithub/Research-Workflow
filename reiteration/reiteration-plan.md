---
phase: 9
status: reiteration_plan
timestamp: 2026-04-06T03:10:00Z
starting_phase: 7
affected_phases: [6, 7, 8]
---

# Reiteration Plan: Dual Convex Optimization in ReLU Neural Networks

> **This plan requires human approval before execution.** Review critique.md and approve the re-run below.

---

## Decision

**Re-run from:** Phase 6 (Hypothesis Formation), specifically H-3 and H-4, then cascade through Phase 7 (Methodology) and Phase 8 (Document Assembly).

**Rationale for starting at Phase 6 (not Phase 7):** Phase 7's E1 flaw originated in Phase 6's H-1 hypothesis. H-1 specifies "training loss within $(1 + \epsilon)$ of the global convex optimum $L^*$ on CIFAR-10 (rank-2688)" — but no polynomial-time method to compute the exact $L^*$ on full-rank CIFAR-10 exists. The hypothesis tacitly assumes $L^*$ is measurable, which it isn't under the stated parameters. Phase 7 (E1) inherited and propagated this flaw. Additionally H-3's exponential bound is a Phase 6 problem that must be corrected before Phase 7 can specify a meaningful experiment for it.

**Scope:** Only H-1, H-3, H-4, and H-6 need revision. H-2 and H-5 have sound hypothesis structures (minor Slater condition caveat noted) and their experimental designs in Phase 7 are executable. The literature map (Phase 3) and gap analysis (Phase 4) are preserved — the gap analysis's 2312.12657 mischaracterization is a minor cleanup.

**Git branch:** `reiteration-1`

---

## Phase 6 Re-Run: Targeted Hypothesis Revisions

Re-run only the four affected hypotheses. H-2 and H-5 are PRESERVED exactly as written.

### H-1 Revision: Fix the measurability of $L^*$

**What must change:**
1. Remove the claim that $L^*$ will be measured on CIFAR-10 (full-rank). CIFAR-10 full-rank L* is not computable exactly.
2. Replace the benchmark dataset with small-scale full-rank synthetic data where exact enumeration is feasible.
3. Add a secondary test using CIFAR-10 for deployment validation (test accuracy gap vs. CRONOS), without claiming to measure optimality ratio.

**Revised hypothesis must state:**
- Primary test: Synthetic Gaussian data with $n = 200$, $d = 20$, $r = 20$ (full rank, small enough for exact enumeration at budget ≈ $O(n^r) = O(200^{20})$ via subsampling). Ground truth $L^*$ computed by exact solver with full enumeration. Approximation ratio $\rho = L_{\text{approx}} / L^*$ measured at sampling budgets $B_\ell \in \{10^2, 10^3, 10^4\}$.
- Secondary test: CIFAR-10 test accuracy comparison between hierarchical subsampling and CRONOS (no optimality ratio claim for CIFAR-10).
- Success criterion for primary test: $\rho \leq 1.1$ at $B_\ell = 10^4$ with probability $\geq 0.95$.
- Success criterion for secondary test: Test accuracy within 1% of CRONOS baseline.
- The hypothesis must not claim that $L^*$ for full-rank CIFAR-10 is measured or estimated via "Lagrangian relaxation bound."

### H-3 Revision: Reframe as empirical exploration, not bound verification

**What must change:**
1. Remove the specific proposed functional form $\Delta \leq (L-1) \cdot \exp(-(m-m^*)/(2m^*))$. This form has no theoretical basis in the corpus.
2. Replace with a two-part empirical hypothesis: (a) Does the duality gap $\Delta(m)$ decrease monotonically as $m$ increases from $m^*$ to $10m^*$? (b) What functional form (exponential, polynomial, logarithmic) best fits the observed $\Delta(m)$ curve?

**Revised hypothesis must state:**
- Exploratory question: "Is the serial-parallel duality gap monotonically decreasing in network width $m$ for $m > m^*$?"
- Prediction: $\Delta(m)$ is monotonically non-increasing in $m$ (directional claim only) and decreases by at least 50% from $m = m^*$ to $m = 10m^*$.
- Post-hoc analysis: Fit three candidate models (exponential, polynomial, logarithmic) to $\Delta(m)$ using $R^2$ and AIC to select the best form.
- Success criterion: Monotonic decrease confirmed ($\Delta(10m^*) \leq 0.5 \cdot \Delta(m^*)$) with $\geq 9/10$ random data seeds.
- Explicitly state: "The specific functional form and decay rate are exploratory; this hypothesis does not posit a specific bound."
- Remove the false citation to "Bach (2017) Theorem 3.2" as justification for the exponential form.

### H-4 Revision: Fix FATS tractability error and clarify strong duality assumption

**What must change:**
1. Remove the FATS claim "zonotope vertex enumeration for $\ell_\infty$ balls is tractable (polytope with $2^d$ vertices)." Replace with "tractable via adversarial-direction vertex subsampling (budget 1000 vertices per sample)."
2. Add explicit precondition: "Strong duality is assumed to hold for parallel networks with zonotope constraints — this is not yet proven and must be verified empirically as part of the experiment."
3. The IBP+CROWN 85% figure must be either sourced from a specific paper or replaced with "state-of-the-art certified accuracy as reported in [SPECIFIC CITATION]."

**Revised hypothesis FATS check must state:**
- Actionable: "Yes — zonotope constraints implemented via vertex subsampling (1000 adversarial-direction vertices per sample); exact vertex enumeration is intractable for $d=784$."
- Note explicitly: "If strong duality fails (duality gap $> 10^{-3}$), H-4 is falsified on strong duality grounds regardless of certified accuracy."

### H-6 Revision: Fix LP-rounding claim

**What must change:**
1. Remove "LP rounding with optimality certificates is tractable for moderate-scale problems." LP relaxation of integer programs does not yield optimality certificates for the integer solution. Replace with "LP relaxation of the integer weight constraint followed by rounding; the rounding gap is empirically measured (no certificate for the integer solution)."
2. Reframe success criterion: The rounding gap (continuous optimum to INT8-rounded objective) should be measured as a confound; the primary claim is that convex-trained INT8 accuracy ≥ PTQ accuracy minus 2%.

---

## Phase 7 Re-Run: Targeted Experiment Redesigns

### E1 Redesign (must follow H-1 revision)

**What must change:**

1. **Replace the dataset and ground truth.** Use synthetic Gaussian data with $n = 200$, $d = 20$, $r = 20$:
   - Exact solver feasibility: $O(n^r) = O(200^{20})$ — use the zonotope subsampling paper's (2312.12657) Algorithm 1 for exact enumeration at small scale.
   - Compute $L^*$ by running the exact convex solver to convergence (verify duality gap $< 10^{-5}$).
   - Compare $L^*$ to approximated $L_{\text{approx}}$ at varying budgets $B_\ell \in \{10^2, 10^3, 10^4\}$.

2. **Add CIFAR-10 secondary experiment.** Use CIFAR-10 for test accuracy comparison only:
   - Compare hierarchical-subsampling test accuracy vs. CRONOS test accuracy.
   - Do NOT compute or claim optimality ratios on CIFAR-10.
   - Report runtime ratio vs. CRONOS.

3. **Correct the variable table.** Remove "Data rank $r$ = 3072 (CIFAR-10 full rank)" as a controlled variable for the primary experiment. Primary experiment uses $r = 20$.

4. **Correct the metrics.** Primary metric is $\rho = L_{\text{approx}} / L^*$ on synthetic data. Remove "scaled to full-rank via Lagrangian relaxation bound" — this undefined scaling must be eliminated entirely.

5. **Expected results section.** Update: "If H-1 is confirmed: for $B_\ell \geq 10^4$ on synthetic $d=20$, $r=20$ data, $\rho \leq 1.1$ with probability $> 0.95$. CIFAR-10 test accuracy within 1% of CRONOS."

### E3 Redesign (must follow H-3 revision)

**What must change:**

1. **Reduce parameters to computationally feasible regime.** The complexity formula for the exact 3-layer serial program is $O(d^3 m_1^3 n^{3(m_1+1)r})$. At the proposed parameters ($d=10$, $m=30$, $n=1000$, $r=2$), the exact solver is physically infeasible. Use:
   - $n = 50$ (not 1000): $O(50^{3 \times 31 \times 2}) \approx O(50^{186})$ — still infeasible exactly, but the **parallel network** (Wang et al.) IS polynomial and provides the dual bound. Use the dual bound $D^* = P^*_{\text{parallel}}$ as computed by the polynomial-time parallel solver, and compute $P^*_{\text{serial}}$ via **SGD estimate** (not exact solver).
   - Clarify: $P^*_{\text{serial}}$ is estimated via best-of-$k$ SGD runs (k=100 restarts), not exact enumeration. This gives an upper bound on the true $P^*_{\text{serial}}$, and therefore an upper bound on $\Delta$.
   - State explicitly: "We measure an upper bound on $\Delta$ via SGD estimate; exact $P^*_{\text{serial}}$ is intractable at meaningful problem sizes."

2. **Remove the "~10 GPU-hours" estimate for the exact 3-layer serial program.** Replace with: "Serial 3-layer exact solver: intractable at $n > 20$ for $r = 2$, $m = 30$. Parallel 3-layer (Wang et al.): polynomial, estimated ~1 GPU-hour for $n = 1000$, $d = 10$."

3. **Retain the exploratory goal.** The experiment is now: compute $D^* = P^*_{\text{parallel}}$ via exact convex solver (polynomial), estimate $P^*_{\text{serial}} \approx \hat{P}_{\text{SGD}}$ via best-of-100 SGD runs, measure $\hat{\Delta} = \hat{P}_{\text{SGD}} - D^*$ across width $m \in \{m^*, 2m^*, 5m^*, 10m^*\}$, and fit functional forms.

### E4 Redesign (must follow H-4 revision)

**What must change:**

1. Remove "Zonotope vertex enumeration for $\ell_\infty$ balls: for MNIST $d=784$, use vertex subsampling" (restate clearly that FULL enumeration is intractable; ONLY subsampling is used).
2. Add explicit duality gap monitoring at each $\epsilon$ level (0.1, 0.2, 0.3). If duality gap $> 10^{-3}$ at any $\epsilon$, report as partial failure of strong duality assumption.
3. Source the IBP+CROWN baseline: retrieve the certified accuracy numbers from Mishkin et al. (2022) or state "we establish our own IBP+CROWN baseline by re-running the open-source code" rather than citing an unverified "typically ~85%."

---

## Phase 8 Re-Run: Document Updates

**What must change (targeted, not full rewrite):**

1. **Section 5 (H-1):** Update to reflect synthetic data primary test + CIFAR-10 secondary test. Remove claim that $L^*$ is measured via Lagrangian bound on CIFAR-10.
2. **Section 5 (H-3):** Replace the exponential bound equation with exploratory form; add "CONJECTURE — no prior theoretical support" label.
3. **Section 5 (H-4):** Fix FATS tractability claim; add strong duality as an empirical precondition; source or remove "85%" figure.
4. **Section 8 (References):** Complete the bibliography to include all 27 sources. At minimum, add: arXiv:2403.01046 (Library of Mirrors), arXiv:2410.02145 (Active Learning cutting planes), arXiv:2406.02806 (Geometric Algebra), arXiv:2411.07729 (Loss Landscape convex duality, Kim et al. 2024).

---

## Success Criteria for Re-Run

The re-run Phase 6–8 passes if ALL of the following are satisfied:

| Criterion | Requirement |
|-----------|-------------|
| H-1 ground truth | $L^*$ computed via exact convex solver on synthetic data with $n \leq 200$, $d = 20$, $r = 20$; NO extrapolation from rank-50 to full-rank |
| H-3 form | Hypothesis states directional prediction (monotonic decrease) only; no specific functional form or decay rate pre-specified |
| H-4 tractability | FATS check explicitly names vertex subsampling (not full enumeration) as the tractable method; strong duality flagged as empirical assumption |
| H-4 benchmark | IBP+CROWN certified accuracy number has an inline citation to a specific published source |
| E1 design | Primary approximation ratio experiment uses synthetic full-rank data where exact $L^*$ is verifiable; CIFAR-10 used only for secondary test accuracy comparison |
| E3 compute | No claim that exact 3-layer serial solver runs in "~10 GPU-hours"; serial $P^*$ explicitly estimated via SGD upper bound, not exact enumeration |
| E4 vertex counts | No unqualified "tractable" claim for $\ell_\infty$-ball vertex enumeration at $d = 784$ |
| Document references | Bibliography contains ≥ 25 of the 27 source corpus papers with full arXiv identifiers |

---

## Phases to Preserve (No Re-Run Needed)

| Phase | Reason to Preserve |
|-------|-------------------|
| Phase 1 (Source Acquisition) | 34 sources acquired; 27 extracted; no issue |
| Phase 2 (Source Extraction) | All 27 sources have readable content files |
| Phase 3 (Literature Map) | Minor characterization fix for 2312.12657 (add zonotope approximation contribution); no structural change |
| Phase 4 (Gap Analysis) | Tier 1 gaps are verified; minor tier-label inconsistency noted but does not change the gaps or evidence |
| Phase 5 (Sanity Check) | Advisory correctly identified the key issues; no structural change needed |
| H-2 and H-5 in Phase 6 | Both hypotheses have sound theoretical rationale and executable experimental designs |
| E2, E3 (partial), E5, E6 in Phase 7 | Executable as written with the E3 parameter change noted above |

---

## Estimated Impact

If the re-run succeeds on all success criteria above, the overall pipeline grade upgrades from **B to A-**.

The single remaining risk at A- (not A) is H-3: even after reframing as exploratory, the duality gap measurement relies on SGD-estimated serial $P^*$, which is an upper bound. If SGD systematically overestimates $P^*$ (fails to reach near-global optima), the gap measurement is biased upward — a limitation not present in the parallel-network dual bound. This cannot be resolved without either exact enumeration (infeasible at scale) or a theoretical compression argument that bounds the SGD-estimated gap relative to the true gap.

---

## Approval Prompt

> **To proceed with reiteration, respond:** "Approve reiteration plan and begin re-run from Phase 6."
>
> **To modify the plan first:** State specific changes — e.g., "Keep H-3's exponential form but label it as speculative" or "Use different synthetic data dimensions for E1."
>
> **To skip reiteration:** "Accept current pipeline output, no reiteration needed."
