---
phase: 3
status: complete
timestamp: 2026-04-06T00:00:00Z
depends_on: [sources/manifest.yaml]
token_estimate: 5200
source_note: "Six user-PDF papers fully read; arXiv duplicates also confirmed. Multiple arXiv sources are Phase 1 acquisition mismatches and were excluded. NTK blog post read; Francis Bach blog returned 404."
---

# Literature Map: Dual Convex Optimization in ReLU Neural Networks

## 1. Overview of the Field

Training neural networks is, at its core, a non-convex optimization problem over continuous parameters that interact multiplicatively through nonlinear activation functions. For ReLU networks in particular, the piecewise-linear structure of the activation introduces an exponential number of linear regions, making the search for global optima appear intractable in general. The prevailing practice relies on stochastic gradient descent and its variants, which converge reliably in practice yet lack theoretical guarantees of reaching global minima in polynomial time.

The research covered in this literature map asks a fundamentally different question: *can the non-convex training problem for regularized ReLU networks be rewritten as an equivalent convex program that is globally solvable in polynomial time?* Beginning with a series of papers from Pilanci and Ergen at Stanford (starting ~2020), the answer turns out to be *yes* — at least under weight-decay regularization and for certain architectures. The core insight is that semi-infinite convex duality converts the non-convex minimization over network weights into a convex program over a higher-dimensional feature space indexed by hyperplane arrangement patterns. This convex program is equivalent to a group-sparse linear model and can be solved globally using standard interior-point or ADMM-based methods.

The practical importance of this line of work is threefold. First, it provides exact, polynomial-time algorithms for training two-layer networks when the data rank is bounded. Second, it gives a precise characterization of what the optimal neural network weights look like — they lie at extreme points of a convex set determined by the dual solution. Third, by understanding which architectures admit zero duality gap (and which do not), it yields principled design guidance for choosing architectures that are provably trainable.

By 2024, the framework has been extended to three-layer and arbitrarily deep parallel architectures, approximate polynomial-time algorithms have been developed for the large-rank setting with provable guarantees, and a GPU-accelerated ADMM solver (CRONOS) has scaled the approach to ImageNet-scale data for the first time. The field also maintains productive contact with adjacent areas — neural tangent kernels, implicit regularization, spline theory, and kernel methods — that provide complementary perspectives on why neural networks work.

---

## 2. Foundational Work and Problem Formulation

### The Semi-Infinite Duality Approach for Two-Layer Networks

The founding contribution of this line of research is the paper "Neural Networks are Convex Regularizers: Exact Polynomial-time Convex Optimization Formulations for Two-Layer Networks" by Pilanci & Ergen [Pilanci&Ergen2020]. The paper's central claim: *training a two-layer ReLU network with weight decay is equivalent to solving a finite convex program.*

The primal problem is the standard regularized two-layer training objective

$$p^* := \min_{\{u_j, \alpha_j\}} \frac{1}{2}\left\|\sum_{j=1}^m (Xu_j)_+ \alpha_j - y\right\|_2^2 + \frac{\beta}{2}\sum_{j=1}^m(\|u_j\|_2^2 + \alpha_j^2)$$

where $X \in \mathbb{R}^{n \times d}$ is the data matrix, $y \in \mathbb{R}^n$ is the label vector, and $(t)_+ = \max(t,0)$ is ReLU. The first step is a rescaling equivalence: squared weight-decay is equivalent to $\ell_1$-penalization on the output weights $\alpha_j$ with unit-norm-constrained hidden weights.

The key technical move is to take the Lagrangian dual with respect to the output weights to obtain a semi-infinite dual problem:

$$d^* := \max_{v} -\frac{1}{2}\|y - v\|_2^2 + \frac{1}{2}\|y\|_2^2 \quad \text{s.t.} \quad |v^T(Xu)_+| \le \beta \;\; \forall u \in \mathcal{B}_2$$

