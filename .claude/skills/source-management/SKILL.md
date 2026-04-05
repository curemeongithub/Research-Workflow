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
| Blog posts | `sources/{domain}/{path}/` | `sources/lilianweng.github.io/posts/2022-06-09-vlm/` |
| d2l.ai chapters | `sources/d2l.ai/{chapter-path}/` | `sources/d2l.ai/chapter_attention/vision-transformer/` |
| HuggingFace | `sources/huggingface.co/docs/{path}/` | `sources/huggingface.co/docs/transformers/vit/` |
| Other sites | `sources/{domain}/{path}/` | `sources/distill.pub/2021/gnn-intro/` |
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
| arXiv (preferred) | `mkdir -p "sources/arxiv-{ID}" && cd "sources/arxiv-{ID}" && curl -sL "https://arxiv.org/src/{ID}" -o source.tar.gz && tar -xzf source.tar.gz && rm source.tar.gz` |
| GitHub repo | `git clone --depth 1 "URL" "sources/github.com/OWNER/REPO"` |
| Web page (default) | `.venv/bin/python scripts/authenticated_extract.py "URL"` |
| Web page + auth | `.venv/bin/python scripts/authenticated_extract.py "URL" --profile substack` |
| Static HTML (faster) | `.venv/bin/python scripts/webpage_to_md.py "URL" -o "sources/{domain}/{path}/"` |
| Standard PDF | `.venv/bin/python scripts/mistral_ocr.py file.pdf -o "sources/{domain}/{path}/"` |

---

## PDF Figure Conversion

arXiv papers include figures as PDFs. Convert to PNG for markdown embedding.

```bash
# Single figure
magick -density 400 "sources/arxiv-{ID}/images/figure.pdf" -trim +repage "sources/arxiv-{ID}/images/figure.png"

# Batch convert all PDF figures in an arXiv source
find "sources/arxiv-{ID}/" \( -name '*.pdf' \) \
  \( -path '*/images/*' -o -path '*/figs/*' -o -path '*/figures/*' -o -path '*/resources/*' \) | \
while read f; do
  outfile="${f%.pdf}"
  [ ! -f "${outfile}.png" ] && \
    magick -density 400 "$f" -trim +repage "${outfile}.png" && \
    echo "Converted: $f → ${outfile}.png"
done
```

**Validate (detect blank placeholders):**
```bash
find "sources/arxiv-{ID}/" -name '*.png' -size -10k | while read f; do
  pdf="${f%.png}.pdf"
  [ -f "$pdf" ] && echo "SUSPECT BLANK: $f — re-converting..."
  magick -density 400 "$pdf" -trim +repage "$f"
done
```

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
  type: arxiv            # arxiv | blog | documentation | pdf | github | user-pdf
  title: "Paper title"
  authors: ["Last, First", "Last, First"]
  year: 2020
  url: "https://arxiv.org/abs/2010.11929"
  local_path: sources/arxiv-2010.11929/
  content_file: sources/arxiv-2010.11929/content.md
  readable: true
  char_count: 48392
  has_figures: true
  extraction_method: pandoc-latex   # pandoc-latex | mistral-ocr | authenticated-extract | raw-html
  notes: ""
```
