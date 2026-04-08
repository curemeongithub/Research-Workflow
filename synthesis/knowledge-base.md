---
phase: P7
topic: "Duality Gap in Dual Convex Optimization of ReLU Neural Networks"
talk_spec:
  duration_minutes: 8
  audience: mixed_academic
  goal: survey
  venue: conference_talk
  qa_format: after_only
  emphasise: ["Pilanci, Mert", "Ergen, Tolga"]
generated: "2026-04-08"
architecture_source: synthesis/talk-architecture.md
---

# Knowledge Base: Duality Gap in Dual Convex Optimization of ReLU Neural Networks

**Purpose:** This document is the speaker's private reference for the 8-minute
conference talk. It is the single source of truth for the Beamer script (Phase
P8), the Q&A session, and the speaker's own preparation. Every theorem statement,
equation, and numerical claim here has been verified against the actual source
content.md files. Do not paraphrase entries in this document without re-checking
the source.

---

## Section 1: Master Notation Glossary

All symbols that appear (or are spoken) during the talk. Ordered by first
appearance. LaTeX column gives the compilable macro. "Slide N" refers to the
numbered slide in the approved architecture.

| Symbol | LaTeX | Plain-English Meaning | First Used |
|--------|-------|-----------------------|------------|
| n | `n` | Number of training samples / data points | Slide 4 |
| d | `d` | Input feature dimension | Slide 4 |
| **X** | `\mathbf{X} \in \mathbb{R}^{n \times d}` | Data matrix; rows are individual samples | Slide 4 |
| **y** | `\mathbf{y} \in \mathbb{R}^n` | Label vector (scalar regression / binary classification) | Slide 4 |
| (t)₊ | `(t)_+ = \max\{t,0\}` | ReLU activation applied elementwise | Slide 4 |
| m | `m` | Width of the network (number of hidden neurons) | Slide 4 |
| uⱼ | `\mathbf{u}_j \in \mathbb{R}^d` | Hidden-layer weight vector for neuron j | Slide 4 |
| αⱼ | `\alpha_j \in \mathbb{R}` | Scalar output-layer weight for neuron j | Slide 4 |
| β | `\beta > 0` | Weight-decay regularization strength | Slide 4 |
| P\* | `P^*` | Optimal value of the non-convex primal training problem | Slide 3 |
| D\* | `D^*` | Optimal value of the convex dual (companion) problem | Slide 3 |
| gap | `\text{gap} = P^* - D^*` | Duality gap; measures how much the dual underestimates the primal | Slide 3 |
| Strong duality | — | The condition P\* = D\*, i.e., gap = 0 | Slide 3 |
| m\* | `m^*` | Critical network width at which strong duality holds; bounded by n+1 | Slide 4 |
| Dᵢ | `D_i = \mathrm{Diag}(\mathbf{1}[X\mathbf{u}_i \geq 0])` | ReLU activation pattern matrix: diagonal 0/1 matrix encoding which neurons fire for arrangement i | Slide 4 (speaker notes) |
| P | `P \leq 2r\!\left(\tfrac{e(n-1)}{r}\right)^r` | Number of distinct hyperplane arrangement patterns | Slide 4 |
| r | `r = \mathrm{rank}(\mathbf{X})` | Rank of the data matrix | Slide 4 |
| L | `L` | Depth of the network (number of layers) | Slide 5 |
| K | `K` | Number of parallel branches in a multi-branch architecture | Slide 5 |
| ‖·‖_\* | `\|\cdot\|_*` | Nuclear norm (sum of singular values; = Schatten-1 norm) | Slide 5 (speaker notes) |
| ‖·‖_{S_{2/L}} | `\|\cdot\|_{S_{2/L}}` | Schatten-2/L quasi-norm: (Σᵢ σᵢ^{2/L})^{L/2}; non-convex for L≥3 | Slide 5 (speaker notes) |
| p̃\* | `\tilde{p}^*` | Optimal value of the O(log n)-pattern convex relaxation | Slide 6 |
| C | `C \geq 1` | Universal constant in the Kim-Pilanci approximation bound | Slide 6 |
| ICNN | — | Input-Convex Neural Network: ReLU network constrained to have non-negative hidden weights, so the output is a convex function of the input | Slide 7 |
| SOCP | — | Second-Order Cone Program: a class of convex programs solvable in polynomial time with interior-point methods | Slide 4 (speaker notes) |
| ADMM | — | Alternating Directions Method of Multipliers: the solver underlying CRONOS | Slide 6 |

---

## Section 2: Per-Slide Content Bank

Each slide entry follows the approved architecture in `synthesis/talk-architecture.md`.
The slide number, title, and timing come directly from that document.

---

### Slide 1 — Title: "The Non-Convex Mystery, Solved?" (0:00–0:15, 15 sec)

**Core claim (plain language):**
This is a survey of one of the most surprising theoretical results in deep
learning: ReLU network training, widely assumed to be intractably non-convex,
turns out to be secretly convex in a precise and exploitable sense.

**Key visual (description for Beamer):**
Plain title slide. No images. Two lines of heading, speaker name and affiliation
on a third line, and a small credit line. Optionally: the Stanford seal or
department logo in a corner; an acknowledgement "Work of M. Pilanci, T. Ergen,
and collaborators — Stanford" in 9pt at the foot.

**On-screen text (verbatim, in order):**
1. Duality Gap in Dual Convex Optimization of ReLU Networks
2. The Non-Convex Mystery, Solved?
3. [Speaker Name] · [Affiliation]
4. A survey, 2020–2025
5. (Emphasis: Pilanci & Ergen)

**Speaking notes:**
Say nothing during slide 1 — allow the title to register for 3–4 seconds.
Then speak the first sentence of the Slide 2 speaker notes. The title slide
exists to identify the talk; it has no content to deliver.

**Source citations:** None (title slide only).

**Transition to Slide 2:**
"For the last ten years we have told students that neural network training is
non-convex, and that SGD has no right to work. Here is the question this talk
is going to answer."

