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
- arXiv PDFs (primary): `curl -sL "https://arxiv.org/pdf/{PAPER_ID}" -o paper.pdf`
- arXiv LaTeX sources (deprecated in v2): `curl -sL "https://arxiv.org/src/{PAPER_ID}" -o source.tar.gz`
- Never fabricate or guess URLs.

---

## SSH / VM Interaction

The pipeline uses an Azure VM for experiment execution. SSH alias is pre-configured.

```bash
# Run a command on the VM
ssh azure-vm-dissertation "{command}"

# File transfer: local → VM
scp experiments/H{n}/scripts/{file} azure-vm-dissertation:~/experiments/H{n}/scripts/

# File transfer: VM → local
scp azure-vm-dissertation:~/experiments/H{n}/results/{file} experiments/H{n}/results/

# Multi-line script on VM
ssh azure-vm-dissertation << 'REMOTE_EOF'
cd ~/experiments/H{n}
source .venv/bin/activate
python scripts/{name}.py
REMOTE_EOF
```

**Rules:**
- NEVER run commands as root on the VM.
- ALWAYS use `timeout` for long-running commands: `ssh azure-vm-dissertation "timeout 3600 python scripts/{name}.py"`
- ALWAYS copy result files back to local after a run completes.
- ALWAYS use experiment-specific venvs on the VM.
- Check disk/RAM before large operations: `ssh azure-vm-dissertation "df -h ~ && free -h"`
