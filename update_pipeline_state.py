#!/usr/bin/env python3
"""Update pipeline-state.yaml for Phase 6 completion"""

import yaml
import datetime

with open('pipeline-state.yaml', 'r') as f:
    state = yaml.safe_load(f)

state['phases'][6] = {
    'status': 'complete',
    'output': 'synthesis/hypotheses.md',
    'hypotheses_formulated': 6,
    'tier1_hypotheses': 3,
    'tier2_hypotheses': 3,
    'excluded_gaps': [2.2, 2.5, 3.1, 3.2],
    'source_lookups_used': 0,
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
}

state['current_phase'] = 7

with open('pipeline-state.yaml', 'w') as f:
    yaml.dump(state, f, default_flow_style=False, sort_keys=False)

print("✓ Pipeline state updated: current_phase → 7")
print("✓ Phase 6 metadata recorded:")
print(f"  - 6 hypotheses formulated (3 Tier 1, 3 Tier 2)")
print(f"  - 4 gaps excluded (2.2, 2.5, 3.1, 3.2)")
print(f"  - Output: synthesis/hypotheses.md")
