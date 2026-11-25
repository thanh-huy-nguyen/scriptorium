# Notation and names

Use the canonical name every time; never a listed variant.

| canonical | kind | definition | never write |
|---|---|---|---|
| out-of-fold filter | method | our method (code name `filter`): predict each training sample with a logistic regression fit on the folds that exclude it, drop the samples whose prediction disagrees with the given label, and refit once on the rest. Write "the out-of-fold filter" at first mention, then "the filter"; tables, figure legends and comparisons may say "ours". No acronym. | out of fold filter, out of fold filtering, outoffold filter, outoffold filtering, OOF filter, OOF filtering, OoF filter, OOF-Filter |
| logistic regression | baseline | linear baseline (code name `logreg`): standardized features and logistic regression trained on all given labels without filtering. | logreg, LogReg, Logreg, log-reg, log reg, Log. Reg., logistic-regression, Logistic-Regression, logistic regressor, logit regression, LR baseline |
| MLP | baseline | larger baseline (code name `mlp`): standardized features and an untuned one-hidden-layer multilayer perceptron, trained on all given labels without filtering. | mlp, Mlp, multi-layer perceptron, Multi-Layer Perceptron, multi layer perceptron, multilayer-perceptron, MLPClassifier |
| clean-label reference | baseline | logistic regression trained on clean labels (the noise-free setting of the same split); the gray reference line in figures. | clean-label baseline, clean-label upper bound, clean upper bound, clean-label oracle |
| digits | dataset | the scikit-learn digits dataset (`load_digits`); lower case except at the start of a sentence or label. | load_digits, load\_digits, sklearn-digits, digit dataset, Digit dataset |
| breast cancer | dataset | the scikit-learn breast cancer dataset (code name `breast_cancer`); two words without a hyphen, lower case except at the start of a sentence or label. | breast_cancer, breast\_cancer, breast-cancer, Breast Cancer, breastcancer, BreastCancer, load_breast_cancer, load\_breast\_cancer, WDBC |
| test accuracy | metric | share of test samples, with clean labels, that a model predicts correctly (code name `test_acc`), in percent. | test_acc, test\_acc, testing accuracy, test-set accuracy, test set accuracy, clean-test acc |
| share of the training set removed | metric | dropped samples divided by all training samples, in percent. | drop fraction, removal rate, rejection rate, filtering rate, pruning rate |
| drop precision | metric | share of dropped samples whose label was flipped by the injected noise, in percent ("drops that are mislabeled"). | drop-precision, filter precision, filtering precision, removal precision, pruning precision, detection precision |
| drop recall | metric | share of flipped training labels that the filter drops, in percent ("flipped labels caught"). | drop-recall, filter recall, filtering recall, removal recall, pruning recall, detection recall |
| lost accuracy won back | metric | ratio of seed means, in percent: test accuracy of ours minus that of logistic regression on noisy labels, divided by the clean-label reference minus logistic regression on noisy labels (Eq. of the setup). Write "share of lost accuracy won back"; the table row says "Won back". | recovered share, recovered fraction, recovery fraction, recovery ratio, recovery rate |
| mislabeled share of the kept set | metric | flipped samples that survive the filter divided by the size of the kept set, per seed, then averaged, in percent; the table row says "Left in kept set". | residual noise rate, remaining noise rate, noise left rate |
| share of correctly labeled samples dropped | metric | correctly labeled samples the filter drops divided by all correctly labeled training samples, per seed, then averaged, in percent; the table row says "Correct dropped". | false drop rate, false positive rate, false removal rate |
| established | term | said of a difference when a two-sided paired t-test over the seeds is significant at the five percent level, uncorrected for multiple comparisons; defined once in the setup. Before that definition, write "not significant". |  |
| label noise | task | the problem of training a classifier when some given training labels are wrong. | label-noise, labelnoise, labeling noise, labelling noise |
| symmetric noise | term | each training label is selected independently with probability equal to the noise rate and replaced by a different class drawn uniformly at random; test labels stay clean. "Symmetric label noise" is the long form. | uniform noise, uniform label noise, symmetrical noise, symmetric-noise, symmetric flipping noise |
| noise rate | term | the probability that a training label is flipped; the realized share of flipped labels varies between runs. The two noisy settings are the lower and the higher noise rate. | noise level, noise-level, corruption rate, flip rate, flipping rate, noise fraction |
| given label | term | the training label a classifier receives, which may be wrong (code name `ytr_noisy`). | ytr_noisy, ytr\_noisy |
| flipped label | term | a given training label that the injected noise changed. | is_noisy, is\_noisy |
| mislabeled | term | said of a training sample whose given label was flipped; a sample that is not mislabeled is correctly labeled. Pre-existing label errors in the datasets are not counted. | mis-labeled, mis labeled, miss-labeled, mislabelled, mis-labelled |
| clean labels | term | labels with no injected noise: the training labels at noise rate zero and all test labels. | noise-free labels, noiseless labels, uncorrupted labels, pristine labels |
| out-of-fold prediction | term | the hard class predicted for a training sample by a model fit on the cross-validation folds that exclude that sample. | out of fold prediction, out-of-fold-prediction, outoffold prediction, OOF prediction, OoF prediction, OOF predictions, held-out-fold prediction |
| cross-validation | term | splitting the training set into folds so that each sample is predicted by a model that was not fit on it. No abbreviation. | cross validation, crossvalidation, Cross Validation, x-validation |
| kept set | term | the training samples whose out-of-fold prediction equals their given label; the final model is fit on it. | retained set, retained subset |
| refit | term | fitting a new standardization and logistic regression on the kept set, once; the result is the refit model. | re-fit, re-fitted, refitted, re-fitting |
| classification filtering | term | prior family of methods that remove training samples a held-out classifier misclassifies; ours is its simplest member. | classification-filtering, classifier filtering |
| confident learning | term | prior method of Northcutt et al. that prunes labels by comparing out-of-sample predicted probabilities with per-class thresholds; discussed, not run. | confident-learning, confidence learning |
| co-teaching | term | prior sample-selection method of Han et al. that trains two networks with a drop rate scheduled from the noise rate; discussed, not run. | coteaching, Coteaching, CoTeaching, co teaching, Co teaching |
| scikit-learn | term | the library that provides the datasets and classifiers. | sklearn, scikit learn, Scikit-Learn, SciKit-Learn |

Abbreviations (define once in the body as "long (SHORT)" at first use, then use SHORT):

- MLP: multilayer perceptron

Symbols:

- $D$: the training set of n pairs of feature vector and given label
- $n$: the number of training samples
- $i$: the index of a training sample
- $x_i$: the feature vector of training sample i
- $\tilde{y}_i$: the given label of training sample i, which may be wrong
- $f_D$: the base model (standardization followed by logistic regression) fit on the set in the subscript, here D; a function from a feature vector to a class
- $K$: the number of cross-validation folds
- $k(i)$: the index of the fold that contains training sample i
- $D_{k(i)}$: the fold of the training set that contains sample i, left out when predicting that sample
- $\hat{y}_i$: the out-of-fold prediction for training sample i, equal to the base model fit on D without that fold, applied to its feature vector
- $D_{\mathrm{keep}}$: the kept set: the training samples whose out-of-fold prediction equals their given label
- $C$: the inverse regularization strength of every logistic regression
- $A$: a seed-mean test accuracy, with subscripts ours, noisy (logistic regression on noisy labels) and clean (the clean-label reference)