---

### Slide 2 — The Mystery (0:15–1:30, 75 sec)

**Core claim (plain language):**
SGD was designed for convex problems. We run it on provably non-convex losses.
It works anyway. No one has a clean theoretical explanation — until 2020.

**Key visual (description for Beamer):**
Single split image, two halves separated by a double-headed arrow with a
question mark label.

- **Left half** (red/orange border): A schematic non-convex loss landscape —
  a wavy 2D surface with several local minima marked as dots. Caption below:
  "non-convex by construction."
- **Right half** (blue/green border): A smooth convex bowl with a single
  global minimum. Caption below: "convex at the global optimum."
- **Arrow label** between them: "?"

This visual is a sketch/placeholder — it should be drawn as a TikZ figure
in the Beamer file (no external image dependency).

**Bullet points for slide body:**
1. SGD was designed for convex problems
2. We run it on provably non-convex losses
3. It works anyway — why?
4. The folk answer: "overparameterization, good init, luck"
5. A better answer exists. It starts in 2020.

*(Note: Five bullets is one over the ≤4 target. The fifth is the narrative
hook and should be displayed last, after a pause. If slide text must be
cut, remove bullet 4 — the "folk answer" is spoken, not read.)*

**Speaking notes:**
Open with the motivator question OQ2 from `analysis/open-questions.md`:
"Stochastic gradient descent was designed for convex problems. We run it on
objectives that are provably non-convex — loss surfaces studded with local
minima and saddle points — and despite a decade of optimization theory telling
us this should not work, we get models that generalize. The folk explanation is
overparameterization plus good initialization plus some luck. I want to argue
today that this explanation is incomplete, and that a much more satisfying
answer exists." Pause. "The answer is that the problem was secretly convex all
along. And the bridge between the non-convex thing you trained and the convex
thing you could have solved is called strong duality." (Source: Wang, Ergen &
Pilanci 2021 frame this as the open problem in `sources/arxiv-2110.06482/content.md`
line 22: "underlying theoretical reasons for this remains an open problem.")

**Source citations:**
- `sources/arxiv-2110.06482/content.md`, line 22 (open-problem framing)
- `analysis/open-questions.md`, OQ2 (motivator question text)

**Transition to Slide 3:**
"To explain what that means I need to define one object — the duality gap
— and then I can state the result that started this programme."

---

### Slide 3 — Duality Gap in 45 Seconds (1:30–2:15, 45 sec)

**Core claim (plain language):**
Every optimization problem has a companion "dual." The dual's optimal value
D\* is always a lower bound on the primal P\*. When P\* = D\*, we say strong
duality holds. For non-convex problems this almost never happens — almost.

**Key visual (description for Beamer):**
A single centred inequality block, large font (18–20pt), with annotations:

```
P*   ≥   D*
```

With horizontal labels: "primal (hard problem)" pointing left, "dual (companion)" pointing right.

Below, two lines:
```
gap = P* − D*
strong duality  ⟺  gap = 0
```

Below that, in 10pt italic:
"For convex problems the gap is zero. For non-convex problems — usually not."

No images. Clean white background. The inequality is the entire slide.

**Bullet points for slide body (these ARE the visual items above):**
1. Every optimization problem has a companion "dual"
2. P\* ≥ D\*  (weak duality, always true)
3. gap = P\* − D\*
4. strong duality ⟺ gap = 0

**Speaking notes:**
"Every optimization problem — what we call the 'primal' — has a companion
problem, called its 'dual,' whose optimal value is always a lower bound on
the original. This is weak duality, and it is always true, even for
non-convex problems. The gap is the difference between the two: how much
the dual underestimates the primal. For convex problems — least squares,
Lasso, linear programming — the gap is zero: the dual and primal touch.
For non-convex problems — almost everything in neural networks — the gap
is usually strictly positive. The reason this talk exists is that for a
specific family of non-convex problems, namely ReLU networks with weight
decay, the gap is also zero. That is the result I want to show you first."

**Source citations:**
- `analysis/audience-map.md`, Section 2 (Lagrangian duality prerequisite entry, "If a slide is needed: YES")
- `analysis/audience-map.md`, Section 7 (notation table: P\*, D\*, duality gap, strong duality)

**Transition to Slide 4:**
"That surprising fact is the result from 2020 I want to show you first."

---

### Slide 4 — The Bridge Is Built: Pilanci & Ergen 2020 (2:15–4:00, 105 sec)

**Core claim (plain language):**
For a two-layer ReLU network with ordinary weight decay, the non-convex
training problem is exactly equivalent to a finite-dimensional convex
program — a second-order cone program. The duality gap is zero, provided
the network is wide enough (m ≥ m\*, and m\* ≤ n+1).

**Key equation (VERIFIED from source):**

The non-convex primal problem (Pilanci & Ergen 2020, equation 2):

```latex
\min_{\{u_j, \alpha_j\}_{j=1}^{m}}
  \frac{1}{2} \left\| \sum_{j=1}^{m} (X u_j)_+ \alpha_j - y \right\|_2^2
  + \frac{\beta}{2} \sum_{j=1}^{m} \left( \|u_j\|_2^2 + \alpha_j^2 \right)
```

This is equivalent (zero duality gap) to the convex program (eqn. 8):

```latex
\min_{\{v_i, w_i\}_{i=1}^{P}}
  \frac{1}{2} \left\| \sum_{i=1}^{P} D_i X (v_i - w_i) - y \right\|_2^2
  + \beta \sum_{i=1}^{P} \left( \|v_i\|_2 + \|w_i\|_2 \right)
\quad \text{s.t.} \quad (2D_i - I_n) X v_i \geq 0,\ (2D_i - I_n) X w_i \geq 0,\ \forall i
```

**Verified at:** `sources/arxiv-2002.10553/content.md`, lines 155–162. Theorem 1
verbatim (line 162): "The convex program (8) and the non-convex problem (2) where
m ≥ m\* have identical optimal values."

