# Audience-Oriented Literature Map
## Topic: Duality Gap in Dual Convex Optimization of ReLU Neural Networks

**Talk spec:** 8 minutes, mixed_academic audience, survey goal, conference talk,
Q&A after only. Emphasis on work by Mert Pilanci and Tolga Ergen.

**The governing constraint:** Eight minutes is roughly 6-8 slides of substance
plus title and closing. At the mixed_academic pacing rate (0.4 new concepts per
minute), the talk can land about 3-4 genuinely new ideas in the listener's head.
Every choice below is made with that budget in mind.

---

## Section 1: The Problem Statement

Training a neural network looks, from the outside, like one of the great mysteries
of modern machine learning. We take a loss surface that is provably non-convex,
studded with saddle points and local minima, hand it to a first-order method like
SGD, and — despite decades of optimization theory telling us this should not work
— we get a model that generalizes to unseen data. The textbook story is that
over-parameterization, good initialization, and some combination of luck and
folklore make the landscape "effectively benign." That story has always felt
incomplete.

The field this talk surveys — convex reformulations of ReLU networks, driven
largely by Mert Pilanci, Tolga Ergen, and their collaborators at Stanford — offers
a much more surprising answer. It says: that non-convex loss surface you have
been staring at is not the real problem. There is an *equivalent* finite-
dimensional **convex** program sitting behind it. Solve the convex program, and
you have globally optimized the original network. The bridge between the two is
Lagrangian duality, and the central technical question is whether the **duality
gap** — the slack between the non-convex primal and its convex dual — is zero.

For a mixed academic audience this matters for three reasons. First, it reframes
a mystery. If training works, perhaps it is because the problem was secretly
convex all along. Second, it gives us something we almost never have for neural
networks: a **certificate of global optimality**. If you have a solution to the
convex dual, you can verify whether your SGD-trained network is actually the
best you can do. Third, it bridges two communities — the convex optimization
community has a century of tools, and this line of work quietly hands those tools
to deep learning researchers. Pilanci and Ergen (2020) proved the result for
two-layer networks. What followed is a five-year effort to push that bridge
deeper, into CNNs, batch normalization, vector outputs, and arbitrary-depth
architectures. Where the bridge holds, we understand training. Where it breaks
— and it does break, in specific identifiable ways — we learn exactly which
architectural choices matter and why.

In eight minutes I will show you where the bridge stands, where it cracks, and
what the field is racing to prove next.

---

## Section 2: Essential Prerequisites

For a mixed-academic audience with mathematical maturity but no specific
background in this subfield. Listed in order of when a listener encounters them.

- **Concept**: ReLU activation and two-layer ReLU network
  - **Assume known for domain_experts**: yes
  - **Assume known for mixed_academic**: yes
  - **If not known, one-sentence explanation**: A ReLU is the function max(t, 0);
    a two-layer ReLU network is a sum of ReLU features of linear projections
    composed with a second linear layer.
  - **If a slide is needed**: A single equation f(x) = sum_j (x^T u_j)_+ alpha_j
    with each symbol labeled.

- **Concept**: Weight decay regularization
  - **Assume known for domain_experts**: yes
  - **Assume known for mixed_academic**: yes
  - **If not known, one-sentence explanation**: Adding a squared-L2 penalty on
    all network parameters, which is what every major deep learning framework
    calls "weight decay."
  - **If a slide is needed**: Not needed.

- **Concept**: Non-convexity of the training loss
  - **Assume known for domain_experts**: yes
  - **Assume known for mixed_academic**: yes
  - **If not known, one-sentence explanation**: The training loss as a function
    of the weights has multiple local minima and saddle points, so gradient
    descent has no a priori reason to find a global optimum.
  - **If a slide is needed**: Not needed.

- **Concept**: Lagrangian duality and weak/strong duality
  - **Assume known for domain_experts**: yes
  - **Assume known for mixed_academic**: partially — name recognition but not
    the precise statement
  - **If not known, one-sentence explanation**: Every optimization problem
    (the "primal") has a companion "dual" problem whose optimal value is always
    a lower bound on the primal; when the two match, we say strong duality
    holds and the duality gap is zero.
  - **If a slide is needed**: YES — one slide with "Primal P* >= Dual D*; gap
    = P* - D*; strong duality means gap = 0." This is the single most important
    prerequisite to make explicit.

