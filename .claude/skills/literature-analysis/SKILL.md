---
name: literature-analysis
description: MECE-based rules for organizing and synthesizing a literature map. Use when creating literature maps, clustering papers by research theme, and cross-paper synthesis in Phase 3.
user-invocable: false
---

# Literature Analysis

Rules for organizing and synthesizing the literature map (Phase 3). The core principle is MECE: the theme structure must be Mutually Exclusive and Collectively Exhaustive.

---

## MECE Principle

**Mutually Exclusive:** Each paper's primary contribution appears in exactly one theme section. No paper's core argument is split across multiple sections or double-counted.

**Collectively Exhaustive:** Every paper in the manifest appears somewhere in the literature map. No paper is dropped.

**Test:** After writing, for each paper in the manifest — can you point to exactly one section where its main contribution lives?

---

## Theme Identification

### Step 1 — Cluster by Research Question

Before writing, read all sources and cluster them by the research question they answer:
- What problem does this paper address?
- What is its core contribution type? (algorithm, theory, dataset, evaluation, application)
- What baseline does it improve on?

Papers that answer the same research question belong in the same theme.

### Step 2 — Name Themes by Question, Not Method

Name theme sections by the intellectual question they answer, not by the method used:

**BAD:** "Transformer-based Approaches"  
**GOOD:** "Scaling Visual Representations Beyond CNNs"

**BAD:** "Contrastive Learning Methods"  
**GOOD:** "Self-Supervised Pre-Training for Transfer"

### Step 3 — Handle Multi-Contribution Papers

Some papers contribute to multiple themes. Place the paper in the theme matching its *primary* contribution. In other sections, reference it briefly: "This approach was later extended to X by [AuthorYear]."

---

## Cross-Paper Synthesis

The literature map should reveal connections that don't exist in any single paper:

- Papers that contradict each other (log these for Section 6 "Contested Areas")
- Papers that solve each other's limitations (A's weakness is addressed by B)
- Papers with similar methods but different claims about the same result
- Methodological convergence: multiple independent groups using similar approaches
- Timeline patterns: where the field accelerated, where it stalled

**When you spot a cross-paper connection, name it explicitly** in the theme section. Do not assume the reader will notice.

---

## Depth vs. Coverage

The literature map must be both deep and complete. Do not sacrifice:

- **Depth** on foundational papers to list more papers
- **Coverage** by deep-diving only your favorite papers

Rule of thumb: allocate ~100-150 words per paper, grouped into thematic paragraphs. Seminal papers may get more. Recent incremental papers may be batched: "Several subsequent papers explored X in different settings [Cite1, Cite2, Cite3]."

---

## Required Structural Sections

Every literature map must include:

1. **Overview** — why this field exists and who works on it
2. **Foundational Work** — how the problem was initially defined
3. **Theme Sections** (3-5) — organized by research question, MECE
4. **Contested Areas** — where papers disagree
5. **Methodological Landscape** — benchmarks, metrics, experimental norms
6. **Research Timeline** — chronological evolution
7. **Key Papers Summary** — one entry per paper from the manifest

---

## Anti-Patterns

- **Paper-by-paper structure** instead of theme-by-theme: "Smith et al. did X. Jones et al. did Y." — this is a bibliography, not a literature map.
- **Recency bias:** Only covering the last 2 years. Include foundational papers from 5-10 years ago.
- **Coverage inflation:** Mentioning 40 papers in 1-2 sentences each with no synthesis.
- **Missing contested areas:** Finding no disagreements is suspicious. Look harder.