**Complexity of the convex program (Remark 3.2, line 172):**
"2dP variables and 2nP linear inequalities where P = 2r(e(n-1)/r)^r, and r =
rank(X). The computational complexity is at most O(d³r³(n/r)^{3r}) using standard
interior-point solvers."

**Bullet points for slide body:**
1. Two-layer ReLU + weight decay is secretly convex
2. Pilanci & Ergen 2020: strong duality holds for m ≥ m\*
3. m\* ≤ n+1 (wider than number of data points = guaranteed zero gap)
4. Finite-dimensional convex program (an SOCP), O((n/r)^r) variables

**Speaking notes:**
"For a two-layer ReLU network with ordinary weight decay — nothing fancy, no
architectural tricks — the non-convex training loss has a finite-dimensional
convex reformulation. The two programs have the same optimal value. The duality
gap is zero."
Walk through the equation: "The first term is the training loss. The second
term is weight decay. The sum is over the m hidden neurons. And (·)₊ is the
ReLU."
State the width condition: "Width m has to be at least some critical value m\*.
That m\* is bounded by n+1 — if the network is wider than roughly the number
of training points you are guaranteed zero gap."
State the implication: "The 'non-convex' problem you were solving with SGD is,
globally, a second-order cone program you could hand to any convex solver. That
is a sentence the textbooks do not tell you."
Pre-empt the complexity objection: "The convex program has (n/r)^r variables —
polynomial in n, exponential in data rank. Clean theoretically, not yet
practical. Hold that thought; we will come back to it." (This IOU is repaid on
Slide 6.)

**Source citations:**
- `sources/arxiv-2002.10553/content.md`, lines 155–162 (Theorem 1 and equations 2, 8)
- `sources/arxiv-2002.10553/content.md`, line 172 (Remark 3.2, complexity)
- `analysis/key-findings.md`, Finding F1

**Transition to Slide 5:**
"Two layers are secretly convex. What happens when you go deeper?"

---

### Slide 5 — THE CLIMAX: Depth Breaks, Parallelism Restores (4:00–5:45, 105 sec)

**Core claim (plain language):**
At L=2, strong duality holds always. At L≥3 for a standard sequential
network, the duality gap is strictly positive — it can be computed in
closed form. But if you rearrange the same network as K independent parallel
branches, strong duality snaps back to zero at any depth.
Architecture, not depth, is the villain.

**Key theorem (VERIFIED from source):**

Wang, Ergen & Pilanci 2021, Theorem 1 (`sources/arxiv-2110.06482/content.md`, line 120):

> "For L ≥ 3, there exists an activation function φ and a L-layer standard
> neural network defined in (3) such that the strong duality does not hold,
> i.e., P > D. In contrast, for any L-layer parallel neural network defined
> in (4) with linear or ReLU activations and sufficiently large number of
> branches, strong duality holds, i.e., P = D."

**Gap formula (for deep linear standard networks):**
The duality gap equals the difference between the Schatten-2/L quasi-norm and
the nuclear norm of X†Y. It is zero only when all singular values of X†Y
are equal. (Source: `sources/arxiv-2110.06482/content.md`, lines 42–44, Contributions bullet 1–3.)

**Parallel network definition (verified, line 115):**
The parallel network output is:
```latex
f_{\theta}^{\mathrm{prl}}(\mathbf{X}) = \mathbf{A}_{L-1} \mathbf{W}_L,
\quad \mathbf{A}_{l,j} = \phi(\mathbf{A}_{l-1,j} \mathbf{W}_{l,j}),
\quad \mathbf{A}_{0,j} = \mathbf{X},\ \forall j \in [m].
```
"In short, we can view the output A_{L-1} from a parallel neural network as a
concatenation of m scalar-output standard neural networks."

**Key visual (description for Beamer):**
Two TikZ network diagrams, side by side.

- **Left diagram** (red): A standard sequential L-layer network, drawn as a
  column of boxes: "Input → Layer 1 → Layer 2 → Layer 3 → Output." Label
  below in red: `P^* > D^*\text{ for }L \geq 3`.
- **Right diagram** (green): A parallel network with K=4 branches, each
  running its own L-layer path from input to a node, then all branch outputs
  summed. Label below in green: `P^* = D^*\text{ for any }L`.
- **Centred punchline** in bold below both diagrams:
  "Architecture, not depth, is the villain."
- **Small citation** beneath: "Wang, Ergen & Pilanci, 2021 (ICLR 2023)."

**Bullet points for slide body:**
1. L = 2: strong duality, always
2. L ≥ 3 standard: strictly positive gap (closed form)
3. L ≥ 3 parallel branches: strong duality restored at any depth
4. Modern architectures (ResNets, Inception, ResNeXt) already have this structure

**Speaking notes:**
Set the expectation explicitly: "You might expect the duality gap to grow
smoothly with depth — deeper networks are 'more non-convex,' so the gap should
get worse the further you go."
Reveal the actual result: "That is not what happens. At L=2 the gap is exactly
zero. At L=3, for a standard deep network with vector output, the gap jumps to
something strictly positive. Wang, Ergen, and Pilanci compute it in closed form
— it is a gap between a Schatten quasi-norm and the nuclear norm, and it is zero
only when all singular values of your label matrix are equal."
Pause. Let it land. Then: "But — and this is the beautiful part — if you
rearrange exactly the same network as K independent parallel branches that sum
at the output, the gap snaps back to zero at any depth."
Pre-empt the "parallel = GPU" confusion: "By parallel I mean architecturally
parallel — not GPU parallelism."
Connect to practice: "And now look at what modern architectures actually do.
Inception, ResNeXt, ResNets with weight decay — these already have parallel
branch structure. The paper suggests this may be part of why they train more
reliably. Architecture, not depth, is the villain."

