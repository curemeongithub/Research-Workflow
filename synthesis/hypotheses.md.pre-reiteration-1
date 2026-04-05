---
phase: 6
status: complete
timestamp: 2026-04-06T00:15:00Z
depends_on: [analysis/gap-analysis.md, analysis/review-notes.md]
token_estimate: 3200
---

# Hypotheses: Dual Convex Optimization in ReLU Neural Networks

## Hypothesis Formation Summary

Six testable hypotheses were formulated from the gap analysis, covering all three Tier 1 gaps and three selected Tier 2 gaps. Gaps 2.2 (continual learning) and 2.5 (SGD convergence) were excluded per sanity check advisory as they stretch beyond the core convex optimization mandate. The hypothesis set prioritizes full-rank tractability (Gap 1.2, highest composite score 7.8) while addressing the foundational recurrent architecture gap (1.1) and the duality gap characterization problem (1.3). The Tier 2 hypotheses target practical deployment constraints: adversarial robustness (2.1), multi-head attention (2.4), and weight quantization (2.3). All hypotheses specify measurable outcomes, falsification criteria, and build on established results from Pilanci-Ergen (2020), Bach (2017), and the parallel network bidual construction of Wang et al. (2023).

---

## Primary Hypotheses (from Tier 1 gaps)

### H-1: Polynomial-Time Certified Approximation for Full-Rank Data

**Source gap:** Gap 1.2 (Full-Rank Tractability — Closing the Exponential-in-Rank Barrier with Optimality Certificates)

**Sanity check status:** LOW concern (composite score 7.8, highest priority)

**Hypothesis:**
> If a hierarchical zonotope subsampling tree is constructed over nested hyperplane arrangements for an $L$-layer ReLU network trained on rank-$r$ data with $r = \min(n,d)$ (full-rank), and the sampling budget per layer is $B_\ell = C \cdot d^2 \log(1/\delta)$ for constant $C$, then the resulting approximate solution achieves training loss within $(1 + \epsilon)$ of the global convex optimum $L^*$ with probability $\geq 1 - \delta$, as measured by the ratio $L_{\text{approx}} / L^*$ on CIFAR-10 (rank-2688), under a wall-clock time budget $\leq 10 \times$ the CRONOS runtime.

**Rationale:** The two-layer zonotope approximation result of Sahiner et al. [2312.12657] proves a dimension-free approximation ratio exists when sampling is sufficiently dense. Extending this to deep networks requires nested sampling: at layer $\ell$, the output region is the Minkowski sum of all previous layers' arrangement patterns. By constructing a sampling tree where each node represents a realized activation pattern and children represent refinements at the next layer, and sampling uniformly within each node's zonotope, the joint distribution over all layers can be controlled via conditional independence. The Carathéodory theorem guarantees that $m^* \leq (r+1)d$ active patterns suffice for optimality; hierarchical sampling with budget $O(d^2 \log(1/\delta))$ per layer ensures coverage of high-probability regions with approximation ratio bounded by the total variation distance between the sampled and exact hyperplane arrangement distributions.

**Null hypothesis:** The approximate solution achieves training loss $> (1 + \epsilon) L^*$ with probability $> \delta$, indicating the hierarchical sampling fails to capture critical activation patterns, or the sampling budget scales exponentially in depth $L$ rather than polynomially.

**Success criteria:**
- For $\epsilon = 0.1$, $\delta = 0.05$: $L_{\text{approx}} / L^* \leq 1.1$ holds on $\geq 95\%$ of random train/test splits of CIFAR-10.
- Sampling budget per layer $B_\ell \leq 10^5$ (tractable on single GPU).
- Total runtime $\leq 10 \times$ CRONOS baseline (which lacks approximation certificate).

**Potential confounds:**
1. Optimizer convergence: The convex solver may not reach optimum within iteration budget — control by running to duality gap $< 10^{-4}$.
2. Hyperplane degeneracy: Parallel arrangements reduce effective dimensionality — measure via condition number of the zonotope generator matrix.
3. Data preprocessing: Whitening or normalization affects rank — report both raw and whitened data results.

