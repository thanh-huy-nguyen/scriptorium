# Evidence notes

Source: `results/runs.jsonl` (90 runs: 2 datasets x noise {0, 0.2, 0.4} x 5 seeds x {logreg, mlp, filter}) and `experiments/config.json`. All values come from recipes in `paper/sources.py` (key names in backticks). Accuracies are percent on a clean test split; sd is over 5 seeds, and seeds change the split, the noise draw and the init together.

## What the data supports
- Filter vs. logreg on the same noisy labels: digits +6.0 pt at 20% noise, +9.0 pt at 40% (5/5 seeds each). breast_cancer +2.9 pt at 20% (4/5 seeds), +3.6 pt at 40% (5/5 seeds). (`diff_*_filter_minus_logreg`, `wins_*_filter_over_logreg`)
- Filter vs. MLP on the same noisy labels: +11 to +28 pt, 5/5 seeds, in all four noisy cells. The MLP degrades badly (digits 97.3 -> 82.4 -> 64.9). (`diff_*_filter_minus_mlp`, `wins_*_filter_over_mlp`)
- Filter drops mostly mislabeled samples. Precision is 64.6% (digits, 20%), 76.1% (digits, 40%), 76.4% (bc, 20%), 68.3% (bc, 40%). Per-seed minimum is 61%. Recall is 98% on digits, 93% on bc at 20%, 79% on bc at 40%. (`precision_*`, `recall_*`)
- Realised noise is close to nominal (19-20% and 39%). (`noisy_frac_*`)
- Clean labels: filter is within 0.2 pt of logreg on both datasets (`clean_cost_dg` -0.22, `clean_cost_bc` -0.12). It still discards 3.5% of digits and 1.9% of bc training samples (`dropped_frac_*_00_mean`).
- Fit time of the filter is about 4.7x logreg on digits (`time_ratio_filter_logreg_digits`). This is machine-dependent, so state it with care.

## Claims in brief.md
1. **"Recovers most of the accuracy that label noise costs a linear model."** Supports a narrower version. Recovery fraction (filter - noisy)/(clean - noisy): digits 78% (20%) and 68% (40%); bc 66% (20%) but only 22% (40%). Most is recovered in 3 of 4 cells. On bc at 40% the filter ends 12.7 pt below clean (`gap_bc_40_filter_to_clean`) and the sd is about 9 pt, so the gain (+3.6 pt) is smaller than the seed spread. Say "most at 20% noise on both datasets and at 40% on digits"; do not generalise to bc at 40%.
2. **"Most of the samples it drops are truly mislabeled."** Supported at 20% and 40% on both datasets (precision 61-77% in every seed). The margin is modest, with roughly a third of drops being clean samples. Not meaningful at 0% noise, where all drops are clean, though few. Say "about two thirds to three quarters".
3. **"It beats a larger model (an MLP) trained on the same noisy labels."** Supported for noisy labels: all 20 (cell, seed) comparisons favour the filter, by 11-28 pt. At 0% noise the MLP is better or tied (digits MLP 97.3 vs filter 96.6, -0.7 pt; bc tied). Restrict to noisy labels. Caveats: the MLP is a default sklearn MLP with no early stopping or regularisation tuning, so this is a weak baseline. "Larger" means 64 hidden units, a single layer. No noise-robust baseline (confident learning, co-teaching) was run, so do not claim to beat the cited methods.
4. **"It costs little when the labels are clean."** Supported: mean change -0.22 pt (digits) and -0.12 pt (bc), well inside the seed sd (0.4-1.2 pt). Filter is below logreg in 2/5 seeds on digits and 1/5 on bc. 5 seeds and tiny effects mean there is no significance claim.
5. **"Avoid: do not claim it scales."** Fully respected. The data covers only two small sklearn datasets, a linear model and one MLP, and symmetric noise only.

## Warnings for the outliner and writers
- No ablations exist (K, C, MLP size, filter variants), and no oracle or noise-robust baseline. Do not write an ablation section.
- Test sets are small (171 for bc, so 1 sample = 0.58 pt). The bc 40% result is high-variance (filter sd 8.95, logreg sd 9.39).
- On breast_cancer with clean labels, `acc_bc_00_mlp_*` is identical to `acc_bc_00_logreg_*` (mean and sd). Probably a coincidence on the same test items, but verify before drawing any contrast; the text should not say "MLP matches logreg" with confidence.
- Noise is symmetric and train-only, and the filter is applied once. Mean +/- sd is across seeds that also change the split. No confidence intervals or paired tests were computed.
- The filter fit time includes 5-fold CV and one refit; timings are single measurements on an unknown machine.
- Library versions and run date are not recorded in the repo.
