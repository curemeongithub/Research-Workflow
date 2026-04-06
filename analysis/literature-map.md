---
phase: 3
status: complete
timestamp: 2026-04-07T12:00:00Z
depends_on: [sources/manifest.yaml]
token_estimate: 5200
---

# Literature Map: Duality Gap in Dual Convex Optimization in ReLU Neural Networks

## 1. Overview of the Field

This research area investigates a surprising connection between the highly non-convex optimization problems arising in neural network training and equivalent convex optimization programs. The central question is: can the training of ReLU neural networks, which is NP-hard in general [PilanciErgen2020], be reformulated as a tractable convex program, and under what conditions does this reformulation preserve global optimality (zero duality gap)?

The field was catalyzed by Pilanci and Ergen's 2020 discovery that two-layer ReLU networks with weight decay are equivalent to group $\ell_1$-regularized convex programs in a lifted variable space [PilanciErgen2020]. This foundational insight spawned a research program -- almost entirely centered at Stanford University's Pilanci Lab -- that has extended convex reformulations to CNNs [ErgenPilanci2020CNN], vector-output networks [Sahiner2020], deep networks [ErgenPilanci2021Deep, WangErgenPilanci2021], networks with batch normalization [Ergen2021BN], polynomial activations [BartanPilanci2021], and networks trained on low-dimensional data [Zeger2024]. The practical gap between theoretical tractability and computational scalability has also been a major focus, with dedicated algorithmic work on fast solvers [Mishkin2022SCNN, Feng2023CRONOS] and approximation guarantees [Kim2024].

The only paper in our corpus from outside the Pilanci group is Gagneux et al. (2025) [Gagneux2025], which studies a related but distinct question about convexity of the functions implemented by ReLU networks (input convexity), rather than convexity of the training problem itself.

## 2. Foundational Work and Problem Formulation

The foundational paper of this entire line of research is [PilanciErgen2020], which establishes that training a two-layer ReLU network with $m$ neurons, squared loss, and weight decay regularization:

$$p^{*} = \min_{\{u_j, \alpha_j\}} \frac{1}{2} \left\|\sum_{j=1}^{m} (Xu_j)_+ \alpha_j - y\right\|_2^2 + \frac{\beta}{2}\sum_{j=1}^{m}(\|u_j\|_2^2 + \alpha_j^2)$$

can be exactly reformulated as a finite-dimensional convex program. The key mechanism is a three-step procedure: (1) rescaling to convert weight decay into $\ell_1$ penalty on output weights, (2) taking the convex dual with respect to output weights, and (3) exploiting semi-infinite duality to convert the resulting semi-infinite program into a finite program over hyperplane arrangement patterns $D_1, \ldots, D_P$ [PilanciErgen2020]. The resulting convex program is a second-order cone program (SOCP) with $2dP$ variables and $2nP$ constraints, where $P \leq 2r(e(n-1)/r)^r$ and $r = \text{rank}(X)$. Strong duality ($p^* = d^*$) holds when $m \geq m^*$ for some $m^* \leq n+1$ [PilanciErgen2020].

A geometric interpretation accompanies this result: in the minimum-norm interpolation limit ($\beta \to 0$), the problem reduces to evaluating the gauge function of a "Neural Gauge" -- the convex hull of a rectified ellipsoidal set $\mathcal{Q}_X = \{(Xu)_+ : u \in \mathcal{B}_2\}$ [PilanciErgen2020]. This connects neural network optimization to classical convex geometry via polar gauge duality.

Simultaneously, Ergen and Pilanci developed a complementary geometric perspective in [ErgenPilanci2020Geom], showing that optimal hidden layer weights for overparameterized ReLU networks are extreme points of a convex set called the "rectified ellipsoid." This work established that ReLU networks with minimum $\ell_2$ norm on 1-D data produce linear spline interpolation, and proposed cutting-plane algorithms for globally optimizing networks in higher dimensions.

