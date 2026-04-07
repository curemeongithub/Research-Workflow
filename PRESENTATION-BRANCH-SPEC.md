# Oral Presentation Branch — Implementation Specification

> **Purpose:** This document is the complete implementation specification for adding 
> an Oral Presentation branch to the existing Research Pipeline v2. Hand this to an 
> implementation agent along with the full project repository and it has everything 
> needed to make the changes.
>
> **Status:** Ready for implementation.
>
> **Assumes:** The main Research Pipeline v2 is already implemented as described in 
> `ARCHITECTURE-V2.md` and `CLAUDE.md`. All amendments described in the generalised 
> architectural fixes document have also been applied before this branch is added.
>
> **Scope:** This document covers every new file to create, every existing file to 
> edit, all new agents, all new skills, and the exact orchestrator changes required.

---

## Table of Contents

1. [Core Design Decisions and Constraints](#1-core-design-decisions-and-constraints)
2. [Branch Trigger and Selection Mechanism](#2-branch-trigger-and-selection-mechanism)
3. [Shared Phases](#3-shared-phases)
4. [Presentation Branch Phase Map](#4-presentation-branch-phase-map)
5. [New Agent Definitions — Complete Specifications](#5-new-agent-definitions--complete-specifications)
6. [New Skills — Complete Specifications](#6-new-skills--complete-specifications)
7. [Changes to Existing Files](#7-changes-to-existing-files)
8. [New Directory Structure](#8-new-directory-structure)
9. [pipeline-state.yaml Schema Extension](#9-pipeline-stateyaml-schema-extension)
10. [Output Files — What the User Receives](#10-output-files--what-the-user-receives)
11. [Implementation Sprint Plan](#11-implementation-sprint-plan)
12. [Design Decisions Log](#12-design-decisions-log)

---

## 1. Core Design Decisions and Constraints

### 1.1 Why the Branch Diverges at Phase 3, Not Phase 6

The original proposal diverged after Phase 5. The agreed revision diverges after 
Phase 2 (Source Extraction) for the following reason:

Every downstream phase in the presentation branch needs to be **goal-aware from 
the start**. A literature comprehension agent writing for a research paper organises 
content by MECE research themes. A literature comprehension agent writing for a 
30-minute talk organises content around a listener's comprehension journey — what 
they must understand first, what the surprise is, what they can safely not know. 
These are structurally different outputs that cannot be produced by the same agent 
or retrofitted from one to the other.

The same logic applies to the gap/open-questions phase: the research branch scores 
gaps on empirical tractability; the presentation branch scores open questions on 
audience-engagement value. Reusing the research branch's gap analysis as input to 
a presentation would either over-weight tractable-but-boring gaps or require a 
separate re-scoring pass anyway.

Therefore: Phases 1 and 2 are shared (source acquisition and extraction are 
goal-agnostic). Phase 3 onward is branch-specific.

### 1.2 What the Branch Produces

The presentation branch produces exactly three output artifacts for the user:

| File | Description |
|------|-------------|
| `synthesis/talk-architecture.md` | Slide-by-slide outline with per-slide purpose, timing, and content sources. USER REVIEWS AND APPROVES THIS before the knowledge base is written. |
| `synthesis/knowledge-base.md` | The comprehensive reference document: per-slide content bank, speaking notes in prose (speaker voice), Q&A bank (25+ questions with answers), notation glossary, further reading. |
| `synthesis/beamer-script.tex` | Compilable LaTeX Beamer file with speaking notes as comments, all equations typeset, bibliography from manifest.yaml, figure placeholders described. |

The presentation branch does NOT produce: a gap analysis for empirical research, 
testable hypotheses, experimental methodology, experimental results, or a research 
paper. It is entirely oriented toward a human giving a live talk.

### 1.3 User Interaction Points

There are exactly two points where the pipeline stops and waits for the user:

1. **Step 0 (Branch Selection):** Before Phase 1 runs. User provides branch choice 
   plus talk parameters if choosing the presentation branch.

2. **After Phase P6 (Talk Architecture):** The agent produces the slide-by-slide 
   outline and surfaces it. User approves or requests changes. Phase P7 
   (Knowledge Base) does NOT begin until approval is received.

All other phases run autonomously.

### 1.4 Reusability

Phases 1 and 2 artifacts (sources/manifest.yaml and sources/*/content.md) are fully 
reusable. If a user runs the presentation branch first and later wants the research 
pipeline on the same topic, they start at Phase 3 of the research branch without 
re-downloading or re-extracting sources.

### 1.5 Phase Numbering Convention

Presentation branch phases are prefixed with "P" to avoid collision with research 
branch phase numbers (1–16). The orchestrator uses this prefix to route correctly.

| Phase | Name |
|-------|------|
| Phase 1 | Source Acquisition (shared) |
| Phase 2 | Source Extraction (shared) |
| Phase P3 | Audience-Oriented Literature Comprehension |
| Phase P4 | Key Findings Extraction |
| Phase P5 | Open Questions Distillation |
| Phase P6 | Talk Architecture Design ← USER APPROVAL GATE |
| Phase P7 | Knowledge Base Assembly |
| Phase P8 | Beamer Script Generation |

### 1.6 Talk Parameters Captured at Step 0

The following parameters are captured at branch selection and written to 
`pipeline-state.yaml` under the `talk_spec` key. They govern every downstream 
phase in the presentation branch:

```yaml
talk_spec:
  audience: domain_experts | mixed_academic | general
  duration_minutes: 15 | 20 | 30 | 45 | 60
  goal: survey | argue_position | introduce_open_problems | present_result
  emphasis_papers: []     # list of source IDs from manifest to treat in depth
  de_emphasis_papers: []  # list of source IDs to mention briefly or skip
  venue_type: conference_talk | seminar | lecture | defense  # affects formality
  interactive: true | false  # whether Q&A happens during or only after
```

---

## 2. Branch Trigger and Selection Mechanism

### 2.1 Changes to CLAUDE.md — Step 0

Add the following as the very first section of CLAUDE.md, before any other content:

```markdown
## Step 0: Branch Selection (ALWAYS RUNS FIRST — before Phase 1)

Before spawning any phase, ask the user:

"""
Which workflow would you like to run?

  (A) Research Pipeline
      Produces an empirical research paper with literature review,
      gap analysis, hypotheses, experiments, and final paper.
      Full pipeline: Phases 1–16.

  (B) Oral Presentation
      Produces a presentation knowledge base and compilable Beamer
      LaTeX for a talk you will give. No experiments or paper.
      Pipeline: Phases 1–2 (shared), then Phases P3–P8.

For option (B), also provide:
  - Talk duration in minutes (e.g., 20, 30, 45)
  - Audience type: domain_experts / mixed_academic / general
  - Primary goal: survey / argue_position / introduce_open_problems / present_result
  - Venue: conference_talk / seminar / lecture / defense
  - Q&A format: during_talk (interactive) / after_only
  - Any papers from your sources to emphasise (optional)
  - Any papers to de-emphasise or skip (optional)
"""

Wait for user response. Then write to pipeline-state.yaml:

  branch: research | presentation
  talk_spec: { ...parameters if presentation... }

Then proceed to Phase 1.
```

### 2.2 Changes to CLAUDE.md — Branch Routing After Phase 2

In the existing orchestration logic, after Phase 2 completes, add:

```markdown
### After Phase 2 Completes:

Read pipeline-state.yaml → check `branch` field.

IF branch == "research":
  Continue with Phase 3 (literature-comprehension) as currently defined.
  [All existing research pipeline phases run as normal.]

IF branch == "presentation":
  DO NOT run Phase 3 (literature-comprehension) from the research branch.
  DO NOT run Phases 4, 5, 6, 7, or any research branch phase.
  Instead, run the presentation branch phases in order:
    Phase P3 → Phase P4 → Phase P5 → Phase P6 → [USER APPROVAL] → Phase P7 → Phase P8
  See "Oral Presentation Branch" section below for full orchestration logic.
```

### 2.3 Changes to CLAUDE.md — Full Presentation Branch Orchestration

Add a new major section to CLAUDE.md titled "PART C: Oral Presentation Branch":

```markdown
# PART C: Oral Presentation Branch

## Overview

The presentation branch produces a knowledge base and Beamer LaTeX for a 
live academic talk. It runs Phases P3–P8 after the shared Phases 1–2.

## Orchestration

### Phase P3 — Audience-Oriented Literature Comprehension
Spawn agent: `audience-literature`
Input: sources/manifest.yaml, sources/*/content.md, pipeline-state.yaml (talk_spec)
Output: analysis/audience-map.md
Verify: current_phase incremented to P4 in pipeline-state.yaml

### Phase P4 — Key Findings Extraction
Spawn agent: `key-findings`
Input: analysis/audience-map.md, sources/manifest.yaml, pipeline-state.yaml
Output: analysis/key-findings.md
Verify: current_phase incremented to P5

### Phase P5 — Open Questions Distillation
Spawn agent: `open-questions`
Input: analysis/audience-map.md, analysis/key-findings.md, pipeline-state.yaml
Output: analysis/open-questions.md
Verify: current_phase incremented to P6

### Phase P6 — Talk Architecture Design
Spawn agent: `talk-architecture`
Input: analysis/audience-map.md, analysis/key-findings.md, 
       analysis/open-questions.md, pipeline-state.yaml
Output: synthesis/talk-architecture.md

After Phase P6 completes, STOP and surface to user:

"""
=== TALK ARCHITECTURE READY — YOUR REVIEW REQUIRED ===

The proposed slide-by-slide structure is in synthesis/talk-architecture.md.

Please review it and respond with one of:
  "Approve talk architecture" — to proceed to the knowledge base
  Any specific changes — e.g. "Move the CRONOS slide earlier" 
    or "Cut Act 2 to 4 slides" or "Add a slide on batch normalisation"

The knowledge base will not be written until you approve.
===
"""

Wait for user response.
If changes requested: re-run Phase P6 (talk-architecture agent reads the 
  user's feedback as additional input) and surface revised architecture.
If approved: continue.

### Phase P7 — Knowledge Base Assembly
Spawn agent: `knowledge-base`
Input: synthesis/talk-architecture.md, analysis/audience-map.md,
       analysis/key-findings.md, analysis/open-questions.md,
       sources/manifest.yaml, pipeline-state.yaml
Output: synthesis/knowledge-base.md
Verify: current_phase incremented to P8

### Phase P8 — Beamer Script Generation
Spawn agent: `beamer-script`
Input: synthesis/knowledge-base.md, synthesis/talk-architecture.md,
       sources/manifest.yaml, pipeline-state.yaml
Output: synthesis/beamer-script.tex
Verify: file compiles with pdflatex (agent self-checks)

### Final Output
Present to user:
  - synthesis/talk-architecture.md
  - synthesis/knowledge-base.md
  - synthesis/beamer-script.tex

Print:
"""
=== ORAL PRESENTATION BRANCH COMPLETE ===

Three files are ready:

  synthesis/talk-architecture.md  — your approved slide outline
  synthesis/knowledge-base.md     — content bank, speaking notes, Q&A bank,
                                    notation glossary, further reading
  synthesis/beamer-script.tex     — compilable LaTeX Beamer skeleton

The .tex file compiles with: pdflatex beamer-script.tex
Speaking notes are LaTeX comments immediately above each \begin{frame}.
Figure placeholders are described in comments — replace with your actual figures.
===
"""
```

---

## 3. Shared Phases

Phases 1 and 2 run identically in both branches. No changes to:
- `.claude/agents/source-acquisition.md`
- `.claude/agents/source-extraction.md`
- `scripts/phase1_search.py`
- Any Phase 1 or Phase 2 skills

The only addition is that `pipeline-state.yaml` now contains `branch` and 
`talk_spec` fields written at Step 0, which Phase P3 onward reads.

---

## 4. Presentation Branch Phase Map

```
Phase 1:  Source Acquisition        → sources/manifest.yaml           [SHARED]
Phase 2:  Source Extraction         → sources/*/content.md             [SHARED]
                    ↓ branch: presentation
Phase P3: Audience-Oriented         → analysis/audience-map.md
          Literature Comprehension
Phase P4: Key Findings Extraction   → analysis/key-findings.md
Phase P5: Open Questions            → analysis/open-questions.md
          Distillation
Phase P6: Talk Architecture         → synthesis/talk-architecture.md
          Design                    ← USER APPROVAL GATE
Phase P7: Knowledge Base Assembly   → synthesis/knowledge-base.md
Phase P8: Beamer Script Generation  → synthesis/beamer-script.tex
```

---

## 5. New Agent Definitions — Complete Specifications

All new agents live in `.claude/agents/presentation/`.

---

### 5.1 `.claude/agents/presentation/audience-literature.md`

```markdown
---
name: audience-literature
description: Phase P3 (Presentation Branch) — Reads all extracted sources and 
  produces an audience-oriented literature map. Organises knowledge around a 
  listener's comprehension journey rather than MECE research themes. The output 
  is calibrated to the talk_spec parameters (audience type, duration, goal). 
  Output goes to analysis/audience-map.md. READ this file first and foremost.
model: opus
tools: Read, Write, Grep, Glob
permissionMode: acceptEdits
effort: high
color: teal
skills:
  - source-integrity
  - audience-synthesis
  - literature-analysis
---

## Phase P3: Audience-Oriented Literature Comprehension

You are the audience-literature agent. Your job is to read all extracted sources 
and produce a literature map organised around how a live audience will encounter 
and process this material — not around the internal thematic structure of the 
research field.

**Critical difference from the research branch Phase 3:**
The research branch produces a MECE thematic map for a paper reader who can 
re-read. You produce a comprehension journey map for a listener who cannot. 
Every choice — what to include, what to abbreviate, what to call out as surprising 
— is made with the specific audience type and talk duration in mind.

---

## Phase Start — Mark in_progress

```bash
python3 -c "
import yaml, datetime, sys
try:
    with open('pipeline-state.yaml', encoding='utf-8') as f:
        state = yaml.safe_load(f)
except FileNotFoundError:
    print('ERROR: pipeline-state.yaml missing.', file=sys.stderr)
    sys.exit(1)
state.setdefault('phases', {})
state['phases']['P3'] = {
    'status': 'in_progress',
    'output': 'analysis/audience-map.md',
    'started': datetime.datetime.utcnow().isoformat() + 'Z',
}
with open('pipeline-state.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(state, f, default_flow_style=False)
print('[phase-P3] Marked in_progress')
"
```

---

## Read Talk Spec First

```bash
python3 -c "
import yaml
with open('pipeline-state.yaml') as f:
    state = yaml.safe_load(f)
talk_spec = state.get('talk_spec', {})
print('AUDIENCE:', talk_spec.get('audience', 'domain_experts'))
print('DURATION:', talk_spec.get('duration_minutes', 30))
print('GOAL:', talk_spec.get('goal', 'survey'))
print('VENUE:', talk_spec.get('venue_type', 'conference_talk'))
print('INTERACTIVE:', talk_spec.get('interactive', False))
print('EMPHASIS:', talk_spec.get('emphasis_papers', []))
print('DE_EMPHASIS:', talk_spec.get('de_emphasis_papers', []))
"
```

Let the talk_spec govern all decisions:
- **domain_experts**: assume convex optimisation and neural network training are 
  known; spend more time on what is surprising or contested; spend less time on 
  motivation
- **mixed_academic**: assume mathematical maturity but not field-specific knowledge; 
  every piece of notation needs a sentence of introduction; spend more time on 
  motivation and prerequisites
- **general**: rare in this field; assume only calculus and linear algebra; heavy 
  analogy use required

---

## Reading Protocol

Read sources sequentially, same as research Phase 3. After reading each paper:
1. Record: what does this contribute to a listener's understanding?
2. Record: at what point in a talk would this be introduced?
3. Record: time estimate to explain the key insight (domain_experts / mixed_academic)
4. Record: what is surprising or counterintuitive about this result?
5. Drop raw content; carry only structured notes.

For papers in emphasis_papers: read in full depth.
For papers in de_emphasis_papers: record only title, one-line contribution.

---

## Output Format: analysis/audience-map.md

```bash
mkdir -p analysis/
```

The audience map has eight required sections:

---

### Section 1: The Problem Statement

[~400 words]

Written as the opening of a talk — not as a research paper introduction. 
Answer three questions:
1. What question does this field exist to answer?
2. What makes this question hard or surprising?
3. Why should the specific audience type care?

This text is the raw material for the talk's first 2–3 motivation slides. 
Write it in a register appropriate to the audience type from talk_spec.

---

### Section 2: Essential Prerequisites

[~300 words]

The minimum prior knowledge an audience member needs to follow the talk.

For each prerequisite item:
- **Concept**: [name]
- **Assume known for domain_experts**: yes/no
- **Assume known for mixed_academic**: yes/no
- **If not known, one-sentence explanation**: [text]
- **If a slide is needed**: [what it should say]

Do not list more than 8 prerequisite items. If more than 8 exist, collapse 
the less critical ones.

---

### Section 3: The Core Results — A Narrative Arc

[~1200 words]

Each major result as a narrative beat. Ordered chronologically (when the 
result was established) but written as a story of the field's progression.

For each result:

#### Result R[N]: [Short Title]

**Paper:** [Citation key], [year]

**What was known before this:** [1–2 sentences]

**What this result changed:** [2–3 sentences in plain language]

**The surprise or insight:** [1 sentence — what makes this result 
non-obvious or interesting to a listener]

**Estimated explanation time:**
- domain_experts: [N minutes]
- mixed_academic: [N minutes]

**Emphasis status:** [emphasis_paper / standard / de_emphasis — from talk_spec]

**For emphasis papers only — deeper treatment:**
- The key equation or theorem statement (verbatim from source, with citation)
- A concrete example or analogy that makes it tangible
- What a listener might misunderstand and how to pre-empt it
- The one follow-up question an expert would ask

---

### Section 4: The Technical Heart

[~600 words]

The 2–3 results that are mathematically load-bearing for the talk. 
These are the results the speaker must understand deeply, not just describe.

For each:

#### Technical Core TC[N]: [Name]

**Theorem statement (plain language):** [1 sentence]

**Theorem statement (precise):** [from source, with exact citation]

**Key mechanism:** [The single insight that makes this work — 
the "aha" in the proof, the reason it's true]

**Proof sketch in 3 steps or fewer:**
1. [Step]
2. [Step]
3. [Step]

**Concrete example:** [A specific small instance that illustrates the theorem]

**Why this belongs in the talk:** [What understanding this unlocks for the audience]

---

### Section 5: Contested Areas and Live Debates

[~400 words]

Where the field has not settled. Framed as talk content, not as a research 
gap analysis (no scoring rubrics).

For each contested area:

**What is contested:** [1 sentence]
**The two positions:** [Position A] vs [Position B]
**What each side cites:** [Papers on each side]
**Current status:** [Unresolved / trending toward one side / may be ill-posed]
**Presentation value:** [Why mentioning this makes the talk feel current and honest]

---

### Section 6: Connections to Adjacent Fields and Applications

[~300 words]

What this field connects to. Useful for motivation slides and "why should I 
care" Q&A answers.

For each connection:
- **Adjacent field / application**: [name]
- **The connection**: [1–2 sentences]
- **Accessible to**: domain_experts / mixed_academic / general
- **Source if any**: [citation]

---

### Section 7: Notation and Vocabulary Reference

Every piece of notation used in the corpus, defined in one sentence. 
Ordered by when a listener would encounter it in a well-structured talk 
(i.e., simpler concepts first).

| Symbol / Term | Definition | First introduced in |
|---------------|-----------|-------------------|
| $p^*$ | Primal optimal value of the regularised training problem | [PilanciErgen2020] |
| $d^*$ | Dual optimal value | [PilanciErgen2020] |
| $D_j$ | Diagonal matrix encoding ReLU activation pattern $j$ | [PilanciErgen2020] |
| ... | | |

---

### Section 8: Per-Paper Audience Value Assessment

For every paper in sources/manifest.yaml, a one-line assessment of its 
presentation value. Graded:
- **Essential**: The talk cannot proceed without this paper's content
- **Useful**: Deepens understanding; include if time permits
- **Background**: Provides context but can be cited without explanation
- **Skip-for-talk**: Valuable for research but adds complexity without clarity

| Paper | Grade | Reason |
|-------|-------|--------|
| [PilanciErgen2020] | Essential | Foundational result; the talk starts here |
| [WangErgenPilanci2021] | Essential | Central mystery (Table 1); the talk's climax |
| [Feng2023CRONOS] | Useful | Shows practical scalability; good for motivation |
| [Mishkin2022SCNN] | Background | Implementation detail; cite but don't explain |
| ... | | |

---

## Update pipeline-state.yaml

```bash
python3 -c "
import yaml, datetime
with open('pipeline-state.yaml') as f:
    state = yaml.safe_load(f)
existing = state.get('phases', {}).get('P3', {})
state['phases']['P3'] = {
    'status': 'complete',
    'output': 'analysis/audience-map.md',
    'started': existing.get('started', 'unknown'),
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
}
state['current_phase'] = 'P4'
with open('pipeline-state.yaml', 'w') as f:
    yaml.dump(state, f, default_flow_style=False)
"
```

## Git Checkpoint

```bash
git -C "${CLAUDE_PROJECT_DIR:-.}" add analysis/audience-map.md pipeline-state.yaml
git -C "${CLAUDE_PROJECT_DIR:-.}" commit -m "phase-P3-complete: audience-oriented literature map"
```
```

---

### 5.2 `.claude/agents/presentation/key-findings.md`

```markdown
---
name: key-findings
description: Phase P4 (Presentation Branch) — Distils the 5–8 most 
  presentation-worthy findings from the audience map. Each finding is packaged 
  as a self-contained explainable unit with a plain-language headline, visual 
  description, one-slide treatment plan, and speaking hook. Source-lookup limit 5. 
  Output goes to analysis/key-findings.md. READ this file first and foremost.
model: opus
tools: Read, Write, Bash
permissionMode: acceptEdits
effort: high
color: purple
skills:
  - source-integrity
  - source-lookup
  - audience-synthesis
---

## Phase P4: Key Findings Extraction

You are the key-findings agent. Your job is to identify the 5–8 results from 
the literature that are most worth presenting to a live audience, and package 
each one as a presentation-ready unit that the knowledge base and Beamer agents 
can use directly.

**What makes a finding presentation-worthy (in order of importance):**
1. It has a clear surprise or counterintuitive element
2. It can be stated in one sentence a non-specialist can follow
3. It resolves a tension or changes how you think about the problem
4. It connects to what the audience already knows
5. It has a visual or diagrammatic representation

**What does NOT make a finding presentation-worthy:**
- It is merely incremental ("we extended X to Y")
- It requires 10 minutes of setup before it can be stated
- It is purely a technical lemma with no interpretive consequence

---

## Phase Start — Mark in_progress

```bash
python3 -c "
import yaml, datetime, sys
with open('pipeline-state.yaml', encoding='utf-8') as f:
    state = yaml.safe_load(f)
state.setdefault('phases', {})
state['phases']['P4'] = {
    'status': 'in_progress',
    'output': 'analysis/key-findings.md',
    'started': datetime.datetime.utcnow().isoformat() + 'Z',
}
with open('pipeline-state.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(state, f, default_flow_style=False)
print('[phase-P4] Marked in_progress')
"
```

---

## Input

```bash
cat analysis/audience-map.md
cat pipeline-state.yaml  # for talk_spec
cat sources/manifest.yaml  # for emphasis_papers list
```

---

## Selection Protocol

1. Read audience-map.md Sections 3, 4, and 5 fully.
2. Generate 10–12 candidate findings from: core results, technical heart, 
   contested areas.
3. For each candidate, score on presentation-worthiness (1–5):
   - Surprise factor: 1–5
   - Explicability: 1–5 
   - Narrative function: 1–5 (does it work as opener, climax, or closer?)
4. Select the top 5–8. Papers in emphasis_papers from talk_spec automatically 
   qualify; papers in de_emphasis_papers are excluded unless nothing else qualifies.
5. Use source lookups (max 5) to verify that plain-language summaries are 
   faithful to the actual paper content.

Source lookup protocol (same as research branch):
```bash
grep -n "KEYWORD" sources/{PATH}/content.md | head -10
echo "[phase-P4] $(date -u) | query: KEYWORD | result: FOUND/NOT_FOUND" >> diagnostics/source-lookups.log
```

---

## Output Format: analysis/key-findings.md

For each selected finding, produce the following block:

---

### Finding F[N]: [Short Descriptive Title]

**Headline (for slide title):**
[A noun phrase, ≤8 words, suitable as a Beamer frame title]

**Plain-language summary:**
[1 paragraph, ~100 words, no jargon. Written as if explaining to a 
smart non-specialist. This is speaking text for the moment the result 
first appears. Verified against source content via lookup if needed.]

**Why it is presentation-worthy:**
[2–3 sentences. What makes an audience react? Is it surprising? Does it 
resolve a tension? Does it open a question? Be specific.]

**Source:** [Citation key], [Section/theorem number if applicable]
**Verified at:** [sources/PATH/content.md, lines N–M]

**Estimated explanation time:**
- domain_experts: [N] minutes
- mixed_academic: [N] minutes

**One-slide treatment plan:**

*For a 90-second version:*
- Title: [frame title]
- Visual: [exact description of what to show — diagram, equation, table, 
  or figure reference from the paper]
- Key equation (if any): [LaTeX, with source citation]
- 3 sentences to say: [literal text]

*For a 3-minute version:*
- Same visual, plus:
- [Additional content to add when time permits]
- Transition to next finding: [1-sentence bridge]

**Speaking hook:**
[The opening sentence for this slide — the first thing the speaker says 
when this slide appears. Should create a micro-anticipation.]

**One thing audiences often misunderstand:**
[The single most common confusion about this result, and how to pre-empt it 
with one sentence]

**The one expert follow-up question:**
[The question a domain expert in the front row is most likely to ask 
about this finding, and its answer]

---

[Repeat for F2, F3, ... F8]

---

## Narrative Sequencing Recommendation

After all findings are defined, add a section:

### Recommended Presentation Sequence

[List the findings in the order they should appear in the talk, 
with a one-sentence justification for each ordering decision.
Example: "F1 before F3 because F3 requires the rescaling lemma 
which F1 introduces."]

Also note:
- Which finding makes the best talk opener (sets up the mystery)
- Which finding is the climax (the most surprising result)
- Which finding makes the best closer (opens to future work)

---

## Update pipeline-state.yaml

```bash
python3 -c "
import yaml, datetime
with open('pipeline-state.yaml') as f:
    state = yaml.safe_load(f)
existing = state.get('phases', {}).get('P4', {})
state['phases']['P4'] = {
    'status': 'complete',
    'output': 'analysis/key-findings.md',
    'started': existing.get('started', 'unknown'),
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
}
state['current_phase'] = 'P5'
with open('pipeline-state.yaml', 'w') as f:
    yaml.dump(state, f, default_flow_style=False)
"
```

## Git Checkpoint

```bash
git -C "${CLAUDE_PROJECT_DIR:-.}" add analysis/key-findings.md diagnostics/ pipeline-state.yaml
git -C "${CLAUDE_PROJECT_DIR:-.}" commit -m "phase-P4-complete: key findings packaged"
```
```

---

### 5.3 `.claude/agents/presentation/open-questions.md`

```markdown
---
name: open-questions
description: Phase P5 (Presentation Branch) — Extracts and ranks open questions 
  from the literature, scored for audience-engagement value rather than empirical 
  tractability. Each question is packaged with a plain-language statement, 
  narrative placement advice, and a pre-emptive Q&A response. Source-lookup limit 5. 
  Output goes to analysis/open-questions.md. READ this file first and foremost.
model: opus
tools: Read, Write, Grep, Bash
permissionMode: acceptEdits
color: yellow
skills:
  - source-lookup
  - audience-synthesis
---

## Phase P5: Open Questions Distillation

You are the open-questions agent. Your job is to identify the most 
presentation-valuable open questions from the literature and package them 
for use in a talk.

**Critical difference from the research branch Phase 4 (gap analysis):**
The research branch scores gaps on empirical tractability, confidence of 
existence, and feasibility. You score open questions on audience-engagement 
value. A question that is theoretically interesting but takes 10 minutes 
to state is useless for a talk closer. A question that a domain expert 
finds obvious is useless for motivating a mixed audience.

You are NOT producing a research gap analysis. You are producing Q&A 
preparation material and talk-closer content.

---

## Phase Start — Mark in_progress

```bash
python3 -c "
import yaml, datetime
with open('pipeline-state.yaml', encoding='utf-8') as f:
    state = yaml.safe_load(f)
state.setdefault('phases', {})
state['phases']['P5'] = {
    'status': 'in_progress',
    'output': 'analysis/open-questions.md',
    'started': datetime.datetime.utcnow().isoformat() + 'Z',
}
with open('pipeline-state.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(state, f, default_flow_style=False)
print('[phase-P5] Marked in_progress')
"
```

---

## Input

```bash
cat analysis/audience-map.md    # Sections 3 and 5 most relevant
cat analysis/key-findings.md    # To avoid duplicating content
cat pipeline-state.yaml         # For talk_spec (audience, goal)
```

---

## Scoring Dimensions

Score each candidate open question on four dimensions (1–5):

| Dimension | Definition |
|-----------|-----------|
| **Explicability** | Can this question be stated clearly to the target audience in 30 seconds or fewer? (5 = one sentence, no setup; 1 = requires 5+ minutes of setup) |
| **Surprise factor** | Is the fact that this is open surprising? Does it violate what a reasonable person would expect? (5 = shocks domain experts; 1 = obviously hard) |
| **Stakes** | If answered, does it matter to the audience's own work or understanding? (5 = changes how they approach their research; 1 = purely academic) |
| **Narrative function** | Does it serve a clear role in the talk structure? (5 = perfect talk closer or motivator; 1 = interesting but has no obvious placement) |

Composite = (Explicability + Surprise + Stakes + Narrative_Function) / 4

Select the top 8–12 for the output. 

Categorise each as:
- **Talk closer**: Works as the final open question to leave the audience with
- **Motivator**: Works at the start to justify why the field exists  
- **Q&A anticipation**: Not for the talk itself, but will be asked

---

## Source Lookup Protocol

Use up to 5 source lookups to verify that open questions stated in the 
corpus are indeed open (not since resolved) and to find the exact phrasing 
authors use.

```bash
grep -n "open problem\|future work\|remains unknown\|open question" sources/{PATH}/content.md | head -20
echo "[phase-P5] $(date -u) | query: KEYWORD | result: FOUND/NOT_FOUND" >> diagnostics/source-lookups.log
```

---

## Output Format: analysis/open-questions.md

### Part 1: Talk-Integrated Open Questions

For each question that belongs in the talk itself:

---

#### OQ[N]: [Short Title]

**Explicable in one sentence:**
[The 30-second version — must be self-contained for someone who has 
followed the talk up to the point where this question appears]

**Composite score:** [N.N/5]
**Narrative function:** talk_closer | motivator
**Recommended placement in talk:** [Act N, after slide on X]

**Why this is open (and surprising):**
[1–2 sentences. What would a reasonable person have guessed? Why is the 
answer not obvious?]

**What an expert will say when you raise this:**
[The most likely follow-up comment or counter-observation from a 
domain expert in the audience]

**Pre-emptive response:**
[How to acknowledge the expert's point while maintaining the question's 
validity. Literal text, written to be spoken.]

**Source confirmation:**
[Which paper states this is open, with file and line reference]

---

### Part 2: Q&A Bank — Anticipated Questions

Questions the audience will ask that are not in the talk itself.

Organised in three categories:

#### Category A: Questions Answerable from This Corpus

For each:

**Q:** [The question, phrased as an audience member would ask it]

**A:** [The answer, written to be spoken. 3–6 sentences. 
Cites the source paper by author-year, not file path.]

**Source:** [Citation key, verified location]
**Confidence:** HIGH | MEDIUM (HIGH = directly stated; MEDIUM = can be inferred)

---

#### Category B: Questions That Are Open Problems

For each:

**Q:** [The question]

**Honest answer:** 
[Written to be spoken. Acknowledges the question is open, explains 
why it is hard, and ideally connects it to OQ[N] above if relevant.
Never pretends to know the answer. Never deflects with "that's outside 
my scope" without explanation.]

**Source for "this is open":** [Citation, verified]

---

#### Category C: Scope Questions

Questions of the form "why didn't you cover X" or "what about Y."

For each:

**Q:** [The question]
**Deflection:** [A respectful, honest 2-sentence answer that acknowledges 
the question's validity and explains the scope decision.]

---

## Update pipeline-state.yaml

```bash
python3 -c "
import yaml, datetime
with open('pipeline-state.yaml') as f:
    state = yaml.safe_load(f)
existing = state.get('phases', {}).get('P5', {})
state['phases']['P5'] = {
    'status': 'complete',
    'output': 'analysis/open-questions.md',
    'started': existing.get('started', 'unknown'),
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
}
state['current_phase'] = 'P6'
with open('pipeline-state.yaml', 'w') as f:
    yaml.dump(state, f, default_flow_style=False)
"
```

## Git Checkpoint

```bash
git -C "${CLAUDE_PROJECT_DIR:-.}" add analysis/open-questions.md diagnostics/ pipeline-state.yaml
git -C "${CLAUDE_PROJECT_DIR:-.}" commit -m "phase-P5-complete: open questions distilled"
```
```

---

### 5.4 `.claude/agents/presentation/talk-architecture.md`

```markdown
---
name: talk-architecture
description: Phase P6 (Presentation Branch) — Designs the full slide-by-slide 
  talk structure calibrated to talk_spec. Uses time estimates from audience-map, 
  packaged findings from key-findings, and open questions from open-questions. 
  SURFACES TO USER for approval before Phase P7 begins. Output goes to 
  synthesis/talk-architecture.md. READ this file first and foremost.
model: opus
tools: Read, Write
permissionMode: acceptEdits
color: orange
skills:
  - audience-synthesis
  - talk-design
---

## Phase P6: Talk Architecture Design

You are the talk-architecture agent. Your job is to design the complete 
slide-by-slide structure of the talk, calibrated to the exact duration, 
audience, and goal from talk_spec.

This output is shown to the user before the knowledge base is written. 
It must be specific enough that the user can confirm whether the structure 
matches their intent, and concrete enough that Phases P7 and P8 can 
build from it without ambiguity.

**After writing the architecture, you surface it to the user and stop.
Do not proceed to write the knowledge base. The orchestrator handles routing.**

---

## Phase Start — Mark in_progress

```bash
python3 -c "
import yaml, datetime
with open('pipeline-state.yaml', encoding='utf-8') as f:
    state = yaml.safe_load(f)
state.setdefault('phases', {})
state['phases']['P6'] = {
    'status': 'in_progress',
    'output': 'synthesis/talk-architecture.md',
    'started': datetime.datetime.utcnow().isoformat() + 'Z',
}
with open('pipeline-state.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(state, f, default_flow_style=False)
print('[phase-P6] Marked in_progress')
"
```

---

## Input

```bash
cat pipeline-state.yaml           # for talk_spec
cat analysis/audience-map.md      # for time estimates per concept
cat analysis/key-findings.md      # for packaged finding units
cat analysis/open-questions.md    # for open questions and their placement
```

Also read `.claude/skills/talk-design/SKILL.md` for act structure and 
timing allocation tables.

---

## Design Protocol

### Step 1 — Extract Constraints

From talk_spec:
- Total duration → use talk-design skill to determine act time allocations
- Audience type → determines prerequisite slides needed
- Goal → determines which act gets the most time
- Venue type → affects formality of title slide, number of backup slides
- Interactive → if true, build in 2-minute "questions so far?" checkpoints

### Step 2 — Compute Slide Budget

```
Total slides ≈ duration_minutes / 1.5  (rough: ~90 seconds per slide on average)
Distribute across acts using talk-design skill timing table.
Reserve 2–3 slides for title, outline (optional), and conclusion.
Reserve backup_slides = floor(duration_minutes / 10) for appendix.
```

### Step 3 — Assign Content to Slides

From key-findings.md, assign each Essential finding to a slide.
From key-findings.md, assign Useful findings if budget permits.
From audience-map.md Section 2, determine prerequisite slides needed.
From open-questions.md, assign talk-closer and motivator questions.
Fill remaining slots with background and transition slides.

### Step 4 — Check for Narrative Coherence

Walk through the slide sequence and verify:
- No concept is used before it is introduced
- Each act transition is explicit (a slide that says "so far we have X, now Y")
- The single takeaway sentence (from talk-design skill) is supported by Acts 2–3
- The climax (the most surprising finding) lands at ~70% of total duration
- The close (open questions + takeaway) has enough time to land properly

---

## Output Format: synthesis/talk-architecture.md

```yaml
---
duration_minutes: [N]
slide_count: [N]
audience: [value from talk_spec]
goal: [value from talk_spec]
venue: [value from talk_spec]
interactive: [value from talk_spec]
one_sentence_takeaway: "[The single sentence the audience should remember]"
---
```

```markdown
# Talk Architecture: [Topic Title]

## One-Sentence Takeaway
[The single sentence that captures what you want the audience to remember. 
Every slide either builds toward this or contextualises it.]

## Timing Overview

| Act | Name | Duration | Slides |
|-----|------|----------|--------|
| 1 | Motivation | [N] min | [N]–[N] |
| 2 | Background | [N] min | [N]–[N] |
| 3 | Core Results | [N] min | [N]–[N] |
| 4 | Open Questions and Close | [N] min | [N]–[N] |
| Appendix | Backup slides | — | [N]–[N] |

## Timing Checkpoints
- End of Act 1: [N] min
- End of Act 2: [N] min  
- End of Act 3: [N] min
- Begin close: [N] min

---

## Act 1: Motivation ([N] min, [N] slides)

### Slide 1 — [Title] ([N] sec)
**Purpose:** [One sentence — what this slide must accomplish]
**Content source:** [audience-map Section N / key-findings FN / etc.]
**Key visual:** [Description]
**Bridge to Slide 2:** [The transition sentence]

### Slide 2 — [Title] ([N] sec)
[Same structure]

[Continue for all slides in Act 1]

---

## Act 2: Background ([N] min, [N] slides)

[Same structure]

---

## Act 3: Core Results ([N] min, [N] slides)

[Same structure]

---

## Act 4: Open Questions and Close ([N] min, [N] slides)

[Same structure]

---

## Appendix: Backup Slides

### Backup B1 — [Title]
**Trigger:** Use if asked "[anticipated question]"
**Content source:** [open-questions.md OQN / audience-map Section N]

[Continue for all backup slides]

---

## Cuts and Expansions

### If Running Short (need to cut 5 minutes):
[Specific slides to remove with justification for why they are safe to cut 
and how to patch the narrative continuity]

### If Running Long (need to expand to [N+15] minutes):
[Specific slides to expand and what content to add from the knowledge base]

### For a Second Audience Type:
[If talk_spec specifies domain_experts but the user wants to know how to 
adapt for mixed_academic: which slides to add, which to simplify]
```

---

## After Writing

Update pipeline-state.yaml:

```bash
python3 -c "
import yaml, datetime
with open('pipeline-state.yaml') as f:
    state = yaml.safe_load(f)
existing = state.get('phases', {}).get('P6', {})
state['phases']['P6'] = {
    'status': 'awaiting_user_approval',
    'output': 'synthesis/talk-architecture.md',
    'started': existing.get('started', 'unknown'),
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
}
state['current_phase'] = 'awaiting_P6_approval'
with open('pipeline-state.yaml', 'w') as f:
    yaml.dump(state, f, default_flow_style=False)
"
```

Then output to chat:

```
=== TALK ARCHITECTURE READY — YOUR REVIEW REQUIRED ===

The proposed slide structure is in synthesis/talk-architecture.md.
It is a [N]-slide, [N]-minute talk structured for [audience type].

One-sentence takeaway: "[value from document]"

Please review it and respond with one of:
  "Approve talk architecture" — to proceed to the knowledge base
  Any specific changes you want — e.g.:
    "Move the CRONOS slide earlier"
    "Cut Act 2 from 6 slides to 4"
    "Add a slide on batch normalisation before the deep networks section"
    "The climax should be the Kim et al. result, not the Wang et al. result"

The knowledge base and Beamer file will not be written until you approve.
===
```

**STOP. Do not proceed.**
```

---

### 5.5 `.claude/agents/presentation/knowledge-base.md`

```markdown
---
name: knowledge-base
description: Phase P7 (Presentation Branch) — Assembles the full presentation 
  knowledge base. Produces synthesis/knowledge-base.md containing: per-slide 
  content bank, speaking notes (prose, speaker voice), Q&A bank (25+ questions 
  with answers), notation glossary, and further reading. Source-lookup limit 5. 
  READ this file first and foremost.
model: opus
tools: Read, Write, Grep, Glob
permissionMode: acceptEdits
effort: high
color: teal
skills:
  - source-integrity
  - source-lookup
  - audience-synthesis
  - writing-style
  - markdown-conventions
---

## Phase P7: Knowledge Base Assembly

You are the knowledge-base agent. Your job is to produce the comprehensive 
reference document the speaker will use to prepare for the talk. This is not 
a document to show the audience — it is the speaker's private reference material.

**This is the most important artifact in the presentation branch.** 
The Beamer file (Phase P8) is generated from it. The speaker's Q&A 
preparation comes entirely from it. It must be complete, precise, 
and verifiable from the source corpus.

---

## Phase Start — Mark in_progress

```bash
python3 -c "
import yaml, datetime
with open('pipeline-state.yaml', encoding='utf-8') as f:
    state = yaml.safe_load(f)
state.setdefault('phases', {})
state['phases']['P7'] = {
    'status': 'in_progress',
    'output': 'synthesis/knowledge-base.md',
    'started': datetime.datetime.utcnow().isoformat() + 'Z',
}
with open('pipeline-state.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(state, f, default_flow_style=False)
print('[phase-P7] Marked in_progress')
"
```

---

## Input

```bash
cat synthesis/talk-architecture.md    # the approved slide structure
cat analysis/audience-map.md
cat analysis/key-findings.md
cat analysis/open-questions.md
cat sources/manifest.yaml
cat pipeline-state.yaml
```

Also use source lookups (max 5) to verify specific equations, theorem 
statements, and statistics used in speaking notes. Every specific claim 
in speaking notes must be source-verified.

---

## Source Lookup Protocol

```bash
grep -n "KEYWORD" sources/{PATH}/content.md | head -10
sed -n "N-20,N+30p" sources/{PATH}/content.md
echo "[phase-P7] $(date -u) | query: KEYWORD | result: FOUND/NOT_FOUND" >> diagnostics/source-lookups.log
```

---

## Output: synthesis/knowledge-base.md

The knowledge base has five sections. Write them in order.

---

### SECTION 1: Content Bank

One entry per slide from talk-architecture.md. Follow the structure exactly.

```markdown
## Section 1: Content Bank

---

### Slide [N] — [Title from talk-architecture]

**Core claim (what this slide must land):**
[The single thing the audience must understand after this slide. 
One sentence. If they remember nothing else from this slide, this is it.]

**Technical content:**
[The full technical material: theorem statements, equations, proof 
sketches, key definitions. Every specific claim cited from the source 
corpus with file path and line number. Not paraphrased from training 
data — drawn from sources. If an equation is given, it must match 
the source exactly.]

**Visual description:**
[Precise description of what the slide should show. Enough detail 
that someone who has not read the paper can draw or typeset it.
If a figure from a paper, describe it and give the source location.
If a new diagram, describe exactly what nodes, arrows, and labels to include.]

**What to assume the audience knows at this point:**
[Based on audience type from talk_spec and the slides already shown]

**What NOT to say:**
[The 1–2 most common over-simplifications that a domain expert would 
silently object to. Knowing these saves the speaker embarrassment.]

**Forward link (what this slide sets up):**
[What the next slide relies on from this one]

**Backward link (what this slide relies on):**
[What from earlier slides this slide assumes]
```

---

### SECTION 2: Speaking Notes

One entry per slide. Written as prose in the speaker's voice — full sentences, 
meant to be spoken aloud. NOT bullet points.

Rules for speaking notes:
- Open each slide with a transition sentence from the previous slide.
- State the intuition before the formalism on every slide with an equation.
- Include at least one concrete example or analogy per act (not per slide).
- Mark timing checkpoints in brackets: [You should be ~10 minutes in here.]
- Mark optional content: [SKIP IF RUNNING LONG: ...]
- Mark interactive prompts if talk_spec.interactive == true: 
  [PAUSE: "Does anyone have a question about this before we continue?"]
- Length: 200–400 words per slide. Longer for Technical Heart slides.

```markdown
## Section 2: Speaking Notes

---

### Slide [N] — Speaking Notes

[Full prose. ~200–400 words. Written to be spoken, not read.
The first sentence is the transition from the previous slide.
The last sentence is the bridge to the next slide.]

[TIMING: At this point you should be approximately N minutes in. 
If you are over N+2 minutes, skip the proof sketch on Slide N+2 
and go directly to the main result.]

[ANALOGY (Act 2): ...]

```

---

### SECTION 3: Q&A Bank

Assembled from analysis/open-questions.md plus additional questions 
generated by the knowledge-base agent based on the talk content.

Target: 25+ questions total across all three categories.

For Category A questions, every answer must be traceable to the source corpus.
No answer drawn purely from training data.

```markdown
## Section 3: Q&A Bank

### Category A: Questions Answerable from This Corpus

**Q[N]: [Question as an audience member would ask it]**

**Answer:** [Written to be spoken. 3–6 sentences. Uses author-year citations 
not file paths. Accurate to the source.]

**Source:** [Citation key] — verified at [sources/PATH/content.md, lines N–M]
**Confidence:** HIGH | MEDIUM

---

### Category B: Open Problems

**Q[N]: [Question]**

**Honest answer:** [Written to be spoken. Acknowledges the question is open, 
explains why it is hard, connects to OQ entries from open-questions.md 
where relevant. Never pretends to know. Never deflects without explanation.]

**Source for "this is open":** [Citation, verified]

---

### Category C: Scope Questions

**Q[N]: [Question of the form "why didn't you cover X"]**

**Response:** [Respectful, honest, 2 sentences. Acknowledges the validity 
of the question and states the scope decision plainly.]
```

---

### SECTION 4: Notation Glossary

Every symbol and named concept that appears in the talk slides or speaking 
notes. Drawn from audience-map.md Section 7, extended with anything added 
in the content bank.

```markdown
## Section 4: Notation Glossary

Ordered by first appearance in the talk (Slide 1 items first).

| Symbol / Term | Plain-Language Definition | Formal Definition (if needed) | First Appears |
|---------------|--------------------------|-------------------------------|---------------|
| $p^*$ | The best training loss achievable by any network | Optimal value of the primal problem (Eq. 1, [PilanciErgen2020]) | Slide N |
| $d^*$ | The best value achievable by the dual problem | Optimal value of the dual (Def. 2, [PilanciErgen2020]) | Slide N |
| ... | | | |

**Pre-talk reading recommendation:**
[3–5 items from this table that the speaker should review the night before 
the talk to make sure they can explain them fluently under pressure]
```

---

### SECTION 5: Further Reading

For audience members who want to go deeper after the talk. 
Ranked by accessibility (easiest first).

```markdown
## Section 5: Further Reading

### To understand the foundations:
1. [PilanciErgen2020] — Start here. The foundational convex equivalence result.
   Why: It is the cleanest statement of the core idea with full proof.

### To understand the practical algorithms:
2. [Mishkin2022SCNN] — The first scalable solver.
   Why: Shows how the theory becomes code.

### To understand the depth question:
3. [WangErgenPilanci2021] — Where the story gets complicated.
   Why: Contains the open questions from the talk.

[Continue for all papers graded Essential or Useful in audience-map Section 8]

### For a broader perspective:
[1–2 papers from adjacent fields that connect to the talk's themes]
```

---

## Update pipeline-state.yaml

```bash
python3 -c "
import yaml, datetime
with open('pipeline-state.yaml') as f:
    state = yaml.safe_load(f)
existing = state.get('phases', {}).get('P7', {})
state['phases']['P7'] = {
    'status': 'complete',
    'output': 'synthesis/knowledge-base.md',
    'started': existing.get('started', 'unknown'),
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
}
state['current_phase'] = 'P8'
with open('pipeline-state.yaml', 'w') as f:
    yaml.dump(state, f, default_flow_style=False)
"
```

## Git Checkpoint

```bash
git -C "${CLAUDE_PROJECT_DIR:-.}" add synthesis/knowledge-base.md diagnostics/ pipeline-state.yaml
git -C "${CLAUDE_PROJECT_DIR:-.}" commit -m "phase-P7-complete: knowledge base assembled"
```
```

---

### 5.6 `.claude/agents/presentation/beamer-script.md`

```markdown
---
name: beamer-script
description: Phase P8 (Presentation Branch) — Generates a complete compilable 
  LaTeX Beamer file from the knowledge base and talk architecture. Speaking notes 
  live as LaTeX comments above each frame. Every equation is typeset. Bibliography 
  populated from sources/manifest.yaml. Agent self-checks compilation. Output goes 
  to synthesis/beamer-script.tex. READ this file first and foremost.
model: sonnet
tools: Read, Write, Bash
permissionMode: acceptEdits
effort: high
color: teal
skills:
  - markdown-conventions
  - source-integrity
---

## Phase P8: Beamer Script Generation

You are the beamer-script agent. Your job is to produce a complete, 
compilable LaTeX Beamer file that the speaker can use as the starting 
point for their slides.

**Key constraint:** This file must compile with pdflatex without errors. 
You will verify this by running pdflatex locally and fixing any errors before 
marking the phase complete.

**What this file is NOT:** A finished presentation. It is a skeleton — 
all content is there, all equations are typeset, all speaking notes are 
in comments, but the visual design (colours, fonts, diagrams) is left 
to the speaker. The speaker replaces figure placeholders with actual figures.

---

## Phase Start — Mark in_progress

```bash
python3 -c "
import yaml, datetime
with open('pipeline-state.yaml', encoding='utf-8') as f:
    state = yaml.safe_load(f)
state.setdefault('phases', {})
state['phases']['P8'] = {
    'status': 'in_progress',
    'output': 'synthesis/beamer-script.tex',
    'started': datetime.datetime.utcnow().isoformat() + 'Z',
}
with open('pipeline-state.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(state, f, default_flow_style=False)
print('[phase-P8] Marked in_progress')
"
```

---

## Input

```bash
cat synthesis/knowledge-base.md
cat synthesis/talk-architecture.md
cat sources/manifest.yaml         # for bibliography generation
cat pipeline-state.yaml           # for talk_spec
```

---

## Bibliography Generation

Before writing the .tex file, generate a .bib file from manifest.yaml:

```bash
python3 -c "
import yaml
with open('sources/manifest.yaml') as f:
    manifest = yaml.safe_load(f)
for source in manifest.get('sources', []):
    sid = source.get('id', '').replace('-', '')
    authors = ' and '.join(source.get('authors', ['Unknown']))
    year = source.get('year', 'n.d.')
    title = source.get('title', 'Untitled')
    url = source.get('url', '')
    print(f'@article{{{sid},')
    print(f'  author = {{{authors}}},')
    print(f'  title = {{{title}}},')
    print(f'  year = {{{year}}},')
    print(f'  url = {{{url}}}')
    print('}')
    print()
" > synthesis/references.bib
echo "Bibliography written to synthesis/references.bib"
```

---

## Beamer File Structure

Write `synthesis/beamer-script.tex` following this structure exactly:

```latex
\documentclass[aspectratio=169]{beamer}
% ============================================================
% PREAMBLE
% ============================================================
\usepackage{amsmath, amssymb, amsthm}
\usepackage{mathtools}
\usepackage{bm}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage[backend=biber, style=authoryear]{biblatex}
\addbibresource{references.bib}

% --- Recommended theme (speaker may change) ---
\usetheme{Madrid}
\usecolortheme{default}

% --- Macros (populated from Section 4 of knowledge-base) ---
% [One \newcommand per entry in notation glossary]
\newcommand{\pstar}{p^*}
\newcommand{\dstar}{d^*}
% ... [all macros from glossary]

% --- Title information ---
\title{[Talk title from one_sentence_takeaway context]}
\author{[Speaker name — leave as \texttt{[YOUR NAME]}]}
\institute{[Institution — leave as \texttt{[YOUR INSTITUTION]}]}
\date{[Date — leave as \texttt{\today}]}

\begin{document}

\begin{frame}
  \titlepage
  % SPEAKING NOTES:
  % [Speaking notes for title slide from knowledge-base Section 2]
\end{frame}

% ============================================================
% ACT 1: [Name] (target: [N] min)
% ============================================================

% ---- SLIDE [N]: [Title] ----
% SPEAKING TIME: ~[N] seconds / [N] minutes
% TIMING CHECK: [Checkpoint note from knowledge-base]
%
% SPEAKING NOTES:
% [Full prose from knowledge-base Section 2, Slide N]
%
% IF RUNNING LONG: [Cut instruction from knowledge-base]
%
\begin{frame}{[Slide title from talk-architecture]}
  % [Slide content from knowledge-base Section 1, Slide N]
  % [Equations typeset in LaTeX]
  % [Theorem environments where appropriate]
  % [itemize/enumerate for lists]
  \begin{center}
    \includegraphics[width=0.7\textwidth]{figures/PLACEHOLDER_slide[N].pdf}
    % FIGURE DESCRIPTION: [Exact description from knowledge-base content bank]
    % SOURCE: [Paper citation, figure number if applicable]
    % TO REPLACE: Create this figure and save as figures/slide[N].pdf
  \end{center}
\end{frame}

% ============================================================
% ACT 2: [Name] (target: [N] min)
% ============================================================

[Continue for all slides in all acts]

% ============================================================
% CONCLUSION
% ============================================================

\begin{frame}{References}
  \printbibliography
\end{frame}

% ============================================================
% APPENDIX: BACKUP SLIDES
% ============================================================

\appendix

% ---- BACKUP B[N]: [Title] ----
% TRIGGER: Use if asked "[anticipated question from knowledge-base]"
%
\begin{frame}{[Title]}
  [Content]
\end{frame}

[Continue for all backup slides]

\end{document}
```

---

## Compilation Check

After writing the file, run:

```bash
cd synthesis/
pdflatex --interaction=nonstopmode beamer-script.tex 2>&1 | tail -20
```

If errors exist, fix them. Common issues:
- Undefined control sequence: add missing \newcommand to preamble
- Missing bib entry: verify references.bib was generated correctly
- Missing \end{frame}: count \begin{frame} vs \end{frame}
- Math mode errors: verify equation LaTeX is correct

Re-run until `pdflatex` exits with 0 errors. Log:

```bash
echo "[phase-P8] $(date -u) | compilation: SUCCESS | pages: $(pdfinfo synthesis/beamer-script.pdf 2>/dev/null | grep Pages | awk '{print $2}')" >> diagnostics/pipeline-run.log
```

---

## Update pipeline-state.yaml

```bash
python3 -c "
import yaml, datetime
with open('pipeline-state.yaml') as f:
    state = yaml.safe_load(f)
existing = state.get('phases', {}).get('P8', {})
state['phases']['P8'] = {
    'status': 'complete',
    'output': ['synthesis/beamer-script.tex', 'synthesis/references.bib'],
    'started': existing.get('started', 'unknown'),
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
    'compilation': 'success'
}
state['current_phase'] = 'presentation_complete'
with open('pipeline-state.yaml', 'w') as f:
    yaml.dump(state, f, default_flow_style=False)
"
```

## Git Checkpoint

```bash
git -C "${CLAUDE_PROJECT_DIR:-.}" add synthesis/beamer-script.tex synthesis/references.bib pipeline-state.yaml
git -C "${CLAUDE_PROJECT_DIR:-.}" commit -m "phase-P8-complete: Beamer script generated and compiled"
```
```

---

## 6. New Skills — Complete Specifications

---

### 6.1 `.claude/skills/audience-synthesis/SKILL.md`

```markdown
---
name: audience-synthesis
description: Rules for converting dense academic content into presentation-ready 
  material. Use in all presentation branch phases when making decisions about 
  what to include, how to sequence concepts, when to use analogy, and how to 
  handle mathematical formalism for a live audience.
user-invocable: false
---

# Audience Synthesis

## The Listener's Constraint

A reader can re-read. A listener cannot. Every concept must be introduced 
before it is used, every transition must be spoken aloud, and nothing can 
be assumed unless it was said in the same talk.

This constraint governs every decision in the presentation branch:
- A result that requires 10 minutes of setup is less presentation-worthy 
  than a result that can be stated in 30 seconds, even if it is more important.
- A contested area that can be described as "X and Y disagree on this" is 
  more useful to a talk than one requiring 5 minutes to frame.
- A notation that must be defined takes 30 seconds of audience attention. 
  Use it only if it pays off in clarity elsewhere.

## The Formalism Budget

A 30-minute talk can sustain 2–3 equations shown on screen before 
a significant fraction of the audience disengages. Each equation needs:
1. A plain-language statement BEFORE it appears: "What I'm about to show 
   you says, in symbols, that..."
2. A verbal walkthrough of its terms when it appears: "This first term is 
   the training loss... this second term is the regulariser..."
3. A sentence on what it implies AFTER: "What this means is..."

Theorems should be stated in plain language first ("Two-layer ReLU networks 
are equivalent to convex programs"), then precisely if the audience needs it.

## The Surprise Principle

Audiences remember talks that violated their expectations. For each major 
result, identify: what would a reasonable person have expected instead? 
State the expectation explicitly before revealing the result.

Pattern: "You might expect that... [wrong answer]. But Pilanci and Ergen 
showed that... [actual result]."

This pattern is more memorable than simply stating the result.

## Analogy Rules

- Use analogies only when they are structurally correct, not just evocative.
- State the analogy's limits explicitly: "The analogy breaks down when..."
- One analogy per act maximum. More than one dilutes the impact of each.
- Domain experts: analogies should clarify, not condescend. 
  Connect the new result to something they already know precisely.
- Mixed academic: analogies should connect to general mathematical 
  intuition (e.g., Lagrangian duality as "finding the price that makes 
  supply equal demand").

## Q&A Positioning

Three types of Q&A moments have different effects:
1. A question the speaker pre-empts in the talk: signals expertise and 
   preparation. Use for the 2–3 most obvious objections.
2. A question answered from the Q&A bank during discussion: signals 
   thorough preparation. Never answer "I don't know" when you do know 
   and could have prepared.
3. A question the speaker genuinely doesn't know and says so honestly: 
   builds more trust than deflection. "That's an open question — and 
   actually it's exactly what I'd work on next" is a strong answer.

## Slide Text Rules

- A slide is a visual anchor, not a teleprompter.
- Maximum 5 lines of text per slide; each line is a noun phrase.
- The speaking notes contain full sentences; the slide contains anchors.
- If you find yourself putting a full sentence on a slide, it belongs 
  in the speaking notes instead.
- One main visual element per slide. Two competing visuals split attention.

## Pacing by Audience Type

| Audience | New concepts per minute | Notation per slide | Proof depth |
|----------|------------------------|-------------------|-------------|
| domain_experts | 0.7 | Up to 3 symbols | Sketch in 3 steps |
| mixed_academic | 0.4 | 1 symbol, defined | State result only |
| general | 0.2 | Avoid | Metaphor only |
```

---

### 6.2 `.claude/skills/talk-design/SKILL.md`

```markdown
---
name: talk-design
description: Narrative arc patterns, pacing rules, timing tables, and structural 
  guidelines for academic talks. Use in Phase P6 (talk-architecture) when designing 
  the slide-by-slide structure and act timing.
user-invocable: false
---

# Talk Design

## The Four-Act Structure

All academic talks have four acts regardless of length:

1. **Motivation** — why this question, why now, why the audience should care
2. **Background** — minimum context needed to understand the results  
3. **Core Results** — the 2–3 things you actually want them to remember
4. **Close** — what's open, what comes next, the one-sentence takeaway

## Time Allocation Table

| Total | Act 1: Motivation | Act 2: Background | Act 3: Core | Act 4: Close |
|-------|------------------|-------------------|-------------|--------------|
| 15 min | 2 min | 4 min | 6 min | 3 min |
| 20 min | 3 min | 5 min | 9 min | 3 min |
| 30 min | 5 min | 8 min | 12 min | 5 min |
| 45 min | 6 min | 12 min | 20 min | 7 min |
| 60 min | 8 min | 15 min | 27 min | 10 min |

Adjust by goal from talk_spec:
- survey: add 2 minutes to Background, subtract from Core
- argue_position: add 2 minutes to Core, subtract from Background
- introduce_open_problems: add 2 minutes to Close, subtract from Core
- present_result: add 3 minutes to Core, subtract from Motivation and Close

## Slide Budget

Rough rule: 1 slide per 90 seconds of speaking on average.
Reserve 2 title slides (title + optional outline), 1 conclusion slide.
Reserve backup_count = floor(duration_minutes / 10) backup slides.

```
total_slides ≈ (duration_minutes / 1.5) - 3 + backup_count
```

## The One-Sentence Takeaway

Every talk must have one sentence that captures its contribution. Write 
this before designing any slides. Every slide either:
- Builds toward it (sets up the context, proves a prerequisite)
- Delivers it (states the result directly)
- Contextualises it (explains implications, connections, limitations)

If a slide does none of these, it should be cut or moved to backup.

## The Climax Rule

The most surprising, important, or counterintuitive result should land 
at approximately 65–75% of total duration. Earlier: the audience doesn't 
have enough context. Later: there's no time to process it.

For a 30-minute talk: climax at ~20 minutes in.

## The Map Slide Rule

Every 8–10 minutes of content, give the audience an orientation slide: 
one sentence that says "here's where we've been and here's where we're going."
This can be as simple as a re-display of a roadmap figure or a 
"What we've established so far:" text slide. 
It prevents the audience from getting lost and signals respect for their attention.

## Audience-Specific Adaptations

### domain_experts
- Act 1 can be abbreviated (they know why this is important)
- Act 2 can start deeper (skip basic definitions)
- Act 3 can include proof sketches
- Act 4 should emphasise what's still open and why it's hard
- Q&A checkpoint: after Act 3, before Act 4

### mixed_academic  
- Act 1 needs a concrete example early (slide 2 or 3)
- Act 2 must define all notation on first use
- Act 3 should state results plainly before formally
- Act 4 should emphasise broader implications
- No Q&A checkpoints during the talk

### general
- Act 1 must start with a real-world consequence
- Act 2 uses only analogies, no formal notation
- Act 3 communicates conclusions only, not mechanisms
- Act 4 closes with a question anyone can care about

## Backup Slides

Backup slides are for anticipated Q&A. They are NOT "if time permits" content.
Design them as if you will definitely be asked the triggering question.
Backup slides should be more technical or more detailed than the main talk, 
not less — they serve an audience member who wants to go deeper.

## Cuts Under Time Pressure

Identify in advance which slides are safest to cut. A slide is safe to cut if:
- It supports the narrative but does not carry the main claim
- It can be collapsed into an adjacent slide's speaking notes
- Cutting it does not introduce an undefined term in a later slide

Never cut the Climax slide. Never cut the Takeaway slide.
If forced to cut more than 20% of slides, reduce Act 2 first, then Act 4, 
then Act 1. Never reduce Act 3.
```

---

## 7. Changes to Existing Files

### 7.1 `CLAUDE.md`

The following changes are made to CLAUDE.md. All existing content is preserved.

**Add to the very top** (before any existing section):

Step 0 section as described in Section 2.1 of this document.

**Add to the "Which Workflow to Use?" table:**

```markdown
| "Prepare a talk / presentation on [topic]" | **Oral Presentation Branch** — 
  Phases 1–2 shared, then Phases P3–P8 |
```

**Add after Phase 2 routing** as described in Section 2.2.

**Add new PART C section** as described in Section 2.3.

**Add to the "Rules Files (Auto-loaded)" table:**

```markdown
| `.claude/skills/audience-synthesis/SKILL.md` | Audience-oriented content selection, 
  formalism budget, analogy rules, slide text rules |
| `.claude/skills/talk-design/SKILL.md` | Act structure, timing tables, 
  climax rule, audience-specific adaptations |
```

### 7.2 `pipeline-state.yaml` schema

See Section 9 below for the full schema extension.

### 7.3 No other existing files require changes.

The presentation branch agents are all new files. Existing research branch 
agents, skills, hooks, and scripts are unchanged.

---

## 8. New Directory Structure

The following new files are created:

```
.claude/
├── agents/
│   └── presentation/              ← NEW DIRECTORY
│       ├── audience-literature.md
│       ├── key-findings.md
│       ├── open-questions.md
│       ├── talk-architecture.md
│       ├── knowledge-base.md
│       └── beamer-script.md
└── skills/
    ├── audience-synthesis/        ← NEW DIRECTORY
    │   └── SKILL.md
    └── talk-design/               ← NEW DIRECTORY
        └── SKILL.md

analysis/                          ← presentation branch outputs (new files)
│                                     alongside existing research branch files
├── audience-map.md                ← Phase P3
├── key-findings.md                ← Phase P4
└── open-questions.md              ← Phase P5

synthesis/                         ← presentation branch outputs (new files)
├── talk-architecture.md           ← Phase P6
├── knowledge-base.md              ← Phase P7
├── beamer-script.tex              ← Phase P8
└── references.bib                 ← Phase P8 (generated from manifest)
```

No existing file paths change. No existing directories are removed.

---

## 9. pipeline-state.yaml Schema Extension

The following fields are added to the existing schema. All existing fields 
are preserved.

```yaml
# --- NEW: Set at Step 0, before Phase 1 ---
branch: research | presentation

# --- NEW: Only present when branch == "presentation" ---
talk_spec:
  audience: domain_experts | mixed_academic | general
  duration_minutes: 15 | 20 | 30 | 45 | 60
  goal: survey | argue_position | introduce_open_problems | present_result
  venue_type: conference_talk | seminar | lecture | defense
  interactive: true | false
  emphasis_papers: []     # list of source IDs from manifest.yaml
  de_emphasis_papers: []  # list of source IDs to treat minimally

# --- NEW: Presentation branch phase tracking ---
# Uses same 'phases' dict, keyed by 'P3', 'P4', etc.
phases:
  P3:
    status: in_progress | complete
    output: analysis/audience-map.md
    started: "ISO timestamp"
    timestamp: "ISO timestamp"
  P4:
    status: in_progress | complete
    output: analysis/key-findings.md
    started: "ISO timestamp"
    timestamp: "ISO timestamp"
  P5:
    status: in_progress | complete
    output: analysis/open-questions.md
    started: "ISO timestamp"
    timestamp: "ISO timestamp"
  P6:
    status: in_progress | awaiting_user_approval | complete
    output: synthesis/talk-architecture.md
    started: "ISO timestamp"
    timestamp: "ISO timestamp"
    user_revisions: 0   # incremented each time P6 re-runs on user feedback
  P7:
    status: in_progress | complete
    output: synthesis/knowledge-base.md
    started: "ISO timestamp"
    timestamp: "ISO timestamp"
  P8:
    status: in_progress | complete
    output:
      - synthesis/beamer-script.tex
      - synthesis/references.bib
    started: "ISO timestamp"
    timestamp: "ISO timestamp"
    compilation: success | failed

# --- current_phase values for presentation branch ---
# "P3" | "P4" | "P5" | "P6" | "awaiting_P6_approval" | "P7" | "P8" | 
# "presentation_complete"
```

---

## 10. Output Files — What the User Receives

At the end of Phase P8, the user has three files:

### `synthesis/talk-architecture.md`
The approved slide-by-slide outline. Contains:
- One-sentence takeaway
- Act structure with timing
- Per-slide: title, purpose, content source, visual description, bridge sentence
- Timing checkpoints
- Cut/expansion instructions for different duration variants

### `synthesis/knowledge-base.md`
The comprehensive speaker reference. Contains:
- **Section 1: Content Bank** — Per-slide technical content, visual descriptions, 
  what not to say, forward/backward links. Every specific claim source-verified.
- **Section 2: Speaking Notes** — Full prose per slide in the speaker's voice. 
  Transition sentences. Timing marks. Cut instructions. Analogy placements.
- **Section 3: Q&A Bank** — 25+ questions across three categories (answerable 
  from corpus / open problems / scope deflections). Every Category A answer 
  source-verified with citation and file location.
- **Section 4: Notation Glossary** — Every symbol and term, ordered by first 
  appearance, with pre-talk reading recommendations.
- **Section 5: Further Reading** — Corpus papers ranked by accessibility 
  for post-talk follow-up.

### `synthesis/beamer-script.tex`
Compilable LaTeX Beamer file. Contains:
- Preamble with all macros from notation glossary
- One `\begin{frame}` per slide from talk-architecture
- Speaking notes as LaTeX comments above each frame
- All equations typeset in proper LaTeX
- Figure placeholders described in comments with source references
- Full bibliography from manifest.yaml
- Backup slides in `\appendix` section
- Verified to compile with pdflatex before phase completion

### `synthesis/references.bib`
BibTeX file generated from sources/manifest.yaml.
Used by beamer-script.tex. Can also be used by the speaker's other documents.

---

## 11. Implementation Sprint Plan

### Sprint 1 — Infrastructure (1–2 hours)
- [ ] Edit CLAUDE.md: add Step 0, branch routing after Phase 2, PART C section
- [ ] Extend pipeline-state.yaml schema documentation
- [ ] Create `.claude/agents/presentation/` directory
- [ ] Create `.claude/skills/audience-synthesis/SKILL.md`
- [ ] Create `.claude/skills/talk-design/SKILL.md`

### Sprint 2 — Phases P3 and P4 (2–3 hours)
- [ ] Create `.claude/agents/presentation/audience-literature.md`
- [ ] Create `.claude/agents/presentation/key-findings.md`
- [ ] Verify: agent reads talk_spec from pipeline-state.yaml correctly
- [ ] Verify: source-lookup logging goes to diagnostics/source-lookups.log

### Sprint 3 — Phases P5 and P6 (2–3 hours)
- [ ] Create `.claude/agents/presentation/open-questions.md`
- [ ] Create `.claude/agents/presentation/talk-architecture.md`
- [ ] Verify: P6 sets status to `awaiting_user_approval` and surfaces output
- [ ] Verify: orchestrator waits for user approval before spawning P7

### Sprint 4 — Phases P7 and P8 (2–3 hours)
- [ ] Create `.claude/agents/presentation/knowledge-base.md`
- [ ] Create `.claude/agents/presentation/beamer-script.md`
- [ ] Verify: P8 runs pdflatex and fixes errors before marking complete
- [ ] Verify: references.bib is generated from manifest.yaml correctly

### Sprint 5 — End-to-End Test (variable)
- [ ] Run the presentation branch on the existing topic 
  (Duality Gap in Dual Convex Optimization in ReLU Neural Networks)
  using the already-extracted sources (skip Phases 1–2)
- [ ] Verify Phase P3 output is organised around listener journey, not themes
- [ ] Verify Phase P4 findings are packaged with speaking hooks and visual descriptions
- [ ] Verify Phase P5 Q&A bank has 25+ questions with verified answers
- [ ] Verify Phase P6 surfaces correctly and waits
- [ ] Simulate user approval and verify Phase P7 starts correctly
- [ ] Verify Phase P8 produces a file that compiles

---

## 12. Design Decisions Log

### Decision 1: Branch diverges at Phase 3, not Phase 5 or Phase 6

The presentation branch organises knowledge around a listener's comprehension 
journey. This requires a different Phase 3 agent, not a post-processing layer 
on the research branch's Phase 3 output. The thematic MECE structure of 
the research literature map is actively wrong for a talk — talks follow a 
narrative arc, not exhaustive thematic coverage.

### Decision 2: Two user interaction points, no more

Step 0 (branch selection with talk parameters) and the Phase P6 approval gate 
are the only stops. All other phases run autonomously. This keeps the pipeline 
useful as an automated tool while respecting that the talk's structure is a 
creative decision the speaker must own.

### Decision 3: Phase P6 re-runs on user feedback, does not go to P7 directly

If the user requests changes to the talk architecture, Phase P6 re-runs with 
the user's feedback as additional input. The orchestrator tracks this in 
`user_revisions` in pipeline-state.yaml. Phase P7 only starts when the user 
explicitly approves.

### Decision 4: Speaking notes are prose, not bullets

Speaking notes are written as full sentences meant to be spoken aloud. 
Bullet-point speaking notes tempt speakers to read from slides. Prose speaking 
notes create a natural speaking rhythm and force the agent to think about 
transitions and flow, not just content.

### Decision 5: Beamer file must compile before phase P8 is marked complete

A Beamer skeleton that doesn't compile is not useful. The beamer-script agent 
runs pdflatex and fixes errors before marking itself complete. This adds 
robustness at the cost of some additional compute.

### Decision 6: Q&A bank answers must be source-verified

Every Category A Q&A answer must cite a location in the source corpus. 
Answers drawn purely from training data may be wrong or outdated. This 
maintains the pipeline's Zero World Knowledge principle in the presentation 
branch, not just the research branch.

### Decision 7: No separate critique/reiteration phase for presentation branch

The presentation branch does not have a Phase P9 critique. The user approval 
gate at Phase P6 is the quality checkpoint. If the user wants to revise the 
knowledge base or Beamer file, they interact directly with the relevant agent. 
A full pipeline critique is overkill for a presentation workflow.

### Decision 8: Phases 1 and 2 artifacts are fully reusable

Running the presentation branch does not consume or modify Phases 1 and 2 
artifacts. A user who runs the presentation branch and later wants the research 
pipeline on the same topic starts directly at Phase 3 of the research branch.

---

*End of Presentation Branch Implementation Specification*
