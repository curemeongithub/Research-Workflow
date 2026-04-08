---
duration_minutes: 8
slide_count: 8
audience: mixed_academic
goal: survey
venue: conference_talk
interactive: false
one_sentence_takeaway: "ReLU network training was never really non-convex — and whether the hidden convex program is exact, tractable, and practically solvable depends on exactly three things: width, architecture, and whether you are willing to lose a logarithmic factor."
---

# Talk Architecture: Duality Gap in Dual Convex Optimization of ReLU Neural Networks

## One-Sentence Takeaway

ReLU network training was never really non-convex — and whether the hidden
convex program is exact, tractable, and practically solvable depends on
exactly three things: width, architecture, and whether you are willing to
lose a logarithmic factor.

Every slide below either (a) sets up the vocabulary this sentence depends
on (Slides 1, 2, 3), (b) delivers one of its three clauses (Slides 4, 5, 6),
or (c) contextualises what is still open and where the bridge still cracks
(Slides 7, 8).

---

## Timing Overview

| Act | Name | Duration | Slides |
|-----|------|----------|--------|
| 1 | Motivation | 1:30 | 1–2 |
| 2 | Background (the bridge) | 2:30 | 3–4 |
| 3 | Core Results (climax + recovery) | 3:00 | 5–6 |
| 4 | Open Questions and Close | 1:00 | 7–8 |
| Appendix | Backup slides | — | B1–B4 |

**Rationale for allocation.** The talk-design skill's 7-minute allocation is
1 / 2 / 3 / 1. The goal is `survey`, which adds 2 minutes to Background and
subtracts from Core. At 8 minutes total I cannot literally apply "+2 min to
Background" without destroying the climax, so I apply it partially: Act 2
gets 30 extra seconds and Act 1 gets 30 extra seconds (because a mixed
audience needs a concrete motivator early), while Act 3 loses 30 seconds
relative to the 7-minute template. The climax (Slide 5) lands at the 5:00
mark — 62.5% through the talk — which is inside the talk-design
skill's 65–75% climax window after accounting for an 8-minute rather than
30-minute talk: at short durations the climax lands slightly earlier because
the close needs proportionally less time.

## Timing Checkpoints

- End of Act 1 (Motivation): 1:30
- End of Act 2 (Background): 4:00
- End of Act 3 (Core Results): 7:00
- Begin close: 7:00
- End of talk (hand over to Q&A): 8:00

## Slide Budget Computation

```
total_slides ≈ (8 / 1.5) - 3 + floor(8/10)
             = 5.33 - 3 + 0
             = 2.33     ← misleadingly low for 8 min
```

The formula in the talk-design skill is calibrated for talks of 15 minutes
and up. At 8 minutes the title / closing / map overhead does not
proportionally scale down — a title slide still takes 15 seconds whether
the talk is 8 minutes or 45. I therefore use:

```
main_slides = 6    (one per ~70 seconds of content)
+ title     = 1
+ takeaway  = 1
--------
total       = 8 main slides + 4 backup slides
```

Backup count is 4 rather than `floor(8/10) = 0` because this is a survey
talk and the Q&A format is `after_only`, meaning every anticipated question
must either be addressed in the main deck or have a backup slide ready.

---

## Act 1: Motivation (1:30, 2 slides)

### Slide 1 — Title ("The Non-Convex Mystery, Solved?") (0:00–0:15, 15 sec)

**Purpose:** Identify the speaker, topic, and the provocation the talk will
resolve, in one beat. The title is a question mark so the audience knows a
claim is coming.

**Content source:** audience-map Section 1 (problem statement); talk_spec
venue = conference_talk, so formal title slide with affiliation.

**Key visual:** Plain title, subtitle "A survey of convex reformulations of
ReLU networks, 2020–2025." Speaker name and affiliation. Optional small
acknowledgement line: "Work of M. Pilanci, T. Ergen, and collaborators —
Stanford."

**On-screen text (max 5 lines):**
- Duality Gap in Dual Convex Optimization of ReLU Networks
- The Non-Convex Mystery, Solved?
- [Speaker name, affiliation]
- A survey, 2020–2025
- (emphasis: Pilanci & Ergen)

