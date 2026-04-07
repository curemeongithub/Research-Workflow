# Key Findings — Presentation-Ready Package
## Topic: Duality Gap in Dual Convex Optimization of ReLU Neural Networks

**Talk spec:** 8 minutes, mixed_academic audience, survey goal, conference talk,
Q&A after only. Emphasis on Pilanci and Ergen.

**Selection notes:** An 8-minute talk at mixed_academic pacing (0.4 new concepts
per minute) can land 3-4 genuinely new ideas. I have therefore selected six
findings; four of them (F1, F2, F4, F6) will occupy the main slides, while F3
and F5 are one-sentence insertions or backup slides the speaker can deploy
if the room is warm. All candidate findings were scored along three axes
(surprise, explicability, narrative function); selection is restricted to
emphasis papers (Pilanci, Ergen, and their immediate collaborators) per the
talk_spec.

---

### Finding F1: Two-Layer ReLU Networks Have Zero Duality Gap

**Headline (for slide title):**
ReLU training is a convex program in disguise

**Plain-language summary:**
For the last decade the training loss of a neural network has been treated as
a cautionary tale about non-convex optimization — a landscape full of local
minima where gradient descent has no right to succeed. In 2020 Mert Pilanci
and Tolga Ergen proved something startling. A two-layer ReLU network trained
with ordinary weight decay is *exactly* equivalent, at the global optimum,
to a finite-dimensional convex program. The duality gap — the slack you
would normally expect between a non-convex primal and its dual — is
identically zero, provided the network is wide enough. The non-convex
problem you were solving with SGD was secretly convex all along.

