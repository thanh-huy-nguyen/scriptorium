# Experimental setup (each fact quoted from its source file)

## baselines

- The logreg baseline is logistic regression with inverse regularization C=1.0 and at most 5000 iterations, trained on the noisy labels. (`experiments/run.py`: "LogisticRegression(C=CFG["logreg_C"], max_iter=5000)")
- The logistic regression regularization constant C is 1.0. (`experiments/config.json`: ""logreg_C": 1.0")
- The mlp baseline is a scikit-learn MLPClassifier with one hidden layer, trained on the noisy labels after standardization, with random_state equal to the seed and other defaults. (`experiments/run.py`: "MLPClassifier(hidden_layer_sizes=(CFG["mlp_hidden"],)")
- The MLP hidden layer has 64 units and is trained for at most 500 iterations. (`experiments/config.json`: ""mlp_hidden": 64")
- The MLP maximum number of iterations is 500. (`experiments/config.json`: ""mlp_max_iter": 500")

## data

- Experiments use two scikit-learn built-in datasets, digits and breast_cancer. (`experiments/run.py`: "LOADERS = {"digits": load_digits, "breast_cancer": load_breast_cancer}")
- The datasets run are digits and breast_cancer, as listed in the configuration. (`experiments/config.json`: ""datasets": ["digits", "breast_cancer"]")
- Symmetric label noise is added: each training label is flipped with probability equal to the noise rate, to a class drawn uniformly from the other classes. (`experiments/run.py`: "y[i] = rng.choice([c for c in range(n_classes) if c != y[i]])")
- Flip decisions are independent Bernoulli draws per training sample from a NumPy generator seeded with the run seed. (`experiments/run.py`: "noisy = rng.random(len(y)) < rate")
- Noise is applied to training labels only; test labels stay clean and are used for scoring. (`experiments/run.py`: "ytr_noisy, is_noisy = flip(ytr, rate, k, rng)")
- Noise rates are 0%, 20% and 40%. (`experiments/config.json`: ""noise_rates": [0.0, 0.2, 0.4]")

## evaluation

- One record is written per dataset, noise rate, seed and method to results/runs.jsonl. (`experiments/run.py`: "out = ROOT / "results" / "runs.jsonl"")

## metrics

- The main metric is accuracy on the clean test split. (`experiments/run.py`: ""test_acc": float(m.score(Xte, yte))")
- For the filter, the number of dropped samples and how many of them were truly flipped are recorded per run. (`experiments/run.py`: ""n_dropped_noisy": int((dropped & is_noisy).sum())")
- Wall-clock fit time is recorded per method; for the filter it includes cross-validation and the refit. (`experiments/run.py`: ""fit_seconds": time.time() - t")

## models

- The filter method gets out-of-fold predictions from logistic regression on the noisy training labels and keeps only samples whose prediction equals their noisy label. (`experiments/run.py`: "keep = oof == ytr_noisy")
- Out-of-fold predictions come from cross_val_predict with the same logistic regression pipeline. (`experiments/run.py`: "oof = cross_val_predict(logreg(), Xtr, ytr_noisy, cv=cv)")
- After dropping disagreeing samples, logistic regression is refit on the kept samples with their noisy labels. (`experiments/run.py`: "m = logreg().fit(Xtr[keep], ytr_noisy[keep])")
- The filter uses 5 stratified, shuffled folds seeded with the run seed. (`experiments/config.json`: ""filter_folds": 5")
- The filter needs neither a clean validation set nor a noise-rate estimate; it takes no noise-rate input. (`experiments/run.py`: "keep = oof == ytr_noisy")

## preprocessing

- Features are standardized with StandardScaler inside every model pipeline, fit on the (noisy-label) training data only. (`experiments/run.py`: "make_pipeline(StandardScaler(), LogisticRegression(")

## seeds

- Each configuration is run with five seeds, 0 to 4. (`experiments/config.json`: ""seeds": [0, 1, 2, 3, 4]")
- The seed sets the train/test split, the noise draw, the cross-validation folds and the MLP initialization; all methods share split and noisy labels within a seed. (`experiments/run.py`: "rng = np.random.default_rng(seed)")

## splits

- Each dataset is split into 70% train and 30% test, stratified by class, with the split seed equal to the run seed. (`experiments/run.py`: "test_size=CFG["test_fraction"], stratify=y")
- The test fraction is 0.3. (`experiments/config.json`: ""test_fraction": 0.3")
- No separate validation set is used; the filter uses cross-validation inside the training set. (`experiments/run.py`: "cv = StratifiedKFold(CFG["filter_folds"], shuffle=True, random_state=seed)")

## Not found in the repository

- the scikit-learn and numpy versions are not recorded anywhere
- hardware (CPU/GPU, machine) is not stated; fit_seconds are indicative only
- dataset sizes are not set in code; n_train and n_test appear only in results/runs.jsonl (digits 1257/540, breast_cancer 398/171)
- no ablations over folds, C or MLP size; MLP hyperparameters were not tuned and convergence within max_iter=500 is not logged
- co-teaching, confident learning and other noise-robust methods are not run; there is no clean-label oracle baseline
- no significance tests or aggregation code exist in the repository; only per-run records