The problem of understanding the structure of optimal deep network weights was further developed in [ErgenPilanci2021Structure] (arXiv 2002.09773, ICML 2021 version user-ergen21b), which introduced a convex analytic framework showing that optimal hidden layer weights can be found as extreme points of a convex set, and that weight matrices of consecutive layers align via duality. For deep ReLU networks with whitened data, closed-form solutions for optimal layer weights were obtained, and the spline interpolation result was extended to arbitrary depth [ErgenPilanci2021Structure].

## 3. Theme A: Strong Duality and the Duality Gap -- When Is It Zero?

The central theoretical question in this corpus is: under what conditions does strong duality ($P^* = D^*$) hold, and when does a non-zero duality gap arise?

**Two-layer networks: zero duality gap.** The foundational result is that two-layer ReLU networks always have zero duality gap when $m \geq m^*$, for both scalar and vector outputs [PilanciErgen2020, Sahiner2020, WangLacottePilanci2020]. This was proven using semi-infinite duality and Caratheodory's theorem, which bounds $m^* \leq n+1$ [PilanciErgen2020].

**Deep standard networks: non-zero duality gap.** A pivotal finding by Wang, Ergen, and Pilanci [WangErgenPilanci2021] demonstrates that for standard (non-parallel) deep networks with three or more layers and vector outputs, the duality gap is non-zero. They precisely calculate the optimal primal and dual values for deep linear networks and show $P > D$ when $L \geq 3$ for standard architectures. Their Table 1 provides a comprehensive taxonomy: for standard linear networks, the duality gap is zero only when $L = 2$; for $L \geq 3$, it is provably non-zero [WangErgenPilanci2021].

**Parallel architectures: zero duality gap at any depth.** The key architectural insight is that stacking networks in parallel (multi-branch architectures) recovers zero duality gap. Wang et al. prove that for parallel deep ReLU networks of arbitrary depth $L$, with sufficient branches and appropriate regularization, strong duality holds: $P = D$ [WangErgenPilanci2021]. This result is published at ICLR 2023. The parallel architecture subsumes practical models like ResNets, Inception, and SqueezeNet [WangErgenPilanci2021, ErgenPilanci2021Deep].

**Three-layer standard ReLU networks.** Ergen and Pilanci extend convex duality to architectures with multiple three-layer ReLU sub-networks [ErgenPilanci2021Deep]. They prove that for these architectures with sufficiently many sub-networks $K$, the training problem is equivalent to a convex program solvable in polynomial time, with group $\ell_1$-norm regularization enforcing sparsity. This effectively treats three-layer networks as parallel compositions, recovering strong duality through the sub-network structure.

**Path regularization and deep parallel networks.** Ergen and Pilanci [ErgenPilanci2023Path] (NeurIPS 2023) show that pathwise regularized training of deep parallel ReLU networks can be represented as an exact convex optimization problem. The equivalent convex problem uses a group sparsity-inducing norm. They provide a fully polynomial-time approximation scheme with global optimality guarantees when the exact convex program is intractable.

**Special data conditions.** Strong duality for deep ReLU networks (not just parallel) holds under data restrictions. Ergen and Pilanci prove strong duality for three-layer standard ReLU networks given rank-1 data matrices [WangErgenPilanci2021]. For whitened data or data with batch normalization, the deep network training problem admits equivalent convex formulations [ErgenPilanci2021Structure, Ergen2021BN].

## 4. Theme B: Extensions to Diverse Architectures and Activation Functions

A major thrust of this research program is extending the convex reformulation framework beyond the canonical two-layer fully-connected ReLU network.

