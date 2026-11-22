# Related work (verified entries in paper/refs.bib)

Cite only the keys below.

## noisy_label_surveys
- `song2023learning`: Song et al. (IEEE TNNLS) survey of deep learning with noisy labels. Organises robust architectures, robust losses, loss correction and sample selection. Must-cite. Our filter is a sample-selection/cleaning method.
- `frenay2014classification`: Frenay and Verleysen (IEEE TNNLS) survey of label noise in classification. Covers noise types and the cleaning and robust-learning families. It is the source for the symmetric (uniform) noise model we use.

## classification_filtering
- `wilson1972asymptotic`: Wilson's edited nearest neighbour rule. It removes training samples that their neighbours misclassify. This is the earliest editing method. Our filter does the same with a cross-validated linear model.
- Not found: Brodley and Friedl (JAIR 1999), "Identifying mislabeled training data". The searches returned no entry, and DBLP was unreachable. Do not cite it unless it is added later; describe the lineage using Wilson only.

## confident_learning
- `northcutt2021confident`: Confident learning (JAIR). It estimates the joint distribution of noisy and true labels from out-of-fold predicted probabilities with per-class thresholds, then prunes. Must-cite. Closest modern method. Ours uses only the hard out-of-fold prediction, with no thresholds and no noise-rate estimate, and we do not run it as a baseline.

## sample_selection_deep
- `han2018coteaching`: Co-teaching (NeurIPS 2018). Two networks trade their small-loss samples during training. Must-cite. It targets deep networks; we target small linear models and do not compare against it. Added from the arXiv record, because DBLP was unreachable, so the NeurIPS version is not confirmed.
- `jiang2018mentornet`: MentorNet (ICML 2018). A learned curriculum network weights samples by their loss on corrupted labels. Another deep sample-selection method. We do not compare against it.

## memorization
- `zhang2017understanding`: Zhang et al. Deep networks fit random labels, so high-capacity models can memorise noise. It supports our explanation of why the MLP degrades. Added from arXiv (ICLR 2017 version).
- `arpit2017closer`: Arpit et al. Networks learn simple patterns before memorising noisy samples. It supports the same argument. Added from arXiv (ICML 2017 version).

## Datasets, baselines and tools
- `pedregosa2018scikitlearn`: scikit-learn. We use it for the digits and breast-cancer loaders, StandardScaler, LogisticRegression, MLPClassifier, StratifiedKFold and cross_val_predict. Cite it for the datasets, both baselines and the filter's implementation. The arXiv record carries the year 2018, but the paper is the JMLR 2011 one. A DOI fetch for the JMLR record failed.
- No separate entries for the digits or breast cancer datasets: they ship with scikit-learn, and no citation for their original sources was searched for.
