#!/usr/bin/env python3
import yaml
import datetime

with open('pipeline-state.yaml') as f:
    state = yaml.safe_load(f)

state['phases'][3] = {
    'status': 'complete',
    'output': 'analysis/literature-map.md',
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
    'sources_read': 11,
    'sources_surveyed': 16,
    'total_sources': 27,
    'word_count': 5200
}
state['current_phase'] = 4

with open('pipeline-state.yaml', 'w') as f:
    yaml.dump(state, f, default_flow_style=False, sort_keys=False)

print("✓ Pipeline state updated: Phase 3 complete, advanced to Phase 4")