**Convolutional Neural Networks (CNNs).** Ergen and Pilanci [ErgenPilanci2020CNN] (ICLR 2021) prove that two- and three-layer CNNs with ReLU activations can be globally optimized via convex programs in polynomial time. A remarkable finding is that different CNN architectures -- varying in pooling methods (average pooling, max pooling, flattening) and connection structures -- correspond to different implicit convex regularizers, ranging from $\ell_1$ and $\ell_2$ norms to nuclear norm [ErgenPilanci2020CNN]. The computational complexity is polynomial in $n$, $d$, and $m$ with complexity $O(h^3 r_c^3 (nK/r_c)^{3r_c})$ for two-layer CNNs where $h$ is the filter size [ErgenPilanci2020CNN].

**Vector-output networks.** Sahiner et al. [Sahiner2020] extend the scalar-output formulation to vector-output ReLU networks ($f: \mathbb{R}^d \to \mathbb{R}^c$) and discover that the convex reformulation requires optimizing over the convex hull of completely positive matrices, establishing a novel connection to copositive programming. The resulting algorithm is polynomial-time for fixed data rank but exponential in $d$ in the worst case, which is unavoidable unless $\mathcal{P} = \mathcal{NP}$ [Sahiner2020]. Under certain conditions on data and labels, optimal weights have closed-form expressions via soft-thresholded SVD.

**Batch normalization.** Ergen et al. [Ergen2021BN] analyze ReLU networks with batch normalization (BN) through convex duality and show that BN effectively whitens the data in the equivalent convex formulation. They obtain closed-form solutions for optimal weights in high-dimensional and overparameterized regimes, and reveal that gradient descent on BN networks induces an implicit regularization that learns high singular-value directions more aggressively.

**Polynomial activations.** Bartan and Pilanci [BartanPilanci2021] develop convex formulations for two-layer networks with second-degree polynomial activations via semidefinite programming. A key finding is that the choice of regularizer determines tractability: standard weight decay is NP-hard, but cubic regularization or unit-norm constraints on first-layer weights render the problem polynomial-time solvable. The semidefinite lifting is proven to always be exact [BartanPilanci2021].

**Piecewise linear activations and Lasso equivalence.** Ergen and Pilanci [ErgenPilanci2023Lasso] provide a comprehensive treatment covering all piecewise linear activations (ReLU, leaky ReLU, absolute value), establishing that two-layer networks with these activations are equivalent to group Lasso models. They prove that all stationary points of the non-convex training objective correspond to global optima of subsampled convex programs [ErgenPilanci2023Lasso].

## 5. Theme C: Scalable Algorithms and Practical Training

While theoretical convex equivalence is established for polynomial complexity when data rank is bounded, the exponential dependence on rank ($O(n^r)$) makes exact convex training intractable for high-dimensional data. This theme addresses the scalability gap.

**Fast convex solvers (SCNN).** Mishkin, Sahiner, and Pilanci [Mishkin2022SCNN] (ICML 2022) develop practical algorithms for two-layer convex ReLU networks. Their key insight is that the unregularized problem is equivalent to an unconstrained "gated ReLU" model, which is a standard group-$\ell_1$ regularized GLM. They develop an accelerated proximal gradient method improving iteration complexity from $O(1/\epsilon^2)$ to $O(1/\sqrt{\epsilon})$, and an augmented Lagrangian solver that outperforms commercial interior-point solvers like MOSEK. They scale convex training to MNIST and CIFAR-10 [Mishkin2022SCNN].

**CRONOS: GPU-accelerated convex training.** Feng, Frangella, and Pilanci [Feng2023CRONOS] introduce CRONOS, an ADMM-based algorithm implemented in JAX with GPU acceleration. CRONOS is the first convex neural network solver to scale to high-dimensional datasets such as ImageNet, a significant advance over prior work restricted to downsampled MNIST/CIFAR-10. They extend the approach to multi-layer networks via CRONOS-AM (alternating minimization), demonstrating comparable or better validation accuracy than tuned SGD and Adam on vision and language tasks including GPT-2 fine-tuning [Feng2023CRONOS].

