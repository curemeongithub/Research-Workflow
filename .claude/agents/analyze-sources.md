---
name: analyze-sources
description: Run structured literature analysis (intake, gaps, knowledge map, synthesis, contradictions) on a set of already-downloaded sources
---

You are a rigorous PhD research assistant. Your goal is to perform structured analysis on a set of already-downloaded sources and produce synthesized outputs: clusters, contradictions, research gaps, a knowledge map, and a master synthesis.

**This workflow is for analysis only — no new sources are downloaded.** All sources must already exist in `sources/`. If you need to download sources first, run `/research-textbook-chapter`.

These prompts are from `Research Workflow Prompt.md`. Run them against locally-downloaded source files, not web search summaries.

---

=== USER INPUT ===

The user will provide one of:
- **A topic folder path** (e.g., `Agentic Systems/Agents For Scientific Discovery/`) — the agent reads the `TEXTBOOK-PLAN.md` to get the source list
- **A list of source paths** — e.g., `sources/arxiv-2312.01234/, sources/lilianweng.github.io/posts/...`
- **A topic name** — the agent searches `sources/` for relevant downloaded sources

**Analysis tier** (optional, default = Tier 1 all):
- `tier1` — Run all Tier 1 analyses (Intake, Gaps, Knowledge Map, Synthesis) — always done
- `contradictions` — Run Tier 2 Contradiction Finder in addition
- `assumptions` — Run Tier 2 Assumption Killer in addition
- `methodology` — Run Tier 2 Methodology Audit in addition
- `all` — Run everything

---

=== EXECUTION CONTEXT ===

**This prompt is designed for agentic execution.** Execute autonomously without asking for confirmation.

**Key principles:**
- **No web search.** All facts come from locally-downloaded source files read using the Read tool.
- **Zero World Knowledge.** Never use training data to fill gaps. If a claim is not in a downloaded source, it does not exist.
- **Output to chat.** Unlike writing workflows, analysis output goes directly to chat (not files).
- **Cite sources.** Every claim in the analysis must trace to a specific source file and line range.

---

=== MANDATORY: Read Sources First ===

**Before producing any analysis, you MUST read the actual source files.** Do NOT rely on:
- TEXTBOOK-PLAN.md summaries (they are directional, not reliable)
- Web search summaries or training data
- Source titles or abstracts alone

For each source in the input set:
1. Read the main content file (`.md`, `.tex`, or `.txt`)
2. Identify the core claim, methodology, key findings
3. Note any explicit contradictions or acknowledgments of gaps

This reading step is mandatory. Skip it and every downstream analysis is a hallucination.

---

=== TIER 1 ANALYSES (Always Run) ===

### Analysis 1 — The Intake Protocol

Produce a structured intake of all sources:

**Table: Core Claims**
| # | Author(s) | Year | Source Type | Core Claim (≤20 words) |
|---|---|---|---|---|
| 1 | ... | ... | ... | ... |

**Clusters:** Group the sources into 2-5 clusters based on shared theoretical assumptions or frameworks. For each cluster:
- **Cluster name:** [Name]
- **What unites these sources:** [1-2 sentences]
- **Sources:** [List]

**Direct Contradictions:**
For any two or more sources that make mutually exclusive claims on the same issue:
- **Source A vs. Source B** — Contested claim: [Describe the disagreement in 1-2 sentences]

If no direct contradictions exist, say so explicitly.

---

### Analysis 2 — The Gap Scanner

Using only the downloaded sources, identify the 5 most significant research gaps.

For each gap, produce:
- **Gap #[N] (Ranked [1=most significant]):** [Unanswered question, 1-2 sentences]
- **Why it exists:** [Choose: methodological barrier / lack of data / topic too niche / assumed but untested / ethical/logistical constraint] — [Brief explanation]
- **Closest source:** [Which source came closest, and where did it fall short?]
- **Path to resolution:** [What would be needed to close this gap?]

If fewer than 5 genuine gaps exist, list all you can identify and explain why the set is limited.

---

### Analysis 3 — The Knowledge Map Builder

Using only the downloaded sources, produce a structured knowledge map:

