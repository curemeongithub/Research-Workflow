---
phase: 6
status: complete
timestamp: 2026-04-07T20:15:00Z
depends_on: [analysis/gap-analysis.md, analysis/review-notes.md]
token_estimate: 7200
---

# Hypotheses: Duality Gap in Dual Convex Optimization in ReLU Neural Networks

## Hypothesis Formation Summary

Seven hypotheses were formed from Tier 1 and Tier 2 gaps. Gap 1.2 (CRONOS-AM optimality) produced H1 and H2 as the strongest candidates, per sanity check recommendation. Gap 1.1 (deep ReLU duality gap) produced H3, reframed to use bounding rather than exact dual computation, addressing the sanity check feasibility concern that no closed-form dual exists for standard deep ReLU. Tier 2 gaps 2.3 (approximation tightness) and 2.4 (rank threshold) produced H4 and H5. Gap 2.1 (regularizer effect) produced H6, reframed per sanity check to test whether the reformulation is even possible rather than just measuring gap changes. Gap 2.2 (generalization) produced H7 as a secondary hypothesis. Gap 2.5 (finite-sample scaling) was excluded as the weakest Tier 2 gap per sanity check. Tier 3 gaps (3.1-3.3) are excluded per protocol and will become baseline experiments in methodology. Of these 7 hypotheses, approximately 3 are expected to survive Phase 11 triage.

## Primary Hypotheses (from Tier 1 gaps)

### H1: CRONOS-AM Optimality Gap Grows Sub-linearly with Depth

**Source gap:** Gap 1.2 (Optimality Gap of CRONOS-AM)
**Sanity check status:** LOW concern (strongest gap for empirical investigation)
**Type:** numerical-scaling

**Hypothesis:**
> If CRONOS-AM is applied to train ReLU networks of increasing depth L in {2, 3, 4, 5} on fixed synthetic datasets (n=200, d=10, Gaussian), then the ratio of CRONOS-AM's achieved training loss to the exact two-layer convex optimum will increase sub-linearly with depth (i.e., the optimality ratio $f_{\text{AM}} / f_{\text{exact}}$ scales as $O(L^{\alpha})$ with $\alpha < 1$), compared to a baseline of SGD/Adam solutions on the same architectures, as measured by the training loss ratio $f_{\text{method}} / f_{\text{convex-2-layer}}$, under the constraint that the exact convex optimum is computable for the two-layer subproblem.

**Rationale:** CRONOS-AM decomposes deep networks into a non-convex inner-layer problem (solved by Adam) and a convex last-two-layer problem (solved by CRONOS). As depth increases, more layers are handled by Adam without optimality guarantees. The alternating minimization scheme may accumulate error with depth, but the convex subproblem anchors each iteration. Understanding how the gap scales with depth directly addresses whether CRONOS-AM's practical success is due to near-optimal convergence or favorable problem structure.

**Null hypothesis:** The optimality ratio $f_{\text{AM}} / f_{\text{exact}}$ grows linearly or super-linearly with depth, indicating the alternating minimization scheme degrades proportionally with network complexity.

**Success criteria:**
- The measured optimality ratio at L=5 is less than 2.5x the ratio at L=2
- A power-law fit $O(L^{\alpha})$ with $\alpha < 1$ achieves $R^2 > 0.8$ across depths
- The scaling exponent $\alpha$ is estimated with a 95% confidence interval that excludes 1.0

**Potential confounds:**
1. Width of the network at each depth -- wider networks may mask depth-dependent degradation
2. Initialization of the non-convex Adam subproblem may dominate the gap rather than depth itself
3. The two-layer exact solution used as baseline may not be the correct reference for deeper architectures

**Implementation sketch:**
- Primary library: JAX (CRONOS is JAX-native), CVXPY for exact two-layer solutions
- Existing code to build on: https://github.com/pilancilab/CRONOS (CRONOS-AM implementation)
- Estimated lines of new code: ~400 (experiment harness, depth sweep, metric computation)
- Compute: CPU-feasible for proof-of-concept (n=200); GPU recommended for larger instances
- Data: synthetic Gaussian (controlled rank and dimensionality)
- Estimated wall-clock: 2-4 hours on CPU for small instances; 1-2 hours with GPU