**Source citations:**
- `sources/arxiv-2110.06482/content.md`, line 120 (Theorem 1, verbatim)
- `sources/arxiv-2110.06482/content.md`, lines 42–44 (Contributions summary)
- `sources/arxiv-2110.06482/content.md`, line 115 (parallel network definition equation 4)
- `analysis/key-findings.md`, Finding F2
- `analysis/audience-map.md`, Section 4, TC2

**Transition to Slide 6:**
"So the bridge holds for two-layer networks, and for parallel networks of any
depth — but the convex program still has that (n/r)^r variables problem. Can
any of this actually run on real data?"

---

### Slide 6 — The Theory Shipped (5:45–7:00, 75 sec)

**Core claim (plain language):**
The (n/r)^r complexity objection is closed. Kim & Pilanci 2024 give the first
polynomial-in-everything approximation guarantee (√(log n) factor). And in
parallel, CRONOS runs convex ReLU training at ImageNet scale, matching tuned
Adam — essentially hyperparameter-free.

**Key equation — approximation bound (VERIFIED from source):**

Kim & Pilanci 2024, Theorem 2.1 (`sources/arxiv-2402.03625/content.md`, line 128):

```latex
p^* \;\leq\; \tilde{p}^* \;\leq\; C\sqrt{\log 2n}\; p^*
```

where C ≥ 1 is a universal constant. This holds with high probability when
only m = O(log n) hyperplane arrangement patterns are sampled.

**Complexity of the approximation algorithm** (Theorem 2.3, line 142):
"There exists a randomized algorithm with O(d³m³) complexity that solves
problem (1) within O(√(log n)) relative optimality bound with high probability."

**Remark on novelty** (Remark 2.2, line 133):
"To the best of our knowledge, the above result provides the first polynomial-
time approximation guarantee for regularized ReLU NNs."

**CRONOS verified claim** (`sources/user-8652-CRONOS/content.md`, lines 26 and 40):
"CRONOS is the first algorithm capable of scaling to high-dimensional datasets
such as ImageNet... CRONOS-AM can obtain comparable or better validation accuracy
than predominant tuned deep learning optimizers on vision and language tasks
with benchmark datasets such as ImageNet and IMDb."

**Key visual (description for Beamer):**
Single horizontal split.

- **Left half — Theory:** Two progress bars (TikZ `\draw[fill]` boxes).
  - Grey bar, wider: "Exact reformulation — O((n/r)^r) variables"
  - Blue bar, shorter: "Random subsample — O(log n) patterns"
  - To the right of the blue bar, the inequality:
    `p^* \leq \tilde{p}^* \leq C\sqrt{\log 2n}\,p^*`
  - Citation: "Kim & Pilanci 2024."

- **Right half — Practice:** A simple bar chart with two bars:
  - "Adam (tuned)" — reference bar
  - "CRONOS-AM" — matching or slightly taller bar
  - Tags/labels: "JAX · RTX-4090 · ADMM · ImageNet"
  - Citation: "Feng, Frangella & Pilanci 2023."

- **Centred headline across the top (bold):** "The theory shipped."

**Bullet points for slide body:**
1. Theory: Kim & Pilanci 2024 — √(log n) approx in true poly time
2. Practice: CRONOS — ImageNet-scale convex ReLU training
3. Matches tuned Adam (and is essentially hyperparameter-free)
4. Global optimality guarantee for the two-layer primitive

**Speaking notes:**
Pay back the IOU from Slide 4: "Remember the (n/r)^r objection I asked you
to hold? Here is what happened next."
State Kim & Pilanci in one sentence: "If you keep only O(log n) randomly
sampled hyperplane arrangement patterns, the resulting small convex program's
optimum is within a factor of √(log n) of the true global optimum with high
probability. That is the first genuinely polynomial-in-everything algorithm
for training regularized ReLU networks with an approximation guarantee."
Pivot to CRONOS: "And in parallel the engineering caught up. CRONOS, from
Feng, Frangella, and Pilanci in 2023, is a GPU-accelerated ADMM solver that
runs convex ReLU training on ImageNet. It matches or beats tuned Adam, with
essentially no hyperparameters to sweep."
Set the hook: "So the bridge is built, extended, and practical. Let me close
with what is still missing."

**Source citations:**
- `sources/arxiv-2402.03625/content.md`, lines 15, 42–44, 128, 133, 142 (Theorem 2.1, 2.3, Remark 2.2)
- `sources/user-8652-CRONOS/content.md`, lines 26, 40 (ImageNet claim; CRONOS-AM result)
- `analysis/key-findings.md`, Findings F4, F5

**Transition to Slide 7:**
"I want to close with one open question, from a research group outside Stanford,
because a survey that only cites one lab is not really a survey."

---

### Slide 7 — Open Question: What Is a "Convex ReLU Network"? (7:00–7:40, 40 sec)

**Core claim (plain language):**
Training is convex (we just established that). A separate question is which
ReLU networks *represent* a convex function as an input-to-output map. ICNNs
were the standard answer; Gagneux et al. 2025 show ICNNs are strictly
less expressive than they needed to be. The right convex class is still open.

**Key finding verified:**
Gagneux, Massias, Soubies & Gribonval 2025 (`sources/arxiv-2501.03017/content.md`,
line 1261): "Whether the proof for the ReLU case can be adapted to fit this
framework is left to future work." (The paper explicitly leaves the deep-ReLU
convex-class characterization open.)

**Key visual (description for Beamer):**
A Venn-diagram drawn in TikZ.

- Large outer ellipse (labelled, at top): "Convex functions a 2-layer ReLU
  network can represent"
- Smaller inner ellipse (labelled, at bottom-left): "Convex functions an
  ICNN of the same architecture can represent"
- Shaded crescent between outer and inner ellipses, labelled: "?" with a
  caption "unknown since depth ≥ 2"
- Small citation below: "Gagneux, Massias, Soubies & Gribonval, 2025
  — non-Stanford group."

