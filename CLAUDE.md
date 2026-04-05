# Research Workflow — Orchestrator Instructions

## Core Rules (Apply to All Tasks)
- Always provide verification (tests, scripts, screenshots). If you can't verify it, don't ship it.
- Scope investigations narrowly or use subagents so the exploration doesn't consume your main context.
- Python: always use `.venv/bin/python` — never bare `python`.
- Read `.claude/rules/portable-env.md` before any terminal commands.

---

## Which Workflow to Use?

| User says... | Use |
|-------------|-----|
| "Research [topic] for me" (one-command) | **Research Pipeline** — 9-phase sequential subagent chain |
| "Write a textbook chapter on [topic]" | **Textbook Chapter** — legacy slash-command workflow |
| "Analyze sources in [folder]" | **Textbook Chapter** — `/analyze-sources` agent |

---

# PART A: Research Pipeline (New — 9-Phase, Conference-Grade)

The research pipeline produces a conference-grade research document: literature map, gap analysis, hypotheses, experimental methodology, and full assembled document. Fully autonomous on first pass; human decision required before reiteration.

## Quick Start

> "Research [topic] for me"

Orchestrator steps (run without confirmation):
1. Initialize `pipeline-state.yaml`
2. Spawn Phase 1-9 subagents sequentially
3. Surface Phase 9 critique to user
4. Wait for user decision on reiteration

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
mkdir -p analysis/ synthesis/ reiteration/ diagnostics/ user-sources/
```

### Step 2 — Sequential Phase Execution

Run each phase by spawning the corresponding subagent. The orchestrator ONLY reads `pipeline-state.yaml` between phases — never reads research content.

```
Phase 1 → source-acquisition     (sources/manifest.yaml)
Phase 2 → source-extraction      (sources/*/content.md)
Phase 3 → literature-comprehension (analysis/literature-map.md)
Phase 4 → gap-analysis           (analysis/gap-analysis.md)        [Opus]
Phase 5 → sanity-check           (analysis/review-notes.md)        [advisory]
Phase 6 → hypothesis-formation   (synthesis/hypotheses.md)
Phase 7 → methodology-design     (synthesis/methodology.md)
Phase 8 → document-assembly      (synthesis/final-document.md)
Phase 9 → critique               (reiteration/critique.md + reiteration-plan.md)  [Opus]
```

After each phase, verify `current_phase` incremented in `pipeline-state.yaml` before spawning the next.

### Step 3 — Reiteration (Human-Gated)

After Phase 9 completes:
1. Surface `reiteration/critique.md` to user
2. Surface `reiteration/reiteration-plan.md` to user
3. **STOP and wait for user decision**

If user approves re-run:
```bash
git -C "${CLAUDE_PROJECT_DIR:-.}" checkout -b reiteration-1
# Update pipeline-state.yaml to point to the weakest phase
# Spawn agents from that phase forward
```

One reiteration maximum. If second pass still has issues, note for manual review.

## Resume from Checkpoint

If a run was interrupted, check `pipeline-state.yaml` and resume:
```bash
cat pipeline-state.yaml
# current_phase tells you where to resume
```

Do NOT re-run completed phases (their git commits exist). Start from `current_phase`.

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
| `/analyze-sources` | Runs structured literature analysis (intake, gaps, knowledge map, synthesis) on already-downloaded sources | Standalone literature review or dissertation prep |
| `/deep-factual-search` | 40+ source rigorous research, outputs to chat with full source audit trail | One-off factual questions, not chapter-writing |
| `/pdf-to-md` | Converts PDF (handwritten or typeset) to Markdown | Converting lecture notes or papers |

---

## Full Automated Pipeline

> **Depth:** This pipeline is tuned for final-year thesis research. Default source counts (40-60), mandatory Tier 2 analyses, and citation-chain tracing reflect the academic rigour expected of thesis-level work.

When the user gives a topic with no other instructions, run this full pipeline autonomously:

### Step 1 — Infer Parameters
Extract from the user's message (or infer defaults):
- **Topic:** The subject to research
- **Prior Knowledge:** What the user likely knows (infer from context, or default to "strong technical background, new to this specific topic")
- **Learning Goals:** Default to "deep understanding sufficient to apply the concepts"
- **Target Depth:** Default to Graduate
- **Output Folder:** Infer from topic (e.g., "preference learning" → `Preference Learning/Learning from Human Feedback/`)

### Step 2 — Research (30-40 sources + structured analysis)
Run `/research-textbook-chapter` with the inferred parameters. This produces:
- Downloaded sources in `sources/` (centralized)
- Source analysis: clusters, contradictions, research gaps, knowledge map, master synthesis
- `TEXTBOOK-PLAN.md` with section plans, source image catalog, notation table

### Step 3 — Write (5-6 sections, ~10,000 words)
Run `/write-textbook-chapter` pointing to the `TEXTBOOK-PLAN.md` from Step 2. This produces:
- `[Topic]/[Topic Name].md` — index file
- `[Topic]/[Topic Name]/_01-introduction.md` through `_99-closing.md` — section files
- Images copied from `sources/` into chapter folder

### Step 4 — Edit (prose quality + semantic coloring)
Run `/edit-textbook-chapter` pointing to the index file from Step 3. This:
- Fixes sentence rhythm, given-new flow, AI tells, emphasis hierarchy
- Applies semantic color-coding (3-5 colors per chapter, WCAG AA compliant)

### What "autonomous" means
- Do NOT ask the user to confirm steps 2-4
- Do NOT ask which folder to use (infer it)
- Do NOT stop between steps unless a scope expansion is genuinely needed
- Brief chat progress updates are fine (e.g., "✓ 32 sources downloaded, starting plan")

---

## Rules Files (Auto-loaded)

All agents re-read these rules from disk at the start of each task. They are not optional:

| File | What It Governs |
|---|---|
| `.claude/skills/source-integrity/SKILL.md` | Zero World Knowledge principle — every specific claim requires a downloaded source |
| `.claude/skills/writing-style/SKILL.md` | Sentence rhythm, given-new contract, AI tell avoidance, emphasis hierarchy, inline citations |
| `.claude/skills/markdown-conventions/SKILL.md` | Folder structure, section file naming, LaTeX formatting, per-section source headers |
| `.claude/skills/web-source-fetching/SKILL.md` | Site-specific fetch strategies (arXiv, PDFs) |
| `.claude/skills/source-management/SKILL.md` | Centralized `sources/` storage, folder naming conventions, PDF figure conversion |
| `.claude/skills/source-lookup/SKILL.md` | Grep-first controlled access to raw sources (Phases 4-9) |
| `.claude/skills/literature-analysis/SKILL.md` | MECE theme organization, cross-paper synthesis |
| `.claude/skills/gap-scoring-rubric/SKILL.md` | Tiered gap scoring criteria, validation protocol |
| `.claude/skills/methodology-standards/SKILL.md` | DOE best practices, experimental design templates |
| `content/maybe-rules/visualization-standards.md` | Image priority order (source images > D2 > hvplot > web > generate_image) |
| `content/maybe-rules/semantic-coloring.md` | WCAG AA color palette, concept color-coding rules for equations and prose |
| `content/maybe-rules/force_verbosity.md` | Default section length: 1,500-2,000 words. Length from depth, never repetition. |

---

## Source Integrity (Non-Negotiable)

The Zero World Knowledge Principle applies to all writing tasks:
- **Hard Ban (requires a downloaded source):** Direct quotes, statistics, named frameworks, specific claims about what authors said, paper titles/authors/venues/years
- **Acceptable (no source needed):** General domain knowledge, structural devices, common definitions, pointing to well-known people as examples

An `N/A` in the Local Path column of the Source Processing Log is **always a failure**. Every source must be downloaded before writing begins.

---

## Folder Structure

```
Research-Workflow/
├── .claude/
│   ├── agents/           ← 9-phase research pipeline agents
│   ├── skills/           ← 9 skill directories (SKILL.md per skill)
│   ├── hooks/
│   │   └── pipeline-logger.sh
│   ├── rules/
│   │   └── portable-env.md
│   └── settings.json     ← Hook configurations
├── sources/              ← Centralized, shared across all chapters and runs
│   ├── arxiv-{PAPER_ID}/ ← arXiv papers (LaTeX source)
│   └── {domain}/{path}/  ← All other sources
├── analysis/             ← Phase 3-5 output (per-run)
├── synthesis/            ← Phase 6-8 output (per-run)
├── reiteration/          ← Phase 9 output (per-run)
├── diagnostics/          ← Hook output (per-run)
├── user-sources/         ← Drop user PDFs here before running
├── pipeline-state.yaml   ← Created per-run (tracks progress)
├── {Subject Area}/       ← Textbook chapter output (legacy workflow)
│   ├── {Topic Name}.md   ← Index file (links to sections)
│   └── {Topic Name}/
│       ├── TEXTBOOK-PLAN.md
│       ├── _01-introduction.md
│       └── _99-closing.md
├── content/
│   └── agents/           ← Textbook chapter slash-command agents (legacy)
└── scripts/              ← Python extraction scripts
```

---

## Editing Existing Chapters

To update an existing chapter with new sources:
> "Update [chapter path] with these new sources: [URL1], [URL2]"

Claude runs `/update-textbook-chapter`, which:
1. Downloads new sources
2. Runs source analysis (Phase 1D) restricted to new sources vs. existing content
3. Surgically integrates new material without rewriting existing sections
4. Updates TEXTBOOK-PLAN.md to record the change

To do a prose-quality editing pass on an existing chapter:
> "Edit [chapter index path]"

---

## Literature Analysis (Without Writing)

For dissertation work or research without chapter-writing:
> "Analyze the sources in [folder] — I want the knowledge map, research gaps, and contradictions"

Claude runs `/analyze-sources`, which produces structured analysis outputs to chat:
- Intake Protocol (clusters, core claims, direct contradictions)
- Gap Scanner (5 most significant research gaps with root causes)
- Knowledge Map (central claim, pillars, contested zones, frontier questions)
- Master Synthesis (400-word field-level synthesis)

Add `contradictions`, `assumptions`, or `methodology` flags for Tier 2 analyses.
