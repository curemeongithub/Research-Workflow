# Portable Environment Rules

Rules for running scripts and commands consistently across Claude Code and VS Code Copilot.

---

## Python

**Always use the project `.venv`.** Never use bare `python`, `pip`, or the system Python.

```bash
# Preferred — relative path (works in all contexts)
.venv/bin/python script.py
.venv/bin/pip install package

# Full absolute path (guaranteed to work in non-interactive shells)
$CLAUDE_PROJECT_DIR/.venv/bin/python script.py
```

**Why:** IDE-spawned subshells do not source shell profiles. `source .venv/bin/activate` does not persist across subagent boundaries. The full path approach is the only reliable method.

---

## Bash / Shell

- All scripts use POSIX bash (`#!/usr/bin/env bash`).
- Use `$CLAUDE_PROJECT_DIR` for absolute references to the repo root when needed.
- Quote all file path variables: `"$CLAUDE_PROJECT_DIR/sources/"` (never `$CLAUDE_PROJECT_DIR/sources/`).
- Use `set -euo pipefail` in all bash scripts.
- Temporary files go in `$TMPDIR`, never `/tmp`.

---

## Directory References in Agents

When an agent needs to reference the project root:

```bash
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"
```

This falls back to `.` (current directory) if the env var is not set, which handles VS Code Copilot contexts where `CLAUDE_PROJECT_DIR` may be unset.

---

## File Path Quoting

Always double-quote paths that may contain spaces:

```bash
rm -rf "$PROJECT_ROOT/sources/old-source/"   # GOOD
rm -rf $PROJECT_ROOT/sources/old-source/     # BAD — breaks on spaces
```

---

## Git Commands

```bash
git -C "$PROJECT_ROOT" add .
git -C "$PROJECT_ROOT" commit -m "phase-N-complete: description"
```

Using `-C` ensures git runs in the correct directory regardless of the subagent's working directory.

---

## Network Access

- All `curl` commands should use `-sL` (silent + follow redirects).
- arXiv LaTeX sources: `curl -sL "https://arxiv.org/src/{PAPER_ID}" -o source.tar.gz`
- Never fabricate or guess URLs.