- **Concept**: Hyperplane arrangements and ReLU activation patterns
  - **Assume known for domain_experts**: partially
  - **Assume known for mixed_academic**: no
  - **If not known, one-sentence explanation**: For a fixed dataset X, the
    possible ways a ReLU neuron can "turn on or off" on each data point are
    encoded by diagonal 0/1 matrices D_i, and there are at most O((n/r)^r) of
    them where r = rank(X).
  - **If a slide is needed**: Only if the technical-core slide uses the D_i
    notation — then include a small cartoon of lines dividing a 2D point cloud
    into regions.

- **Concept**: Group L1 / group Lasso regularization
  - **Assume known for domain_experts**: yes
  - **Assume known for mixed_academic**: name recognition
  - **If not known, one-sentence explanation**: A penalty that encourages whole
    groups of variables to be simultaneously zero, promoting "neuron-level"
    sparsity rather than coordinate-level sparsity.
  - **If a slide is needed**: Not needed as a separate slide; mention in one
    sentence during the convex-reformulation slide.

---

## Section 3: The Core Results — A Narrative Arc

Ordered chronologically. For an 8-minute talk, only Result R1, R2, R3, and R5
will make the main slides. R4, R6, R7 are Q&A/backup material. The arc is:
bridge built (R1) → bridge generalized (R2, R3) → bridge's limit discovered (R3) →
bridge made practical (R5) → open frontier (R7).

### Result R1: Two-layer ReLU networks have zero duality gap

**Paper:** Pilanci & Ergen, 2020 (arxiv-2002.10553)

**What was known before this:** Convex reformulations of neural networks existed
only in the infinite-width limit (Bengio et al. 2006; Bach 2017). Finite-width
ReLU network training was believed to be NP-hard, with the best exact algorithm
being O(2^m n^(dm)) brute-force enumeration (Arora et al. 2018).

**What this result changed:** Pilanci and Ergen showed that a finite two-layer
ReLU network with weight decay, for m large enough, has an *exact* equivalent
finite-dimensional convex program. Strong duality holds — the duality gap is
zero. The convex program has complexity polynomial in n when data rank is fixed.
The implication: the non-convex training problem was not really non-convex; it
was a convex problem in disguise that you were solving with the wrong algorithm.

**The surprise or insight:** You would expect a loss function with ReLU
nonlinearities and products of layer weights to have a non-trivial duality gap —
that is what weak duality warns you about for non-convex problems. Pilanci and
Ergen show the gap is *exactly* zero as long as the network is "wide enough"
(m >= m*, where m* <= n + 1).

**Estimated explanation time:**
- domain_experts: 1.5 minutes
- mixed_academic: 2 minutes

**Emphasis status:** emphasis_paper

**For emphasis papers only — deeper treatment:**
- **Key theorem statement (verbatim from source):** From arxiv-2002.10553,
  Theorem 1: "The convex program (8) and the non-convex problem (2) where
  m >= m* have identical optimal values. Moreover, an optimal solution to (2)
  with m* neurons can be constructed from an optimal solution to (8)" via the
  rescaling formulas. The convex program (8) has "2dP variables and 2nP linear
  inequalities where P = 2r(e(n-1)/r)^r, and r = rank(X)" (arxiv-2002.10553).
- **Concrete example:** For a tiny problem with n = 10 points in d = 2
  dimensions, P is at most a few dozen. The convex program is a second-order
  cone program (SOCP) solvable in seconds with CVXPY, while the non-convex
  problem needs SGD with no optimality guarantee.
- **What a listener might misunderstand and how to pre-empt it:** A listener
  will hear "polynomial time" and think "cheap in practice." Pre-empt this:
  the complexity is polynomial in n but exponential in rank(X). For
  high-dimensional data, that is still intractable. The gap between "provably
  convex" and "practically solvable" is exactly what the 2022-2024 follow-up
  work attacks.
- **The one follow-up question an expert would ask:** "Does this require a
  specific width m, or any width?" — Answer: any width m >= m* where m* is
  bounded above by n + 1 and is often much smaller; narrower networks may have
  a non-zero gap.

### Result R2: The bridge extends to CNNs, vector outputs, and batch normalization

**Paper:** Ergen & Pilanci 2021 (arxiv-2006.14798, CNNs); Sahiner et al. 2020
(arxiv-2012.13329, vector outputs); Ergen et al. 2021 (arxiv-2103.01499, batch
normalization)

