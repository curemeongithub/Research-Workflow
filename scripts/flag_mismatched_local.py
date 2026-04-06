#!/usr/bin/env python3
"""Flag known mismatched arXiv sources based on content verification."""
import os
import yaml

# Papers confirmed to have wrong content based on content inspection
CONFIRMED_MISMATCHED = {
    'arxiv-2012.13401': {
        'expected': 'Neural Networks are Convex Regularizers (Pilanci & Ergen 2020)',
        'actual': 'Matter representations from geometry: under the spell of Dynkin (F-theory/physics)',
    },
    'arxiv-2104.02796': {
        'expected': 'Global Optimality via Convex Duality for Deep Neural Networks (Sahiner et al 2021)',
        'actual': 'Nanoscale oscillator / molecular dynamics (carbon nanotube physics)',
    },
    'arxiv-2209.01113': {
        'expected': 'Vector-Output ReLU Neural Network Problems are Copositive Programs (Chen & Pilanci 2022)',
        'actual': 'Hubble tension / f(T) gravity cosmology paper',
    },
    'arxiv-2104.01506': {
        'expected': 'Group-Sparse Neural Networks via Convex Duality (Ergen & Pilanci 2021)',
        'actual': 'Unknown wrong paper (0 ML keywords)',
    },
    'arxiv-1811.10927': {
        'expected': 'The Loss Surfaces of Multilayer Networks (Dauphin et al 2019)',
        'actual': 'Unknown wrong paper (0 ML keywords)',
    },
    'arxiv-2105.09206': {
        'expected': 'Randomized Subspace Newton (Gower et al 2021)',
        'actual': 'Unknown wrong paper (0 ML keywords)',
    },
    'arxiv-2103.01799': {
        'expected': 'Characterizing Implicit Bias in Terms of Optimization Geometry (Woodworth et al 2021)',
        'actual': 'Unknown wrong paper (0 ML keywords)',
    },
    'arxiv-1907.11714': {
        'expected': 'Gradient Descent with Early Stopping is Provably Robust to Label Noise (Li et al 2020)',
        'actual': 'Modular symmetry A4 (particle physics)',
    },
    'arxiv-1711.07576': {
        'expected': 'Bounding the Optimal Value of a Mixed-Integer Neural Network (Anderson et al 2020)',
        'actual': 'Nuclear Magnetic Resonance (NMR) paper',
    },
    'arxiv-0709.1542': {
        'expected': 'Random Features for Large-Scale Kernel Machines (Rahimi & Recht 2007)',
        'actual': 'Josephson effect / BEC quantum physics paper',
    },
    'arxiv-2012.12965': {
        'expected': 'Banach Space Representer Theorems for Neural Networks and Ridge Splines (Parhi & Nowak 2021)',
        'actual': 'DGP baryogenesis / cosmology ("DGP__baryo.tex")',
    },
    'arxiv-2012.09769': {
        'expected': 'Sparse Neural Network Training via Convex Polytope Projections (Ergen & Pilanci 2020)',
        'actual': 'BPS states / exponential networks (string theory/math physics)',
    },
    # Possible mismatch - only 1 ML keyword match:
    'arxiv-2209.01062': {
        'expected': 'Regularization and Optimization in Deep Learning via Dual Methods (Mishkin & Pilanci 2022)',
        'actual': 'Possible mismatch (1 ML keyword, needs verification)',
    },
    'arxiv-2104.01506': {
        'expected': 'Group-Sparse Neural Networks via Convex Duality — Deep Architectures (Ergen & Pilanci 2021)',
        'actual': 'Unknown wrong paper (1 ML keyword)',
    },
}

def flag_content(content_file: str, src_id: str, info: dict) -> None:
    """Prepend a mismatch notice to content.md."""
    if not os.path.isfile(content_file):
        return

    with open(content_file, encoding='utf-8', errors='replace') as f:
        existing = f.read()

    if '<!-- PHASE2_MISMATCH -->' in existing:
        return  # Already flagged

    note = (
        f"<!-- PHASE2_MISMATCH -->\n"
        f"> **⚠️ PHASE 1 ACQUISITION MISMATCH — DO NOT USE FOR CITATIONS**\n"
        f">\n"
        f"> Source ID: `{src_id}`\n"
        f"> Expected paper: {info['expected']}\n"
        f"> Actual content: {info['actual']}\n"
        f"> \n"
        f"> This arXiv tarball contained content from a *different* paper. "
        f"Phase 3+ must **skip** or **disregard** this source unless re-acquired.\n\n"
        f"---\n\n"
    )
    with open(content_file, 'w', encoding='utf-8') as f:
        f.write(note + existing)
    print(f'  Flagged: {content_file}')


def update_manifest_quality(manifest_path: str, mismatched_ids: set) -> None:
    """Update manifest to flag mismatched sources."""
    with open(manifest_path, encoding='utf-8') as f:
        manifest = yaml.safe_load(f)

    for s in manifest['sources']:
        if s['id'] in mismatched_ids:
            s['content_quality'] = 'mismatched'
            s['phase1_note'] = 'Wrong arXiv tarball downloaded in Phase 1'
        else:
            s['content_quality'] = 'ok'

    with open(manifest_path, 'w', encoding='utf-8') as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f'Manifest updated: {len(mismatched_ids)} sources flagged as mismatched')


if __name__ == '__main__':
    print('Flagging mismatched sources ...')
    for src_id, info in CONFIRMED_MISMATCHED.items():
        arxiv_id = src_id.replace('arxiv-', '')
        content_file = f'sources/arxiv-{arxiv_id}/content.md'
        flag_content(content_file, src_id, info)
        print(f'  {src_id}: {info["actual"][:60]}')

    update_manifest_quality('sources/manifest.yaml', set(CONFIRMED_MISMATCHED.keys()))
    print('\nDone.')