**FATES check:**
- Falsifiable: yes -- a measured scaling exponent $\alpha \geq 1$ would disprove sub-linear scaling
- Actionable: yes -- CRONOS codebase is public, experiment design is a depth sweep
- Testable: yes -- the training loss ratio is a scalar metric computable at each depth
- Empirically tractable: yes -- requires running CRONOS-AM and CVXPY, no theoretical derivation needed
- Specific: yes -- names depths {2,3,4,5}, dataset parameters, specific metric, and power-law model

---

### H2: CRONOS-AM Solutions Are Within Constant Factor of SGD on Small-to-Medium Instances

**Source gap:** Gap 1.2 (Optimality Gap of CRONOS-AM)
**Sanity check status:** LOW concern
**Type:** empirical-verification

**Hypothesis:**
> If CRONOS-AM and SGD (with grid-searched learning rate and momentum) are both applied to train 3-layer ReLU networks on MNIST digit-pair subsets (n in {500, 1000, 2000}), then CRONOS-AM will achieve training loss within a factor of 1.5x of the best SGD solution in at least 80% of configurations, as measured by the ratio $f_{\text{AM}} / f_{\text{SGD-best}}$, under the constraint that both methods use identical architectures and regularization strengths.

**Rationale:** The CRONOS paper demonstrates competitive validation accuracy against SGD/Adam but does not systematically compare training loss optimality. If CRONOS-AM consistently matches or beats SGD on training loss, this provides empirical evidence that the alternating minimization approach preserves near-optimality despite lacking theoretical guarantees. The 1.5x threshold is chosen because the two-layer CRONOS component provably converges to the global optimum, so degradation should come only from the Adam portion of the alternation.

**Null hypothesis:** CRONOS-AM achieves training loss more than 1.5x of SGD-best in more than 20% of configurations, indicating the alternating minimization scheme introduces substantial suboptimality.

**Success criteria:**
- Across all (n, architecture, regularization) configurations, the fraction where $f_{\text{AM}} / f_{\text{SGD-best}} \leq 1.5$ exceeds 80%
- The median training loss ratio across all configurations is reported with bootstrap confidence intervals

**Potential confounds:**
1. SGD hyperparameter grid may be insufficient, making SGD look worse than it should
2. Regularization strength $\beta$ affects both methods differently -- need matched $\beta$ values
3. MNIST is a relatively easy dataset; results may not generalize to harder problems

**Implementation sketch:**
- Primary library: JAX (CRONOS), PyTorch (SGD baseline)
- Existing code to build on: https://github.com/pilancilab/CRONOS, standard PyTorch training loops
- Estimated lines of new code: ~500 (SGD grid search, CRONOS-AM wrapper, comparison harness)
- Compute: CPU-feasible for n<=2000 with CRONOS; GPU recommended for SGD grid search
- Data: MNIST digit-pair subsets (binary classification, publicly available)
- Estimated wall-clock: 4-8 hours on CPU; 1-2 hours with GPU

**FATES check:**
- Falsifiable: yes -- if more than 20% of configurations exceed the 1.5x threshold, H2 is false
- Actionable: yes -- both codebases are public, MNIST is standard
- Testable: yes -- training loss ratio is a directly computable scalar
- Empirically tractable: yes -- standard train-and-measure experiment
- Specific: yes -- names dataset, sample sizes, architecture depth, threshold, and success rate

---

### H3: Duality Gap for Standard 3-Layer ReLU Networks Is Bounded by a Data-Rank-Dependent Quantity

**Source gap:** Gap 1.1 (Duality Gap for Standard Deep ReLU), Gap 2.4 (Beyond Rank-1)
**Sanity check status:** MEDIUM concern (Gap 1.1: feasibility overstated; Gap 2.4: LOW concern). Reframed to use bounding approach rather than exact dual computation.
**Type:** numerical-scaling

**Hypothesis:**
> If standard (non-parallel) 3-layer ReLU networks are trained on synthetic data matrices $X \in \mathbb{R}^{n \times d}$ with controlled rank $r \in \{1, 2, 3, 5, d\}$ (n=100, d=10), then the gap between the non-convex primal optimal value and the parallel-architecture convex optimum (used as a lower bound on the dual) will be zero for $r=1$ and will increase monotonically with rank $r$, as measured by the normalized gap $(P_{\text{standard}} - D_{\text{parallel}}) / P_{\text{standard}}$, under the constraint that the parallel-architecture dual is computable via existing solvers and serves as a valid lower bound.

