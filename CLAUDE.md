# Research Workflow — Orchestrator Instructions (v2)

## Core Rules (Apply to All Tasks)
- Always provide verification (tests, scripts, screenshots). If you can't verify it, don't ship it.
- Scope investigations narrowly or use subagents so the exploration doesn't consume your main context.
- Python: always use `.venv/bin/python` — never bare `python`.
- Read `.claude/rules/portable-env.md` before any terminal commands.

---

## Which Workflow to Use?

| User says... | Use |
|-------------|-----|
| "Research [topic] for me" (one-command) | **Research Pipeline v2** — 16-phase pipeline with experiments |
| "Write a textbook chapter on [topic]" | **Textbook Chapter** — legacy slash-command workflow |
| "Analyze sources in [folder]" | **Textbook Chapter** — `/analyze-sources` agent |

---

# PART A: Research Pipeline v2 (Conference-Grade Empirical Paper)

The research pipeline produces an empirical research paper: literature map, gap analysis, hypotheses, actual experimental results, statistical analysis, and full assembled paper. Autonomous through Phase 7; planning + execution phases follow; human decision required before reiteration.

## Quick Start

> "Research [topic] for me"

Orchestrator runs the full pipeline:
1. Research Phase (Phases 1–7): ~1 hour
2. Planning Phase (Phases 10–12): ~20 minutes
3. Execution Phase (Phases 13–14): variable (hours to days, may require user Colab interaction)
4. Assembly Phase (Phases 15–16): ~30 minutes
5. Surface critique to user for reiteration decision

## Pipeline Phase Map

```
═══════════════════════════════════════════════════════
RESEARCH PHASE (Phases 1–7) — modified from v1
═══════════════════════════════════════════════════════

Phase 1:  Source Acquisition        → sources/manifest.yaml
Phase 2:  Source Extraction         → sources/*/content.md
Phase 3:  Literature Comprehension  → analysis/literature-map.md
Phase 4:  Gap Analysis              → analysis/gap-analysis.md
Phase 5:  Sanity Check (advisory)   → analysis/review-notes.md
Phase 6:  Hypothesis Formation      → synthesis/hypotheses.md
Phase 7:  Methodology Design        → synthesis/methodology.md

═══════════════════════════════════════════════════════
PLANNING PHASE (Phases 10–12) — NEW in v2
═══════════════════════════════════════════════════════

Phase 10: Compute Probe             → diagnostics/vm-profile.yaml
Phase 11: Hypothesis Triage         → experiments/triage.md
Phase 12: Experiment Roadmaps (×3)  → experiments/H{n}/roadmap.md

═══════════════════════════════════════════════════════
EXECUTION PHASE (Phases 13–14) — NEW in v2, runs 3×
═══════════════════════════════════════════════════════

  For each of the 3 selected hypotheses:

  Phase 13: Experiment Loop         → experiments/H{n}/results/
            (coder + reviewer in loop until base case met
             or Colab gate hit → user action → resume)

  Phase 14: Results Analysis        → experiments/H{n}/analysis.md

═══════════════════════════════════════════════════════
ASSEMBLY PHASE (Phases 15–16) — replaces v1 Phases 8–9
═══════════════════════════════════════════════════════

Phase 15: Final Paper Assembly      → synthesis/final-paper.md
Phase 16: Critique + Reiteration    → reiteration/critique.md
```

Phases 8 and 9 are intentionally skipped to preserve backward compatibility with v1 artifacts.

## Pipeline Orchestration

### Step 1 — Initialize State

Create `pipeline-state.yaml` if it does not exist:

```bash
if [ ! -f pipeline-state.yaml ]; then
cat > pipeline-state.yaml << 'EOF'
topic: "{TOPIC}"
started: "{TIMESTAMP}"
current_phase: 1
reiteration: 0
phases: {}
EOF
fi
```

Also create required directories:
```bash
mkdir -p analysis/ synthesis/ reiteration/ diagnostics/ user-sources/ experiments/
```

### Step 2 — Research Phase (Phases 1–7)

Run each phase by spawning the corresponding subagent. The orchestrator ONLY reads `pipeline-state.yaml` between phases — never reads research content.

```
Phase 1 → source-acquisition     (sources/manifest.yaml)
Phase 2 → source-extraction      (sources/*/content.md)
Phase 3 → literature-comprehension (analysis/literature-map.md)
Phase 4 → gap-analysis           (analysis/gap-analysis.md)        [Opus]
Phase 5 → sanity-check           (analysis/review-notes.md)        [advisory]
Phase 6 → hypothesis-formation   (synthesis/hypotheses.md)
Phase 7 → methodology-design     (synthesis/methodology.md)
```

After each phase, verify `current_phase` incremented in `pipeline-state.yaml` before spawning the next.