**Why it is presentation-worthy:**
This result rewrites the textbook story about why neural network training
is hard. It converts a mystery ("why does SGD work?") into a concrete
technical answer ("because the problem has zero duality gap and strong
duality holds"), and it does so with a single one-sentence theorem a
non-specialist can recognise. Without this finding the rest of the talk
does not exist.

**Source:** Pilanci & Ergen, 2020 (arxiv-2002.10553), Theorem 1
**Verified at:** sources/arxiv-2002.10553/content.md, lines 162 and 172
(verbatim theorem statement and SOCP complexity claim).

**Estimated explanation time:**
- domain_experts: 1.5 minutes
- mixed_academic: 2 minutes

**One-slide treatment plan:**

*For a 90-second version:*
- Title: "ReLU training is a convex program in disguise"
- Visual: Two boxes connected by a double-headed arrow. Left box: the
  familiar non-convex loss landscape cartoon (wavy 2D surface with local
  minima marked). Right box: a convex bowl labelled "finite-dim SOCP."
  The arrow is labelled "zero duality gap (Pilanci-Ergen 2020)."
- Key equation (optional, one line):
  `min_{u_j, α_j}  (1/2)||Σ_j (X u_j)_+ α_j - y||² + (β/2) Σ_j (||u_j||² + α_j²)`
  with arrow to
  `= min  ||·||_{2,1} subject to finite linear constraints over P hyperplane patterns`
  (Pilanci & Ergen 2020, eqn. 2 and 8)
- 3 sentences to say:
  1. "The training loss of a two-layer ReLU network with weight decay is
     non-convex — it has local minima, saddle points, the usual mess."
  2. "Pilanci and Ergen showed in 2020 that if you write down its
     Lagrangian dual and then the dual of that, you recover a
     finite-dimensional convex program with exactly the same optimal
     value — the duality gap is zero."
  3. "The non-convex problem you thought you were solving with SGD is,
     globally, a second-order cone program you could hand to any
     convex solver."

*For a 3-minute version:*
- Same visual, plus:
- A small inset showing how the critical width m* <= n + 1 — "any network
  wider than roughly the number of training points is guaranteed to hit
  strong duality."
- The rescaling identity in one line: `u_j → c u_j, α_j → α_j/c` leaves
  the network unchanged, so weight decay behaves like an L1 penalty on
  the *product* α_j ||u_j||.
- Transition to next finding: "So two layers are convex. What about
  the architectural tricks that actually matter in practice?"

**Speaking hook:**
"For the last ten years we have told students that neural network training
is non-convex — that SGD has no right to work. In 2020 Pilanci and Ergen
showed we were wrong about that."

**One thing audiences often misunderstand:**
Polynomial time does not mean cheap. The complexity is polynomial in n
but exponential in the data rank r — fine for low-rank problems, still
intractable for full-rank high-dimensional data. Pre-empt with: "The
convex program has O((n/r)^r) variables, so the theorem is clean but the
naive solver is not scalable — and we will see in a minute what the
field did about that."

**The one expert follow-up question:**
*"Does the theorem need a specific width or any width?"* — Answer: any
width m >= m* where m* is bounded above by n + 1 and is often much
smaller. Narrower networks may have a strictly positive gap.

---

### Finding F2: Depth Breaks Strong Duality, Parallelism Restores It

**Headline (for slide title):**
Depth breaks duality; parallelism restores it

**Plain-language summary:**
Once strong duality was established for two-layer networks, the obvious
question was: does it extend to deep networks? In 2021 Wang, Ergen, and
Pilanci gave a sharp answer. For *standard* deep networks with three or
more layers and vector output, the duality gap is strictly positive — it
can be computed in closed form and arises from a mismatch between a
Schatten quasi-norm and the nuclear norm. Remarkably, the fix is
architectural, not analytical. If you rewrite the same network as a sum
of independent parallel branches — the structure already present in
Inception, ResNeXt, and SqueezeNet — strong duality snaps back at any
depth. The villain is not depth; it is sequential composition.

**Why it is presentation-worthy:**
This is the first *negative* result in the corpus and the dramatic centre
of the talk. It takes a listener who has just been told "ReLU networks
are secretly convex" and immediately subverts the expectation by showing
that sequential depth breaks the result — then rescues the story with a
clean architectural fix that matches what practitioners already do. The
pattern "expected A, got B, and B has a physical meaning" is the strongest
narrative move in the talk.

**Source:** Wang, Ergen & Pilanci, 2021 (arxiv-2110.06482), Theorem 1
**Verified at:** sources/arxiv-2110.06482/content.md, lines 120, 42-44
(main theorem and summary of contributions).

**Estimated explanation time:**
- domain_experts: 2 minutes
- mixed_academic: 2.5 minutes

**One-slide treatment plan:**

*For a 90-second version:*
- Title: "Depth breaks duality; parallelism restores it"
- Visual: Two network diagrams side by side. Left: a standard sequential
  L-layer network drawn as a stack of boxes. Label underneath in red:
  "P > D for L >= 3." Right: a parallel / multi-branch network with K
  independent branches that sum at the output. Label underneath in
  green: "P = D for any L." Below both, the single sentence
  "Architecture, not depth, is the villain."
- Key equation (verbal only): "The gap equals the Schatten-2/L norm minus
  the nuclear norm of X†Y — zero only when all singular values are equal."
- 3 sentences to say:
  1. "You would expect that deeper networks are 'more non-convex,' so
     maybe the duality gap grows with depth."
  2. "Wang, Ergen, and Pilanci showed it is not that gradual. At L=2 the
     gap is exactly zero; at L=3 it jumps to something strictly positive
     they can write in closed form."
  3. "But — and this is the beautiful part — if you rearrange the same
     network as a sum of independent parallel branches, the gap
     immediately snaps back to zero at every depth."

*For a 3-minute version:*
- Same visual, plus:
- One sentence of context: the bi-dual of a standard deep network
  literally *is* a parallel network — the parallel architecture is
  what the dual problem is "trying to be."
- One sentence on practice: most modern architectures (Inception,
  ResNeXt, Wide ResNets) already have parallel structure, which may
  explain why they train more reliably.
- Transition to next finding: "So strong duality holds for two-layer
  networks and for parallel deep networks — but only if the convex
  program is tractable. How tractable is it actually?"

**Speaking hook:**
"You might expect the duality gap to degrade gracefully as networks
get deeper. It does not. It degrades abruptly at three layers — and
is rescued by an architectural choice you already make."

**One thing audiences often misunderstand:**
"Parallel" here does *not* mean data parallelism on multiple GPUs. It
means the network architecture itself is split into K independent
branches whose outputs are summed. Pre-empt with one sentence when the
word first appears: "By parallel I mean architecturally parallel, in
the sense of Inception or ResNeXt — not GPU parallelism."

**The one expert follow-up question:**
*"Does this mean we should re-architect production networks as parallel
branches?"* — Answer: modern architectures (ResNeXt, Inception,
SqueezeNet, Wide ResNets) already have that structure. The paper
actually interprets their empirical success partly through this lens.
ResNets with weight decay fit as a special case.