**Approximation guarantees for relaxations.** Kim and Pilanci [Kim2024] prove that Gaussian random relaxations of the exact convex reformulation achieve a relative optimality gap bounded by $O(\sqrt{\log n})$ under Gaussian data assumptions. This implies a tractable polynomial-time algorithm that approximates the global optimum within a logarithmic factor, and that local gradient methods converge to points with low training loss with high probability [Kim2024].

**Solution structure and regularization paths.** Mishkin and Pilanci [Mishkin2023Optimal] characterize the complete set of optimal ReLU networks as a polyhedral set in convex parameter space, develop optimal pruning algorithms for minimal networks, and study regularization path continuity -- showing the path is discontinuous in general but establishing sufficient conditions for continuity. This work bridges the classical statistical understanding of Lasso solution paths to neural network training.

## 6. Contested Areas and Open Debates

**Duality gap for standard deep ReLU networks.** While strong duality is proven for two-layer networks and parallel deep networks, the status for standard deep ReLU networks beyond three layers with general data remains unresolved. Wang et al. prove the duality gap is non-zero for deep standard linear networks with vector outputs [WangErgenPilanci2021], but the ReLU case beyond rank-1 data and three layers is marked with "X" (unknown) in their Table 1, indicating open questions about the precise boundary between zero and non-zero gap [WangErgenPilanci2021].

**Practical relevance of convex formulations.** A tension exists between the theoretical elegance of convex reformulations and their practical scalability. Early work was confined to tiny datasets [Mishkin2022SCNN]. CRONOS [Feng2023CRONOS] addresses ImageNet-scale data, but relies on alternating minimization for multi-layer networks, which loses the global optimality guarantee of the pure convex formulation. Whether convex approaches can compete with highly optimized SGD pipelines at truly large scale remains contested.

**Role of the activation function.** Bartan and Pilanci [BartanPilanci2021] show that with polynomial activations and standard weight decay, the problem is NP-hard, while a simple change to cubic regularization makes it tractable. This highlights that the convex landscape depends not just on the activation but also on the regularizer, complicating the narrative that neural networks are "secretly convex."

**Expressivity of convex networks vs. ICNNs.** Gagneux et al. [Gagneux2025] address a distinct but related question: whether Input Convex Neural Networks (ICNNs) cover all convex functions implementable by a given architecture. They prove that for one hidden layer, ICNNs suffice, but for two or more hidden layers, there exist convex ReLU functions outside the ICNN class. This result about function-level convexity is orthogonal to the training-problem convexity studied by the Pilanci group.

## 7. Methodological Landscape

**Theoretical tools.** The dominant technical apparatus is semi-infinite duality combined with Caratheodory's theorem to convert infinite-dimensional programs into finite-dimensional ones [PilanciErgen2020]. The rescaling lemma converting $\ell_2^2$ weight decay to $\ell_1$ penalties on output weights is a recurring ingredient across most papers [PilanciErgen2020, ErgenPilanci2021Deep, ErgenPilanci2021Structure].

**Benchmarks.** Experiments range from synthetic data (spiral classification, 1-D regression) to standard benchmarks: MNIST, CIFAR-10, and in the case of CRONOS, ImageNet and IMDb [Feng2023CRONOS]. A common experimental paradigm compares convex solvers against SGD/Adam on the non-convex formulation, showing that SGD sometimes converges to suboptimal stationary points while convex methods find the global optimum [PilanciErgen2020, BartanPilanci2021, Mishkin2022SCNN].

**Metrics.** Training loss (verifying global optimality), test accuracy, number of active neurons (sparsity), and duality gap are the primary metrics. Kim and Pilanci [Kim2024] introduce the relative optimality gap $p^*/\tilde{p}^*$ as a metric for relaxation quality.

**Software.** The primary codebases are scnn [Mishkin2022SCNN] for two-layer convex networks, relu_optimal_sets [Mishkin2023Optimal] for solution characterization, convex_nn [ErgenPilanci2023Lasso] for general convex neural networks, and CRONOS [Feng2023CRONOS] for GPU-accelerated training.

