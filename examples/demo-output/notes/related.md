# Related work (verified keys; cite only these)

All 17 keys were added with `scriptorium cite add` and pass `scriptorium cite verify`. We did not run any method below except logistic regression, the MLP and our filter, so make no empirical claim against the others. Natarajan et al. (2013) could not be found by search and is not in the bibliography; do not cite it.

## noisy_label_surveys

- `song2023learning`: survey of deep learning with noisy labels (62 methods in five groups, noise-rate estimation, evaluation practice). Must-cite. Use it to frame the families: robust losses, correction, reweighting, sample selection.
- `frenay2014classification`: survey of label noise in classification with a taxonomy of noise types and of noise-robust, noise-cleansing and noise-tolerant algorithms. Our filter is a noise-cleansing method in this taxonomy.

## loss_correction_reweighting

- `patrini2017making`: loss correction for class-dependent noise using an estimated corruption matrix. Differs: needs the noise transition (or an estimate of it); our filter needs neither.
- `ren2018learning`: reweights examples by gradient direction on a small clean validation set. Differs: needs clean validation data; our filter uses none.
- `zhang2018generalized`: generalized cross entropy, a noise-robust loss that interpolates between MAE and cross entropy. Robust-loss family; background only.

## sample_selection

- `han2018coteaching`: co-teaching, two networks each select small-loss samples for the other. Must-cite. Differs: deep networks, needs the noise rate to set the keep ratio; our filter has no rate and no threshold. Not run here.
- `jiang2018mentornet`: MentorNet, a learned curriculum that weights samples of a student network. Another selection method for deep networks; not run.
- `li2020dividemix`: DivideMix, splits data into clean and noisy sets with a mixture model on per-sample loss and trains semi-supervised. Strong deep-network method; not run, and we make no claim against it.
- `northcutt2017learning`: Rank Pruning, binary classification with flipped labels that estimates the noise rates and prunes. Differs: estimates rates; ours does not.

## confident_learning

- `northcutt2021confident`: confident learning prunes samples using out-of-sample predicted probabilities and per-class thresholds, and estimates the joint noise distribution. Must-cite and the closest method. Differs: we keep only the argmax-disagreement rule of a linear model with no thresholds and no noise estimate; the two were not compared.

## mislabeled_data_filtering

- `brodley1999identifying`: uses learning algorithms as noise filters (single-algorithm, majority-vote, consensus) to find and remove mislabeled instances. Closest classical precedent. Differs: we study the single-linear-model rule, measure precision and recall against known flips, and measure what refitting buys against the noisy model and an MLP.
- `brodley1996identifying`: earlier version of the same idea, an ensemble under n-fold cross validation, with the final learner trained on the instances the filter classifies correctly. Same differences as above.
- `saez2016inffc`: INFFC, iterative ensemble noise filter with noise-sensitivity control. More elaborate filter; not run.

## memorization

- `zhang2016understanding`: large networks fit random labelings of the training data. Use to explain why the untuned MLP degrades under noise (it can fit flipped labels). Framing only; we did not test memorization.
- `arpit2017closer`: networks learn simple patterns before memorizing noise. Background for the MLP trend.
- `rolnick2017deep`: deep networks can generalize despite massive label noise given a larger dataset. Counterpoint: our MLP result is for one untuned MLP on two small datasets and does not contradict it.

## Datasets, baselines and tools

- `pedregosa2012scikitlearn`: scikit-learn (arXiv version of the JMLR paper). Cite for `LogisticRegression`, `MLPClassifier`, `StratifiedKFold`, `cross_val_predict`, `StandardScaler`, and the built-in digits and breast cancer datasets (loaded with `load_digits` and `load_breast_cancer`). No separate paper was added for the datasets; they are scikit-learn built-ins.
- Baselines logistic regression and the MLP are standard scikit-learn models; cite `pedregosa2012scikitlearn` for both.
