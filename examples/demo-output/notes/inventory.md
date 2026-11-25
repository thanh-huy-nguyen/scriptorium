# Inventory

All paths are relative to the repository root. Approximate values in this file (marked "approx.") were worked out by
hand from `results/runs.jsonl` to find gaps. Do not print them; every printed number needs a recipe in
`paper/sources.py`.

## Files in the repository

| Path | What it is |
|---|---|
| `brief.md` | Authors' claims, must-cite work, scope limit |
| `README.md` | Study description; says output is already in `results/runs.jsonl` (its `cd examples/demo` path does not match this folder) |
| `experiments/run.py` | The whole implementation: data loading, noise, three methods, output (77 lines) |
| `experiments/config.json` | All experiment settings |
| `results/runs.jsonl` | The only result file (90 records) |
| `run_console.log` | Empty (0 bytes) |
| `scriptorium.toml` | Paper settings: CVPR template, `mode = "review"` (anonymous), `page_limit = 4`, figure theme `harbor` |
| `paper/cvpr.sty`, `paper/ieeenat_fullname.bst` | Venue style files |
| `paper/sources.py` | Recipe file; only a commented example, no recipes yet |

There is no `main.tex`, no `refs.bib`, and no requirements or environment file.

## Research question and method

Question (brief.md): does dropping the training samples whose out-of-fold prediction disagrees with their given label,
then refitting, help a linear classifier under label noise? Implementation is entirely in `experiments/run.py`
(`main()`, lines 39-73). Per (dataset, noise rate, seed): `train_test_split` with `test_size=test_fraction`,
`stratify=y` (clean labels), `random_state=seed`; `flip(ytr, rate, k, rng)` (lines 27-32) with
`rng = np.random.default_rng(seed)` selects each **training** label independently with probability `rate` and replaces
it with a uniformly chosen *different* class (symmetric noise; test labels stay clean). `logreg()` (lines 35-36) is
`StandardScaler()` + `LogisticRegression(C=logreg_C, max_iter=5000)`. Method `filter` (lines 63-71):
`StratifiedKFold(filter_folds, shuffle=True, random_state=seed)` stratified on the noisy labels;
`cross_val_predict(logreg(), Xtr, ytr_noisy, cv=cv)` gives hard out-of-fold predictions; `keep = oof == ytr_noisy`;
a fresh `logreg()` (scaler refit too) is fit on the kept samples and scored on the clean test set. One filtering pass,
no confidence threshold, no per-class threshold. The filter reads neither the noise rate nor any clean data;
`is_noisy` is used only to count `n_dropped_noisy`.

## Datasets

Both come from `sklearn.datasets` (`LOADERS`, `run.py` line 24; listed in `config.json` key `datasets`). Split:
random stratified train/test, test fraction 0.3, redrawn for every seed. No validation set. Sizes are from the result
records.

| Key in results | Loader | n_train | n_test | Total (train + test) |
|---|---|---|---|---|
| `digits` | `load_digits` | 1257 | 540 | 1797 |
| `breast_cancer` | `load_breast_cancer` | 398 | 171 | 569 |

Number of classes and features is **not stated in any repository file**. `run.py` computes `k = len(np.unique(y))` but
does not save it. (From scikit-learn's documentation, not this repo: digits has 10 classes and 64 features;
breast_cancer has 2 classes and 30 features.)

Realized noisy training labels (`n_noisy`, min-max over 5 seeds; it varies because flipping is Bernoulli):

| Dataset | noise 0.0 | noise 0.2 | noise 0.4 |
|---|---|---|---|
| digits | 0 | 229-259 | 487-502 |
| breast_cancer | 0 | 65-83 | 141-168 |

## Baselines and ablations

| `method` value | Meaning | Role |
|---|---|---|
| `filter` | Out-of-fold filtering + refit logistic regression | Ours |
| `logreg` | Logistic regression on standardized features, noisy labels | Baseline; at `noise` = 0.0 it is the clean-label reference |
| `mlp` | `StandardScaler` + `MLPClassifier(hidden_layer_sizes=(64,), max_iter=500, random_state=seed)`, noisy labels | "Larger model" baseline; all other MLP arguments are library defaults (nothing tuned) |

Ablations: **none**. No variation of fold count, C, MLP size, noise type, or filtering rule.

## Result files

- `results/runs.jsonl`: JSON Lines, written by `experiments/run.py` (overwritten on each run). 90 records =
  2 datasets x 3 noise rates x 5 seeds (0-4) x 3 methods; the grid is complete with no duplicates. This is the only
  result file and the final one; there are no exploratory, debug or old runs.
  - One record = one method on one (dataset, noise, seed).
  - `dataset` (str: `digits`, `breast_cancer`)
  - `noise` (float: 0.0, 0.2, 0.4; requested flip probability)
  - `seed` (int 0-4; sets split, noise draw, CV folds and MLP initialization)
  - `n_train`, `n_test` (sample counts); `n_noisy` (training labels actually flipped)
  - `method` (str, see above)
  - `test_acc` (fraction in [0, 1] on clean test labels)
  - `fit_seconds` (wall-clock seconds). The timer is read after `test_acc` is computed, so it includes test scoring
    for all methods; for `filter` it also includes cross-validation and the refit.
  - `filter` records only: `n_dropped` (training samples removed), `n_dropped_noisy` (removed samples whose label had
    been flipped)
  - Records are ordered by dataset, noise, seed, then logreg, mlp, filter.
  - Pairing: for a fixed (dataset, noise, seed), all three methods share the split and noisy labels. For a fixed
    (dataset, seed), the split is also the same across noise rates.