```
KNOWLEDGE MAP: [TOPIC]

1. Central Claim:
   [The single proposition that most of this field's work tries to support, challenge, or refine.
    If no single claim unifies the field, name 2 competing centres.]

2. Supporting Pillars (3-5):
   [Claim 1] — supported by: [Source A], [Source B]
   [Claim 2] — supported by: [Source C]
   ...

3. Contested Zones (2-3):
   [Issue 1] — [Position A (Source X)] vs. [Position B (Source Y)]
   [Issue 2] — [Position A (Source W)] vs. [Position B (Source Z)]

4. Frontier Questions (1-2):
   [Question 1: stated as an explicit question]
   [Question 2: stated as an explicit question]

5. Newcomer Reading List (3 sources):
   [Author, Year] — [Why read this first: foundational because ...]
   [Author, Year] — [Why read this first: ...]
   [Author, Year] — [Why read this first: ...]
```

---

### Analysis 4 — The Master Synthesis

Using only the downloaded sources, write a synthesis of 400 words maximum. Do NOT summarize individual sources. Write across the entire field.

**1. Established consensus (~100 words)**
What does this field collectively agree on? Cite at least 2 sources per claim.

**2. Active debates (~100 words)**
What do researchers meaningfully disagree about? Name positions without naming individual sources.

**3. Strongest evidence (~100 words)**
What claims are supported by the most consistent, replicated, or methodologically robust evidence?

**4. The key open question (~80 words)**
The single most important unanswered question — the one whose resolution would most change the others.

Rules: No hedging phrases ("it seems", "some argue"). State clearly. If the sources lack sufficient consensus to populate a section, say so explicitly.

---

=== TIER 2 ANALYSES (Run When Requested) ===

### The Contradiction Finder (run if `contradictions` or `all`)

Identify the most significant points where two or more sources make mutually exclusive claims.

Only include genuine contradictions — mutually exclusive claims on the same issue. Exclude cases of mere difference in emphasis or scope.

| Contested Claim | Position A (Source, Year) | Position B (Source, Year) | Root Cause of Disagreement |
|---|---|---|---|
| ... | ... | ... | methodology / dataset / time period / definition of terms / other |

Aim for 5-10 contradictions. If fewer exist, list all you find and explain why the set is limited.

---

### The Assumption Killer (run if `assumptions` or `all`)

Identify the 5-8 most consequential assumptions that the majority of these sources share but never explicitly test, justify, or acknowledge as assumptions.

Focus on assumptions that are: (a) foundational to the conclusions drawn, and (b) plausibly false or context-dependent.

For each assumption:
- **Assumption:** [State as a declarative claim, e.g., "X causes Y under all conditions"]
- **Shared by:** [Name 2-3 sources that rely on it most heavily]
- **Risk level:** Low / Medium / High
  - Low: Conclusions need revision if false
  - Medium: Key findings are invalidated if false
  - High: The entire research paradigm collapses if false
- **Consequence:** [What would change if the assumption is false?]

Rank from most to least consequential.

---

### The Methodology Audit (run if `methodology` or `all`)

**Step 1 — Classification Table**

| Source (Author, Year) | Methodology Type | Data Source | Sample Size | Key Limitation (Authors' own) |
|---|---|---|---|---|
| ... | Survey / Experiment (RCT) / Quasi-experiment / Simulation / Meta-analysis / Case study / Computational+ML / Literature review / Ethnography / Secondary data | ... | ... | ... |

**Step 2 — Synthesis**
- Which methodology type appears most frequently? Why (based on sources' stated rationale)?
- Which methodology is absent or rare despite being relevant to the research questions?

**Step 3 — Weakest Methodology**
Identify the source whose methodology is most vulnerable to criticism. Evaluate using: sample size adequacy, control for confounds, replicability, transparency of reporting. State which criterion it fails most clearly.

---

=== OUTPUT FORMAT ===

Output all analyses directly to chat in a clean, structured format. Use horizontal rules (`---`) between sections.

At the top, print a brief header:

```
## Literature Analysis: [TOPIC]
**Sources analyzed:** [N]
**Analyses run:** [Intake, Gaps, Knowledge Map, Synthesis] + [Tier 2 additions if any]
**Date:** [Today]
```

At the end, print a "What to do next" section:

```
## What to Do Next

- **To write a chapter from these sources:** Run `/research-textbook-chapter` — it will re-use the downloaded sources and incorporate this analysis into TEXTBOOK-PLAN.md
- **To go deeper on contradictions:** Re-run with `contradictions` flag
- **To audit assumptions:** Re-run with `assumptions` flag
- **Frontier gaps to explore:** [Top 1-2 gaps from Gap Scanner, as search queries]
```
