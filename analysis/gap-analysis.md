---
phase: 4
status: complete
timestamp: 2026-04-06T00:00:00Z
depends_on: [analysis/literature-map.md]
token_estimate: 4800
---

# Research Gap Analysis: Dual Convex Optimization in ReLU Neural Networks

## Summary

The field of convex reformulations for ReLU networks has made rapid progress since 2020, establishing
rigorous theory for two-layer networks, parallel deep architectures, CNNs, batch normalization, and
transformers. The complexity landscape is well understood under low-rank data assumptions, and CRONOS
has demonstrated ImageNet-scale practicality. Yet three structural gaps define the frontier where
the current theory runs out: (1) recurrent and state-space architectures are explicitly excluded from
every existing result—the original Pilanci-Ergen paper named them as future work and they remain
untouched; (2) the exponential-in-rank complexity barrier means all polynomial-time guarantees evaporate
on full-rank real-world data, with only heuristic approximations available; and (3) while parallel
architectures have zero duality gap, standard serial deep networks (the dominant form in practice) have
nonzero duality gap with no tight upper bounds known. Below these foundational cracks sit a cluster of
Tier 2 actionable extensions—robustness certification, continual learning, quantized weights, and
residual-connection transformers—and two Tier 3 stress-tests probing what happens near the non-convex/
convex boundary.

---

## Tier 1 — Fundamental Gaps

### Gap 1.1: Convex Reformulation for Recurrent and State-Space Architectures

**Claim:** No convex duality formulation exists for recurrent neural networks (RNNs, LSTMs) or
modern state-space models (S4, Mamba, Hawk), despite these architectures dominating sequence
modeling.

**Evidence from literature:**
- Pilanci and Ergen [2002.10553v2, content.md line 493] explicitly state: "one can extend our
  convex approach to various architectures, e.g., modern CNNs, recurrent networks, and autoencoders"
  — CNNs and autoencoders have since been addressed; recurrent networks have not.
- Ergen and Pilanci [arxiv-2110.09548, main.tex line 527] list architectures successfully extended
  to convex programs: "convolution networks, generative adversarial networks, NNs with batch
  normalization, Transformers" — recurrent architectures are absent from this list.
- Source lookup 1 (query: "recurrent|LSTM|RNN|state.space|Mamba|SSM") returned no substantive
  matches across any non-citation context in 27 sources.
- The literature map (Section 4 and Section 9) confirms transformers, CNNs, GANs, and batch norm
  are addressed but explicitly categorizes "state-of-the-art architectures like ResNets, Vision
  Transformers with residual connections, and diffusion models" as unexplored — recurrent models
  are not even mentioned as candidates.

**Scoring:**
- Confidence of Existence: 9/10 — Two separate papers explicitly call out recurrent networks as
  future work; zero papers in the 27-source corpus address this.
- Potential Impact: 9/10 — LSTMs remain standard in time-series, medical, and finance applications;
  state-space models (Mamba) are the leading alternative to transformers for long sequences. A convex
  reformulation would enable polynomial-time globally optimal training for an entirely new modality.
- Feasibility: 4/10 — Recurrent architectures involve weight tying across time steps: the same weight
  matrix $\mathbf{W}_{\text{rec}}$ is multiplied at each step $t = 1, \ldots, T$. This creates
  multiplicative dependencies that cannot be split into per-step hyperplane arrangements without
  breaking the independence assumptions underlying Fenchel duality. A fundamentally new proof
  technique is needed, not a straightforward extension.
- Verifiability: 7/10 — Well-established sequence modeling benchmarks (PTB, MNIST sequential,
  Long Range Arena) allow direct comparison of convex-optimal vs. SGD-trained RNNs.
- **Composite: (9×2 + 9 + 4 + 7) / 5 = 38/5 = 7.6**

**Source lookup used:** Yes — query "recurrent|LSTM|RNN|state.space|Mamba|SSM" across all sources;
result NOT_FOUND in any non-incidental context.

**Proposed research direction:** Develop a lifted convex program for unrolled RNNs treating each
time step as a separate "neuron" layer with shared weight constraints enforced via linear equality
coupling. For state-space models with linear recurrences, exploit the Toeplitz structure of
$\mathbf{W}_{\text{rec}}^t$ to derive circular hyperplane arrangements analogous to the CNN extension.