**What was known before this:** R1 applied only to scalar-output, two-layer,
fully-connected networks without normalization layers. Whether real architectures
— the ones people actually train — have the zero-gap property was open.

**What this result changed:** Convex reformulations were established for
(i) two- and three-layer CNNs with various pooling, (ii) vector-output networks
via copositive programs, and (iii) ReLU networks with batch normalization.
The BN paper contains a particularly clean surprise: batch normalization is
equivalent to *whitening the data* inside the convex reformulation.

**The surprise or insight:** Every standard architectural "trick" — pooling,
vector outputs, batch norm — turns out to correspond to a specific convex
regularizer in the reformulation. Architecture choices are, implicitly, choices
of regularization.

**Estimated explanation time:**
- domain_experts: 1 minute
- mixed_academic: 1.5 minutes

**Emphasis status:** emphasis_paper (all Pilanci/Ergen)

**For emphasis papers — deeper treatment (batch norm result, the one I will
actually show):**
- **Key statement (arxiv-2103.01499):** "We prove that regularized ReLU network
  training problems with BN can be equivalently stated as a finite-dimensional
  convex problem... the equivalent convex problems involve whitened data
  matrices unlike the original non-convex training problem. Hence, using convex
  optimization, we reveal an implicit whitening effect introduced by BN."
- **Concrete example/analogy:** Think of batch norm as a preprocessor that,
  from the convex program's point of view, is already there. Training the BN
  network is equivalent to training a convex model on pre-whitened data.
- **What a listener might misunderstand:** "So BN is just whitening?" — No,
  BN has additional effects on conditioning and gradient flow; the equivalence
  is at the global-optimum level.

### Result R3: The bridge breaks — deep vector-output networks have a non-zero duality gap

**Paper:** Wang, Ergen, & Pilanci 2021 (arxiv-2110.06482)
"Parallel Deep Neural Networks Have Zero Duality Gap," ICLR 2023

**What was known before this:** For two-layer networks, the gap was zero.
Previous work (Ergen & Pilanci 2021) had extended this to deep linear networks
with *scalar* output, and to three-layer networks for rank-1 data. Whether
strong duality held for standard deep networks in general was the open question.

**What this result changed:** Three very precise statements, collectively the
sharpest result in the field: (1) For standard *deep linear* networks with
vector output and L >= 3 layers, the duality gap is *non-zero* and can be
computed in closed form. (2) The gap arises from a Schatten norm mismatch and
vanishes only when all singular values are equal. (3) A modified architecture —
**parallel / multi-branch networks** — restores zero duality gap at arbitrary
depth.

**The surprise or insight:** You might expect that deeper networks are "more
non-convex," so the gap should grow continuously with depth. Instead, the gap
is exactly zero for L = 2, then suddenly non-zero for L >= 3 — but only for
the *standard* architecture. Split the network into parallel branches and the
gap snaps back to zero regardless of depth. Architecture, not depth, is the
villain.

**Estimated explanation time:**
- domain_experts: 2 minutes
- mixed_academic: 2.5 minutes

**Emphasis status:** emphasis_paper — this is the centerpiece of the talk
because it is the first *negative* result and the most interesting sentence.

**For emphasis papers — deeper treatment:**
- **Key theorem statement (verbatim from source, arxiv-2110.06482 Theorem 1):**
  "For L >= 3, there exists an activation function phi and a L-layer standard
  neural network... such that the strong duality does not hold, i.e., P > D.
  In contrast, for any L-layer parallel neural network... with linear or ReLU
  activations and sufficiently large number of branches, strong duality holds,
  i.e., P = D."
- **Concrete example:** A three-layer deep linear network with vector output
  trained with weight decay on data where the singular values of X^† Y are not
  all equal — the paper computes a closed-form primal and dual and shows a
  strict gap.
- **What a listener might misunderstand:** "Parallel" does not mean data
  parallelism on multiple GPUs. It means the network architecture itself is
  organized into K independent branches whose outputs are summed — like
  Inception, ResNeXt, or the "multi-branch" wide networks.
- **The one follow-up question an expert would ask:** "Does this mean you
  should re-architect production networks as parallel branches?" — Answer:
  The paper notes that modern architectures (ResNeXt, Inception, SqueezeNet)
  already have parallel structure, which may explain why they train more
  reliably. ResNets with weight decay fit as a special case.

### Result R4: The optimal solution set is a polytope, and Lasso is lurking everywhere

