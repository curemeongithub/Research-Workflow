---
name: methodology-standards
description: DOE best practices and experimental design standards for Phase 7. Use when designing experiments, selecting baselines, identifying variables, and writing reproducibility checklists.
user-invocable: false
---

# Methodology Standards

Design of Experiments (DOE) best practices for Phase 7. Ensures experimental designs are rigorous, reproducible, and grounded in the literature.

---

## The FATS Framework (from Phase 6)

Every experiment must test a hypothesis that is:
- **Falsifiable** — a conceivable result would disprove it
- **Actionable** — can be investigated with real experiments
- **Testable** — has measurable outcomes
- **Specific** — names specific conditions, methods, or quantities

If the hypothesis is not FATS, the experiment is not worth designing.

---

## Baseline Selection

### Required Baselines

Every experiment must include at minimum:
1. **Ablation baseline:** The full proposed method minus the novel component
2. **Best prior method:** The strongest published result on the same evaluation setup
3. **Simple baseline:** The simplest possible approach (often surprisingly hard to beat)

### Citing Baselines

Every baseline must be cited from the downloaded sources:
```
- **ViT-B/16** (Dosovitskiy et al., 2020): achieves 81.8% top-1 on ImageNet with standard fine-tuning. We use this as our primary baseline because it represents the dominant architecture for patch-based vision transformers.
```

Do NOT invent baseline names. If you cannot find a baseline in the literature, note that the experiment would advance the field precisely because there is no established baseline.

---

## Variable Identification

### Independent Variables

List ALL variables you will manipulate, not just the one you're testing:
- Primary: the intervention being tested
- Secondary: any other variables you'll sweep over (e.g., learning rate, model size)

### Controlled Variables

List everything you hold constant. These need to be specified because a reader must be able to reproduce the result:
- Hardware (GPU model, memory)
- Random seed(s)
- Number of training epochs
- Data preprocessing pipeline
- Optimizer and hyperparameters

### Confounding Variables

Variables that could explain a positive result without the hypothesis being true:
- Dataset contamination (train/test overlap)
- Hyperparameter overfitting
- Model size differences between compared methods
- Different training budgets

---

## Evaluation Protocol

### Primary Metric

Choose ONE primary metric that directly tests the hypothesis. The metric must be:
- Established in the literature (cite the paper that introduced it)
- Applicable to your baseline as well
- Interpretable: what does it mean for the metric value to go up/down?

### Statistical Significance

Never report a single-run result as definitive. Specify:
- Number of seeds/runs (minimum 3 for small models, 3-5 for large)
- Statistical test: t-test (normal data), Wilcoxon (non-normal), bootstrap CI
- Significance threshold: α = 0.05 (standard)
- Correction for multiple comparisons if testing N hypotheses: Bonferroni

### Expected Results Table

Before running experiments, write down what you expect to see:

| Condition | Expected primary metric | Interpretation |
|-----------|------------------------|---------------|
| Proposed method | >X% | Hypothesis confirmed |
| Ablation baseline | ~Y%, lower than proposed | Component matters |
| Best prior method | ~Z% | Competitive with literature |

If results match this table: hypothesis supported. If each condition achieves roughly the same result: hypothesis not supported. This table must be written BEFORE running experiments (pre-registration).

---

## Reproducibility Checklist

A methodology is complete only if a researcher with standard resources could reproduce it. Verify:

- [ ] Code repository referenced or planned
- [ ] Dataset with specific version/split specified
- [ ] All hyperparameters listed
- [ ] Hardware requirements specified
- [ ] Estimated compute budget (GPU-hours)
- [ ] Random seeds specified
- [ ] Evaluation metric formula given

---

## Effort Estimation Guidelines

| Effort Level | Typical Profile |
|-------------|----------------|
| **LOW** (<1 week) | Existing code, existing data, small model (<1B params), < 8 GPU-hours |
| **MEDIUM** (1-4 weeks) | New implementation, public data, medium model (1-10B params), < 100 GPU-hours |
| **HIGH** (>4 weeks) | New dataset collection, large model (>10B params), >100 GPU-hours, OR requires coordination with external parties |

---

## Common Design Failures

- **Underpowered study:** Too few samples or runs to detect the effect size the hypothesis predicts
- **Moving goalposts:** Success metric changes after seeing results
- **Missing ablation:** Attributing improvement to the novel component without verifying it's not the optimizer, data, or training recipe
- **Overfitted hyperparameters:** Tuning on the test split (even inadvertently)
- **Benchmark saturation:** Evaluating on a benchmark where published methods already exceed 99% — no room to show improvement
