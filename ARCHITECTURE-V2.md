# Research Workflow Architecture v2 — Complete Redesign Document

> **Purpose:** This document is the single source of truth for redesigning the automated research pipeline. It captures everything: what exists, what's broken, what to change, what to add, and how to implement it. Hand this to Claude Code and it has everything it needs.
>
> **Status:** Ready for implementation.
>
> **Date:** April 6, 2026
>
> **Scope of change:** The pipeline evolves from "produce a research agenda document" to "produce an empirical research paper with actual experimental results."

---

## Table of Contents

1. [Run Retrospective — What Happened and Why](#1-run-retrospective)
2. [Design Philosophy Change](#2-design-philosophy-change)
3. [New Pipeline Structure — Complete Phase Map](#3-new-pipeline-structure)
4. [Changes to Existing Phases (1–7)](#4-changes-to-existing-phases)
5. [New Planning Phases (10–12)](#5-new-planning-phases)
6. [New Execution Phases (13–14) — The Experiment Loop](#6-new-execution-phases)
7. [New Assembly Phases (15–16) — Final Paper + Critique](#7-new-assembly-phases)
8. [Orchestrator Rewrite — CLAUDE.md](#8-orchestrator-rewrite)
9. [New Agent Definitions — Complete Specifications](#9-new-agent-definitions)
10. [New and Modified Skills](#10-new-and-modified-skills)
11. [Directory Structure v2](#11-directory-structure-v2)
12. [Experiment Directory Conventions](#12-experiment-directory-conventions)
13. [Colab Notebook Generation](#13-colab-notebook-generation)
14. [SSH and VM Interaction Conventions](#14-ssh-and-vm-interaction-conventions)
15. [Changes to Existing Scripts](#15-changes-to-existing-scripts)
16. [Implementation Sprint Plan](#16-implementation-sprint-plan)
17. [Architecture Decisions Log v2](#17-architecture-decisions-log-v2)

---

## 1. Run Retrospective

### What the first run produced (topic: "Dual Convex Optimization in ReLU Neural Networks")

The pipeline ran all 9 phases in ~70 minutes (23:51 → 01:00 UTC). Six user-provided PDFs carried the analysis. The output was a conference-grade research *proposal* document: literature map, gap analysis, 7 hypotheses, experimental methodology, and a self-critique.

### What went wrong, by severity

#### Severity 1 — Phase 1 acquisition is structurally broken

- 17 of 30 arXiv tarballs (57%) contained wrong papers. The `arxiv.org/src/{ID}` endpoint returned unrelated papers (F-theory physics, NMR, cosmology).
- The acquisition script (`scripts/phase1_search.py`) never verifies paper identity after download. It checks file size (>500 chars) but not content relevance.
- The pipeline survived only because the user pre-loaded 6 PDFs covering the core corpus.
- **Root cause:** arXiv source tarballs are unreliable. The paper ID in the URL sometimes resolves to a different paper's source bundle, especially for older or cross-listed papers.
- **Fix:** Switch to `arxiv.org/pdf/{ID}` + Mistral OCR. Always verify identity by grepping for title keywords in extracted content. Remove all blog/web source logic — papers only.

#### Severity 2 — The pipeline produces a theoretical research agenda, not empirical work

- H1 and H2 require inventing new mathematical proofs (extending duality theory to new settings). These are multi-year PhD-level problems, not pre-doctoral empirical work.
- E1's "proof strategy" section describes a 5-step mathematical derivation. This is not something you run on a computer.
- Phase 7 designs experiments that require A100 GPUs and ImageNet-scale data without ever asking what hardware is available.
- **Root cause:** Phase 6 (hypothesis formation) and Phase 7 (methodology) have no concept of "what can we actually do with available resources?" They optimize for theoretical impact, not empirical feasibility.
- **Fix:** Add empirical tractability as a first-class dimension in hypothesis scoring. Add a compute-aware triage phase. Reorient the entire downstream pipeline toward "run code, measure things, report findings."

#### Severity 3 — E1 proof strategy has a mathematical error

- The three-layer ReLU architecture is conflated with a two-layer formulation in Step 1 of E1's proof strategy. A standard three-layer network has two hidden-layer weight matrices ($W_1$, $W_2$) that produce feature maps $D_{2,l}D_{1,i}X$ (products of two diagonal activation matrices). The proof strategy incorrectly reduces this to a single-$\mathbf{w}$ formulation $\min_\mathbf{w} \frac{1}{2}\|\sigma(X\mathbf{w}) - \mathbf{y}\|^2$.
- Phase 5 (sanity check) did not catch this. Phase 7 (methodology) propagated it. Phase 9 (critique) caught it but too late — the final document already contained the error.
- **Fix:** For the redesigned pipeline this is less relevant since we're dropping proof-based hypotheses. But Phase 7 should include a self-consistency check: does the experiment design match the architecture described in the hypothesis?

#### Severity 4 — Diagnostics system is blind

- Every hook event logs `UNKNOWN_CHECK_PROBE` for agent name, tool name, and exit code. Claude Code's hook system does not expose `CLAUDE_SUBAGENT_NAME`, `CLAUDE_TOOL_NAME`, or `CLAUDE_TOOL_EXIT_CODE` as environment variables.
- The `pipeline-logger.sh` script works (it fires on events) but captures no useful information.
- **Fix:** Simplify hooks to log only what's knowable: timestamps, phase transitions read from `pipeline-state.yaml`, and a count of events. Remove all `CLAUDE_*` env var dependencies.

#### Severity 5 — Phase 3 hit context limits

- The run log shows Phase 3 started twice (two SubagentStart entries) and a PreCompact event mid-phase. The agent likely ran out of context reading all source files and was compacted.
- The recovery worked (Phase 3 completed with a valid literature map) but cost ~15 extra minutes.
- **Fix:** Phase 3's sequential reading protocol should be more aggressive about summarizing-as-it-goes rather than holding multiple full papers in context simultaneously. The existing protocol says "read sequentially" but doesn't enforce dropping prior papers from working memory.

#### Severity 6 — No web sources beyond NTK blog

- Francis Bach blog returned 404 and was never substituted.
- The NTK blog post (Lilian Weng) is the only non-paper source and provides secondary-level coverage of NTK theory.
- **Fix for v2:** Remove all blog/web source acquisition entirely. The pipeline is papers-only. NTK coverage (if needed) comes from acquiring the actual Jacot et al. 2018 paper via PDF download.

### What went right

- **Literature map quality:** MECE-organized, mathematically precise, correctly excluded mismatched sources. 5,200 words covering the full corpus.
- **Gap analysis:** All 3 Tier 1 gaps confirmed by direct source lookups. Rejected candidates are well-justified. Scoring is calibrated.
- **Sanity check:** Caught the missing generalization bounds gap (high-severity finding). Correctly rescoped Gap 2.3 from ImageNet to CIFAR-10. Flagged feasibility overstatement on Gap 1.1.
- **Phase 9 critique:** Correctly identified Phase 1 as weakest. Caught the E1 proof strategy error. Produced an actionable reiteration plan.
- **Overall coherence:** Despite the acquisition failure, the pipeline produced a self-consistent research agenda with no circular reasoning. All Tier 1 claims trace to downloaded sources.

---

## 2. Design Philosophy Change

### Old philosophy (v1)

"Given a research topic, produce a conference-grade research *proposal*: literature review, gap analysis, hypotheses, and experimental methodology."

**Output:** A document describing what someone *should* research.

### New philosophy (v2)

"Given a research topic, produce an empirical research *paper*: literature review, gap analysis, three testable hypotheses, actual experimental results, statistical analysis, and interpretation."

**Output:** A paper presenting what we *did* research, with real data.

### What this changes

| Aspect | v1 | v2 |
|--------|----|----|
| **Hypothesis selection** | Maximize theoretical impact | Maximize (feasibility × impact) for empirical work |
| **Methodology** | Abstract experimental design | Implementation specification with repos, packages, scripts |
| **Compute awareness** | None | VM profiled, experiments sized to available hardware |
| **Execution** | None — ends at proposal | Full experiment loop: code → run → evaluate → iterate |
| **Final document** | Research proposal/agenda | Empirical research paper with results |
| **Hypothesis types** | Theoretical proofs welcome | Empirical verification, numerical scaling, mechanistic probes only |
| **Number of hypotheses tested** | 7 proposed, 0 tested | 3 selected, 3 tested to completion |
| **Bar for "done"** | Document written | Base case met for all 3 experiments |
| **Source types** | Papers + blogs | Papers only |

### The "pre-doctoral empirical researcher" bar

Every hypothesis must be testable by writing code that:
1. Uses existing libraries (CVXPY, PyTorch, JAX, scikit-learn, etc.)
2. Runs on available hardware (4 vCPU/16GB VM for CPU work; Colab T4 for GPU work)
3. Produces numerical results that confirm or disconfirm a specific prediction
4. Does NOT require inventing new mathematical theory, proving new theorems, or deriving new algorithms

The framing is: "An Empirical Analysis of [Topic]" — we're testing predictions from the theoretical literature, not extending the theory.

---

## 3. New Pipeline Structure

### Complete Phase Map

```
═══════════════════════════════════════════════════════
RESEARCH PHASE (Phases 1–7) — modified from v1
═══════════════════════════════════════════════════════

Phase 1:  Source Acquisition        → sources/manifest.yaml
Phase 2:  Source Extraction         → sources/*/content.md
Phase 3:  Literature Comprehension  → analysis/literature-map.md
Phase 4:  Gap Analysis              → analysis/gap-analysis.md
Phase 5:  Sanity Check (advisory)   → analysis/review-notes.md
Phase 6:  Hypothesis Formation      → synthesis/hypotheses.md        ← MODIFIED
Phase 7:  Methodology Design        → synthesis/methodology.md      ← MODIFIED

═══════════════════════════════════════════════════════
PLANNING PHASE (Phases 10–12) — NEW
═══════════════════════════════════════════════════════

Phase 10: Compute Probe             → diagnostics/vm-profile.yaml   ← NEW
Phase 11: Hypothesis Triage         → experiments/triage.md         ← NEW
Phase 12: Experiment Roadmaps (×3)  → experiments/H{n}/roadmap.md   ← NEW

═══════════════════════════════════════════════════════
EXECUTION PHASE (Phases 13–14) — NEW, runs 3× sequentially
═══════════════════════════════════════════════════════

  For each of the 3 selected hypotheses:

  Phase 13: Experiment Loop         → experiments/H{n}/results/     ← NEW
            (coder + reviewer in loop until base case met
             or Colab gate hit → user action → resume)

  Phase 14: Results Analysis        → experiments/H{n}/analysis.md  ← NEW

═══════════════════════════════════════════════════════
ASSEMBLY PHASE (Phases 15–16) — moved from v1 Phases 8–9
═══════════════════════════════════════════════════════

Phase 15: Final Document Assembly   → synthesis/final-paper.md      ← was Phase 8
Phase 16: Critique + Reiteration    → reiteration/critique.md       ← was Phase 9
```

### Phase numbering note

Phases 8 and 9 are intentionally skipped to preserve backward compatibility with v1 artifacts and git history. The new phases start at 10.

### Sequential flow for the Execution Phase

```
Orchestrator reads experiments/triage.md → gets [H_a, H_b, H_c]

FOR hypothesis H_a:
  spawn experiment-roadmap(H_a) → experiments/H_a/roadmap.md
  LOOP:
    spawn experiment-coder(H_a) → runs code, writes results
    read experiments/H_a/status.yaml
    IF status == "colab_needed":
      spawn colab-notebook-generator(H_a) → experiments/H_a/colab/notebook.ipynb
      PRINT to user: "Upload notebook, run cells, paste output file to experiments/H_a/colab-results/"
      WAIT for user confirmation
      UPDATE status.yaml → "colab_complete"
      CONTINUE loop (coder reads colab results)
    IF status == "base_case_met":
      BREAK
    IF status == "failed_irrecoverable":
      LOG failure, BREAK (skip this hypothesis)
    spawn experiment-reviewer(H_a) → experiments/H_a/review.md
    CONTINUE loop (coder reads review)
  spawn experiment-analyst(H_a) → experiments/H_a/analysis.md

FOR hypothesis H_b:
  [same loop]

FOR hypothesis H_c:
  [same loop]

spawn final-document-assembly → synthesis/final-paper.md
spawn critique → reiteration/critique.md + reiteration/reiteration-plan.md
SURFACE to user
```

---

## 4. Changes to Existing Phases

### Phase 1: Source Acquisition — MODIFIED

**Changes:**
1. **Remove all web/blog source logic.** No Substack, no Medium, no distill.pub, no personal blogs. Papers only (arXiv + user PDFs).
2. **Switch from `arxiv.org/src/` to `arxiv.org/pdf/` + Mistral OCR.** Tarballs are unreliable. PDFs are stable.
3. **Add identity verification.** After extraction, grep for title keywords and first author surname. If neither match, mark as `identity_verified: false` and re-try with direct PDF download.
4. **Search for implementation repos.** For each paper, query Semantic Scholar for linked code repositories. Also search GitHub for `"{paper_title}" OR "{first_author} {year}"`. Record any found repos in the manifest entry as `code_repos: [...]`.
5. **Target 15–25 papers** (down from 30–40). Fewer but verified > more but half wrong.

**New manifest entry schema:**
```yaml
- id: arxiv-2002.10553
  type: arxiv
  title: "Neural Networks are Convex Regularizers"
  authors: ["Pilanci, M.", "Ergen, T."]
  year: 2020
  url: "https://arxiv.org/abs/2002.10553"
  local_path: sources/arxiv-2002.10553/
  content_file: sources/arxiv-2002.10553/content.md
  readable: true
  identity_verified: true  # NEW — grep confirmed title/author match
  char_count: 48392
  extraction_method: mistral-ocr-pdf  # NEW — was pandoc-latex
  code_repos:                         # NEW
    - url: "https://github.com/pilancilab/CRONOS"
      verified: true
  notes: ""
```

**Changes to `scripts/phase1_search.py`:**
- Replace `download_arxiv_source()` (tarball) with `download_arxiv_pdf()` as primary method
- Add `verify_paper_identity(content_file, expected_title, expected_author)` function
- Add `search_code_repos(title, authors, year)` function using Semantic Scholar API `fields=externalIds,url` and GitHub search API
- Remove all `WEB_SOURCES` references
- Lower `ARXIV_PAPERS` target from 30 to 15–25

**Changes to agent definition (`.claude/agents/source-acquisition.md`):**
- Remove Step 2 (Web Sources) entirely
- Remove all references to `authenticated_extract.py`, blog profiles, Substack, Medium
- Add Step 2: Identity Verification (grep for title/author in extracted content)
- Add Step 3: Code Repository Search (Semantic Scholar + GitHub)
- Update quality gate: "At least 15 sources with `identity_verified: true`"

### Phase 2: Source Extraction — MODIFIED

**Changes:**
1. **Primary extraction method is now Mistral OCR on PDFs** (not pandoc on LaTeX).
2. **Remove LaTeX-specific logic** (pandoc conversion, figure PDF→PNG conversion). These are only needed when working from LaTeX source tarballs, which we no longer use.
3. **Add content quality check:** After extraction, count domain-relevant keywords (from topic). Sources with <2 keyword hits in the first 3000 chars are flagged as `content_quality: suspect`.

**Changes to agent definition (`.claude/agents/source-extraction.md`):**
- Remove the "arXiv (LaTeX source)" section
- Remove the `magick` figure conversion commands
- Primary path: Mistral OCR on PDF → content.md
- Add a content-quality keyword check after extraction

### Phase 3: Literature Comprehension — MINOR CHANGES

**Changes:**
1. **Add aggressive context management instruction:** "After reading each paper and taking working notes, explicitly drop the raw content from working memory. Carry forward only your structured notes (key claims, methods, results, relationships). Do not attempt to hold more than 2 papers' raw text simultaneously."
2. **Remove blog source handling.**
3. **Add a new Section 10: Implementation Landscape.** For each paper that has a public code repository (from `code_repos` in manifest), note: what language, what framework, what the repo contains. This is read by Phase 12 (experiment roadmap).

**New required section in literature-map.md:**
```markdown
## 10. Implementation Landscape
[For each paper with a public code repository]
- **[AuthorYear]**: Repo: {URL}. Language: Python/JAX. Contains: {brief description}.
  Dependencies: {key packages}. Last commit: {if determinable from manifest}.
```

### Phase 4: Gap Analysis — MINOR CHANGES

**Changes:**
1. **Add "Empirical Testability" as the 5th scoring dimension (0–10).**

| Score | Criteria |
|-------|---------|
| 9–10 | Can be tested by running existing code on public data with commodity hardware. |
| 7–8 | Requires writing new experiment code using existing libraries; public data; standard hardware. |
| 5–6 | Requires moderate new code + may need GPU or specialized data. |
| 3–4 | Requires significant new implementation or proprietary resources. |
| 1–2 | Requires new theory/algorithms before any experiment is possible. |

2. **Modified composite score:**
```
Composite = (Confidence × 2 + Impact + Feasibility + Verifiability + EmpiricalTestability) / 6
```

3. **New tier consideration:** A gap with Empirical Testability ≤ 3 cannot be Tier 1 regardless of other scores.

### Phase 5: Sanity Check — NO CHANGES

Works well as-is. The advisory-only model is correct.

### Phase 6: Hypothesis Formation — SIGNIFICANTLY MODIFIED

**Changes:**

1. **Replace FATS with FATES criteria:**
- **F**alsifiable
- **A**ctionable
- **T**estable
- **E**mpirically tractable (NEW — can be tested by writing code and running experiments, not by proving theorems)
- **S**pecific

2. **Hypothesis type tagging.** Every hypothesis must be tagged as one of:
- `empirical-verification`: Test a specific prediction from the literature by measuring something
- `numerical-scaling`: Measure how a quantity scales with a parameter across a range
- `mechanistic-probe`: Use existing tools to investigate a mechanism predicted by theory
- `theoretical-proof`: Requires deriving new mathematical results (NOT ALLOWED in v2 unless no empirical alternative exists for the gap)

3. **Hard rule:** If an empirical alternative exists for a gap, do NOT generate a `theoretical-proof` hypothesis. Always prefer `empirical-verification` or `numerical-scaling`.

4. **Reduced count:** Generate 5–7 hypotheses (down from unlimited). Expect ~3 to survive triage.

5. **New required field per hypothesis: "Implementation sketch"**
```markdown
**Implementation sketch:**
- Primary library: CVXPY / PyTorch / JAX / etc.
- Existing code to build on: {repo URL from literature map Section 10, or "none"}
- Estimated lines of new code: ~{N}
- Compute: CPU-feasible / needs-GPU
- Data: synthetic / {public dataset name}
- Estimated wall-clock: {hours}
```

**Changes to agent definition (`.claude/agents/hypothesis-formation.md`):**
- Replace FATS with FATES throughout
- Add hypothesis type tagging
- Add the "theoretical-proof prohibition" rule
- Add implementation sketch requirement
- Add instruction: "Read analysis/literature-map.md Section 10 (Implementation Landscape) to identify existing codebases that experiments can build on."

### Phase 7: Methodology Design — SIGNIFICANTLY MODIFIED

**Changes:**

1. **Rename from "DOE Design" to "Implementation Specification."** The output should read like a software specification, not an abstract experimental design.

2. **New required sections per experiment:**

```markdown
### Implementation Specification

**Repository setup:**
- Clone: `git clone {URL}`
- Key files: `{path/to/relevant/module.py}`
- Install: `pip install {packages}`

**Script to write:**
- Filename: `experiments/H{n}/scripts/{name}.py`
- Inputs: {what data, what parameters}
- Outputs: {what files, what format}
- Entry point: `python {name}.py --n 100 --beta 0.01 --seeds 20`

**Compute requirements:**
- CPU estimate: {hours} on 4-core machine
- RAM peak: ~{GB}
- GPU needed: yes/no
- If GPU needed: mark as COLAB_GATE, estimate Colab T4 time

**Data:**
- Source: synthetic (generated in script) / {dataset name} from {URL}
- Size: {MB/GB}
- Download command: `wget {URL}` or `from sklearn.datasets import {name}`
```

3. **Remove "Proof Strategy" sections entirely.** No mathematical derivation plans. Every experiment must be runnable as code.

4. **Add base case definition per experiment:**
```markdown
**Base case (pass/fail):**
- PASS if: {specific quantitative criterion, e.g., "Spearman ρ > 0.7"}
- FAIL if: {specific quantitative criterion, e.g., "Spearman |ρ| < 0.3"}
- INCONCLUSIVE if: {between pass and fail thresholds}
- Minimum runs for conclusion: {N seeds × M parameter settings}
```

**Changes to agent definition (`.claude/agents/methodology-design.md`):**
- Replace DOE framing with implementation specification
- Add base case definition requirement
- Add compute requirements section
- Add COLAB_GATE flagging
- Remove proof strategy template
- Add instruction: "Read diagnostics/vm-profile.yaml to size experiments to available hardware. If vm-profile.yaml does not exist yet, assume: 4 vCPU, 16GB RAM, no GPU, Python 3.10+, pip available."

---

## 5. New Planning Phases (10–12)

### Phase 10: Compute Probe

**Purpose:** SSH into the Azure VM, profile its environment, and write a structured report that downstream agents use to size experiments.

**Agent definition: `.claude/agents/compute-probe.md`**

```yaml
---
name: compute-probe
description: Phase 10 — SSHs into the experiment VM, profiles hardware, software, and storage. Writes diagnostics/vm-profile.yaml for use by downstream experiment planning agents.
model: haiku
tools: Bash
permissionMode: acceptEdits
maxTurns: 10
color: gray
---
```

**Behavior:**

1. Mark Phase 10 as `in_progress` in `pipeline-state.yaml`.
2. Run the following commands via `ssh azure-vm-dissertation`:

```bash
# Hardware
ssh azure-vm-dissertation "lscpu | head -20"
ssh azure-vm-dissertation "free -h"
ssh azure-vm-dissertation "df -h /"
ssh azure-vm-dissertation "cat /proc/cpuinfo | grep 'model name' | head -1"

# GPU check
ssh azure-vm-dissertation "nvidia-smi 2>/dev/null || echo 'NO_GPU'"

# Python
ssh azure-vm-dissertation "python3 --version 2>/dev/null || echo 'NO_PYTHON3'"
ssh azure-vm-dissertation "pip3 --version 2>/dev/null || echo 'NO_PIP3'"
ssh azure-vm-dissertation "pip3 list 2>/dev/null | head -30"

# Network
ssh azure-vm-dissertation "curl -sI https://pypi.org --max-time 5 | head -1 || echo 'NO_INTERNET'"
ssh azure-vm-dissertation "git --version 2>/dev/null || echo 'NO_GIT'"

# OS
ssh azure-vm-dissertation "cat /etc/os-release | head -5"
```

3. Write `diagnostics/vm-profile.yaml`:

```yaml
vm_name: azure-vm-dissertation
ssh_command: "ssh azure-vm-dissertation"
probed_at: "{TIMESTAMP}"
hardware:
  cpus: 4
  cpu_model: "AMD EPYC 7763 64-Core Processor"
  ram_total_gb: 16
  ram_available_gb: 14.2
  disk_total_gb: 128
  disk_available_gb: 95
  gpu: none
software:
  os: "Ubuntu 22.04.3 LTS"
  python_version: "3.10.12"
  pip_version: "22.0.2"
  git_version: "2.34.1"
  preinstalled_packages:
    - numpy
    - scipy
    # ... (from pip list)
network:
  internet_access: true
  pypi_reachable: true
compute_constraints:
  max_cpu_hours_reasonable: 8  # per experiment, before it's "too long"
  max_ram_per_process_gb: 12
  gpu_available: false
  colab_fallback: true  # GPU work goes to Colab T4
```

4. Mark Phase 10 as `complete`. Git commit.

### Phase 11: Hypothesis Triage

**Purpose:** Read all hypotheses, score them on empirical feasibility given actual compute constraints, and select the 3 best (feasibility × impact) for testing.

**Agent definition: `.claude/agents/hypothesis-triage.md`**

```yaml
---
name: hypothesis-triage
description: Phase 11 — Reads hypotheses, methodology, VM profile, and literature map. Scores each hypothesis on empirical feasibility × impact. Selects the 3 best for testing. Outputs experiments/triage.md.
model: opus
tools: Read, Write, Bash
permissionMode: acceptEdits
effort: high
color: orange
---
```

**Behavior:**

1. Read inputs:
   - `synthesis/hypotheses.md`
   - `synthesis/methodology.md`
   - `diagnostics/vm-profile.yaml`
   - `analysis/literature-map.md` (Section 10: Implementation Landscape)
   - `analysis/review-notes.md` (Phase 5 advisory priorities)

2. Score each hypothesis on 5 dimensions (1–10):

| Dimension | Definition |
|-----------|-----------|
| **Code complexity** | How many lines of new code? Are there existing repos to build on? (10 = <100 lines using existing library; 1 = >2000 lines from scratch) |
| **Compute fit** | Can it run on the VM? (10 = CPU-only, <1h; 7 = CPU-only, <8h; 4 = needs Colab T4; 1 = needs A100/multi-GPU) |
| **Data availability** | (10 = synthetic; 8 = public dataset, <1GB; 5 = public, >1GB; 1 = proprietary/unavailable) |
| **Time to result** | Wall-clock including coding + debugging + runs (10 = <4h total; 7 = <1 day; 4 = <3 days; 1 = >1 week) |
| **Impact if confirmed** | Same as Phase 4's Impact score but re-evaluated for empirical contribution |

**Triage composite:** `(CodeComplexity + ComputeFit + DataAvailability + TimeToResult + Impact) / 5`

3. **Hard filters** (eliminate before scoring):
   - Hypothesis type is `theoretical-proof` → ELIMINATE unless no alternatives
   - Hypothesis requires hardware not available (e.g., multi-node cluster) → ELIMINATE
   - Hypothesis depends on another hypothesis being confirmed first → DEPRIORITIZE

4. Rank by composite score. Select top 3.

5. Write `experiments/triage.md`:

```markdown
---
phase: 11
status: complete
timestamp: {TIMESTAMP}
selected_hypotheses: [H4, H5, H3]
---

# Hypothesis Triage: {TOPIC}

## Triage Scores

| Hypothesis | Code | Compute | Data | Time | Impact | **Composite** | Selected |
|-----------|------|---------|------|------|--------|------------|----------|
| H1 | 3 | 5 | 10 | 4 | 9 | 6.2 | No (proof-based) |
| H2 | 4 | 5 | 10 | 5 | 9 | 6.6 | No (proof-based) |
| H3 | 7 | 6 | 9 | 7 | 6 | 7.0 | **Yes (#3)** |
| H4 | 8 | 8 | 10 | 8 | 8 | **8.4** | **Yes (#1)** |
| H5 | 9 | 10 | 10 | 9 | 5 | **8.6** | **Yes (#2)** |
| H6 | 5 | 6 | 10 | 5 | 6 | 6.4 | No |
| H7 | 4 | 3 | 8 | 3 | 7 | 5.0 | No (needs GPU) |

## Selected Hypotheses (in execution order)

### #1: H5 — Fixed-Point BN Convex Equivalence
**Why selected:** Highest compute fit (CPU, n=50), fastest time-to-result, clean yes/no outcome.
**Execution order rationale:** Quick win; builds confidence and validates toolchain.

### #2: H4 — Carathéodory Generalization Bound
**Why selected:** Highest impact among feasible hypotheses; pure CVXPY on CPU; 960 runs are parallelizable.
**Execution order rationale:** Longest individual runtime; start after H5 validates setup.

### #3: H3 — CRONOS-AM Lyapunov Descent
**Why selected:** Tests the practical solver; UCI datasets are small. JAX may need Colab for full runs.
**COLAB_GATE:** Likely for JAX/CRONOS; CPU fallback possible for toy-scale validation.

## Eliminated Hypotheses

| Hypothesis | Reason |
|-----------|--------|
| H1 | Requires new theorem proof (theoretical-proof type); empirical verification sub-component (CVXPY enumeration) is included in H4's infrastructure |
| H2 | Requires extending Gordon's comparison inequality (theoretical-proof type) |
| H6 | Lower impact than H4; logistic loss extension is incremental |
| H7 | Requires CRONOS at CIFAR-10 scale (~50k samples); exceeds VM capacity; Colab T4 may be marginal |
```

6. Mark Phase 11 as `complete`. Git commit.

### Phase 12: Experiment Roadmaps

**Purpose:** For each selected hypothesis, produce a detailed implementation plan that the experiment coder can follow step-by-step.

**Agent definition: `.claude/agents/experiment-roadmap.md`**

```yaml
---
name: experiment-roadmap
description: Phase 12 — Creates a detailed implementation roadmap for a single hypothesis experiment. Called once per selected hypothesis. Reads hypothesis, methodology, VM profile, and literature map. Outputs experiments/H{n}/roadmap.md.
model: opus
tools: Read, Write, Bash, Grep
permissionMode: acceptEdits
effort: high
color: orange
skills:
  - experiment-execution
  - vm-interaction
  - source-lookup
---
```

**Behavior:**

1. Read inputs:
   - `synthesis/hypotheses.md` (the specific hypothesis)
   - `synthesis/methodology.md` (the experiment specification)
   - `diagnostics/vm-profile.yaml`
   - `analysis/literature-map.md` (Section 10: Implementation Landscape)
   - `experiments/triage.md` (for context on why this hypothesis was selected)

2. For each experiment, produce `experiments/H{n}/roadmap.md` with these sections:

```markdown
---
hypothesis: H{n}
title: "{hypothesis title}"
type: empirical-verification | numerical-scaling | mechanistic-probe
estimated_total_hours: {N}
colab_gates: {0 or N}
---

# Experiment Roadmap: H{n} — {Title}

## 1. Objective
[1-2 sentences: what we're measuring and why]

## 2. Base Case (Pass/Fail Criteria)
- **PASS:** {specific quantitative criterion}
- **FAIL:** {specific quantitative criterion}
- **INCONCLUSIVE:** {between thresholds}
- **Minimum data for conclusion:** {N runs}

## 3. VM Setup
```bash
ssh azure-vm-dissertation
mkdir -p ~/experiments/H{n}
cd ~/experiments/H{n}
python3 -m venv .venv
source .venv/bin/activate
pip install {package1} {package2} ...
```

## 4. Repository Cloning (if applicable)
```bash
git clone {repo_url} ~/experiments/H{n}/vendor/{repo_name}
# Key files to use:
# - vendor/{repo_name}/src/{module}.py — {what it does}
```

## 5. Implementation Steps

### Step 1: {Description}
**Script:** `scripts/step1_{name}.py`
**Inputs:** {what}
**Outputs:** `results/step1_output.{ext}`
**Compute:** CPU, ~{N} minutes
**Pseudocode:**
```python
# [Detailed pseudocode — NOT abstract, actual function calls and logic]
import cvxpy as cp
import numpy as np

def run_experiment(n, d, beta, seed):
    np.random.seed(seed)
    X = np.random.randn(n, d)
    # ... [specific steps]
    prob = cp.Problem(cp.Minimize(objective), constraints)
    prob.solve(solver=cp.SCS)
    return {
        'primal_value': prob.value,
        'dual_support_size': np.sum(np.abs(dual_var.value) > 1e-8),
        # ...
    }

# Parameter grid
results = []
for n in [50, 100, 200, 500]:
    for beta in [1e-3, 1e-2, 1e-1]:
        for seed in range(20):
            results.append(run_experiment(n, d, beta, seed))

# Save
pd.DataFrame(results).to_csv('results/step1_output.csv', index=False)
```

### Step 2: {Description}
[Same format]

### Step N (COLAB_GATE): {Description}
**⚠️ This step requires GPU. Run on Google Colab T4.**
**Notebook:** `colab/H{n}_step{N}.ipynb`
**Upload instructions:**
1. Upload notebook to Google Colab
2. Set runtime to GPU (T4)
3. Run all cells
4. Download `results/step{N}_output.csv`
5. Copy to VM: `scp step{N}_output.csv azure-vm-dissertation:~/experiments/H{n}/results/`

## 6. Analysis Steps
**Script:** `scripts/analyze.py`
**Reads:** all `results/*.csv`
**Produces:**
- `results/summary_table.csv` — main results table
- `results/figures/` — plots
- `results/base_case_evaluation.json` — {"pass": true/false, "metric": value, "threshold": value}

## 7. Expected Timeline
| Step | Estimated time | Compute |
|------|---------------|---------|
| VM Setup | 10 min | — |
| Step 1 | 2 hours | CPU |
| Step 2 | 30 min | CPU |
| Analysis | 15 min | CPU |
| **Total** | **~3 hours** | |

## 8. Troubleshooting
- If CVXPY SCS solver fails: try `solver=cp.ECOS` or increase `max_iters`
- If memory exceeds 12GB: reduce grid size (fewer seeds first, then fewer n values)
- If step takes >2x estimated time: reduce parameter range and note in results
```

3. Create the directory structure:
```bash
mkdir -p experiments/H{n}/{scripts,results,colab,results/figures}
```

4. Write `experiments/H{n}/status.yaml`:
```yaml
hypothesis: H{n}
status: roadmap_complete
steps_total: {N}
steps_completed: 0
base_case_met: false
colab_gates_pending: {0 or N}
last_updated: "{TIMESTAMP}"
```

5. Mark Phase 12 as `complete` for this hypothesis. Git commit.

**The orchestrator calls Phase 12 three times, once per selected hypothesis.**

---

## 6. New Execution Phases (13–14) — The Experiment Loop

### Phase 13: Experiment Loop

This is the core execution engine. It's an orchestrator-managed loop of two agents: **experiment-coder** and **experiment-reviewer**.

#### Agent: experiment-coder

```yaml
---
name: experiment-coder
description: Phase 13 worker — Reads the experiment roadmap and reviewer feedback, SSHs into the VM, writes experiment scripts, runs them, and reports results. Does not make scientific decisions — follows the roadmap and reviewer instructions.
model: sonnet
tools: Bash, Read, Write
permissionMode: acceptEdits
color: green
skills:
  - vm-interaction
  - experiment-execution
---
```

**Behavior:**

1. Read `experiments/H{n}/roadmap.md` to understand the full plan.
2. Read `experiments/H{n}/status.yaml` to know which step to execute next.
3. Read `experiments/H{n}/review.md` (if it exists) for reviewer feedback on previous iteration.
4. Execute the next step:
   a. Write the Python script locally in `experiments/H{n}/scripts/`.
   b. Copy it to the VM: `scp experiments/H{n}/scripts/{name}.py azure-vm-dissertation:~/experiments/H{n}/scripts/`
   c. SSH and run it:
   ```bash
   ssh azure-vm-dissertation "cd ~/experiments/H{n} && source .venv/bin/activate && python scripts/{name}.py"
   ```
   d. Copy results back: `scp azure-vm-dissertation:~/experiments/H{n}/results/{output} experiments/H{n}/results/`
5. If the step is a COLAB_GATE:
   - Do NOT run on VM.
   - Update `status.yaml` to `status: colab_needed` with details.
   - The orchestrator will handle the user interaction.
6. After running, check if base case can be evaluated:
   - If all steps are complete, run the analysis script.
   - Read `results/base_case_evaluation.json`.
   - Update `status.yaml` accordingly.
7. If there's an error (script crashes, import fails, etc.):
   - Capture the full traceback.
   - Write it to `experiments/H{n}/error.log`.
   - Update `status.yaml` to `status: error` with error summary.
   - The reviewer will diagnose and provide fix instructions.

**Critical rules for the coder:**
- Never make scientific decisions (change parameters, reinterpret results, modify the base case). Only the reviewer does that.
- Always capture full stdout/stderr from VM runs.
- Always copy result files back to local before updating status.
- If a run takes >2x the roadmap's estimated time, kill it and report timeout.

#### Agent: experiment-reviewer

```yaml
---
name: experiment-reviewer
description: Phase 13 reviewer — Reads experiment results, errors, and the roadmap. Decides whether to continue, fix, adjust parameters, or declare base case met/failed. Writes instructions for the coder.
model: opus
tools: Read, Write, Grep
permissionMode: acceptEdits
effort: high
color: red
skills:
  - experiment-execution
  - source-lookup
---
```

**Behavior:**

1. Read:
   - `experiments/H{n}/roadmap.md` (the plan)
   - `experiments/H{n}/status.yaml` (current state)
   - `experiments/H{n}/results/` (any results so far)
   - `experiments/H{n}/error.log` (if error occurred)
   - `analysis/literature-map.md` and `synthesis/hypotheses.md` (for scientific context)

2. Evaluate the situation and write `experiments/H{n}/review.md`:

```markdown
---
iteration: {N}
timestamp: {TIMESTAMP}
verdict: continue | fix_code | adjust_parameters | base_case_met | base_case_failed | escalate_to_user
---

# Experiment Review: H{n}, Iteration {N}

## Status Assessment
[What happened in the last coder run]

## Results So Far
[Summary of any numerical results]

## Decision
**Verdict: {verdict}**

## Instructions for Next Coder Run
[If verdict is continue or fix_code:]
- {Specific instruction 1}
- {Specific instruction 2}

[If verdict is adjust_parameters:]
- Change {parameter} from {old} to {new} because {reason}
- Re-run step {N} with new parameters

[If verdict is base_case_met:]
- The base case criterion ({criterion}) is satisfied with value {value}.
- No further runs needed for this hypothesis.

[If verdict is base_case_failed:]
- After {N} iterations, the base case cannot be met. Reason: {reason}.
- Recommendation: {skip / try alternative approach / escalate}
```

3. Update `experiments/H{n}/status.yaml` with the verdict.

**Critical rules for the reviewer:**
- Be honest about whether results meet the base case. Do not lower the bar.
- If an error is a simple bug (typo, wrong import, shape mismatch), provide the exact fix.
- If results are consistently unexpected after 3+ iterations, consider whether the roadmap's approach is flawed and suggest an alternative.
- Never tell the coder to fabricate or cherry-pick results.

#### Orchestrator logic for the experiment loop:

```python
# Pseudocode for orchestrator
for hypothesis in selected_hypotheses:
    spawn_agent("experiment-roadmap", hypothesis=hypothesis)
    
    max_iterations = 30  # safety limit
    for i in range(max_iterations):
        spawn_agent("experiment-coder", hypothesis=hypothesis)
        
        status = read_yaml(f"experiments/{hypothesis}/status.yaml")
        
        if status["status"] == "colab_needed":
            # Generate notebook
            spawn_agent("colab-notebook-generator", hypothesis=hypothesis)
            print(f"USER ACTION REQUIRED: Run Colab notebook for {hypothesis}")
            print(f"  Notebook: experiments/{hypothesis}/colab/notebook.ipynb")
            print(f"  After running, copy results to experiments/{hypothesis}/colab-results/")
            wait_for_user_confirmation()
            update_status(hypothesis, "colab_complete")
            continue  # coder will read colab results on next iteration
        
        if status["status"] == "base_case_met":
            print(f"{hypothesis}: Base case met!")
            break
        
        if status["status"] == "failed_irrecoverable":
            print(f"{hypothesis}: Failed after {i+1} iterations. Skipping.")
            break
        
        # Spawn reviewer for any other status
        spawn_agent("experiment-reviewer", hypothesis=hypothesis)
        
        review = read_yaml(f"experiments/{hypothesis}/review.md")
        if review["verdict"] in ("base_case_met", "base_case_failed"):
            break
    
    # After loop completes, run analysis
    spawn_agent("experiment-analyst", hypothesis=hypothesis)
```

### Phase 14: Results Analysis

**Agent: experiment-analyst**

```yaml
---
name: experiment-analyst
description: Phase 14 — Reads all experimental results for a completed hypothesis, performs statistical analysis, generates figures/tables, and writes a structured analysis report. Does NOT re-run experiments.
model: opus
tools: Read, Write, Bash
permissionMode: acceptEdits
effort: high
color: purple
skills:
  - experiment-execution
---
```

**Behavior:**

1. Read:
   - `experiments/H{n}/roadmap.md`
   - `experiments/H{n}/results/*.csv`
   - `experiments/H{n}/status.yaml`
   - `synthesis/hypotheses.md` (for the hypothesis statement and predictions)

2. Run analysis scripts on the VM (or locally if data is small):
   - Statistical tests (Spearman correlation, t-tests, bootstrap CIs)
   - Generate plots (matplotlib/seaborn) saved to `experiments/H{n}/results/figures/`
   - Summary statistics table

3. Write `experiments/H{n}/analysis.md`:

```markdown
---
hypothesis: H{n}
base_case: pass | fail | inconclusive
timestamp: {TIMESTAMP}
---

# Experimental Analysis: H{n} — {Title}

## Hypothesis Recap
[1-2 sentences restating the hypothesis and its measurable prediction]

## Experimental Setup Summary
[Brief: what was run, how many times, what parameters]

## Results

### Primary Metric
[The main number/correlation/comparison with confidence intervals]

### Results Table
| Parameter | Metric Value | 95% CI | Interpretation |
|-----------|-------------|--------|----------------|
| ... | ... | ... | ... |

### Figures
![{description}](results/figures/{filename}.png)

## Base Case Evaluation
**Criterion:** {the specific pass/fail criterion from the roadmap}
**Observed value:** {value}
**Verdict:** PASS / FAIL / INCONCLUSIVE

## Interpretation
[3-5 sentences: what does this result mean in the context of the hypothesis and the broader literature?]

## Limitations
[What caveats apply? What would strengthen the result?]

## Connection to Literature
[How does this relate to the specific papers and gaps identified in the literature map?]
```

4. Copy any generated figures from VM to local.
5. Update `experiments/H{n}/status.yaml` to `status: analysis_complete`.
6. Git commit.

---

## 7. New Assembly Phases (15–16)

### Phase 15: Final Document Assembly

**Replaces Phase 8 from v1.** Now assembles an empirical research *paper*, not a research proposal.

**Agent definition: `.claude/agents/final-paper-assembly.md`**

```yaml
---
name: final-paper-assembly
description: Phase 15 — Assembles the final empirical research paper from all pipeline artifacts including experimental results. Outputs synthesis/final-paper.md.
model: sonnet
tools: Read, Write, Grep, Glob
permissionMode: acceptEdits
effort: high
color: teal
skills:
  - writing-style
  - source-integrity
  - markdown-conventions
  - source-lookup
---
```

**Document structure (empirical paper format):**

```
1. Abstract (300 words)
2. Introduction (800 words)
   - Problem statement
   - Why empirical analysis matters for this topic
   - Contributions of this paper (3 experiments, key findings)
3. Background and Related Work (2,000 words)
   - Synthesized from analysis/literature-map.md
   - Focused on the concepts directly tested in experiments
4. Research Gaps and Hypotheses (1,000 words)
   - From analysis/gap-analysis.md, filtered to the 3 tested hypotheses
   - Each hypothesis stated formally with measurable predictions
5. Experimental Setup (1,500 words)
   - 5.1 Hypothesis H_a: Setup
   - 5.2 Hypothesis H_b: Setup
   - 5.3 Hypothesis H_c: Setup
   - (Each includes: data, methodology, baselines, evaluation metrics, compute)
6. Results (2,000 words)
   - 6.1 H_a Results (with tables and figures)
   - 6.2 H_b Results
   - 6.3 H_c Results
7. Discussion (800 words)
   - What the results mean collectively
   - How they connect to the theoretical framework
   - Surprising findings or negative results
8. Limitations and Future Work (500 words)
9. Conclusion (300 words)
10. References
11. Appendix: Additional Experimental Details
```

**Target length: 8,000–12,000 words** (longer than v1 because we have actual results to present).

**Key differences from v1 Phase 8:**
- Sections 5 and 6 (Setup and Results) are NEW — they incorporate actual experimental data.
- Section 3 (Background) is shorter and more focused — only covers concepts relevant to the 3 tested hypotheses.
- No "Gap Analysis" section in the style of v1 — gaps are woven into the Introduction and Hypotheses section.
- The paper reads as a completed study, not a proposal.

### Phase 16: Critique + Reiteration

**Replaces Phase 9 from v1.** Now evaluates the full package including experimental results.

**Agent definition: `.claude/agents/critique-v2.md`**

```yaml
---
name: critique-v2
description: Phase 16 — Evaluates the entire pipeline output including experimental results. Identifies weaknesses, scores phases, and produces a reiteration plan that may target research phases (1-7), experiment execution (13-14), or document assembly (15). Requires user approval before re-running.
model: opus
tools: Read, Write
permissionMode: acceptEdits
color: red
skills:
  - source-lookup
---
```

**Evaluation scope now includes:**

| Phase | Quality Criteria |
|-------|-----------------|
| Phases 1-5 | Same as v1 |
| Phase 6 | Were hypotheses empirically tractable? Were the right ones generated? |
| Phase 7 | Were implementation specifications accurate? Did the roadmap match reality? |
| Phase 10 | Was the VM profile accurate? |
| Phase 11 | Were the right 3 hypotheses selected? Was triage well-calibrated? |
| Phase 12 | Were roadmaps realistic? Were base cases well-defined? |
| Phase 13 | Were experiments well-executed? Were there excessive iterations? |
| Phase 14 | Is the statistical analysis correct? Are interpretations justified by data? |
| Phase 15 | Does the paper flow? Are results presented clearly? Are all claims cited? |

**New reiteration targets:**

The reiteration plan can now target:
- **Research re-run:** Re-run Phases 1–7 (e.g., if literature coverage was insufficient)
- **Experiment re-run:** Re-run Phase 13 for a specific hypothesis (e.g., if base case was barely missed and a parameter adjustment could fix it)
- **Document revision:** Re-run Phase 15 only (e.g., if the paper has structural issues but results are fine)

**Output format is same as v1 critique** (`reiteration/critique.md` + `reiteration/reiteration-plan.md`) but with expanded scope.

**User approval required before any re-run.** The orchestrator surfaces both files and waits.

---

## 8. Orchestrator Rewrite — CLAUDE.md

The CLAUDE.md orchestrator instructions need significant updates. Here's what changes:

### New "Quick Start" section:

```markdown
## Quick Start

> "Research [topic] for me"

Orchestrator runs the full pipeline:
1. Research Phase (Phases 1–7): ~1 hour
2. Planning Phase (Phases 10–12): ~20 minutes
3. Execution Phase (Phases 13–14): variable (hours to days, may require user Colab interaction)
4. Assembly Phase (Phases 15–16): ~30 minutes
5. Surface critique to user for reiteration decision
```

### New orchestrator decision logic after Phase 7:

```markdown
### After Phase 7 completes:

DO NOT spawn Phase 8 (old document assembly) or Phase 9 (old critique).
Instead:

1. Spawn Phase 10 (compute-probe)
2. Read pipeline-state.yaml, verify Phase 10 complete
3. Spawn Phase 11 (hypothesis-triage)
4. Read experiments/triage.md, extract selected_hypotheses list
5. For each hypothesis in selected_hypotheses (sequentially):
   a. Spawn Phase 12 (experiment-roadmap) for this hypothesis
   b. Enter the experiment loop (Phase 13):
      - Spawn experiment-coder
      - Check status.yaml
      - If colab_needed: spawn colab-notebook-generator, surface to user, wait
      - If base_case_met: break
      - If error/continue: spawn experiment-reviewer, then loop back to coder
   c. Spawn Phase 14 (experiment-analyst) for this hypothesis
6. After all 3 hypotheses are done:
   a. Spawn Phase 15 (final-paper-assembly)
   b. Spawn Phase 16 (critique)
   c. Surface critique to user
```

### Colab interaction protocol:

```markdown
### When a hypothesis hits a COLAB_GATE:

The orchestrator prints to the user:

"""
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
"""

The orchestrator STOPS and WAITS for the user to confirm.
After confirmation, it continues the experiment loop.
```

---

## 9. New Agent Definitions — Complete Specifications

### Summary of all agents in v2

| Agent | Phase | Model | New/Modified |
|-------|-------|-------|-------------|
| source-acquisition | 1 | Sonnet | Modified |
| source-extraction | 2 | Sonnet | Modified |
| literature-comprehension | 3 | Opus | Modified |
| gap-analysis | 4 | Opus | Modified |
| sanity-check | 5 | Opus | Unchanged |
| hypothesis-formation | 6 | Opus | Modified |
| methodology-design | 7 | Opus | Modified |
| compute-probe | 10 | Haiku | **New** |
| hypothesis-triage | 11 | Opus | **New** |
| experiment-roadmap | 12 | Opus | **New** |
| experiment-coder | 13 | Sonnet | **New** |
| experiment-reviewer | 13 | Opus | **New** |
| colab-notebook-generator | 13 | Sonnet | **New** |
| experiment-analyst | 14 | Opus | **New** |
| final-paper-assembly | 15 | Sonnet | **New** (replaces Phase 8) |
| critique-v2 | 16 | Opus | **New** (replaces Phase 9) |
| diagnostics-summary | — | Haiku | Unchanged |

### New agent: colab-notebook-generator

```yaml
---
name: colab-notebook-generator
description: Generates a self-contained Google Colab .ipynb notebook for experiment steps that require GPU. The notebook includes all setup (pip installs, data generation/download), the experiment code, result saving, and download instructions.
model: sonnet
tools: Read, Write, Bash
permissionMode: acceptEdits
color: green
skills:
  - experiment-execution
---
```

**Behavior:**

1. Read `experiments/H{n}/roadmap.md` to find the COLAB_GATE step.
2. Read any prior results from `experiments/H{n}/results/` that the Colab step needs as input.
3. Generate `experiments/H{n}/colab/H{n}_step{N}.ipynb` as a valid Jupyter notebook JSON file.

**Notebook structure:**
```
Cell 1 (markdown): "# H{n}: {step_name}\nThis notebook runs step {N} of the {hypothesis_title} experiment.\nRuntime: GPU (T4 recommended)."

Cell 2 (code): pip installs
  !pip install -q {packages}

Cell 3 (code): Upload input files (if any)
  from google.colab import files
  # uploaded = files.upload()  # Only if input files are needed

Cell 4 (code): The actual experiment code
  [Complete, self-contained Python code]
  [Generates results and saves to CSV/pickle]

Cell 5 (code): Display summary
  import pandas as pd
  results = pd.read_csv('results.csv')
  print(results.describe())

Cell 6 (code): Download results
  from google.colab import files
  files.download('results.csv')
  # files.download('figures/plot.png')  # if applicable

Cell 7 (markdown): "## Next Steps\nDownload the result files above and place them in:\n`experiments/H{n}/colab-results/`\nThen tell the orchestrator the results are ready."
```

**The notebook must be completely self-contained.** No imports from the local project. All data is either generated within the notebook or uploaded by the user.

---

## 10. New and Modified Skills

### New skill: experiment-execution

**Location:** `.claude/skills/experiment-execution/SKILL.md`

```markdown
---
name: experiment-execution
description: Conventions for experiment directory structure, status tracking, result formats, and the coder-reviewer interaction protocol. Used by all agents in Phases 12-14.
user-invocable: false
---

# Experiment Execution Conventions

## Directory Structure per Hypothesis

experiments/H{n}/
├── roadmap.md           # Phase 12 output — the plan
├── status.yaml          # Current state — updated by coder and reviewer
├── review.md            # Latest reviewer feedback
├── error.log            # Latest error (if any)
├── scripts/             # Python scripts written by coder
│   ├── step1_setup.py
│   ├── step2_run.py
│   └── analyze.py
├── results/             # Output data
│   ├── step1_output.csv
│   ├── step2_output.csv
│   ├── summary_table.csv
│   ├── base_case_evaluation.json
│   └── figures/
│       ├── main_result.png
│       └── ...
├── colab/               # Colab notebooks (if GPU needed)
│   └── H{n}_step{N}.ipynb
├── colab-results/       # Results from Colab runs (user places here)
│   └── step{N}_output.csv
└── analysis.md          # Phase 14 output — final analysis

## status.yaml Schema

hypothesis: H{n}
status: roadmap_complete | in_progress | error | colab_needed | colab_complete | base_case_met | base_case_failed | analysis_complete
current_step: {N}
steps_total: {N}
steps_completed: {N}
iteration: {N}  # how many coder-reviewer cycles
base_case_met: true | false
base_case_metric: {name}
base_case_value: {number or null}
base_case_threshold: {number}
last_error: "{error summary or null}"
last_updated: "{TIMESTAMP}"

## Result File Conventions

- All tabular results: CSV with headers
- All numerical summaries: JSON
- All figures: PNG, 300 DPI, with descriptive filenames
- base_case_evaluation.json format:
  {
    "pass": true/false,
    "metric_name": "spearman_rho",
    "metric_value": 0.73,
    "threshold": 0.7,
    "comparison": "greater_than",
    "details": "Computed over 960 runs across (n, r, beta) grid"
  }

## Coder-Reviewer Protocol

1. Coder runs a step → updates status.yaml
2. If error → writes error.log, sets status to "error"
3. Reviewer reads error.log → writes review.md with fix instructions
4. Coder reads review.md → applies fix → re-runs
5. If success → coder moves to next step
6. After final step → coder runs analysis script → checks base case
7. If base_case_met → done
8. If not → reviewer decides: adjust parameters and re-run, or fail

## Script Conventions

- All scripts must be runnable standalone: `python scripts/{name}.py [args]`
- All scripts must save results to `results/` (relative to experiment directory)
- All scripts must print progress to stdout
- All scripts must catch and print exceptions with full traceback
- All scripts must set random seeds for reproducibility
- Use argparse for any configurable parameters
```

### New skill: vm-interaction

**Location:** `.claude/skills/vm-interaction/SKILL.md`

```markdown
---
name: vm-interaction
description: SSH command patterns, file transfer conventions, and environment setup rules for interacting with the Azure VM. Used by compute-probe, experiment-coder, and experiment-analyst agents.
user-invocable: false
---

# VM Interaction Conventions

## SSH Access

The VM is accessible via: `ssh azure-vm-dissertation`
This is a pre-configured SSH alias. No password or key path needed.

## Command Execution Patterns

### Run a single command:
ssh azure-vm-dissertation "{command}"

### Run a multi-line script:
ssh azure-vm-dissertation << 'REMOTE_EOF'
cd ~/experiments/H{n}
source .venv/bin/activate
python scripts/step1.py
REMOTE_EOF

### Run with timeout (prevent runaway processes):
ssh azure-vm-dissertation "timeout 3600 python ~/experiments/H{n}/scripts/step1.py"

## File Transfer

### Local → VM:
scp experiments/H{n}/scripts/{file} azure-vm-dissertation:~/experiments/H{n}/scripts/

### VM → Local:
scp azure-vm-dissertation:~/experiments/H{n}/results/{file} experiments/H{n}/results/

### Recursive copy:
scp -r azure-vm-dissertation:~/experiments/H{n}/results/ experiments/H{n}/results/

## Environment Setup (per experiment)

ssh azure-vm-dissertation << 'REMOTE_EOF'
mkdir -p ~/experiments/H{n}
cd ~/experiments/H{n}
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install {packages}
REMOTE_EOF

## Rules

1. NEVER run commands as root on the VM.
2. ALWAYS use the experiment-specific venv (source .venv/bin/activate).
3. ALWAYS use `timeout` for long-running commands (default: 1 hour).
4. ALWAYS copy result files back to local after a run completes.
5. If a command fails, capture full stderr:
   ssh azure-vm-dissertation "{command}" 2>&1
6. Check disk space before large operations:
   ssh azure-vm-dissertation "df -h ~"
7. Check RAM before large operations:
   ssh azure-vm-dissertation "free -h"
```

### Modified skill: gap-scoring-rubric

**Add the 5th dimension (Empirical Testability)** to `.claude/skills/gap-scoring-rubric/SKILL.md`:

```markdown
### 5. Empirical Testability (0-10) — NEW in v2

Can this gap be investigated through empirical experiments (running code)?

| Score | Criteria |
|-------|---------|
| 9-10 | Testable by running existing code on public data with commodity hardware (CPU, ≤16GB RAM). |
| 7-8 | Requires writing new experiment code (<500 lines) using existing libraries; public data; standard hardware (CPU or single GPU). |
| 5-6 | Requires moderate new code (500-2000 lines) and/or GPU and/or specialized data preparation. |
| 3-4 | Requires significant new implementation (>2000 lines), proprietary resources, or multi-GPU compute. |
| 1-2 | Requires new theory, algorithms, or mathematical proofs before any experiment is possible. |

## Updated Composite Score (v2)

Composite = (Confidence × 2 + Impact + Feasibility + Verifiability + EmpiricalTestability) / 6

## Updated Tier Assignment (v2)

| Tier | Additional v2 rule |
|------|-------------------|
| Tier 1 | EmpiricalTestability ≥ 5 required |
| Tier 2 | EmpiricalTestability ≥ 3 required |
| Tier 3 | No EmpiricalTestability requirement |

A gap with EmpiricalTestability ≤ 3 CANNOT be Tier 1, regardless of other scores.
```

---

## 11. Directory Structure v2

```
Research-Workflow/
├── .claude/
│   ├── agents/                    # Agent definitions
│   │   ├── source-acquisition.md     (modified)
│   │   ├── source-extraction.md      (modified)
│   │   ├── literature-comprehension.md (modified)
│   │   ├── gap-analysis.md           (modified)
│   │   ├── sanity-check.md           (unchanged)
│   │   ├── hypothesis-formation.md   (modified)
│   │   ├── methodology-design.md     (modified)
│   │   ├── compute-probe.md          (NEW)
│   │   ├── hypothesis-triage.md      (NEW)
│   │   ├── experiment-roadmap.md     (NEW)
│   │   ├── experiment-coder.md       (NEW)
│   │   ├── experiment-reviewer.md    (NEW)
│   │   ├── colab-notebook-generator.md (NEW)
│   │   ├── experiment-analyst.md     (NEW)
│   │   ├── final-paper-assembly.md   (NEW, replaces document-assembly.md)
│   │   ├── critique-v2.md            (NEW, replaces critique.md)
│   │   └── diagnostics-summary.md    (unchanged)
│   ├── skills/
│   │   ├── experiment-execution/SKILL.md  (NEW)
│   │   ├── vm-interaction/SKILL.md        (NEW)
│   │   ├── gap-scoring-rubric/SKILL.md    (modified — 5th dimension)
│   │   ├── source-integrity/SKILL.md      (unchanged)
│   │   ├── writing-style/SKILL.md         (unchanged)
│   │   ├── literature-analysis/SKILL.md   (unchanged)
│   │   ├── source-lookup/SKILL.md         (unchanged)
│   │   ├── source-management/SKILL.md     (modified — remove blog logic)
│   │   ├── web-source-fetching/SKILL.md   (modified — remove blog strategies)
│   │   ├── markdown-conventions/SKILL.md  (modified — add empirical paper format)
│   │   └── methodology-standards/SKILL.md (modified — add implementation spec format)
│   ├── hooks/
│   │   └── pipeline-logger.sh        (simplified — remove env var dependencies)
│   ├── rules/
│   │   └── portable-env.md           (add SSH/VM rules)
│   └── settings.json                 (unchanged)
├── CLAUDE.md                         (rewritten — see Section 8)
├── ARCHITECTURE.md                   (v1 — kept for reference)
├── ARCHITECTURE-V2.md                (this document)
├── pipeline-state.yaml               (expanded schema)
├── sources/                          (Phase 1-2 output)
│   ├── manifest.yaml
│   └── {source-dirs}/content.md
├── user-sources/                     (user drops PDFs here)
├── analysis/                         (Phase 3-5 output)
│   ├── literature-map.md
│   ├── gap-analysis.md
│   └── review-notes.md
├── synthesis/                        (Phase 6-7 + 15 output)
│   ├── hypotheses.md
│   ├── methodology.md
│   └── final-paper.md               (NEW — the actual paper)
├── experiments/                      (NEW — Phases 10-14 output)
│   ├── triage.md                    (Phase 11)
│   ├── H4/                          (per-hypothesis)
│   │   ├── roadmap.md
│   │   ├── status.yaml
│   │   ├── review.md
│   │   ├── error.log
│   │   ├── scripts/
│   │   ├── results/
│   │   │   ├── figures/
│   │   │   └── base_case_evaluation.json
│   │   ├── colab/
│   │   ├── colab-results/
│   │   └── analysis.md
│   ├── H5/
│   │   └── [same structure]
│   └── H3/
│       └── [same structure]
├── reiteration/                      (Phase 16 output)
│   ├── critique.md
│   └── reiteration-plan.md
├── diagnostics/                      (hook output + VM profile)
│   ├── vm-profile.yaml              (NEW)
│   ├── pipeline-run.log
│   ├── phase-metrics.yaml
│   ├── source-lookups.log
│   └── tool-calls.log
└── scripts/                          (extraction scripts)
```

---

## 12. Experiment Directory Conventions

See the `experiment-execution` skill in Section 10 for full details. Key points:

- Each hypothesis gets its own directory under `experiments/`
- `status.yaml` is the single source of truth for experiment state
- The coder-reviewer loop is tracked via `iteration` count in status.yaml
- All results are CSV (tabular) or JSON (scalar/structured)
- All figures are PNG at 300 DPI
- `base_case_evaluation.json` is the definitive pass/fail record
- Colab inputs go in `colab/`, Colab outputs go in `colab-results/`

---

## 13. Colab Notebook Generation

The `colab-notebook-generator` agent produces `.ipynb` files as valid JSON. The notebook structure is defined in the agent specification (Section 9).

**Key constraints on generated notebooks:**
1. **Completely self-contained.** No imports from the project. All pip installs in the notebook.
2. **All data generated or uploaded within the notebook.** No references to local filesystem paths.
3. **Clear output handling.** Results saved to files with `files.download()` calls at the end.
4. **Progress printing.** Each long-running cell prints progress (e.g., "Processing run 47/960...").
5. **Error handling.** Try/except around the main experiment code with informative error messages.
6. **Runtime check.** First code cell verifies GPU is available:
```python
import torch
assert torch.cuda.is_available(), "GPU not available — change runtime to GPU"
print(f"GPU: {torch.cuda.get_device_name(0)}")
```

---

## 14. SSH and VM Interaction Conventions

See the `vm-interaction` skill in Section 10 for full details. Key points:

- SSH alias: `azure-vm-dissertation` (pre-configured, no password)
- All experiment work goes in `~/experiments/H{n}/` on the VM
- Each experiment gets its own venv
- Always use `timeout` for long-running commands
- Always copy results back to local after runs
- Never run as root

---

## 15. Changes to Existing Scripts

### `scripts/phase1_search.py`

**Changes:**
1. Replace `download_arxiv_source()` with PDF-based download as primary method
2. Add `verify_paper_identity()`:
```python
def verify_paper_identity(content_file: str, expected_title: str, expected_author: str) -> bool:
    """Grep for title keywords and author surname in extracted content."""
    if not os.path.isfile(content_file):
        return False
    with open(content_file, encoding='utf-8', errors='replace') as f:
        text = f.read(5000).lower()
    # Check for 2+ words from title
    title_words = [w.lower() for w in expected_title.split() if len(w) > 3]
    title_hits = sum(1 for w in title_words if w in text)
    # Check for author surname
    author_surname = expected_author.split(',')[0].split()[-1].lower()
    author_hit = author_surname in text
    return title_hits >= 2 and author_hit
```
3. Add `search_code_repos()`:
```python
def search_code_repos(title: str, authors: list, year: int) -> list:
    """Search Semantic Scholar for linked code repos."""
    # Query Semantic Scholar for paper
    # Extract 'url' field which sometimes points to GitHub
    # Also search GitHub API: repos matching title keywords
    pass
```
4. Remove `WEB_SOURCES` list and `download_web_source()` function entirely
5. Remove all references to `authenticated_extract.py` for blog sources

### `scripts/check_content_quality.py`

**No changes needed** — already does keyword-based content validation.

### `scripts/flag_mismatched_sources.py` and variants

**Keep as-is** — useful for post-hoc validation. May need to run again if Phase 1 has issues.

### `pipeline-logger.sh`

**Simplify:**
- Remove all `CLAUDE_*` env var reads (they don't work)
- Log only: timestamp, event name, current_phase from pipeline-state.yaml
- Remove the `safe_env()` function and env probe

---

## 16. Implementation Sprint Plan

### Sprint 1: Foundation Updates (estimated: 2-3 hours)

- [ ] Update `CLAUDE.md` with new orchestrator logic (Section 8)
- [ ] Update `pipeline-state.yaml` schema to include phases 10-16
- [ ] Simplify `pipeline-logger.sh` (remove env var dependencies)
- [ ] Update `.claude/rules/portable-env.md` with SSH/VM rules

### Sprint 2: Modify Existing Agents (estimated: 2-3 hours)

- [ ] Modify `source-acquisition.md` — remove blogs, add PDF primary, add identity verification, add repo search
- [ ] Modify `source-extraction.md` — PDF primary extraction
- [ ] Modify `literature-comprehension.md` — add Section 10 (Implementation Landscape), aggressive context management
- [ ] Modify `gap-analysis.md` — add 5th dimension (Empirical Testability)
- [ ] Modify `hypothesis-formation.md` — FATES, type tagging, implementation sketch, no theoretical-proof
- [ ] Modify `methodology-design.md` — implementation specification, base cases, compute requirements

### Sprint 3: Modify Existing Skills (estimated: 1-2 hours)

- [ ] Modify `gap-scoring-rubric/SKILL.md` — add Empirical Testability dimension
- [ ] Modify `source-management/SKILL.md` — remove blog logic
- [ ] Modify `web-source-fetching/SKILL.md` — remove blog strategies
- [ ] Modify `markdown-conventions/SKILL.md` — add empirical paper format
- [ ] Modify `methodology-standards/SKILL.md` — add implementation spec format

### Sprint 4: New Skills (estimated: 1 hour)

- [ ] Create `experiment-execution/SKILL.md`
- [ ] Create `vm-interaction/SKILL.md`

### Sprint 5: New Planning Agents (estimated: 2-3 hours)

- [ ] Create `compute-probe.md`
- [ ] Create `hypothesis-triage.md`
- [ ] Create `experiment-roadmap.md`

### Sprint 6: New Execution Agents (estimated: 3-4 hours)

- [ ] Create `experiment-coder.md`
- [ ] Create `experiment-reviewer.md`
- [ ] Create `colab-notebook-generator.md`
- [ ] Create `experiment-analyst.md`

### Sprint 7: New Assembly Agents (estimated: 2-3 hours)

- [ ] Create `final-paper-assembly.md` (replaces `document-assembly.md`)
- [ ] Create `critique-v2.md` (replaces `critique.md`)
- [ ] Archive old `document-assembly.md` and `critique.md` (move to `.claude/agents/archived/`)

### Sprint 8: Update Scripts (estimated: 1-2 hours)

- [ ] Update `scripts/phase1_search.py` — PDF download, identity verification, repo search
- [ ] Simplify `scripts/pipeline-logger.sh`

### Sprint 9: End-to-End Test (estimated: varies)

- [ ] Run full pipeline on the existing topic ("Dual Convex Optimization in ReLU Neural Networks")
- [ ] Verify Phase 1 downloads correct papers
- [ ] Verify Phase 10 profiles the VM correctly
- [ ] Verify Phase 11 selects reasonable hypotheses
- [ ] Verify Phase 12 produces implementable roadmaps
- [ ] Verify Phase 13 coder can SSH, run code, collect results
- [ ] Verify Phase 14 produces valid analysis
- [ ] Verify Phase 15 produces a coherent paper
- [ ] Verify Phase 16 critique is meaningful

---

## 17. Architecture Decisions Log v2

### Decision 1: Papers only, no blogs

**Rationale:** Blogs introduce secondary-source reliability issues (the NTK blog post was the only NTK source in v1, causing attribution thinness). For empirical research, primary sources (papers) are sufficient and more reliable. Removing blogs simplifies Phase 1 significantly and eliminates the need for `authenticated_extract.py` browser profiles.

### Decision 2: PDF download + OCR instead of LaTeX tarballs

**Rationale:** arXiv tarballs returned wrong papers 57% of the time in v1. PDF download is reliable — the PDF for arxiv ID X is always the PDF for paper X. Mistral OCR produces good-enough markdown for our purposes (we need text, not perfect LaTeX rendering).

### Decision 3: Empirical-first hypothesis selection

**Rationale:** The user's bar is pre-doctoral empirical research, not theoretical contributions. Hypotheses requiring new proofs are explicitly deprioritized. The FATES criteria (adding Empirical tractability) encode this preference at the scoring level.

### Decision 4: Sequential hypothesis execution, not parallel

**Rationale:** The VM is a single machine with 4 vCPU and 16GB RAM. Running multiple experiments simultaneously would cause resource contention. Sequential execution also simplifies the orchestrator logic and makes the coder-reviewer loop easier to manage.

### Decision 5: Colab notebook generation for GPU steps

**Rationale:** The VM has no GPU. Rather than abandoning GPU-dependent experiments, we generate self-contained Colab notebooks that the user can upload and run manually. The results flow back into the pipeline via the `colab-results/` directory. This keeps the pipeline flexible without requiring complex cloud GPU orchestration.

### Decision 6: Separate coder and reviewer agents (not a single agent)

**Rationale:** The coder agent needs to be good at writing Python code and executing SSH commands. The reviewer agent needs to be good at evaluating experimental results and making scientific decisions. These are different skills best served by different prompts and potentially different models (Sonnet for coding, Opus for review). Separating them also prevents the common failure mode where a single agent writes code, sees it fail, and keeps making the same mistake — the reviewer provides an external perspective.

### Decision 7: Deferred document assembly and critique to after experiments

**Rationale:** In v1, the final document was written before any experiments were run, making it a proposal. In v2, the document is written after experiments, making it a paper with results. The critique now evaluates the full package including experimental quality. This changes the document from "here's what to research" to "here's what we found."

### Decision 8: Base case as the definitive completion criterion

**Rationale:** Without a clear pass/fail criterion, the experiment loop could run indefinitely. The base case (defined in the roadmap) provides a concrete stopping condition. The reviewer can only declare "base_case_met" or "base_case_failed" — it cannot move the goalposts. This prevents both premature stopping and infinite iteration.

### Decision 9: Simplified diagnostics (remove env var dependencies)

**Rationale:** Claude Code's hook system doesn't expose the environment variables our logger expected. Rather than building workarounds, we simplify to logging only what's knowable (timestamps, phase transitions from pipeline-state.yaml). The diagnostics are useful for timing and debugging, not for detailed tool-call analytics.

### Decision 10: 3 hypotheses (not more, not fewer)

**Rationale:** 3 hypotheses × detailed experiments + analysis is the right scope for an empirical paper. Fewer would feel thin; more would be rushed. Each hypothesis gets a full section in the paper (setup, results, analysis). This matches the standard structure of an empirical ML paper that tests multiple related claims.

---

*End of Architecture v2 Document*
