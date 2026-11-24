# Experimental setup (each fact quoted from its source file)

## baselines

- The MLP baseline has one hidden layer of 64 units, at most 500 iterations, scikit-learn defaults otherwise, and is trained on the noisy labels with the run seed as random state. (`experiments/run.py`: "MLPClassifier(hidden_layer_sizes=(CFG["mlp_hidden"],),")
- The MLP has 64 hidden units and a 500-iteration cap. (`experiments/config.json`: ""mlp_max_iter": 500")
- The no-filter baseline is the same logistic regression trained directly on the noisy labels. (`experiments/run.py`: "m = logreg().fit(Xtr, ytr_noisy)")

## data

- Experiments use two scikit-learn built-in datasets: digits (10 classes) and breast cancer (2 classes). (`experiments/run.py`: "LOADERS = {"digits": load_digits, "breast_cancer": load_breast_cancer}")
- The dataset list in the config is digits and breast_cancer. (`experiments/config.json`: ""datasets": ["digits", "breast_cancer"]")
- Label noise is symmetric: each training label is flipped independently with probability equal to the noise rate, to a class drawn uniformly from the other classes; test labels stay clean. (`experiments/run.py`: "y[i] = rng.choice([c for c in range(n_classes) if c != y[i]])")
- Each flip is selected by an independent uniform draw below the noise rate. (`experiments/run.py`: "noisy = rng.random(len(y)) < rate")
- Noise rates are 0%, 20% and 40%. (`experiments/config.json`: ""noise_rates": [0.0, 0.2, 0.4]")

## evaluation

- The grid is 2 datasets x 3 noise rates x 5 seeds x 3 methods, one record per run. (`experiments/run.py`: "Writes one JSON line per (dataset, noise rate, seed, method)")

## metrics

- The main metric is accuracy on the clean held-out test labels. (`experiments/run.py`: ""test_acc": float(m.score(Xte, yte))")
- For the filter, the number of dropped samples and how many of them were truly flipped are recorded, which gives the precision and recall of the filter. (`experiments/run.py`: ""n_dropped_noisy": int((dropped & is_noisy).sum())")
- Fit time is wall-clock seconds; for the filter it includes cross-validation and the refit. (`experiments/run.py`: ""fit_seconds": time.time() - t")

## models

- Logistic regression uses L2 regularization strength C = 1.0 (scikit-learn default penalty) and at most 5000 iterations, after standardization. (`experiments/run.py`: "LogisticRegression(C=CFG["logreg_C"], max_iter=5000)")
- The logistic regression C is 1.0. (`experiments/config.json`: ""logreg_C": 1.0")
- The filter computes out-of-fold predictions with 5-fold stratified, shuffled cross-validation of the logistic regression on the noisy training labels. (`experiments/run.py`: "cv = StratifiedKFold(CFG["filter_folds"], shuffle=True, random_state=seed)")
- Out-of-fold predictions come from cross_val_predict on the noisy labels. (`experiments/run.py`: "oof = cross_val_predict(logreg(), Xtr, ytr_noisy, cv=cv)")
- The filter drops every training sample whose out-of-fold prediction differs from its noisy label, then refits the logistic regression on the remaining samples; it uses no clean labels or noise-rate estimate. (`experiments/run.py`: "keep = oof == ytr_noisy")
- The final model is refit on the kept samples only. (`experiments/run.py`: "m = logreg().fit(Xtr[keep], ytr_noisy[keep])")
- The number of filter folds is 5. (`experiments/config.json`: ""filter_folds": 5")

## other

- The code uses scikit-learn and numpy only. (`experiments/run.py`: "Needs scikit-learn and numpy.")

## preprocessing

- All models standardize features with a StandardScaler fit inside the pipeline on the (noisy-label) training data. (`experiments/run.py`: "make_pipeline(StandardScaler(), LogisticRegression(")

## seeds

- Each configuration is run with 5 seeds (0 to 4). (`experiments/config.json`: ""seeds": [0, 1, 2, 3, 4]")
- The seed sets the train/test split, the noise draw, the cross-validation folds and the MLP initialization, so methods are paired within a seed. (`experiments/run.py`: "rng = np.random.default_rng(seed)")

## splits

- Each dataset is split into 70% train and 30% test, stratified by class, with the split seed set to the run seed, so the split changes with the seed. (`experiments/run.py`: "train_test_split(X, y, test_size=CFG["test_fraction"], stratify=y,")
- The test fraction is 0.3. (`experiments/config.json`: ""test_fraction": 0.3")
- No validation set is used and no hyperparameters are tuned; all settings are fixed in the config. (`experiments/config.json`: ""filter_folds": 5")

## Not found in the repository

- Library versions (scikit-learn, numpy, Python) are not recorded anywhere.
- No hardware (CPU, GPU, machine) is stated, so fit_seconds were taken on an unrecorded machine.
- Dataset sizes are not stated in any code or config; they come from scikit-learn (digits 1797 samples, breast cancer 569) and from n_train and n_test in results/runs.jsonl.
- The MLP may not have converged within 500 iterations; no convergence flag is logged.
- Co-teaching and confident learning are not run, and there is no oracle clean-label baseline; the 0% noise logreg runs are the nearest stand-in.
- No ablation of K, C or the MLP size and no hyperparameter tuning procedure exist.
- Whether results/runs.jsonl matches a fresh run of run.py was not checked.
