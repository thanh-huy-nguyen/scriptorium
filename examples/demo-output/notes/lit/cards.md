# What the literature says (one card per paper, from its abstract)

## learning with noisy labels

- `doi:10.1007/s10462-004-0751-8` Class Noise vs. Attribute Noise: A Quantitative Study (2003), background: Systematic evaluation of noise in machine learning that separates class noise from attribute noise.
- `doi:10.1007/bf00116829` Learning From Noisy Examples (1988), background: Shows that with independent random classification errors by the teacher, choosing the most consistent rule for the sample is sufficient.

## sample selection and noise filtering

- `arxiv:1804.06872` Co-teaching: Robust Training of Deep Neural Networks with Extremely Noisy Labels (2018), competing: Trains two deep networks at once; each selects data of possibly clean labels in a mini-batch and passes it to its peer for the update.
- `doi:10.1613/jair.1.12125` Confident Learning: Estimating Uncertainty in Dataset Labels (2021), competing: Confident learning characterizes and identifies label errors by pruning noisy data, counting with probabilistic thresholds to estimate noise, and ranking examples, assuming class-conditional noise.
- `doi:10.1613/jair.606` Identifying Mislabeled Training Data (1999), competing: Uses a set of learning algorithms as noise filters to identify and remove mislabeled training instances, comparing single-algorithm, majority-vote and consensus filters.
- `openalex:W123339444` Identifying and eliminating mislabeled training instances (1996), builds-on: Filters mislabeled training instances with an ensemble of classifiers under n-fold cross validation, and trains the final learner only on instances the filter classifies correctly.
- `doi:10.1016/j.inffus.2015.04.002` INFFC: An iterative class noise filter based on the fusion of classifiers with noise sensitivity control (2016), competing: Proposes a noise filter that fuses the predictions of several classifiers, filters iteratively, and uses a noisy score to control how many examples are removed.
- `doi:10.1016/j.knosys.2017.10.026` CNC-NOS: Class noise cleaning by ensemble filtering and noise scoring (2018), competing: Proposes an ensemble of noise filters that filters mislabeled instances and corrects them when possible.
- `arxiv:1705.01936` Learning with Confident Examples: Rank Pruning for Robust Classification with Noisy Labels (2017), competing: Proposes Rank Pruning for binary classification with flipped labels, which also estimates the noise rates.
- `arxiv:2103.14749` Pervasive Label Errors in Test Sets Destabilize Machine Learning Benchmarks (2021), background: Uses confident learning to flag label errors in the test sets of 10 common datasets, validates them by crowdsourcing, and studies how they affect model rankings.
- `arxiv:1706.02613` Decoupling "when to update" from "how to update" (2017), competing: Proposes a meta algorithm for noisy labels that separates the decision of when to update from how to update, tested on a noisy gender classification dataset.
- `arxiv:2002.07394` DivideMix: Learning with Noisy Labels as Semi-supervised Learning (2020), competing: Splits training data into a clean labeled set and a noisy unlabeled set with a mixture model on per-sample loss, then trains two networks with semi-supervised learning.

## surveys

- `doi:10.1109/tnnls.2022.3152527` Learning From Noisy Labels With Deep Neural Networks: A Survey (2022), background: Survey of learning with label noise for deep networks: 62 robust training methods in five groups, noise rate estimation, and evaluation practice.
- `doi:10.1109/tnnls.2013.2292894` Classification in the Presence of Label Noise: A Survey (2014), background: Survey of label noise in classification: a taxonomy of noise types, its consequences, and noise-robust, noise-cleansing and noise-tolerant algorithms.
- `doi:10.1016/j.knosys.2021.106771` Image classification with deep learning in the presence of noisy labels: A survey (2021), background: Survey on image classification with deep learning under noisy labels (title only; no abstract could be fetched). (abstract unavailable)

## robust losses and loss correction

- `doi:10.1109/cvpr.2017.240` Making Deep Neural Networks Robust to Label Noise: A Loss Correction Approach (2017), competing: Proposes two loss correction procedures for class-dependent label noise that need a matrix inversion and multiplication given the class corruption probabilities, plus a way to estimate those probabilities.
- `doi:10.1609/aaai.v31i1.10894` Robust Loss Functions under Label Noise for Deep Neural Networks (2017), competing: Gives sufficient conditions on a loss function for risk minimization to tolerate label noise in multiclass problems, and shows the mean absolute error loss satisfies them.
- `arxiv:1805.07836` Generalized Cross Entropy Loss for Training Deep Neural Networks with Noisy Labels (2018), competing: Presents a family of noise-robust losses that generalizes mean absolute error and categorical cross entropy, after showing MAE can perform poorly with DNNs on challenging datasets.

## deep networks and memorization

- `arxiv:1611.03530` Understanding deep learning requires rethinking generalization (2016), background: Shows through systematic experiments that large convolutional networks trained with stochastic gradient methods fit random labelings of the training data, so traditional explanations of generalization do not account for their behavior.
- `arxiv:1706.05394` A Closer Look at Memorization in Deep Networks (2017), background: Examines memorization in deep networks and finds that, although they can memorize noise, they tend to learn simple patterns first, with optimization behaving differently on noise than on real data.
- `arxiv:1705.10694` Deep Learning is Robust to Massive Label Noise (2017), competing: Shows that deep neural networks can generalize from training data in which true labels are massively outnumbered by incorrect labels, given a larger dataset.

## tools

- `doi:10.5555/1953048.2078195` Scikit-learn: Machine Learning in Python (2011), tool: Describes scikit-learn, a Python module of machine learning algorithms for medium-scale supervised and unsupervised problems. The fetched abstract is truncated after its first sentence and a fragment of the second.