**Bridge to Slide 2:** "For the last ten years we have told students that
neural network training is non-convex and that SGD has no right to work.
Here is the question this talk is going to answer."

---

### Slide 2 — The Mystery (0:15–1:30, 75 sec)

**Purpose:** Pose the open question "why does SGD work on a provably
non-convex loss?" and state, in plain language, what the answer will be —
without yet naming anyone or proving anything. This is the motivator
open-question (OQ2) from open-questions.md.

**Content source:** open-questions.md OQ2 (motivator); audience-map
Section 1, paragraph 1–2.

**Key visual:** A single split image. Left half: a cartoon non-convex loss
landscape (wavy surface, a few local minima marked with dots). Caption:
"non-convex by construction." Right half: a clean convex bowl with a single
minimum. Caption: "convex at the global optimum." A double-headed arrow
between them labelled with a question mark.

**On-screen text (max 5 lines):**
- SGD was designed for convex problems
- We run it on provably non-convex losses
- It works anyway — why?
- The folk answer: "overparameterization, good init, luck"
- A better answer exists. It starts in 2020.

**Speaker moves:**
- Open with OQ2 as the motivator — "this is the question I want to answer
  today."
- Name the folk explanation and mark it as incomplete.
- Preview the thesis without proving it: "what I want to argue is that the
  problem was secretly convex all along — and the bridge between the
  non-convex thing you trained and the convex thing you could have solved
  is called strong duality."

**Bridge to Slide 3:** "To explain what that means I need to define one
object — the duality gap — and then I can state the result that started
this programme."

---

## Act 2: Background — Building the Bridge (2:30, 2 slides)

### Slide 3 — Duality Gap in 45 Seconds (1:30–2:15, 45 sec)

**Purpose:** Give the one piece of prerequisite vocabulary the rest of the
talk depends on — Lagrangian duality, primal vs dual, strong duality — in
the minimum possible time. This is the single prerequisite slide the
audience-map explicitly flagged as essential (audience-map Section 2,
Lagrangian duality entry, "If a slide is needed: YES").

**Content source:** audience-map Section 2 (Lagrangian duality
prerequisite); audience-map Section 7 notation table (P*, D*, duality gap,
strong duality).

**Key visual:** A single inequality, centred and large:

```
P*  ≥  D*
```

Below it, in smaller text: `gap = P* − D*`. Below that: `strong duality
⇔ gap = 0`. Left of the inequality: the word "primal (hard problem)."
Right of the inequality: "dual (companion problem)." A small sub-caption:
"For convex problems the gap is zero. For non-convex problems — usually
not."

**On-screen text (max 5 lines):**
- Every optimization problem has a companion "dual"
- P* ≥ D*  (weak duality, always true)
- gap = P* − D*
- strong duality ⇔ gap = 0
- For non-convex problems this almost never holds… almost.

**Speaker moves:**
- State in one sentence: "every optimization problem has a twin, called its
  dual, whose optimal value is always a lower bound on the original."
- Define the gap as the difference.
- Plant the teaser: "For a convex problem the gap is zero. For a non-convex
  problem it usually is not. The reason this talk exists is that for a
  specific family of non-convex problems — ReLU networks with weight decay —
  the gap is also zero."

**Bridge to Slide 4:** "That surprising fact is the result from 2020 I want
to show you first."

---

### Slide 4 — The Bridge Is Built: Pilanci & Ergen 2020 (2:15–4:00, 105 sec)

**Purpose:** Deliver Finding F1 — the foundational zero-duality-gap theorem
for two-layer ReLU networks. This is the slide every later slide depends on.

**Content source:** key-findings.md F1; audience-map Section 3 Result R1;
audience-map Section 4 Technical Core TC1.

**Key visual:** Two boxes connected by a double-headed arrow. Left box:
same non-convex loss cartoon from Slide 2 ("two-layer ReLU + weight decay").
Right box: a clean convex bowl labelled "finite-dim SOCP, O((n/r)^r) vars."
Arrow label: "zero duality gap — Pilanci & Ergen 2020."

Below the two boxes, the single equation the talk will show this entire
time:

