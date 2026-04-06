#!/usr/bin/env python3
"""Fetch abstracts from Semantic Scholar for mismatched papers and write/fix content.md."""
import os
import sys
import time
import json
import urllib.request
import yaml

MISMATCHED = {
    'arxiv-2012.13401': '2012.13401',
    'arxiv-2104.02796': '2104.02796',
    'arxiv-2209.01113': '2209.01113',
    'arxiv-2209.01062': '2209.01062',
    'arxiv-2104.01506': '2104.01506',
    'arxiv-1811.10927': '1811.10927',
    'arxiv-2105.09206': '2105.09206',
    'arxiv-2103.01799': '2103.01799',
    'arxiv-1907.11714': '1907.11714',
    'arxiv-1711.07576': '1711.07576',
    'arxiv-0709.1542': '0709.1542',
    'arxiv-2012.12965': '2012.12965',
}

MANIFEST_EXPECTED_TITLES = {
    'arxiv-2012.13401': 'Neural Networks are Convex Regularizers',
    'arxiv-2104.02796': 'Global Optimality via Convex Duality for Deep Neural Networks',
    'arxiv-2209.01113': 'Vector-Output ReLU Neural Network Problems are Copositive Programs',
    'arxiv-2209.01062': 'Regularization and Optimization in Deep Learning via Dual Methods',
    'arxiv-2104.01506': 'Group-Sparse Neural Networks via Convex Duality',
    'arxiv-1811.10927': 'The Loss Surfaces of Multilayer Networks',
    'arxiv-2105.09206': 'Randomized Subspace Newton',
    'arxiv-2103.01799': 'Characterizing Implicit Bias in Terms of Optimization Geometry',
    'arxiv-1907.11714': 'Gradient Descent with Early Stopping',
    'arxiv-1711.07576': 'Bounding the Optimal Value of a Mixed-Integer Neural Network',
    'arxiv-0709.1542': 'Random Features for Large-Scale Kernel Machines',
    'arxiv-2012.12965': 'Banach Space Representer Theorems for Neural Networks',
}

def fetch_ss_abstract(arxiv_id: str) -> dict:
    url = f'https://api.semanticscholar.org/graph/v1/paper/arXiv:{arxiv_id}?fields=title,abstract,year,authors,venue'
    req = urllib.request.Request(url, headers={'User-Agent': 'research-pipeline/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {'error': str(e)}

def mismatch_note(src_id, arxiv_id, ss_data, expected_title):
    actual_title = ss_data.get('title', 'unknown')
    return (
        f"# EXTRACTION NOTE\n\n"
        f"**Phase 1 Acquisition Issue**: The arXiv tarball for `{arxiv_id}` "
        f"contained content from a different paper.\n\n"
        f"- **Expected**: {expected_title}\n"
        f"- **Actual arXiv {arxiv_id}**: {actual_title}\n\n"
        f"This source needs to be re-acquired. Content below is from the wrong paper's LaTeX source.\n\n"
        f"---\n\n"
    )

results = []

for src_id, arxiv_id in MISMATCHED.items():
    dest = f'sources/arxiv-{arxiv_id}'
    content_file = f'{dest}/content.md'
    expected_title = MANIFEST_EXPECTED_TITLES.get(src_id, '')
    
    print(f'Processing {src_id} ...')
    ss = fetch_ss_abstract(arxiv_id)
    time.sleep(0.5)
    
    actual_title = ss.get('title', '')
    abstract = ss.get('abstract', '')
    
    # Check if this is indeed a mismatch
    is_mismatch = expected_title.lower()[:20] not in actual_title.lower()
    
    if is_mismatch:
        # Prepend a mismatch warning to existing content
        if os.path.isfile(content_file):
            with open(content_file, encoding='utf-8', errors='replace') as f:
                existing = f.read()
        else:
            existing = ''
        
        note = mismatch_note(src_id, arxiv_id, ss, expected_title)
        # Only prepend if not already noting the mismatch
        if 'EXTRACTION NOTE' not in existing[:200]:
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(note + existing)
        
        print(f'  MISMATCH: actual="{actual_title[:60]}"')
        results.append({'id': src_id, 'status': 'mismatch', 'actual': actual_title})
    else:
        print(f'  OK: "{actual_title[:60]}"')
        results.append({'id': src_id, 'status': 'ok', 'actual': actual_title})

print('\n=== Summary ===')
for r in results:
    print(f"  [{r['status']:8}] {r['id']}: {r['actual'][:55]}")
