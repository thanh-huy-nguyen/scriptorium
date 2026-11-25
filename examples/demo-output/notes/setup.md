# Experimental setup (each fact quoted from its source file)

## baselines

- The linear baseline is a logistic regression trained on all noisy training labels. (`experiments/run.py`: "m = logreg().fit(Xtr, ytr_noisy)")
- The larger baseline is a scikit-learn multilayer perceptron on standardized features, with all arguments other than hidden layer size, maximum iterations and random state left at library defaults. (`experiments/run.py`: "m = make_pipeline(StandardScaler(), MLPClassifier(hidden_layer_sizes=(CFG["mlp_hidden"],),")
- The multilayer perceptron has one hidden layer with 64 units. (`experiments/config.json`: ""mlp_hidden": 64")
- The multilayer perceptron is trained on the same noisy training labels as the logistic regression baseline, without filtering. (`experiments/run.py`: "m.fit(Xtr, ytr_noisy)")

## data

- Experiments use the digits and breast cancer datasets. (`experiments/config.json`: ""datasets": ["digits", "breast_cancer"]")
- Both datasets are loaded with the scikit-learn functions load_digits and load_breast_cancer. (`experiments/run.py`: "LOADERS = {"digits": load_digits, "breast_cancer": load_breast_cancer}")
- The training and test set sizes of every run are saved with its result. (`experiments/run.py`: ""n_train": int(len(ytr)), "n_test": int(len(yte))")

## evaluation

- All three methods are run for every combination of dataset, noise rate and seed, sharing the same split and noisy labels within each combination. (`experiments/run.py`: "for rate in CFG["noise_rates"]:")

## metrics

- Methods are compared by classification accuracy on the clean test labels. (`experiments/run.py`: ""method": "filter", "test_acc": float(m.score(Xte, yte))")
- For the filter, we record the number of dropped training samples and how many of them had a corrupted label. (`experiments/run.py`: ""n_dropped_noisy": int((dropped & is_noisy).sum())")

## models

- Every logistic regression uses an inverse regularization strength C of 1.0. (`experiments/config.json`: ""logreg_C": 1.0")
- The filter uses 5-fold cross-validation. (`experiments/config.json`: ""filter_folds": 5")
- Each training sample receives a predicted class from a logistic regression fit on the folds that exclude it. (`experiments/run.py`: "oof = cross_val_predict(logreg(), Xtr, ytr_noisy, cv=cv)")
- A training sample is kept only if its out-of-fold predicted class equals its noisy label, with no confidence threshold, noise-rate estimate or clean data. (`experiments/run.py`: "keep = oof == ytr_noisy")

## other

- The experiments are implemented with scikit-learn and NumPy. (`experiments/run.py`: "Needs scikit-learn and numpy.")

## preprocessing

- Logistic regression is preceded by feature standardization fit on the data that the classifier is trained on, including within each cross-validation fold and again before the filter's refit. (`experiments/run.py`: "return make_pipeline(StandardScaler(), LogisticRegression(C=CFG["logreg_C"], max_iter=5000))")
- Label noise is studied at rates of 0, 0.2 and 0.4. (`experiments/config.json`: ""noise_rates": [0.0, 0.2, 0.4]")
- Each training label is selected for corruption independently with probability equal to the noise rate, so the realized number of noisy labels varies between runs. (`experiments/run.py`: "noisy = rng.random(len(y)) < rate")
- A selected label is replaced by a class drawn uniformly at random from the other classes (symmetric label noise). (`experiments/run.py`: "y[i] = rng.choice([c for c in range(n_classes) if c != y[i]])")
- Noise is applied to the training labels only, and the test labels stay clean. (`experiments/run.py`: "ytr_noisy, is_noisy = flip(ytr, rate, k, rng)")

## seeds

- Each setting is repeated with five seeds, 0 to 4. (`experiments/config.json`: ""seeds": [0, 1, 2, 3, 4]")
- The run seed initializes the NumPy random generator that draws the label noise, and the generator is re-created for each noise rate. (`experiments/run.py`: "rng = np.random.default_rng(seed)")
- The run seed also sets the train/test split, so for a given dataset and seed the split is the same across noise rates. (`experiments/run.py`: "stratify=y,
                                                      random_state=seed)")
- The run seed sets the random state of the multilayer perceptron. (`experiments/run.py`: "max_iter=CFG["mlp_max_iter"], random_state=seed))")

## splits

- A fraction of 0.3 of each dataset is held out for testing. (`experiments/config.json`: ""test_fraction": 0.3")
- Each seed draws a random train/test split, stratified on the clean labels, with no separate validation set. (`experiments/run.py`: "Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=CFG["test_fraction"], stratify=y,")
- The filter's cross-validation folds are shuffled with the run seed and stratified on the noisy training labels. (`experiments/run.py`: "cv = StratifiedKFold(CFG["filter_folds"], shuffle=True, random_state=seed)")

## training

- Every logistic regression is fit with at most 5000 solver iterations, and its remaining settings are scikit-learn defaults. (`experiments/run.py`: "LogisticRegression(C=CFG["logreg_C"], max_iter=5000)")
- The multilayer perceptron is trained for at most 500 iterations. (`experiments/config.json`: ""mlp_max_iter": 500")
- After a single filtering pass, a new standardization and logistic regression pipeline is fit on the kept samples with their noisy labels. (`experiments/run.py`: "m = logreg().fit(Xtr[keep], ytr_noisy[keep])")

## Not found in the repository

- scikit-learn, NumPy and Python versions are not stated, and there is no requirements or environment file; library defaults (logistic regression solver and penalty; MLP activation, optimizer, learning rate, batch size, L2 penalty and stopping rule) therefore cannot be pinned to values from the repository
- hardware is not stated, although fit_seconds is recorded in the results
- the number of classes and features of each dataset is not stated or saved by any repository file
- dataset sizes are not set in code or config; they follow from the loaders and test_fraction and appear only as n_train and n_test in results/runs.jsonl, so printed sizes need recipes
- how C, the number of folds, the MLP hidden size, the iteration limits and the noise rates were chosen is not stated; the code performs no tuning and uses no validation set
- convergence status and warnings for logistic regression and the MLP are not recorded
- the aggregation across seeds (mean, spread) and any statistical test are not implemented in experiments/run.py, which writes only per-run records
- seeds re-split the same data, so test sets can overlap between seeds and runs are not independent samples
- co-teaching and confident learning, named in brief.md as must-cite work, are not implemented or run
- run_console.log is empty and no run date is recorded, so there is no log of the run that produced results/runs.jsonl
- no disagreement was found between experiments/config.json and experiments/run.py; the logistic regression iteration limit of 5000 is hard-coded in run.py and absent from the config
- README.md gives the path examples/demo, which does not match the layout of this repository
