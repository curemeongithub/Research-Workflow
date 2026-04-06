#!/usr/bin/env python3
"""Check content quality for arXiv sources."""
import os
import yaml

keywords = [
    'neural', 'convex', 'relu', 'network', 'optimization', 'dual', 'regulariz',
    'kernel', 'gradient', 'sparse', 'deep learning', 'overparameter', 'semidefinite',
    'random features', 'banach', 'representer', 'tangent'
]

with open('sources/manifest.yaml', encoding='utf-8') as f:
    manifest = yaml.safe_load(f)

results_ok = []
results_mismatch = []
results_empty = []

for s in manifest['sources']:
    if s['type'] != 'arxiv':
        continue
    cf = s.get('content_file', '')
    if not os.path.isfile(cf):
        cf = f"{s['local_path']}/content.md"
    if not os.path.isfile(cf):
        results_empty.append(s['id'])
        continue
    with open(cf, encoding='utf-8', errors='replace') as f:
        text = f.read(3000).lower()
    hits = sum(1 for kw in keywords if kw in text)
    if hits >= 2:
        results_ok.append((s['id'], hits, s['title'][:60]))
    else:
        results_mismatch.append((s['id'], hits, s['title'][:60]))

print(f"ON-TOPIC ({len(results_ok)}/{len(results_ok) + len(results_mismatch)}):")
for id_, hits, title in results_ok:
    print(f"  [{hits}kw] {id_}: {title}")
print()
print(f"MISMATCHED ({len(results_mismatch)}/{len(results_ok) + len(results_mismatch)}):")
for id_, hits, title in results_mismatch:
    print(f"  [{hits}kw] {id_}: {title}")