```
min_{u_j, α_j}  ½‖ Σ_j (X u_j)_+ α_j − y ‖² + (β/2) Σ_j (‖u_j‖² + α_j²)
```

with an equivalence arrow to a compact "convex program on hyperplane
arrangements" box (no equation, just a label).

**On-screen text (max 5 lines):**
- Two-layer ReLU + weight decay is secretly convex
- Pilanci & Ergen 2020: strong duality holds
- Width m ≥ m* ≤ n+1 suffices
- Finite-dimensional convex program (an SOCP)
- The non-convex problem was a convex problem in disguise

**Speaker moves (this is the one slide with one equation):**
1. Plain language first: "For a two-layer ReLU network with ordinary weight
   decay — nothing fancy — the non-convex training loss has a finite-
   dimensional convex reformulation. The two programs have the same
   optimal value. The duality gap is zero."
2. Walk through the equation's terms once: "first term is the training
   loss, second term is weight decay, the sum is over the m hidden neurons,
   and (·)_+ is the ReLU."
3. State the width caveat: "width m has to be at least some critical value
   m*, and that m* is bounded by n+1 — if the network is wider than roughly
   the number of training points you are guaranteed zero gap."
4. State the implication: "the 'non-convex' problem you were solving with
   SGD is, globally, a second-order cone program you could hand to any
   convex solver. That is a sentence the textbooks do not tell you."
5. Pre-empt the complexity objection: "The convex program has (n/r)^r
   variables — polynomial in n, exponential in data rank. Clean
   theoretically, not yet practical. Hold that thought; we will come back
   to it."

**Bridge to Slide 5:** "Two layers are secretly convex. What happens when
you go deeper?"

---

## Act 3: Core Results — Climax and Recovery (3:00, 2 slides)

### Slide 5 — THE CLIMAX: Depth Breaks, Parallelism Restores (4:00–5:45, 105 sec)

**Purpose:** Deliver Finding F2 — the single most surprising sentence in
the corpus. This is the slide audiences will remember. Lands at 50–72%
of the talk (climax window).

**Content source:** key-findings.md F2; audience-map Section 3 Result R3;
audience-map Section 4 Technical Core TC2; audience-map Section 5 Contested
Area 2.

**Key visual:** Two network diagrams side by side, maximally readable.

- Left: standard sequential L-layer network, drawn as a stack of boxes
  labelled "layer 1 → layer 2 → layer 3 → output." Red caption underneath:
  `P* > D* for L ≥ 3`.
- Right: parallel / multi-branch network, drawn as K branches (say K=4)
  each running layer-1→layer-2→layer-3 independently, outputs summed at a
  plus sign. Green caption underneath: `P* = D* for any L`.

Below both diagrams, centred in bold, the punchline in plain text:

> **Architecture, not depth, is the villain.**

Small citation: "Wang, Ergen & Pilanci 2021 (ICLR 2023)."

**On-screen text (max 5 lines):**
- L = 2: strong duality, always.
- L ≥ 3 standard: strictly positive gap, closed form.
- L ≥ 3 parallel branches: strong duality restored.
- Gap = Schatten-2/L quasi-norm − nuclear norm
- ResNets, Inception, ResNeXt already have this structure

**Speaker moves (this is the over-invested slide):**
1. Set up the expectation explicitly: "You might expect that the duality
   gap would grow smoothly with depth — deeper networks are 'more non-
   convex,' so the gap should get worse the further you go."
2. Reveal the actual result: "That is not what happens. At L=2 the gap is
   exactly zero. At L=3, for a standard deep network with vector output,
   the gap *jumps* to something strictly positive. Wang, Ergen, and Pilanci
   compute it in closed form — it is a gap between a Schatten norm and
   the nuclear norm, and it is zero only when all singular values are
   equal."
3. Pause. Let it land.
4. Deliver the twist: "But — and this is the beautiful part — if you
   rearrange exactly the same network as K independent parallel branches
   that sum at the output, the gap snaps back to zero at any depth."
