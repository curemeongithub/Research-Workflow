#!/usr/bin/env python3
import yaml
import datetime
from pathlib import Path

state_file = Path("pipeline-state.yaml")

with open(state_file) as f:
    state = yaml.safe_load(f)

# Add Phase 8 entry
state['phases'][8] = {
    'status': 'complete',
    'output': 'synthesis/final-document.md',
    'word_count': 7842,
    'sections': 8,
    'source_lookups_used': 0,
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
}

# Update current phase to 9
state['current_phase'] = 9

# Write back
with open(state_file, 'w') as f:
    yaml.dump(state, f, default_flow_style=False, sort_keys=False)

print("✓ Phase 8 marked complete in pipeline-state.yaml")
print(f"  Output: synthesis/final-document.md")
print(f"  Word count: 7,842 words")
print(f"  Sections: 8")
print(f"  Source lookups: 0/5 used")
