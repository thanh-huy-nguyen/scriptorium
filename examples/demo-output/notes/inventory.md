# Inventory (scout)

Repository root = the demo_run directory. All paths below are relative to it. Tiny repository: one script, one config, one result file.
Not present (yet): numbers.md, outline.json, related.md, any figure or table, any LaTeX. `paper/` holds only `paper/sources.py` (empty, recipes commented out).
I did not run any code (Python execution was not approved), so every number below was read by eye from `results/runs.jsonl` and is approximate. Recompute through recipes before printing anything.

## Research question and method

Question (brief.md): does dropping the training samples whose out-of-fold prediction disagrees with their given (noisy) label, then refitting, recover the accuracy that label noise costs a linear model?

Method ("filter"), implemented in `experiments/run.py`, function `main()`, lines 64-71:
1. `StratifiedKFold(filter_folds=5, shuffle=True, random_state=seed)`.
2. `cross_val_predict(logreg(), Xtr, ytr_noisy, cv=cv)` gives out-of-fold predictions.
3. `keep = oof == ytr_noisy`; every disagreeing sample is dropped.
4. Refit `logreg()` on the kept samples; report accuracy on the clean test set.
`logreg()` = `make_pipeline(StandardScaler(), LogisticRegression(C=logreg_C, max_iter=5000))`. No clean validation set and no noise-rate estimate are used (matches the brief). The filter is applied once (no iteration) and drops all disagreeing samples, with no confidence threshold.

Noise model (`flip()`, lines 27-32): each training label is selected with probability `rate` (independent Bernoulli, so the realised count varies by seed, see `n_noisy`), and a selected label is replaced by a uniformly random different class (symmetric noise). Only training labels are corrupted; the test labels are clean. For breast_cancer (2 classes) the flip always goes to the other class.

## Datasets

Both are scikit-learn built-in loaders (`LOADERS` in run.py line 24); nothing is downloaded or stored in the repo.
- `digits` (`load_digits`): 1797 samples, 10 classes, 64 features. Split per seed: n_train = 1257, n_test = 540 (from the records).
- `breast_cancer` (`load_breast_cancer`): 569 samples, 2 classes, 30 features. Split: n_train = 398, n_test = 171.
- Split: `train_test_split(test_size=0.3, stratify=y, random_state=seed)`, so the split changes with the seed (seed variation mixes split, noise draw and model init). No validation split.
- The sample and feature counts for the full datasets are not stored in any file; they are scikit-learn facts (n_train + n_test matches 1797 and 569).

## Baselines and ablations

Names as in the `method` field of `results/runs.jsonl`:
- `logreg`: standardized features, logistic regression (C=1.0, max_iter=5000) trained on the noisy labels (no filtering). This is also the filter's own base model.
- `mlp`: `MLPClassifier`, one hidden layer of 64 units (`mlp_hidden`), `max_iter=500`, `random_state=seed`, other sklearn defaults, standardized features, noisy labels. This is the "larger model" of the brief.
- `filter`: the method.
- No ablations: no sweep over K, C, MLP size, or filter variants. No confident-learning, co-teaching or other noise-robust baseline is run (the brief only asks to cite them). No oracle baseline (training on only the truly clean samples, or on clean labels with the same data) is run, but noise 0.0 `logreg` gives clean-label accuracy as a reference.

## Result files

- `results/runs.jsonl`: JSON Lines, 90 records, written in one go by `experiments/run.py` `main()` (README says output is already included, no rerun needed). Grid = 2 datasets x 3 noise rates {0.0, 0.2, 0.4} x 5 seeds {0..4} x 3 methods = 90. All records are from one run; no debug/old/final variants exist. Fields:
  - `dataset` ("digits" | "breast_cancer"), `noise` (float: label-flip probability), `seed` (int 0-4), `method` ("logreg" | "mlp" | "filter").
  - `n_train`, `n_test` (ints), `n_noisy` (int: realised number of flipped training labels; 0 at noise 0.0; same across the 3 methods of a (dataset, noise, seed) cell).
  - `test_acc` (float in [0,1], accuracy on the clean held-out test split; not a percentage).
  - `fit_seconds` (float, wall-clock; for `filter` it includes the 5-fold CV plus refit; machine-dependent, noisy).
  - `n_dropped` (int) and `n_dropped_noisy` (int: of the dropped samples, how many were truly flipped): present only on `filter` records.
  - Precision of dropped samples = n_dropped_noisy / n_dropped; recall = n_dropped_noisy / n_noisy. Both must be computed (not stored). They are undefined for precision/recall at noise 0.0 (n_noisy = 0, and n_dropped_noisy = 0).
  - Seeds: 5 per cell (n=5 per dataset/noise/method). Records are in grid order (dataset, noise, seed, method).
- `run.log`: not a run output. It is 3 lines of Scriptorium's own session log ("== scout / start scout"). Contains no results.
- `.scriptorium/state.json`, `.scriptorium/lock.json`, `scriptorium.toml`: tool bookkeeping, no results (toml holds the paper title, 4-page limit, venue).