---

### Finding F3: Batch Normalization Is Whitening in Disguise

**Headline (for slide title):**
Batch norm = whitening the data

**Plain-language summary:**
Batch normalization is the single most common trick in deep learning — 
people add it because it makes networks train faster and generalize
better, but the *reason* has been a matter of folklore. Ergen and
colleagues (2021) showed that once you pass a ReLU network with batch
normalization through the convex-dual lens, the equivalent convex
program is exactly the same as the un-normalized program, *except* that
the data matrix has been whitened. Batch normalization is not a
mysterious optimization trick. It is a preprocessor that, from the
convex program's point of view, has already whitened your features
before training began.

**Why it is presentation-worthy:**
A one-line interpretation of one of the most used tricks in deep
learning, delivered with a precise mathematical equivalence. Audiences
respond strongly to "X, which you have been using forever, is secretly
just Y." It also demonstrates — in one sentence — that the convex
reformulation lens generalises to real architectural features, which
is the content the talk needs to cover in its middle section without
burning minutes.

**Source:** Ergen, Sahiner, Ozturkler, Pauly, Mardani & Pilanci, 2021
(arxiv-2103.01499), Theorem 2.2
**Verified at:** sources/arxiv-2103.01499/content.md, lines 40 and 150
(verbatim claim that the BN convex equivalent "involves whitened data
matrices," and "the data matrix for the convex program is whitened,
i.e., U'^T U' = I").

**Estimated explanation time:**
- domain_experts: 45 seconds
- mixed_academic: 1 minute

**One-slide treatment plan:**

*For a 90-second version (this slide runs 45-60 seconds in the actual talk):*
- Title: "Batch norm = whitening the data"
- Visual: A single block diagram. Raw data X → box labelled "BN-ReLU
  network" → output y, with an equals sign below pointing to: whitened
  data X_w → box labelled "plain ReLU convex program" → output y. One
  arrow, one equivalence.
- Key equation (verbal only, or inline): "U'^T U' = I in the equivalent
  convex program" (Ergen et al. 2021, Thm 2.2).
- 3 sentences to say:
  1. "Batch normalization is the single most common trick in deep
     learning and nobody has a clean story for why it helps."
  2. "Ergen and collaborators in 2021 pushed a BN-ReLU network through
     the convex-dual lens and discovered something strikingly simple."
  3. "The equivalent convex program is identical to the one without
     batch norm, except that the data has been whitened — batch norm
     is implicit whitening."

*For a 3-minute version:*
- Same visual, plus:
- One follow-up sentence: this is equivalence at the level of the
  global optimum; SGD on a BN network and an SGD on a whitened input
  may take different trajectories because of conditioning effects.
- Transition to next finding: "These results cover the theory side. But
  an exponential-in-rank convex program is not something you can run
  on ImageNet. Can any of this actually be solved at scale?"

**Speaking hook:**
"Here is one sentence about one of the most-used tricks in deep learning
that I think will surprise you."

**One thing audiences often misunderstand:**
"So batch norm is just whitening?" — Only at the global optimum. BN
still has extra effects on gradient conditioning and training dynamics
that are not captured by the convex-equivalence statement. Pre-empt
with: "This is an equivalence of optimal values, not of training
trajectories."

**The one expert follow-up question:**
*"Does the equivalence extend to layer norm, group norm, weight norm?"*
— Answer: the same machinery works for any normalization that can be
written as a reparametrization of the data matrix; the BN paper
handles BN specifically and leaves LN/GN as natural corollaries.

---

### Finding F4: Polynomial-Time Approximation Within a sqrt(log n) Factor

**Headline (for slide title):**
Polynomial-time approximation: a log-factor guarantee

**Plain-language summary:**
The original zero-duality-gap theorem had one big asterisk. The convex
program is exact, but it has roughly (n/r)^r variables, which is
exponential in the data rank — so in high dimensions the "polynomial
time" claim is misleading. In 2024 Kim and Pilanci closed this gap in
theory. They proved that if you randomly subsample the hyperplane
arrangement patterns and keep only O(log n) of them, the solution of
the resulting small convex program is within a factor of
sqrt(log n) of the true global optimum with high probability. The
implication: there is now a genuinely polynomial-time algorithm that
approximates neural network training within a logarithmic factor.

**Why it is presentation-worthy:**
This is the theoretical closing beat — the result that promotes the
convex reformulation story from elegant theory to genuine algorithm.
It also resolves a tension that any expert in the audience will have
already raised mentally: "polynomial in n but exponential in rank is
not polynomial in practice." The answer is "and here is the fix,
from 2024." It rewards the listener for noticing the issue.

**Source:** Kim & Pilanci, 2024 (arxiv-2402.03625), Theorem 2.1 and 2.3
**Verified at:** sources/arxiv-2402.03625/content.md, lines 15, 42-44,
128 (O(sqrt(log n)) bound verbatim; first polynomial-time approximation
guarantee for regularized ReLU networks).

**Estimated explanation time:**
- domain_experts: 1 minute
- mixed_academic: 1.5 minutes

**One-slide treatment plan:**

*For a 90-second version:*
- Title: "Polynomial-time approximation: a log-factor guarantee"
- Visual: Two progress bars. Top bar: "exact convex reformulation,
  O((n/r)^r) variables" in grey. Bottom bar: "random subsample,
  O(log n) patterns" in blue, with a tag to the right that reads
  "p* <= p_tilde* <= C sqrt(log 2n) p*". A single citation:
  Kim & Pilanci 2024.
- Key equation (one line, centred):
  `p* ≤ p̃* ≤ C · sqrt(log 2n) · p*`
  (Kim & Pilanci 2024, Theorem 2.1)
- 3 sentences to say:
  1. "The catch with the 2020 theorem is that the convex program, while
     exact, has about (n/r)^r variables — exponential in the rank of
     the data."
  2. "In 2024 Kim and Pilanci showed that if you keep only O(log n)
     randomly sampled hyperplane patterns, the resulting convex
     program's optimum is within a factor of sqrt(log n) of the true
     global optimum."
  3. "That is the first polynomial-in-everything algorithm for
     training regularized ReLU networks with any approximation
     guarantee."

*For a 3-minute version:*
- Same visual, plus:
- One sentence on the stronger corollary: under the same assumptions,
  ordinary SGD/Adam with random init converges to stationary points
  that are sqrt(log n) approximate — so the theorem also speaks to
  why first-order methods work.
- Transition to next finding: "Theory is polynomial. But does any of
  this run on real data?"

**Speaking hook:**
"If you remember one number from this talk, it should be sqrt(log n)."

**One thing audiences often misunderstand:**
The sqrt(log n) is a *relative* approximation factor on the training
loss, not on generalization or test error. Pre-empt with: "This is a
training-loss guarantee; generalization bounds are downstream."

**The one expert follow-up question:**
*"What are the assumptions? This is not a worst-case result, right?"*
— Answer: it assumes the input data is random Gaussian (or satisfies
a similar concentration condition) and that d is sufficiently large.
The paper is explicit that these are average-case guarantees, not
worst-case; the worst-case hardness of Boob et al. 2022 remains.

---

### Finding F5: CRONOS Runs Convex Neural Networks on ImageNet

**Headline (for slide title):**
CRONOS: convex ReLU training at ImageNet scale

**Plain-language summary:**
For most of the convex-reformulation story's history, "practical" meant
downsampled MNIST. The convex programs were mathematically clean but
memory-bound on anything larger. CRONOS, introduced by Feng, Frangella,
and Pilanci in 2023, is the first algorithm to bring convex neural
network training to ImageNet scale. It uses GPU-accelerated ADMM with
exploitation of the low-rank structure of the data-dependent constraint
matrices. The upshot is that on ImageNet and on GPT-2-style language
tasks, CRONOS with alternating minimization matches or beats tuned
Adam — while retaining the global-optimality guarantee of the convex
reformulation.

**Why it is presentation-worthy:**
This finding converts the talk from a theory survey into a claim about
the present. It answers the reasonable worry — "sure, convex, but can
it actually run?" — with a single concrete yes. For a mixed academic
audience, showing that a theoretical programme has produced a working
algorithm that hits a benchmark they recognise (ImageNet) is more
persuasive than any additional theorem.

**Source:** Feng, Frangella & Pilanci, 2023 (user-8652-CRONOS)
**Verified at:** sources/user-8652-CRONOS/content.md, lines 26 and 40
(first algorithm to scale to ImageNet; GPU-accelerated ADMM;
CRONOS-AM matches or beats tuned Adam on ImageNet and IMDb).

**Estimated explanation time:**
- domain_experts: 45 seconds
- mixed_academic: 1 minute

**One-slide treatment plan:**

*For a 90-second version:*
- Title: "CRONOS: convex ReLU training at ImageNet scale"
- Visual: Reference Figure from the CRONOS paper showing CRONOS-AM
  test accuracy on ImageNet vs tuned Adam, or a simple bar chart:
  "Adam (tuned) | CRONOS-AM" with matching or slightly better bars.
  Logos/tags: JAX, RTX-4090, ADMM.
- Key equation (none — this is the engineering slide).
- 3 sentences to say:
  1. "Until 2023 the convex reformulation story was, pragmatically,
     stuck at downsampled MNIST."
  2. "Feng, Frangella, and Pilanci built CRONOS: a GPU-accelerated
     ADMM solver that exploits the low-rank structure of the
     constraint matrices to scale to ImageNet."
  3. "On ImageNet and on GPT-2-style language tasks, CRONOS matches
     or beats a tuned Adam baseline — while keeping the
     global-optimality guarantee."

*For a 3-minute version:*
- Same visual, plus:
- One sentence on CRONOS-AM: alternating minimization extends the
  two-layer guarantee to arbitrary architectures by applying CRONOS
  block-wise.
- Transition to next finding: "The Pilanci-Ergen programme is
  theoretically complete and practically scalable. What is left
  open?"

**Speaking hook:**
"Engineering caught up with theory in 2023."

**One thing audiences often misunderstand:**
CRONOS-AM on multi-layer networks is *not* globally optimal — only
each CRONOS subproblem is. The global guarantee is for the two-layer
primitive. Pre-empt with: "Global optimality is inherited for the
two-layer case; the multi-layer extension is alternating-minimization
and keeps the local guarantees only."

**The one expert follow-up question:**
*"What is the wall-clock comparison to tuned Adam?"* — Answer: on
ImageNet, CRONOS is competitive with tuned Adam after a single,
almost hyperparameter-free run — Adam's tuned number comes after
hyperparameter sweeps that CRONOS does not need.

---

### Finding F6: Is ICNN the Right Convex Class? (Open Question)

**Headline (for slide title):**
Is ICNN the right convex class? (open)

**Plain-language summary:**
The Pilanci-Ergen programme builds convex reformulations for the *training
problem* of ReLU networks. A separate question is which ReLU networks
*represent* convex functions — relevant for optimal transport and
energy-based models, where you want the network itself to be convex as
an input-to-output map. The standard answer has been Input-Convex
Neural Networks (ICNNs). In 2025 Gagneux and colleagues (a non-Stanford
group) proved that ICNNs capture all convex functions expressible by a
one-hidden-layer ReLU network, but from two hidden layers onward there
are convex functions a ReLU network can express that *no* ICNN of the
same architecture can. The "right" convex class for deep ReLU networks
is still unknown.

**Why it is presentation-worthy:**
This is the closing beat — the one that opens the door to what is not
known. It serves three functions at once. First, it signals that the
field is not the private property of a single group; a recent external
check from a different research community has identified a real gap.
Second, it gives the talk an honest open-question ending — the most
credible way to end a survey. Third, it connects to an adjacent
application area (optimal transport) that some audience members will
care about.

**Source:** Gagneux, Massias, Soubies & Gribonval, 2025 (arxiv-2501.03017)
**Verified at:** noted in audience-map Section 3 Result R7 and Section 5
Contested Area 3; external-group ICNN expressivity result.

**Estimated explanation time:**
- domain_experts: 1 minute
- mixed_academic: 1.5 minutes

**One-slide treatment plan:**

*For a 90-second version:*
- Title: "Is ICNN the right convex class? (open)"
- Visual: A Venn-style diagram. Outer set: "convex functions a ReLU
  network can represent." Inner set: "convex functions an ICNN of the
  same architecture can represent." The inner set is strictly smaller,
  with a question mark in the crescent. Label: "Gagneux et al. 2025."
- Key equation: none.
- 3 sentences to say:
  1. "A separate question from 'is training convex' is 'when is the
     network itself a convex map from input to output' — this matters
     for optimal transport."
  2. "The standard answer has been ICNNs, Input-Convex Neural Networks."
  3. "In 2025 Gagneux and colleagues showed that from two hidden layers
     onward, the space of convex functions a ReLU network can
     represent is strictly larger than the ICNN class — so the right
     notion of 'convex ReLU network' is still contested."

*For a 3-minute version:*
- Same visual, plus:
- One sentence on why this matters: in optimal transport, the Brenier
  map is the gradient of a convex function; better convex classes
  give better transport maps.
- One sentence on provenance: "this result is from a non-Stanford
  group, which makes it an honest external check on the programme."
- Transition to next (closing) moment: "So the bridge between convex
  optimization and deep learning is built, it scales, and the edges
  we are still arguing about are here."

**Speaking hook:**
"I want to close with one open question, and one result from a
different research group entirely, because a survey that only cites
one lab is not a survey."

**One thing audiences often misunderstand:**
"Input-convex" refers to the *function represented by* the network,
not to its loss landscape. Pre-empt with: "This is about the map
from x to f(x) being convex — a different question from whether
training f is convex."

**The one expert follow-up question:**
*"Does this contradict the universal-approximation results for
ICNNs?"* — Answer: no. Universal approximation holds in the limit of
unbounded depth and width; the Gagneux result is an exact
architectural-level statement at fixed depth, which is the operational
regime practitioners care about.

---

## Recommended Presentation Sequence

For an 8-minute conference talk with the structure outlined in the
audience map, the findings should appear in the following order:

1. **F1 — Two-layer zero duality gap.** Opens the talk. Sets up the
   bridge between non-convex training and convex optimization, and
   introduces the vocabulary ("duality gap," "strong duality") that
   every subsequent finding uses. Without F1 the rest is nonsense.

2. **F3 — Batch norm is whitening.** Inserted as a 45-second aside
   immediately after F1 to demonstrate, economically, that the
   machinery generalizes to real architectural features. Placed here
   (not later) because it reinforces F1 before the negative result
   lands, and because the speaker does not want the listener's last
   taste of the "convex" story to be a result that expires.

3. **F2 — Depth breaks, parallelism restores.** The climax. Placed in
   the middle third of the talk so the first negative result arrives
   after the listener has bought into the convex programme, which
   maximizes the surprise effect. This is the slide to over-invest
   minutes in.

4. **F4 — Polynomial-time sqrt(log n) approximation.** Placed after
   the dramatic negative result so the talk recovers momentum with a
   fresh positive result. It also pre-empts the natural expert
   objection that "polynomial in n but exponential in r is not
   practical" — an objection that any alert listener will have formed
   during F1.

5. **F5 — CRONOS at ImageNet scale.** Engineering complement to F4.
   The theory-to-practice pairing is stronger when both appear in the
   same minute: "polynomial in theory, ImageNet in practice." F5 can
   be collapsed into a one-sentence mention if time is tight.

6. **F6 — ICNN open question.** Closes the talk on an honest open
   question and introduces an external research group. This is the
   correct closing move for a survey talk because it invites the
   audience into the unfinished work.

**Best talk opener:** F1. The mystery-then-resolution pattern ("you
thought training was non-convex; it isn't") is the strongest opening
move in the corpus and is the only finding that every subsequent one
depends on.

**Climax (most surprising result):** F2. The "depth breaks, parallelism
restores" result is the single most memorable sentence in the corpus
for a mixed academic audience. It is the first *negative* result
(which creates tension), and the rescue is architectural rather than
analytical (which creates satisfaction). This is the slide audiences
will still be thinking about when they leave the room.

**Best closer:** F6. It opens the door to future work, cites an
external group, and ends the survey on the honest note that the
field's most-used convexification trick (ICNNs) is still not known
to be the right one. A survey talk that ends with a clean open
question always outperforms one that ends with a summary of what
was covered.