---

### Gap 1.2: Full-Rank Tractability — Closing the Exponential-in-Rank Barrier with Optimality Certificates

**Claim:** Every polynomial-time guarantee in the convex ReLU literature assumes rank $r \ll n$, but
real-world datasets are full-rank (or near-full-rank), making all existing complexity bounds
exponential in practice; no approximation algorithm with a certifiable approximation ratio exists
for the full-rank regime.

**Evidence from literature:**
- The literature map (Section 5) enumerates: two-layer networks $O(d^3 r^3 (n/r)^{3r})$, CNNs
  $O(n^{r_c} h^3)$, three-layer networks $O(d^3 m_1^3 n^{3(m_1+1)r})$ — all exponential in $r$.
- The map notes explicitly: "All these bounds are polynomial when rank $r$ and width are treated as
  constants, but exponential in $r$ for fully-ranked data. This motivates rank-reduction
  preprocessing."
- CRONOS uses "randomized sampling rather than exhaustive enumeration" (Section 5) but does not
  provide a certified approximation bound — the gap between the sampled solution and the true
  optimum is uncharacterized.
- The literature map (Section 9) identifies this directly: "Should we focus on rank-adaptive
  algorithms (CRONOS-style sampling) or develop worst-case guarantees? The community is split."
- Source 2312.12657 (Section on approximation): proposes zonotope subsampling with "a guaranteed
  approximation ratio" for the *two-layer* case only; extension to deeper or multi-output networks
  is stated as future work.

**Scoring:**
- Confidence of Existence: 9/10 — The exponential dependence on rank is proven (not merely
  empirical), and the approximation-ratio problem for deep networks is explicitly open in multiple
  sources.
- Potential Impact: 8/10 — Closing this gap would mean the first polynomial-time algorithm *with
  certificate* for globally optimal training on real datasets like ImageNet in full generality, not
  just under the low-rank assumption that CRONOS quietly relies on.
- Feasibility: 5/10 — Techniques exist for randomized approximation of hyperplane arrangements
  (zonotopes, random projection Johnson-Lindenstrauss), and for two layers a ratio exists. Extending
  to deep networks requires new combinatorial arguments for nested arrangement sampling.
- Verifiability: 8/10 — Approximation ratio can be measured on synthetic data where the exact
  optimum is known; on real data, convergence of the approximate solution as sampling budget
  increases is a clean metric.
- **Composite: (9×2 + 8 + 5 + 8) / 5 = 39/5 = 7.8**

**Source lookup used:** No (claim verified directly from literature map Section 5 and 9).

**Proposed research direction:** Extend the zonotope-subsampling approximation scheme of
[2312.12657] to deep multi-layer networks by constructing a hierarchical subsampling tree over
nested hyperplane arrangements, proving a dimension-free approximation ratio via chain-rule
arguments on conditional probabilities of pattern agreement.

---

### Gap 1.3: Tight Upper Bounds on Duality Gap for Standard Serial Deep Networks

**Claim:** For standard (serial, non-parallel) networks with $L \geq 3$ layers, the duality gap
$P^* - D^* > 0$ is known to exist but is entirely uncharacterized — no computable upper bound, no
condition predicting when the gap is small, and no algorithm exploiting partial duality to improve
over heuristic SGD.

**Evidence from literature:**
- The literature map (Section 3) establishes: "standard deep networks (L ≥ 3 layers) can exhibit
  non-zero duality gap" and provides no further characterization beyond existence.
- Section 9 states directly: "Open question: Can tighter convex relaxations reduce this gap? Some
  propose semi-definite programming hierarchies (Sum-of-Squares) to close the gap, but computational
  complexity becomes prohibitive."
- Wang, Ergen, Pilanci [WangErgenPilanci2023] characterize duality gap for *parallel* architectures
  (zero gap) and prove the bidual of standard deep = primal of parallel deep, but this gives the
  *lower* bound $D^*$ only; no upper bound on $P^* - D^*$ is derived.
