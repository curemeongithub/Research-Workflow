---
name: gap-scoring-rubric
description: Standardized 4-dimensional scoring rubric for research gap analysis. Use when scoring gaps by Confidence, Impact, Feasibility, and Verifiability to assign Tier 1/2/3 classification.
user-invocable: false
---

# Gap Scoring Rubric

Standardized scoring criteria for Phase 4 gap analysis. Ensures gaps are scored consistently using evidence-based calibration rather than intuition.

---

## The Four Dimensions

### 1. Confidence of Existence (0-10)

Does the evidence confirm this gap actually exists?

| Score | Criteria |
|-------|---------|
| 9-10 | Multiple papers explicitly state this is open/unsolved. Literature map Section 6 lists it as contested. |
| 7-8 | One paper states it as future work + Section 7 shows no methodology has addressed it. |
| 5-6 | Absence of evidence: no paper addresses this specific question, but none say it's open either. |
| 3-4 | Gap inferred from model knowledge — must be marked as "unverified from sources." |
| 1-2 | Contradicted by a source that appears to address the question. |
| 0 | A source directly refutes the claim that this gap exists. |

**Default when uncertain:** Score ≤5 and mark as "unverified."

### 2. Potential Impact (0-10)

If this gap is filled, how much would it advance the field?

| Score | Criteria |
|-------|---------|
| 9-10 | Would challenge a core assumption or enable an entirely new class of applications. |
| 7-8 | Would significantly extend the frontier; likely to be cited widely. |
| 5-6 | Useful incremental advance; addresses a known limitation in practical settings. |
| 3-4 | Interesting academically but limited practical impact. |
| 1-2 | Marginal: addresses edge case or rarely-used configuration. |

### 3. Feasibility (0-10)

Can this gap be addressed with currently available methods, data, and compute?

| Score | Criteria |
|-------|---------|
| 9-10 | Requires only combining existing methods; no new theory needed; public data and compute. |
| 7-8 | Requires new implementation but no fundamental methodological breakthroughs. |
| 5-6 | Requires new methodology that is plausible given the current state of the field. |
| 3-4 | Requires breakthrough that isn't currently in sight; or needs proprietary/unavailable data. |
| 1-2 | Requires fundamental unsolved problems to be solved first. |

### 4. Verifiability (0-10)

Can researchers confirm the gap is being closed through measurable results?

| Score | Criteria |
|-------|---------|
| 9-10 | Existing benchmarks directly measure the capability. Clear quantitative success threshold. |
| 7-8 | New benchmark needed but straightforward to define; metric is obvious. |
| 5-6 | Requires new evaluation framework; definition of success may be contested. |
| 3-4 | Difficult to define success objectively; risk of goalpost moving. |
| 1-2 | Essentially unfalsifiable; success cannot be measured. |

---

## Composite Score

```
Composite = (Confidence × 2 + Impact + Feasibility + Verifiability) / 5
```

Confidence is weighted 2× because an unverified gap is not a real gap.

---

## Tier Assignment Rules

| Tier | Minimum Composite | Confidence Minimum | Impact Minimum |
|------|-----------------|-------------------|---------------|
| **Tier 1** | ≥7.0 | ≥7 | ≥8 |
| **Tier 2** | ≥5.5 | ≥6 | ≥5 |
| **Tier 3** | ≥4.0 | ≥8 | ≥3 |

Note: Tier 3 requires HIGH confidence despite lower impact — stress-tests must be verifiably needed.

If no gaps qualify for Tier 1, degrade gracefully to Tier 2. Do not fabricate Tier 1 gaps to fill the template.

---

## Rejected Candidate Requirements

Every rejected candidatesMUST include:
1. The specific reason for rejection (evidence found, gap too vague, not verifiable)
2. The source that most directly addresses the gap (with file path and approximate location)

Poor reason: "This gap seemed too broad."  
Good reason: "Smith et al. (2023) directly address this in Section 4.2 of their paper (sources/arxiv-2302.XXXXX/paper.tex, ~line 450). Their Experiment 3 measures precisely this condition."

---

## Calibration Notes

**Overconfident patterns to avoid:**
- Giving Confidence 8 when you only have a single "future work" mention
- Giving Impact 9 to anything that sounds interesting
- Marking everything as Tier 1

**Calibration anchors:**
- Tier 1 gap: would be a compelling NeurIPS workshop motivation
- Tier 2 gap: would be an interesting ablation in a larger paper
- Tier 3 gap: would be a solid empirical evaluation paper