**Paper:** Mishkin & Pilanci 2023 (arxiv-2306.00119); Ergen & Pilanci 2023
(arxiv-2312.12657); Zeger et al. 2024 (arxiv-2403.01046)

**What was known before this:** R1 gave the optimal value. The *geometry* of
the optimal set was not characterized.

**What this result changed:** The set of all globally optimal ReLU networks
for a two-layer weight-decay problem is a polyhedral set in the convex-lifted
parameterization; all stationary points of the non-convex problem correspond
to global optima of a subsampled convex program; and for 1-D data, deep
networks reduce to Lasso with a "library of mirrors" dictionary of reflection
features.

**The surprise or insight:** Not just the value but the structure is
classical — neural networks with weight decay are, in a precise sense, sparse
linear regression in a particular high-dimensional feature space.

**Estimated explanation time:**
- domain_experts: 1 minute
- mixed_academic: 1.5 minutes

**Emphasis status:** standard — mentioned as part of a "what else followed"
sentence; will not get its own slide in an 8-minute talk.

### Result R5: The convex reformulation is approximable in true polynomial time

**Paper:** Kim & Pilanci 2024 (arxiv-2402.03625); supported by Mishkin, Sahiner,
Pilanci 2022 (arxiv-2202.01331, SCNN) and Feng, Frangella, Pilanci 2023
(CRONOS, user-8652-CRONOS)

**What was known before this:** The exact convex reformulation has ~(n/r)^r
variables, which is intractable for high-dimensional data. Practitioners used
randomized subsampling but had no approximation guarantee.

**What this result changed:** Kim and Pilanci (2024) proved that randomly
subsampling the hyperplane arrangement patterns gives an optimality gap
bounded by O(sqrt(log n)), so there is now a truly polynomial-time algorithm
that approximates the global optimum within a logarithmic factor. In parallel,
SCNN (ICML 2022) and CRONOS (2023) built GPU-accelerated ADMM solvers that
actually run on ImageNet — the first time convex reformulations scaled beyond
downsampled MNIST.

**The surprise or insight:** The gap between "theoretically convex" and
"practically solvable" was closed twice over in 2022-2024: once with a
provable approximation bound and once with engineering.

**Estimated explanation time:**
- domain_experts: 1 minute
- mixed_academic: 1.5 minutes

**Emphasis status:** emphasis_paper (Pilanci). This is the closing beat of
the talk — shows the field is mature enough to run on real data.

### Result R6: Convex duality fixes the NTK's known limitations

**Paper:** Dwaraknath, Ergen, Pilanci 2023 (arxiv-2309.15096)

**What was known before this:** The Neural Tangent Kernel view (Jacot et al.
2018) explained infinite-width network training but Chizat & Bach (2018)
showed that no actual feature learning happens in this regime.

**What this result changed:** The convex reformulation of a *gated ReLU*
network is shown to be an instance of Multiple Kernel Learning whose kernel
reduces to the NTK when the mask weights do not depend on targets. Iterative
reweighting upgrades the NTK into the optimal MKL kernel, which equals the
convex-reformulation solution.

**The surprise or insight:** The NTK is the "lazy" version of the exact convex
kernel; feature learning is exactly the gap between them.

**Estimated explanation time:**
- domain_experts: 1.5 minutes
- mixed_academic: 2 minutes

**Emphasis status:** standard — mention only in Q&A if asked about NTK.

### Result R7: What is the right notion of convexity for deep ReLU networks?

**Paper:** Gagneux, Massias, Soubies, Gribonval 2025 (arxiv-2501.03017)

**What was known before this:** Input-Convex Neural Networks (ICNNs) are the
standard way to build a neural network that represents a convex function.

**What this result changed:** A non-Pilanci group shows that ICNNs capture all
convex functions implementable by one-hidden-layer networks, but from two
hidden layers on there exist convex functions expressible by a ReLU network
that *no* ICNN of the same architecture can realize. The right notion of
"convex ReLU network" is still contested.

**The surprise or insight:** The field's most popular convexification trick
(ICNNs) is strictly less expressive than the theoretical space of convex
functions expressible by ReLU networks at depth >= 2.

**Estimated explanation time:**
- domain_experts: 1.5 minutes
- mixed_academic: 2 minutes

**Emphasis status:** standard — reserved for "open directions" closing slide.

---

## Section 4: The Technical Heart