### Step 3 — Planning Phase (Phases 10–12)

After Phase 7 completes, DO NOT spawn Phase 8 or Phase 9 (v1). Instead:

1. Spawn Phase 10 (compute-probe) → `diagnostics/vm-profile.yaml`
2. Read `pipeline-state.yaml`, verify Phase 10 complete
3. Spawn Phase 11 (hypothesis-triage) → `experiments/triage.md`
4. Read `experiments/triage.md`, extract `selected_hypotheses` list
5. For each hypothesis in `selected_hypotheses` (sequentially):
   - Spawn Phase 12 (experiment-roadmap) for this hypothesis

### Step 4 — Execution Phase (Phases 13–14)

For each selected hypothesis (sequentially):

```
LOOP (max 30 iterations):
  Spawn experiment-coder(H_n) → runs code, writes results
  Read experiments/H{n}/status.yaml

  IF status == "colab_needed":
    Spawn colab-notebook-generator(H_n) → experiments/H{n}/colab/notebook.ipynb
    PRINT to user: "Upload notebook, run cells, paste output to experiments/H{n}/colab-results/"
    WAIT for user confirmation
    UPDATE status.yaml → "colab_complete"
    CONTINUE loop

  IF status == "base_case_met":
    BREAK

  IF status == "failed_irrecoverable":
    LOG failure, BREAK (skip this hypothesis)

  Spawn experiment-reviewer(H_n) → experiments/H{n}/review.md
  CONTINUE loop

After loop: Spawn experiment-analyst(H_n) → experiments/H{n}/analysis.md
```

### Step 5 — Assembly Phase (Phases 15–16)

After all 3 hypotheses are done:
1. Spawn Phase 15 (final-paper-assembly) → `synthesis/final-paper.md`
2. Spawn Phase 16 (critique-v2) → `reiteration/critique.md` + `reiteration/reiteration-plan.md`
3. Surface both files to user

### Step 6 — Reiteration (Human-Gated)

After Phase 16 completes:
1. Surface `reiteration/critique.md` to user
2. Surface `reiteration/reiteration-plan.md` to user
3. **STOP and wait for user decision**

If user approves re-run:
```bash
git -C "${CLAUDE_PROJECT_DIR:-.}" checkout -b reiteration-1
```

The reiteration plan can target:
- **Research re-run:** Re-run Phases 1–7
- **Experiment re-run:** Re-run Phase 13 for a specific hypothesis
- **Document revision:** Re-run Phase 15 only

One reiteration maximum.

### Colab Interaction Protocol

When a hypothesis hits a COLAB_GATE, print to user:

```
=== COLAB ACTION REQUIRED ===

Hypothesis {H_n} step {step_name} requires a GPU.
A Colab notebook has been prepared.

1. Upload: experiments/H{n}/colab/{notebook_name}.ipynb
2. Runtime → Change runtime type → GPU (T4)
3. Run all cells
4. Download the output file(s) listed at the end of the notebook
5. Place them in: experiments/H{n}/colab-results/

Tell me when the results are ready.
===
```

STOP and WAIT for user confirmation.

## Resume from Checkpoint

If a run was interrupted, check `pipeline-state.yaml` and resume:

```bash
cat pipeline-state.yaml
```

### Resume Rules

| `status` of `current_phase` | Action |
|-----------------------------|--------|
| `complete` | Spawn the **next** phase. |
| `in_progress` | Re-run from scratch — output may be partial. |
| absent | Phase was never started. Spawn it. |

**Never skip a phase whose status is `in_progress`.**

### Resume Script

```bash
python3 -c "
import yaml, sys

with open('pipeline-state.yaml', encoding='utf-8') as f:
    state = yaml.safe_load(f)

current = state.get('current_phase', 1)
phases  = state.get('phases', {})
phase_state = phases.get(current, {})
status = phase_state.get('status', 'absent')

if status == 'complete':
    resume_at = current + 1
    # Skip phases 8-9 (v1 only)
    if resume_at in (8, 9):
        resume_at = 10
    print(f'Phase {current} is complete. Resume at phase {resume_at}.')
elif status == 'in_progress':
    resume_at = current
    print(f'Phase {current} was interrupted (in_progress). Re-running phase {resume_at}.')
else:
    resume_at = current
    print(f'Phase {current} was never started. Starting phase {resume_at}.')

print(f'RESUME_AT={resume_at}')
" 2>&1
```

---

# PART B: Textbook Chapter Workflow (Legacy — Slash Commands)

## The One-Command Workflow (Textbook Chapters)

**Give Claude a topic and it does everything automatically.** Example:

> "Research preference learning from human feedback for me"

