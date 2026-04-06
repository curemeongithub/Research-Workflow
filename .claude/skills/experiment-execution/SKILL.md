---
name: experiment-execution
description: Conventions for experiment directory structure, status tracking, result formats, and the coder-reviewer interaction protocol. Used by all agents in Phases 12-14.
user-invocable: false
---

# Experiment Execution Conventions

## Directory Structure per Hypothesis

```
experiments/H{n}/
├── roadmap.md           # Phase 12 output — the plan
├── status.yaml          # Current state — updated by coder and reviewer
├── review.md            # Latest reviewer feedback
├── error.log            # Latest error (if any)
├── scripts/             # Python scripts written by coder
│   ├── step1_setup.py
│   ├── step2_run.py
│   └── analyze.py
├── results/             # Output data
│   ├── step1_output.csv
│   ├── step2_output.csv
│   ├── summary_table.csv
│   ├── base_case_evaluation.json
│   └── figures/
│       ├── main_result.png
│       └── ...
├── colab/               # Colab notebooks (if GPU needed)
│   └── H{n}_step{N}.ipynb
├── colab-results/       # Results from Colab runs (user places here)
│   └── step{N}_output.csv
└── analysis.md          # Phase 14 output — final analysis
```

## status.yaml Schema

```yaml
hypothesis: H{n}
status: roadmap_complete | in_progress | error | colab_needed | colab_complete | base_case_met | base_case_failed | failed_irrecoverable | analysis_complete
current_step: {N}
steps_total: {N}
steps_completed: {N}
iteration: {N}  # how many coder-reviewer cycles
base_case_met: true | false
base_case_metric: {name}
base_case_value: {number or null}
base_case_threshold: {number}
last_error: "{error summary or null}"
last_updated: "{TIMESTAMP}"
```

## Result File Conventions

- All tabular results: CSV with headers
- All numerical summaries: JSON
- All figures: PNG, 300 DPI, with descriptive filenames
- base_case_evaluation.json format:
  ```json
  {
    "pass": true,
    "metric_name": "spearman_rho",
    "metric_value": 0.73,
    "threshold": 0.7,
    "comparison": "greater_than",
    "details": "Computed over 960 runs across (n, r, beta) grid"
  }
  ```

## Coder-Reviewer Protocol

1. Coder runs a step → updates status.yaml
2. If error → writes error.log, sets status to "error"
3. Reviewer reads error.log → writes review.md with fix instructions
4. Coder reads review.md → applies fix → re-runs
5. If success → coder moves to next step
6. After final step → coder runs analysis script → checks base case
7. If base_case_met → done
8. If not → reviewer decides: adjust parameters and re-run, or fail

## Script Conventions

- All scripts must be runnable standalone: `python scripts/{name}.py [args]`
- All scripts must save results to `results/` (relative to experiment directory)
- All scripts must print progress to stdout
- All scripts must catch and print exceptions with full traceback
- All scripts must set random seeds for reproducibility
- Use argparse for any configurable parameters