These are the two results the speaker must know cold, not just describe. An
8-minute talk can afford to show one equation prominently (the convex
reformulation) and to state two theorems verbally. TC1 and TC2 are those two.

### Technical Core TC1: Strong duality for two-layer ReLU networks (Pilanci-Ergen 2020)

**Theorem statement (plain language):** For a two-layer ReLU network with
weight decay, if the width is at least some critical value m*, the non-convex
training problem has the same optimal value as a finite-dimensional convex
program, and any solution to the convex program can be mapped back to a
globally optimal network.

**Theorem statement (precise):** From arxiv-2002.10553, Theorem 1 — "The
convex program (8) and the non-convex problem (2) where m >= m* have
identical optimal values. Moreover, an optimal solution to (2) with m*
neurons can be constructed from an optimal solution to (8)" with m* given by
the sum of nonzero v_i* and w_i* variables in the convex solution.

**Key mechanism:** The product of the hidden-layer weight u_j and the outer
weight alpha_j can be absorbed into a single variable, and the combinatorial
non-linearity of ReLU is resolved by enumerating hyperplane arrangement
patterns — there are only finitely many of them (at most 2r(e(n-1)/r)^r),
and *within* each arrangement the problem becomes convex. The dual of the
resulting semi-infinite program has a polyhedral feasible set.

**Proof sketch in 3 steps:**
1. Rewrite the weight-decay problem as an L1-penalized problem on rescaled
   weights (Lemma, arxiv-2002.10553). This is possible because of the
   homogeneity of ReLU: rescaling u by a factor c and alpha by 1/c leaves
   the network output invariant.
2. Take the Lagrangian dual with respect to alpha, which gives a
   semi-infinite maximization over a constraint indexed by all
   unit-norm u in R^d. Partition R^d by the hyperplane arrangement patterns
   D_1, ..., D_P; within each pattern the constraint becomes convex.
3. Take the dual again (bi-dual), and apply Caratheodory's theorem to show
   the bi-dual has a finite optimal solution with at most n + 1 atoms.
   Match against the primal. Strong duality holds by Slater's condition on
   the finite convex program.

**Concrete example:** n = 4 two-dimensional points with a rank-2 data matrix.
The hyperplane arrangements number P <= 8. The convex program has 16
variables and 16 linear inequalities. A standard interior-point SOCP solver
solves it in milliseconds. SGD on the non-convex problem, with random
initialization, converges to different values on different runs — but the
convex solver returns a certificate that SGD's best run matches the global
optimum.

**Why this belongs in the talk:** This is the foundational theorem. Without
understanding that P = D holds here and only here, the rest of the talk is
vocabulary. It is also the only theorem the speaker will state precisely;
everything else will be described in English.

### Technical Core TC2: Depth breaks strong duality, parallelism restores it (Wang-Ergen-Pilanci 2021)

**Theorem statement (plain language):** For standard deep networks with three
or more layers, strong duality can fail and the duality gap is strictly
positive. But if you rearrange the same network into independent parallel
branches, strong duality is restored at any depth.

**Theorem statement (precise):** From arxiv-2110.06482, Theorem 1 — "For
L >= 3, there exists an activation function phi and a L-layer standard
neural network defined in (3) such that the strong duality does not hold,
i.e., P > D. In contrast, for any L-layer parallel neural network defined
in (4) with linear or ReLU activations and sufficiently large number of
branches, strong duality holds, i.e., P = D."

**Key mechanism:** The non-zero gap in deep linear networks comes from the
Schatten-2/L quasi-norm that the L2 weight decay implicitly induces. For
L = 2 this is the nuclear norm, which is convex. For L >= 3 it becomes a
non-convex quasi-norm and the duality gap equals the difference between the
nuclear and Schatten-2/L norms. Parallel architectures eliminate this by
replacing the composition of L layers with a sum over independent branches,
which decouples the weight matrices and makes the regularizer convex again.

**Proof sketch in 3 steps:**
1. For the standard deep linear network, rescale layer weights using a scale
   parameter t and reduce to a Schatten-2/L norm minimization problem. Compute
   the primal in closed form (arxiv-2110.06482, Prop. 2).
2. Compute the dual, which corresponds to a *parallel* network's minimum-norm
   problem (the bi-dual literally corresponds to a parallel architecture —
   the surprise). The dual equals the nuclear norm of X^†Y times a constant.