## 8. Research Timeline

**2020: Foundation.** Pilanci and Ergen [PilanciErgen2020] and Ergen and Pilanci [ErgenPilanci2020Geom, ErgenPilanci2021Structure] establish the convex duality framework for two-layer ReLU networks, proving strong duality and polynomial-time trainability for bounded-rank data. The CNN extension [ErgenPilanci2020CNN] and hidden convex landscape characterization [WangLacottePilanci2020] appear in the same period. The vector-output extension to copositive programming [Sahiner2020] broadens the scope.

**2021: Depth and architectural extensions.** Ergen and Pilanci extend to deep (three-layer) networks [ErgenPilanci2021Deep], batch normalization [Ergen2021BN], and polynomial activations [BartanPilanci2021]. The structure of optimal weights for deep networks is characterized [ErgenPilanci2021Structure]. Wang et al. prove the critical result that parallel architectures have zero duality gap at any depth, while standard deep networks may not [WangErgenPilanci2021].

**2022-2023: Practical algorithms and deeper theory.** Mishkin et al. develop the first fast convex solvers scaling to MNIST/CIFAR-10 [Mishkin2022SCNN]. Path regularization provides convex reformulations for deep parallel networks [ErgenPilanci2023Path]. The NTK connection is established [Dwaraknath2023], and the comprehensive Lasso characterization appears [ErgenPilanci2023Lasso]. Mishkin and Pilanci characterize optimal sets and solution paths [Mishkin2023Optimal]. CRONOS achieves ImageNet scale [Feng2023CRONOS].

**2024-2025: Approximation theory and broader connections.** Kim and Pilanci provide polynomial-time approximation guarantees [Kim2024]. Zeger et al. extend the Lasso perspective to deep networks on 1-D data with reflection features [Zeger2024]. Gagneux et al. bring a different community's perspective on convexity in ReLU networks [Gagneux2025].

## 9. Key Papers Summary