**Bullet points for slide body:**
1. Training is convex. But which *networks* represent convex functions?
2. Standard answer: ICNNs (Amos et al. 2017)
3. Gagneux et al. 2025: at depth ≥ 2, ICNN ⊊ ReLU-convex
4. Matters for: optimal transport, energy-based models

**Speaking notes:**
Distinguish the two questions: "I have been talking about convexifying the
training problem. There is a different question — which ReLU networks
*represent* a convex function as a map from input to output? This matters
when you need the network itself to be convex, as in optimal transport or
energy models."
Deliver the open question: "The standard answer has been Input-Convex Neural
Networks. In 2025 Gagneux and colleagues showed that from two hidden layers
onward, there exist convex functions a ReLU network can express that no ICNN
of the same architecture can. The right convex class is still unknown."
Acknowledge the external provenance: "This is from a group outside Stanford,
which I think is worth noting for a survey talk."

**Source citations:**
- `sources/arxiv-2501.03017/content.md`, line 1261 (future-work statement)
- `analysis/key-findings.md`, Finding F6
- `analysis/open-questions.md`, OQ1
- `analysis/audience-map.md`, Section 3 R7, Section 5 Contested Area 3

**Transition to Slide 8:**
"So to summarise where the field stands…"

---

### Slide 8 — Takeaway (7:40–8:00, 20 sec)

**Core claim (plain language):**
Three things determine whether the convex bridge is exact, tractable, and
practical: width, architecture, and whether you accept a logarithmic factor.

**Key visual (description for Beamer):**
A single sentence, 18–20pt, centred, bold:

> ReLU network training was never really non-convex — and whether the hidden
> convex program is exact, tractable, and practically solvable depends on
> three things: width, architecture, and whether you accept a logarithmic factor.

Below it, three spaced words in 14pt bold:

**width | architecture | log n**

No images. No citations. No decorations. One sentence plus three words.

**Bullet points for slide body:**
1. ReLU training is secretly convex
2. width — Pilanci & Ergen 2020, m ≥ m\*
3. architecture — Wang-Ergen-Pilanci 2021, parallel branches
4. log n — Kim-Pilanci 2024, √(log n) approximation
5. Thank you — questions welcome.

**Speaking notes:**
Speak the takeaway sentence at a pace slower than normal; the audience is
reading it as you say it: "ReLU training was secretly convex. Width gives
you the bridge, architecture decides whether it holds at depth, and a
√(log n) factor makes it tractable in practice." (30 words, ~12 seconds
spoken — use this shorter spoken version even though the slide shows the
longer written version.)
Walk the audience down the three bullet points while pointing at the three
words at the bottom: "Width, architecture, log n. That is the talk." Thank
them, stop, hand over to Q&A.
Do not re-raise the open question from Slide 7 — that slide already handled it.

**Source citations:** None (closing summary slide — all material was cited on earlier slides).

**No bridge — this is the end of the talk.**

---

## Section 3: Appendix Slide Content Bank

Four backup slides for Q&A. Each slide is triggered by a specific anticipated
question. Timing is not fixed — these are shown only if the corresponding
question arises.

---

### Backup B1 — Generalisation, Not Training Loss

**Trigger question:**
"Does the zero-duality-gap result say anything about generalization, or only
training loss?" (QA-B2 from open-questions.md — predicted most-likely Q&A question.)

**Core claim:**
The Pilanci-Ergen programme characterises the global optimum of the regularised
training objective only. It gives zero guarantees about test error. This is one
of the most important things to be honest about in a talk on this topic.

**Key visual (TikZ):**
Two boxes connected by an arrow.
- Left box: "training loss — characterised by the convex reformulation"
- Right box: "test error — no theorem yet"
- Arrow label: "active research direction?"

**On-screen text:**
1. Zero duality gap = global optimum of regularised training loss
2. Test error / generalisation bounds: NOT covered by this programme
3. Optimal-set polytope → hope for future generalization bounds
4. The most important honest thing to say about this work

**Speaker script:**
"Only training loss. The Pilanci-Ergen programme characterises the global
optimum of the regularised training objective — it tells you what the optimal
network looks like and how to compute it. It does not on its own give you a
bound on test error. There is a natural hope that the polytope structure of
the optimal set will eventually feed into a generalisation bound, and there
is active work in that direction, but the field has not yet produced a clean
theorem of the form 'zero duality gap implies generalisation bound X.' It is
a genuine open direction — arguably the most important one."

**Source citations:**
- `analysis/open-questions.md`, QA-B2

---

### Backup B2 — Does This Extend to Transformers?

**Trigger question:**
"Does this extend to transformers?" (QA-B3 — second-most-likely Q&A question.)

**Core claim:**
Not in a published, global-optimality sense. The machinery depends structurally
on ReLU being piecewise linear. Transformers use softmax attention, which is
smooth, and the whole hyperplane-arrangement enumeration machinery does not
carry over. Kim & Pilanci 2024 explicitly flag this as future work.

**Key visual (TikZ):**
Three boxes in a row:
- "ReLU (piecewise linear)" — green checkmark
- "Attention / softmax (smooth)" — red X
- "Polynomial activations (SDP lifts)" — yellow tilde

**On-screen text:**
1. Convex reformulation requires ReLU: piecewise linear
2. Attention (softmax) is smooth — no hyperplane patterns
3. Extension to transformers: explicitly open (Kim-Pilanci 2024 conclusion)
4. Polynomial activations: partial result via SDP (Bartan-Pilanci 2021)

**Speaker script:**
"Not in a published global-optimality sense. The whole convex-reformulation
machinery depends structurally on ReLU being piecewise linear, which is what
lets you enumerate hyperplane arrangement patterns. Attention is softmax, which
is smooth — not piecewise linear — and that structural property does not carry
over. Kim and Pilanci explicitly flag transformers as something they want to
extend to — that honest flag is itself the answer. It is probably the biggest
single open direction in this area."

**Source citations:**
- `sources/arxiv-2402.03625/content.md`, line 461 (Kim-Pilanci conclusion)
- `analysis/open-questions.md`, QA-B3