**FATS check:**
- **Falsifiable:** Yes — the ratio $L_{\text{approx}} / L^*$ is directly measurable; if it exceeds $1.1$ on $> 5\%$ of trials, H-1 is rejected.
- **Actionable:** Yes — hierarchical zonotope sampling is implementable via randomized projection trees (existing code in scipy.spatial).
- **Testable:** Yes — CIFAR-10 is a standard benchmark; running the exact convex solver on a small subset to compute $L^*$ provides ground truth.
- **Specific:** Yes — specifies data regime (full-rank), approximation bound ($1 + \epsilon$), probability threshold ($1 - \delta$), and runtime constraint ($10\times$ CRONOS).

---

### H-2: Convex Reformulation for Unrolled Recurrent Networks via Temporal Hyperplane Coupling

**Source gap:** Gap 1.1 (Convex Reformulation for Recurrent and State-Space Architectures)

**Sanity check status:** LOW concern (composite score 7.6, highest impact per sanity check)

**Hypothesis:**
> If a vanilla RNN with shared recurrent weight matrix $\mathbf{W}_{\text{rec}} \in \mathbb{R}^{h \times h}$ is unrolled for $T$ time steps, and the recurrent connections are reformulated as linear equality constraints $\mathbf{z}_t = \mathbf{W}_{\text{rec}} \sigma(\mathbf{z}_{t-1})$ with auxiliary variables $\mathbf{z}_t$ treated as independent neuron activations subject to cross-time coupling, then the resulting lifted convex program over $\{(\mathbf{w}_t, \mathbf{v}_t)\}_{t=1}^T$ achieves training loss equal to the SGD-trained RNN baseline $\pm 5\%$ on sequential MNIST, while guaranteeing global optimality via zero duality gap verified by complementary slackness conditions.

**Rationale:** Pilanci and Ergen [2002.10553v2] explicitly name "recurrent networks" as an extension direction. The core obstacle is weight sharing across time: standard duality assumes per-layer independence. However, weight sharing can be reformulated as a *constraint* rather than a structural primitive: introduce time-indexed neuron variables $\{(\mathbf{w}_t, \mathbf{v}_t)\}$ for each unrolled step, then impose equality constraints $\mathbf{w}_1 = \mathbf{w}_2 = \cdots = \mathbf{w}_T$. This lifts the RNN into a $(T \cdot h)$-neuron feedforward network with linear constraints. The group-LASSO formulation of Pilanci-Ergen applies to the lifted neuron set; the weight-sharing constraints are affine (convex), preserving strong duality. The key question is whether the $(T \cdot h)$-neuron problem remains tractable — for sequential MNIST ($T = 784$ pixels, $h = 128$ hidden), this yields $\approx 10^5$ neurons, comparable to CRONOS-scale problems.

**Null hypothesis:** Either (a) the lifted convex program's duality gap is nonzero (strong duality fails due to constraint interaction), or (b) the computational cost scales as $O(T^3 h^3 n^{3h})$ (exponential in sequence length), rendering it intractable for $T > 50$.

**Success criteria:**
- Zero duality gap verified: $|P^* - D^*| / P^* < 10^{-3}$ on sequential MNIST.
- Training loss matches SGD baseline: $L_{\text{convex}} / L_{\text{SGD}} \in [0.95, 1.05]$.
- Solver converges within 1000 iterations using CVXPY/Mosek.

**Potential confounds:**
1. Unrolling depth $T$: Longer sequences may violate tractability — test $T \in \{50, 100, 200, 784\}$ to identify scaling threshold.
2. Initialization of SGD baseline: RNN training is notoriously unstable — average over 10 random seeds.
3. Gradient clipping in SGD: The nonconvex baseline may use clipping; ensure fair comparison by reporting both clipped and unclipped SGD.

