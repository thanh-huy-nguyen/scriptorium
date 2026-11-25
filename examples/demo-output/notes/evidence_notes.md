# Evidence notes

The data supports this story: on two small datasets with synthetic symmetric label noise, one pass of out-of-fold
filtering improves logistic regression in nearly every noisy run, at almost no mean cost on clean labels. It does
not support "recovers most of the lost accuracy" as a general statement. The recovery is partial, and it is small in
the hardest setting (breast_cancer at 40% noise).

All numbers come from `paper/sources.py` (93 recipes, all resolving).

## Claims in brief.md

| Claim | Verdict | What may be written |
|---|---|---|
| The filter recovers most of the accuracy that label noise costs a linear model | **Narrower. False as stated.** | Most of the loss is won back on digits at both rates and on breast_cancer at 20%, judged on seed means. On breast_cancer at 40% only a small part is won back. |
| Most of the samples it drops are truly mislabeled | **Supported on noisy training sets only** | True in every noisy run. False on clean labels, where every dropped sample is correctly labeled. |
| It beats a larger model (an MLP) trained on the same noisy labels | **Supported only as a bare comparison. It says little about the filter.** | The filter is above the MLP in every noisy run, but plain logistic regression is too. With clean labels the MLP is ahead on digits and tied in the mean on breast_cancer. |
| It costs little when the labels are clean | **Supported** | Mean accuracy drops very slightly on both datasets, although the filter still discards correct samples. |
| Needs no clean validation set and no noise-rate estimate (idea paragraph) | **True by design** | A property of the code, not a measured result. C and K are fixed in the config, with no record of how they were chosen. |

## Numbers behind the claims

Mean test accuracy (%) ± sample sd over 5 seeds.

| Dataset | Noise | Ours | Logistic regression | MLP | Lost accuracy won back (%) | Drop precision (%) | Drop recall (%) | Training set dropped (%) |
|---|---|---|---|---|---|---|---|---|
| digits | 0% | 96.6 ± 0.4 | 96.8 ± 0.8 | 97.3 ± 0.5 | n/a | 0 | n/a | 3.5 |
| digits | 20% | 95.1 ± 0.9 | 89.1 ± 1.0 | 82.4 ± 1.6 | 77.9 | 64.6 | 98.5 | 30.0 |
| digits | 40% | 92.6 ± 1.6 | 83.6 ± 1.3 | 64.9 ± 3.1 | 68.3 | 76.1 | 97.5 | 50.5 |
| breast_cancer | 0% | 96.6 ± 1.0 | 96.7 ± 1.2 | 96.7 ± 1.2 | n/a | 0 | n/a | 1.9 |
| breast_cancer | 20% | 95.2 ± 0.8 | 92.3 ± 3.7 | 84.2 ± 4.0 | 65.8 | 76.4 | 92.5 | 23.3 |
| breast_cancer | 40% | 84.0 ± 9.0 | 80.4 ± 9.4 | 65.4 ± 5.4 | 22.1 | 68.3 | 78.9 | 44.5 |

## What the data supports

1. Filtering helps logistic regression under symmetric noise. It is strictly more accurate in 19 of 20 noisy runs
   (`wins_vs_logreg_noisy`). The exception is breast_cancer, 20%, seed 3. The mean gain is larger at 40% than at 20%
   on both datasets, but only slightly so on breast_cancer.
2. The share won back falls as noise rises, on both datasets. With two rates this is an observation, not a trend law.
   Filtered accuracy stays below the clean-label reference in every noisy setting (seed means).
3. The share won back varies a lot between seeds. On breast_cancer at 40% it is below half in every seed (by hand,
   about 9% to 35%). On breast_cancer at 20% it runs from negative to about 100% because the loss in some seeds is
   tiny. Even on digits, one seed at 40% is below half (about 44%). Quote only the ratio of means
   (`recovered_*`), and do not print per-seed ratios.
4. The filter catches most flipped labels (high recall), at the price of also dropping many correct ones. Precision
   lies between `drop_precision_min` (61%) and `drop_precision_max` (81%) per noisy run. Recall is weakest on
   breast_cancer at 40%, which is also where recovery is weakest. That co-occurrence is not a demonstrated cause.
5. Clean-label cost: the mean difference to logistic regression is -0.22 points on digits (lower in 2 seeds, higher
   in 3) and -0.12 points on breast_cancer (tied in 4 seeds, lower in 1).
6. The MLP loses far more accuracy to noise than logistic regression does, in this one untuned configuration.

## What must not be claimed

- **"Recovers most of the lost accuracy" without a scope.** The title-level and abstract wording must say "much of",
  or name the exception.
- **That filtering is what beats the MLP.** Logistic regression without filtering beats the MLP in all 20 noisy runs
  (`wins_logreg_vs_mlp_noisy`). The comparison shows that this MLP is more sensitive to noise. There is no MLP with
  filtering, no tuning, no early stopping, and no parameter count. "Larger model" can only mean "an MLP with one
  hidden layer of 64 units".
- **That the MLP fails because it memorizes noise.** No training accuracy or learning curves were saved.
- **That the gain comes from choosing the right samples.** No random-drop control and no oracle filter were run.
- **Anything against co-teaching or confident learning.** Neither was run. The method is close to out-of-fold
  classification filtering and to confident learning, so it should not be presented as new without a related-work
  check. Cite them as related work.
- **Anything about class-dependent or instance-dependent noise, other rates, other K or C, repeated filtering,
  deep networks, or large data.** None was run, and brief.md rules out the last two.
- **Per-class behavior or examples of dropped samples.** No per-sample outputs were saved.
- **Runtime.** `fit_seconds` has no hardware record and has no recipe.

## Cautions for the outline and the statistician

- Each cell has 5 seeds. The seeds are random re-splits of one dataset, so test sets overlap and the runs are not
  independent. Treat significance tests as descriptive. A two-sided exact sign or Wilcoxon test on 5 pairs cannot
  go below p = 0.0625.
- The breast_cancer 40% cell has a very large spread for both ours and logistic regression. The paired differences
  are positive in all 5 seeds, so show paired values there, not only overlapping error bars.
- The best baseline is logistic regression in every noisy cell (`gain_vs_logreg_*` is "ours minus best baseline").
  With clean labels it is the MLP on digits, and the two baselines tie on breast_cancer.
- "Truly mislabeled" means flipped by the experiment. Any label errors already in the datasets are not counted.
- The number of classes and features is in no repository file, so it has no recipe and cannot be printed.
- There is no ablation section to write. The only analysis the data supports is what the filter drops.
