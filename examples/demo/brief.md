# Brief for the paper

## Working title
Drop what the model disagrees with: out-of-fold filtering for label noise

## The idea in one paragraph
Label noise hurts simple classifiers. We fit logistic regression with K-fold cross-validation, drop every training
sample whose out-of-fold prediction disagrees with its given label, and refit on the rest. The filter needs no clean
validation set and no noise-rate estimate.

## What we want to claim
- The filter recovers most of the accuracy that label noise costs a linear model.
- Most of the samples it drops are truly mislabeled.
- It beats a larger model (an MLP) trained on the same noisy labels.
- It costs little when the labels are clean.

## Where the results live
results/runs.jsonl (all runs; experiments/run.py writes it), settings in experiments/config.json.

## Must-cite work
Co-teaching (Han et al., NeurIPS 2018), confident learning (Northcutt et al., JAIR 2021), the survey by Song et al.
on learning from noisy labels (IEEE TNNLS).

## Anything to avoid
This is a small study on two small datasets; do not claim it scales to deep networks or large data.
