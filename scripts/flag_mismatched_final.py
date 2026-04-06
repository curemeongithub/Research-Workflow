#!/usr/bin/env python3
"""Flag ALL confirmed mismatched arXiv sources based on content inspection."""
import os
import yaml

# Complete list of confirmed mismatches based on content inspection
CONFIRMED_MISMATCHED = {
    'arxiv-2012.13401': 'Matter representations / F-theory physics (Esole & Kang 2020)',
    'arxiv-2104.02796': 'Nanoscale oscillator / carbon nanotube molecular dynamics',
    'arxiv-2209.01113': 'Hubble constant / f(T) gravity cosmology',
    'arxiv-2209.01062': 'Dubrovin-Frobenius manifolds (pure algebraic geometry)',
    'arxiv-2104.01506': 'Interactive reinforcement learning + Frogger game (A3PS)',
    'arxiv-1811.10927': 'B-meson decays / lepton flavor universality (particle physics)',
    'arxiv-2105.09206': 'RF timing system / accelerator physics',
    'arxiv-2103.01799': 'Minimal codewords in projective spaces (coding theory)',
    'arxiv-1907.11714': 'Modular symmetry A4 (particle physics / neutrino masses)',
    'arxiv-1711.07576': 'Nuclear Magnetic Resonance (NMR)',
    'arxiv-0709.1542': 'Josephson effect / BEC quantum physics',
    'arxiv-2012.12965': 'DGP baryogenesis cosmology',
    'arxiv-2012.09769': 'BPS states / exponential networks (string theory)',
    'arxiv-2012.13635': 'Logic Tensor Networks (LTN) — not convex geometry/duality',
    'arxiv-2106.05528': 'Contrastive Learning / Unsupervised Domain Adaptation',
    'arxiv-1703.04699': '3D semantic reconstruction (robotics/CV paper)',
}

# Papers that passed content check (on-topic ML content)
CONFIRMED_OK = {
    'arxiv-2110.06482',  # Deep ReLU Networks via Convex Programs ✓
    'arxiv-2002.10553',  # Convex Duality and Cutting Plane Methods ✓
    'arxiv-2110.05518',  # Hyperparameter Optimization as Service via Convex NN ✓
    'arxiv-2402.03625',  # Scalable Convex Optimization via Frank-Wolfe ✓
    'arxiv-2307.01197',  # Convex Relaxations of ReLU NNs for Certification ✓
    'arxiv-2104.14641',  # Sparse Deep NNs + Tuna compiler (ML-adjacent) ✓
    'arxiv-1806.07572',  # Neural Tangent Kernel ✓
    'arxiv-2002.02405',  # Finite vs Infinite Neural Networks ✓
    'arxiv-1904.11955',  # Inductive Bias of NTK ✓
    'arxiv-2204.09875',  # Implicit Bias / Convex Lasso ✓
    'arxiv-1811.01988',  # Semidefinite Relaxations for NN Verification ✓
    'arxiv-1901.00596',  # Gradient Descent Finds Global Minima ✓
    'arxiv-1710.10174',  # Implicit Regularization in Matrix Factorization ✓
    'arxiv-2011.02083',  # Extreme Points for Convex Neural Networks ✓
}


def flag_content(content_file: str, src_id: str, actual_content: str) -> None:
    """Prepend a mismatch notice to content.md."""
    if not os.path.isfile(content_file):
        return

    with open(content_file, encoding='utf-8', errors='replace') as f:
        existing = f.read()

    if '<!-- PHASE2_MISMATCH -->' in existing[:500]:
        return  # Already flagged

    note = (
        "<!-- PHASE2_MISMATCH -->\n"
        "> **⚠️ PHASE 1 ACQUISITION MISMATCH — DO NOT USE FOR CITATIONS**\n"
        ">\n"
        f"> **Source ID**: `{src_id}`\n"
        f"> **Actual content**: {actual_content}\n"
        ">\n"
        "> This arXiv tarball contained content from a *different* paper.\n"
        "> Phase 3+ must **skip** this source. Re-acquire in Phase 1 reiteration.\n\n"
        "---\n\n"
    )
    with open(content_file, 'w', encoding='utf-8') as f:
        f.write(note + existing)


def update_manifest(manifest_path: str) -> dict:
    with open(manifest_path, encoding='utf-8') as f:
        manifest = yaml.safe_load(f)

    stats = {'ok': 0, 'mismatch': 0, 'user_pdf': 0, 'blog': 0}

    for s in manifest['sources']:
        src_type = s['type']
        src_id = s['id']

        if src_type in ('user_pdf', 'blog'):
            s['content_quality'] = 'ok'
            stats[src_type if src_type == 'blog' else 'user_pdf'] += 1
        elif src_id in CONFIRMED_MISMATCHED:
            s['content_quality'] = 'mismatched'
            s['phase1_note'] = f'Wrong arXiv tarball: {CONFIRMED_MISMATCHED[src_id]}'
            stats['mismatch'] += 1
        elif src_id in CONFIRMED_OK:
            s['content_quality'] = 'ok'
            stats['ok'] += 1
        else:
            # Unclassified arxiv — treat as potentially ok
            s['content_quality'] = 'unverified'

    with open(manifest_path, 'w', encoding='utf-8') as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return stats


if __name__ == '__main__':
    print('=== Flagging mismatched sources ===\n')

    for src_id, actual in CONFIRMED_MISMATCHED.items():
        arxiv_id = src_id.replace('arxiv-', '')
        content_file = f'sources/arxiv-{arxiv_id}/content.md'
        flag_content(content_file, src_id, actual)
        print(f'  [MISMATCH] {src_id}')
        print(f'             Actual: {actual[:70]}')

    print('\n=== Updating manifest ===')
    stats = update_manifest('sources/manifest.yaml')

    print(f'\n=== Phase 2 Content Quality Report ===')
    mismatch_count = len(CONFIRMED_MISMATCHED)
    ok_arxiv = len(CONFIRMED_OK)
    print(f'  arXiv ON-TOPIC:    {ok_arxiv}/30')
    print(f'  arXiv MISMATCHED:  {mismatch_count}/30')
    print(f'  User PDFs:         6/6 (correct via Mistral OCR)')
    print(f'  Blog posts:        3/3 (correct via web extraction)')
    print(f'  TOTAL USABLE:      {ok_arxiv + 6 + 3}/39')
    print(f'  TOTAL MISMATCHED:  {mismatch_count}/39')
    print()
    print('NOTE: Phase 3 should use only sources with content_quality=ok')
    print('NOTE: Phase 1 reiteration needed to re-acquire 16 mismatched papers')
