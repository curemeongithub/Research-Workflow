---
name: source-management
description: Rules for storing and organizing downloaded sources in the centralized sources/ directory. Use when downloading, naming, or checking for existing sources in Phases 1-2.
user-invocable: false
---

# Source Management

Rules for storing and organizing downloaded sources. All sources share a centralized `sources/` directory.

---

## Centralized Storage (CRITICAL)

**All sources are stored in `sources/` at the project root — NOT in per-chapter or per-run subfolders.**

This is a shared, persistent repository. Sources downloaded for one run are available to all future runs. Always check if a source already exists before downloading.

---

## Folder Naming Conventions

| Source Type | Pattern | Example |
|-------------|---------|---------|
| arXiv papers | `sources/arxiv-{PAPER_ID}` | `sources/arxiv-2010.11929/` |
| GitHub repos | `sources/github.com/{OWNER}/{REPO}/` | `sources/github.com/google/jax/` |
| User PDFs | `sources/user-{filename}/` | `sources/user-my-notes/` |

**URL → folder conversion rules:**
1. Strip `https://` and `http://`
2. Strip `www.`
3. Remaining URL path = folder path
4. Main content stored as `content.md` inside the folder

---

## Check Before Downloading

**Always check if a source already exists:**

```bash
ls "sources/arxiv-2010.11929/" 2>/dev/null && echo "EXISTS" || echo "NEW"
```

If it exists and has a readable content file, skip downloading.

---

## Quick Reference: Download Commands

| Source Type | Command |
|-------------|---------|
| arXiv (primary) | `mkdir -p "sources/arxiv-{ID}" && curl -sL "https://arxiv.org/pdf/{ID}" -o "sources/arxiv-{ID}/{ID}.pdf" && .venv/bin/python scripts/mistral_ocr.py "sources/arxiv-{ID}/{ID}.pdf" -o "sources/arxiv-{ID}/"` |
| Standard PDF | `.venv/bin/python scripts/mistral_ocr.py file.pdf -o "sources/{domain}/{path}/"` |
| GitHub repo | `git clone --depth 1 "URL" "sources/github.com/OWNER/REPO"` |

---

## Readability Verification

Every source must have at least one readable text file (>500 characters):

```bash
wc -c "sources/{PATH}/content.md" 2>/dev/null | awk '{if ($1 > 500) print "OK"; else print "UNREADABLE"}'
```

A source with `readable: false` in the manifest must be re-extracted before Phase 3 uses it.

---

## Per-Source Manifest Entry Schema

```yaml
- id: arxiv-2010.11929
  type: arxiv            # arxiv | pdf | github | user-pdf
  title: "Paper title"
  authors: ["Last, First", "Last, First"]
  year: 2020
  url: "https://arxiv.org/abs/2010.11929"
  local_path: sources/arxiv-2010.11929/
  content_file: sources/arxiv-2010.11929/content.md
  readable: true
  identity_verified: true
  char_count: 48392
  has_figures: true
  extraction_method: mistral-ocr-pdf   # mistral-ocr-pdf | raw-html
  code_repos: []
  notes: ""
```
