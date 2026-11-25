# Statistical tests

| comparison | setting | test | p | verdict |
|---|---|---|---|---|
| ours (filter) vs logistic regression | digits, 20% symmetric training-label noise, test accuracy, 5 seeds | `p_filter_vs_logreg_digits_noise20` | 0.000688 | significant |
| ours (filter) vs logistic regression | digits, 40% symmetric training-label noise, test accuracy, 5 seeds | `p_filter_vs_logreg_digits_noise40` | 0.000868 | significant |
| ours (filter) vs logistic regression | breast_cancer, 20% symmetric training-label noise, test accuracy, 5 seeds | `p_filter_vs_logreg_breast_noise20` | 0.117 | not significant |
| ours (filter) vs logistic regression | breast_cancer, 40% symmetric training-label noise, test accuracy, 5 seeds | `p_filter_vs_logreg_breast_noise40` | 0.0037 | significant |
| ours (filter) vs MLP | digits, 20% symmetric training-label noise, test accuracy, 5 seeds | `p_filter_vs_mlp_digits_noise20` | 0.000239 | significant |
| ours (filter) vs MLP | digits, 40% symmetric training-label noise, test accuracy, 5 seeds | `p_filter_vs_mlp_digits_noise40` | 0.000111 | significant |
| ours (filter) vs MLP | breast_cancer, 20% symmetric training-label noise, test accuracy, 5 seeds | `p_filter_vs_mlp_breast_noise20` | 0.00327 | significant |
| ours (filter) vs MLP | breast_cancer, 40% symmetric training-label noise, test accuracy, 5 seeds | `p_filter_vs_mlp_breast_noise40` | 0.000492 | significant |
| ours (filter) vs logistic regression | digits, clean training labels, test accuracy, 5 seeds | `p_filter_vs_logreg_digits_noise0` | 0.553 | not significant |
| ours (filter) vs logistic regression | breast_cancer, clean training labels, test accuracy, 5 seeds | `p_filter_vs_logreg_breast_noise0` | 0.374 | not significant |
| ours (filter) vs half-recovery accuracy (midpoint of clean-label and noisy-label logistic regression) | digits, 20% noise: is more than half of the lost accuracy won back, 5 seeds | `p_filter_vs_halfway_digits_noise20` | 0.0262 | significant |
| ours (filter) vs half-recovery accuracy (midpoint of clean-label and noisy-label logistic regression) | digits, 40% noise: is more than half of the lost accuracy won back, 5 seeds | `p_filter_vs_halfway_digits_noise40` | 0.0728 | not significant |
| ours (filter) vs half-recovery accuracy (midpoint of clean-label and noisy-label logistic regression) | breast_cancer, 20% noise: is more than half of the lost accuracy won back, 5 seeds | `p_filter_vs_halfway_breast_noise20` | 0.468 | not significant |
| ours (filter) vs half-recovery accuracy (midpoint of clean-label and noisy-label logistic regression) | breast_cancer, 40% noise: is more than half of the lost accuracy won back, 5 seeds | `p_filter_vs_halfway_breast_noise40` | 0.067 | not significant |
| share of dropped samples truly mislabeled vs 50% | digits, 20% noise, 5 seeds | `p_drop_precision_vs_half_digits_noise20` | 0.000152 | significant |
| share of dropped samples truly mislabeled vs 50% | digits, 40% noise, 5 seeds | `p_drop_precision_vs_half_digits_noise40` | 2.14e-07 | significant |
| share of dropped samples truly mislabeled vs 50% | breast_cancer, 20% noise, 5 seeds | `p_drop_precision_vs_half_breast_noise20` | 6.52e-05 | significant |
| share of dropped samples truly mislabeled vs 50% | breast_cancer, 40% noise, 5 seeds | `p_drop_precision_vs_half_breast_noise40` | 0.000545 | significant |
| share of mislabeled samples dropped vs 50% | digits, 20% noise, 5 seeds | `p_drop_recall_vs_half_digits_noise20` | 4.91e-09 | significant |
| share of mislabeled samples dropped vs 50% | digits, 40% noise, 5 seeds | `p_drop_recall_vs_half_digits_noise40` | 2.62e-08 | significant |
| share of mislabeled samples dropped vs 50% | breast_cancer, 20% noise, 5 seeds | `p_drop_recall_vs_half_breast_noise20` | 4.54e-06 | significant |
| share of mislabeled samples dropped vs 50% | breast_cancer, 40% noise, 5 seeds | `p_drop_recall_vs_half_breast_noise40` | 0.000563 | significant |
| MLP vs ours (filter) | digits, clean training labels, test accuracy, 5 seeds | `p_mlp_vs_filter_digits_noise0` | 0.0309 | significant |
| ours (filter) vs MLP | breast_cancer, clean training labels, test accuracy, 5 seeds | `p_filter_vs_mlp_breast_noise0` | 0.704 | not significant |
| MLP vs logistic regression | digits, clean training labels, test accuracy, 5 seeds | `p_mlp_vs_logreg_digits_noise0` | 0.0378 | significant |
| logistic regression vs MLP | breast_cancer, clean training labels, test accuracy, 5 seeds | `p_logreg_vs_mlp_breast_noise0` | 1 | not significant |
| logistic regression vs MLP | digits, 20% noise, test accuracy, 5 seeds | `p_logreg_vs_mlp_digits_noise20` | 0.000116 | significant |
| logistic regression vs MLP | digits, 40% noise, test accuracy, 5 seeds | `p_logreg_vs_mlp_digits_noise40` | 5.54e-05 | significant |
| logistic regression vs MLP | breast_cancer, 20% noise, test accuracy, 5 seeds | `p_logreg_vs_mlp_breast_noise20` | 0.00305 | significant |
| logistic regression vs MLP | breast_cancer, 40% noise, test accuracy, 5 seeds | `p_logreg_vs_mlp_breast_noise40` | 0.00143 | significant |
| logistic regression, clean labels vs logistic regression, noisy labels | digits, 0% vs 20% noise, same splits, 5 seeds | `p_noise_cost_logreg_digits_noise20` | 1.48e-06 | significant |
| logistic regression, clean labels vs logistic regression, noisy labels | digits, 0% vs 40% noise, same splits, 5 seeds | `p_noise_cost_logreg_digits_noise40` | 6.11e-06 | significant |
| logistic regression, clean labels vs logistic regression, noisy labels | breast_cancer, 0% vs 20% noise, same splits, 5 seeds | `p_noise_cost_logreg_breast_noise20` | 0.0304 | significant |
| logistic regression, clean labels vs logistic regression, noisy labels | breast_cancer, 0% vs 40% noise, same splits, 5 seeds | `p_noise_cost_logreg_breast_noise40` | 0.0144 | significant |
| accuracy lost to noise by the MLP vs accuracy lost to noise by logistic regression | digits, 20% noise, 5 seeds | `p_noise_cost_mlp_vs_logreg_digits_noise20` | 0.000113 | significant |
| accuracy lost to noise by the MLP vs accuracy lost to noise by logistic regression | digits, 40% noise, 5 seeds | `p_noise_cost_mlp_vs_logreg_digits_noise40` | 8.29e-05 | significant |
| accuracy lost to noise by the MLP vs accuracy lost to noise by logistic regression | breast_cancer, 20% noise, 5 seeds | `p_noise_cost_mlp_vs_logreg_breast_noise20` | 0.00204 | significant |
| accuracy lost to noise by the MLP vs accuracy lost to noise by logistic regression | breast_cancer, 40% noise, 5 seeds | `p_noise_cost_mlp_vs_logreg_breast_noise40` | 0.000838 | significant |
| logistic regression, clean labels vs ours (filter), noisy labels | digits, gap left at 20% noise, same splits, 5 seeds | `p_clean_logreg_vs_filter_digits_noise20` | 0.053 | not significant |
| logistic regression, clean labels vs ours (filter), noisy labels | digits, gap left at 40% noise, same splits, 5 seeds | `p_clean_logreg_vs_filter_digits_noise40` | 0.0157 | significant |
| logistic regression, clean labels vs ours (filter), noisy labels | breast_cancer, gap left at 20% noise, same splits, 5 seeds | `p_clean_logreg_vs_filter_breast_noise20` | 0.0486 | significant |
| logistic regression, clean labels vs ours (filter), noisy labels | breast_cancer, gap left at 40% noise, same splits, 5 seeds | `p_clean_logreg_vs_filter_breast_noise40` | 0.0275 | significant |
| accuracy lost by logistic regression at 40% noise vs accuracy lost by logistic regression at 20% noise | digits, trend over noise rate, 5 seeds | `p_trend_noise_cost_logreg_digits` | 9.81e-05 | significant |
| accuracy lost by logistic regression at 40% noise vs accuracy lost by logistic regression at 20% noise | breast_cancer, trend over noise rate, 5 seeds | `p_trend_noise_cost_logreg_breast` | 0.0122 | significant |
| gain over logistic regression at 40% noise vs gain over logistic regression with clean labels | digits, ends of the noise range, 5 seeds | `p_trend_gain_vs_logreg_digits_noise40_vs_noise0` | 0.000202 | significant |
| gain over logistic regression at 40% noise vs gain over logistic regression at 20% noise | digits, between the two noisy rates, 5 seeds | `p_trend_gain_vs_logreg_digits_noise40_vs_noise20` | 0.00248 | significant |
| gain over logistic regression at 40% noise vs gain over logistic regression with clean labels | breast_cancer, ends of the noise range, 5 seeds | `p_trend_gain_vs_logreg_breast_noise40_vs_noise0` | 0.00341 | significant |
| gain over logistic regression at 40% noise vs gain over logistic regression at 20% noise | breast_cancer, between the two noisy rates, 5 seeds | `p_trend_gain_vs_logreg_breast_noise40_vs_noise20` | 0.663 | not significant |
| gain over the MLP at 40% noise vs gain over the MLP with clean labels | digits, ends of the noise range, 5 seeds | `p_trend_gain_vs_mlp_digits_noise40_vs_noise0` | 7.5e-05 | significant |
| gain over the MLP at 40% noise vs gain over the MLP at 20% noise | digits, between the two noisy rates, 5 seeds | `p_trend_gain_vs_mlp_digits_noise40_vs_noise20` | 0.000461 | significant |
| gain over the MLP at 40% noise vs gain over the MLP with clean labels | breast_cancer, ends of the noise range, 5 seeds | `p_trend_gain_vs_mlp_breast_noise40_vs_noise0` | 0.000276 | significant |
| gain over the MLP at 40% noise vs gain over the MLP at 20% noise | breast_cancer, between the two noisy rates, 5 seeds | `p_trend_gain_vs_mlp_breast_noise40_vs_noise20` | 0.0532 | not significant |
| share of lost accuracy won back at 20% noise vs share of lost accuracy won back at 40% noise | digits, per-seed shares, 5 seeds | `p_trend_recovered_digits` | 0.061 | not significant |
| share of lost accuracy won back at 20% noise vs share of lost accuracy won back at 40% noise | breast_cancer, per-seed shares, 5 seeds | `p_trend_recovered_breast` | 0.613 | not significant |
| drop precision at 40% noise vs drop precision at 20% noise | digits, precision rises with noise, 5 seeds | `p_trend_drop_precision_digits` | 0.000361 | significant |
| drop precision at 20% noise vs drop precision at 40% noise | breast_cancer, precision falls with noise, 5 seeds | `p_trend_drop_precision_breast` | 0.0254 | significant |
| drop recall at 20% noise vs drop recall at 40% noise | digits, recall falls with noise, 5 seeds | `p_trend_drop_recall_digits` | 0.0163 | significant |
| drop recall at 20% noise vs drop recall at 40% noise | breast_cancer, recall falls with noise, 5 seeds | `p_trend_drop_recall_breast` | 0.0219 | significant |
| share of training set dropped at 40% noise vs share of training set dropped with clean labels | digits, ends of the noise range, 5 seeds | `p_trend_drop_fraction_digits` | 2.02e-08 | significant |
| share of training set dropped at 40% noise vs share of training set dropped with clean labels | breast_cancer, ends of the noise range, 5 seeds | `p_trend_drop_fraction_breast` | 3.58e-06 | significant |
| ours (filter) vs logistic regression | all noisy runs pooled over both datasets and both noise rates | `-` |  | untestable |
| digits vs breast_cancer | gain or recovered share of ours compared between datasets | `-` |  | untestable |
| ours (filter) vs co-teaching | any | `-` |  | untestable |
| ours (filter) vs confident learning | any | `-` |  | untestable |
| ours (filter) vs dropping the same number of samples at random | any | `-` |  | untestable |
| ours (filter) vs dropping exactly the flipped samples | any | `-` |  | untestable |
| MLP with filtering vs MLP | any | `-` |  | untestable |
| one filtering pass with the configured folds and C vs other fold counts, regularization strengths or repeated filtering | any | `-` |  | untestable |
| ours (filter) vs logistic regression | class-dependent or instance-dependent label noise | `-` |  | untestable |
