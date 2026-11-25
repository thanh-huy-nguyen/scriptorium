# What the literature says (one card per paper, from its abstract)

## surveys and noise models

- `doi:10.1109/tnnls.2022.3152527` Learning From Noisy Labels With Deep Neural Networks: A Survey (2022), background: Surveys robust training methods for deep neural networks under noisy labels, together with noise rate estimation, evaluation methodology and research directions.
- `doi:10.1109/tnnls.2013.2292894` Classification in the Presence of Label Noise: A Survey (2014), background: Surveys label noise in classification: its definitions, sources and types, its potential consequences, the algorithms that account for it, and experiment design.
- `doi:10.1007/bf00116829` Learning from noisy examples (1988), background: Title only (no abstract could be fetched): concerns learning from noisy examples. (abstract unavailable)
- `doi:10.1007/s10462-004-0751-8` Class Noise vs. Attribute Noise: A Quantitative Study (2004), background: Title only (no abstract could be fetched): a quantitative study of class noise versus attribute noise. (abstract unavailable)
- `doi:10.1007/s10994-009-5165-z` Random classification noise defeats all convex potential boosters (2009), background: Title only (no abstract could be fetched): concerns the effect of random classification noise on convex potential boosters. (abstract unavailable)
- `doi:10.1145/3446776` Understanding deep learning (still) requires rethinking generalization (2021), background: Shows experimentally that large image classification networks easily fit random labels and argues that traditional explanations do not account for why large networks generalize well in practice.
- `arxiv:2103.14749` Pervasive Label Errors in Test Sets Destabilize Machine Learning Benchmarks (2021), background: Identifies label errors in the test sets of 10 commonly used vision, language, and audio datasets and studies how these errors can affect benchmark results.

## training-data filtering

- `doi:10.1613/jair.606` Identifying Mislabeled Training Data (1999), builds-on: Identifies and eliminates mislabeled training instances by using classifiers as noise filters, with the goal of improving the accuracy of supervised learning.
- `doi:10.1613/jair.1.12125` Confident Learning: Estimating Uncertainty in Dataset Labels (2021), competing: Confident learning focuses on label quality: it characterizes and identifies label errors in datasets by estimating the joint distribution between given noisy labels and unknown uncorrupted labels.
- `doi:10.1109/tsmc.1972.4309137` Asymptotic Properties of Nearest Neighbor Rules Using Edited Data (1972), background: Develops the convergence properties of a nearest neighbor rule that edits the preclassified samples to reduce their number and improve the performance of the rule.
- `doi:10.1023/a:1025832930864` Identifying and Handling Mislabelled Instances (2004), competing: Title only (no abstract could be fetched): the title concerns identifying and handling mislabelled instances. (abstract unavailable)
- `doi:10.1016/j.inffus.2015.04.002` INFFC: An iterative class noise filter based on the fusion of classifiers with noise sensitivity control (2016), competing: Proposes a noise filter that combines several filtering strategies to increase the accuracy of classifiers trained after filtering. The abstract describes an experimental comparison but reports no outcome.
- `doi:10.1111/j.2517-6161.1974.tb00994.x` Cross-Validatory Choice and Assessment of Statistical Predictions (1974), background: Applies a generalized form of the cross-validation criterion to the choice and assessment of statistical prediction.

## sample selection in deep networks

- `arxiv:1804.06872` Co-teaching: Robust Training of Deep Neural Networks with Extremely Noisy Labels (2018), competing: Trains two deep networks at once, each selecting possibly clean data in every mini-batch for its peer to learn from.
- `arxiv:1901.04215` How does Disagreement Help Generalization against Label Corruption? (2019), competing: Proposes Co-teaching+, which adds an update-by-disagreement step to Co-teaching because the two Co-teaching networks converge to a consensus as training proceeds.
- `arxiv:1712.05055` MentorNet: Learning Data-Driven Curriculum for Very Deep Neural Networks on Corrupted Labels (2017), competing: Learns a second network, MentorNet, that guides a deep StudentNet toward samples whose labels are probably correct.
- `arxiv:2002.07394` DivideMix: Learning with Noisy Labels as Semi-supervised Learning (2020), competing: Treats learning with noisy labels as semi-supervised learning by splitting the training data into a clean labeled set and a noisy unlabeled set.
- `doi:10.1109/cvpr42600.2020.01374` Combating Noisy Labels by Agreement: A Joint Training Method with Co-Regularization (2020), competing: Proposes JoCoR, which trains two networks jointly and aims to make them agree instead of keeping them diverse.

## noise-tolerant losses and estimators

- `doi:10.1109/cvpr.2017.240` Making Deep Neural Networks Robust to Label Noise: A Loss Correction Approach (2017), competing: Proposes two loss correction procedures for training deep networks, including recurrent ones, under class-dependent label noise, and shows how to estimate the class corruption probabilities they need.
- `doi:10.1109/tpami.2015.2456899` Classification with Noisy Labels by Importance Reweighting (2016), competing: Studies classification with randomly flipped, possibly class-conditional labels: uses importance reweighting so that any surrogate loss can be used, and shows how the noise rate can be estimated.
- `doi:10.1609/aaai.v31i1.10894` Robust Loss Functions under Label Noise for Deep Neural Networks (2017), competing: Gives sufficient conditions for a loss function to make multiclass risk minimization tolerant to label noise, and shows that the mean absolute error loss is inherently robust to it.
- `doi:10.1007/978-3-642-33460-3_15` Label-Noise Robust Logistic Regression and Its Applications (2012), competing: No abstract could be fetched. From the title only: the paper concerns label-noise robust logistic regression and its applications. (abstract unavailable)

## datasets and tools

- `doi:10.1109/isic.1997.626420` Multistage classification by cascaded classifiers (1997), background: Proposes a cascade in which a distributed learner learns the rule and a local learner learns the exceptions, trained using cross-validation and tested on handwritten digit recognition.
- `doi:10.1117/12.148698` Nuclear feature extraction for breast tumor diagnosis (1993), dataset: Diagnoses breast tumors from nuclear size, shape and texture features measured on digitized fine needle aspirate slides, using a linear-programming-based classifier.
- `doi:10.1287/opre.43.4.570` Breast Cancer Diagnosis and Prognosis Via Linear Programming (1995), dataset: Describes two medical applications of linear programming-based machine learning: diagnosing breast cancer from cell characteristics and predicting its recurrence.
- `arxiv:1201.0490` Scikit-learn: Machine Learning in Python (2012), tool: Presents scikit-learn, a Python module that integrates a wide range of machine learning algorithms for medium-scale supervised and unsupervised problems.
- `doi:10.1038/s41586-020-2649-2` Array programming with NumPy (2020), tool: Reviews how a few array concepts lead to a programming paradigm for organizing, exploring and analyzing scientific data with NumPy.
