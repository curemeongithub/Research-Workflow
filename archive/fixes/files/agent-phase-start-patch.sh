# Phase-Start Block — Patch for All Agents
#
# For each agent file listed below, insert the following block IMMEDIATELY
# before the first "## Input" section. Substitute the correct PHASE and
# OUTPUT values per the table.
#
# The python3 call uses encoding='utf-8' to fix the portability gap
# identified in the analysis (bare open() can fail on non-UTF-8 systems).
#
# ┌──────────────────────────────────┬───────┬──────────────────────────────────────┐
# │ Agent file                       │ PHASE │ OUTPUT                               │
# ├──────────────────────────────────┼───────┼──────────────────────────────────────┤
# │ source-acquisition.md            │  1    │ sources/manifest.yaml                │
# │ source-extraction.md             │  2    │ sources/                             │
# │ literature-comprehension.md      │  3    │ analysis/literature-map.md           │
# │ gap-analysis.md                  │  4    │ analysis/gap-analysis.md  ← DONE     │
# │ sanity-check.md                  │  5    │ analysis/review-notes.md             │
# │ hypothesis-formation.md          │  6    │ synthesis/hypotheses.md              │
# │ methodology-design.md            │  7    │ synthesis/methodology.md             │
# │ document-assembly.md             │  8    │ synthesis/final-document.md          │
# │ critique.md                      │  9    │ reiteration/critique.md              │
# └──────────────────────────────────┴───────┴──────────────────────────────────────┘
#
# Block to insert (substitute PHASE_NUMBER and PHASE_OUTPUT):
# ─────────────────────────────────────────────────────────────

: '
## Phase Start — Mark in_progress

Run this **before any reading or analysis**:

```bash
python3 -c "
import yaml, datetime, sys
try:
    with open('"'"'pipeline-state.yaml'"'"', encoding='"'"'utf-8'"'"') as f:
        state = yaml.safe_load(f)
except FileNotFoundError:
    print('"'"'ERROR: pipeline-state.yaml missing.'"'"', file=sys.stderr)
    sys.exit(1)
state.setdefault('"'"'phases'"'"', {})
state['"'"'phases'"'"'][PHASE_NUMBER] = {
    '"'"'status'"'"': '"'"'in_progress'"'"',
    '"'"'output'"'"': '"'"'PHASE_OUTPUT'"'"',
    '"'"'started'"'"': datetime.datetime.utcnow().isoformat() + '"'"'Z'"'"',
}
with open('"'"'pipeline-state.yaml'"'"', '"'"'w'"'"', encoding='"'"'utf-8'"'"') as f:
    yaml.dump(state, f, default_flow_style=False)
print('"'"'[phase-PHASE_NUMBER] Marked in_progress'"'"')
"
```
'

# ─────────────────────────────────────────────────────────────
# ALSO: update the existing "Update pipeline-state.yaml" block
# at the END of each agent to write status='complete' and include
# the 'started' timestamp that was already written. The existing
# python3 snippets only need one addition — change:
#
#     state['phases'][N] = {
#         'status': 'complete',
#         ...
#     }
#
# to:
#
#     existing = state.get('phases', {}).get(N, {})
#     state['phases'][N] = {
#         'status': 'complete',
#         'output': '...',
#         'started': existing.get('started', 'unknown'),
#         'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
#     }
#
# This preserves the start time so diagnostics can compute phase duration.
