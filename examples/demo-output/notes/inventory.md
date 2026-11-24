# Inventory

Repository root: examples/demo. Files outside .scriptorium/ and paper/: README.md, brief.md, scriptorium.toml, experiments/run.py, experiments/config.json, results/runs.jsonl. paper/ holds only sources.py (empty template, no recipes yet). No figures, tables, notebooks, logs or other result files exist. No other notes (setup.md, numbers.md, ...) existed when this was written; only style.md.

## Research question and method

Question: does dropping training samples whose out-of-fold prediction disagrees with their (noisy) label, then refitting, recover the accuracy that label noise costs a logistic regression? Secondary questions from brief.md: how many dropped samples are truly mislabeled, how the filter compares with an MLP trained on the same noisy labels, and what it costs on clean labels.

Method ("filter", the proposed method) is implemented in `experiments/run.py`, function `main()`, lines 64-71:
1. `StratifiedKFold(filter_folds=5, shuffle=True, random_state=seed)`.
2. `cross_val_predict(logreg(), Xtr, ytr_noisy, cv=cv)` gives the out-of-fold prediction `oof`.
3. `keep = oof == ytr_noisy`; every sample with `oof != noisy label` is dropped.
4. Refit `logreg()` on `Xtr[keep], ytr_noisy[keep]`; score on the clean test set.
`logreg()` = `make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000))`. No clean validation set and no noise-rate estimate are used (confirmed in code). Its `fit_seconds` includes the cross-validation and the refit.

Noise model, `flip()` (lines 27-32): each training label is selected with probability `rate` (independent Bernoulli), and a selected label is replaced by a class drawn uniformly from the other classes (symmetric noise). Test labels stay clean. `rng = np.random.default_rng(seed)`.

## Datasets

Both are scikit-learn built-ins, loaded by `LOADERS` in `experiments/run.py` (`load_digits`, `load_breast_cancer`). Split: `train_test_split(test_size=0.3, stratify=y, random_state=seed)`, so the split changes with the seed. No dataset size is stated in any file, but `n_train` and `n_test` in runs.jsonl give:
- `digits`: 10 classes, n_train 1257, n_test 540 (total 1797). Seen in the first records; confirm for all rows.
- `breast_cancer`: 2 classes, n_train 398, n_test 171 (total 569). Seen in one record (noise 0.4, seed 0). Class count (10 and 2) comes from sklearn, not from a file here.

## Baselines and ablations

Names in the `method` field of runs.jsonl:
- `logreg`: logistic regression on standardized features, trained on noisy labels, no filtering. Also the "no filter" ablation of the method.
- `mlp`: `MLPClassifier(hidden_layer_sizes=(64,), max_iter=500, random_state=seed)` after StandardScaler, trained on noisy labels. This is the "larger model" baseline in brief.md.
- `filter`: the proposed method.
No other baselines. Co-teaching and confident learning are must-cite in brief.md but are NOT run. There is no oracle baseline (training on clean labels). The 0% noise runs of `logreg` stand in for it. There are no ablations of K, C or the MLP size.

## Result files