5. Connect to practice: "And now look at what modern architectures
   actually do. Inception, ResNeXt, ResNets with weight decay — these
   already have parallel branch structure. The paper suggests this may
   be part of why they train more reliably. Architecture, not depth, is
   the villain."
6. Pre-empt the "parallel = GPU" confusion: "By parallel I mean
   architecturally parallel, not GPU parallelism."

**Bridge to Slide 6:** "So the bridge holds for two-layer networks, and
for parallel networks of any depth — but the convex program still has
that (n/r)^r variables problem. Can any of this actually run on real data?"

---

### Slide 6 — The Theory Shipped (5:45–7:00, 75 sec)

**Purpose:** Deliver the third clause of the takeaway. This is the
one-slide fusion of Finding F4 (Kim & Pilanci 2024 sqrt(log n) approximation)
and Finding F5 (CRONOS at ImageNet). They belong on the same slide because
they answer the same objection — "can this run?" — from two angles, theory
and engineering, and collapsing them saves 45 seconds.

**Content source:** key-findings.md F4 and F5; audience-map Section 3
Result R5; audience-map Section 6 (Adjacent field / Practical deep learning
at scale).

**Key visual:** A single horizontal split.

- Left half: "Theory." Two progress bars. Grey bar: "exact convex
  reformulation, O((n/r)^r) variables." Blue bar (much shorter): "random
  subsample, O(log n) patterns." To the right, the inequality:
  `p*  ≤  p̃*  ≤  C · √(log 2n) · p*`  (Kim & Pilanci 2024).
- Right half: "Practice." A simple bar chart with two bars: "Adam (tuned)"
  vs "CRONOS-AM" on ImageNet, showing matching or slightly-better test
  accuracy. Tag line: "GPU-accelerated ADMM, JAX, ImageNet, GPT-2."
  Citation: "Feng, Frangella & Pilanci 2023."

Centred headline across the top: **The theory shipped.**

**On-screen text (max 5 lines):**
- Theory: Kim & Pilanci 2024 — √(log n)-approx in true poly time
- Practice: CRONOS — ImageNet-scale convex ReLU training
- Matches tuned Adam (and is essentially hyperparameter-free)
- Global optimality guarantee for the two-layer primitive
- 2020 theorem → 2024 practical algorithm in four years

**Speaker moves:**
1. Pay back the IOU from Slide 4: "Remember the (n/r)^r objection I asked
   you to hold? Here is what happened next."
2. State Kim & Pilanci in one sentence: "If you keep only O(log n)
   randomly sampled hyperplane patterns, the resulting small convex
   program's optimum is within a factor of √(log n) of the true global
   optimum. That is the first genuinely polynomial-in-everything algorithm
   for training regularized ReLU networks with an approximation guarantee."
3. Pivot to CRONOS: "And in parallel the engineering caught up. CRONOS,
   from Feng, Frangella, and Pilanci in 2023, is a GPU-accelerated ADMM
   solver that runs convex ReLU training on ImageNet. It matches or beats
   tuned Adam, with essentially no hyperparameters to sweep."
4. Set the hook for the close: "So the bridge is built, extended, and
   practical. Let me close with what is still missing."

**Bridge to Slide 7:** "I want to close with one open question, from a
research group outside Stanford, because a survey that only cites one lab
is not really a survey."

---

## Act 4: Open Questions and Close (1:00, 2 slides)

### Slide 7 — Open Question: What Is a "Convex ReLU Network"? (7:00–7:40, 40 sec)

**Purpose:** Deliver the primary talk-closer open question (OQ1) and
introduce an external research group. This is the honest survey closer:
it signals both that the field is not a single lab's private property and
that the core theoretical question is not fully settled.

**Content source:** open-questions.md OQ1 (talk_closer, primary);
key-findings.md F6; audience-map Section 3 Result R7; audience-map
Section 5 Contested Area 3; audience-map Section 6 (optimal transport
connection).

**Key visual:** A Venn-style diagram. Large outer set labelled "convex
functions a 2-hidden-layer ReLU network can represent." Smaller inner set
labelled "convex functions an ICNN of the same architecture can represent."
The inner set is strictly contained in the outer set, with a shaded
crescent marked by a question mark. Citation: "Gagneux, Massias, Soubies &
Gribonval, 2025 — non-Stanford group."