This dual is convex in $v$ but has infinitely many constraints (one per unit-norm $u$). The main theorem is that this semi-infinite program can be discretized: the infinite constraint set reduces to constraints indexed by the *hyperplane arrangement* diagonal matrices $D_i = \text{diag}(\mathbf{1}[Xu_i \geq 0])$, of which there are at most $P = O((n/r)^r)$ distinct ones for data of rank $r$ [Pilanci&Ergen2020]. The resulting **finite convex program** is:

$$\min_{\{v_i, w_i\} \in \mathcal{C}} \frac{1}{2}\|\sum_{i=1}^P D_i X(v_i - w_i) - y\|_2^2 + \beta(\|v_i\|_2 + \|w_i\|_2)$$

subject to the polyhedral cones $\mathcal{C} = \{(2D_i - I)Xv_i \geq 0, \; (2D_i - I)Xw_i \leq 0\}$. This has $2dP$ variables and $2nP$ inequality constraints [Pilanci&Ergen2020]. **Strong duality** $p^* = d^*$ holds whenever the network width satisfies $m \geq m^*$ where $m^* \leq n + 1$, proven via Carathéodory's theorem applied to the dual's bi-dual (an infinite-dimensional total-variation minimization problem over Radon measures) [Pilanci&Ergen2020].

The convex program is equivalent to **group-sparse regression** in the high-dimensional feature space $[\tilde{X}_1, \ldots, \tilde{X}_P]$ where $\tilde{X}_i = D_i X$ — a group lasso with group structure indexed by hyperplane arrangement patterns. This reveals that neural network training with weight decay is not fundamentally different from high-dimensional linear regression with a structured sparsity-inducing prior.

A geometric interpretation is provided by the **Neural Gauge Function**: the minimum-norm interpolant equals the gauge function of the convex hull $\text{Conv}(\mathcal{Q}_X \cup -\mathcal{Q}_X)$ where $\mathcal{Q}_X = \{(Xu)_+ : \|u\|_2 \leq 1\}$ is the rectified ellipsoid [Pilanci&Ergen2020]. This geometry characterizes the implicit bias of weight decay regularization.

Computational complexity is $O(d^3 r^3 (n/r)^{3r})$ using standard interior-point methods [Pilanci&Ergen2020], which is polynomial in $n$ for fixed rank $r$, a dramatic improvement over the prior $O(2^m n^{dm})$ brute-force bound.

---

## 3. Theme A: Extending Convex Duality to Deep and Parallel Architectures

### Three-Layer Networks via Parallel Sub-Networks

The two-layer result does not extend directly to deep networks due to the composition of multiple ReLU layers, which produces pathologically non-convex problems. The paper "Global Optimality Beyond Two Layers: Training Deep ReLU Networks via Convex Programs" by Ergen & Pilanci [Ergen&Pilanci2021global] addresses this by considering architectures with $K$ *parallel* three-layer ReLU sub-networks. The key observation is that training this *ensemble* architecture with group-$\ell_1$ regularization has a convex equivalent.

The equivalent convex program for the three-layer sub-network architecture is a group-$\ell_{2,1}$-norm regularized linear model in an expanded feature space indexed by pairs of hyperplane arrangement patterns $(D_{1,i}, D_{2,l})$ — one for each of the two ReLU layers [Ergen&Pilanci2021global]:

$$\min_{\mathbf{w}, \mathbf{w}' \in \mathcal{C}} \frac{1}{2}\|\tilde{X}(\mathbf{w}' - \mathbf{w}) - y\|_2^2 + \beta(\|\mathbf{w}\|_{2,1} + \|\mathbf{w}'\|_{2,1})$$

where $\tilde{X}_s = [D_{2,1} D_{1,11} X \;\cdots\; D_{2,P_2} D_{1,P_1 m_1} X]$ involves *products* of two diagonal matrices. This represents a key architectural difference from the two-layer case: two-layer networks embed data via $D_i X$, while three-layer networks embed via $D_{2,l} D_{1,ij} X$ — a higher-order feature map that captures the composition of two ReLU stages [Ergen&Pilanci2021global].

Strong duality $P^* = P_B^* = D^*$ is again proven via Carathéodory's theorem applied to a total-variation minimization problem over Radon measures, and holds when the number of sub-networks satisfies $K \geq K^*$ where $K^* \leq n + 1$ [Ergen&Pilanci2021global]. This provides the polynomial-time trainability of regularized multi-sub-network architectures. ResNets appear as a special case: with $K=2$, $\mathbf{W}_{12} = \mathbf{W}_{22} = \mathbf{I}_d$, the architecture reduces to a standard residual block [Ergen&Pilanci2021global]. An implicit regularization interpretation follows: the group-$\ell_1$ norm encourages sparsity, meaning the optimal solution uses far fewer sub-networks than the maximum available — the optimal $K$ satisfies $K^* \leq n+1$ [Ergen&Pilanci2021global].

### The Duality Gap Problem for Standard Deep Networks

A critical question is whether strong duality holds for *standard* (non-parallel) networks with three or more layers. "Parallel Deep Neural Networks Have Zero Duality Gap" by Wang, Ergen & Pilanci [Wang&Ergen&Pilanci2023] provides a definitive answer via a complete taxonomy of duality gaps:

**Standard deep linear networks** with $L \geq 3$ layers have a *non-zero* duality gap whenever the singular values of $X^\dagger Y$ are not all equal [Wang&Ergen&Pilanci2023]. Specifically, $P_\text{lin}(t) = t^{-(L-2)}\|X^\dagger Y\|_{S_{2/L}}$ while $D_\text{lin}(t) = t^{-(L-2)}\|X^\dagger Y\|_*$, and $P = D$ if and only if the Schatten-$2/L$ quasi-norm equals the nuclear norm, which holds only for matrices with equal singular values. This is the first explicit calculation of the duality gap for deep networks and establishes that depth generically creates non-zero duality gap.

**Parallel deep ReLU networks** at *any depth $L$* have zero duality gap with appropriate convex regularization and sufficiently many branches [Wang&Ergen&Pilanci2023]. The proof shows that the bi-dual of a standard deep network's minimum-norm problem equals the minimum-norm problem of a parallel network — a deep structural connection. **Table 1** in [Wang&Ergen&Pilanci2023] provides the complete taxonomy: both linear and ReLU networks with $L=2$ always have zero gap; standard networks with $L \geq 3$ have non-zero gap; parallel networks at any depth have zero gap.

An additional insight comes from the deep linear case: $\ell_2$-regularization implicitly forces low-rank solutions, and this bias strengthens with depth. The optimal standard deep linear network has closed-form weights $W_l = U_{l-1} \Sigma^{1/L} U_l^T$ where the factorization is via the SVD of $X^\dagger Y$ [Wang&Ergen&Pilanci2023]. The optimal value is $\frac{L}{2}\|W\|_{S_{2/L}}^{2/L}$ — the Schatten-$2/L$ quasi-norm — which interpolates between nuclear norm ($L=2$) and spectral norm ($L \to \infty$), showing mathematically how depth amplifies low-rank implicit regularization.

---

## 4. Theme B: Structural Insights via Duality

### Optimal Weights as Extreme Points of a Convex Set

"Revealing the Structure of Deep Neural Networks via Convex Duality" [Ergen&Pilanci2021reveal] uses the dual optimality conditions to characterize *what* the optimal hidden layer weights look like. The main result is:

**Theorem:** The optimal hidden layer weights of a regularized deep ReLU network are the *extreme points* of a convex set determined by the dual solution [Ergen&Pilanci2021reveal].

This is a stronger statement than strong duality — it says that once the dual problem is solved, the primal solution's structure is completely determined. The dual variables identify the active constraints, and the active constraint hyperplane arrangements give the optimal weight vectors. For deep linear networks and deep ReLU networks with whitened or rank-1 data, the optimal weights are given in closed form:

$$\mathbf{W}_l^* = U_{l-1} \Sigma^{1/L} U_l^T, \quad l \in [L]$$

where $U_0, U_L$ come from the SVD of the data, and $U_1, \ldots, U_{L-1}$ can be arbitrary orthonormal matrices [Wang&Ergen&Pilanci2023, Ergen&Pilanci2021reveal].

**Weight alignment**: Duality proves that optimal weight matrices align with the previous layer's weights — the singular vectors are shared across layers in a predictable way [Ergen&Pilanci2021reveal]. This is an exact algebraic consequence of dual optimality conditions, not just an empirical observation.

### Spline Interpolation as the Deep ReLU Solution

For one-dimensional or rank-1 data, the optimal solution to a deep ReLU network (any depth $L \geq 2$) with squared loss and weight decay is the *linear spline interpolator* [Ergen&Pilanci2021reveal]. This extends earlier two-layer results from Savarese et al. and Parhi & Nowak to all depths, resolving a longstanding question about whether depth changes the function class of the optimal solution for 1D data. The answer (for rank-1 data) is no: optimal functions are always piecewise linear, regardless of depth [Ergen&Pilanci2021reveal].

### Batch Normalization, Neural Collapse, and Arbitrary Data

A limitation of several results in [Ergen&Pilanci2021reveal] is that they require whitened or rank-1 data to obtain closed-form solutions. The paper shows that **batch normalization** eliminates this restriction: applying batch normalization before the final layer effectively whitens the intermediate representations, making the exact weight characterization hold for arbitrary data. This provides a theoretical explanation for batch normalization's empirical effectiveness.

A striking corollary is an explanation of **neural collapse** [Ergen&Pilanci2021reveal]: when batch normalization and weight decay are applied, the class means collapse to a *simplex equiangular tight frame* (ETF) at convergence. This geometric structure — the most spread-out configuration of $K$ points in $K-1$ dimensions — follows from the interaction between batch normalization's whitening effect and norm regularization's sparsity-inducing behavior, as characterized by the convex dual program.

### Implicit Regularization as Group Sparsity

A consistent theme across [Pilanci&Ergen2020], [Ergen&Pilanci2021global], and [Ergen&Pilanci2021reveal] is that weight decay's *effective* regularization in the convex-equivalent problem is group sparsity. In the two-layer case, the group-$\ell_1$ norm in the convex program penalizes groups of features $(D_i X)$ not selected by the optimizer. In the three-layer case, the group-$\ell_{2,1}$ norm penalizes unused sub-networks. This means weight decay — a simple isotropic prior over parameters — implicitly induces structured sparsity in the feature space, selecting a minimal parsimonious set of hyperplane arrangement patterns [Ergen&Pilanci2021global]. The connection between weight decay in parameter space and group-lasso in feature space is an exact equivalence, not an approximation [Pilanci&Ergen2020].

---

## 5. Theme C: Computational Tractability and Scalability

### The Intractability Barrier and Polynomial Approximations

The exact convex reformulation of [Pilanci&Ergen2020] has $O((n/r)^r)$ variables — exponential in the data rank $r$, which is typically $d$ for full-rank data. For small rank problems this is fine, but for general data it is computationally intractable. Two approaches address this.

The first, suggested in [Pilanci&Ergen2020] and formalized in [Kim&Pilanci2024], is **Gaussian random subsampling**: instead of enumerating all $P$ hyperplane arrangements, sample $\tilde{P} \ll (n/r)^r$ patterns from random Gaussian vectors $g_i \sim \mathcal{N}(0, I_d)$ and solve the smaller convex program. "Convex Relaxations of ReLU Neural Networks Approximate Global Optima in Polynomial Time" [Kim&Pilanci2024] provides the first theoretical guarantee for this relaxation:

**Theorem 1 (informal):** Under Gaussian data (A1) and with $m = \kappa \max\{m^*, O(\log n)\}$ sampled patterns, the relative optimality gap is bounded as $p^* \leq \tilde{p}^* \leq C\sqrt{\log 2n} \cdot p^*$ with high probability [Kim&Pilanci2024].

This is the first polynomial-time approximation guarantee for regularized ReLU networks. The dependence on $\log n$ is essentially tight given the hardness result that without regularization, training is NP-Hard [Kim&Pilanci2024, citing Boob et al. 2022]. The proof uses Gordon's comparison inequality from random matrix theory to bound the effective number of distinct hyperplane patterns needed.

A related result (Theorem 2.5 in [Kim&Pilanci2024]) uses a **coupling lemma** from the SGD convergence literature: stationary points of SGD with random initialization preserve the hyperplane arrangement patterns from initialization, meaning each stationary point corresponds to a global minimum of the Gaussian-relaxed convex problem. Therefore, *SGD with random initialization achieves $O(\sqrt{\log n})$ relative training error with respect to the true global minimum* [Kim&Pilanci2024].

### CRONOS: ADMM with Nyström Preconditioning at GPU Scale

The theoretical convex reformulation remained impractical at scale until "CRONOS" [Feng&Frangella&Pilanci2023]. The paper reformulates the convex program of [Pilanci&Ergen2020] as a **linearly constrained generalized linear model with group lasso** (Proposition 3.1), then solves it using the **Alternating Direction Method of Multipliers (ADMM)**.

The algorithmic novelty is **Nyström Preconditioning**: the CG (conjugate gradient) sub-solver within ADMM normally requires $O(\kappa)$ iterations where $\kappa$ is the condition number. Nyström preconditioning, which approximates the dominant part of the data kernel matrix, reduces this to $O(\log(1/\delta))$ iterations independent of condition number [Feng&Frangella&Pilanci2023]. This is crucial for large $n,d$ where condition numbers can be enormous.

Implementation uses JAX + JIT compilation on a single RTX-4090 GPU, achieving the first successful application of the convex neural network training framework to ImageNet-scale data (images of size $512 \times 512 \times 3$) and IMDb text classification [Feng&Frangella&Pilanci2023]. This is an order-of-magnitude scale improvement over prior experiments with convex NN formulations.

For deeper networks, **CRONOS-AM** (alternating minimization) handles arbitrary-depth $L$-layer networks by alternating between: (i) applying CRONOS to the last two layers (which admits the convex reformulation), and (ii) applying DAdapted-Adam to the earlier, non-convexly structured layers. CRONOS-AM converges to the global minimum of the convex sub-problem under mild assumptions and achieves comparable or better validation accuracy than tuned SGD/Adam baselines on ImageNet and IMDb [Feng&Frangella&Pilanci2023].

---

## 6. Contested Areas and Open Debates

### Zero vs. Non-Zero Duality Gap: Architecture Matters

The clearest contested area revealed by this literature is the question of which architectures admit zero duality gap. [Wang&Ergen&Pilanci2023] explicitly proved that standard deep linear networks have non-zero gap for $L \geq 3$, while parallel architectures at any depth have zero gap. The paper stops short of a complete characterization of exactly which standard ReLU architectures have non-zero gap — the ReLU case for $L \geq 3$ is marked as not proven in [Wang&Ergen&Pilanci2023]'s Table 1. This remains an open question.

### The Role of Rank Assumptions

The exact convex reformulation of [Pilanci&Ergen2020] and the closed-form structural results of [Ergen&Pilanci2021reveal] both require bounded data rank $r$ for polynomial complexity. The results of [Kim&Pilanci2024] relax this slightly — under Gaussian data with $n \asymp d$, the approximation guarantee $O(\sqrt{\log n})$ holds, but extending this to deterministic data with general rank without paying an exponential price remains open. The assumption (A1) (Gaussian i.i.d. data) in [Kim&Pilanci2024] is noted as potentially extendable to distributions satisfying restricted isometry property (RIP), but no such extension is proven in the paper.

### NTK / Overparameterization View vs. Convex Duality View

The neural tangent kernel (NTK) literature [Jacot et al. 2018, discussed in Lilianweng2022] provides an alternative explanation for neural network training: in the infinite-width limit, gradient dynamics become linear and the network stays close to its initialization (lazy training). The convex duality view [Pilanci&Ergen2020] explicitly contrasts with this, arguing that "the kernel approximation as the width tends to infinity is unable to fully explain the success of non-convex neural network models" and that "our work precisely characterizes the mechanism behind extraordinary modeling capabilities of neural networks for *any finite number of hidden neurons*" [Pilanci&Ergen2020]. These two frameworks make different predictions: NTK implies lazy training and no feature learning, while the convex duality view predicts non-trivial feature selection (sparse hyperplane arrangement support). Which regime is active in practice for modern large networks is an active, unresolved debate.

[Ergen&Pilanci2021global] directly cites recent work showing that as the number of sub-networks increases, the loss landscape becomes progressively more convex (Figure 2 in that paper), providing experimental evidence that the convex duality framework is predictive even at practical finite widths — in contrast to the infinite-width NTK regime.

### Practical Significance of Batch Normalization's Effect

[Ergen&Pilanci2021reveal] shows theoretically that batch normalization removes the whitened/rank-1 data requirement from the structural results. However, the interaction between batch normalization and the convex reformulation is not fully worked out for the multi-layer case. The paper proves the neural collapse corollary for the last linear layer with BN, but whether the full convex duality framework extends seamlessly to architectures with batch normalization at every layer remains partially open.

---

## 7. Methodological Landscape

**Theoretical methodology:** All papers in this literature use **semi-infinite duality** as the primary tool. The recipe is: (1) reformulate the non-convex primal training problem in $\ell_1$-penalty form via Lemma 1 (rescaling); (2) dualize with respect to the output weights to obtain a semi-infinite dual; (3) characterize the dual constraints via hyperplane arrangement diagonal matrices; (4) apply Carathéodory's theorem to the Radon-measure bi-dual to establish strong duality; (5) extract the primal convex equivalent from the dual characterization. This recipe appears across [Pilanci&Ergen2020], [Ergen&Pilanci2021global], [Wang&Ergen&Pilanci2023], and [Ergen&Pilanci2021reveal] with varying levels of generalization.

**Experimental benchmarks:** Papers in this literature use: (a) synthetic datasets (random Gaussian data, small $n$) for landscape experiments [Ergen&Pilanci2021global]; (b) MNIST for small-scale exact convex solver validation [Kim&Pilanci2024]; (c) CIFAR-10/100 for medium-scale comparisons [Feng&Frangella&Pilanci2023]; (d) ImageNet (512×512×3) and IMDb as the largest-scale benchmarks [Feng&Frangella&Pilanci2023].

**Metrics:** Training loss convergence to global minimum is the primary metric. Validation accuracy comparisons against SGD and Adam baselines are used in [Feng&Frangella&Pilanci2023]. Relative optimality gap $(\tilde{p}^* - p^*)/p^*$ is the theoretical metric in [Kim&Pilanci2024].

**Solvers used:** Interior-point solvers via CVXPY for small-scale experiments; ADMM with Nyström preconditioning (CRONOS) for large-scale experiments [Feng&Frangella&Pilanci2023]; DAdapted-Adam for the non-convex early layers in CRONOS-AM [Feng&Frangella&Pilanci2023].

**Assumptions across the literature:** Weight decay regularization is universal. Most exact results require either (a) bounded data rank $r$ or (b) Gaussian/whitened data. Parallel architectures (rather than standard sequential) are required for zero duality gap at depth $\geq 3$.

---

## 8. Research Timeline

**Prior work (~2017–2019):** The infinite-width regime was well understood via neural tangent kernels [Jacot et al. 2018]. Convex arguments in the overparameterized neural network literature [Bach 2017; Bengio et al. 2006] were restricted to infinite-width networks with intractable infinite-dimensional optimization. Gradient descent global convergence in the overparameterized regime was proven under NTK assumptions [Du et al. 2019]. Implicit regularization in matrix factorization (a linear analogue) was studied by Gunasekar et al. (arxiv-1710.10174 listed in manifest), establishing that gradient descent on matrix factorization implicitly minimizes nuclear norm.

**2020 — Foundational papers:** Pilanci & Ergen publish the core two-layer convex reformulation [Pilanci&Ergen2020], introducing semi-infinite duality and hyperplane arrangements as the central technical language. This is the inflection point of the field.

**2021 — Deep and structural extensions:** Ergen & Pilanci extend to three-layer sub-networks [Ergen&Pilanci2021global] and publish the structural characterization of optimal weights [Ergen&Pilanci2021reveal]. Extensions to CNNs, vector outputs, and batch normalization appear in companion papers cited in [Ergen&Pilanci2021global].

**2022–2023 — Duality gap characterization and warm reception:** Wang, Ergen & Pilanci publish [Wang&Ergen&Pilanci2023] at ICLR 2023, providing the first systematic taxonomy of duality gaps and proving that parallel architectures have zero gap at any depth. This paper resolves a key question about the depth barrier for convex equivalents.

**2023 — Scalable solvers:** CRONOS [Feng&Frangella&Pilanci2023] demonstrates for the first time that convex NN training can scale to ImageNet, closing the remaining important practical gap.

**2024 — Polynomial approximation guarantees:** Kim & Pilanci publish [Kim&Pilanci2024] at ICML 2024, establishing $O(\sqrt{\log n})$ optimality gaps for the Gaussian relaxation and connecting SGD convergence to the convex framework.

---

## 9. Key Papers Summary

**[Pilanci&Ergen2020]** — "Neural Networks are Convex Regularizers: Exact Polynomial-time Convex Optimization Formulations for Two-Layer Networks" (Pilanci & Ergen). The founding paper. Proves that two-layer ReLU training with weight decay equals a finite group-sparse convex program parameterized by hyperplane arrangement matrices $D_i$. Establishes strong duality via Carathéodory theorem; complexity $O(d^3r^3(n/r)^{3r})$ for data rank $r$.

**[Ergen&Pilanci2021global]** — "Global Optimality Beyond Two Layers: Training Deep ReLU Networks via Convex Programs" (Ergen & Pilanci). Extends the convex reformulation to $K$ parallel three-layer ReLU sub-networks. Proves strong duality $P^* = P_B^* = D^*$ via Carathéodory; implicit regularization is group $\ell_1$-norm; ResNets are a special case ($K=2$). Loss landscape becomes more convex as $K$ increases (Figure 2 experiment).

**[Wang&Ergen&Pilanci2023]** — "Parallel Deep Neural Networks Have Zero Duality Gap" (Wang, Ergen & Pilanci; ICLR 2023). Proves standard deep networks ($L \geq 3$) have *non-zero* duality gap. Proves parallel architectures at any depth have zero duality gap. Provides Table 1 systematic taxonomy for linear/ReLU, standard/parallel, $L = 2/3/>3$. Shows deep linear optimal value is Schatten-$2/L$ quasi-norm; closed-form solution via SVD factorization.

**[Ergen&Pilanci2021reveal]** — "Revealing the Structure of Deep Neural Networks via Convex Duality" (Ergen & Pilanci). Characterizes optimal hidden weights as extreme points of a convex set. Proves weight alignment via duality. Establishes spline interpolation for rank-1/1D data at any depth. Explains neural collapse via BN + weight decay = simplex ETF class means.

**[Feng&Frangella&Pilanci2023]** — "CRONOS: Enhancing Deep Learning with Scalable GPU Accelerated Convex Neural Networks" (Feng, Frangella & Pilanci). Introduces ADMM solver with Nyström preconditioning; eliminates condition number dependence. First convex NN solver to scale to ImageNet and IMDb. CRONOS-AM handles arbitrary deep networks via alternating minimization.

**[Kim&Pilanci2024]** — "Convex Relaxations of ReLU Neural Networks Approximate Global Optima in Polynomial Time" (Kim & Pilanci; ICML 2024). Proves $O(\sqrt{\log n})$ relative optimality gap for Gaussian-sampled hyperplane arrangements under Gaussian data (A1). First polynomial-time approximation guarantee for regularized ReLU networks. Coupling lemma implies SGD stationary points have $O(\sqrt{\log n})$ relative training error.

**[Lilianweng2022]** — "Some Math behind Neural Tangent Kernel" (Lilian Weng blog, 2022). Accessible exposition of NTK theory [Jacot et al. 2018]: infinite-width limit, deterministic NTK, lazy training regime. Contextualizes the contrast with the convex duality approach by explaining the NTK perspective's strength (guaranteed convergence in infinite-width limit) and weakness (lazy training does not capture feature learning at finite width).
