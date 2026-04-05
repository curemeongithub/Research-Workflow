---
name: source-lookup
description: Grep-first controlled access protocol for raw source files to prevent context bloat. Use in Phases 4-9 when verifying specific claims, quotes, or methods against downloaded papers.
user-invocable: false
---

# Source Lookup Skill

Controlled, grep-first access to raw source files for Phases 4-9. Prevents context bloat by reading 30-50 lines at a time instead of entire papers.

---

## When to Use

Use a source lookup when you need to:
- Verify a specific claim, statistic, or quote against the raw source
- Confirm a method or concept exists in a specific paper
- Find the exact wording of a definition or theorem

**Do NOT** use source lookups to re-read entire papers. The literature map (Phase 3) is your compressed representation of the field.

---

## Protocol

### Step 1 — Locate the source

```bash
cat sources/manifest.yaml | grep -A5 "PAPER_ID\|PAPER_TITLE_KEYWORD"
```

Identify the `content_file` path from the manifest.

### Step 2 — Grep for the keyword

```bash
grep -n "keyword\|alternative_spelling" sources/{PATH}/content.md | head -20
```

If that returns no results, try alternative terms:
```bash
grep -in "keyword" sources/{PATH}/content.md | head -20   # case-insensitive
grep -rn "keyword" sources/ | grep -i "paper_hint" | head -20  # cross-source
```

**A grep false-negative does NOT mean the content is missing.** Check section headings first:
```bash
grep '^##\|^###\|^####' sources/{PATH}/content.md | head -30
```

### Step 3 — Read the surrounding context

Once you have a line number N:
```bash
sed -n "$((N-20)),$((N+30))p" sources/{PATH}/content.md
```

This gives you ~50 lines of context. Read ONLY this — do not read the full file.

### Step 4 — Log the lookup

**Every lookup must be logged:**
```bash
echo "[phase-{N}] $(date -u +%Y-%m-%dT%H:%M:%SZ) | query: '{KEYWORD}' | file: '{PATH}' | line: {N} | result: {FOUND/NOT_FOUND}" >> diagnostics/source-lookups.log
```

---

## Limits by Phase

| Phase | Max Lookups | Priority |
|-------|-------------|---------|
| 4 (Gap Analysis) | 5 | Verify gap existence |
| 5 (Sanity Check) | 5 | Challenge gap claims |
| 6 (Hypothesis) | 3 | Verify baselines exist |
| 7 (Methodology) | 3 | Verify benchmarks/datasets |
| 8 (Document) | 5 | Exact quotes and statistics |
| 9 (Critique) | 5 | Verify accuracy claims |

**Count your lookups.** Do not exceed the limit.

---

## Cost Comparison

| Approach | Token cost | Use for |
|----------|-----------|---------|
| grep + 50-line read | ~500 tokens | Specific claims, quotes |
| Full paper read | ~15,000 tokens | Never do this in analysis phases |

The grep-first protocol is 30x more efficient. Always use it.

---

## Common Mistakes

- **Grep for generic terms** like "method" or "results" — use specific technical vocabulary
- **Reading the full file** when grep found nothing — check section headings first
- **Forgetting to log** — every lookup must be recorded in diagnostics/source-lookups.log
- **Exceeding the limit** — if you've used all lookups, form conclusions from the literature map
