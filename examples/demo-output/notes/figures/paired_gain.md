# Figure paired_gain (column width)

## Caption

The out-of-fold filter's accuracy gain grows with label noise. Each bar is the paired test-accuracy difference between the filter and a baseline, logistic regression (dark bars) or an untuned multilayer perceptron (MLP, light bars), at each noise rate on digits (left) and breast cancer (right). Both shades are the color of our method because every bar measures the filter's gain. Bars are means over 5 seeds, error bars are 95% CIs of the paired difference, and dots are individual seeds. Values below zero mean the baseline is better. On clean labels the gain is near zero against logistic regression and slightly negative against the MLP on digits. Under noise every seed favors the filter over the MLP, and on digits the gain over logistic regression grows from 20 to 40% noise.

## What it shows

Every bar is the filter's gain (filter minus the named baseline), so the legend names the baseline being subtracted. Dark = minus logistic regression, light tint of the same color = minus MLP. The colors are our method's color from the theme (not the baseline hues of Figure 1, so the two figures do not clash); the caption deliberately names no hue. Gray line: zero. Both panels share the y axis (-3 to 33 points). Per-seed dots come from results/runs.jsonl, paired by seed.

Mean paired gain (points), recipe keys `diff_filter_{logreg,mlp}_{digits,breast_cancer}_n{0,20,40}`; 95% CIs from `dg*/bc*_{lr,mlp}_diff_ci_{low,high}`:

| dataset | baseline | 0% | 20% | 40% |
|---|---|---|---|---|
| digits | logistic regression | -0.22 | 6.00 | 9.04 |
| digits | MLP | -0.74 | 12.70 | 27.74 |
| breast cancer | logistic regression | -0.12 | 2.92 | 3.63 |
| breast cancer | MLP | -0.12 | 10.99 | 18.60 |

Digits at 0% noise: the CI against logistic regression is [-0.89, 0.33] (includes zero); against the MLP it is [-1.15, -0.37] (below zero).

Changes from the earlier `gains` version: the bars no longer use the Figure 1 baseline blue and orange; the figure is taller (aspect 0.75) so the theme's fonts are not shrunk on the page; the y label is shortened to "Accuracy gain (points)"; the legend title reads "Filter (ours) minus".