- `results/runs.jsonl`: JSON Lines, 90 records, written by `experiments/run.py` (overwrites the whole file). One record is one (dataset, noise, seed, method) run. The grid is 2 datasets x 3 noise rates x 5 seeds x 3 methods = 90 (30 per method, 45 per dataset; the counts were checked with grep). This is the only result file, and it is the final one. Fields:
  - `dataset`: `digits` or `breast_cancer`.
  - `noise`: symmetric flip rate on training labels: 0.0, 0.2 or 0.4.
  - `seed`: 0-4. It sets the split, the noise draw, the CV folds and the MLP init.
  - `n_train`, `n_test`: sample counts after the 70/30 split.
  - `n_noisy`: number of training labels actually flipped (0 at noise 0.0). It is the same in all three methods for a given (dataset, noise, seed).
  - `method`: `logreg`, `mlp` or `filter`.
  - `test_acc`: accuracy in [0, 1] on the clean test labels. It is not a percentage.
  - `fit_seconds`: wall-clock fit time in seconds (for `filter`, CV plus refit).
  - `n_dropped`, `n_dropped_noisy` (only in `filter` records): the number of training samples dropped, and how many of them were truly flipped. Precision of the filter = `n_dropped_noisy / n_dropped`. Recall = `n_dropped_noisy / n_noisy`. Both are derived, not stored.
  Example: breast_cancer, noise 0.4, seed 0: logreg 0.865, mlp 0.673, filter 0.895 (n_dropped 159, n_dropped_noisy 114, n_noisy 142). These are single-run values, quoted only to show the format.
  Seeds: 5 (0-4) per cell. The seeds are paired across methods, since they share the split and the noisy labels.
  Caveat: at noise 0.0, `n_dropped_noisy` is 0 by construction, so precision is 0 whenever `n_dropped > 0` (the first digits record dropped 42 clean samples). At noise 0.0 "truly mislabeled" does not apply.

Nothing has been aggregated yet. No means, sds or tests exist in any file.

## Settings the paper may report

`experiments/config.json` (read by `run.py` as `CFG`):
- `datasets`: ["digits", "breast_cancer"]
- `noise_rates`: [0.0, 0.2, 0.4]
- `seeds`: [0, 1, 2, 3, 4]
- `test_fraction`: 0.3
- `logreg_C`: 1.0 (the logistic regression `max_iter=5000` and the StandardScaler are hardcoded in run.py)
- `mlp_hidden`: 64 (one hidden layer; `max_iter` is `mlp_max_iter` = 500; sklearn defaults otherwise: relu, adam)
- `mlp_max_iter`: 500
- `filter_folds`: 5
Hardcoded in run.py: stratified split and stratified, shuffled K-fold; symmetric uniform noise; scikit-learn and numpy only. The library versions are not recorded. No hyperparameters were tuned in any file. The MLP may not have converged at 500 iterations (no convergence flag is logged).
`scriptorium.toml`: paper title and a 4-page limit; no experiment settings.

## Existing figures or tables

None in the repository. `paper/` has only an empty `sources.py` template (`@source(key, means=...)`, `load(path)` relative to the repo root).

## Gaps

- Brief claim "recovers most of the accuracy that noise costs": supportable from `logreg` vs `filter` vs the 0.0-noise `logreg`, but needs aggregation. No file states the figure. Whether it holds on both datasets and both noise rates is unknown until computed.
- "Most dropped samples are truly mislabeled": supportable only from `n_dropped_noisy / n_dropped` at noise 0.2 and 0.4. The example above gives 114/159 (72%) at noise 0.4. Not checked elsewhere. At noise 0.0 precision is 0 by construction, and the filter drops clean samples (digits seed 0: 42 dropped).
- "Beats an MLP": data exist (`mlp` records). The MLP example above is much worse on breast_cancer at 0.4 noise, but the comparison on digits is not checked. Do not generalize beyond the MLP with 64 hidden units and these defaults. The MLP is at 0.0 noise slightly above `logreg` on digits seed 0, so the comparison may flip on clean data.
- "Costs little when clean": supportable from noise 0.0 `logreg` vs `filter`. In digits seed 0 the filter is lower (0.965 vs 0.972). Compute the mean difference per dataset.
- Only 5 seeds, 2 datasets and one noise type (symmetric). No class-dependent noise, no noise above 0.4, no other classifiers. Both datasets are small. Brief says not to claim scaling to deep networks or large data.
- No run of co-teaching or confident learning, so the paper can cite them but cannot compare against them.
- No per-class, per-fold or seed-level stored predictions. No hyperparameter sensitivity (K, C).
- `fit_seconds` is a single wall-clock timing, noisy, and was taken on an unrecorded machine.
- `runs.jsonl` was produced once by run.py. Whether it matches a fresh run was not checked (a rerun is not allowed here).
- The README says "about 20 agent sessions"; it is a demo repository, and no exploratory or old result files exist, so there is no final-versus-exploratory ambiguity.
