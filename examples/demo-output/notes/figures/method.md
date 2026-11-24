# Figure `method`

**Caption.** Out-of-fold filtering in four steps. (1) The training labels contain flips; each tile shows a sample with its given label as a colored bar, and a red-orange corner flag marks a flipped label. (2) A classifier is fit with K-fold cross-validation (K = 5): trained on four folds (dark strips), it predicts the held-out fold (outlined strip), so every sample is predicted by a model that did not see it. (3) The dot on each tile is the out-of-fold predicted class; every sample whose predicted class differs from its label bar is crossed out and dropped. One flip goes unnoticed and one clean sample is dropped, so the filter is not perfect. (4) The classifier is refit on the kept samples. The filter uses no clean validation set and no estimate of the noise rate.

**What it shows.** A 2 by 2 reading order (1 to 4) with the same thick arrows between panels. Disagreement is visible by color: in panel 3 the dot (prediction) and the bar (label) differ on every crossed-out tile. The purple classifier card is the only learned part. The tile grid is illustrative (20 tiles, 16 kept), not real data.

**Notes.** Panel titles render in the module's default face; the in-panel labels are sans-serif.