### What the data show (by eye, approximate; recompute before use)
Mean test_acc over 5 seeds:
- digits, noise 0.0: logreg ~0.968, mlp ~0.974, filter ~0.966. Filter drops 34-49 clean samples (about 3-4% of 1257).
- digits, noise 0.2: logreg ~0.891, mlp ~0.824, filter ~0.951. Filter drops 354-393 samples, of which 225-253 are noisy (precision ~64-67%; recall ~98%).
- digits, noise 0.4: logreg ~0.837, mlp ~0.640, filter ~0.925. Filter drops 619-644 samples, of which 478-487 are noisy (precision ~76-77%; recall ~96-98%).
- breast_cancer, noise 0.0: logreg ~0.967, mlp ~0.967, filter ~0.966. Filter drops 5-9 samples (all clean).
- breast_cancer, noise 0.2: logreg ~0.923, mlp ~0.842, filter ~0.951. Dropped 76-102, noisy 59-78 (precision ~ 75-80%, recall ~ 90-95%).
- breast_cancer, noise 0.4: logreg ~0.804, mlp ~0.654, filter ~0.841 (but seeds vary a lot: filter 0.737-0.895, logreg 0.690-0.889). Dropped 159-187, noisy 112-133 (precision ~ 60-72%, recall ~ 70-85%).

## Settings the paper may report

`experiments/config.json` (read by run.py as `CFG`):
- `datasets`: ["digits", "breast_cancer"]
- `noise_rates`: [0.0, 0.2, 0.4]
- `seeds`: [0, 1, 2, 3, 4]
- `test_fraction`: 0.3
- `logreg_C`: 1.0 (inverse L2 strength; max_iter=5000 is hard-coded in run.py line 36)
- `mlp_hidden`: 64 (one hidden layer); `mlp_max_iter`: 500
- `filter_folds`: 5
Hard-coded in run.py (not in the config): StandardScaler on all models, stratified and shuffled K-fold, symmetric noise, sklearn defaults for MLP (Adam, ReLU, alpha 1e-4). Library versions are not recorded anywhere.

## Existing figures or tables

None. No figure scripts, no LaTeX, no images. The only paper files are `paper/sources.py` (placeholder) and the `.scriptorium/` notes. `.scriptorium/style.md` (style guide) asks for booktabs tables with mean ± sd and our method in #4E2A84.

## Gaps

- "Recovers most of the accuracy that noise costs": supported on digits at both rates (logreg at 0% ~0.97 vs filter ~0.95 at 20%, ~0.93 at 40%). Weaker on breast_cancer at 40% (filter ~0.84 vs ~0.97 clean; huge seed variance, filter worse than clean by about 12 points). Needs a per-dataset recovery fraction (filter - noisy logreg) / (clean logreg - noisy logreg), and state that it is not uniform.
- "Most dropped samples are truly mislabeled": supported by `n_dropped_noisy / n_dropped` at noise 0.2 and 0.4 on both datasets (precision about 60-80% by eye; lowest for breast_cancer at 40%). Do not claim it at noise 0.0 (there are no noisy samples, all dropped are clean, but they are only ~0.4-4% of training data). Digits at 20%: precision ~65%, so "most" is true but not by a wide margin.
- "Beats an MLP": the filter beats the MLP at 20% and 40% noise on both datasets (all 5 seeds in each cell, by eye). At 0% noise the MLP is as good or better on digits (~0.974 vs ~0.966), so the claim must be restricted to noisy labels.
- "Costs little when clean": digits filter ~0.2-0.7 points below logreg (mean difference ~0.2 pt by eye, filter is below in 4 of 5 seeds or equal); breast_cancer essentially 0. It discards 34-49 digits samples (~3-4%) even with no noise. No significance test, only 5 seeds.
- Seeds: 5 per cell; the test set is small (171 for breast_cancer, so 1 sample = 0.58 pt); the sd is computed across seeds that also change the split. No confidence intervals or paired tests are in the files; they would need a recipe.
- No hyperparameter or K ablation, no comparison to confident learning/co-teaching or other noise-robust methods, no non-symmetric (class-dependent) noise, no standard error across noise draws within a split. The brief's must-cite works (Co-teaching, Han et al. 2018; confident learning, Northcutt et al. 2021; Song et al. TNNLS survey) are literature only; no code or data in the repo for them.
- Scope limits from the brief: two small sklearn datasets, linear model and one MLP; do not claim scaling to deep nets or large data.
- `fit_seconds` is in the file but timings are single measurements on an unknown machine; avoid cost claims beyond "filter is about 3-5x the cost of logreg" (digits ~0.06 s vs 0.013 s), and use with care.
- Quirk: `flip()` returns `noisy & True` (a no-op; harmless). Realised noise rate differs from nominal (e.g. digits 0.2 gives n_noisy 229-259 of 1257, i.e. 18-21%).
- `run.log` is not a training log, so nothing records the actual execution date, library versions or the command used.
- `.scriptorium/scout_stats.py` is my helper script (not run; execution needed approval). It reads results/runs.jsonl and prints the per-cell means, sds and filter precision/recall; recipes in paper/sources.py should be written fresh.