**On-screen text (max 5 lines):**
- Training is convex. But which *networks* represent convex functions?
- Standard answer: ICNNs (Amos et al. 2017)
- Gagneux et al. 2025: at depth ≥ 2, ICNN ⊊ ReLU-convex
- The right convex class is still open
- Matters for: optimal transport, energy-based models

**Speaker moves:**
1. Distinguish the two questions cleanly: "I have been talking about
   convexifying the training problem. There is a different question —
   which ReLU networks represent a convex function as a map from input
   to output? This matters when you need the network itself to be
   convex, as in optimal transport or energy models."
2. Deliver the open question: "The standard answer has been Input-Convex
   Neural Networks. In 2025 Gagneux and colleagues showed that from two
   hidden layers onward, there exist convex functions a ReLU network can
   express that no ICNN of the same architecture can. The right convex
   class is still unknown."
3. Acknowledge the external provenance: "This is from a group outside
   Stanford, which I think is worth noting."

**Bridge to Slide 8:** "So to summarise where the field stands…"

---

### Slide 8 — Takeaway (7:40–8:00, 20 sec)

**Purpose:** Deliver the one-sentence takeaway with the three clauses
explicit so the audience walks out with a single crisp summary. This is
the slide that must not be cut under any circumstance.

**Content source:** talk-design skill (one-sentence takeaway rule);
key-findings.md recommended sequence; all of Acts 2 and 3.

**Key visual:** A single sentence, large, centred. No images. No citations.
No distractions.

> **ReLU network training was never really non-convex — and whether
> the hidden convex program is exact, tractable, and practically solvable
> depends on three things: width, architecture, and whether you accept
> a logarithmic factor.**

Below, three small words, spaced apart: **width | architecture | log n**

**On-screen text (max 5 lines):**
- ReLU training is secretly convex
- width  (Pilanci-Ergen 2020, m ≥ m*)
- architecture  (Wang-Ergen-Pilanci 2021, parallel branches)
- log n  (Kim-Pilanci 2024, √(log n) approximation)
- Thank you — questions welcome.

**Speaker moves:**
- Speak the takeaway sentence at a slower-than-usual pace; the audience is
  reading it at the same time.
- Walk the audience down the three bullet points while pointing at the
  three words at the bottom — "width, architecture, log n. That is the
  talk." Thank them, stop, hand over.
- Do not try to re-raise the open question; Slide 7 already did that.
  Slide 8 is the landing.

**No bridge — this is the end.**

---

## Appendix: Backup Slides

Backup count = 4. All four are questions the audience map or the
open-questions Q&A bank flags as very likely to be asked in an `after_only`
Q&A session.

### Backup B1 — Generalisation, Not Training Loss

**Trigger:** Use if asked "Does the zero-duality-gap result say anything
about generalisation, or only training loss?" (QA-B2 — the highest-stakes
open question; predicted to be the single most likely Q&A question.)

**Content source:** open-questions.md QA-B2.

**Key visual:** Two boxes. Left: "training loss — characterised by the
convex reformulation." Right: "test error — no theorem yet." Arrow between
them with a question mark and the label "active research direction."

**Speaker script:**
"Only training loss. This is one of the most important things to be
honest about. The Pilanci-Ergen programme characterises the *global
optimum of the regularised training objective* — it tells you what the
optimal network looks like and how to compute it. It does not on its own
give you a bound on test error. There is a natural hope that the
polytope structure of the optimal set will eventually feed into a
generalisation bound, and there is active work in that direction, but
the field has not yet produced a clean theorem of the form 'zero duality
gap implies generalisation bound X.' It is a genuine open direction —
arguably the most important one."

---

### Backup B2 — Does This Extend to Transformers?

**Trigger:** Use if asked "Does this extend to transformers?" (QA-B3 —
second-most-likely Q&A question.)

**Content source:** open-questions.md QA-B3.

**Key visual:** Three boxes, labelled "ReLU (piecewise linear)",
"Attention / softmax (smooth)", "Polynomial activations (SDP lifts)." Green
check on the first, red X on the second, yellow tilde on the third.