Claude will:
1. Extract the topic, infer your prior knowledge and learning goals, choose an output folder
2. Run `/research-textbook-chapter` — which researches 30-40 sources, downloads them all, analyzes the literature, and produces `TEXTBOOK-PLAN.md`
3. Run `/write-textbook-chapter` — which writes the full chapter (5-6 sections, 1,500-2,000 words each) from the downloaded sources
4. Run `/edit-textbook-chapter` — which does a prose-quality pass and applies semantic coloring

**No confirmation needed at any step. Just give the topic.**

---

## Available Agents (Slash Commands)

| Command | What It Does | When to Use |
|---|---|---|
| `/research-textbook-chapter` | Deep research → downloads 30-40 sources → structured literature analysis → `TEXTBOOK-PLAN.md` | Starting a new topic from scratch |
| `/write-textbook-chapter` | Writes full chapter from `TEXTBOOK-PLAN.md`, 1,500-2,000 words/section | After research is done |
| `/edit-textbook-chapter` | Prose-quality editing pass + semantic coloring | After chapter is written |
| `/update-textbook-chapter` | Integrates new sources into an existing chapter surgically | When you find new papers to add |
| `/analyze-sources` | Runs structured literature analysis on already-downloaded sources | Standalone literature review or dissertation prep |
| `/deep-factual-search` | 40+ source rigorous research, outputs to chat with full source audit trail | One-off factual questions |
| `/pdf-to-md` | Converts PDF (handwritten or typeset) to Markdown | Converting lecture notes or papers |

---

## Source Integrity (Non-Negotiable)

The Zero World Knowledge Principle applies to all writing tasks:
- **Hard Ban (requires a downloaded source):** Direct quotes, statistics, named frameworks, specific claims about what authors said, paper titles/authors/venues/years
- **Acceptable (no source needed):** General domain knowledge, structural devices, common definitions

An `N/A` in the Local Path column of the Source Processing Log is **always a failure**.

---

## Folder Structure (v2)

```
Research-Workflow/
├── .claude/
│   ├── agents/                    # Agent definitions (v1 + v2)
│   ├── skills/                    # Skill directories (SKILL.md per skill)
│   ├── hooks/
│   │   └── pipeline-logger.sh
│   ├── rules/
│   │   └── portable-env.md
│   └── settings.json
├── CLAUDE.md                      # This file
├── sources/                       # Centralized, shared across all runs
│   ├── manifest.yaml
│   └── {source-dirs}/content.md
├── user-sources/                  # Drop user PDFs here before running
├── analysis/                      # Phase 3-5 output
│   ├── literature-map.md
│   ├── gap-analysis.md
│   └── review-notes.md
├── synthesis/                     # Phase 6-7 + 15 output
│   ├── hypotheses.md
│   ├── methodology.md
│   └── final-paper.md
├── experiments/                   # Phases 10-14 output (NEW in v2)
│   ├── triage.md
│   └── H{n}/
│       ├── roadmap.md
│       ├── status.yaml
│       ├── review.md
│       ├── error.log
│       ├── scripts/
│       ├── results/
│       │   ├── figures/
│       │   └── base_case_evaluation.json
│       ├── colab/
│       ├── colab-results/
│       └── analysis.md
├── reiteration/                   # Phase 16 output
│   ├── critique.md
│   └── reiteration-plan.md
├── diagnostics/                   # Hook output + VM profile
│   ├── vm-profile.yaml
│   └── pipeline-run.log
├── pipeline-state.yaml            # Progress tracker
└── scripts/                       # Python scripts
```

---

## Rules Files (Auto-loaded)

| File | What It Governs |
|---|---|
| `.claude/skills/source-integrity/SKILL.md` | Zero World Knowledge — every claim needs a source |
| `.claude/skills/writing-style/SKILL.md` | Sentence rhythm, given-new contract, AI tell avoidance |
| `.claude/skills/markdown-conventions/SKILL.md` | Folder structure, section naming, LaTeX formatting |
| `.claude/skills/web-source-fetching/SKILL.md` | Site-specific fetch strategies (arXiv PDFs) |
| `.claude/skills/source-management/SKILL.md` | Centralized `sources/` storage, naming conventions |
| `.claude/skills/source-lookup/SKILL.md` | Grep-first controlled access to raw sources (Phases 4-9) |
| `.claude/skills/literature-analysis/SKILL.md` | MECE theme organization, cross-paper synthesis |
| `.claude/skills/gap-scoring-rubric/SKILL.md` | 5-dimensional tiered gap scoring (v2) |
| `.claude/skills/methodology-standards/SKILL.md` | Implementation specifications, base cases |
| `.claude/skills/experiment-execution/SKILL.md` | Experiment directories, status tracking, coder-reviewer protocol |
| `.claude/skills/vm-interaction/SKILL.md` | SSH commands, file transfer, VM environment rules |
