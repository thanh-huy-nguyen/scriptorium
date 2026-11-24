# fig1

## Caption

Out-of-fold disagreement finds flipped labels, and refitting without them keeps a linear model accurate under label noise. (1) A training set with symmetric label flips; flipped tags are outlined in red, and thumbnails are schematic digit glyphs, not dataset samples. (2) Each sample is predicted by a logistic regression fit on the other four folds; samples whose prediction disagrees with their tag are crossed out and dropped. Most dropped samples are truly flipped (bar, pooled over all digits runs at 40% noise). (3) Test accuracy of logistic regression, an untuned MLP and the filter (ours, in the accent color of the method) at 0, 20 and 40% label noise. Bars are means over 5 seeds (all runs, no selection), error bars are sd, and dots are seeds. The y axis starts at 50%; the dashed line is the filter's clean-label accuracy. The filter stays closest to its clean-label accuracy as noise grows and the MLP falls furthest; on Breast cancer at 40% noise the seed spread is wide and the filter's lead over logistic regression is small.

## What the figure shows

Three panels: noisy labels, out-of-fold dropping, refit. Panel 2 shows folds 1-4 (bracket) fitting the network card and the fifth as the held-out fold it predicts. The stacked bar gives the pooled precision (flipped 76%, clean 24%), computed from `results/runs.jsonl` (digits, 40% noise runs where the filter dropped samples). Panel 3 draws bars, sd and seed dots from the same file.

## Notes for the author

- Layout fixes: all text is now 8 pt at print size, the tiny fold digits are gone, and the "all dropped" note has its own row well above the bar.
- Color: the accent comes from the theme (`sf.color`), which is teal in "harbor", not Northwestern purple. The caption names it by role only, so it is correct either way. For purple, set the theme in scriptorium.toml (outside my scope).
- Placement (outside my scope): the teaser must be `\begin{figure*}[t]` before the first paragraph of 01_intro.tex, and the tables must come after it. The script writes `fig1`, so `\includegraphics` should point to `figures/fig1.pdf`; the older `teaser` files are unused.
- scikit-learn is not importable here, so thumbnails are schematic pixel digits; delete that clause from the caption if sklearn becomes available.
