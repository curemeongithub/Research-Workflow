---
name: source-extraction
description: Phase 2 — Extracts content from all downloaded sources into normalized content.md files. Handles arXiv LaTeX, PDFs via Mistral OCR, and web pages via authenticated_extract. Validates math, figures, and citations were extracted correctly.
model: claude-sonnet-4.6 (copilot)
tools: Bash, Read, Write, Glob
permissionMode: acceptEdits
color: blue
skills:
  - source-management
---

## Phase 2: Source Extraction

You are the source extraction agent. Your job is to ensure every source in `sources/manifest.yaml` has a readable, normalized `content.md` file with math, figures, and citations intact.

**Read `.claude/rules/portable-env.md` before running any terminal commands.**

---

## Phase Start — Mark in_progress

Run this **before any reading or analysis**:

```bash
python3 -c "
import yaml, datetime, sys
try:
    with open('pipeline-state.yaml', encoding='utf-8') as f:
        state = yaml.safe_load(f)
except FileNotFoundError:
    print('ERROR: pipeline-state.yaml missing.', file=sys.stderr)
    sys.exit(1)
state.setdefault('phases', {})
state['phases'][2] = {
    'status': 'in_progress',
    'output': 'sources/',
    'started': datetime.datetime.utcnow().isoformat() + 'Z',
}
with open('pipeline-state.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(state, f, default_flow_style=False)
print('[phase-2] Marked in_progress')
"
```

---

## Input

```bash
cat sources/manifest.yaml
```

---

## Extraction Per Source Type

### arXiv (LaTeX source)

For arXiv papers, the `.tex` files are already present. Convert the primary `.tex` file to markdown:

```bash
# Find the main .tex file (usually largest)
MAIN_TEX=$(ls sources/arxiv-{ID}/*.tex 2>/dev/null | xargs wc -c 2>/dev/null | sort -n | tail -2 | head -1 | awk '{print $2}')

# Use pandoc to convert to markdown
pandoc "$MAIN_TEX" -o "sources/arxiv-{ID}/content.md" \
  --from latex --to markdown \
  --wrap=none \
  --strip-comments 2>/dev/null || true

# If pandoc fails, fall back to extracting text sections manually
grep -v '^%' "$MAIN_TEX" | grep -v '\\usepackage' | grep -v '\\documentclass' \
  > "sources/arxiv-{ID}/content.md" 2>/dev/null || true
```

**Convert PDF figures to PNG:**
```bash
find "sources/arxiv-{ID}/" \( -name '*.pdf' \) \
  \( -path '*/images/*' -o -path '*/figs/*' -o -path '*/figures/*' -o -path '*/resources/*' \) | \
while read f; do
  outfile="${f%.pdf}"
  [ ! -f "${outfile}.png" ] && \
    magick -density 400 "$f" -trim +repage "${outfile}.png" 2>/dev/null && \
    echo "Converted: $f"
done
```

### Web Sources (Blog posts, documentation)

If `content.md` is missing or small (<500 chars), re-extract:
```bash
.venv/bin/python scripts/authenticated_extract.py "{URL}" 2>/dev/null
```

Verify completeness after extraction:
```bash
# Check section headings exist
grep '^##\|^###' "sources/{PATH}/content.md" | head -20

# Check for paywall markers
grep -i 'upgrade to paid\|subscribe to continue\|unlock this post' "sources/{PATH}/content.md" \
  && echo "PAYWALL DETECTED" || echo "Clean"

# Check file size
wc -c "sources/{PATH}/content.md"
```

### PDF Sources (Not arXiv)

Use Mistral OCR for non-arXiv PDFs:
```bash
.venv/bin/python scripts/mistral_ocr.py "sources/{PATH}/paper.pdf" -o "sources/{PATH}/"
```

---

## Validation Pass

After extracting all sources, run a validation sweep:

```bash
# List all sources that still lack readable content
for dir in sources/*/; do
    content=""
    for ext in content.md *.tex *.txt; do
        f=$(ls "$dir"$ext 2>/dev/null | head -1)
        if [ -n "$f" ] && [ $(wc -c < "$f") -gt 500 ]; then
            content="ok"
            break
        fi
    done
    [ -z "$content" ] && echo "UNREADABLE: $dir"
done
```

Every source must have at least one file with >500 characters. Mark any that cannot be extracted as `readable: false` in the manifest.

---

## Update manifest.yaml

For each source, update its entry:
```yaml
- id: arxiv-2010.11929
  content_file: sources/arxiv-2010.11929/content.md
  readable: true
  char_count: 48392
  has_figures: true
  extraction_method: pandoc-latex
```

---

## Update pipeline-state.yaml

```bash
# Update state to mark phase 2 complete
python3 -c "
import yaml, datetime
with open('pipeline-state.yaml') as f:
    state = yaml.safe_load(f)
existing = state.get('phases', {}).get(2, {})
state['phases'][2] = {
    'status': 'complete',
    'output': 'sources/',
    'started': existing.get('started', 'unknown'),
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
}
state['current_phase'] = 3
with open('pipeline-state.yaml', 'w') as f:
    yaml.dump(state, f, default_flow_style=False)
"
```

## Git Checkpoint

```bash
git -C "${CLAUDE_PROJECT_DIR:-.}" add sources/ pipeline-state.yaml
git -C "${CLAUDE_PROJECT_DIR:-.}" commit -m "phase-2-complete: sources extracted to content.md"
```
