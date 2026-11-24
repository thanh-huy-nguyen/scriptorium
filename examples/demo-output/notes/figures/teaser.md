# teaser

## Caption

Out-of-fold disagreement finds flipped labels, and dropping those samples wins back much of the accuracy that label noise costs a linear model, most on digits. (a) Share of dropped samples that were truly flipped (precision, dark slate blue) and share of flipped labels that were dropped (recall, light blue) at 20% and 40% symmetric noise. Error bars on precision are sd over 5 seeds; recall bars have none. The dashed line marks 50%: in every setting more than half of the drops are flips. (b) Test accuracy against label noise for logistic regression (teal), an untuned MLP (brown) and our out-of-fold filter (purple); bands are sd over 5 seeds. The dashed gray line is logistic regression on clean labels. The lavender box at 40% spans the gap between noisy logistic regression and that clean level, the purple tick marks where the filter lands, and the label gives the share of the gap won back. The y axes do not start at zero and differ between the two datasets. (c) Cost of filtering when labels are clean: paired accuracy change of the filter against logistic regression at 0% noise (points, 95% interval over 5 paired seeds) and the share of clean training samples the filter drops. The filter's mean is slightly below logistic regression on both datasets; the interval includes zero on digits and touches zero on breast cancer.

## What the figure shows

- (a) Precision at 20% / 40% noise: digits 64.6 / 76.1%, breast cancer 76.4 / 68.3% (sd 2.3 / 0.8 and 3.4 / 4.0). Recall: digits 98.5 / 97.5%, breast cancer 92.5 / 78.9%.
- (b) Share of the accuracy lost to 40% noise that the filter wins back: digits 68.3%, breast cancer 22.1% (recipes `recovery_digits_n40`, `recovery_bc_n40`). The MLP falls fastest on both datasets.
- (c) Filter minus logistic regression at 0% noise: digits -0.22 points (95% interval -0.89 to 0.33), breast cancer -0.12 points (-0.35 to 0). Dropped clean samples: digits 3.5%, breast cancer 1.9%.

Every plotted value comes from `sf.recipe`. Per-seed dots are omitted because no recipe stores per-seed values.