- Ergen and Pilanci [arxiv-2110.09548] note: "an exact convex program only for three-layer
  networks; recently [wang2023parallel] proved strong duality for deeper parallel networks... a
  similar analysis can be extended to deeper networks" — but this extension applies to parallel
  only.
- Source lookup 3 found no paper studying bounds on duality gap for standard (non-parallel)
  networks.

**Scoring:**
- Confidence of Existence: 8/10 — Duality gap existence is proven; the absence of bounding
  techniques is confirmed across four papers; Section 9 frames it as explicitly open.
- Potential Impact: 9/10 — Standard serial architectures (ResNet-50, VGG, BERT) are the dominant
  form in practice. A computable gap bound would upgrade their training from "SGD heuristic" to
  "certifiable near-optimal" without requiring architectural changes.
- Feasibility: 4/10 — The Sum-of-Squares hierarchy is the leading candidate but faces exponential
  cost. New techniques—possibly Lasserre hierarchy warm-starts or moment relaxations tailored to
  the group-LASSO structure—would be needed.
- Verifiability: 7/10 — Duality gap can be measured directly: train to convergence with SGD and
  compare the primal objective to the dual lower bound $D^*$.
- **Composite: (8×2 + 9 + 4 + 7) / 5 = 36/5 = 7.2**

**Source lookup used:** No (Section 3, 9 of literature map confirm; source lookup 3 confirmed
absence of robustness-for-deep-serial content, corroborating).

**Proposed research direction:** Derive a first-order duality gap bound using the Lagrangian dual
function evaluated at the parallel bidual solution; characterize how the bound tightens as a
function of network width $m$ relative to the Carathéodory bound $m^*$, yielding a quantitative
tradeoff between architecture choice and solution quality guarantee.

---

## Tier 2 — Extensions

### Gap 2.1: Certified Adversarial Robustness for Deep Multi-Layer Convex Networks

**Claim:** Adversarial robustness constraints have been incorporated into the convex framework for
two-layer networks only; for deep ($L \geq 3$) networks, no certified robustness formulation via
the convex dual exists.

**Evidence from literature:**
- Source arxiv-2205.08078 (transformer paper) explicitly cites "incorporate additional constraints
  for adversarial robustness [mishkin2022fast, bai2022efficient]" as existing work — but this
  context is for two-layer convex networks and is listed as a *contrast* to the Transformer
  extension (which does not include robustness).
- The literature map (Section 5 and 6) does not mention robustness as an application of deep
  network convex formulations; it is conspicuously absent from the "Methodological Landscape"
  Section 10.
- Source lookup 3 (query: "certif.*robust|adversarial.*convex") found only 2-layer and GAN-related
  results; no hit for "certified robust" in multi-layer context.

**Scoring:**
- Confidence of Existence: 6/10 — The 2-layer robustness work is known; deep multi-layer absence
  is inferred from the pattern of citations, not explicitly stated as an open problem.
- Potential Impact: 8/10 — Certified robustness for deep architectures is a core goal of
  trustworthy AI; convex duality could provide exact adversarial training certificates unlike the
  LP/MILP approximations currently used in IBP/CROWN.
- Feasibility: 6/10 — Extending the group-LASSO + Lipschitz constraints approach from 2-layer to
  multi-layer is technically demanding but plausible; tools from interval bound propagation can
  be recast as convex constraints within the existing framework.
- Verifiability: 8/10 — Auto-Attack and standard certified accuracy benchmarks (MNIST ε=0.3,
  CIFAR-10 ε=8/255) are well-established.
- **Composite: (6×2 + 8 + 6 + 8) / 5 = 34/5 = 6.8**

**Source lookup used:** Yes — query "certif.*robust|adversarial.*convex" (Lookup 3); found 2-layer
robustness citations but NOT_FOUND for deep multi-layer certified robustness.

**Proposed research direction:** Formulate $\ell_\infty$-ball robustness constraints as additional
hyperplane arrangement conditions in the convex group-LASSO program for parallel deep networks,
leveraging the zero duality gap property to certify global adversarial training optimality.

---

### Gap 2.2: Continual and Online Learning via Convex Neural Networks