3. The gap equals the Schatten-2/L norm minus the nuclear norm, which is
   strictly positive unless all singular values of X^†Y are equal. For
   parallel networks, the primal already is the bi-dual, so the gap vanishes
   by construction.

**Concrete example:** A 3-layer linear network with vector output on data
whose X^†Y has distinct singular values 1, 2, 3. The paper computes both
primal and dual in closed form; the gap is positive and explicit. Rearrange
as a parallel network with enough branches (bounded by KN+1): the gap
vanishes.

**Why this belongs in the talk:** This is the single most interesting
sentence in the corpus for a mixed academic audience. It says "the thing
you thought was true (strong duality) is actually false in general, and the
fix has a clean architectural interpretation." Without this result, the
talk is a victory lap for R1. With it, the talk has a dramatic arc.

---

## Section 5: Contested Areas and Live Debates

Three live debates, each of which the speaker should be prepared to discuss
but at most one of which (the middle one) will be mentioned explicitly in
the eight minutes.

**What is contested:** Whether the zero-duality-gap story is the *right*
explanation for why SGD trains neural networks well.
**The two positions:** Position A (Pilanci-Ergen school): the non-convex
loss landscape is secretly convex; SGD succeeds because it is approximately
solving the convex dual. Position B (NTK / mean-field school): the
non-convex loss is "benign" in the over-parameterized limit and the kernel
or mean-field approximation is what matters.
**What each side cites:** Position A: Pilanci & Ergen 2020; Wang, Lacotte &
Pilanci 2020 (which shows all stationary points of the non-convex problem
correspond to optima of subsampled convex programs). Position B: Jacot et al.
2018 (NTK); Chizat & Bach 2018 (mean-field).
**Current status:** Trending toward partial reconciliation. Dwaraknath,
Ergen, Pilanci 2023 (arxiv-2309.15096) shows the NTK is a special case of
the convex reformulation's MKL structure, so the two views are not in
conflict; the convex view is strictly more general.
**Presentation value:** Explains why this line of work is *the* answer and
not just *an* answer — positions it against the audience's existing beliefs.

**What is contested:** Whether standard deep architectures (beyond two
layers) actually have zero duality gap in practice, or whether only parallel
architectures do.
**The two positions:** Position A: Only parallel/multi-branch networks have
provable zero gap at depth >= 3 (Wang, Ergen, Pilanci 2021). Position B:
Maybe a more clever analysis will extend the zero-gap result to standard
networks; the 2021 negative result is about a specific construction.
**What each side cites:** Position A: arxiv-2110.06482 explicitly constructs
a counterexample for L = 3 standard networks. Position B: arxiv-2002.09773
handles deep linear networks with scalar output and whitened data; the
closed question is whether the result holds for vector outputs.
**Current status:** Trending toward Position A — the counterexample is
explicit, and the parallel-architecture result suggests the obstruction is
intrinsic.
**Presentation value:** This is the drama of the talk — Result R3 (TC2).
Mentioning it explicitly makes the talk feel current and honest.

**What is contested:** What is the "right" convex class of ReLU networks?
**The two positions:** Position A: Input Convex Neural Networks (ICNNs) are
the correct convexification — they are expressive enough for any convex
function in theory. Position B: ICNNs are a strict subset; there exist
convex functions expressible by deep ReLU networks that no ICNN of the same
architecture can implement.
**What each side cites:** Position A: Amos, Xu, Kolter 2017 (the original
ICNN paper); Chen et al. 2019 (universal approximation). Position B:
Gagneux et al. 2025 (arxiv-2501.03017).
**Current status:** Unresolved and recent (2025). The Gagneux paper is from
a different research group, which makes this a healthy external check on
the Pilanci-Ergen program.
**Presentation value:** Useful for the "open questions" closing slide to
show the field is not the private property of a single group.

---

## Section 6: Connections to Adjacent Fields and Applications

