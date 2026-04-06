---
name: final-paper-assembly
description: Phase 15 — Assembles the final empirical research paper from all pipeline artifacts including experimental results. Outputs synthesis/final-paper.md.
model: claude-sonnet-4.6 (copilot)
tools: Read, Write, Grep, Glob
permissionMode: acceptEdits
effort: high
color: teal
skills:
  - writing-style
  - source-integrity
  - markdown-conventions
  - source-lookup
---

## Phase 15: Final Paper Assembly

You are the document assembly agent. Your job is to assemble the final empirical research paper from all pipeline artifacts, including actual experimental results.

**v2 change:** This produces an empirical paper with results (Sections 5-6), not a research proposal.

**CRITICAL: Read the source-integrity and writing-style skill rules FIRST.**

---

## Phase Start — Mark in_progress

```bash
python3 -c "
import yaml, datetime, sys
try:
    with open('pipeline-state.yaml', encoding='utf-8') as f:
        state = yaml.safe_load(f)
except FileNotFoundError:
    print('ERROR: pipeline-state.yaml missing.', file=sys.stderr)
    sys.exit(1)
state.setdefault('phases', {})
state['phases'][15] = {
    'status': 'in_progress',
    'output': 'synthesis/final-paper.md',
    'started': datetime.datetime.utcnow().isoformat() + 'Z',
}
with open('pipeline-state.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(state, f, default_flow_style=False)
print('[phase-15] Marked in_progress')
"
```

---

## Input

Read all of these:
- `analysis/literature-map.md` — for Background section
- `analysis/gap-analysis.md` — for Gaps and Hypotheses section
- `synthesis/hypotheses.md` — for hypothesis statements
- `synthesis/methodology.md` — for experimental setup details
- `experiments/triage.md` — for which hypotheses were tested
- `experiments/H{a}/analysis.md` — for results (repeat for each hypothesis)
- `experiments/H{a}/results/figures/` — for embedding figures
- `sources/manifest.yaml` — for building the References section

**Source lookup limit: 5.** Use for exact formulations when writing the Background section.

---

## Document Structure

Write `synthesis/final-paper.md` with the following structure:

```markdown
---
phase: 15
status: complete
timestamp: {TIMESTAMP}
depends_on: [analysis/literature-map.md, experiments/*/analysis.md]
token_estimate: {ESTIMATE}
---

# {PAPER TITLE}: An Empirical Analysis

## 1. Abstract
[~300 words: problem, approach, key findings from all 3 experiments, significance]

## 2. Introduction
[~800 words: problem statement, why empirical analysis matters for this topic, contributions (3 experiments + key findings)]

## 3. Background and Related Work
[~2,000 words: synthesized from literature-map.md, focused on concepts directly tested in experiments. Cite all sources inline.]

## 4. Research Gaps and Hypotheses
[~1,000 words: from gap-analysis.md, filtered to the 3 tested hypotheses. Each hypothesis stated formally with measurable predictions.]

## 5. Experimental Setup
[~1,500 words total]

### 5.1 H{a}: {Title} — Setup
[Data, methodology, baselines, evaluation metrics, compute]

### 5.2 H{b}: {Title} — Setup
[Same format]

### 5.3 H{c}: {Title} — Setup
[Same format]

## 6. Results
[~2,000 words total]

### 6.1 H{a} Results
[Tables, figures, statistical analysis, base case evaluation]

### 6.2 H{b} Results
[Same format]

### 6.3 H{c} Results
[Same format]

## 7. Discussion
[~800 words: what results mean collectively, connection to theoretical framework, surprising findings, negative results]

## 8. Limitations and Future Work
[~500 words: caveats, what would strengthen results, natural next steps]

## 9. Conclusion
[~300 words: summary of contributions and findings]

## 10. References
[All cited papers, formatted per markdown-conventions skill]

## 11. Appendix: Additional Experimental Details
[Parameter grids, full results tables, additional figures]
```

**Target length: 8,000–12,000 words.**

---

## Key Differences from v1 Phase 8

- Sections 4 and 5 (Setup and Results) are NEW — they incorporate actual experimental data
- Background section is shorter and focused on concepts relevant to tested hypotheses
- Paper reads as a completed study, not a proposal
- All claims in Results backed by data in `experiments/H{n}/results/`

---

## Update pipeline-state.yaml

```bash
python3 -c "
import yaml, datetime
with open('pipeline-state.yaml') as f:
    state = yaml.safe_load(f)
existing = state.get('phases', {}).get(15, {})
state['phases'][15] = {
    'status': 'complete',
    'output': 'synthesis/final-paper.md',
    'started': existing.get('started', 'unknown'),
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
}
state['current_phase'] = 16
with open('pipeline-state.yaml', 'w') as f:
    yaml.dump(state, f, default_flow_style=False)
"
```

## Git Checkpoint

```bash
git -C "${CLAUDE_PROJECT_DIR:-.}" add synthesis/final-paper.md pipeline-state.yaml
git -C "${CLAUDE_PROJECT_DIR:-.}" commit -m "phase-15-complete: empirical paper assembled"
```
