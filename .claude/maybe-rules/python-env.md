# Python Environment

This project uses a **uv virtual environment** located at `.venv/` in the repo root.

## Terminal Commands

**PREFERRED: Use the full path to the Python executable.** This works reliably in all contexts (interactive shells, IDE subprocesses, subagents, non-interactive scripts):

```bash
/Users/abhinavmallick/Github.nosync/Research-Workflow/.venv/bin/python script.py
```

**For scripts in the repo root, use a relative path:**

```bash
.venv/bin/python script.py
```

**WHY:** IDE-spawned subshells (Claude Code, Claude Code, Claude Code subagents) often don't source shell profiles, so virtual environment activation via `source .venv/bin/activate` may not persist. The full path approach bypasses this entirely.

## Rules

- **ALWAYS** use `.venv/bin/python` (relative) or the full absolute path when running Python in terminal commands, especially in workflows and subagents.
- For `pip` and `uv pip`, use: `.venv/bin/pip` or `.venv/bin/uv pip`.
- **NEVER** use bare `python` or `pip` without the venv path.
- **NEVER** use the system Python.
- **ALWAYS** double-quote file paths in `rm` commands to prevent word-splitting on spaces, e.g. `rm -rf "/path/to/folder/"`.