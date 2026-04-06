opus# AI Research Workflow

An agentic research workflow for generating high-quality, structured markdown content from complex technical papers and webpages using Claude Code.

## How It Works

This project uses **agentic LLM prompts** to orchestrate deep research workflows. Instead of producing an entire document in one shot, the workflow divides the task into:
1. Source extraction and parsing.
2. Section-by-section research via Claude Code sub-process/agentss.
3. Rigorous verification and markdown generation.

**Recommended model:** Claude 3.5 Sonnet / Claude Opus — for generating high-fidelity markdown and architecture diagrams.

## Project Structure

```
AI-Research-Workflow/
├── .cursor/commands/            # Claude Code agent prompts
├── .claude/agents/            # Claude Code agent prompts
├── scripts/                     # Source extraction tools
│   ├── authenticated_extract.py # Login-gated / JS-heavy pages → MD + images
│   ├── setup_browser_profile.py # One-time login to create browser profiles
│   ├── webpage_to_md.py         # Static pages → MD + images
│   ├── mistral_ocr.py           # PDF → MD + images (via Mistral API)
│   └── .browser-profiles/       # Saved browser sessions (gitignored)
├── sources/                     # Downloaded sources (gitignored)
├── Topic-1/                     # Each topic is a folder with .md documents
├── Topic-2/
└── ...
```

---

## Setup

### Python Environment (conda + uv)

Create the project's conda environment and install all dependencies.
These commands are idempotent — safe to re-run.

```bash
# Create conda env (skips if already exists)
conda create -n ai-learning-gems python=3.13 --yes 2>/dev/null || true
conda activate ai-learning-gems

# Install uv for fast pip installs (skips if already installed)
pip install uv 2>/dev/null || true

# Install all Python dependencies
cd /path/to/AI-Research-Workflow
uv pip install -r requirements.txt
```

### Crawl4AI Browser Setup (for authenticated web extraction)

After installing requirements, set up Playwright browsers for the web extraction tool:

```bash
conda activate ai-learning-gems
crawl4ai-setup    # Downloads Chromium (~90MB, one-time)
```

Then create browser profiles for login-gated sites (one-time per site):

```bash
cd /path/to/AI-Research-Workflow
```

Profiles are saved to `scripts/.browser-profiles/` (gitignored — they contain session cookies).
Re-run if sessions expire or you get empty output.

---

## Source Extraction Tools

The `scripts/` folder contains tools for downloading web sources as clean Markdown with local images. See `.claude/rules/web-source-fetching.md` for the full decision tree.

### Authenticated / JS-Heavy Pages → Markdown + Images

Uses [Crawl4AI](https://crawl4ai.com/) with persistent browser profiles.

# Custom CSS selector for unknown sites
python scripts/authenticated_extract.py "https://example.com/page" -s "article"

# Skip images
python scripts/authenticated_extract.py "https://example.com/page" --no-images
```

### Static Web Pages (public, no JS needed)

```bash
python scripts/webpage_to_md.py "https://d2l.ai/chapter_.../section.html" -o sources/d2l.ai/chapter_.../
```

### PDF → Markdown (via Mistral OCR)

Requires `MISTRAL_API_KEY` in `.env`.

```bash
python scripts/mistral_ocr.py document.pdf -o sources/output/
```

### ArXiv Papers (LaTeX source preferred)

```bash
mkdir -p sources/arxiv-2010.11929 && cd sources/arxiv-2010.11929
curl -sL "https://arxiv.org/src/2010.11929" -o source.tar.gz && tar -xzf source.tar.gz
```

