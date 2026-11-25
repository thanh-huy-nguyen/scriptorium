# Verified related work

The filter is a known idea. Brodley and Friedl already removed training samples flagged by held-out classifiers,
including with a single algorithm, so the paper presents the filter as a plain instance of classification filtering
and measures it. No method listed here was run, so claim no advantage over any of them.

The 22 citable keys are more than a 190-word related-work section needs. The core set is `brodley1999identifying`,
`northcutt2021confident`, `han2018coteaching` and `song2023learning` (the last three are the brief's must-cites).
Each line below stays within what the fetched abstract supports. "Title only" means no abstract could be fetched,
so cite the paper for nothing beyond its title.

## classification_filtering

- `brodley1999identifying`: uses classifiers as noise filters to remove mislabeled training instances; compares
  single-algorithm, majority-vote and consensus filters and reports higher accuracy for noise levels up to 30%.
  Differs: the closest antecedent. Ours is a single-algorithm filter with one logistic regression for both the
  out-of-fold check and the refit, and we measure what it drops on clean as well as noisy labels.
- `saez2016inffc`: iterative noise filter that fuses several classifiers and controls removal with a noisy score.
  Differs: ours uses one linear model, one pass and no score or threshold.
- `verbaeten2003ensemble`: ensemble methods for noise elimination in classification (title only).
- `wilson1972asymptotic`: edits the training set of a nearest neighbor rule with a 3-nearest neighbor rule before
  1-nearest neighbor classification. An early data-editing method; its abstract does not mention label noise.
- `stone1974crossvalidatory`: cross-validation for the choice and assessment of statistical predictions. Cite only
  for cross-validation itself, not for filtering.

## confident_learning

- `northcutt2021confident`: finds label errors by estimating the joint distribution of given and true labels under
  class-conditional noise, combining pruning, counting with probabilistic thresholds, and ranking.
  Differs: ours drops every hard out-of-fold disagreement, with no threshold and no noise estimate. Not run here.
  The abstract does not say "out-of-sample probabilities" or "per-class thresholds"; the safe wording is
  "probabilistic thresholds".
- `northcutt2021pervasive`: finds label errors in the test sets of 10 benchmark datasets with confident learning
  plus human validation; reports that lower-capacity models may be more useful than higher-capacity ones when many
  labels are wrong. Differs: ours adds synthetic noise to training labels only. Relevant to the uncounted
  pre-existing label errors and, with care, to the MLP comparison.

## sample_selection

- `han2018coteaching`: two deep networks each select likely-clean samples in every mini-batch for the other to learn
  from. Differs: ours acts once before the final fit, uses one linear model, and takes no drop rate. Not run here.
  The abstract does not mention a drop rate scheduled from the noise rate, so do not hang that detail on the
  citation without checking the paper.
- `jiang2017mentornet`: a second network learns a sample-weighting curriculum that steers the main network toward
  probably correct labels. Differs: ours makes a hard keep-or-drop decision with no learned weighting.
- `yu2019how`: Co-teaching+, which adds an update-by-disagreement step to Co-teaching. Differs: its disagreement is
  between two networks; ours is between a prediction and the given label.
- `wei2020combating`: JoCoR, which trains two networks jointly with co-regularization and updates both on small-loss
  samples.
- `li2020dividemix`: splits data into clean and noisy sets by per-sample loss and trains semi-supervised, keeping
  suspected noisy samples as unlabeled data. Differs: ours discards them.

## noise_models

- `song2023learning`: survey of robust training for deep networks with noisy labels, covering noise rate estimation
  and evaluation. Differs: ours is a small study of one filter for logistic regression.
- `frenay2014classification`: survey of label noise in classification with a taxonomy of noise types, its
  consequences, and noise-robust, cleansing and noise-tolerant algorithms. Use this one for noise types and for
  data cleansing. Neither survey abstract names symmetric, class-dependent and instance-dependent noise.
- `patrini2017making`: corrects the training loss using class corruption probabilities, which it also estimates.
  Differs: ours changes the training set instead of the loss and estimates no noise parameters.
- `liu2016classification`: importance reweighting of surrogate losses under noisy labels, with noise rate estimation.
  Differs: ours estimates no noise rate.
- `ghosh2017robust`: conditions under which a loss tolerates label noise; shows that mean absolute error does.
- `bootkrajang2012labelnoise`: label-noise robust logistic regression (title only). A model-based alternative for our
  base classifier; do not describe how it works.

## Datasets, baselines and tools

- `pedregosa2012scikitlearn`: the scikit-learn library. Cite for both dataset loaders, the logistic regression and
  MLP baselines, standardization and cross-validation.
- `harris2020array`: NumPy, used in `experiments/run.py` (including the random generator for label noise).
- `mangasarian1995breast`: breast cancer diagnosis from fine needle aspirate cell characteristics with linear
  programming, trained on 569 patients. Cite for the breast cancer data.
- `kaynakmultistage`: Kaynak and Alpaydin's cascade of classifiers, tested on handwritten digit recognition. Its
  abstract does not say that it introduces or releases the digits data, so do not call it the dataset's source.
  The safe wording cites `pedregosa2012scikitlearn` for "digits, as distributed with scikit-learn" and leaves this key
  for a statement about the authors' digit recognition work.

## Do not cite

- `street1993lt` (nuclear feature extraction for breast tumor diagnosis): the fetched title contains escaped HTML
  tags (`&lt;title&gt;`), and the raw `&` is expected to break the LaTeX bibliography. Cite `mangasarian1995breast`
  instead.