---

### Backup B3 — Relationship to NTK

**Trigger question:**
"How does the convex reformulation relate to the Neural Tangent Kernel? Isn't
NTK already the 'convex' story for neural networks?" (QA-A1)

**Core claim:**
NTK is a strict special case of the convex reformulation. The convex reformulation
of a gated ReLU network is an instance of Multiple Kernel Learning. The NTK is
what you get when the mask weights are target-independent (the "lazy" regime).
Feature learning is exactly the gap between the NTK and the full convex optimum.

**Key visual (TikZ):**
Nested circles (Venn):
- Small inner circle: "NTK — lazy regime, target-independent mask weights"
- Large outer circle: "Convex reformulation — Multiple Kernel Learning, target-dependent"
- Arrow between the two: "iterative reweighting"
- Caption below: "feature learning = the gap"

**On-screen text:**
1. NTK (Jacot 2018): works at infinite width, no feature learning
2. Convex reformulation: exact at finite width, with feature learning
3. Dwaraknath-Ergen-Pilanci 2023: NTK is a special case of the MKL structure
4. Iterative reweighting: upgrades NTK to the full convex solution

**Speaker script:**
"NTK is a strict special case of the convex reformulation — this is the result
of Dwaraknath, Ergen, and Pilanci in 2023. The convex reformulation of a gated
ReLU network is an instance of Multiple Kernel Learning, and the NTK is what you
get when the mask weights are target-independent — the 'lazy' regime where no
feature learning happens. Iteratively reweighting the MKL kernel recovers the
full convex optimum, and the difference between the NTK and the full convex
solution is exactly what we call feature learning. The two views are not in
conflict; the convex view contains NTK."

**Source citations:**
- `analysis/open-questions.md`, QA-A1
- Dwaraknath, Ergen, Pilanci 2023 (arxiv-2309.15096)

---

### Backup B4 — What About ResNets?

**Trigger question:**
"What about ResNets? Do skip connections fit into this framework?" (QA-A3)

**Core claim:**
Yes, cleanly. A residual block is structurally a two-branch parallel network —
one branch is the identity, one branch is the transformation. Wang, Ergen, and
Pilanci 2021 show this fits the parallel-network framework as a special case.

**Key visual (TikZ):**
A standard residual block diagram redrawn as an explicit two-branch parallel
network:
- Branch 1: identity path (just the input x flowing through unchanged)
- Branch 2: transformed path (Conv → BN → ReLU)
- Both branches summed at the output
- Label: "a ResNet block *is* a parallel network"

**On-screen text:**
1. ResNet residual block = 2-branch parallel network
2. Branch 1: identity; Branch 2: transform
3. Wang-Ergen-Pilanci 2021: ResNets with weight decay ⊆ parallel-network framework
4. Strong duality restored: inherits zero-duality-gap result

**Speaker script:**
"Yes, cleanly. Wang, Ergen, and Pilanci show that a ResNet with weight decay
fits the parallel-network framework as a special case — a residual block is
structurally a two-branch parallel network, with one branch being the identity.
This is actually part of why the paper interprets modern architectures like
ResNeXt, Inception, and SqueezeNet as empirically successful: they were already
built in a parallel pattern, and that parallel pattern is what restores strong
duality at depth beyond two."

**Source citations:**
- `sources/arxiv-2110.06482/content.md` (Wang, Ergen, Pilanci 2021 — parallel architecture definition)
- `analysis/open-questions.md`, QA-A3

---

## Section 4: Q&A Preparation Bank

Full 10-question bank with 2–3 sentence answers, difficulty rating, and
source reference. Difficulty: A = answerable from corpus, B = open problem,
C = scope question.

---

**Q1** (QA-A1)
**Q:** How does the convex reformulation relate to the Neural Tangent Kernel?
Isn't NTK already the 'convex' story for neural networks?
**A:** NTK is a strict special case of the convex reformulation. Dwaraknath,
Ergen, and Pilanci in 2023 showed that the convex reformulation of a gated
ReLU network is an instance of Multiple Kernel Learning, and the NTK is what
you get when mask weights are target-independent — the "lazy" regime with no
feature learning. Iterative reweighting of the MKL kernel recovers the full
convex optimum, and the difference between the NTK and the true convex solution
is exactly what we call feature learning.
**Difficulty:** A
**Source:** arxiv-2309.15096 (Dwaraknath, Ergen, Pilanci 2023); `analysis/open-questions.md` QA-A1

---

**Q2** (QA-A2)
**Q:** You mentioned batch normalization is equivalent to whitening — does the
same result hold for layer norm or group norm?
**A:** The batch norm paper from Ergen et al. 2021 handles BN specifically by
pushing it through the convex-dual lens and recovering a whitened data matrix
(U'^T U' = I, verified at `sources/arxiv-2103.01499/content.md` line 150). The
same machinery in principle works for any normalization that can be written as
a reparametrization of the data matrix, and layer norm, weight norm, and group
norm all fit that template — but the paper does not spell out the extensions.
The result for BN is rigorous and published; the extension to other normalizations
is a natural corollary the community generally believes but has not written down
in equal detail.
**Difficulty:** A (direct for BN; inferred for LN/GN)
**Source:** arxiv-2103.01499, Theorem 2.2; `analysis/open-questions.md` QA-A2

---

**Q3** (QA-A3)
**Q:** What about ResNets? Do skip connections fit into this framework?
**A:** Yes, cleanly. Wang, Ergen, and Pilanci in 2021 show that ResNets with
weight decay fit the parallel-network framework as a special case — a residual
block is structurally a two-branch parallel network, with one branch being the
identity transformation. This is actually part of how the paper interprets the
empirical success of modern architectures like ResNeXt, Inception, and SqueezeNet:
they were already built in a parallel pattern, and that parallel pattern is
exactly what restores strong duality at depth beyond two.
**Difficulty:** A
**Source:** arxiv-2110.06482 (Wang, Ergen, Pilanci 2021); `analysis/open-questions.md` QA-A3

