# Related work (verified entries in paper/refs.bib)

Cite only these keys. No numbers from these papers are used. Arpit et al. (memorization) was not found in the databases and is not in the bibliography; cite `zhang2021understanding` for memorization.

## noisy_label_surveys

- `song2023learning`: survey of learning with noisy labels for deep networks; reviews 62 robust training methods in five groups and discusses noise-rate estimation and evaluation practice. Must-cite. Ours: a measurement of one cleansing rule for a linear model, not a survey.
- `frenay2014classification`: survey of label noise in classification for classical classifiers: taxonomy, consequences, and robust, cleansing and tolerant algorithms. Ours: places the filter among the cleansing methods.

## sample_selection

- `han2018coteaching`: co-teaching; two deep networks each pass their small-loss samples to the peer. Must-cite. Ours: relies on deep-network training dynamics; we use a linear model's out-of-fold prediction and do not compare against it.
- `yu2019how`: Co-teaching+; keeps samples on which the two networks disagree, then selects small-loss ones. Ours: not compared.
- `pleiss2020identifying`: Area Under the Margin; ranks samples by training dynamics to find mislabeled data. Ours: not compared; no training dynamics needed.

## cv_filtering

- `brodley1999identifying`: uses learning algorithms as noise filters (single algorithm, majority vote, consensus) to remove mislabeled instances. Closest work. Ours: our rule is the single-algorithm filter with logistic regression and plain argmax disagreement; we add a checkable measurement of precision, recall, accuracy gain and clean-label cost, not a new idea.
- `northcutt2021confident`: confident learning; prunes label errors from out-of-sample predicted probabilities with per-class thresholds and noise-count estimation, under class-conditional noise. Must-cite. Ours: no thresholds, no noise-count estimation; not compared in experiments.
- `lallich2002improving`: removing or relabeling mislabeled instances to improve classification. The abstract could not be fetched, so cite only for the general topic (removal or relabeling of mislabeled instances), with no specific claim.

## noise_models

- `patrini2017making`: loss correction for deep networks with a matrix of class-corruption probabilities, which it can also estimate. Ours: needs no transition matrix; the loss is unchanged.
- `ghosh2017robust`: sufficient conditions for noise-tolerant multiclass losses; the mean absolute error loss satisfies them. Ours: the model and loss are unchanged.
- `bootkrajang2014learning`: label-noise robust kernel logistic regression that sets model complexity without a trusted validation set. Ours: no noise model inside the classifier.
- `lee2021individual`: logistic regression for binary classification with a nonparametric label-noise model with individual transition parameters. Ours: no noise model; multiclass and binary cases handled by plain logistic regression.

## memorization

- `zhang2021understanding`: large networks trained with stochastic gradient methods easily fit random labelings. Use only as context consistent with, but not a test of, the untuned MLP's drop under noise.

## Datasets, baselines and tools

- `pedregosa2012scikitlearn`: scikit-learn; source of the digits and breast cancer datasets (built-in loaders), logistic regression, MLPClassifier, StratifiedKFold, cross_val_predict and StandardScaler used in the experiments.
- Baselines (logistic regression, MLP) are scikit-learn models and have no separate citation; no other dataset or tool paper is needed.
