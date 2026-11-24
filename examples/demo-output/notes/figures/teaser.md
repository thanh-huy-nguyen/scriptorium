# teaser

## Caption

Out-of-fold disagreement finds flipped labels, and refitting without them keeps a linear model accurate under label noise. (1) A training set with symmetric label flips; flipped tags are outlined in red, and thumbnails are schematic digit glyphs, not dataset samples. (2) Each sample is predicted by a logistic regression fit on the other four folds; samples whose prediction disagrees with their tag are crossed out and dropped. Most dropped samples are truly flipped (bar, pooled over all noisy runs). (3) Test accuracy of plain logistic regression, an untuned MLP and the filter (ours) at 0, 20 and 40% label noise. Bars are means over 5 seeds (all runs, no selection), error bars are sd, and dots are seeds. The y axis starts at 50%; the dashed line is the filter's clean-label accuracy. The filter stays closest to its clean-label accuracy as noise grows and the MLP falls furthest; on Breast cancer at 40% noise the seed spread is wide and the filter's lead over logistic regression is small.

## What the figure shows

Three panels: noisy labels, out-of-fold dropping, refit. Panel 2 shows folds 1-4 (bracket) fitting the network card and fold 5 as the held-out fold it predicts. The stacked bar gives the pooled precision, computed from `results/runs.jsonl` (digits, 40% noise runs where the filter dropped samples). Panel 3 draws bars, sd and seed dots from the same file.

## Notes for the author

- Colors now come from the theme (`sf.color`), so figlint passes. The accent is therefore the theme's ours color (teal in "harbor"), not Northwestern purple, and the pale tints are computed from it. The figure uses the theme's partner color for flipped tags and crosses. If the paper should show purple, set that in scriptorium.toml.
- scikit-learn is not importable in the figure environment, so the script falls back to hand-drawn 5x7 pixel digits, and the caption says the thumbnails are schematic. With sklearn it uses real 8x8 digit images; then delete that clause from the caption.
- Fonts: labels, tags, legend and tick labels are 7.5-8 pt. "clean 24%" sits below the bar. The legend row is one line above the plots, and the dashed-line meaning is in the caption only.