**FATS check:**
- **Falsifiable:** Yes — duality gap is directly measurable; if $|P^* - D^*| / P^* > 10^{-3}$, strong duality has failed and H-2 is rejected.
- **Actionable:** Yes — constraint-based weight sharing is implementable in standard convex solvers via equality constraints.
- **Testable:** Yes — sequential MNIST is a standard RNN benchmark with established SGD baselines.
- **Specific:** Yes — specifies architecture (vanilla RNN), sequence length ($T$), hidden size ($h$), verification metric (duality gap $< 10^{-3}$), and performance target ($\pm 5\%$ of SGD).

---

### H-3: Width-Dependent Duality Gap Bound for Serial Deep Networks via Bidual Sandwiching

**Source gap:** Gap 1.3 (Tight Upper Bounds on Duality Gap for Standard Serial Deep Networks)

**Sanity check status:** MEDIUM concern (composite score 7.2; sanity check notes "entirely uncharacterized" is overstated, but upper bound is missing)

**Hypothesis:**
> If a standard serial $L$-layer ReLU network is trained with width $m$ neurons per layer, and the bidual construction of Wang et al. [WangErgenPilanci2023] is used to compute the dual lower bound $D^* = P^*_{\text{parallel}}$, then the duality gap $\Delta = P^*_{\text{serial}} - D^*$ is upper-bounded by $\Delta \leq (L-1) \cdot \exp(-(m - m^*)/(2m^*))$ where $m^* = (r+1)d$ is the Carathéodory bound, as measured by training a 3-layer network ($L=3$) on synthetic rank-2 data with varying width $m \in \{m^*, 2m^*, 5m^*, 10m^*\}$ and verifying the gap decays exponentially.

**Rationale:** Wang et al. prove the bidual of a serial network equals the primal of a parallel network, providing the constructive lower bound $D^*$. The gap arises because serial networks have constrained information flow (each layer depends only on the previous), while parallel networks allow direct skip connections from all layers to the output. The gap $\Delta$ quantifies the value of skip connections. The Carathéodory theorem implies that when $m \geq m^*$, the serial network can represent any function expressible by the parallel network, but the *optimization landscape* differs. The proposed bound conjectures that as width $m$ increases beyond $m^*$, the serial network's constrained optimization problem increasingly approximates the parallel network's relaxed problem. The exponential decay rate reflects the fact that each additional neuron beyond $m^*$ provides redundancy, reducing the probability that the serial constraint binds. This is analogous to concentration inequalities for random hyperplane arrangements (cf. Bach [2017] Theorem 3.2 on pattern diversity).

**Null hypothesis:** The duality gap $\Delta$ does not decay exponentially in $(m - m^*)$, or decays slower than $\exp(-(m - m^*)/(2m^*))$, indicating the serial-parallel gap is not simply a width-dependent phenomenon but reflects a fundamental structural difference unbounded by over-parameterization.

**Success criteria:**
- For synthetic rank-2 data ($m^* = 3d$): measure $\Delta(m)$ at $m \in \{m^*, 2m^*, 5m^*, 10m^*\}$.
- Fit exponential model $\Delta(m) = A \exp(-B(m - m^*))$ and verify $B \geq 1/(2m^*)$ with $R^2 > 0.9$.
- Bound holds for $L \in \{3, 4, 5\}$ (deeper networks may have tighter or looser bounds).

**Potential confounds:**
1. Solver precision: Numerical errors in computing $P^*$ and $D^*$ — require duality gap tolerance $< 10^{-5}$.
2. Data distribution: Gaussian vs. uniform data may affect the constant $A$ — test both.
3. Activation pattern diversity: If data lies in a lower-dimensional subspace, effective $m^*$ decreases — report intrinsic dimensionality via PCA.

**FATS check:**
- **Falsifiable:** Yes — if the fitted exponent $B < 1/(2m^*)$ or $R^2 < 0.9$, the exponential decay hypothesis is rejected.
- **Actionable:** Yes — the bidual construction is proven in Wang et al.; implementing it requires solving both serial and parallel convex programs and comparing objectives.
- **Testable:** Yes — synthetic data allows controlled variation of $m$ and $m^*$; gap $\Delta$ is measurable as primal objective difference.
- **Specific:** Yes — specifies functional form (exponential), decay rate ($1/(2m^*)$), width range ($m$ to $10m^*$), and fit quality threshold ($R^2 > 0.9$).