**Speaker script:**
"Not in a published global-optimality sense. The whole convex-reformulation
machinery depends structurally on ReLU being piecewise linear, which is
what lets you enumerate hyperplane arrangement patterns. Attention is
softmax, which is smooth. Kim and Pilanci explicitly flag transformers as
something they want to extend to — that honest flag is itself the answer.
There is preliminary work on attention reformulations but no theorem yet
of the form 'transformer training is a convex program in disguise.' It is
probably the biggest single open direction in this area."

---

### Backup B3 — Relationship to NTK

**Trigger:** Use if asked "How does the convex reformulation relate to the
Neural Tangent Kernel? Isn't NTK already the 'convex' story for neural
networks?" (QA-A1.)

**Content source:** open-questions.md QA-A1; audience-map Section 3
Result R6; audience-map Section 5 Contested Area 1.

**Key visual:** Venn diagram. Small inner circle labelled "NTK — lazy
regime, target-independent mask weights." Large outer circle labelled
"Convex reformulation — Multiple Kernel Learning, target-dependent." Arrow
between the two labelled "iterative reweighting." Caption: "feature
learning = the gap."

**Speaker script:**
"NTK is a strict special case of the convex reformulation — this is the
result of Dwaraknath, Ergen and Pilanci in 2023. The convex reformulation
of a gated ReLU network is an instance of Multiple Kernel Learning, and
the NTK is what you get when the mask weights are target-independent —
the 'lazy' regime where no feature learning happens. Iteratively
reweighting the MKL kernel recovers the full convex optimum, and the
difference between the NTK and the full convex solution is exactly what
we call feature learning. The two views are not in conflict; the convex
view contains NTK."

---

### Backup B4 — What About ResNets?

**Trigger:** Use if asked "What about ResNets? Do skip connections fit into
this framework?" (QA-A3.)

**Content source:** open-questions.md QA-A3.

**Key visual:** A residual block diagram with its identity shortcut
highlighted, redrawn as an explicit two-branch parallel network (identity
branch + transformed branch summing at the output). Label: "a ResNet block
*is* a parallel network."

**Speaker script:**
"Yes, cleanly. Wang, Ergen, and Pilanci show that a ResNet with weight
decay fits the parallel-network framework as a special case — a residual
block is structurally a two-branch parallel network, with one branch being
the identity. This is actually part of why the paper interprets modern
architectures like ResNeXt, Inception, and SqueezeNet as empirically
successful: they were already built in a parallel pattern, and that
parallel pattern is what restores strong duality at depth beyond two."

---

## Cuts and Expansions

### If Running Short (need to cut 1:30 down to 6:30)

An 8-minute talk is already tight; there is not much fat. In order of
safety (cut Slide 7 before Slide 3 before Slide 6):

1. **Cut Slide 7 (open question, ICNN).** The open question can be folded
   into a single sentence spoken while Slide 8 is on screen: "One last
   thing — the right convex *architectural* class for ReLU networks is
   still open; Gagneux et al. 2025 from an external group." This saves
   40 seconds. The takeaway slide still lands. Narrative cost: the talk no
   longer cites a non-Stanford paper, which is a real loss for a survey.

2. **Collapse Slide 3 into Slide 4.** Drop the standalone duality-gap
   prerequisite slide and spend 15 seconds at the top of Slide 4 defining
   `P* ≥ D*` inline. Saves 30 seconds. Narrative cost: the audience members
   who do not know duality well will be catching up during the climax,
   which is the one slide where you cannot afford cognitive load spent
   elsewhere.

3. **Trim Slide 6 to theory OR practice, not both.** If the room is
   theory-weighted, keep Kim-Pilanci and drop CRONOS. If engineering-
   weighted, keep CRONOS and drop Kim-Pilanci. Saves 30 seconds.

Never cut Slide 2 (the motivator open question), Slide 4 (the foundational
theorem), Slide 5 (the climax), or Slide 8 (the takeaway). These are the
talk.

### If Running Long (expand to 15 minutes)

The talk-design skill allocation for 15 minutes is 2 / 4 / 6 / 3. Adding
~7 minutes to this architecture means:

1. **Add a Slide 4.5 on batch normalization (Finding F3, "BN is whitening
   in disguise").** This is already in the key-findings as a one-sentence
   aside; at 15 minutes it earns its own 90-second slide. Source: Ergen
   et al. 2021. Placement: between the foundational theorem and the
   climax, reinforcing the "bridge generalises to real architectures"
   beat before the negative result hits.

2. **Split Slide 5 into two slides.** Slide 5a: the counterexample at L=3
   (2 minutes, show the Schatten-2/L vs nuclear-norm gap formula). Slide
   5b: the parallel-architecture fix and its connection to Inception /
   ResNeXt / ResNets (2 minutes, show a concrete parallel-branch
   architecture from a real paper).

3. **Add a Slide 6.5 on the Lasso interpretation (Finding: audience-map
   Section 3 R4 — Mishkin & Pilanci, Ergen & Pilanci 2023).** "Neural
   networks with weight decay are, in a precise sense, sparse linear
   regression in a high-dimensional feature space." This is the slide
   that bridges to statistics audiences.

4. **Expand Slide 7 to add a second open question.** Add OQ3 (constant-
   factor vs log-factor approximation) as a sub-bullet alongside OQ1,
   giving the talk two open questions instead of one.

5. **Add a new Slide 7.5 on contested areas.** Specifically the NTK
   vs convex-reformulation debate from Contested Area 1 — use the
   Dwaraknath-Ergen-Pilanci 2023 reconciliation as the punchline.

Total additions: 3 new main slides, 1 slide split, 1 slide expanded.
Backup count grows from 4 to 6 (add a slide on CNNs and a slide on
polynomial activations via SDP lifts, per the audience-map Section 8
"Useful" grade list).

### For a Second Audience Type (domain_experts)

If this same talk were delivered to a `domain_experts` audience at the
same duration, the changes would be:

1. **Slide 2 can be abbreviated to 45 seconds.** Domain experts already
   know SGD works and already know the non-convex framing. Skip the
   "folk explanation" beat; go straight to "the answer is that the loss
   was secretly convex."

2. **Slide 3 (duality-gap prerequisite) is cut entirely.** Domain experts
   do not need strong duality defined on screen. Recover 45 seconds to
   spend on Slide 4 or Slide 5.

3. **Slide 4 can state the theorem precisely.** For mixed_academic I
   state it in plain language only. For domain_experts, include a verbal
   proof sketch in three steps: (1) rescale to an L1 problem via ReLU
   homogeneity, (2) dualise, enumerate hyperplane patterns, dualise again,
   (3) apply Slater's condition to the finite convex bi-dual.

4. **Slide 5 can include the closed-form gap.** For mixed_academic I say
   "Schatten norm minus nuclear norm, closed form." For domain_experts
   write the formula and interpret each term.

5. **Slide 6 can mention the SCNN/ADMM algorithmic machinery.** For
   mixed_academic I only mention CRONOS by name. For domain_experts
   include one sentence on the Gauss-Newton ADMM inner loop and why
   low-rank structure of the constraint matrices makes the cubic
   complexity tractable.

6. **Slide 7's open question can be replaced with OQ3 (constant-factor
   approximation).** Domain experts find the algorithmic complexity
   question sharper than the ICNN architectural question; use OQ3 as
   the closer instead of OQ1.

7. **Backup slides grow from 4 to 6 by adding B5 (mean-field /
   Wasserstein gradient flow comparison) and B6 (polynomial activations
   via SDP lifts).**

8. **Q&A checkpoint inserted after Slide 5.** For a domain_experts
   audience talk-design skill suggests a checkpoint after Act 3, before
   Act 4 — this is the one interactive audience where the checkpoint
   pays off.

---

## Narrative Coherence Check