---

**Q4** (QA-A4)
**Q:** Can CRONOS actually replace Adam in production? Why is nobody using it?
**A:** CRONOS was released in 2023, so "nobody is using it" is mostly adoption
lag — the field moves slowly. On technical merits, Feng, Frangella, and Pilanci
report that CRONOS matches or beats tuned Adam on ImageNet and GPT-2-style
language tasks, and the comparison is "one run of CRONOS versus a full
hyperparameter sweep of Adam." The important caveat is that the global-optimality
guarantee holds only for the two-layer case; for multi-layer networks, CRONOS-AM
uses alternating minimization, which is locally optimal per block — not
end-to-end globally optimal.
**Difficulty:** A
**Source:** `sources/user-8652-CRONOS/content.md`, lines 26–44; `analysis/open-questions.md` QA-A4

---

**Q5** (QA-B1)
**Q:** What is the actual worst-case complexity? I have heard this problem is
NP-hard.
**A:** Both statements are simultaneously true and describe different regimes.
Boob et al. 2022 proved worst-case NP-hardness for training a two-layer ReLU
network without distributional assumptions. Pilanci & Ergen 2020 give a
polynomial-in-n but exponential-in-data-rank algorithm, which is exact but
intractable for high-dimensional data. Kim & Pilanci 2024 close the gap under
average-case Gaussian-data assumptions: you can approximate within √(log n) in
true polynomial time. The honest summary: worst-case hard, average-case tractable
under distributional assumptions, and whether the log factor is necessary is
itself open.
**Difficulty:** B (open)
**Source:** `sources/arxiv-2402.03625/content.md`, lines 28–30; `analysis/open-questions.md` QA-B1

---

**Q6** (QA-B2) — **Highest-priority Q&A question. Prepare this one cold.**
**Q:** Does the zero-duality-gap result say anything about generalization, or
only training loss?
**A:** Only training loss. The Pilanci-Ergen programme characterises the global
optimum of the regularised training objective — it tells you what the optimal
network looks like and how to compute it, but it does not on its own give a
bound on test error. There is active work exploring whether the polytope structure
of the optimal set can yield a generalisation bound, but the field has not yet
produced a clean theorem of the form "zero duality gap implies generalisation
bound X." It is arguably the most important open direction in this entire programme.
**Difficulty:** B (open)
**Source:** `analysis/open-questions.md` QA-B2 (absence of any generalisation result in corpus)

---

**Q7** (QA-B3)
**Q:** Does this extend to transformers?
**A:** Not in a published, global-optimality sense. The convex-reformulation
machinery depends structurally on ReLU being piecewise linear — that is what
lets you enumerate hyperplane arrangement patterns, which is the core technique.
Attention uses softmax, which is smooth and does not have that structure. Kim
and Pilanci 2024 explicitly list "extending the theorems to different
architectures, i.e., CNNs, transformers, and multi-layer networks" as a main
open direction in their conclusion. It is probably the biggest single open
direction in this area.
**Difficulty:** B (open)
**Source:** `sources/arxiv-2402.03625/content.md`, line 461; `analysis/open-questions.md` QA-B3

---

**Q8** (QA-C1)
**Q:** Why didn't you cover the mean-field / Wasserstein gradient flow story?
That's the other big approach to non-convex training theory.
**A:** You are right that mean-field theory is the other major theoretical
framework and deserves its own talk. I restricted to the finite-width convex
reformulation line precisely because it gives equivalences at fixed finite width,
which is the regime practitioners actually train in — and I wanted the talk to
have a tight narrative arc rather than survey two frameworks shallowly. The two
views are partly reconciled by Dwaraknath-Ergen-Pilanci 2023, who show the NTK
(a lazy version of the mean-field story) is a special case of the convex MKL
structure.
**Difficulty:** C (scope)
**Source:** `analysis/open-questions.md` QA-C1

---

**Q9** (QA-C2)
**Q:** What about non-ReLU activations — GELU, Swish, Mish?
**A:** The convex reformulation machinery depends structurally on ReLU being
piecewise linear, which lets you enumerate hyperplane arrangement patterns; smooth
activations like GELU and Swish do not give you that combinatorial structure
directly. Bartan and Pilanci 2021 handle polynomial activations via semidefinite
lifts, which is a distinct branch of the programme (arxiv-2101.02429). For
smooth-activation questions there is no analogous clean result yet.
**Difficulty:** C (scope)
**Source:** `analysis/open-questions.md` QA-C2

---

**Q10** (QA-C3)
**Q:** You are showing us mostly Pilanci-Ergen papers. Is there any independent
verification of this line of work?
**A:** This is a fair challenge. I deliberately included the Gagneux et al. 2025
result on ICNN expressivity at the end of the talk precisely because it is from
a different research group (INRIA/Université de Lyon) and offers an external
check on the programme's claims about convex neural networks. The broader
convex-optimization community has engaged with the results through ICML and
NeurIPS venues. But honest disclosure: the field is concentrated in Pilanci's
group at Stanford and their immediate collaborators, and more external replication
would strengthen it.
**Difficulty:** C (scope / honest disclosure)
**Source:** `analysis/open-questions.md` QA-C3

---

## Section 5: Further Reading

Eight papers for audience members who want to go deeper. Ordered from most
accessible to most technical. All paper IDs match `sources/manifest.yaml`.

1. **arxiv-2002.10553** — Pilanci & Ergen (2020). "Neural Networks are Convex
   Regularizers: Exact Polynomial-time Convex Optimization Formulations for
   Two-layer Networks." *The foundational paper: if you read one paper from
   this talk, read this one. Theorem 1 is the entire bridge.*

2. **arxiv-2110.06482** — Wang, Ergen & Pilanci (2021). "Parallel Deep Neural
   Networks Have Zero Duality Gap." ICLR 2023. *The climax of the talk: proves
   that depth breaks strong duality for standard architectures and that parallel
   branches restore it at any depth.*

