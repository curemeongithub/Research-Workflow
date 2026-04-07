# Open Questions — Presentation-Ready Package
## Topic: Duality Gap in Dual Convex Optimization of ReLU Neural Networks

**Talk spec:** 8 minutes, mixed_academic audience, survey goal, conference
talk, Q&A after only. Emphasis on Pilanci and Ergen.

**Selection principle:** These questions are scored on audience-engagement
value, not empirical tractability. A question that is theoretically deep
but takes five minutes to state is useless as a talk closer. A question
that a domain expert finds trivially obvious is useless as a motivator
for a mixed audience. The ten questions below were chosen from a pool
of roughly eighteen candidates identified in the audience map
(Sections 3, 5) and in the source papers' own "future work" and
"open problem" language. Three are marked as talk-integrated
(two closers, one motivator); the remaining seven are Q&A bank material.

**Scoring key (1-5 each):**
- **Exp** = Explicability: can it be stated in 30 seconds without lengthy setup?
- **Sur** = Surprise: does the fact that it is open violate audience expectations?
- **Sta** = Stakes: does answering it matter to the audience's own work?
- **NF**  = Narrative function: clear role as closer, motivator, or bridge?

---

## Part 1: Talk-Integrated Open Questions

Three open questions that earn a place in the 8-minute talk itself. OQ1
is the primary talk closer (Section 7:30-8:00 of the budget). OQ2 is
the motivator at the opening. OQ3 is an optional backup closer if the
speaker wants a sharper technical edge.

---

#### OQ1: What is the right notion of "convex ReLU network" beyond depth two?

**Explicable in one sentence:**
We know how to convexify the *training* of a ReLU network, but the
separate question of which ReLU networks *represent* a convex function
is still unsettled, because from two hidden layers onward there exist
convex functions a ReLU network can express that no Input-Convex
Neural Network of the same architecture can match.

**Composite score:** 4.75/5
**Scores:** Exp 5, Sur 5, Sta 4, NF 5
**Narrative function:** talk_closer
**Recommended placement in talk:** Act 4, final slide (7:30-8:00), after
the CRONOS-at-ImageNet slide.

**Why this is open (and surprising):**
A reasonable listener would assume that after a decade of ICNN papers,
the field has settled on the "right" convex neural-network architecture
for tasks like optimal transport. It has not. Gagneux et al. 2025 show
that the standard ICNN construction is strictly less expressive than
the full space of convex functions implementable by a two-hidden-layer
ReLU network, and the right convex class is still unknown.

**What an expert will say when you raise this:**
"But ICNNs are universal approximators — doesn't that resolve it?"

**Pre-emptive response:**
"Universal approximation holds in the limit of unbounded depth and width.
Gagneux and colleagues are making an exact architectural statement at
fixed depth — which is the regime we actually build networks in. So
the universality result and the expressivity gap are both true, and
they describe different regimes."

