# Figure fig2 (column width, 3.3 in; replaces the earlier "gains" figure)

## Caption

The filter's accuracy gain grows with label noise. Bars show the paired test-accuracy difference between the filter (ours) and each baseline, logistic regression (mauve) and an untuned multilayer perceptron (MLP, gray-blue), at each noise rate on digits (left) and breast cancer (right). Both hues match Figure 1; every bar is the filter's gain, so no bar is purple. Bars are means over 5 seeds, error bars are 95% CIs of the paired difference, and dots are individual seeds. Values below zero mean the baseline is better. On clean labels the gain is near zero against logistic regression and slightly negative against the MLP on digits. Under noise every seed favors the filter over the MLP, and on digits the gain over logistic regression grows from 20 to 40% noise.

## What it shows

Drawn at its final print width (3.3 in), so the theme's font sizes are real points; the tex must include it at `\linewidth` (the old include used 0.5\linewidth, which shrank the text to about 4 pt). Bar colors come from `sf.color("logreg")` and `sf.color("mlp")`, the same calls Figure 1 uses. The legend sits above the panels, titled "Filter (ours) minus". The gray line is zero. Both panels share the y axis (-3 to 33 points). Per-seed dots come from results/runs.jsonl, paired by seed.

Mean paired gain (points), recipe keys `diff_filter_{logreg,mlp}_{digits,breast_cancer}_n{0,20,40}`; 95% CIs from `dg*/bc*_{lr,mlp}_diff_ci_{low,high}`:

| dataset | baseline | 0% | 20% | 40% |
|---|---|---|---|---|
| digits | logistic regression | -0.22 | 6.00 | 9.04 |
| digits | MLP | -0.74 | 12.70 | 27.74 |
| breast cancer | logistic regression | -0.12 | 2.92 | 3.63 |
| breast cancer | MLP | -0.12 | 10.99 | 18.60 |

Digits at 0% noise: the CI against logistic regression is [-0.89, 0.33] (includes zero); against the MLP it is [-1.15, -0.37] (below zero).

## For the tex (outside my edit scope)

- Include `figures/fig2.pdf` at `width=\linewidth` and use label `fig:gains` (or update references).
- Caption: replace "(purple)" with the wording above; the bars are mauve and gray-blue, as in Figure 1.
