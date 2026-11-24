# Inventory

Repository root: `examples/demo`. Files present: `brief.md`, `README.md`, `scriptorium.toml`, `experiments/run.py`, `experiments/config.json`, `results/runs.jsonl`, `paper/sources.py` (empty template, only a commented example), `paper/cvpr.sty`, `paper/ieeenat_fullname.bst`. No figures, tables, notebooks, logs, checkpoints or other result files exist. The run is a demo (README: "a tiny research repository to try Scriptorium on").

## Research question and method

Question: does dropping training samples that out-of-fold predictions disagree with their given (noisy) label help a linear classifier under label noise, without a clean validation set or a noise-rate estimate?

Method ("filter"), implemented in `experiments/run.py`, function `main()`, lines 64-71:
1. Fit a standardized logistic regression (`logreg()`, line 35) with `StratifiedKFold(5, shuffle=True, random_state=seed)` and `cross_val_predict` on the noisy training labels.
2. `keep = oof == ytr_noisy`; every sample whose out-of-fold prediction differs from its noisy label is dropped.
3. Refit `logreg()` on the kept samples and score on the clean test labels.

Noise model (`flip()`, line 27): symmetric. Each training label is selected with probability `rate` (independent Bernoulli draw from `np.random.default_rng(seed)`) and replaced by a label drawn uniformly from the other classes. Test labels are never corrupted. The returned `is_noisy` mask is exactly the set of flipped samples (the `noisy & True` is a no-op).

## Datasets

Both are scikit-learn built-ins, loaded in `run.py` line 24 (`LOADERS`); no files are downloaded or stored. Selected by `datasets` in `experiments/config.json`.
- `digits` (`load_digits`): 10 classes, 8x8 images as 64 features. From the result file: n_train 1257, n_test 540 (1797 total).
- `breast_cancer` (`load_breast_cancer`): 2 classes. From the result file: n_train 398, n_test 171 (569 total). Feature count (30) is not stated in any file here; it is a property of the scikit-learn loader.
- Split: `train_test_split(test_size=0.3, stratify=y, random_state=seed)`, so the split changes with the seed. No separate validation set; the filter uses cross-validation inside the training set.
- Noise is added to training labels only.

## Baselines and ablations

Names in the `method` field of `results/runs.jsonl`:
- `logreg`: standardized logistic regression (`C=1.0`, `max_iter=5000`) trained on the noisy labels. Baseline, and the model the filter wraps.
- `mlp`: `StandardScaler` + `MLPClassifier`, one hidden layer of 64 units, `max_iter=500`, `random_state=seed`, other sklearn defaults, trained on the noisy labels. The "larger model" in the brief.
- `filter`: ours (above).
- No ablations (no varying of fold count, `C`, hidden size, or filter variants). No clean-label oracle baseline (training on the true labels is not run). The 0% noise condition acts as the clean reference. No other noise-robust methods (co-teaching, confident learning) are run, although the brief says to cite them.

## Result files

- `results/runs.jsonl`: JSON lines, 90 records, written by `experiments/run.py` (the README says it need not be rerun). One record per (dataset, noise, seed, method): 2 datasets x 3 noise rates x 5 seeds x 3 methods = 90. All cells are complete (verified: 90 lines; the breast_cancer, noise 0.4, seed 0 triple is present). Seeds 0-4, so n = 5 per cell. Fields:
  - `dataset`: `digits` or `breast_cancer`.
  - `noise`: symmetric label-flip rate on training labels, 0.0, 0.2 or 0.4 (a fraction, not a percent).
  - `seed`: 0-4. It sets the split, the noise draw, the CV folds and the MLP initialization. All three methods share the same split and noisy labels within a seed.
  - `n_train`, `n_test`: sample counts.
  - `n_noisy`: number of training labels actually flipped (realized, so it deviates from `noise * n_train`). Example: breast_cancer, noise 0.4, seed 0 has n_noisy 142 of 398.
  - `method`: `logreg`, `mlp` or `filter`.
  - `test_acc`: accuracy (fraction in [0,1]) on the clean test split.
  - `fit_seconds`: wall-clock fit time. For `filter` it includes the 5-fold CV and the refit. Machine and load are unknown, so treat as indicative only.
  - `n_dropped` (`filter` rows only): number of training samples removed.
  - `n_dropped_noisy` (`filter` rows only): of those dropped, how many were actually flipped. Precision of the filter is `n_dropped_noisy / n_dropped`. Recall is `n_dropped_noisy / n_noisy` (undefined when `n_noisy = 0`).
  - Observed at noise 0.0: the filter still drops samples (digits seed 0: `n_dropped` 42, `n_dropped_noisy` 0) and its test_acc is lower than logreg there (0.965 vs 0.972 in that one seed).
  - Observed in one seed (breast_cancer, noise 0.4, seed 0): logreg 0.865, mlp 0.673, filter 0.895; `n_dropped` 159, `n_dropped_noisy` 114. These are single-record observations, not summaries. No aggregate has been computed.
