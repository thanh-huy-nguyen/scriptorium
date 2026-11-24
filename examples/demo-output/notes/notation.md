# Notation and names

Use the canonical name every time; never a listed variant.

| canonical | kind | definition | never write |
|---|---|---|---|
| out-of-fold filter | method | our method: predict each training sample with a logistic regression fit on the other folds, drop the samples whose prediction disagrees with their label, and refit on the rest | Out-of-Fold Filter, out of fold filter, OOF filter, OOF-filter, oof filter, disagreement filter, LogReg filter, logreg filter |
| logistic regression | baseline | standardized logistic regression (C = 1.0) trained on all noisy labels; also the model the filter wraps | Logistic Regression, logreg, LogReg, logistic-regression, linear baseline |
| multilayer perceptron | baseline | untuned scikit-learn network with one hidden layer of 64 units, trained on all noisy labels | multi-layer perceptron, Multilayer Perceptron, multilayer-perceptron, neural network baseline, deep baseline |
| digits | dataset | scikit-learn digits: 10 classes, 8x8 images as 64 features | Digits dataset, sklearn digits, load_digits, handwritten digits dataset |
| breast cancer | dataset | scikit-learn breast cancer: 2 classes | breast_cancer, breast-cancer, Breast Cancer, Wisconsin dataset |
| accuracy | metric | share of correctly classified samples on the clean test split | test_acc, test acc |
| precision | metric | share of dropped training samples that were truly flipped | drop precision, filter precision |
| recall | metric | share of flipped training samples that the filter drops | drop recall, filter recall |
| recovered share | metric | (filter accuracy - logistic regression accuracy) / (logistic regression accuracy at 0% noise - logistic regression accuracy); our own definition | recovered fraction, recovery fraction, recovery rate, recovered percentage, recovery share |
| symmetric noise | term | each training label is flipped with the noise rate to a class drawn uniformly from the other classes | uniform noise, uniform label noise, random label noise, symmetric label noise, symmetric flips |
| noise rate | term | the probability that a training label is flipped (0, 20 or 40%) | noise level, flip rate, flip probability, corruption rate |
| flipped label | term | a training label replaced by a wrong class by the noise process | corrupted label |
| out-of-fold prediction | term | the class predicted for a training sample by a model fit on the folds that do not contain it | out of fold prediction, OOF prediction, oof prediction, cross-validated prediction |
| cross-validation | term | K-fold stratified cross-validation inside the training set (K = 5) | cross validation, crossvalidation, k-fold CV |
| clean test split | term | the 30% of each dataset held out with uncorrupted labels, used for scoring | clean test set, clean-test split, uncorrupted test set |

Abbreviations (define once in the body as "long (SHORT)" at first use, then use SHORT):

- MLP: multilayer perceptron

Symbols:

- $\mathcal{D}$: the training set of n samples with observed labels
- $n$: the number of training samples
- $x_i$: the feature vector of training sample i
- $\tilde{y}_i$: the observed, possibly flipped label of sample i
- $y_i$: the true label of sample i, never seen by the filter
- $f$: the standardized logistic regression classifier
- $K$: the number of cross-validation folds (K = 5)
- $k(i)$: the fold that contains sample i
- $\hat{y}_i$: the out-of-fold prediction for sample i
- $\mathcal{S}$: the kept subset of training samples on which the final model is refit
- $\rho$: the symmetric noise rate
