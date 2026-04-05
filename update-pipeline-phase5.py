#!/usr/bin/env python3
import yaml
import datetime

with open('pipeline-state.yaml') as f:
    state = yaml.safe_load(f)

state['phases'][5] = {
    'status': 'complete',
    'output': 'analysis/review-notes.md',
    'advisory': True,
    'source_lookups_used': 1,
    'key_findings': 'Tier 1 gaps verified; tier scoring inconsistency noted; GNNs/equivariant missing',
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
}
state['current_phase'] = 6

with open('pipeline-state.yaml', 'w') as f:
    yaml.dump(state, f, default_flow_style=False, sort_keys=False)

print("Pipeline state updated: current_phase = 6")