- **Adjacent field / application**: Compressed sensing and sparse regression
  - **The connection**: The convex reformulation is a group Lasso in a
    high-dimensional feature space. Training a ReLU network = solving a
    structured sparse recovery problem.
  - **Accessible to**: mixed_academic
  - **Source**: arxiv-2312.12657 (Ergen & Pilanci 2023, "Convex Landscape
    of Neural Networks via Lasso Models")

- **Adjacent field / application**: Semidefinite programming and copositive
  optimization
  - **The connection**: Vector-output ReLU networks correspond to copositive
    programs; polynomial-activation networks correspond to SDPs via
    semidefinite lifts.
  - **Accessible to**: domain_experts
  - **Source**: arxiv-2012.13329 (Sahiner et al., copositive);
    arxiv-2101.02429 (Bartan & Pilanci, neural spectrahedra)

- **Adjacent field / application**: Practical deep learning at scale
  - **The connection**: CRONOS (2023) runs convex ReLU network training on
    ImageNet with GPU-accelerated ADMM, matching or beating tuned Adam.
    This is the first time convex reformulations became practically useful
    on real data.
  - **Accessible to**: mixed_academic
  - **Source**: user-8652-CRONOS (Feng, Frangella, Pilanci 2023)

- **Adjacent field / application**: Neural Tangent Kernel and kernel methods
  - **The connection**: The convex reformulation of gated ReLU networks is
    an instance of Multiple Kernel Learning; the NTK is a fixed-point of
    this MKL with target-independent weights, and iterative reweighting
    recovers the full convex optimum.
  - **Accessible to**: domain_experts
  - **Source**: arxiv-2309.15096 (Dwaraknath, Ergen, Pilanci 2023)

- **Adjacent field / application**: Optimal transport and Brenier maps
  - **The connection**: Training convex neural networks is needed to learn
    Monge maps in optimal transport; ICNNs are the standard but may not be
    the most expressive choice.
  - **Accessible to**: mixed_academic
  - **Source**: arxiv-2501.03017 (Gagneux et al. 2025)

---

## Section 7: Notation and Vocabulary Reference

Ordered by when a listener encounters each term in the talk.

| Symbol / Term | Definition | First introduced in |
|---------------|-----------|-------------------|
| n | Number of training samples | arxiv-2002.10553 |
| d | Input feature dimension | arxiv-2002.10553 |
| X in R^(n x d) | Data matrix; rows are samples | arxiv-2002.10553 |
| y in R^n | Label vector (regression/binary classification) | arxiv-2002.10553 |
| (t)_+ = max(t, 0) | ReLU activation | arxiv-2002.10553 |
| m | Number of hidden neurons (network width) | arxiv-2002.10553 |
| u_j in R^d | Hidden-layer weight for neuron j | arxiv-2002.10553 |
| alpha_j in R | Output-layer weight for neuron j | arxiv-2002.10553 |
| beta > 0 | Weight-decay regularization strength | arxiv-2002.10553 |
| P* | Optimal value of the non-convex primal training problem | arxiv-2002.10553 |
| D* | Optimal value of the convex dual problem | arxiv-2002.10553 |
| Duality gap | P* - D*; zero means "strong duality holds" | arxiv-2002.10553 |
| Strong duality | P* = D*, i.e., the gap is zero | arxiv-2002.10553 |
| m* | Critical width at which strong duality holds; m* <= n + 1 | arxiv-2002.10553 |
| D_i = diag(1[X u_i >= 0]) | ReLU activation pattern (diagonal 0/1 matrix) | arxiv-2002.10553 |
| P | Number of distinct hyperplane arrangements, P = O((n/r)^r) | arxiv-2002.10553 |
| r = rank(X) | Rank of the data matrix | arxiv-2002.10553 |
| L | Depth of the network (number of layers) | arxiv-2110.06482 |
| Parallel / multi-branch network | L-layer network split into K independent branches that sum at the output | arxiv-2110.06482 |
| Schatten-p norm | (sum of sigma_i(A)^p)^(1/p); Schatten-1 is the nuclear norm | arxiv-2110.06482 |
| Gated ReLU network | A ReLU variant where activation gates are decoupled from the linear map | arxiv-2309.15096 |
| ICNN | Input Convex Neural Network; ReLU network with non-negative hidden weights | arxiv-2501.03017 |

---

## Section 8: Per-Paper Audience Value Assessment

For an 8-minute survey, the talk can afford to name about 6-8 papers on
screen. Everything graded Essential or Useful is a candidate; everything
graded Background is cited orally only if relevant to a Q&A.

| Paper | Grade | Reason |
|-------|-------|--------|
| arxiv-2002.10553 (Pilanci & Ergen 2020) | **Essential** | The foundational theorem. Without it the talk does not exist. |
| arxiv-2110.06482 (Wang, Ergen, Pilanci 2021 — Parallel) | **Essential** | The dramatic centerpiece: duality gap is non-zero at depth >= 3, except for parallel networks. |
| arxiv-2402.03625 (Kim & Pilanci 2024) | **Essential** | Closes the theory-to-practice gap with a polynomial-time approximation guarantee. Natural talk closer. |
| user-8652-CRONOS (Feng, Frangella, Pilanci 2023) | **Essential** | The practical demonstration — scales to ImageNet; shows the field is mature enough to run on real data. |
| arxiv-2110.05518 (Ergen & Pilanci 2021 — Deep networks) | **Useful** | Three-layer extension; provides the algorithmic bridge from two layers to parallel-deep networks. |
| arxiv-2103.01499 (Ergen et al. 2021 — Batch Norm) | **Useful** | Surprising: BN = whitening. Good one-sentence insertion when discussing architectural extensions. |
| arxiv-2202.01331 (Mishkin, Sahiner, Pilanci 2022 — SCNN) | **Useful** | Fast solver and the "gated ReLU" model class. Complements CRONOS as the ICML-venue version. |
| arxiv-2501.03017 (Gagneux et al. 2025) | **Useful** | External-group check on ICNN expressivity; closing-slide open-question material. |
| arxiv-2312.12657 (Ergen & Pilanci 2023 — Convex Landscape) | **Useful** | Single clean statement of the Lasso view; good reference for the "why this matters for stats audiences" slide. |
| arxiv-2309.15096 (Dwaraknath, Ergen, Pilanci 2023 — NTK) | **Background** | Resolves a natural Q&A question ("how does this relate to NTK?"); not worth a slide in 8 min. |
| arxiv-2002.09773 / user-ergen21b (Ergen & Pilanci 2021 — Revealing Structure) | **Background** | Deep linear and whitened ReLU; used as a reference for weight alignment claims in Q&A. |
| arxiv-2002.11219 (Ergen & Pilanci 2020 — Convex Geometry) | **Background** | Extreme-point characterization; cutting-plane algorithms. Background for cone-constrained slide if asked. |
| arxiv-2006.05900 (Wang, Lacotte, Pilanci 2020) | **Background** | Characterizes all stationary points as optima of subsampled convex programs. Key for the "position A vs NTK" debate in Q&A. |
| arxiv-2006.14798 (Ergen & Pilanci 2020 — CNNs) | **Background** | CNN extension; mention orally as part of "this was then extended to CNNs, vector outputs, and batch norm." |
| arxiv-2012.13329 (Sahiner et al. 2020 — Vector outputs) | **Background** | Vector-output/copositive programs; mention orally in the same sentence as CNNs. |
| arxiv-2101.02429 (Bartan & Pilanci 2021 — Polynomial activations) | **Skip-for-talk** | Polynomial activations are a side branch; too much to set up in 8 min. |
| arxiv-2110.09548 (Ergen & Pilanci 2021 — Path Regularization) | **Skip-for-talk** | Important for the research paper version but a distraction in a conference survey. |
| arxiv-2306.00119 (Mishkin & Pilanci 2023 — Optimal Sets) | **Skip-for-talk** | Geometric characterization of the optimal polytope; valuable research direction but too technical for 8 minutes. |
| arxiv-2403.01046 (Zeger et al. 2024 — Library of Mirrors) | **Skip-for-talk** | 1-D Lasso reduction; beautiful but narrow. Skip unless audience asks about toy-dimensional results. |
| user-ergen21b (Revealing Structure, ICML 2021 version) | **Skip-for-talk** | Duplicate of arxiv-2002.09773; already covered. |

---

## Talk Budget Summary

For the 8-minute budget, the narrative fits roughly as:

- 0:00-1:30 — Problem statement: why non-convex training is a mystery and
  what duality buys us (Section 1 material).
- 1:30-3:30 — R1: Pilanci-Ergen 2020 two-layer zero-gap theorem. Show the
  convex reformulation equation once. (TC1)
- 3:30-4:15 — R2: one sentence on CNNs / batch norm / vector outputs. Show
  the "BN = whitening" insight as the most memorable.
- 4:15-6:30 — R3 / TC2: the negative result and the parallel-architecture
  fix. Spend real time here — this is the talk's dramatic peak.
- 6:30-7:30 — R5: Kim-Pilanci 2024 approximation guarantee + CRONOS
  demonstration. "The theory has shipped."
- 7:30-8:00 — Open questions: non-Pilanci convexity results (R7), what
  happens beyond parallel architectures, and the Q&A preview.
