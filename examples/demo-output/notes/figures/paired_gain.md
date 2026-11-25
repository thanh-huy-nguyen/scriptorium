# Figure `paired_gain`

Single column, 3.25 in x 1.94 in. Files: `paper/figures/paired_gain.py`, `paired_gain.pdf`, `paired_gain.png`.

## Caption

Paired gain in test accuracy of the out-of-fold filter (ours) over logistic regression trained on all given labels. Each dot is one seed, with both methods on the same split and the same given labels. Bars are means over 5\src{n_seeds} seeds, error bars are the sd of the 5\src{n_seeds} paired differences, and the red line at zero is logistic regression (no difference); values above it favor ours. Under noise the dots lie above zero in all but one run (breast cancer at 20\%\src{noise_rate_low} noise), including on breast cancer at 40\%\src{noise_rate_high} noise, where the accuracy of both methods varies widely between seeds (Fig.~\ref{fig:teaser}(c)). With 5\src{n_seeds} seeds, the gain on breast cancer at 20\%\src{noise_rate_low} noise is not established. On clean labels both mean gains are slightly below zero and close to it.

## What the figure shows

Comparing the two methods run by run removes the split-to-split variation that they share. The filter then comes out ahead in nearly every noisy run (19 of 20), and with clean labels it stays near logistic regression. The weak case is breast cancer at 20% noise, where one run falls below zero and the error bar crosses it. The figure supports no claim of a trend over noise rate on breast cancer.

## Values shown

Test accuracy of ours minus that of logistic regression, in percentage points. Seeds are listed in order 0 to 4, which is also the left-to-right order of the dots within each bar. Recipe keys follow `gain_vs_logreg_<dataset>_<noise>` (mean), `std_gain_vs_logreg_<dataset>_<noise>` (sd) and `gain_vs_logreg_<dataset>_<noise>_seed<s>` (dots).

| Dataset | Noise | Key suffix | Mean | sd | Seed 0 | Seed 1 | Seed 2 | Seed 3 | Seed 4 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Digits | Clean | `digits_noise0` | -0.22 | 0.77 | -0.74 | 0.19 | 0.56 | -1.30 | 0.19 |
| Digits | 20% | `digits_noise20` | 6.00 | 1.41 | 5.93 | 6.11 | 7.41 | 3.70 | 6.85 |
| Digits | 40% | `digits_noise40` | 9.04 | 2.26 | 8.89 | 9.63 | 11.85 | 5.56 | 9.26 |
| Breast cancer | Clean | `breast_noise0` | -0.12 | 0.26 | 0.00 | 0.00 | 0.00 | -0.58 | 0.00 |
| Breast cancer | 20% | `breast_noise20` | 2.92 | 3.28 | 2.92 | 5.85 | 6.43 | -1.17 | 0.58 |
| Breast cancer | 40% | `breast_noise40` | 3.63 | 1.33 | 2.92 | 5.85 | 2.34 | 3.51 | 3.51 |

Other keys behind the figure and caption: `noise_rate_low`, `noise_rate_high` (tick labels), `n_seeds`, `wins_vs_logreg_noisy` and `n_noisy_runs` (the run count above), `std_logreg_breast_noise40` and `std_filter_breast_noise40` (the wide spread between seeds, drawn in Fig. 1(c)), `p_filter_vs_logreg_breast_noise20` (gain not established) and `p_trend_gain_vs_logreg_breast_noise40_vs_noise20` (no trend on breast cancer).

## Layout choices that differ from the plan

- The zero line is drawn in the partner color of logistic regression, not in reference gray. The method keeps one color across figures, and gray keeps its single meaning in Fig. 1(c), the clean-label reference.
- The zero line is 1.0 pt wide, heavier than the grid, so that it covers less of the small clean-label bars.
- The y label names test accuracy and runs over three lines. The figure is slightly taller than planned so that the label fits the height of the axis.
