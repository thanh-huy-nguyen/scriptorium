# Evidence notes

All values come from `paper/sources.py` (91 recipes, all return values; `scriptorium numbers` run). Data: 90 runs, 2 datasets x 3 noise rates (0, 20, 40%) x 5 seeds x 3 methods. Per-seed helpers: `_accs`, `_diff`, `_precisions`, `_recalls`, `_dropped`.

## What the data supports

Label noise costs logistic regression a lot (digits: 7.7 points at 20%, 13.2 at 40%; breast_cancer: 4.4 and 16.4). The out-of-fold filter beats plain logreg in 19 of 20 noisy runs and beats the MLP in all 20. The MLP is hurt far more than logreg by noise, so the "larger model" comparison is really "a flexible model memorizes noise". The gain over logreg grows with noise on both datasets (digits +6.0, +9.0; breast_cancer +2.9, +3.6 points). The filter drops many samples (digits about 377 of 1257 at 20% noise, 634 at 40%), and its precision is 65 to 76% across the four noisy cells. Its recall is high (79 to 98%). Cost on clean labels is small: 0.22 points on digits and 0.12 on breast_cancer, with filter beating logreg in only 3 of 10 clean runs.

## Claims in brief.md

1. **"Recovers most of the accuracy that noise costs a linear model."** Narrower version supported. Recovered share of logreg's loss: digits 78% (20%) and 68% (40%); breast_cancer 66% (20%) but only 22% (40%). So "most" holds in three of four cells and fails for breast_cancer at 40% noise, where the filter is still about 12 points below clean accuracy and has a large seed sd (8.95). Say "recovers most of the loss at moderate noise and on digits at high noise". The recovered fraction uses means over seeds and our own definition (clean reference is logreg at 0% noise, not a separate clean-label run). Breast_cancer losses at 20% noise are small (4.4 points), so that ratio is noisy.
2. **"Most of the samples it drops are truly mislabeled."** Supported, with a limit. Mean precision is above 50% in every noisy cell (digits 64.6% and 76.1%, breast_cancer 76.4% and 68.3%; pooled 71.3%). Roughly 25 to 35% of drops are correctly labeled samples. Precision is undefined at 0% noise: the filter still drops 43.6 digits samples (3.5%) and 7.4 breast_cancer samples (1.9%), all clean. We only have counts, not which samples were dropped, so we cannot say what kind of clean samples go.
3. **"Beats a larger model (an MLP) on the same noisy labels."** Supported on both datasets at 20% and 40% noise (20 of 20 paired runs; gaps 11 to 28 points). Caveats: the MLP is untuned (64 hidden units, 500 iterations, convergence not logged), and it ties or beats the filter with clean labels (digits: MLP 97.3 vs filter 96.6). Do not say "larger models are worse"; say an untuned MLP overfits the noisy labels. No tuned, early-stopped or regularized MLP was run.
4. **"Costs little when labels are clean."** Supported, narrowly. Loss is 0.22 points (digits) and 0.12 points (breast_cancer) against logreg; both are well within one seed sd (0.8 to 1.2 points). The filter also takes about 5x the fit time of logreg on digits (indicative only; machine unknown). Significance is the statistician's call.

## Do not claim

- No scaling, no deep networks, no large data (brief agrees). Two small sklearn datasets, one symmetric noise type, five seeds.
- No comparison with co-teaching or confident learning, and no ablation (folds, C, MLP size). Cite them as related work only.
- No clean-label oracle run exists. The 0% noise condition is the only clean reference.
- "No noise-rate estimate needed": true by construction (the code never uses the rate), but the data do not test robustness to a wrong rate.
- Seed variance mixes split, noise draw and fold variance. Realized noise is slightly below nominal at 40% (digits 39.4%, breast_cancer 38.6%).
- Breast_cancer at 40% noise is unstable: filter sd 8.95 and logreg sd 9.39 points. Do not put a tight claim on that cell.
