# Research Workflow — Claude Code Instructions


## Core Rules (Apply to All Tasks)
- Always provide verification (tests, scripts, screenshots). If you can't verify it, don't ship it.
- Scope investigations narrowly or use subagents so the exploration doesn't consume your main context.

---

## The One-Command Workflow

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
| `source-integrity.md` | Zero World Knowledge principle — every specific claim requires a downloaded source |
| `writing-style.md` | Sentence rhythm, given-new contract, AI tell avoidance, emphasis hierarchy, inline citations |
| `markdown-conventions.md` | Folder structure, section file naming, LaTeX formatting, per-section source headers |
| `visualization-standards.md` | Image priority order (source images > D2 > hvplot > web > generate_image) |
| `source-management.md` | Centralized `sources/` storage, folder naming conventions, PDF figure conversion |
| `web-source-fetching.md` | Site-specific fetch strategies (arXiv, blogs, d2l.ai, Substack, PDFs) |
| `high-quality-blogs.md` | Curated registry of 30+ textbook-quality technical blogs — searched first during research |
| `semantic-coloring.md` | WCAG AA color palette, concept color-coding rules for equations and prose |
| `python-env.md` | Always use `.venv/bin/python` — never bare `python` or system Python |
| `force_verbosity.md` | Default section length: 1,500-2,000 words. Length from depth, never repetition. |

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
├── sources/                          ← Centralized, shared across all chapters
│   ├── arxiv-{PAPER_ID}/             ← arXiv papers (LaTeX source)
│   └── {domain}/{path}/              ← All other sources
├── {Subject Area}/
│   ├── {Topic Name}.md               ← Index file (links to sections)
│   └── {Topic Name}/
│       ├── TEXTBOOK-PLAN.md          ← Research plan (do not edit manually)
│       ├── _01-introduction.md
│       ├── _02-...md
│       └── _99-closing.md
├── .claude/
│   ├── agents/                       ← Slash command agents
│   └── rules/                        ← Rules files (auto-read by agents)
└── scripts/                          ← Python extraction scripts
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