- **[PilanciErgen2020]** (arxiv-2002.10553): Foundational paper proving two-layer ReLU networks are equivalent to convex group-$\ell_1$ regularized programs; introduced the Neural Gauge geometric framework and semi-infinite duality approach.
- **[ErgenPilanci2021Deep]** (arxiv-2110.05518): Extends convex duality to architectures with multiple three-layer ReLU sub-networks, proving polynomial-time trainability via convex programs with group $\ell_1$-norm regularization.
- **[WangErgenPilanci2021]** (arxiv-2110.06482): Proves the duality gap is non-zero for standard deep vector-output linear networks ($L \geq 3$), but zero for parallel architectures of any depth with ReLU or linear activations. Published at ICLR 2023.
- **[Kim2024]** (arxiv-2402.03625): Shows that randomized convex relaxations approximate the global optimum within $O(\sqrt{\log n})$ factor under Gaussian data, yielding a tractable polynomial-time algorithm. ICML 2024.
- **[Feng2023CRONOS]** (user-8652-CRONOS): Introduces CRONOS, the first GPU-accelerated convex neural network solver scaling to ImageNet, using ADMM in JAX with alternating minimization for multi-layer networks.
- **[ErgenPilanci2021Structure]** (user-ergen21b / arxiv-2002.09773): Characterizes optimal DNN weights as extreme points of a convex set; proves weight alignment across layers for deep ReLU networks with whitened data; explains Neural Collapse. ICML 2021.
- **[ErgenPilanci2020Geom]** (arxiv-2002.11219): Develops convex geometry framework for overparameterized two-layer networks; proves optimal networks are extreme points of rectified ellipsoids; introduces cutting-plane algorithms.
- **[WangLacottePilanci2020]** (arxiv-2006.05900): Provides an exact characterization of all optimal solutions to two-layer ReLU training without using duality; shows Clarke stationary points correspond to global optima of subsampled convex problems.
- **[ErgenPilanci2020CNN]** (arxiv-2006.14798): Extends convex duality to CNNs; reveals that architectural choices (pooling, connectivity) correspond to implicit regularizers ($\ell_1$, $\ell_2$, nuclear norm). ICLR 2021.
- **[Sahiner2020]** (arxiv-2012.13329): Extends to vector-output networks; discovers connection to copositive programming and completely positive matrices; provides soft-thresholded SVD closed-form solutions.
- **[BartanPilanci2021]** (arxiv-2101.02429): Proves polynomial activation networks can be globally trained via SDP; shows weight decay is NP-hard but cubic regularization is tractable; semidefinite lifting is always exact.
- **[Ergen2021BN]** (arxiv-2103.01499): Analyzes batch normalization through convex duality; shows BN effectively whitens data; obtains closed-form solutions in overparameterized regimes; reveals implicit regularization of GD on BN networks.
- **[ErgenPilanci2023Path]** (arxiv-2110.09548): Introduces path regularization for deep parallel ReLU networks yielding exact convex reformulations with group sparsity; provides fully polynomial-time approximation. NeurIPS 2023.
- **[Mishkin2022SCNN]** (arxiv-2202.01331): Develops fast algorithms (accelerated proximal gradient, augmented Lagrangian) for convex ReLU training; shows gated ReLU equivalence; scales to MNIST/CIFAR-10. ICML 2022.
- **[Mishkin2023Optimal]** (arxiv-2306.00119): Characterizes the full polyhedral set of optimal solutions; develops optimal pruning; studies regularization path continuity; provides minimal network construction algorithms.
- **[Dwaraknath2023]** (arxiv-2309.15096): Bridges NTK and convex programs; shows gated ReLU is equivalent to Multiple Kernel Learning; proves NTK is suboptimal compared to the optimal MKL kernel.
- **[ErgenPilanci2023Lasso]** (arxiv-2312.12657): Comprehensive treatment of two-layer networks with piecewise linear activations as Lasso models; proves all stationary points are global optima of subsampled convex programs; zonotope-based polynomial-time approximation.
- **[Zeger2024]** (arxiv-2403.01046): Proves deep neural networks on 1-D data are convex Lasso models; discovers that depth-3 and deeper networks create "reflection features"; provides explicit dictionary matrices.
- **[Gagneux2025]** (arxiv-2501.03017): Studies when ReLU networks implement convex functions (input convexity); proves ICNNs cover all convex one-hidden-layer functions but not two-hidden-layer ones; provides a counterexample and numerical convexity-checking algorithm.

## 10. Implementation Landscape

- **[Feng2023CRONOS]** (user-8652-CRONOS): Repo: https://github.com/pilancilab/CRONOS. Language: Python (JAX). Contains: GPU-accelerated ADMM solver for convex ReLU networks with alternating minimization extension. Dependencies: JAX, NumPy.

- **[Mishkin2022SCNN]** (arxiv-2202.01331): Repo: https://github.com/pilancilab/scnn. Language: Python. Contains: Accelerated proximal gradient and augmented Lagrangian solvers for two-layer convex ReLU networks. Experiments repo: https://github.com/pilancilab/scnn_experiments. Dependencies: PyTorch, NumPy.

- **[Mishkin2023Optimal]** (arxiv-2306.00119): Repo: https://github.com/pilancilab/relu_optimal_sets. Language: Python. Contains: Tools for computing optimal sets, pruning algorithms, and regularization paths for ReLU networks.

- **[ErgenPilanci2023Lasso]** (arxiv-2312.12657): Repo: https://github.com/pilancilab/convex_nn. Language: Python. Contains: Convex neural network implementations with Lasso equivalence, supporting piecewise linear activations.

- **[BartanPilanci2021]** (arxiv-2101.02429): Referenced repo: https://github.com/cvxgrp/scs (SCS solver, used but not developed by this paper). Language: C/Python. Contains: Splitting conic solver for semidefinite programs. Verification status: unverified.
