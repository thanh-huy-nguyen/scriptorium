# Demo: a small label-noise study

A tiny research repository to try Scriptorium on. `experiments/run.py` (scikit-learn) compares logistic regression,
an MLP, and logistic regression with out-of-fold label filtering under 0%, 20% and 40% symmetric label noise on two
scikit-learn datasets, five seeds each. Its output is already in `results/runs.jsonl`, so you do not need to rerun it.

```bash
cd examples/demo
scriptorium init      # keeps the brief.md and scriptorium.toml that are here; locks the data
scriptorium run       # about 20 agent sessions; writes paper/main.pdf and .scriptorium/report.md
```