## Settings the paper may report

| Setting | Value | Source (file, key or line) |
|---|---|---|
| Datasets | digits, breast_cancer | `experiments/config.json` `datasets` |
| Noise rates | 0.0, 0.2, 0.4 | `config.json` `noise_rates` |
| Seeds | 0-4 (5) | `config.json` `seeds` |
| Test fraction | 0.3 | `config.json` `test_fraction` |
| Logistic regression C | 1.0 | `config.json` `logreg_C` |
| Logistic regression max iterations | 5000 | `run.py` line 36 (hard-coded) |
| MLP hidden units (one layer) | 64 | `config.json` `mlp_hidden` |
| MLP max iterations | 500 | `config.json` `mlp_max_iter` |
| Filter folds K | 5 | `config.json` `filter_folds` |
| Noise model | symmetric, training labels only | `run.py` `flip`, lines 27-32 |

Not recorded: scikit-learn and numpy versions, solver and penalty (library defaults), hardware, run date, convergence
warnings.

## Existing figures or tables

None. No images, plotting scripts, or table files in the repository.

## Gaps

### Brief claims against the data

1. **"The filter recovers most of the accuracy that label noise costs a linear model."** Supported only in part.
   Recovered share = (filter - noisy logreg) / (clean logreg - noisy logreg), from seed means, approx.: digits 20%:
   0.78; digits 40%: 0.68; breast_cancer 20%: 0.66; **breast_cancer 40%: about 0.22** (per seed about 0.09 to 0.35).
   "Most" is false for breast_cancer at 40% noise. Filter beats noisy logreg in 19 of 20 noisy (dataset, rate, seed)
   runs; the exception is breast_cancer, 0.2, seed 3 (filter 0.9591, logreg 0.9708).
2. **"Most of the samples it drops are truly mislabeled."** Supported for noisy settings: `n_dropped_noisy /
   n_dropped` is above 0.5 in all 20 noisy runs (approx. range 0.61 to 0.81). False by construction at noise 0.0,
   where the filter still drops samples (digits 34-49 of 1257; breast_cancer 5-9 of 398) and none are mislabeled.
   The claim must be scoped to noisy training sets. Recall (`n_dropped_noisy / n_noisy`) is also computable (approx.
   0.97-0.99 digits; 0.89-0.96 breast_cancer 20%; 0.70-0.88 breast_cancer 40%).
3. **"It beats a larger model (an MLP) trained on the same noisy labels."** Filter is above MLP in all 20 noisy runs.
   At noise 0.0 it is not: digits, MLP above filter in 5 of 5 seeds; breast_cancer, filter above in 1 seed, tied in 3,
   below in 1. Plain `logreg` is also above `mlp` in all 20 noisy runs, so the gap to the MLP does not isolate the
   effect of filtering. The MLP is a single untuned configuration, and there is no MLP + filter run. Parameter counts
   are not recorded.
4. **"It costs little when the labels are clean."** Supported: at noise 0.0 the mean filter minus logreg accuracy is
   approx. -0.2 points (digits; filter lower in 2 seeds, higher in 3) and -0.1 points (breast_cancer; tied in 4 seeds,
   lower in 1).
- "Needs no clean validation set and no noise-rate estimate" (brief, idea paragraph): true of the code (a design
  property, not a measured result). C and K are fixed in the config; the repository does not show how they were chosen.

### Missing evidence

- **Must-cite methods were not run:** no co-teaching and no confident learning results, so no comparison with them can
  be claimed. The `filter` method is close in kind to out-of-fold classification filtering and to confident learning
  (cross-validated predictions used to prune labels), so novelty wording needs care and a related-work check.
- No controls: no random dropping of the same number of samples, no oracle that drops exactly the flipped samples.
  The clean-label reference is `logreg` at noise 0.0.
- No ablation of K, C, number of filtering passes, or a no-refit variant.
- Only symmetric (uniform) noise; no class-dependent or instance-dependent noise; only the rates 0.0, 0.2, 0.4.
- Only two small datasets and linear or small MLP models. brief.md forbids claims about deep networks or large data.
- No statistical tests stored. n = 5 seeds per cell. Seeds are random re-splits of the same data, so test sets overlap
  across seeds and the 5 runs are not independent samples.
- Large seed spread at breast_cancer 40% (`test_acc`: logreg 0.690 to 0.889; filter 0.737 to 0.924).
- Filtering removes a large share of the training set at 40% noise (approx. half for digits, 40-47% for
  breast_cancer).
- No predictions, per-sample outputs, dropped-sample indices, per-class drop counts or learned weights are saved, so
  the result file supports no per-class analysis and no qualitative figure of dropped samples.
- `fit_seconds` exists but hardware is not recorded; the brief makes no runtime claim.

### Inconsistencies

None found between `config.json`, `run.py`, and the grid, sizes and fields in `results/runs.jsonl`. `run_console.log`
is empty, so there is no log of the run that produced the file.