**Source confirmation:**
Gagneux, Massias, Soubies, Gribonval 2025
(sources/arxiv-2501.03017/content.md, line 1261, where the authors
explicitly leave the deep-ReLU convex-class characterization to future
work: "Whether the proof for the ReLU case can be adapted to fit this
framework is left to future work.") Audience map Section 3 Result R7
and Section 5 Contested Area 3.

---

#### OQ2: Why does SGD work on a non-convex loss landscape?

**Explicable in one sentence:**
Stochastic gradient descent was designed for convex problems, we run
it on objectives that are provably non-convex, and despite a decade of
theoretical explanations nobody agrees on why it reliably finds good
solutions — this talk argues the answer is that the problem was
secretly convex all along.

**Composite score:** 4.75/5
**Scores:** Exp 5, Sur 4, Sta 5, NF 5
**Narrative function:** motivator
**Recommended placement in talk:** Act 1, opening slide (0:00-1:30),
before the Pilanci-Ergen 2020 theorem.

**Why this is open (and surprising):**
Most of the audience will accept "non-convex training works because of
overparameterization and good initialization" as folk wisdom. What
surprises them is that no one has produced a clean theoretical account
of why that folk wisdom is correct. Pilanci-Ergen 2020 do not resolve
the general question, but they resolve it exactly for regularized
two-layer networks — and the answer is that the landscape was not
really non-convex.

**What an expert will say when you raise this:**
"NTK and mean-field theory already explain SGD in the overparameterized
limit — why do we need a new story?"

**Pre-emptive response:**
"NTK tells us SGD converges; it does not tell us it converges to a
global optimum of the finite-width problem, and in fact Chizat and
Bach showed no feature learning happens in that limit. The convex
reformulation is strictly more general — Dwaraknath, Ergen and Pilanci
2023 show the NTK is a special case of the convex formulation's
multiple-kernel-learning structure with target-independent weights.
So the two views are not in conflict; one contains the other."

**Source confirmation:**
Wang, Ergen & Pilanci 2021 explicitly frame this as the open problem
that motivates their paper: "underlying theoretical reasons for this
remains an open problem"
(sources/arxiv-2110.06482/content.md, line 22).

---

#### OQ3: Is there a polynomial-time algorithm for regularized ReLU training with a *constant-factor* approximation guarantee?

**Explicable in one sentence:**
Kim and Pilanci in 2024 gave the first polynomial-time algorithm for
training regularized ReLU networks with an approximation guarantee,
but the factor they prove is sqrt(log n) — whether the logarithm can
be removed, leaving a constant-factor polynomial-time algorithm, is
open.

**Composite score:** 4.25/5
**Scores:** Exp 4, Sur 4, Sta 4, NF 5
**Narrative function:** talk_closer (backup)
**Recommended placement in talk:** Act 4, final slide (7:30-8:00), as
an alternative closer if the speaker prefers an algorithmic open
problem over the ICNN expressivity question.

**Why this is open (and surprising):**
A listener who has just heard "polynomial-time approximation" will
assume the log factor is cosmetic. It is not — Kim and Pilanci
themselves flag removing it as the first of two open directions in
their conclusion. And the worst-case hardness results of Goel et al.
(2018, 2020) say you *cannot* remove it below some floor, so there is
a genuine theoretical obstacle.

**What an expert will say when you raise this:**
"Isn't this subsumed by worst-case hardness results for ReLU training?"

**Pre-emptive response:**
"The worst-case results of Goel and Klivans show hardness for
unregularized ReLU training without distributional assumptions. Kim
and Pilanci work under average-case assumptions — Gaussian data,
sufficient dimension — and get the sqrt(log n) factor under those.
The open question is whether those average-case assumptions let you
push all the way to a constant factor, not whether the worst-case
barrier can be broken."

**Source confirmation:**
Kim & Pilanci 2024, Conclusion (sources/arxiv-2402.03625/content.md,
line 461): "We hope to improve the work in two ways: First, removing
the logarithmic factor of the approximation would be an important
problem to tackle. Also, extending the theorems to different
architectures, i.e. CNNs, transformers, and multi-layer networks would
be meaningful."

---

## Part 2: Q&A Bank — Anticipated Questions

Seven questions the audience will very likely ask that are not in the
talk itself, organised into three categories: answerable from the
corpus (A), genuinely open (B), and scope questions (C).

---

### Category A: Questions Answerable from This Corpus

#### QA-A1

**Q:** "How does the convex reformulation relate to the Neural Tangent
Kernel? Isn't NTK already the 'convex' story for neural networks?"

**A:** NTK is a strict special case of the convex reformulation.
Dwaraknath, Ergen, and Pilanci in 2023 showed that the convex
reformulation of a gated ReLU network is an instance of Multiple
Kernel Learning, and that the NTK is what you get when the mask
weights are target-independent — the "lazy" regime where no feature
learning happens. Iterative reweighting of the MKL kernel recovers the
full convex optimum, and the gap between the NTK and the true convex
solution is exactly what we call "feature learning." So the two views
are not competing; the convex view contains NTK as a first-order
approximation.

**Source:** Dwaraknath, Ergen, Pilanci 2023 (arxiv-2309.15096)
**Confidence:** HIGH

---

#### QA-A2

**Q:** "You mentioned batch normalization is equivalent to whitening —
does the same result hold for layer norm or group norm?"

**A:** The batch norm paper from Ergen, Sahiner, Ozturkler, Pauly,
Mardani, and Pilanci in 2021 handles batch normalization specifically
by pushing it through the convex-dual lens and recovering a whitened
data matrix. The same machinery in principle works for any
normalization that can be written as a reparametrization of the data
matrix — layer norm, weight norm, and group norm all fit that
template — but the paper does not spell out the extensions. So the
result for batch norm is rigorous and published; the extension to
other normalizations is a natural corollary the community generally
believes but has not written down in equal detail.

**Source:** Ergen et al. 2021 (arxiv-2103.01499), Theorem 2.2
**Confidence:** MEDIUM (direct for BN; inferred for LN/GN)

---

#### QA-A3

**Q:** "What about ResNets? Do skip connections fit into this framework?"

**A:** Yes, and in a clean way. Wang, Ergen, and Pilanci in 2021 show
that ResNets with weight decay fit the parallel-network framework as a
special case — a residual block is structurally a two-branch parallel
network, one branch being the identity. This is actually part of why
the paper interprets modern architectures like ResNeXt, Inception, and
SqueezeNet as empirically successful: they are already built in a
parallel pattern, and that parallel pattern is exactly what restores
strong duality at depth beyond two.

**Source:** Wang, Ergen, Pilanci 2021 (arxiv-2110.06482)
**Confidence:** HIGH

---

#### QA-A4

**Q:** "Can CRONOS actually replace Adam in production? Why is nobody
using it?"

**A:** CRONOS was released in 2023, so the "nobody is using it" part
is mostly a matter of adoption lag. On the technical merits, Feng,
Frangella, and Pilanci report that CRONOS matches or beats tuned Adam
on ImageNet and on GPT-2-style language tasks, and — importantly — it
is essentially hyperparameter-free, so the comparison is "one run of
CRONOS versus a full hyperparameter sweep of Adam." The catch is that
the global-optimality guarantee holds only for the two-layer case;
for the multi-layer networks people actually ship, CRONOS-AM uses
alternating minimization, which is locally optimal per block. So
CRONOS is a serious candidate, not a replacement with an end-to-end
global guarantee for ImageNet-scale ResNets.

**Source:** Feng, Frangella, Pilanci 2023 (user-8652-CRONOS)
**Confidence:** HIGH

---

### Category B: Questions That Are Open Problems

#### QA-B1

**Q:** "What is the actual worst-case complexity? I have heard this
problem is NP-hard."

**Honest answer:**
Both statements are true at once. Goel, Klivans, Manurangsi, and
Reichman proved worst-case hardness for training two-layer ReLU
networks without distributional assumptions, and that hardness has
not been broken. Pilanci and Ergen 2020 give a polynomial-in-n but
exponential-in-data-rank algorithm, which is exact but intractable for
high-dimensional data. Kim and Pilanci 2024 close the gap in a
different direction: under average-case assumptions like Gaussian
data, you can approximate within sqrt(log n) in true polynomial time.
The honest summary is: worst-case hard, average-case tractable, and
this connects to OQ3 — whether the logarithmic factor is necessary is
itself open.

**Source for "this is open":** Kim & Pilanci 2024
(arxiv-2402.03625), Conclusion — the authors explicitly leave
log-factor removal and multi-architecture extension as the two main
open directions.

---

#### QA-B2

**Q:** "Does the zero-duality-gap result say anything about
generalization, or only training loss?"

**Honest answer:**
Only training loss. This is one of the most important things to be
honest about. The Pilanci-Ergen programme characterises the global
optimum of the regularized training objective — it tells you what the
optimal network looks like and how to compute it, but it does not on
its own give a bound on test error. There is a natural hope that the
convex-reformulation geometry — the polytope structure of the optimal
set, the Lasso interpretation — will eventually feed into a
generalization bound, and there is active work in that direction, but
the field has not yet produced a clean theorem of the form "zero
duality gap implies generalization bound X." It is a genuine open
direction, and arguably the most important one.

**Source for "this is open":** Absence in the corpus; the audience map
lists generalization as outside the scope of all surveyed papers.
Audience map Section 8 does not rank any generalization-focused paper
as Essential precisely because none exist.

---

#### QA-B3

**Q:** "Does this extend to transformers?"

**Honest answer:**
Not in a published, global-optimality sense. Kim and Pilanci 2024
explicitly list transformers among the architectures they want to
extend their results to, which is an honest flag that the extension
does not yet exist. The attention mechanism is not ReLU, it is softmax,
and softmax is not piecewise linear, which is the structural property
the whole convex-reformulation machinery relies on. There is
preliminary work from a couple of groups on attention reformulations,
but as of the corpus I reviewed there is no theorem of the form
"transformer training is a convex program in disguise." It is probably
the biggest single open direction in this area.

**Source for "this is open":** Kim & Pilanci 2024
(arxiv-2402.03625), Conclusion, line 461 ("extending the theorems to
different architectures, i.e. CNNs, transformers, and multi-layer
networks would be meaningful").

---

### Category C: Scope Questions

#### QA-C1

**Q:** "Why didn't you cover the mean-field / Wasserstein gradient flow
story? That's the other big approach to non-convex training theory."

**Deflection:** You are right that mean-field theory is the other
major theoretical framework and deserves its own talk. I restricted to
the finite-width convex reformulation line precisely because it gives
equivalences at fixed finite width, which is the regime practitioners
actually train in — and I wanted the talk to have a tight narrative
arc rather than survey two frameworks shallowly.

---

#### QA-C2

**Q:** "What about non-ReLU activations — GELU, Swish, Mish? Do any of
these results transfer?"

**Deflection:** The convex reformulation machinery depends
structurally on ReLU being piecewise linear, which lets you enumerate
hyperplane arrangement patterns; smooth activations like GELU and
Swish do not give you that combinatorial structure directly. Bartan
and Pilanci 2021 handle polynomial activations via semidefinite
lifts, which is a distinct branch of the programme, but for the
smooth-activation question there is no analogous clean result yet, so
I left it out rather than give a misleading answer.

---

#### QA-C3

**Q:** "You're showing us mostly Pilanci-Ergen papers. Is there any
independent verification of this line of work?"

**Deflection:** This is a fair challenge and worth taking seriously.
I deliberately included the Gagneux et al. 2025 result on ICNN
expressivity at the end of the talk precisely because it is from a
different research group and offers an external check on the
programme's claims about convex neural networks. The broader
convex-optimization community has also engaged with the results
through ICML and NeurIPS venues, but honest disclosure: the field is
concentrated in Pilanci's group at Stanford and their immediate
collaborators, and more external replication would strengthen it.

---

## Summary Scoring Table

| ID | Title (short) | Exp | Sur | Sta | NF | Composite | Role |
|----|---------------|-----|-----|-----|----|-----------|------|
| OQ1 | Right convex class for deep ReLU | 5 | 5 | 4 | 5 | 4.75 | talk_closer (primary) |
| OQ2 | Why does SGD work at all? | 5 | 4 | 5 | 5 | 4.75 | motivator |
| OQ3 | Constant-factor poly-time training | 4 | 4 | 4 | 5 | 4.25 | talk_closer (backup) |
| QA-A1 | Relation to NTK | 4 | 3 | 4 | 2 | 3.25 | Q&A bank |
| QA-A2 | LayerNorm / GroupNorm extension | 4 | 3 | 3 | 2 | 3.00 | Q&A bank |
| QA-A3 | ResNets and skip connections | 5 | 3 | 4 | 2 | 3.50 | Q&A bank |
| QA-A4 | CRONOS vs Adam in production | 5 | 3 | 4 | 2 | 3.50 | Q&A bank |
| QA-B1 | Actual worst-case hardness | 4 | 4 | 4 | 2 | 3.50 | Q&A bank |
| QA-B2 | Generalization bounds | 5 | 5 | 5 | 3 | 4.50 | Q&A bank (highest-stakes open) |
| QA-B3 | Extension to transformers | 5 | 4 | 5 | 3 | 4.25 | Q&A bank |

QA-B2 (generalization) scores high on composite but is deliberately
held out of the talk itself: the talk's narrative arc is about
optimization, and introducing a generalization open question in the
final minute would fracture the closing beat. It is the single
question most likely to be asked in Q&A and the speaker should be
ready to give the honest answer above.

---

## Speaker Notes on Deployment

1. **OQ1 as primary closer.** The ICNN question is the correct closing
   beat for a survey talk because it (a) is recent (2025), (b) comes
   from an external group, (c) connects to optimal transport — an
   adjacent area some listeners will care about — and (d) can be
   stated in a single sentence on the final slide. Use it unless the
   room turns out to be algorithmically focused, in which case OQ3 is
   sharper.

2. **OQ2 as the opening motivator.** This is the question the talk
   exists to answer. Open with it explicitly — the pattern "here is
   what everyone assumes, and here is what Pilanci and Ergen showed is
   actually going on" is the strongest opening move available in this
   corpus.

3. **QA-B2 (generalization) is the question to prepare cold.** It will
   be asked, it is honestly open, and the worst possible answer is
   "that's outside my scope." The written answer above can be spoken
   in under 45 seconds and treats the audience as intelligent.

4. **Do not volunteer OQ3 unless someone asks about complexity.**
   The sqrt(log n) detail is beautiful but burns audience budget. Keep
   it in reserve for Q&A.

5. **All three talk-integrated questions are under 30 seconds spoken
   length.** This is the non-negotiable constraint for an 8-minute
   conference talk: if an open question cannot be stated in the time
   it takes a listener to set down their coffee, it does not belong
   in the talk.
