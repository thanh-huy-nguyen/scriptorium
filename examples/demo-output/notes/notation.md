# Notation and names

Use the canonical name every time; never a listed variant.

| canonical | kind | definition | never write |
|---|---|---|---|
| out-of-fold filter | method | our method: fit logistic regression with K-fold cross-validation, drop every training sample whose out-of-fold prediction disagrees with its label, and refit on the rest | OOF filter, oof filter, OOF-filter, out of fold filter, out-of-fold-filter, disagreement filter, cross-validated filter, CV filter |
| logistic regression | baseline | logistic regression on standardized features trained on the noisy labels, with no filtering; also the no-filter ablation | logreg, LogReg, logistic-regression, Logistic Regression, LR baseline |
| multilayer perceptron | baseline | untuned one-hidden-layer network with 64 units and scikit-learn defaults, trained on the same noisy labels | multi-layer perceptron, MLPClassifier, mlp baseline, neural network baseline |
| digits | dataset | scikit-learn digits dataset, 10 classes | load_digits, digits dataset, sklearn digits |
| breast cancer | dataset | scikit-learn breast cancer dataset, 2 classes | breast_cancer, Breast Cancer, breast-cancer, load_breast_cancer, Wisconsin breast cancer |
| test accuracy | metric | accuracy on the clean held-out test labels | clean test accuracy, test_acc, held-out accuracy |
| precision | metric | share of dropped samples that were truly flipped | drop precision, filter precision |
| recall | metric | share of flipped labels that the filter drops | drop recall, filter recall, detection rate |
| recovered share | metric | (filter minus noisy logistic regression) divided by (clean minus noisy logistic regression) test accuracy, from 5-seed means | recovered fraction, recovery rate, recovered accuracy share |
| symmetric noise | term | each training label is flipped with probability equal to the noise rate to a uniformly drawn other class; test labels stay clean | uniform noise, random label noise, symmetric label noise |
| flipped label | term | a training label that noise changed from its true class | corrupted label, flipped-label, wrong label |
| out-of-fold prediction | term | the prediction for a sample made by a model fit on the other K-1 folds, which never saw that sample | out of fold prediction, OOF prediction, oof prediction, held-out-fold prediction |
| noisy labels | term | the observed training labels, a share of which are flipped | corrupted labels, noisy-label training set |
| clean labels | term | training labels with no noise (0% noise rate) | uncorrupted labels, noise-free labels |
| noise rate | term | the probability that a training label is flipped (0%, 20% or 40%) | noise level, corruption rate, flip probability |
| drop set | term | the training samples the filter removes | removed set, discard set |

Abbreviations (define once in the body as "long (SHORT)" at first use, then use SHORT):

- MLP: multilayer perceptron

Symbols:

- $n$: the number of training samples
- $x_i$: the standardized feature vector of training sample $i$
- $\tilde{y}_i$: the observed, possibly flipped label of sample $i$
- $f$: the logistic regression classifier
- $K$: the number of cross-validation folds (K = 5)
- $\hat{y}_i$: the out-of-fold prediction for sample $i$
- $S$: the set of kept samples whose out-of-fold prediction equals the observed label
- $C$: the inverse L2 regularization strength of logistic regression (C = 1)
- $\rho$: the symmetric noise rate