---

## Secondary Hypotheses (from Tier 2 gaps)

### H-4: Exact Adversarial Training via $\ell_\infty$-Constrained Hyperplane Arrangements

**Source gap:** Gap 2.1 (Certified Adversarial Robustness for Deep Multi-Layer Convex Networks)

**Sanity check status:** MEDIUM concern (confidence 6/10 — gap inferred from citations, not explicitly stated)

**Hypothesis:**
> If $\ell_\infty$-ball robustness constraints $\|\mathbf{x}' - \mathbf{x}\|_\infty \leq \epsilon$ are incorporated into the group-LASSO convex program for a parallel 3-layer network by expanding each training point $\mathbf{x}_i$ into a zonotope $\mathcal{Z}_i = \mathbf{x}_i + [-\epsilon, \epsilon]^d$, and requiring the learned function to satisfy $|f(\mathbf{x}) - y| \leq \tau$ for all $\mathbf{x} \in \mathcal{Z}_i$, then the resulting convex program yields a classifier with certified robust accuracy (PGD-40 attack) matching or exceeding IBP+CROWN bounds on MNIST $\epsilon = 0.3$, while guaranteeing global optimality via zero duality gap.

**Rationale:** The two-layer adversarial robustness work of Mishkin et al. [mishkin2022fast] demonstrates that $\ell_\infty$ constraints can be encoded as additional linear inequalities in the convex program. Extending to deep parallel networks leverages the zero-duality-gap result of Wang et al. [WangErgenPilanci2023]: the parallel architecture preserves strong duality even with additional affine constraints. Each adversarial ball $\mathcal{Z}_i$ defines a polytope in input space; the convex program's hyperplane arrangement must satisfy robustness constraints at all vertices of $\mathcal{Z}_i$ (via the ReLU polytope structure, this is finite and tractable). The key advantage over IBP/CROWN is that the convex formulation computes the *exact* maximum loss over $\mathcal{Z}_i$ (via worst-case vertices), whereas IBP/CROWN use interval relaxations that may be loose. Global optimality guarantees no adversarial perturbation within $\epsilon$ can increase loss beyond $\tau$.

**Null hypothesis:** The convex-optimal robust network achieves lower certified accuracy than IBP+CROWN, indicating the zonotope constraint encoding either breaks strong duality or is too conservative (over-constrains the function class).