- `.scriptorium/*` (`state.json`, `events.jsonl`, `run.log`, `lock.json`, `history.git/`): tool bookkeeping, not results. Not read for numbers.

## Settings the paper may report

`experiments/config.json` (read by `run.py` as `CFG`):
- `datasets`: `["digits", "breast_cancer"]`
- `noise_rates`: `[0.0, 0.2, 0.4]`
- `seeds`: `[0, 1, 2, 3, 4]`
- `test_fraction`: 0.3
- `logreg_C`: 1.0
- `mlp_hidden`: 64
- `mlp_max_iter`: 500
- `filter_folds`: 5

Hard-coded in `run.py` (not in config): `LogisticRegression(max_iter=5000)`, `StandardScaler` in every model, stratified splits and folds, MLP `random_state=seed`, symmetric noise with a uniform choice among the other classes. The sklearn version is not recorded anywhere.

`scriptorium.toml`: venue CVPR 2026 workshop, 4 main-text pages, template `cvpr`, review mode (anonymous), author "Demo Author". It is not an experimental setting.

## Existing figures or tables

None. `paper/` holds only `cvpr.sty`, `ieeenat_fullname.bst` and `sources.py` (no recipes yet; no `.tex`, no `.bib`).

## Gaps

- "Recovers most of the accuracy that noise costs": the data support computing it (accuracy of `filter` against `logreg` and against the 0% noise `logreg`, per dataset and noise rate), but a "recovered fraction" must be defined by the authors. No clean-label reference at the same split exists beyond the 0% condition.
- "Most dropped samples are truly mislabeled": supported by `n_dropped_noisy / n_dropped` for noisy conditions. At 0% noise precision is 0 by definition (nothing is mislabeled), so report precision at 0.2 and 0.4 only. Only precision and recall can be computed; there is no per-sample record of which samples were dropped.
- "Beats an MLP": `mlp` rows exist for every cell. A comparison on the shared (dataset, noise, seed) triples is possible (n = 5 per cell). No significance tests exist. With five seeds, power is low. Whether it holds on both datasets and both noise levels is untested until computed.
- "Costs little when labels are clean": the 0% noise rows are the evidence. In the one record seen, the filter drops 42 clean digits samples and loses accuracy relative to logreg. The size of the cost is not aggregated and must be computed before the claim is worded.
- Scope: two small sklearn datasets, linear model plus one small MLP, one noise type (symmetric), no scaling or deep-network experiment. The brief itself forbids claiming scaling.
- Missing comparisons the brief asks to cite but the repository cannot support with data: co-teaching, confident learning, and the Song et al. survey are not run (no code or results). They can be cited as related work only.
- No ablation over folds, `C`, or MLP size; MLP settings are untuned, and it is not stated whether the MLP converged within `max_iter=500` (sklearn ConvergenceWarning not logged). The MLP's poor accuracy under heavy noise may reflect memorization, but no file tests that explanation.
- No variance beyond seeds: the split changes with the seed, so seed variance mixes split and noise variance. Realized noise rate varies per seed (see `n_noisy`).
- `paper/sources.py` has no recipes yet. Every number printed in the paper needs one reading `results/runs.jsonl` or `experiments/config.json`.