**Rationale:** Wang et al. prove strong duality for standard 3-layer ReLU networks with rank-1 data but mark the general case as unknown. Since the dual for standard deep ReLU has not been derived in closed form (per sanity check), we use the parallel-architecture convex optimum as a proxy lower bound -- it provides a valid relaxation because the parallel architecture admits more solutions than the standard architecture. The gap between the standard network's primal and this lower bound provides an upper bound on the true duality gap. If this upper bound itself grows with rank, the true gap must also grow.

**Null hypothesis:** The measured gap $(P_{\text{standard}} - D_{\text{parallel}})$ does not increase monotonically with rank, or is zero for all ranks tested, suggesting strong duality may hold more broadly than currently proven.

**Success criteria:**
- The gap is verified to be zero (within numerical tolerance $10^{-6}$) at $r=1$, matching the known theoretical result
- The gap at $r=d$ exceeds the gap at $r=2$ by at least a factor of 2
- A monotonic trend is statistically significant (Spearman $\rho > 0.8$, $p < 0.05$) across 10+ random seeds per rank

**Potential confounds:**
1. The parallel-architecture lower bound may be loose, making the measured gap an overestimate
2. Non-convex optimization for the standard architecture may converge to local minima, inflating the apparent gap
3. Small problem sizes may not exhibit the same rank-dependence as larger instances

**Implementation sketch:**
- Primary library: CVXPY (parallel-architecture convex program), PyTorch (standard network training with multiple restarts)
- Existing code to build on: https://github.com/pilancilab/convex_nn (convex formulations), https://github.com/pilancilab/scnn (two-layer solvers as subroutines)
- Estimated lines of new code: ~700 (3-layer standard network training, parallel-architecture convex program setup, rank-controlled data generation, gap measurement)
- Compute: CPU-feasible for n=100, d=10
- Data: synthetic with controlled rank via SVD truncation
- Estimated wall-clock: 3-6 hours on CPU (multiple seeds per rank level)

**FATES check:**
- Falsifiable: yes -- a non-monotonic relationship or zero gap at all ranks would disprove it
- Actionable: yes -- uses existing convex solvers and standard non-convex training
- Testable: yes -- the normalized gap is a computable scalar for each (rank, seed) pair
- Empirically tractable: yes -- bounding approach avoids the need to derive the closed-form dual
- Specific: yes -- names rank values, problem dimensions, metric formula, and statistical test

---

## Secondary Hypotheses (from Tier 2 gaps)

### H4: Kim et al.'s $O(\sqrt{\log n})$ Bound Is Loose by at Least a Constant Factor on Gaussian Data

**Source gap:** Gap 2.3 (Tightness of $O(\sqrt{\log n})$ Approximation on Real Data)
**Sanity check status:** LOW concern (clean, well-scoped empirical gap)
**Type:** numerical-scaling

**Hypothesis:**
> If the Gaussian randomized relaxation from Kim and Pilanci (2024) is applied to two-layer ReLU networks on synthetic Gaussian data with $n \in \{50, 100, 200, 500, 1000\}$ and $d = 20$, then the actual relative optimality gap $\tilde{p}^* / p^*$ will be bounded by $C \cdot (\log n)^{1/4}$ for some constant $C < 1$, which is strictly tighter than the proven $O(\sqrt{\log n})$ upper bound, as measured by the ratio of the relaxed solution value to the exact convex optimum, under the constraint that exact solutions are computable for the tested problem sizes.

**Rationale:** Theoretical worst-case bounds are often loose by polynomial factors on typical instances. Kim and Pilanci's bound of $O(\sqrt{\log n})$ is proven under Gaussian assumptions but may be pessimistic for typical Gaussian draws. If the actual gap scales as $(\log n)^{1/4}$ or even $O(1)$, this would suggest the relaxation is much more practical than the theory indicates, motivating algorithmic work that relies on the relaxation for scalability.

**Null hypothesis:** The actual relative optimality gap grows at the theoretical rate $\Theta(\sqrt{\log n})$, indicating the bound is tight.

**Success criteria:**
- Across the range $n \in \{50, ..., 1000\}$, the best-fit power law for the gap as a function of $\log n$ yields an exponent $< 0.5$ with $R^2 > 0.7$
- At $n = 1000$, the measured gap is less than 50% of the theoretical upper bound $C_0 \sqrt{\log 1000}$