**Success criteria:**
- Certified robust accuracy (PGD-40, $\epsilon = 0.3$) on MNIST: $\geq$ IBP+CROWN baseline (typically ~85%).
- Zero duality gap verified: $|P^* - D^*| / P^* < 10^{-3}$.
- Standard accuracy (clean data) $\geq 97\%$ (ensuring robustness doesn't collapse to trivial solution).

**Potential confounds:**
1. Perturbation budget $\epsilon$: Larger $\epsilon$ exponentially increases the number of zonotope vertices — test $\epsilon \in \{0.1, 0.2, 0.3\}$.
2. Attack strength: PGD-40 may be insufficient; verify with AutoAttack.
3. Network depth: Parallel 3-layer may not match standard serial 5-layer expressiveness — compare both at equal width.

**FATS check:**
- **Falsifiable:** Yes — certified accuracy is measurable via AutoAttack; if convex-optimal accuracy $<$ IBP+CROWN, H-4 is rejected.
- **Actionable:** Yes — zonotope vertex enumeration for $\ell_\infty$ balls is tractable (polytope with $2^d$ vertices); constraint encoding is standard in convex optimization.
- **Testable:** Yes — MNIST $\epsilon = 0.3$ is a standard certified robustness benchmark with established baselines.
- **Specific:** Yes — specifies attack (PGD-40, AutoAttack), perturbation ($\epsilon = 0.3$), accuracy threshold ($\geq$ IBP+CROWN), and architecture (parallel 3-layer).

---

### H-5: Multi-Head Attention Convex Formulation via Parallel Branch Decomposition

**Source gap:** Gap 2.4 (Multi-Head Attention with Residual Connections in Convex Reformulations)

**Sanity check status:** LOW concern (single-head restriction explicitly stated in Sahiner et al. [SahinerErgen2023])

**Hypothesis:**
> If a Vision Transformer (ViT) block with $H$ attention heads and residual connection $\mathbf{z}_{\text{out}} = \mathbf{z}_{\text{in}} + \text{MHA}(\mathbf{z}_{\text{in}})$ is reformulated as $H$ independent single-head convex programs (one per head) with a shared output constraint $\mathbf{z}_{\text{out}} = \mathbf{z}_{\text{in}} + \sum_{h=1}^H \mathbf{z}_h$, and each head's convex program is constructed via the attention transformation $\mathbf{z}_h = \text{Attention}(\mathbf{Q}_h, \mathbf{K}_h, \mathbf{V}_h)$ following Sahiner et al. [2205.08078], then the joint optimization over $H$ coupled programs with residual coupling yields training loss within 10\% of a standard AdamW-trained ViT-Tiny on CIFAR-10, as measured by cross-entropy loss, under sequential coordinate ascent optimization.

**Rationale:** Sahiner et al. proved convex duality for single-head attention without residuals. Multi-head attention is a parallelization: each head computes an independent attention transformation, and outputs are concatenated/summed. The residual connection $\mathbf{z}_{\text{out}} = \mathbf{z}_{\text{in}} + \text{MHA}(\mathbf{z}_{\text{in}})$ is a linear constraint (addition). By formulating each head $h$ as an independent convex program over its $(\mathbf{Q}_h, \mathbf{K}_h, \mathbf{V}_h)$ parameters, and coupling them via the residual constraint, the joint program remains convex (intersection of convex sets). The Wang et al. [WangErgenPilanci2023] parallel network result suggests this structure preserves strong duality: the parallel heads act like parallel branches, and the residual is a skip connection. Sequential coordinate ascent (optimizing one head at a time while fixing others) is guaranteed to converge for convex programs, though possibly to a local optimum of the coupled system — measuring optimality gap identifies if coupling breaks global optimality.

**Null hypothesis:** The coupled multi-head + residual program either (a) has nonzero duality gap due to residual interaction, or (b) achieves $> 10\%$ worse loss than AdamW-trained ViT-Tiny, indicating the single-head convex formulation does not compose to multi-head.

**Success criteria:**
- Training loss on CIFAR-10: $L_{\text{convex}} / L_{\text{AdamW}} \leq 1.10$.
- Duality gap: $|P^* - D^*| / P^* < 10^{-2}$ (moderate tolerance given coupling complexity).
- Convergence within 500 coordinate ascent iterations.

**Potential confounds:**
1. Residual scale: Standard ViTs use LayerNorm before residual addition — test both with and without normalization.
2. Head diversity: If heads learn redundant representations, the coupled program may collapse to a degenerate solution — measure head diversity via attention pattern correlation.
3. Optimizer: Coordinate ascent may be slow; test alternating direction method of multipliers (ADMM) as alternative.

**FATS check:**
- **Falsifiable:** Yes — loss ratio $L_{\text{convex}} / L_{\text{AdamW}}$ is directly measurable; if $> 1.10$, H-5 is rejected.
- **Actionable:** Yes — single-head convex formulation exists (Sahiner et al.); parallelization and residual coupling are standard in convex optimization.
- **Testable:** Yes — CIFAR-10 and ViT-Tiny are standard benchmarks; AdamW-trained baseline is reproducible.
- **Specific:** Yes — specifies architecture (ViT-Tiny, multi-head attention), constraint ($10\%$ loss gap), optimization method (coordinate ascent), and dataset (CIFAR-10).

---

### H-6: Quantization-Aware Convex Training via Mixed-Integer Group-LASSO Relaxation

**Source gap:** Gap 2.3 (Integer and Quantized Weight Constraints in the Convex Framework)

**Sanity check status:** LOW concern (distinction between quantized activations vs. weights is valid and clearly articulated)

**Hypothesis:**
> If integer weight constraints $\mathbf{w}_j \in \{-127, -126, \ldots, 127\}$ (INT8 quantization) are incorporated into the two-layer convex group-LASSO program via a rounding-based convex relaxation — where the continuous relaxation is solved, then weights are rounded to the nearest integer and the objective is re-evaluated — the resulting quantized network achieves test accuracy within 2\% of a post-training quantization (PTQ) baseline on CIFAR-10, while maintaining training loss within 5\% of the unquantized convex optimum, as measured by cross-entropy loss on a two-layer network with $m = 512$ neurons.

**Rationale:** Ergen and Pilanci [ErgenPilanci2023] address quantized *activations* (threshold networks), demonstrating the convex framework extends to discrete activation functions. Integer *weights* are a different constraint: the decision variable $\mathbf{w}_j$ is restricted to a discrete set. Mixed-integer convex programming is NP-hard in general, but for small bitwidths (INT8 = 256 values per weight), branch-and-bound or LP rounding with optimality certificates is tractable for moderate-scale problems (up to $10^4$ weights). The proposed approach: (1) solve the continuous convex relaxation to obtain $\mathbf{w}_j^*$, (2) round each $\mathbf{w}_j^* \to \text{round}(\mathbf{w}_j^*)$, (3) verify the rounded solution satisfies the KKT conditions of the quantized problem. If the rounding introduces slack, the gap between rounded and optimal quantized solution is bounded by the number of weights times the maximum rounding error (at most 0.5 per weight).

**Null hypothesis:** The quantized convex-trained network achieves $> 2\%$ lower accuracy than PTQ baseline, indicating the continuous-relaxation-then-round heuristic loses critical information, or the quantized problem's optimum is far from the continuous relaxation.

**Success criteria:**
- Test accuracy on CIFAR-10: $\text{Acc}_{\text{convex-INT8}} \geq \text{Acc}_{\text{PTQ}} - 2\%$ (e.g., if PTQ = 88\%, convex ≥ 86\%).
- Training loss of rounded solution: $L_{\text{INT8}} / L_{\text{continuous}}^* \leq 1.05$.
- Optimality certificate: KKT residual of rounded solution $< 10^{-2}$.

**Potential confounds:**
1. Quantization scheme: Symmetric vs. asymmetric INT8 affects dynamic range — test both.
2. Calibration data: PTQ baselines use calibration sets; ensure fair comparison by using the same calibration data for both.
3. Network depth: Two-layer networks may not expose quantization brittleness; extend to three layers if tractable.

**FATS check:**
- **Falsifiable:** Yes — accuracy gap is measurable; if convex-INT8 accuracy $< \text{PTQ} - 2\%$, H-6 is rejected.
- **Actionable:** Yes — continuous relaxation + rounding is a standard approximation for mixed-integer programs; implementations exist in CVXPY and Gurobi.
- **Testable:** Yes — CIFAR-10 PTQ baselines are well-established; two-layer networks with $m = 512$ are tractable.
- **Specific:** Yes — specifies bitwidth (INT8), network size ($m = 512$), accuracy threshold ($2\%$ of PTQ), and loss threshold ($5\%$ of continuous optimum).

---

## Excluded Gaps and Reasoning

### Gap 2.2: Continual and Online Learning via Convex Neural Networks
**Reason:** HIGH CONCERN per sanity check — "shifts focus from convex optimization of neural networks to continual learning, which is a distinct problem domain." The gap conflates "incremental data addition" (online optimization) with "catastrophic forgetting" (continual learning task boundaries). The cutting-plane algorithm's incremental constraint addition is an optimization implementation detail, not a continual learning method. **Excluded from hypothesis formation.**

### Gap 2.5: Non-Convex Gradient Descent Convergence Guarantees to the Convex Global Optimum
**Reason:** MEDIUM-HIGH CONCERN per sanity check — "addresses non-convex optimization theory (when does SGD converge to global optima?) rather than convex optimization for neural networks." The proposed research direction (PL-condition + hyperplane bijection → convergence guarantee) is plausible but "arguably belongs in the over-parameterization/NTK literature, not the convex duality literature per se." Scope concern: this is a gap in a *neighboring field* (gradient descent dynamics), not in convex reformulations. **Excluded from hypothesis formation.**

### Gap 3.1: Formal Characterization of the Initialization-Independence Boundary
**Reason:** Tier 3 stress-test with low practical impact (4/10). While scientifically interesting, formulating a testable hypothesis for the width threshold $m^*(r, n, d)$ below which initialization matters is secondary to the foundational and extension hypotheses. **Deferred to future work.**

### Gap 3.2: CRONOS Throughput Scalability to Adaptive Architecture Search
**Reason:** Tier 3 stress-test focused on throughput engineering rather than mathematical formulation. While CRONOS-style NAS would be valuable, it is a systems/engineering challenge (GPU kernel optimization, neural architecture search integration) rather than a theoretical gap in convex duality. **Deferred to future work.**

---

## Hypothesis Dependency Map

**Independent hypotheses:** H-1, H-2, H-4, H-6 can be tested independently; no cross-dependencies.

**Dependent hypotheses:**
- **H-3 depends on H-1 (weak dependency):** The width-dependent duality gap bound (H-3) is most meaningful if full-rank tractability (H-1) is resolved, as it addresses the serial-vs-parallel tradeoff for real data. However, H-3 can be tested on low-rank synthetic data independently.
- **H-5 depends on H-4 (weak dependency):** Both use parallel network convex formulations (H-4 for robustness, H-5 for multi-head attention). If H-4 demonstrates that parallel architectures preserve strong duality under additional constraints, this strengthens confidence in H-5's residual-coupling approach. However, H-5 can proceed independently using the existing Wang et al. parallel network result.

**Execution order recommendation:**
1. **H-1** (full-rank tractability) — highest composite score, unlocks real-data applications.
2. **H-2** (recurrent networks) — foundational, highest impact per sanity check.
3. **H-3** (duality gap bounds) — builds on H-1's full-rank methods, provides theoretical characterization.
4. **H-4** (adversarial robustness) — Tier 2, high verifiability (standard benchmarks).
5. **H-5** (multi-head attention) — Tier 2, moderate difficulty.
6. **H-6** (quantized weights) — Tier 2, lowest feasibility of selected hypotheses but high practical value.

---

## Connection to Known Results

All six hypotheses build explicitly on the following established theorems and results:

### From Pilanci and Ergen [2002.10553v2, 2020]:
- **Group-LASSO convex formulation** for two-layer ReLU networks (Theorem 1): The foundation for H-1, H-6.
- **Hyperplane arrangement bijection** (Theorem 2): The neuron-to-hyperplane correspondence used in H-1's zonotope sampling and H-2's temporal coupling.
- **Carathéodory bound** $m^* = (r+1)d$: Appears in H-1 (sampling budget), H-3 (width threshold), and H-6 (over-parameterization for quantization).
- **Future work statement on recurrent networks** (Section 6): Direct motivation for H-2.

### From Bach [2017]:
- **Pattern diversity concentration for random hyperplanes** (Theorem 3.2): Theoretical basis for H-1's approximation ratio and H-3's exponential decay conjecture.

### From Wang, Ergen, Pilanci [WangErgenPilanci2023]:
- **Parallel network bidual construction** (Theorem 4): The $D^* = P^*_{\text{parallel}}$ identity used in H-3's gap bound.
- **Zero duality gap for parallel architectures** (Theorem 5): Enables H-4 (parallel network for robustness) and H-5 (multi-head as parallel branches).

### From Sahiner, Ergen, et al. [SahinerErgen2023, 2205.08078]:
- **Single-head attention convex formulation** (Theorem 1): Foundation for H-5's multi-head extension.
- **Zonotope approximation ratio for two-layer networks** [2312.12657]: Starting point for H-1's hierarchical extension.

### From Ergen and Pilanci [ErgenPilanci2023]:
- **Threshold activation convex formulation**: Demonstrates discretization is compatible with convex framework, motivating H-6's integer weight extension.

**All hypotheses are grounded in proven results** — none rely on unverified conjectures as premises. The novelty lies in *extending* and *combining* these results to address the identified gaps.
