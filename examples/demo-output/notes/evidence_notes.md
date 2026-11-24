# Evidence notes

`paper/sources.py` has 103 recipes and all return values (`scriptorium numbers`). Per-seed helpers: `_accs(dataset, noise, method)`, `_diff(dataset, noise, a, b)`, `_precisions`, `_recalls`, `_dropped_frac`, `_recovery`. All are in seed order and paired by seed. Accuracy is in percent. The dataset keys are `digits` and `breast_cancer` (`bc` in recipe keys).

## What the data supports

Out-of-fold filtering helps a linear model clearly at 20% and 40% symmetric noise. The gain over plain logistic regression is largest on digits (about 6 points at 20% noise and 9 points at 40%) and smaller on breast_cancer (about 3 and 4 points). It lowers variance at 20% noise, but not at 40% on breast_cancer, where the sd is about 9 for both filter and logreg.

The MLP trained on the same noisy labels degrades much faster than the linear model. It falls to about 65% at 40% noise on both datasets. The filter beats the MLP in all 5 seeds in all four noisy cells, by 11 to 28 points. The MLP is the better model on clean digits.

The filter drops mostly flipped labels. Mean precision is 65–76% across the four noisy cells, with a minimum of 61% in any single run. Recall is high (79–98%). The filter also drops many correct samples, since precision is far from 100%.

The filter costs a little on clean labels: -0.2 points on digits and -0.1 on breast_cancer. It still drops 3.5% (digits) and 1.9% (breast_cancer) of clean training samples.

## Claims in brief.md

1. "Recovers most of the accuracy that label noise costs a linear model." This is supported only in a narrower form.
   - Digits: about 78% recovered at 20% noise and 68% at 40%.
   - Breast_cancer: about 66% at 20% noise, but only 22% at 40%.
   - At 40% noise on breast_cancer the claim is contradicted. The gain is 3.6 points against a 16.4-point loss, and the seed variance is large (sd about 9).
   - On breast_cancer at 20% noise the loss is only 4.4 points, so the recovery ratio is unstable across seeds (per-seed minimum -67%). Report the ratio of means, or use the absolute points.
   - Say "most" for digits at both rates and for breast_cancer at 20% noise. Say "part" for breast_cancer at 40% noise.
   - The recovered share depends on the clean logreg accuracy as the reference. No oracle run exists.
2. "Most of the samples it drops are truly mislabeled." This is supported at 20% and 40% noise (precision 61–76% per run, mean 65–76%). The margin is moderate: roughly a quarter to a third of dropped samples are clean. At 0% noise the notion does not apply, because every dropped sample is clean.
3. "Beats a larger model (an MLP) trained on the same noisy labels." This is supported at 20% and 40% noise on both datasets. It is not supported at 0% noise: the MLP is ahead by about 0.7 points on digits and is level with or ahead of the filter on breast_cancer. Scope the claim to one MLP (64 hidden units, sklearn defaults, 500 iterations, no tuning, no noise-robust training, convergence not logged). Say "an untuned MLP", not "larger models".
4. "It costs little when the labels are clean." This is supported: -0.22 points on digits and -0.12 on breast_cancer, within the seed sd (0.4–1.2). It is a mean over 5 seeds only, and a test of paired differences is needed before saying "no cost".

## Not supported, or to avoid

- No comparison with co-teaching or confident learning was run. Cite them only. Do not write "outperforms prior noise-robust methods".
- Only symmetric noise, noise rates up to 40%, two small datasets, 5 seeds, and no hyperparameter sensitivity (K, C). No scaling claim, no claim about deep networks or large data.
- The fit-time numbers come from a single unrecorded machine. The filter is about 5 times slower than logreg here (0.056 s against 0.012 s on digits). Do not make speed claims beyond this.
- The sampled noise rates are slightly below nominal (39.4% on digits and 38.6% on breast_cancer at nominal 40%).
