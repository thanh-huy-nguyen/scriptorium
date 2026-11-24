# Figure gains (column width)

## Caption

The filter's accuracy gain grows with label noise. Bars show the paired test-accuracy difference between the filter (ours) and each baseline, logistic regression and an untuned multilayer perceptron (MLP), at each noise rate on digits (left) and breast cancer (right). Bars are means over 5 seeds, error bars are 95% CIs of the paired difference, and dots are individual seeds. Values below zero mean the baseline is better, so the y axis starts below zero. On clean labels the gain is near zero against logistic regression and slightly negative against the MLP on digits. Under noise every seed favors the filter over the MLP, and on digits the gain over logistic regression grows from 20 to 40% noise.

## What it shows

Every bar is the filter's gain (filter minus the named baseline), so the legend names the baseline, not the method. Gray line: zero. Both panels share the y axis (-3 to 33 points). Per-seed dots come from results/runs.jsonl, paired by seed.

Mean paired gain (points), recipe keys `diff_filter_{logreg,mlp}_{digits,breast_cancer}_n{0,20,40}`; 95% CIs from `dg*/bc*_{lr,mlp}_diff_ci_{low,high}`:

| dataset | baseline | 0% | 20% | 40% |
|---|---|---|---|---|
| digits | logistic regression | -0.22 | 6.00 | 9.04 |
| digits | MLP | -0.74 | 12.70 | 27.74 |
| breast cancer | logistic regression | -0.12 | 2.92 | 3.63 |
| breast cancer | MLP | -0.12 | 10.99 | 18.60 |

Digits at 0% noise: the CI against logistic regression is [-0.89, 0.33] (includes zero); against the MLP it is [-1.15, -0.37] (below zero).

Note: the bar colors are the hexes Figure 1 (teaser.py) uses for the baselines: muted blue #5B84B1 for logistic regression and muted orange #E0A25A for the MLP. They are set directly in the script because the theme maps the MLP to purple, which is reserved for our method; the theme mapping (outside paper/figures/) should be changed to match. Dots are drawn at s=9 with a thin white edge; the zero line is dark gray, lw 1.0.
