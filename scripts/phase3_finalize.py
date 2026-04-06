#!/usr/bin/env python3
"""Phase 3 finalization script — updates pipeline-state.yaml and commits.

Run from project root:
    .venv/bin/python scripts/phase3_finalize.py
"""
import yaml
import datetime
import subprocess
import os

PROJECT_ROOT = os.environ.get("CLAUDE_PROJECT_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE_FILE = os.path.join(PROJECT_ROOT, "pipeline-state.yaml")

with open(STATE_FILE, encoding="utf-8") as f:
    state = yaml.safe_load(f)

existing = state.get("phases", {}).get(3, {})
state.setdefault("phases", {})[3] = {
    "status": "complete",
    "output": "analysis/literature-map.md",
    "started": existing.get("started", "2026-04-06T00:00:00Z"),
    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    "sources_used": {
        "valid": [
            "user-2002.10553v2",
            "user-2110.05518v2",
            "user-2110.06482v3",
            "user-2402.03625v3",
            "user-ergen21b",
            "user-8652_CRONOS_Enhancing_Deep_Lea",
            "arxiv-2110.05518",
            "arxiv-2110.06482",
            "arxiv-2402.03625",
            "arxiv-2002.10553",
        ],
        "mismatch_skipped": [
            "arxiv-2012.13401", "arxiv-2012.13635", "arxiv-2106.05528",
            "arxiv-2104.02796", "arxiv-2209.01113", "arxiv-2307.01197",
            "arxiv-2209.01062", "arxiv-2104.14641", "arxiv-2105.09206",
            "arxiv-2104.01506", "arxiv-2204.09875", "arxiv-2011.02083",
        ],
    }
}
state["current_phase"] = 4

with open(STATE_FILE, "w", encoding="utf-8") as f:
    yaml.dump(state, f, default_flow_style=False, allow_unicode=True)

print("[phase-3] pipeline-state.yaml updated: current_phase=4, phase 3 status=complete")

# Git commit
result = subprocess.run(
    ["git", "-C", PROJECT_ROOT, "add", "analysis/", "pipeline-state.yaml"],
    capture_output=True, text=True
)
print("git add:", result.stdout, result.stderr)

result = subprocess.run(
    ["git", "-C", PROJECT_ROOT, "commit", "-m", "phase-3-complete: literature map written"],
    capture_output=True, text=True
)
print("git commit:", result.stdout, result.stderr)
