# ─────────────────────────────────────────────────────────────
# PHASE START — Mark this phase as in_progress IMMEDIATELY.
# This must be the first bash block an agent runs, before any
# reading or analysis, so that a crash mid-phase is detectable
# on resume (status remains "in_progress" rather than absent).
# ─────────────────────────────────────────────────────────────
# Replace PHASE_NUMBER with the integer for this phase (1–9).
# Replace PHASE_OUTPUT with the primary output path for this phase.

PHASE_NUMBER=N
PHASE_OUTPUT="path/to/output"

python3 -c "
import yaml, datetime, sys
phase = int('$PHASE_NUMBER')
output = '$PHASE_OUTPUT'
try:
    with open('pipeline-state.yaml', encoding='utf-8') as f:
        state = yaml.safe_load(f)
except FileNotFoundError:
    print('ERROR: pipeline-state.yaml not found. Orchestrator must create it before spawning agents.', file=sys.stderr)
    sys.exit(1)
state.setdefault('phases', {})
state['phases'][phase] = {
    'status': 'in_progress',
    'output': output,
    'started': datetime.datetime.utcnow().isoformat() + 'Z',
}
with open('pipeline-state.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(state, f, default_flow_style=False)
print(f'[phase-{phase}] Marked in_progress in pipeline-state.yaml')
"
