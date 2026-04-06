# Research Workflow Architecture — Complete Handoff Document

> **Purpose:** This document captures the complete system design for an automated graduate-level research pipeline built on Claude Code. It is the single source of truth for implementation. Everything discussed during the design phase is recorded here.
>
> **Status:** Design complete. Ready for implementation.
>
> **Last updated:** April 5, 2026

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Goals and Constraints](#2-system-goals-and-constraints)
3. [Architecture Overview](#3-architecture-overview)
4. [Pipeline Phases — Detailed Specifications](#4-pipeline-phases--detailed-specifications)
5. [Checkpoint and State Management](#5-checkpoint-and-state-management)
6. [Source-Lookup Skill — Controlled Source Access](#6-source-lookup-skill--controlled-source-access)
7. [Reiteration Loop Design](#7-reiteration-loop-design)
8. [Logging and Diagnostics](#8-logging-and-diagnostics)
9. [Git Checkpoint Strategy](#9-git-checkpoint-strategy)
10. [Skills Specifications](#10-skills-specifications)
11. [IDE Compatibility](#11-ide-compatibility--claude-code-vs-vs-code-copilot)
12. [Directory Structure](#12-directory-structure--complete-file-tree)
13. [Implementation Plan — Sprints](#13-implementation-plan--sprints)
14. [Architecture Decisions Log](#14-architecture-decisions-log)
15. [Reference Documentation](#15-reference-documentation)
16. [Original Requirements](#16-original-requirements)

---

## 1. Executive Summary

### What this system does

Given a niche research topic (e.g., "Dual Convex Optimization in ReLU Neural Networks"), the system autonomously:

1. Finds and downloads 30-40 relevant papers
2. Extracts them into normalized, parsable markdown
3. Builds a comprehensive literature map (themes, timeline, consensus, contested areas)
4. Identifies research gaps with tiered confidence scoring
5. Runs a skeptical sanity-check review
6. Formulates testable hypotheses
7. Designs experimental methodology / DOE for each hypothesis
8. Assembles a conference-grade research document
9. Self-critiques and identifies the weakest phase for reiteration

### Architecture in one sentence

A sequential subagent chain where the orchestrator (main context) spawns one subagent per phase, each writing structured output to disk before dying. The orchestrator reads only a ~20-line state file to decide what to chain next.

### Key design principles

- **Depth + Accuracy > Breadth > Novelty** — for niche fields with 30-40 papers
- **Context rot prevention** — agents read compressed artifacts, not raw sources
- **Resumability** — git commits after every phase; crash recovery from any point
- **Budget-conscious** — designed for Claude Pro; Sonnet everywhere except Phases 4 and 9 (Opus)
- **Quality at every step** — each phase optimizes for a specific quality dimension (MECE)
- **Reiteration over perfection** — first pass runs autonomously; critique surfaces issues for human-approved re-run

---

## 2. System Goals and Constraints

### Quality Model

Quality is optimized per-phase, with each phase targeting a specific dimension:

| Phase | Primary quality dimension | Secondary |
|-------|--------------------------|-----------|
| 1. Source Acquisition | Coverage completeness | — |
| 2. Source Extraction | Extraction accuracy (math, figures, citations) | — |
| 3. Literature Comprehension | Depth of understanding | MECE organization |
| 4. Gap Analysis | Analytical rigor | Confidence calibration |
| 5. Sanity Check | Skepticism, feasibility assessment | — |
| 6. Hypothesis Formation | Testability, falsifiability | Rigor |
| 7. Methodology / DOE | Feasibility, experimental validity | — |
| 8. Document Assembly | Prose quality, conference-grade formatting | Coherent narrative |
| 9. Critique | Diagnostic accuracy | Actionable reiteration plan |

### Gap-Finding Philosophy

The system uses a tiered scoring system for research gaps:

- **Tier 1 — Fundamental gaps:** Unanswered questions that address core assumptions. High impact but may be hard to verify.
- **Tier 2 — Extensions:** Natural extensions of existing work. Moderate impact, higher confidence of existence.
- **Tier 3 — Stress-tests:** Testing whether current solutions hold under different conditions. Lower novelty, highest verifiability.

The system aims for Tier 1 but gracefully degrades to Tier 2/3. The key constraint is verifiability: can we confirm this gap exists from the literature? Each gap must have a "confidence of gap existence" metric alongside "potential impact."

### Constraints

- **Budget:** Claude Pro (not API). Standard Claude Code context window per session.
- **Context per subagent:** Target 60-70% of context capacity, with explicit disk checkpoints before any compaction risk.
- **Token efficiency:** Orchestrator never holds research content. It reads only pipeline-state.yaml (~20 lines).
- **Unit of research:** Niche topics with ~30-40 papers. Not broad surveys.
- **Interaction model:** Fully autonomous on first pass. Reiteration surfaces critique to user before re-running.

### The Zero World Knowledge Resolution

The "Zero World Knowledge" rule is split by phase type:

- **During writing/claim-making (Phase 8):** Every specific claim requires a downloaded source.
- **During analysis/gap-finding (Phase 4):** The model may use training knowledge to hypothesize gaps, but those hypotheses must be validated against the literature map. Unverified gaps are marked as such.
- **The sanity-check agent (Phase 5):** Partly catches cases where a "gap" is actually something the model missed in the sources.

---

## 3. Architecture Overview

### Orchestration Model

Sequential subagent chain. The orchestrator (main Claude Code session) chains subagents one-by-one. No nesting. No Agent Teams.

```
Orchestrator (main context — stays lean)
    |— spawns Phase 1 subagent -> writes to disk -> dies
    |— reads state, spawns Phase 2 -> writes to disk -> dies
    |— reads state, spawns Phase 3 -> writes to disk -> dies
    |— ... through Phase 8 ...
    |— spawns Phase 9 (Critique) -> writes critique -> dies
    |— surfaces critique to user
    |— user approves re-run plan
    |— re-runs from identified phase on git branch
```

### Why Sequential Subagents

- Agent Teams (experimental) add token cost and coordination overhead unnecessary for a sequential pipeline.
- Parallel subagents evaluated and rejected: for 30-40 papers, extraction is I/O-bound (bash/network), not reasoning-bound. Comprehension (Phase 3) requires common context to find cross-paper connections.
- Subagents cannot spawn other subagents in Claude Code, so the "Interim Manager" tier from the original PRD was simplified to 2 tiers: orchestrator + workers.

### Model Allocation

| Phase | Model | Rationale |
|-------|-------|-----------|
| Orchestrator | Sonnet | Just a router |
| Phases 1-3 | Sonnet | Mechanical work |
| Phase 4 (Gap Analysis) | **Opus** | Critical thinking — must distinguish real gaps from missed papers |
| Phase 5 | Sonnet | Skeptical review — sufficient with good prompt |
| Phases 6-7 | Sonnet | Synthesis — well-structured input |
| Phase 8 | Sonnet | Writing quality driven by skills |
| Phase 9 (Critique) | **Opus** | Must evaluate entire pipeline and identify weakest link |
| Diagnostics | Haiku | Just formatting data |

---

## 4. Pipeline Phases — Detailed Specifications

### Phase 1: Source Acquisition

```yaml
# .claude/agents/source-acquisition.md frontmatter
name: source-acquisition
description: Searches for and downloads research papers for a given topic.
model: Claude Sonnet 4.6 (copilot)
tools: Bash, Read, Write, Glob, Grep
permissionMode: acceptEdits
memory: project
color: blue
skills:
  - web-source-fetching
  - source-management
```

- **Input:** Topic string + optional user-sources/ directory
- **Process:** Search arXiv, Semantic Scholar, Google Scholar. Download PDFs. Process user PDFs through Mistral OCR. Index into manifest.yaml.
- **Output:** sources/manifest.yaml (index of all sources with metadata)
- **Context budget:** ~40%
- **User PDFs:** Agent checks user-sources/ directory for PDFs placed by user before running. Processed through Mistral OCR into normalized markdown.

### Phase 2: Source Extraction

```yaml
name: source-extraction
description: Extracts content from downloaded sources into normalized markdown.
model: Claude Sonnet 4.6 (copilot)
tools: Bash, Read, Write, Glob
permissionMode: acceptEdits
color: blue
skills:
  - source-management
```

- **Input:** sources/manifest.yaml
- **Process:** For each source: arXiv LaTeX -> md, PDF -> Mistral OCR -> md, Web -> crawl4ai -> md. Validate math/figures/citations extracted correctly.
- **Output:** sources/{source-dir}/content.md per source, updated manifest.yaml
- **Context budget:** ~50%

### Phase 3: Literature Comprehension

```yaml
name: literature-comprehension
description: Reads all extracted sources and produces a comprehensive literature map.
model: Claude Sonnet 4.6 (copilot)
tools: Read, Write, Grep, Glob
permissionMode: acceptEdits
effort: high
color: teal
skills:
  - source-integrity
  - literature-analysis
```

- **Input:** All sources/*/content.md files (read sequentially)
- **Process:** Read each source, identify themes/methodologies/relationships, write single comprehensive literature map (~4-5K words). Organize by research themes (MECE), NOT by paper.
- **Output:** analysis/literature-map.md
- **Context budget:** ~70% (most intensive — holds multiple papers simultaneously)
- **MECE principle:** Each theme section is mutually exclusive. Collectively they cover the entire field.

### Phase 4: Gap Analysis + Scoring

```yaml
name: gap-analysis
description: Identifies and scores research gaps from the literature map.
model: Claude Opus 4.6 (copilot)
tools: Read, Write, Grep
permissionMode: acceptEdits
effort: high
color: teal
skills:
  - gap-scoring-rubric
  - source-lookup
```

- **Input:** analysis/literature-map.md (~4-5K words)
- **Process:** Identify gap candidates using literature map AND training knowledge. Validate each against literature map. Score on: confidence of existence (0-10), potential impact (0-10), feasibility (0-10), verifiability (0-10). Source-lookup limit: 5 lookups.
- **Output:** analysis/gap-analysis.md (tiered gaps with scores and evidence)
- **Context budget:** ~60%
- **Why Opus:** Must distinguish "not studied" from "studied but agent missed it." Sonnet overconfident; Opus better calibrated.

### Phase 5: Sanity Check (Advisory)

```yaml
name: sanity-check
description: Fresh-eyes skeptical review. Advisory only — never blocks the pipeline.
model: Claude Sonnet 4.6 (copilot)
tools: Read, Write, Grep
permissionMode: acceptEdits
color: yellow
skills:
  - source-lookup
```

- **Input:** analysis/literature-map.md + analysis/gap-analysis.md (~7K words)
- **Process:** Fresh-eyes review. Check gaps are real, assess feasibility, verify consistency. Source-lookup limit: 5 lookups.
- **Output:** analysis/review-notes.md (concerns, alternative interpretations, feasibility flags)
- **Context budget:** ~40%
- **System prompt directive:** "You are a skeptical reviewer. Assume every gap claim might be wrong. You do NOT have authority to stop the pipeline."

### Phase 6: Hypothesis Formation

```yaml
name: hypothesis-formation
description: Formulates testable hypotheses from validated research gaps.
model: Claude Sonnet 4.6 (copilot)
tools: Read, Write
permissionMode: acceptEdits
effort: high
color: purple
skills:
  - source-lookup
```

- **Input:** analysis/gap-analysis.md + analysis/review-notes.md
- **Process:** For each viable gap (Tier 1 and 2, adjusted by sanity-check), formulate testable hypotheses. Each: specific, falsifiable, connected to identified gap. Source-lookup limit: 3.
- **Output:** synthesis/hypotheses.md
- **Context budget:** ~50%

### Phase 7: Methodology / DOE

```yaml
name: methodology-design
description: Designs experimental methodology and DOE for each hypothesis.
model: Claude Sonnet 4.6 (copilot)
tools: Read, Write, Bash
permissionMode: acceptEdits
effort: high
color: purple
skills:
  - methodology-standards
  - source-lookup
```

- **Input:** synthesis/hypotheses.md + analysis/literature-map.md (for methodological precedents)
- **Process:** For each hypothesis: experimental setup, baselines, metrics, data requirements, expected results, confounds, effort estimate. Source-lookup limit: 3.
- **Output:** synthesis/methodology.md
- **Context budget:** ~60%

### Phase 8: Document Assembly

```yaml
name: document-assembly
description: Assembles the final research document from all pipeline artifacts.
model: Claude Sonnet 4.6 (copilot)
tools: Read, Write, Grep, Glob
permissionMode: acceptEdits
effort: high
color: teal
skills:
  - writing-style
  - source-integrity
  - markdown-conventions
  - source-lookup
```

- **Input:** ALL structured artifacts
- **Process:** Write conference-grade prose. Format citations. Ensure narrative flow. Source-lookup: 5 lookups for exact formulations.
- **Output:** synthesis/final-document.md
- **Document structure:** Executive Summary -> Literature Review -> Key Paper Summaries (5-8 papers) -> Gap Analysis -> Hypotheses -> Methodology -> References
- **Context budget:** ~70%

### Phase 9: Critique + Reiteration

```yaml
name: critique
description: Evaluates entire pipeline output, identifies weakest phase, produces reiteration plan.
model: Claude Opus 4.6 (copilot)
tools: Read, Write
permissionMode: acceptEdits
color: red
skills:
  - source-lookup
```

- **Input:** ALL structured artifacts + diagnostics/source-lookups.log (~15-20K words)
- **Process:** Evaluate each phase for completeness, accuracy, consistency, logical soundness. Identify single weakest phase. Produce re-run instructions.
- **Output:** reiteration/critique.md + reiteration/reiteration-plan.md
- **Context budget:** ~50%
- **Surfaces to user before any re-run.**

---

## 5. Checkpoint and State Management

### Core Principle

Agents never read raw source PDFs — they read structured summaries from the previous agent. This is the compression pipeline preventing context rot.

### pipeline-state.yaml

The orchestrator reads ONLY this file. It never reads research content.

```yaml
topic: "Dual Convex Optimization in ReLU Neural Networks"
started: "2026-04-05T14:00:00Z"
current_phase: 4
reiteration: 0
phases:
  1: { status: complete, output: sources/manifest.yaml, git_commit: abc1234 }
  2: { status: complete, output: sources/, git_commit: def5678 }
  3: { status: complete, output: analysis/literature-map.md, git_commit: ghi9012 }
  4: { status: in_progress }
```

### Artifact Frontmatter

Every structured output file includes:

```yaml
---
phase: 3
status: complete
timestamp: 2026-04-05T14:30:00Z
depends_on: [sources/manifest.yaml]
token_estimate: 4200
---
```

The token_estimate lets downstream agents budget context before reading.

---

## 6. Source-Lookup Skill

Phases 4-9 can verify claims against raw sources via a controlled, narrow interface.

### Protocol

1. Check sources/manifest.yaml for the source path
2. Use grep -n "keyword" to find the relevant section
3. Read ONLY 30-50 lines surrounding the match
4. Log every lookup to diagnostics/source-lookups.log

### Limits by Phase

| Phase | Max lookups |
|-------|-------------|
| 4 (Gap Analysis) | 5 |
| 5 (Sanity Check) | 5 |
| 6 (Hypothesis) | 3 |
| 7 (Methodology) | 3 |
| 8 (Document) | 5 |
| 9 (Critique) | 5 |

### Why Grep-First

A targeted 30-50 line read costs ~500 tokens. A full paper costs ~15K tokens. 30x difference.

---

## 7. Reiteration Loop Design

### Flow

```
Phase 1-8 run autonomously
    -> Phase 9 (Critique) reads all artifacts
    -> Produces critique.md + reiteration-plan.md
    -> Surfaces to user
    -> User approves (or modifies) re-run plan
    -> Orchestrator: git checkout -b reiteration-1
    -> Re-runs only specified phases
    -> Downstream phases cascade (their inputs changed)
```

### What the Critique Produces

**critique.md:** Per-phase assessment with scores, specific problems, and the weakest phase identified.

**reiteration-plan.md:** Exactly which phases to re-run, with specific updated instructions, and which phases cascade automatically.

### Budget

One reiteration cycle. Not infinite loops. If second pass still has issues, noted for manual attention.

---

## 8. Logging and Diagnostics

### Hook-based system using pipeline-logger.sh

Captures: SubagentStart, SubagentStop, PostToolUse, PreCompact events.

Output directory: diagnostics/
- pipeline-run.log (human-readable timeline)
- phase-metrics.yaml (machine-readable per-phase stats)
- source-lookups.log (from source-lookup skill)
- tool-calls.log (raw tool call log)

### PostCompact Context Injection

SessionStart hook with "compact" matcher re-injects pipeline-state.yaml into context after compaction.

### Diagnostics Summary Agent

Haiku model, 5 max turns. Reads diagnostics/ and formats a human-readable summary.

See Section 8 of the full architecture for complete hook script and settings.json configuration.

---

## 9. Git Checkpoint Strategy

After each phase: `git add . && git commit -m "phase-{N}-complete: {summary}"`

Enables: crash recovery (resume from last committed phase), reiteration branching (git branch before re-run), audit trail (git log shows sequence), comparison (git diff between original and reiteration).

---

## 10. Skills Specifications

| Skill | Used By | Purpose |
|-------|---------|---------|
| source-lookup | Phases 4-9 | Controlled access to raw sources (grep-first) |
| source-integrity | Phases 3, 4, 8 | Zero World Knowledge rules for claims |
| writing-style | Phase 8 | Sentence rhythm, AI-tell avoidance, prose quality |
| literature-analysis | Phase 3 | MECE theme organization, cross-paper synthesis |
| gap-scoring-rubric | Phase 4 | Tiered scoring criteria, validation protocol |
| web-source-fetching | Phase 1 | Site-specific fetch strategies |
| source-management | Phases 1, 2 | Folder naming, extraction conventions |
| markdown-conventions | Phase 8 | Citation format, heading structure |
| methodology-standards | Phase 7 | DOE best practices, experimental design templates |

---

## 11. IDE Compatibility — Claude Code vs VS Code Copilot

### Summary

Designed for Claude Code as primary runtime. VS Code Copilot as supported secondary.

### What works in both

- Agent definitions: VS Code reads .claude/agents/ natively
- Skills: Agent Skills open standard works across both
- Subagent spawning: Both support context-isolated subagents
- Model selection: Both support Claude models

### What degrades in VS Code

- SubagentStart/Stop hooks: Not documented in VS Code -> logging partially disabled
- PreCompact hooks: Not available -> no compaction monitoring
- permissionMode: May prompt for each file write -> pipeline interruptions
- skills: preloading in agents: Not documented -> skills loaded at runtime
- Auto-compaction control: Not available

### VS Code Advantages

- Handoffs: Interactive buttons for agent transitions (useful for Phase 9 -> User flow)
- Nested subagents (experimental): allowInvocationsFromSubagents setting

### Portability Rules

All scripts use $CLAUDE_PROJECT_DIR, project .venv, POSIX bash. No IDE-specific dependencies.

---

## 12. Directory Structure — Complete File Tree

```
Research-Workflow/
+-- .claude/
|   +-- agents/           (10 agent definitions)
|   +-- skills/           (9 skill directories, each with SKILL.md)
|   +-- hooks/
|   |   +-- pipeline-logger.sh
|   +-- rules/
|   |   +-- portable-env.md
|   +-- settings.json     (hook configurations)
+-- CLAUDE.md             (orchestrator instructions)
+-- ARCHITECTURE.md       (this document)
+-- scripts/              (extraction scripts from legacy system)
+-- pipeline-state.yaml   (created per-run)
+-- sources/              (Phase 1-2 output)
|   +-- manifest.yaml
|   +-- {source-dirs}/content.md
+-- user-sources/         (user drops PDFs here)
+-- analysis/             (Phase 3-5 output)
|   +-- literature-map.md
|   +-- gap-analysis.md
|   +-- review-notes.md
+-- synthesis/            (Phase 6-8 output)
|   +-- hypotheses.md
|   +-- methodology.md
|   +-- final-document.md
+-- reiteration/          (Phase 9 output)
|   +-- critique.md
|   +-- reiteration-plan.md
+-- diagnostics/          (hook output)
    +-- pipeline-run.log
    +-- phase-metrics.yaml
    +-- source-lookups.log
    +-- tool-calls.log
```

---

## 13. Implementation Plan — Sprints

### Sprint 1: Foundation

- [ ] Create .claude/ directory structure
- [ ] Write CLAUDE.md (orchestrator: read state, spawn agents, handle reiteration)
- [ ] Write pipeline-state.yaml schema
- [ ] Write pipeline-logger.sh hook script
- [ ] Write .claude/settings.json (all hooks)
- [ ] Write .claude/rules/portable-env.md
- [ ] Test: orchestrator creates state file, commits, reads back

### Sprint 2: Acquisition + Extraction (Phases 1-2)

- [ ] Write source-acquisition.md agent (full frontmatter + prompt)
- [ ] Write source-extraction.md agent
- [ ] Write web-source-fetching skill
- [ ] Write source-management skill
- [ ] Verify legacy scripts work with new directory structure
- [ ] Add user-PDF processing
- [ ] Test: run on real topic

### Sprint 3: Analysis Core (Phases 3-5)

- [ ] Write literature-comprehension.md agent
- [ ] Write gap-analysis.md agent
- [ ] Write sanity-check.md agent
- [ ] Write source-integrity skill
- [ ] Write literature-analysis skill
- [ ] Write gap-scoring-rubric skill
- [ ] Write source-lookup skill
- [ ] Test: run Phases 3-5 on real extracted sources

### Sprint 4: Synthesis + Reiteration (Phases 6-9)

- [ ] Write hypothesis-formation.md agent
- [ ] Write methodology-design.md agent
- [ ] Write document-assembly.md agent
- [ ] Write critique.md agent
- [ ] Write diagnostics-summary.md agent
- [ ] Write writing-style, markdown-conventions, methodology-standards skills
- [ ] Implement reiteration loop (git branching, selective re-run)
- [ ] Test: full end-to-end pipeline
- [ ] Test: reiteration flow

---

## 14. Architecture Decisions Log

1. **Sequential subagents over Agent Teams** — disk-based communication is simpler and more token-efficient for a pipeline where each phase feeds into the next.

2. **Opus for Phases 4 and 9 only** — these require the strongest analytical reasoning (gap validation and pipeline critique). All other phases work well with Sonnet + good skills.

3. **No parallel subagents** — for 30-40 papers, extraction is I/O-bound and comprehension benefits from common context.

4. **Tiered gap scoring with graceful degradation** — avoids fabricating "revolutionary" gaps. Always produces useful, verifiable output.

5. **Split Zero World Knowledge** — analysis can hypothesize with model knowledge; writing must cite sources. Sanity check catches unvalidated claims.

6. **Human-in-the-loop at reiteration only** — first pass autonomous for momentum; reiteration pauses because re-running is expensive.

7. **Claude Code primary, VS Code Copilot secondary** — Claude Code has full hook support, permission modes, and compaction control critical for the pipeline.

---

## 15. Reference Documentation

### Claude Code (Primary)

- Subagents: https://code.claude.com/docs/en/sub-agents
- Agent Teams: https://code.claude.com/docs/en/agent-teams
- Skills: https://code.claude.com/docs/en/skills
- Hooks Guide: https://code.claude.com/docs/en/hooks-guide
- Hooks Reference: https://code.claude.com/docs/en/hooks
- Settings: https://code.claude.com/docs/en/settings
- CLI Reference: https://code.claude.com/docs/en/cli-reference
- Tools Reference: https://code.claude.com/docs/en/tools-reference
- Environment Variables: https://code.claude.com/docs/en/env-vars

### VS Code Copilot (Secondary)

- Custom Agents: https://code.visualstudio.com/docs/copilot/customization/custom-agents
- Agent Skills: https://code.visualstudio.com/docs/copilot/customization/agent-skills
- Subagents: https://code.visualstudio.com/docs/copilot/agents/subagents
- Hooks: https://code.visualstudio.com/docs/copilot/customization/hooks
- Agent Concepts: https://code.visualstudio.com/docs/copilot/concepts/agents
- Memory: https://code.visualstudio.com/docs/copilot/agents/memory

### Agent Skills Standard

- https://agentskills.io/skill-creation/best-practices
- https://agentskills.io/specification

---

## 16. Original Requirements

### User Requirements (paraphrased)

1. Automate graduate-level research (topic -> lit review -> synthesis -> output) optimizing for quality
2. Modular architecture using subagents, skills, hooks, configurations
3. Quality: accuracy and depth > breadth > novelty; tiered gap finding
4. Reiteration loop that criticizes weakest step and re-runs with cascading changes
5. Sanity check: advisory only, fresh eyes, never blocks pipeline
6. Budget: Claude Pro, optimize context
7. IDE-agnostic: should run from VS Code Copilot too
8. Controlled source access for downstream agents (grep-first, hard limits)
9. Logging: per-agent diagnostics via hooks
10. User PDFs: accept user-provided PDFs with full extraction
11. Final output: conference-grade lit review + gap analysis + hypotheses + methodology + citations

### From Legacy System

- Slash-command agents replaced by modular subagents
- Rules files replaced by skills (more powerful)
- Python extraction scripts preserved
- New additions: reiteration loop, diagnostics, gap analysis pipeline

### From PRD (TODO.md)

- 3-tier agent hierarchy simplified to 2-tier (orchestrator + workers)
- Bias-check layer implemented as Phase 5 (advisory)
- Scoped directory access via tool restrictions and source-lookup skill
- Git commits for memory persistence implemented as phase checkpoints
- Experiments layer (upcoming scope) foundation laid by Phase 7

---

*End of Architecture Document*
