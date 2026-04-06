---
name: web-source-fetching
description: Site-specific fetch strategies for downloading research papers (arXiv PDFs, standard PDFs, GitHub repos). Use in Phase 1 before running any download command to choose the correct fetch method.
user-invocable: false
---

# Source Fetching Strategies

Fetch strategies for downloading research papers. Read this before running any download command.

**v2 change:** Papers only. No blogs, Substack, Medium, distill.pub, or personal websites. arXiv uses PDF download + Mistral OCR (not LaTeX tarballs).

---

## Decision Tree: Choosing a Fetch Method

```
Is it an arXiv paper?
├─ YES → Download PDF + Mistral OCR (ALWAYS)
│       curl -sL "https://arxiv.org/pdf/{PAPER_ID}" -o paper.pdf
│       .venv/bin/python scripts/mistral_ocr.py paper.pdf -o output/
└─ NO
   ├─ Is it a PDF?
   │  ├─ Is it a OneNote export? (handwritten, no text layer)
   │  │  └─ YES → .venv/bin/python scripts/onenote_pdf_to_markdown.py file.pdf -o output/
   │  └─ NO (standard PDF: textbooks, papers, scanned docs)
   │     └─ .venv/bin/python scripts/mistral_ocr.py file.pdf -o output/
   ├─ Is it a GitHub repo or file?
   │  ├─ Repo → git clone --depth 1 "URL" sources/github.com/OWNER/REPO/
   │  └─ Single file → curl -sL "https://raw.githubusercontent.com/OWNER/REPO/BRANCH/PATH"
   └─ Any other URL → NOT SUPPORTED in v2 (papers only)
```

---

## Site-Specific Strategies

### arXiv

**Best approach: PDF download + Mistral OCR**

```bash
PAPER_ID="2010.11929"
mkdir -p "sources/arxiv-$PAPER_ID"
curl -sL "https://arxiv.org/pdf/$PAPER_ID" -o "sources/arxiv-$PAPER_ID/$PAPER_ID.pdf"
.venv/bin/python scripts/mistral_ocr.py "sources/arxiv-$PAPER_ID/$PAPER_ID.pdf" -o "sources/arxiv-$PAPER_ID/"
```

Folder naming: always `arxiv-{PAPER_ID}` (hyphenated). Example: `arxiv-2010.11929`.

arXiv URL patterns:
- `arxiv.org/abs/PAPER_ID` — abstract page
- `arxiv.org/pdf/PAPER_ID` — PDF (PRIMARY in v2)
- `arxiv.org/src/PAPER_ID` — LaTeX source tarball (deprecated in v2 — unreliable)

**Identity verification (MANDATORY):** After extraction, grep for title keywords and first author surname in content.md. If neither match, mark as `identity_verified: false` and flag for review.

### GitHub Repositories

```bash
git clone --depth 1 "https://github.com/OWNER/REPO.git" "sources/github.com/OWNER/REPO"
```

For a single file:
```bash
curl -sL "https://raw.githubusercontent.com/OWNER/REPO/BRANCH/PATH" -o "sources/github.com/OWNER/REPO/filename"
```

---

## Completeness Verification (MANDATORY After Any Extraction)

```bash
# 1. Check file size
wc -c sources/{PATH}/content.md   # Must be > 500 characters

# 2. Check section headings exist
grep '^##\|^###\|^####' sources/{PATH}/content.md | head -20

# 3. Check the ending (does it end with a conclusion or cut off?)
tail -20 sources/{PATH}/content.md
```

---

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Use web search snippets as content | Download the full paper PDF |
| Fabricate or guess URLs | Only use URLs you've confirmed exist |
| Trust that a large .md file has complete content | Verify with section heading check |
| Download LaTeX tarballs from arXiv | Use PDF download + Mistral OCR |
| Use system python | Always `.venv/bin/python` |
