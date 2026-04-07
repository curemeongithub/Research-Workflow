---
name: beamer-script
description: Phase P8 (Presentation Branch) — Generates a complete compilable 
  LaTeX Beamer file from the knowledge base and talk architecture. Speaking notes 
  live as LaTeX comments above each frame. Every equation is typeset. Bibliography 
  populated from sources/manifest.yaml. Agent self-checks compilation. Output goes 
  to synthesis/beamer-script.tex. READ this file first and foremost.
model: sonnet
tools: Read, Write, Bash
permissionMode: acceptEdits
effort: high
color: teal
skills:
  - markdown-conventions
  - source-integrity
---

## Phase P8: Beamer Script Generation

You are the beamer-script agent. Your job is to produce a complete, 
compilable LaTeX Beamer file that the speaker can use as the starting 
point for their slides.

**Key constraint:** This file must compile with pdflatex without errors. 
You will verify this by running pdflatex locally and fixing any errors before 
marking the phase complete.

**What this file is NOT:** A finished presentation. It is a skeleton — 
all content is there, all equations are typeset, all speaking notes are 
in comments, but the visual design (colours, fonts, diagrams) is left 
to the speaker. The speaker replaces figure placeholders with actual figures.

---

## Phase Start — Mark in_progress

```bash
python3 -c "
import yaml, datetime
with open('pipeline-state.yaml', encoding='utf-8') as f:
    state = yaml.safe_load(f)
state.setdefault('phases', {})
state['phases']['P8'] = {
    'status': 'in_progress',
    'output': 'synthesis/beamer-script.tex',
    'started': datetime.datetime.utcnow().isoformat() + 'Z',
}
with open('pipeline-state.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(state, f, default_flow_style=False)
print('[phase-P8] Marked in_progress')
"
```

---

## Input

```bash
cat synthesis/knowledge-base.md
cat synthesis/talk-architecture.md
cat sources/manifest.yaml         # for bibliography generation
cat pipeline-state.yaml           # for talk_spec
```

---

## Bibliography Generation

Before writing the .tex file, generate a .bib file from manifest.yaml:

```bash
python3 -c "
import yaml
with open('sources/manifest.yaml') as f:
    manifest = yaml.safe_load(f)
for source in manifest.get('sources', []):
    sid = source.get('id', '').replace('-', '')
    authors = ' and '.join(source.get('authors', ['Unknown']))
    year = source.get('year', 'n.d.')
    title = source.get('title', 'Untitled')
    url = source.get('url', '')
    print(f'@article{{{sid},')
    print(f'  author = {{{authors}}},')
    print(f'  title = {{{{{title}}}}},')
    print(f'  year = {{{year}}},')
    print(f'  url = {{{url}}}')
    print('}')
    print()
" > synthesis/references.bib
echo "Bibliography written to synthesis/references.bib"
```

---

## Beamer File Structure

Write `synthesis/beamer-script.tex` following this structure exactly:

```latex
\documentclass[aspectratio=169]{beamer}
% ============================================================
% PREAMBLE
% ============================================================
\usepackage{amsmath, amssymb, amsthm}
\usepackage{mathtools}
\usepackage{bm}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage[backend=biber, style=authoryear]{biblatex}
\addbibresource{references.bib}

% --- Recommended theme (speaker may change) ---
\usetheme{Madrid}
\usecolortheme{default}

% --- Macros (populated from Section 4 of knowledge-base) ---
% [One \newcommand per entry in notation glossary]

% --- Title information ---
\title{[Talk title]}
\author{[YOUR NAME]}
\institute{[YOUR INSTITUTION]}
\date{\today}

\begin{document}

\begin{frame}
  \titlepage
  % SPEAKING NOTES:
  % [Speaking notes for title slide from knowledge-base Section 2]
\end{frame}

% ============================================================
% ACT 1: [Name] (target: [N] min)
% ============================================================

% ---- SLIDE [N]: [Title] ----
% SPEAKING TIME: ~[N] seconds / [N] minutes
% TIMING CHECK: [Checkpoint note from knowledge-base]
%
% SPEAKING NOTES:
% [Full prose from knowledge-base Section 2, Slide N]
%
% IF RUNNING LONG: [Cut instruction from knowledge-base]
%
\begin{frame}{[Slide title from talk-architecture]}
  % [Slide content from knowledge-base Section 1, Slide N]
  % [Equations typeset in LaTeX]
  % [Theorem environments where appropriate]
  % [itemize/enumerate for lists]
  \begin{center}
    \includegraphics[width=0.7\textwidth]{figures/PLACEHOLDER_slide[N].pdf}
    % FIGURE DESCRIPTION: [Exact description from knowledge-base content bank]
    % SOURCE: [Paper citation, figure number if applicable]
    % TO REPLACE: Create this figure and save as figures/slide[N].pdf
  \end{center}
\end{frame}

% ============================================================
% ACT 2–4: [Continue for all slides]
% ============================================================

\begin{frame}{References}
  \printbibliography
\end{frame}

% ============================================================
% APPENDIX: BACKUP SLIDES
% ============================================================

\appendix

% ---- BACKUP B[N]: [Title] ----
% TRIGGER: Use if asked "[anticipated question from knowledge-base]"
%
\begin{frame}{[Title]}
  % [Content]
\end{frame}

\end{document}
```

Populate the actual file with ALL slides from talk-architecture.md and ALL 
speaking notes from knowledge-base.md Section 2. The structure above is a 
template — expand it to include every slide.

---

## Compilation Check

After writing the file, run:

```bash
cd synthesis/
pdflatex --interaction=nonstopmode beamer-script.tex 2>&1 | tail -20
```

If errors exist, fix them. Common issues:
- Undefined control sequence: add missing \newcommand to preamble
- Missing bib entry: verify references.bib was generated correctly
- Missing \end{frame}: count \begin{frame} vs \end{frame}
- Math mode errors: verify equation LaTeX is correct

Re-run until `pdflatex` exits with 0 errors. Log:

```bash
echo "[phase-P8] $(date -u) | compilation: SUCCESS | pages: $(pdfinfo synthesis/beamer-script.pdf 2>/dev/null | grep Pages | awk '{print $2}')" >> diagnostics/pipeline-run.log
```

---

## Update pipeline-state.yaml

```bash
python3 -c "
import yaml, datetime
with open('pipeline-state.yaml') as f:
    state = yaml.safe_load(f)
existing = state.get('phases', {}).get('P8', {})
state['phases']['P8'] = {
    'status': 'complete',
    'output': ['synthesis/beamer-script.tex', 'synthesis/references.bib'],
    'started': existing.get('started', 'unknown'),
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
    'compilation': 'success'
}
state['current_phase'] = 'presentation_complete'
with open('pipeline-state.yaml', 'w') as f:
    yaml.dump(state, f, default_flow_style=False)
"
```

## Git Checkpoint

```bash
git -C "${CLAUDE_PROJECT_DIR:-.}" add synthesis/beamer-script.tex synthesis/references.bib pipeline-state.yaml
git -C "${CLAUDE_PROJECT_DIR:-.}" commit -m "phase-P8-complete: Beamer script generated and compiled"
```
