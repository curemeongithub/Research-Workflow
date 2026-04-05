## Resume from Checkpoint

If a run was interrupted, check `pipeline-state.yaml` and resume from the correct point:

```bash
cat pipeline-state.yaml
```

### Resume Rules

The `current_phase` field tells you the phase that was running when the session ended.
The phase's `status` field tells you whether it finished.

| `status` of `current_phase` | Action |
|-----------------------------|--------|
| `complete` | That phase finished. Spawn the **next** phase (`current_phase + 1`). |
| `in_progress` | That phase was interrupted mid-run. **Re-run it from scratch** — its output may be partial or absent. Do NOT increment `current_phase`. |
| absent (key missing) | Phase was never started. Spawn it. |

**Never skip a phase whose status is `in_progress`.** A crash after `in_progress` was written but before `complete` was written means the output file is unreliable. Re-running is always safe because agents write to fixed output paths and each run ends with a git commit.

### Resume Script

```bash
python3 -c "
import yaml, sys

with open('pipeline-state.yaml', encoding='utf-8') as f:
    state = yaml.safe_load(f)

current = state.get('current_phase', 1)
phases  = state.get('phases', {})
phase_state = phases.get(current, {})
status = phase_state.get('status', 'absent')

if status == 'complete':
    resume_at = current + 1
    print(f'Phase {current} is complete. Resume at phase {resume_at}.')
elif status == 'in_progress':
    resume_at = current
    print(f'Phase {current} was interrupted (in_progress). Re-running phase {resume_at}.')
else:
    resume_at = current
    print(f'Phase {current} was never started. Starting phase {resume_at}.')

print(f'RESUME_AT={resume_at}')
" 2>&1
```

Use the `RESUME_AT` value to determine which subagent to spawn next. Do NOT re-run phases with `status: complete`.