3. **user-8652-CRONOS** — Feng, Frangella & Pilanci (2023). "CRONOS: Enhancing
   Deep Learning with Scalable GPU Accelerated Convex Neural Networks." *The
   engineering demonstration that convex ReLU training scales to ImageNet;
   the place to start if you want to run convex networks on real data.*

4. **arxiv-2402.03625** — Kim & Pilanci (2024). "Convex Relaxations of ReLU
   Neural Networks Approximate Global Optima in Polynomial Time." ICML 2024.
   *The √(log n) approximation guarantee: the first theoretical result that
   closes the exponential-in-rank gap and gives a polynomial-in-everything
   algorithm.*

5. **arxiv-2103.01499** — Ergen, Sahiner, Ozturkler, Pauly, Mardani & Pilanci
   (2021). "Demystifying Batch Normalization in ReLU Networks." *Shows batch
   normalization is equivalent to whitening the data in the convex program;
   one of the most accessible extension papers.*

6. **arxiv-2202.01331** — Mishkin, Sahiner & Pilanci (2022). "Fast Convex
   Optimization for Two-Layer ReLU Networks: Equivalent Model Classes and Cone
   Decompositions." ICML 2022. *The SCNN algorithm: the predecessor to CRONOS
   and the paper that made convex ReLU training algorithmically practical at
   moderate scale.*

7. **arxiv-2501.03017** — Gagneux, Massias, Soubies & Gribonval (2025).
   "Convexity in ReLU Neural Networks: beyond ICNNs?" *The external-group check
   raised at the end of the talk; establishes that ICNNs are strictly less
   expressive than the full set of convex functions a deep ReLU network can
   represent.*

8. **arxiv-2309.15096** — Dwaraknath, Ergen & Pilanci (2023). "Fixing the NTK:
   From Neural Network Linearizations to Exact Convex Programs." *Reconciles
   the NTK and convex-reformulation views; essential reading if you come from
   a kernel-methods background and want to understand how the two frameworks
   relate.*

---

## Section 6: Speaker Notes Summary

A single page of bullet-point reminders for the speaker to read 30 minutes
before the talk. These are meta-notes — they do not contain content, only
execution guidance.

### Timing Cues

- **Slide 1 (0:00–0:15):** 15 seconds. Say nothing on screen. Begin speaking
  the bridge line. If you run over on any subsequent slide, cut the bridge line
  and go straight to the next slide.
- **Slide 2 (0:15–1:30):** 75 seconds. This is the longest single slide. If
  you feel yourself rushing, it means you are on track.
- **Slide 3 (1:30–2:15):** 45 seconds. This is the shortest content slide.
  Do not linger.
- **Slide 4 (2:15–4:00):** 105 seconds = 1:45. The only slide with an equation
  on screen. Walk through the equation in plain language; do not read symbols.
- **Slide 5 (4:00–5:45):** 105 seconds = 1:45. The climax. Pause after "the
  gap jumps to something strictly positive." The pause should be long enough
  to feel slightly uncomfortable.
- **Slide 6 (5:45–7:00):** 75 seconds. Two-part slide. Left half (theory) gets
  35 seconds; right half (CRONOS) gets 40 seconds.
- **Slide 7 (7:00–7:40):** 40 seconds. One open question, one external group,
  one sentence. Do not expand.
- **Slide 8 (7:40–8:00):** 20 seconds. Speak slow. Point at "width |
  architecture | log n." Stop.

### Common Mistakes

- **Overexplaining Slide 3.** The duality-gap slide is vocabulary, not content.
  One minute maximum. If a listener looks confused, that is fine — Slide 4 will
  demonstrate it concretely.
- **Not pausing on Slide 5.** The pause is the dramatic device. It communicates
  "this is the important sentence." Without it the climax does not land.
- **Using "parallel" without disambiguation.** Every time you say "parallel
  network" say "architecturally parallel — not GPU parallelism" for the first
  occurrence.
- **Overstating the CRONOS result.** CRONOS is globally optimal only for the
  two-layer case. For multi-layer CRONOS-AM: "locally optimal per block" is
  the correct phrase. Do not say "globally optimal for ImageNet."
- **Skipping the IOU repayment on Slide 6.** The "(n/r)^r objection I asked
  you to hold" sentence is load-bearing — it links back to Slide 4 and
  completes the arc. Do not cut it.

### Audience Interaction Points

- **After Slide 2:** Watch the audience. If there are nodding heads when you
  say "the problem was secretly convex all along," you have buy-in. If there are
  furrowed brows, spend one extra sentence on Slide 3 before moving on.
- **During Slide 5:** Make eye contact when you say "Architecture, not depth,
  is the villain." This is the sentence people will repeat in the hallway.
- **Before Slide 8:** Slow down noticeably as you move from Slide 7 to Slide 8.
  The audience needs to feel the landing.

### Pre-Emption Reminders

- "(n/r)^r is intractable, hold that thought" — say it on Slide 4, pay it back
  on Slide 6.
- "By parallel I mean architecturally parallel, not GPU parallelism" — say it
  on Slide 5, first use of "parallel."
- "Only training loss, not test error" — prepare this answer cold for Q&A; it
  will be asked.
- "Gagneux et al. is not a Pilanci group paper" — say it explicitly on Slide 7
  to pre-empt the "you only cite one lab" challenge.

### The One-Sentence Takeaway (spoken version)

> "ReLU training was secretly convex. Width gives you the bridge, architecture
> decides whether it holds at depth, and a √(log n) factor makes it tractable
> in practice."

Memorise this. It is 30 words, ~12 seconds at conference-talk pace. Say it on
Slide 8 while the longer version is on screen.

### The Single Most Important Thing to Leave Them With

The audience must walk out knowing one fact: the thing everyone calls a
non-convex problem was secretly a convex problem, and the question of *when*
the equivalence holds is fully characterised by three architectural decisions.
If they remember width, architecture, and log n, you have succeeded.
