# Research Workflow (v2)

An agentic research pipeline that produces either a **conference-grade empirical paper** or a **compilable oral presentation** from a topic string. Runs autonomously on Claude Code using a two-branch architecture.

---

## Workflows

### (A) Research Pipeline v2 — Conference-Grade Empirical Paper

> "Research [topic] for me"

Runs 16 phases end-to-end: source acquisition → literature analysis → gap scoring → hypotheses → experiment implementation → statistical analysis → final paper → critique.

**Phase map:**

| Phase | Agent | Output |
|---|---|---|
| 1 | `source-acquisition` | `sources/manifest.yaml` |
| 2 | `source-extraction` | `sources/*/content.md` |
| 3 | `literature-comprehension` | `analysis/literature-map.md` |
| 4 | `gap-analysis` | `analysis/gap-analysis.md` |
| 5 | `sanity-check` | `analysis/review-notes.md` |
| 6 | `hypothesis-formation` | `synthesis/hypotheses.md` |
| 7 | `methodology-design` | `synthesis/methodology.md` |
| 10 | `compute-probe` | `diagnostics/vm-profile.yaml` |
| 11 | `hypothesis-triage` | `experiments/triage.md` |
| 12 | `experiment-roadmap` ×3 | `experiments/H{n}/roadmap.md` |
| 13 | `experiment-coder` + `experiment-reviewer` loop | `experiments/H{n}/results/` |
| 14 | `experiment-analyst` | `experiments/H{n}/analysis.md` |
| 15 | `final-paper-assembly` | `synthesis/final-paper.md` |
| 16 | `critique-v2` | `reiteration/critique.md` |

---

### (B) Oral Presentation Branch — Beamer LaTeX + Knowledge Base

> "Prepare a talk on [topic]"

Runs Phases 1–2 (shared), then P3–P8. Produces a slide-by-slide outline, a full speaker knowledge base, and a compilable LaTeX Beamer file. No experiments or paper.

**Additional inputs required at Step 0:**
- Talk duration (minutes)
- Audience type: `domain_experts` / `mixed_academic` / `general`
- Goal: `survey` / `argue_position` / `introduce_open_problems` / `present_result`
- Venue: `conference_talk` / `seminar` / `lecture` / `defense`
- Q&A format: `during_talk` / `after_only`

**Phase map:**

| Phase | Agent | Output |
|---|---|---|
| 1–2 | (shared with research branch) | `sources/` |
| P3 | `audience-literature` | `analysis/audience-map.md` |
| P4 | `key-findings` | `analysis/key-findings.md` |
| P5 | `open-questions` | `analysis/open-questions.md` |
| P6 | `talk-architecture` ← **USER APPROVAL** | `synthesis/talk-architecture.md` |
| P7 | `knowledge-base` | `synthesis/knowledge-base.md` |
| P8 | `beamer-script` | `synthesis/beamer-script.tex` |

---

## Project Structure

```
Research-Workflow/
├── .claude/
│   ├── agents/                      # All agent definitions (flat — both branches)
│   │   ├── source-acquisition.md    # Phase 1
│   │   ├── source-extraction.md     # Phase 2
│   │   ├── literature-comprehension.md
│   │   ├── gap-analysis.md
│   │   ├── sanity-check.md
│   │   ├── hypothesis-formation.md
│   │   ├── methodology-design.md
│   │   ├── compute-probe.md
│   │   ├── hypothesis-triage.md
│   │   ├── experiment-roadmap.md
│   │   ├── experiment-coder.md
│   │   ├── experiment-reviewer.md
│   │   ├── experiment-analyst.md
│   │   ├── final-paper-assembly.md
│   │   ├── critique-v2.md
│   │   ├── colab-notebook-generator.md
│   │   ├── clean-run.md
│   │   ├── diagnostics-summary.md
│   │   ├── audience-literature.md   # Phase P3 (presentation branch)
│   │   ├── key-findings.md          # Phase P4
│   │   ├── open-questions.md        # Phase P5
│   │   ├── talk-architecture.md     # Phase P6
│   │   ├── knowledge-base.md        # Phase P7
│   │   └── beamer-script.md         # Phase P8
│   ├── skills/                      # Skill modules (SKILL.md per skill)
│   │   ├── source-integrity/
│   │   ├── writing-style/
│   │   ├── markdown-conventions/
│   │   ├── web-source-fetching/
│   │   ├── source-management/
│   │   ├── source-lookup/
│   │   ├── literature-analysis/
│   │   ├── gap-scoring-rubric/
│   │   ├── methodology-standards/
│   │   ├── experiment-execution/
│   │   ├── vm-interaction/
│   │   ├── audience-synthesis/      # Presentation branch
│   │   └── talk-design/             # Presentation branch
│   ├── hooks/
│   │   └── pipeline-logger.sh
│   ├── rules/
│   │   └── portable-env.md
│   └── settings.json
├── CLAUDE.md                        # Orchestrator instructions
├── pipeline-state.yaml              # Progress tracker
├── sources/                         # Downloaded sources (shared across runs)
│   ├── manifest.yaml
│   └── {arxiv-id}/
│       └── content.md
├── user-sources/                    # Drop PDFs here before running
├── analysis/                        # Intermediate analysis outputs
├── synthesis/                       # Final deliverables
├── experiments/                     # Experiment scripts, results, notebooks
├── reiteration/                     # Critique and reiteration plan
├── diagnostics/                     # Logs and VM profile
└── scripts/                         # Source extraction utilities
```

---

## Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Requires a `.env` file with:
```
MISTRAL_API_KEY=...   # for PDF OCR (Phase 2)
```

---

## Source Extraction Tools

The `scripts/` folder contains utilities for downloading sources as clean Markdown.

### PDF → Markdown (via Mistral OCR)

```bash
.venv/bin/python scripts/mistral_ocr.py document.pdf -o sources/output/
```

### Static Web Pages

```bash
.venv/bin/python scripts/webpage_to_md.py "https://example.com/page" -o sources/example/
```

### Authenticated / JS-Heavy Pages

```bash
.venv/bin/python scripts/authenticated_extract.py "https://example.com/page" -s "article"
```

### ArXiv Papers

```bash
curl -sL "https://arxiv.org/pdf/2010.11929" -o sources/arxiv-2010.11929/paper.pdf
.venv/bin/python scripts/mistral_ocr.py sources/arxiv-2010.11929/paper.pdf -o sources/arxiv-2010.11929/
```