**Potential confounds:**
1. The exact convex solution may be hard to compute for $n = 1000$ with $d = 20$, requiring solver tolerance checks
2. The number of sampled hyperplane arrangements $\tilde{P}$ affects the relaxation quality -- need to match the theoretical prescription
3. Random seed variability may be large; need sufficient repetitions (20+ seeds per $n$)

**Implementation sketch:**
- Primary library: CVXPY (exact convex program), NumPy (Gaussian relaxation sampling)
- Existing code to build on: https://github.com/pilancilab/scnn (two-layer exact solvers)
- Estimated lines of new code: ~500 (Gaussian relaxation implementation following Kim et al.'s construction, exact solver wrapper, scaling analysis)
- Compute: CPU-feasible for $n \leq 500$; may need extended time for $n = 1000$
- Data: synthetic Gaussian i.i.d. entries
- Estimated wall-clock: 4-8 hours on CPU

**FATES check:**
- Falsifiable: yes -- if the gap scales as $\Theta(\sqrt{\log n})$, the hypothesis of a tighter bound is false
- Actionable: yes -- involves implementing the relaxation and computing exact solutions
- Testable: yes -- the relative optimality gap is a scalar, and the scaling exponent is estimable
- Empirically tractable: yes -- standard convex optimization experiments
- Specific: yes -- names $n$ values, dimensionality, exponent threshold, and fit criterion

---

### H5: Duality Gap Emerges at Rank 2 for Standard 3-Layer ReLU Networks

**Source gap:** Gap 2.4 (Convex Duality Beyond Rank-1 for Standard Deep ReLU)
**Sanity check status:** LOW concern
**Type:** empirical-verification

**Hypothesis:**
> If standard 3-layer ReLU networks are trained on synthetic data with rank $r = 2$ (n=100, d=10, data constructed as $X = AB^T$ with $A \in \mathbb{R}^{n \times 2}$, $B \in \mathbb{R}^{d \times 2}$), then the gap between the standard non-convex primal optimum and the parallel-architecture convex lower bound will be strictly positive (exceeding numerical tolerance of $10^{-4}$), as measured by the normalized gap $(P_{\text{standard}} - D_{\text{parallel}}) / P_{\text{standard}}$, under the constraint that the rank-1 case yields zero gap (serving as a positive control).

**Rationale:** Wang et al. prove strong duality holds for standard 3-layer ReLU with rank-1 data. The rank-2 case is the immediate next step. If the gap appears at rank 2, this establishes that rank-1 is the exact boundary for strong duality in standard deep ReLU, which would be a sharp characterization. If the gap remains zero at rank 2, it suggests the boundary lies elsewhere, potentially at full rank.

**Null hypothesis:** The gap at rank 2 is indistinguishable from zero (within tolerance $10^{-4}$), suggesting strong duality may hold beyond rank-1.

**Success criteria:**
- Rank-1 positive control: gap $< 10^{-6}$ across all seeds
- Rank-2 test: gap $> 10^{-4}$ in at least 90% of random seeds (out of 50+ seeds)
- The gap at rank 2 is statistically significantly greater than zero (one-sample t-test, $p < 0.01$)

**Potential confounds:**
1. Non-convex optimization may fail to find the true primal optimum for standard architecture -- use multiple random restarts (50+)
2. The parallel-architecture bound may be loose at rank 2, showing a gap that does not exist in the true dual
3. Numerical precision of solvers may create false positives; need careful tolerance calibration

**Implementation sketch:**
- Primary library: CVXPY (parallel-architecture program), PyTorch (standard network with multi-restart)
- Existing code to build on: https://github.com/pilancilab/convex_nn
- Estimated lines of new code: ~500 (rank-controlled data generation, 3-layer standard network training, parallel-architecture convex program, statistical testing)
- Compute: CPU-feasible
- Data: synthetic rank-controlled matrices
- Estimated wall-clock: 2-4 hours on CPU

**FATES check:**
- Falsifiable: yes -- zero gap at rank 2 across seeds would disprove it
- Actionable: yes -- uses standard tools and synthetic data
- Testable: yes -- binary outcome (gap > threshold or not) with clear statistical test
- Empirically tractable: yes -- no theory derivation required, just computation
- Specific: yes -- names rank value, dimensions, tolerance thresholds, and statistical test

---

### H6: Elastic Net Regularization Breaks the Convex Reformulation for Two-Layer ReLU Networks

**Source gap:** Gap 2.1 (Effect of Regularizer Choice on Duality Gap)
**Sanity check status:** MEDIUM concern (reformulation may break at step 1; reframed per sanity check to test whether reformulation is possible, not just gap magnitude)
**Type:** empirical-verification

**Hypothesis:**
> If two-layer ReLU networks are trained with elastic net regularization ($\lambda_1 \|w\|_1 + \lambda_2 \|w\|_2^2$, with $\lambda_1 / \lambda_2 = 1$) instead of pure $\ell_2^2$ weight decay, then the rescaling lemma that converts $\ell_2^2$ weight decay to $\ell_1$ penalty on output weights will not apply, and the gap between the non-convex training loss and the best achievable by the standard convex reformulation (applied with $\ell_2^2$ only) will exceed 10% of the non-convex optimal value, as measured by $(f_{\text{elastic-net}}^* - f_{\text{convex-}\ell_2}^*) / f_{\text{elastic-net}}^*$, under the constraint that both solutions are computed on the same data (n=200, d=10, Gaussian).

**Rationale:** The entire convex reformulation pipeline for ReLU networks hinges on the rescaling lemma, which converts $\ell_2^2$ weight decay on all layers into an $\ell_1$ penalty on output weights. This rescaling exploits the positive homogeneity of ReLU and the specific structure of $\ell_2^2$. Elastic net adds an $\ell_1$ term that is not positively homogeneous in the same way, potentially breaking the rescaling step. The sanity check specifically flagged that the question is not "how does the gap change" but "can the reformulation be constructed at all." This hypothesis tests whether elastic net creates a fundamentally different optimization landscape that the existing convex framework cannot capture.

**Null hypothesis:** The standard $\ell_2^2$ convex reformulation still achieves training loss within 10% of the elastic net optimum, suggesting the reformulation is robust to regularizer perturbation even if not theoretically justified.

**Success criteria:**
- The measured gap $(f_{\text{elastic-net}}^* - f_{\text{convex-}\ell_2}^*) / f_{\text{elastic-net}}^*$ exceeds 10% for the tested $\lambda_1 / \lambda_2 = 1$ ratio
- The gap is positive across all 20+ random seeds
- A control experiment with pure $\ell_2^2$ ($\lambda_1 = 0$) yields gap $< 1\%$, confirming the baseline works

**Potential confounds:**
1. The elastic net may have multiple local minima; need sufficient restarts for the non-convex problem
2. The $\lambda_1 / \lambda_2$ ratio matters -- different ratios may give different results; should sweep a range
3. The $\ell_2^2$ convex solution might happen to be near-optimal for elastic net by coincidence on small instances

**Implementation sketch:**
- Primary library: CVXPY (convex $\ell_2^2$ reformulation), PyTorch (elastic net non-convex training with custom regularizer)
- Existing code to build on: https://github.com/pilancilab/scnn (two-layer convex solver with $\ell_2^2$)
- Estimated lines of new code: ~400 (elastic net regularizer in PyTorch, comparison harness, ratio sweep for $\lambda_1 / \lambda_2$)
- Compute: CPU-feasible
- Data: synthetic Gaussian
- Estimated wall-clock: 2-3 hours on CPU

**FATES check:**
- Falsifiable: yes -- if the gap is below 10% across all seeds, the hypothesis is false
- Actionable: yes -- uses existing convex solver + standard PyTorch training
- Testable: yes -- the loss ratio is a scalar; threshold is pre-specified
- Empirically tractable: yes -- no theoretical derivation; just train and compare
- Specific: yes -- names regularizer form, ratio, dimensions, threshold, and control condition

---

### H7: Networks Closer to the Convex Optimum Do Not Generalize Better Than SGD Solutions

**Source gap:** Gap 2.2 (Relationship Between Duality Gap and Generalization)
**Sanity check status:** MEDIUM concern (broad optimization-generalization literature may already address this; needs careful framing)
**Type:** empirical-verification

**Hypothesis:**
> If two-layer ReLU networks are trained on MNIST binary classification (digits 3 vs 8, n=1000) using both the SCNN convex solver (achieving global training optimum) and SGD with early stopping (achieving a local minimum with training loss 1.1-2x of convex optimum), then the convex-optimal solution will not achieve strictly better test accuracy than the best SGD solution, as measured by test accuracy on a held-out set of 500 samples, under the constraint that regularization strength $\beta$ is matched between methods.

**Rationale:** A fundamental question in optimization-generalization theory is whether finding the global optimum of a regularized training problem is better for generalization than finding a "good enough" local minimum. The convex framework provides a unique setting to test this because the global optimum is actually computable. The broader ML literature suggests that SGD's implicit regularization (via gradient noise, learning rate, early stopping) may provide generalization benefits that the global convex optimum lacks. This hypothesis tests whether optimization quality (measured by proximity to the convex optimum) translates to generalization quality in the specific context of convex ReLU networks.

**Null hypothesis:** The convex-optimal solution achieves strictly better test accuracy (by at least 2 percentage points) than the best SGD solution, indicating that closing the optimization gap benefits generalization.

**Success criteria:**
- Test accuracy of the SCNN convex solution minus test accuracy of the best SGD solution is $\leq 0$ (convex is no better) in at least 70% of $\beta$ values tested
- Results are robust across 5 different digit-pair tasks (not just 3 vs 8)
- Confidence intervals (bootstrap, 95%) for the accuracy difference include zero or are negative

**Potential confounds:**
1. SGD hyperparameter tuning quality -- undertrained SGD would unfairly advantage the convex solution
2. The regularization strength $\beta$ strongly affects both optimization and generalization; need a $\beta$ sweep
3. MNIST may be too easy to show differences; both methods may achieve near-100% accuracy for some $\beta$

**Implementation sketch:**
- Primary library: PyTorch (SGD training), CVXPY or scnn (convex solver)
- Existing code to build on: https://github.com/pilancilab/scnn (two-layer convex solver with MNIST experiments)
- Estimated lines of new code: ~500 (SGD training loop with hyperparameter grid, SCNN wrapper, generalization comparison, bootstrap confidence intervals)
- Compute: CPU-feasible for n=1000
- Data: MNIST digit pairs (publicly available)
- Estimated wall-clock: 3-5 hours on CPU

**FATES check:**
- Falsifiable: yes -- if the convex solution consistently outperforms SGD on test accuracy by >2pp, H7 is false
- Actionable: yes -- uses public code and standard datasets
- Testable: yes -- test accuracy is a standard metric with well-defined comparison
- Empirically tractable: yes -- standard train-evaluate pipeline
- Specific: yes -- names dataset, sample sizes, methods, metric threshold, and statistical test

---

## Excluded Gaps and Reasoning

| Gap | Reason for Exclusion |
|-----|---------------------|
| Gap 2.5 (Finite-Sample Scaling) | MEDIUM concern from sanity check; weakest Tier 2 gap; primarily confirms known combinatorial bounds ($P \leq 2r(e(n-1)/r)^r$) rather than discovering new phenomena; Impact 6/10 deemed generous by reviewer |
| Gap 3.1 (Gated ReLU Depth) | TIER 3 -- goes to methodology as baseline experiment |
| Gap 3.2 (Robustness of Convex Optimum) | TIER 3 -- goes to methodology as baseline experiment |
| Gap 3.3 (Solution Sparsity Comparison) | TIER 3 -- goes to methodology as baseline experiment |

## Hypothesis Dependency Map

```
H1 (CRONOS-AM depth scaling)
 |
 +-- H2 (CRONOS-AM vs SGD on real data)
 |     Independent but complementary: H1 measures optimality gap scaling,
 |     H2 measures practical competitiveness. Both address Gap 1.2.
 |     If H1 shows super-linear degradation, H2 results contextualize severity.
 |
H3 (Rank-dependent duality gap bound)
 |
 +-- H5 (Rank-2 threshold test)
       H5 is a special case of H3. If H5 shows zero gap at rank 2,
       H3's monotonic-increase hypothesis needs revision. Run H5 first
       as a cheaper test; H3 extends it across the full rank spectrum.

H4 (Approximation tightness) -- Independent of all others

H6 (Elastic net breaks reformulation) -- Independent of all others

H7 (Convex optimum vs SGD generalization) -- Loosely related to H2
     (both compare convex and SGD solutions), but H7 measures test
     accuracy while H2 measures training loss. Can share infrastructure.
```

**Recommended execution order (for Phase 11 triage):**
1. H5 first (cheapest, validates setup for H3)
2. H1 or H2 (strongest gap, highest impact)
3. H4 (clean standalone experiment)
4. H3, H6, H7 as resources allow
