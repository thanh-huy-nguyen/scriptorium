# Figure `teaser`

Files: `paper/figures/teaser.pdf` (script `paper/figures/teaser.py`), full text width, 6.75 in x 3.33 in.

## Caption

This is the caption printed in `paper/01_intro.tex`.

We show what the out-of-fold filter does, removes, gains and costs. (a) A logistic regression fit on the other cross-validation folds predicts each training sample (1). The filter compares this prediction with the given label (2), drops mismatches (3) and refits once (4). Samples are schematic (fill marks the given class); correctly labeled ones can be dropped too. (b) Share of the training set removed, split into mislabeled and correctly labeled samples; black marks beside the bars give the mislabeled share of the whole training set. (c) Test accuracy of ours minus that of logistic regression with the same settings (red zero line), paired by seed. Gray marks place the clean-label reference on this scale, at the accuracy that noise costs logistic regression. Under noise, every mean gain falls short of its mark. Bars are means over 5\src{n_seeds} seeds; in (c), error bars are sd and dots are seeds.

## What the figure shows

- (a) "Filter noisy labels": the noisy input with the two things the filter does without ("Needs no clean set", "Needs no noise rate"), then four numbered stages ("Predict", "Compare", "Drop", "Refit once"). In stage 1 a bracket and arrow lead from the other folds into the model card (fit), and a curved arrow leads from the card into the held-out fold (predict). The held-out fold, the crosses, the refit line and the refit model card are in the accent color. The scatter positions are hand-placed and schematic; one correctly labeled point is dropped along with three mislabeled ones.
- (b) "What it removes": stacked means per setting (`drop_fraction_*_noise0`, `drop_share_mislabeled_*`, `drop_share_correct_*`). The mislabeled share of the training set (`noisy_share_*`) is a black mark in two short stubs, one on each side of the bar, so the top of the solid segment stays visible. All three encodings share one legend.
- (c) "What it gains and costs": mean paired gain over logistic regression (`gain_vs_logreg_*`), its sd (`std_gain_vs_logreg_*`), the five seed values of each bar, and on each noisy setting the accuracy that noise costs logistic regression (`noise_cost_*`) as a gray mark. The red zero line is logistic regression.

## Layout choices that differ from the plan

- The figure uses the kit's full width and is slightly taller than planned, so that all text stays at 7.5 pt or larger without collisions.
- Stage titles are shortened so that each numbered circle sits directly left of its title inside the tile.
- The note under the fold strip reads "Out-of-fold, each in turn", and the two pills begin with "Needs".
- The input tile also names the correctly labeled point that stage 3 drops.
- The reference in (b) is black instead of gray, so that gray stands only for the clean-label reference. The legend labels of (b) are shortened to fit on one line.
- Panel (c) is titled "What it gains and costs" and plots paired gains with a true zero, in place of two accuracy bars per setting on an axis that starts at 60.
- The check and cross marks are drawn in the script, so that they match in weight and cannot be mistaken for the filled class marker.