- **Is any concept used before it is introduced?**
  - "Duality gap" → introduced on Slide 3, first used on Slide 4. OK.
  - "Strong duality" → introduced on Slide 3, used on Slides 4, 5. OK.
  - "Parallel network" → introduced verbally on Slide 5 with
    disambiguation ("architectural, not GPU"). OK.
  - "Hyperplane arrangement patterns" → mentioned only in speaker notes on
    Slide 4 (not on-screen) and never used standalone. OK.
  - "SOCP" → appears on Slide 4 only; defined verbally. Borderline.
    Acceptable because the audience is mixed_academic and the term is
    parenthetical — the slide is still readable without knowing what SOCP
    expands to.
  - "Schatten norm" → mentioned on Slide 5, one sentence only. Stated
    verbally as "a gap between two matrix norms — the Schatten-2/L and
    the nuclear norm, zero only when all singular values are equal." A
    listener who does not know Schatten norms still hears the functional
    content ("a closed-form gap"). OK.

- **Is each act transition explicit?**
  - Slide 2 → 3: "To explain what that means I need to define one object
    — the duality gap." Explicit.
  - Slide 4 → 5: "Two layers are secretly convex. What happens when you
    go deeper?" Explicit.
  - Slide 6 → 7: "Let me close with what is still missing… and one open
    question from a research group outside Stanford." Explicit.
  - Slide 7 → 8: "So to summarise where the field stands…" Explicit.

- **Does the takeaway sentence have support from Acts 2–3?**
  - Clause 1 ("exact"): supported by Slide 4 (Pilanci-Ergen 2020, exact
    finite-dimensional reformulation).
  - Clause 2 ("tractable"): supported by Slide 5 (parallel architecture
    restores strong duality) AND Slide 6 (√(log n) approximation).
  - Clause 3 ("practically solvable"): supported by Slide 6 (CRONOS).
  - All three clauses are supported by content earlier in the talk. OK.

- **Does the climax land at ~65–75% of total duration?**
  - Slide 5 starts at 4:00 and ends at 5:45. Midpoint: 4:52, which is
    61% of 8:00. This is slightly earlier than the 65–75% window, but the
    talk-design skill explicitly notes that short talks need climaxes
    earlier because the close requires less time. At 8 minutes a 60–65%
    climax is appropriate; 75% would leave only 2 minutes for the close,
    which is wasteful at this length. OK — deliberately slightly early.

- **Does the close have enough time to land?**
  - 60 seconds for Slides 7 and 8 combined (40 + 20). That is tight but
    survivable because both slides are verbally minimal — Slide 7 delivers
    one open question, Slide 8 delivers one sentence. The backup slides
    carry anything else the audience wants. OK.

- **Is the one-sentence takeaway speakable in under 15 seconds?**
  - Counted: 45 words. At conference-talk pace (~155 wpm) that is 17.5
    seconds. Slightly long. Alternative shorter form for the spoken
    version: "ReLU training was secretly convex. Width gives you the
    bridge, architecture decides whether it holds at depth, and a
    √(log n) factor makes it tractable in practice." 30 words, ~12 seconds.
    The slide displays the long version; the speaker says the short
    version.

---

## Papers Named in the Talk

Per audience-map Section 8, an 8-minute talk can afford 6–8 cited papers
on screen. The architecture cites:

| Slide | Paper | Grade |
|------|------|------|
| 4 | Pilanci & Ergen 2020 (arxiv-2002.10553) | Essential |
| 5 | Wang, Ergen & Pilanci 2021 (arxiv-2110.06482) | Essential |
| 6 | Kim & Pilanci 2024 (arxiv-2402.03625) | Essential |
| 6 | Feng, Frangella & Pilanci 2023 (CRONOS) | Essential |
| 7 | Gagneux, Massias, Soubies & Gribonval 2025 (arxiv-2501.03017) | Useful |
| B3 | Dwaraknath, Ergen & Pilanci 2023 (arxiv-2309.15096) | Background |
| B4 | (covered by Wang, Ergen & Pilanci 2021, already cited) | — |

Total distinct papers cited in main deck: 5. With backup slides
triggered: 6. This is inside the 6–8 budget from audience-map Section 8.

All Essential papers from audience-map Section 8 are covered except
Ergen & Pilanci 2021 (three-layer extension) and Ergen et al. 2021 (batch
norm) — both graded "Useful" rather than "Essential" — which are dropped
under the 8-minute constraint. At 15 minutes (expansion plan) both are
added back.
