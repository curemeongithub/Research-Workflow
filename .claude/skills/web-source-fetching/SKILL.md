---
name: web-source-fetching
description: Site-specific fetch strategies for downloading research sources (arXiv, PDFs, GitHub, web pages). Use in Phase 1 before running any download command to choose the correct fetch method.
user-invocable: false
---

# Web Source Fetching Strategies

Site-specific fetch strategies for downloading research sources. Read this before running any download command.

---

## Decision Tree: Choosing a Fetch Method

```
Is it an arXiv paper?
├─ YES → Download LaTeX source (ALWAYS prefer over PDF)
│       curl -sL "https://arxiv.org/src/{PAPER_ID}" -o source.tar.gz
└─ NO
   ├─ Is it a PDF?
   │  ├─ Is it a OneNote export? (handwritten, no text layer)
   │  │  └─ YES → .venv/bin/python scripts/onenote_pdf_to_markdown.py file.pdf -o output/
   │  └─ NO (standard PDF: textbooks, papers, scanned docs)
   │     ├─ Need Markdown + images? → .venv/bin/python scripts/mistral_ocr.py file.pdf -o output/
   │     └─ Just text? → pdftotext -layout file.pdf > file.txt
   ├─ Is it a GitHub repo or file?
   │  ├─ Repo → git clone --depth 1 "URL" sources/github.com/OWNER/REPO/
   │  └─ Single file → curl -sL "https://raw.githubusercontent.com/OWNER/REPO/BRANCH/PATH"
   └─ Is it any other web page?
      ├─ DEFAULT → .venv/bin/python scripts/authenticated_extract.py "URL"
      ├─ Substack/Medium → add --profile substack or --profile medium
      └─ Static HTML fallback → .venv/bin/python scripts/webpage_to_md.py "URL" -o output/
```

---

## Site-Specific Strategies

### arXiv

**Best approach: LaTeX source**

```bash
mkdir -p "sources/arxiv-{PAPER_ID}"
cd "sources/arxiv-{PAPER_ID}"
curl -sL "https://arxiv.org/src/{PAPER_ID}" -o source.tar.gz
tar -xzf source.tar.gz && rm source.tar.gz
cd -
```

Folder naming: always `arxiv-{PAPER_ID}` (hyphenated). Example: `arxiv-2010.11929`.

arXiv URL patterns:
- `arxiv.org/abs/PAPER_ID` — abstract page
- `arxiv.org/pdf/PAPER_ID` — PDF
- `arxiv.org/src/PAPER_ID` — LaTeX source tarball (preferred)

### Substack

```bash
# Public posts
.venv/bin/python scripts/authenticated_extract.py "URL"

# Paywalled posts (requires authenticated browser profile)
.venv/bin/python scripts/authenticated_extract.py "URL" --profile substack
```

After extraction, verify for paywall:
```bash
grep -i 'upgrade to paid\|subscribe to continue\|unlock this post' content.md && echo "PAYWALL HIT"
```

### d2l.ai

```bash
.venv/bin/python scripts/authenticated_extract.py "https://d2l.ai/{chapter}/{section}.html" -s ".document"
```

The `-s ".document"` selector extracts only the main content, not the navigation.

### Distill.pub

```bash
.venv/bin/python scripts/authenticated_extract.py "https://distill.pub/YEAR/ARTICLE/"
```

### HuggingFace (docs, papers, model cards)

```bash
.venv/bin/python scripts/authenticated_extract.py "URL"
```

### GitHub Repositories

```bash
git clone --depth 1 "https://github.com/OWNER/REPO.git" "sources/github.com/OWNER/REPO"
```

For a single file:
```bash
curl -sL "https://raw.githubusercontent.com/OWNER/REPO/BRANCH/PATH" -o "sources/github.com/OWNER/REPO/filename"
```

---

## Completeness Verification (MANDATORY After Any Web Extraction)

Readability is necessary but not sufficient. A web extraction can produce a .md file that is missing entire sections.

**Always run after extracting any web article:**

```bash
# 1. List section headings
grep '^##\|^###\|^####' content.md | head -20

# 2. Check for paywall markers
grep -i 'upgrade to paid\|subscribe to continue\|for paid subscribers' content.md

# 3. Check the ending (does it end with a conclusion or cut off?)
tail -20 content.md

# 4. Check file size
wc -c content.md   # Must be > 500 characters
```

If section headings are missing or the article cuts off abruptly, re-extract with `--profile` or try a different method.

---

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Use web search snippets as content | Download the full page |
| Fabricate or guess URLs | Only use URLs you've actually fetched a response from |
| Trust that a large .md file has complete content | Verify with section heading check |
| Use `grep` results to declare content missing | Check section headings first; grep false negatives are common |
| Use system python | Always `.venv/bin/python` |