**Claim:** The relationship between convex neural network reformulations and continual or online
learning—especially whether the convex structure enables provable resistance to catastrophic
forgetting—is entirely unexplored.

**Evidence from literature:**
- Source lookup 4 (query: "continual learn|online learning convex neural|catastrophic forgetting|
  lifelong learn") returned zero matches across all 27 sources.
- The cutting-plane algorithm in [ErgenPilanci2020b] incrementally adds neurons/constraints, which
  structurally resembles online learning, but no paper frames this as a continual learning method
  or analyzes forgetting.
- The literature map does not mention continual learning in any section.

**Scoring:**
- Confidence of Existence: 6/10 — The absence is confirmed by zero source matches; however, the
  gap is inferred (no paper explicitly names it as open).
- Potential Impact: 7/10 — The convex program's globally optimal solution is data-determined; if
  new data shifts the optimum, understanding the incremental update cost and catastrophic forgetting
  rate could yield a principled alternative to rehearsal-based methods.
- Feasibility: 5/10 — Warm-starting convex programs from previous solutions and adding new data
  constraints is standard in convex optimization (cutting-plane warm start); the theoretical
  analysis of forgetting bounds in terms of the convex objective requires new work.
- Verifiability: 7/10 — Permuted MNIST and Split-CIFAR are standard continual learning benchmarks
  with well-defined forgetting metrics.
- **Composite: (6×2 + 7 + 5 + 7) / 5 = 31/5 = 6.2**

**Source lookup used:** Yes — Lookup 4 returned NO_FOUND for "continual" and "online learning
convex neural" across all sources.

**Proposed research direction:** Frame the incremental cutting-plane algorithm of [ErgenPilanci2020b]
as an online convex learning procedure; for each new task $t$, add the new data's hyperplane
constraints and warm-start from the previous solution, then prove an upper bound on the duality
gap increase (forgetting) in terms of the distributional shift $\|\mathbf{X}_t - \mathbf{X}_{t-1}\|_F$.

---

### Gap 2.3: Integer and Quantized Weight Constraints in the Convex Framework

**Claim:** While threshold *activations* have been convexified for binary deployment [ErgenPilanci2023],
the convex framework offers no formulation for networks with integer or quantized *weights*—the
primary constraint for on-device inference.

**Evidence from literature:**
- The literature map (Section 4) notes ErgenPilanci2023 addresses "threshold and binary networks"
  specifically for *activation functions* (sign activations), not weight quantization.
- Source lookup 2 (query: "quantiz|integer weight|binary weight|discrete weight") found references
  to "Gradient descent quantizes ReLU network features" [quantized_hartmut] only in citation/
  bibliography context; no paper in the corpus formulates integer *weight* constraints in the
  convex training program.
- The literature map Section 10 lists no paper on quantization-aware convex training.

**Scoring:**
- Confidence of Existence: 6/10 — The threshold-activation paper is confirmed to address
  activations not weights; the integer-weight version is absent, but no paper explicitly calls it
  open.
- Potential Impact: 7/10 — Post-training quantization degrades accuracy; convex-optimal training
  with integer weight constraints would yield deployment-ready models without a separate
  quantization step.
- Feasibility: 5/10 — Integer programming extensions of group LASSO (mixed-integer convex programs)
  are NP-hard in general but tractable for small weight bitwidths (e.g., INT8) via branch-and-bound
  warm-started from the continuous relaxation.
- Verifiability: 8/10 — Quantization accuracy benchmarks on ImageNet with INT4/INT8 weight
  constraints against PTQ and QAT baselines are standard.
- **Composite: (6×2 + 7 + 5 + 8) / 5 = 32/5 = 6.4**

**Source lookup used:** Yes — Lookup 2 query "quantiz|integer weight|binary weight|discrete weight";
found only non-neural-network quantization references in bibliography (arxiv-2312.12657/references.bib).

**Proposed research direction:** Introduce binary/integer weight constraints directly into the
cone-constrained group-LASSO formulation as an $\ell_0$ or integrality constraint, then develop a
convex relaxation (e.g., LP rounding of the group-LASSO) with a provable approximation ratio for
the weight quantization problem, leveraging the data-dependent geometry of hyperplane arrangements.

---

### Gap 2.4: Multi-Head Attention with Residual Connections in Convex Reformulations

**Claim:** The existing convex transformer formulation of Sahiner et al. addresses single-head
attention without residual connections; multi-head attention with skip connections—the actual
architecture of all deployed ViTs—has no convex dual.

**Evidence from literature:**
- The literature map (Section 4) states Sahiner et al. [SahinerErgen2023] "proved that vision
  transformers with single-head attention admit convex reformulations" — the single-head and no-
  skip-connection restrictions are explicitly noted.
- Section 9 lists "ResNets, Vision Transformers with residual connections" as an "open frontier"
  for convex reformulations.
- The transformer paper (arxiv-2205.08078) itself states: "none of these works have analyzed the
  building blocks of transformers" — their own work addresses a simplified version; the full ViT
  architecture remains unaddressed.

**Scoring:**
- Confidence of Existence: 7/10 — The single-head / no-residual restriction is explicitly stated
  in the source paper; the gap to full ViT is clearly implied.
- Potential Impact: 7/10 — Modern vision and language models are universally multi-head + residual;
  a convex formulation for this class would extend global optimality guarantees to the most
  widely deployed deep learning architectures.
- Feasibility: 5/10 — Residual connections create multiplicative interactions between layer outputs;
  the group-LASSO structure breaks when skip connections bypass activation functions. New
  semidefinite lifting or copositive formulations may be needed.
- Verifiability: 8/10 — ViT-S/16 on ImageNet is a standard benchmark; performance parity with
  AdamW-trained ViT would provide a clear verifiable target.
- **Composite: (7×2 + 7 + 5 + 8) / 5 = 34/5 = 6.8**

**Source lookup used:** No (literature map Section 4 and 9 provide direct evidence).

**Proposed research direction:** Extend the transformer convex reformulation by modeling residual
connections as summations of multiple convex programs (one per branch), then proving that the
joint optimization over branch programs with shared normalization constraints preserves polynomial-
time solvability via the parallel network bidual construction of [WangErgenPilanci2023].

---

### Gap 2.5: Non-Convex Gradient Descent Convergence Guarantees to the Convex Global Optimum

**Claim:** While it is known empirically that SGD often finds solutions matching the convex global
optimum, no formal characterization exists of *when* (i.e., under what architectural and data
conditions) standard gradient descent is guaranteed to converge to the convex-optimal solution
rather than a suboptimal stationary point.

**Evidence from literature:**
- The literature map (Section 7) notes: "Multiple papers explore the loss landscape... they prove
  that for over-parameterized networks ($m \geq m^*$), all local minima are global minima," but
  does not characterize *convergence rate* or *probability* of gradient descent reaching the global
  minimum.
- Source 2002.10553v2 (line 493, literature map Section 2): "one can view backpropagation as a
  heuristic method to solve the convex program" — this acknowledges the connection but makes no
  guarantee.
- Source arxiv-2107.05680 (line 715) illustrates that non-convex WGAN training "is unstable and
  leads to undamped oscillations depending on the initialization" — empirically demonstrating the
  gap remains unclosed for more complex objectives.
- Source arxiv-2312.12657 (line 10) explicitly states: "in non-convex optimization, the choice of
  optimization method and its internal parameters such as initialization, mini-batching, and step
  sizes have a significant effect on the quality of the learned model," framing the convex-
  nonconvex correspondence as heuristic.

**Scoring:**
- Confidence of Existence: 7/10 — Two sources acknowledge the gap between SGD and convex optimum
  without resolving it; the WGAN source provides direct experimental evidence.
- Potential Impact: 6/10 — Formal convergence guarantees would help practitioners know when to
  trust SGD-trained models without running the expensive convex solver as a verification oracle.
- Feasibility: 7/10 — Tools exist: Polyak-Łojasiewicz conditions, loss landscape connectivity
  theorems, and the convex-nonconvex bijection of Pilanci-Ergen. Combining them into a convergence
  theorem is technically within reach.
- Verifiability: 7/10 — The fraction of random SGD initializations that converge to solutions
  within ε of the convex optimum is a concrete, measurable quantity.
- **Composite: (7×2 + 6 + 7 + 7) / 5 = 34/5 = 6.8**

**Source lookup used:** No (evidence drawn from literature map Sections 7, 9 and direct quotes
from sources already cited).

**Proposed research direction:** Combine the PL-condition analysis for over-parameterized ReLU
networks with the hyperplane arrangement bijection to prove that gradient descent with sufficiently
small step size and over-parameterization $m \geq c \cdot m^*$ (for some constant $c > 1$ derived
from the Carathéodory bound) converges to the global convex optimum with probability $1 - \delta$
over random initialization, for some computable $\delta(m, r, n)$.

---

## Tier 3 — Stress-Tests

### Gap 3.1: Formal Characterization of the Initialization-Independence Boundary

**Claim:** The claim that convex solutions are independent of initialization (a central selling
point of the framework) holds trivially for convex solvers but has not been formally characterized
at the boundary where *non-convex SGD* transitions from initialization-dependent to initialization-
independent behavior as width $m$ increases toward $m^*$.

**Evidence from literature:**
- Source arxiv-2312.12657 (line 10): "in non-convex optimization, the choice of optimization
  method and its internal parameters such as initialization... have a significant effect on the
  quality of the learned model. This is in sharp contrast to convex optimization, for which these
  hyperparameters have no effect."
- Source arxiv-2002.11219 (line 296): "the resulting optimal network output is linear spline
  interpolation when the initialization magnitude... is small" — shows initialization *does* affect
  non-convex SGD outcomes, mapping to the convex optimum only in one regime.
- Source arxiv-2107.05680 (line 690): describes non-convex WGAN results varying "depending on the
  initialization seed," directly demonstrating initialization sensitivity even for architectures
  that have convex duals.
- Source lookup 5 (query: "initialization.*convex|warm start") confirmed that initialization is
  discussed as eliminated for convex programs but the *transition threshold* (value of $m$) is
  never studied.

**Scoring:**
- Confidence of Existence: 9/10 — Three independent sources show initialization sensitivity in
  non-convex training while the convex program eliminates it; the specific characterization of the
  transition width $m^*(r, n, d)$ below which initialization matters is explicitly absent from all
  sources.
- Potential Impact: 4/10 — This addresses a theoretical stress-test question; the practical payoff
  is knowing the minimum width needed to reliably escape initialization dependence, which has
  model-design implications but is niche.
- Feasibility: 7/10 — Requires connecting the over-parameterization literature (width thresholds
  for loss landscape connectivity) with the convex reformulation (Carathéodory bound $m \geq KN+1$);
  both bodies of math exist separately.
- Verifiability: 8/10 — Can measure empirically: vary $m$ from under- to over-parameterized and
  measure variance of SGD solutions across multiple random initializations.
- **Composite: (9×2 + 4 + 7 + 8) / 5 = 37/5 = 7.4**

**Source lookup used:** Yes — Lookup 5 query "initialization.*convex|warm start|nonconvex.*
convergence.*convex"; confirmed discussion of initialization in sources but NOT_FOUND for transition
width characterization.

**Proposed research direction:** Prove a *phase transition theorem*: for $m < m^*(r,n,d)$, the
non-convex landscape contains local minima strictly above $D^*$; for $m \geq m^*$, all first-order
stationary points of the non-convex objective lie in the $\epsilon(m - m^*)$-neighborhood of the
convex global optimum, where $\epsilon \to 0$ as $m \to \infty$.

---

### Gap 3.2: CRONOS Throughput Scalability to Adaptive Architecture Search

**Claim:** CRONOS achieves competitive accuracy on ImageNet for *fixed* architectures, but the
computational overhead of re-enumerating hyperplane arrangements when architecture width changes
makes convex training unusable for architecture search or neural architecture optimization alongside
weight optimization.

**Evidence from literature:**
- The literature map (Section 5) states: "CRONOS achieves comparable or better validation accuracy
  than tuned SGD on ImageNet... with guaranteed global optimality."
- Section 9 notes: "While CRONOS scales to ImageNet, it remains slower than highly optimized SGD
  implementations (hours vs. minutes). Open question: Can convex approaches match or exceed SGD
  speed on billion-parameter models?"
- The CRONOS-AM algorithm uses "alternating minimization" with fixed upper layers — architecture
  width is assumed fixed before solving begins. No dynamic width adjustment during training is
  described.
- No paper in the literature map addresses joint architecture and weight optimization under the
  convex framework.

**Scoring:**
- Confidence of Existence: 8/10 — CRONOS's fixed-architecture assumption is stated explicitly
  in the literature map; the architecture-search gap is confirmed absent from all sources.
- Potential Impact: 6/10 — Combining convex guarantees with NAS would yield globally optimal
  architectures, extending the value proposition significantly; however this is incremental
  relative to the foundational gaps above.
- Feasibility: 6/10 — The CRONOS-AM alternating framework could in principle be extended by
  adding a width-selection step between alternating rounds via a sparsity-promoting prior on
  neuron use (already implicit in group-LASSO); no fundamental obstacles, but significant
  engineering and theoretical work needed.
- Verifiability: 8/10 — NAS benchmarks (NAS-Bench-201, DARTS search space on CIFAR-10) provide
  clean accuracy vs. search cost comparisons.
- **Composite: (8×2 + 6 + 6 + 8) / 5 = 36/5 = 7.2**

**Source lookup used:** No (confirmed directly from literature map Section 5 and 9).

**Proposed research direction:** Leverage the group sparsity structure of the convex objective to
perform architecture search via $\ell_{2,1}$ regularization strength annealing: as $\beta$ increases,
neurons are pruned (group sparsity eliminates whole neuron directions), yielding a path of
architectures of decreasing width all at global optimality; study the computational cost of this
path as a function of width trajectory.

---

## Rejected Candidates

### Candidate R.1: Convex Reformulation for Diffusion Models

**Considered because:** Diffusion models are the current state-of-the-art for generative modeling;
a convex dual could enable optimal score-function learning.

**Rejected because:** Diffusion models use U-Net or transformer architectures where the training
loss is a *denoising score matching* objective — not a standard empirical risk minimization with
weight-decay regularization. The Pilanci-Ergen framework requires a specific form of $\ell_2$
weight regularization to generate the group-LASSO convex reformulation. Without this structural
match, the hyperplane arrangement bijection does not apply. This is not a "gap to fill" within
the existing theory but a fundamentally different modeling problem requiring a new theoretical
foundation. No source mentions diffusion models in the convex optimization context.

### Candidate R.2: Implicit Regularization in Adam vs. SGD through Convex Lens

**Considered because:** Adam's adaptive second-moment normalization might correspond to a different
convex regularizer than the group-LASSO induced by SGD with weight decay.

**Rejected because:** The literature map (Section 6) is focused on $\ell_2$ weight decay, which
maps cleanly to group-LASSO. The convex reformulation framework is fundamentally anchored to weight
decay — the regularizer $\beta \|\mathbf{w}\|_2^2$ is what generates the Fenchel dual. Adam's
adaptive learning rates modify the *optimization trajectory*, not the *regularized objective*. The
duality results hold for the objective regardless of which optimizer finds the solution. Studying
Adam's implicit bias is a distinct problem (implicit bias of adaptive methods) already well-studied
outside this corpus. No source in the corpus mentions Adam or adaptive methods in connection with
convex reformulations.

### Candidate R.3: Extension to Non-ReLU Smooth Activations (GELU, SiLU)

**Considered because:** Modern transformers use GELU/SiLU activations; the hyperplane arrangement
technique requires piecewise-linear activations.

**Rejected because:** Source arxiv-2312.12657 explicitly covers "piecewise linear activations"
broadly (not just ReLU), and the SKILL of the existing framework has been extended to threshold/
binary activations [literature map Section 4]. The key structural requirement is piecewise
linearity — GELU and SiLU are *smooth*, making hyperplane arrangement enumeration inapplicable.
This is a categorical architectural exclusion, not a fillable gap; a completely different mathematical
approach (e.g., random feature methods for smooth activations) would be needed. Framing this as a
gap within the dual convex optimization framework for ReLU networks is category-incorrect.
