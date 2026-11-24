# What the literature says (one card per paper, from its abstract)

## sample selection and filtering

- `arxiv:1804.06872` Co-teaching: Robust Training of Deep Neural Networks with Extremely Noisy Labels (2018), competing: Trains two deep networks at once; in each mini-batch each network selects data of possibly clean labels and passes them to its peer for the update.
- `doi:10.1613/jair.1.12125` Confident Learning: Estimating Uncertainty in Dataset Labels (2021), competing: Confident learning identifies label errors by pruning noisy data, counting with probabilistic thresholds to estimate noise, and ranking examples, under a class-conditional noise assumption.
- `doi:10.1613/jair.606` Identifying Mislabeled Training Data (1999), builds-on: Uses a set of learning algorithms as noise filters to identify and remove mislabeled training instances, comparing single algorithm, majority vote and consensus filters.
- `arxiv:2001.10528` Identifying Mislabeled Data using the Area Under the Margin Ranking (2020), competing: Identifies mislabeled training samples with the Area Under the Margin statistic computed from training dynamics, then removes them.
- `arxiv:1901.04215` How does Disagreement Help Generalization against Label Corruption? (2019), competing: Co-teaching+ keeps only the samples on which two networks disagree and lets each network train on the small-loss samples chosen by its peer.
- `doi:10.1007/3-540-48050-1_3` Improving Classification by Removing or Relabeling Mislabeled Instances (), background: Title only: no abstract could be fetched, so the content is not verified. The title indicates a study of removing or relabeling mislabeled training instances to improve classification. (abstract unavailable)

## surveys

- `doi:10.1109/tnnls.2022.3152527` Learning From Noisy Labels With Deep Neural Networks: A Survey (2022), background: Survey of learning with noisy labels for deep networks: reviews 62 robust training methods in five groups, analyzes noise rate estimation and evaluation practice.
- `doi:10.1109/tnnls.2013.2292894` Classification in the Presence of Label Noise: A Survey (2014), background: Survey of label noise in classification: definitions, taxonomy, consequences, and label noise-robust, cleansing and tolerant algorithms.

## linear models under label noise

- `doi:10.1016/j.patcog.2014.05.007` Learning kernel logistic regression in the presence of class label noise (2014), competing: Introduces a label-noise robust kernel logistic regression that sets model complexity without a trusted validation set, using Multiple Kernel Learning and Bayesian regularisation.
- `doi:10.1080/00401706.2020.1870564` Individual Transition Label Noise Logistic Regression in Binary Classification for Incorrectly Labeled Data (2021), competing: Studies label noise logistic regression for binary classification and proposes a flexible nonparametric label noise model with individual transition parameters.

## loss correction and robust losses

- `doi:10.1109/cvpr.2017.240` Making Deep Neural Networks Robust to Label Noise: A Loss Correction Approach (2017), competing: Corrects the training loss of deep networks for class-dependent label noise using a matrix of class-corruption probabilities, which it can also estimate.
- `doi:10.1609/aaai.v31i1.10894` Robust Loss Functions under Label Noise for Deep Neural Networks (2017), competing: Gives sufficient conditions for a multiclass loss to be inherently noise-tolerant and shows the mean absolute value of error loss meets them.

## memorization

- `doi:10.1145/3446776` Understanding deep learning (still) requires rethinking generalization (2021), background: Shows experimentally that large convolutional networks trained with stochastic gradient methods easily fit random labelings, so traditional explanations of generalization fail.
