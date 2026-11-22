# Numbers the paper may print

Each row is a recipe in paper/sources.py. Print a number with its key right after it, e.g. `81.8\%\src{acc}`; choose the precision in the text; the checker rounds the recipe's value to that precision. Values below are unrounded.

| key | value | what it is | files read |
|---|---|---|---|
| `acc_bc_00_filter_mean` | 96.6082 | test accuracy (%) on clean test split, breast_cancer, noise 0.0, filter, mean over 5 seeds | results/runs.jsonl |
| `acc_bc_00_filter_sd` | 0.960917 | sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.0, filter | results/runs.jsonl |
| `acc_bc_00_logreg_mean` | 96.7251 | test accuracy (%) on clean test split, breast_cancer, noise 0.0, logreg, mean over 5 seeds | results/runs.jsonl |
| `acc_bc_00_logreg_sd` | 1.21266 | sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.0, logreg | results/runs.jsonl |
| `acc_bc_00_mlp_mean` | 96.7251 | test accuracy (%) on clean test split, breast_cancer, noise 0.0, MLP, mean over 5 seeds | results/runs.jsonl |
| `acc_bc_00_mlp_sd` | 1.21266 | sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.0, MLP | results/runs.jsonl |
| `acc_bc_20_filter_mean` | 95.2047 | test accuracy (%) on clean test split, breast_cancer, noise 0.2, filter, mean over 5 seeds | results/runs.jsonl |
| `acc_bc_20_filter_sd` | 0.76248 | sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.2, filter | results/runs.jsonl |
| `acc_bc_20_logreg_mean` | 92.2807 | test accuracy (%) on clean test split, breast_cancer, noise 0.2, logreg on noisy labels, mean over 5 seeds | results/runs.jsonl |
| `acc_bc_20_logreg_sd` | 3.73079 | sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.2, logreg | results/runs.jsonl |
| `acc_bc_20_mlp_mean` | 84.2105 | test accuracy (%) on clean test split, breast_cancer, noise 0.2, MLP on noisy labels, mean over 5 seeds | results/runs.jsonl |
| `acc_bc_20_mlp_sd` | 3.98777 | sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.2, MLP | results/runs.jsonl |
| `acc_bc_40_filter_mean` | 83.9766 | test accuracy (%) on clean test split, breast_cancer, noise 0.4, filter, mean over 5 seeds | results/runs.jsonl |
| `acc_bc_40_filter_sd` | 8.95138 | sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.4, filter | results/runs.jsonl |
| `acc_bc_40_logreg_mean` | 80.3509 | test accuracy (%) on clean test split, breast_cancer, noise 0.4, logreg on noisy labels, mean over 5 seeds | results/runs.jsonl |
| `acc_bc_40_logreg_sd` | 9.38956 | sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.4, logreg | results/runs.jsonl |
| `acc_bc_40_mlp_mean` | 65.3801 | test accuracy (%) on clean test split, breast_cancer, noise 0.4, MLP on noisy labels, mean over 5 seeds | results/runs.jsonl |
| `acc_bc_40_mlp_sd` | 5.42947 | sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.4, MLP | results/runs.jsonl |
| `acc_dg_00_filter_mean` | 96.5926 | test accuracy (%) on clean test split, digits, noise 0.0, filter, mean over 5 seeds | results/runs.jsonl |
| `acc_dg_00_filter_sd` | 0.360992 | sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.0, filter | results/runs.jsonl |
| `acc_dg_00_logreg_mean` | 96.8148 | test accuracy (%) on clean test split, digits, noise 0.0, logreg, mean over 5 seeds | results/runs.jsonl |
| `acc_dg_00_logreg_sd` | 0.821939 | sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.0, logreg | results/runs.jsonl |
| `acc_dg_00_mlp_mean` | 97.3333 | test accuracy (%) on clean test split, digits, noise 0.0, MLP, mean over 5 seeds | results/runs.jsonl |
| `acc_dg_00_mlp_sd` | 0.549348 | sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.0, MLP | results/runs.jsonl |
| `acc_dg_20_filter_mean` | 95.1111 | test accuracy (%) on clean test split, digits, noise 0.2, filter, mean over 5 seeds | results/runs.jsonl |
| `acc_dg_20_filter_sd` | 0.874498 | sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.2, filter | results/runs.jsonl |
| `acc_dg_20_logreg_mean` | 89.1111 | test accuracy (%) on clean test split, digits, noise 0.2, logreg on noisy labels, mean over 5 seeds | results/runs.jsonl |
| `acc_dg_20_logreg_sd` | 0.974644 | sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.2, logreg | results/runs.jsonl |
| `acc_dg_20_mlp_mean` | 82.4074 | test accuracy (%) on clean test split, digits, noise 0.2, MLP on noisy labels, mean over 5 seeds | results/runs.jsonl |
| `acc_dg_20_mlp_sd` | 1.63551 | sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.2, MLP | results/runs.jsonl |
| `acc_dg_40_filter_mean` | 92.6296 | test accuracy (%) on clean test split, digits, noise 0.4, filter, mean over 5 seeds | results/runs.jsonl |
| `acc_dg_40_filter_sd` | 1.59517 | sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.4, filter | results/runs.jsonl |
| `acc_dg_40_logreg_mean` | 83.5926 | test accuracy (%) on clean test split, digits, noise 0.4, logreg on noisy labels, mean over 5 seeds | results/runs.jsonl |
| `acc_dg_40_logreg_sd` | 1.25325 | sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.4, logreg | results/runs.jsonl |
| `acc_dg_40_mlp_mean` | 64.8889 | test accuracy (%) on clean test split, digits, noise 0.4, MLP on noisy labels, mean over 5 seeds | results/runs.jsonl |
| `acc_dg_40_mlp_sd` | 3.11695 | sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.4, MLP | results/runs.jsonl |
| `cfg_folds` | 5 | number of cross-validation folds K of the filter, from the config | experiments/config.json |
| `cfg_logreg_C` | 1 | inverse L2 regularisation strength C of logistic regression, from the config | experiments/config.json |
| `cfg_mlp_hidden` | 64 | hidden units of the single-hidden-layer MLP, from the config | experiments/config.json |
| `cfg_mlp_max_iter` | 500 | max_iter of the MLP, from the config | experiments/config.json |
| `cfg_n_noise_rates` | 3 | number of nominal noise rates in the config (0.0, 0.2, 0.4) | experiments/config.json |
| `cfg_noise_high_pct` | 40 | highest nominal noise rate (%) in the config | experiments/config.json |
| `cfg_noise_low_pct` | 20 | lower nonzero nominal noise rate (%) in the config | experiments/config.json |
| `cfg_test_fraction_pct` | 30 | test fraction (%) of the train/test split, from the config | experiments/config.json |
| `clean_cost_bc` | -0.116959 | accuracy difference (points of %), filter minus logreg, clean labels, breast_cancer, difference of 5-seed means | results/runs.jsonl |
| `clean_cost_dg` | -0.222222 | accuracy difference (points of %), filter minus logreg, clean labels, digits, difference of 5-seed means | results/runs.jsonl |
| `clean_worse_seeds_bc` | 1 | number of seeds (of 5) where filter is strictly below logreg, clean labels, breast_cancer | results/runs.jsonl |
| `clean_worse_seeds_dg` | 2 | number of seeds (of 5) where filter is strictly below logreg, clean labels, digits | results/runs.jsonl |
| `diff_bc_00_filter_minus_mlp` | -0.116959 | accuracy difference (points of %), filter minus MLP, breast_cancer, noise 0.0, difference of 5-seed means | results/runs.jsonl |
| `diff_bc_20_filter_minus_logreg` | 2.92398 | accuracy difference (points of %), filter minus logreg on same noisy labels, breast_cancer, noise 0.2, difference of 5-seed means | results/runs.jsonl |
| `diff_bc_20_filter_minus_mlp` | 10.9942 | accuracy difference (points of %), filter minus MLP, breast_cancer, noise 0.2, difference of 5-seed means | results/runs.jsonl |
| `diff_bc_40_filter_minus_logreg` | 3.62573 | accuracy difference (points of %), filter minus logreg on same noisy labels, breast_cancer, noise 0.4, difference of 5-seed means | results/runs.jsonl |
| `diff_bc_40_filter_minus_mlp` | 18.5965 | accuracy difference (points of %), filter minus MLP, breast_cancer, noise 0.4, difference of 5-seed means | results/runs.jsonl |
| `diff_dg_00_filter_minus_mlp` | -0.740741 | accuracy difference (points of %), filter minus MLP, digits, noise 0.0, difference of 5-seed means | results/runs.jsonl |
| `diff_dg_20_filter_minus_logreg` | 6 | accuracy difference (points of %), filter minus logreg on same noisy labels, digits, noise 0.2, difference of 5-seed means | results/runs.jsonl |
| `diff_dg_20_filter_minus_mlp` | 12.7037 | accuracy difference (points of %), filter minus MLP, digits, noise 0.2, difference of 5-seed means | results/runs.jsonl |
| `diff_dg_40_filter_minus_logreg` | 9.03704 | accuracy difference (points of %), filter minus logreg on same noisy labels, digits, noise 0.4, difference of 5-seed means | results/runs.jsonl |
| `diff_dg_40_filter_minus_mlp` | 27.7407 | accuracy difference (points of %), filter minus MLP, digits, noise 0.4, difference of 5-seed means | results/runs.jsonl |
| `dropped_bc_00_mean` | 7.4 | training samples dropped by the filter with clean labels, breast_cancer, mean over 5 seeds | results/runs.jsonl |
| `dropped_bc_20_mean` | 92.8 | training samples dropped by the filter, breast_cancer, noise 0.2, mean over 5 seeds | results/runs.jsonl |
| `dropped_bc_40_mean` | 177.2 | training samples dropped by the filter, breast_cancer, noise 0.4, mean over 5 seeds | results/runs.jsonl |
| `dropped_dg_00_mean` | 43.6 | training samples dropped by the filter with clean labels, digits, mean over 5 seeds | results/runs.jsonl |
| `dropped_dg_20_mean` | 377.4 | training samples dropped by the filter, digits, noise 0.2, mean over 5 seeds | results/runs.jsonl |
| `dropped_dg_40_mean` | 634.2 | training samples dropped by the filter, digits, noise 0.4, mean over 5 seeds | results/runs.jsonl |
| `dropped_frac_bc_00_mean` | 1.8593 | percentage of training samples dropped by the filter with clean labels, breast_cancer, mean over 5 seeds | results/runs.jsonl |
| `dropped_frac_dg_00_mean` | 3.46858 | percentage of training samples dropped by the filter with clean labels, digits, mean over 5 seeds | results/runs.jsonl |
| `droppedshare_bc_20` | 23.3166 | mean share (%) of training set dropped by the filter, breast_cancer, noise 0.2 | results/runs.jsonl |
| `droppedshare_bc_40` | 44.5226 | mean share (%) of training set dropped by the filter, breast_cancer, noise 0.4 | results/runs.jsonl |
| `droppedshare_dg_20` | 30.0239 | mean share (%) of training set dropped by the filter, digits, noise 0.2 | results/runs.jsonl |
| `droppedshare_dg_40` | 50.4535 | mean share (%) of training set dropped by the filter, digits, noise 0.4 | results/runs.jsonl |
| `gap_bc_20_filter_to_clean` | 1.52047 | accuracy (points of %) by which filter at noise 0.2 is below clean-label logreg, breast_cancer, 5-seed means | results/runs.jsonl |
| `gap_bc_40_filter_to_clean` | 12.7485 | accuracy (points of %) by which filter at noise 0.4 is below clean-label logreg, breast_cancer, 5-seed means | results/runs.jsonl |
| `gap_dg_20_filter_to_clean` | 1.7037 | accuracy (points of %) by which filter at noise 0.2 is below clean-label logreg, digits, 5-seed means | results/runs.jsonl |
| `gap_dg_40_filter_to_clean` | 4.18519 | accuracy (points of %) by which filter at noise 0.4 is below clean-label logreg, digits, 5-seed means | results/runs.jsonl |
| `loss_bc_20_logreg` | 4.44444 | accuracy lost by logreg to noise (points of %), clean logreg minus noisy logreg, breast_cancer, noise 0.2, 5-seed means | results/runs.jsonl |
| `loss_bc_40_logreg` | 16.3743 | accuracy lost by logreg to noise (points of %), clean logreg minus noisy logreg, breast_cancer, noise 0.4, 5-seed means | results/runs.jsonl |
| `loss_dg_20_logreg` | 7.7037 | accuracy lost by logreg to noise (points of %), clean logreg minus noisy logreg, digits, noise 0.2, 5-seed means | results/runs.jsonl |
| `loss_dg_40_logreg` | 13.2222 | accuracy lost by logreg to noise (points of %), clean logreg minus noisy logreg, digits, noise 0.4, 5-seed means | results/runs.jsonl |
| `n_runs` | 90 | total number of run records in results/runs.jsonl | results/runs.jsonl |
| `n_seeds` | 5 | number of seeds in the config | experiments/config.json |
| `n_test_bc` | 171 | test set size, breast_cancer | results/runs.jsonl |
| `n_test_digits` | 540 | test set size, digits | results/runs.jsonl |
| `n_total_bc` | 569 | number of samples in breast_cancer (n_train + n_test of seed 0) | results/runs.jsonl |
| `n_total_digits` | 1797 | number of samples in digits (n_train + n_test of seed 0) | results/runs.jsonl |
| `n_train_bc` | 398 | training set size, breast_cancer | results/runs.jsonl |
| `n_train_digits` | 1257 | training set size, digits | results/runs.jsonl |
| `noisy_frac_bc_20_mean` | 19.196 | realised percentage of flipped training labels, breast_cancer, nominal noise 0.2, mean over 5 seeds | results/runs.jsonl |
| `noisy_frac_bc_40_mean` | 38.593 | realised percentage of flipped training labels, breast_cancer, nominal noise 0.4, mean over 5 seeds | results/runs.jsonl |
| `noisy_frac_dg_20_mean` | 19.6977 | realised percentage of flipped training labels, digits, nominal noise 0.2, mean over 5 seeds | results/runs.jsonl |
| `noisy_frac_dg_40_mean` | 39.3636 | realised percentage of flipped training labels, digits, nominal noise 0.4, mean over 5 seeds | results/runs.jsonl |
| `pdmax_bc_00` | 0 | largest per-seed paired difference (points of %), filter minus logreg, breast_cancer, noise 0 | results/runs.jsonl |
| `pdmax_bc_20` | 6.43275 | largest per-seed paired difference (points of %), filter minus logreg, breast_cancer, noise 0.2 | results/runs.jsonl |
| `pdmax_bc_40` | 5.84795 | largest per-seed paired difference (points of %), filter minus logreg, breast_cancer, noise 0.4 | results/runs.jsonl |
| `pdmax_dg_00` | 0.555556 | largest per-seed paired difference (points of %), filter minus logreg, digits, noise 0 | results/runs.jsonl |
| `pdmax_dg_20` | 7.40741 | largest per-seed paired difference (points of %), filter minus logreg, digits, noise 0.2 | results/runs.jsonl |
| `pdmax_dg_40` | 11.8519 | largest per-seed paired difference (points of %), filter minus logreg, digits, noise 0.4 | results/runs.jsonl |
| `pdmin_bc_00` | -0.584795 | smallest per-seed paired difference (points of %), filter minus logreg, breast_cancer, noise 0 | results/runs.jsonl |
| `pdmin_bc_20` | -1.16959 | smallest per-seed paired difference (points of %), filter minus logreg, breast_cancer, noise 0.2 | results/runs.jsonl |
| `pdmin_bc_40` | 2.33918 | smallest per-seed paired difference (points of %), filter minus logreg, breast_cancer, noise 0.4 | results/runs.jsonl |
| `pdmin_dg_00` | -1.2963 | smallest per-seed paired difference (points of %), filter minus logreg, digits, noise 0 | results/runs.jsonl |
| `pdmin_dg_20` | 3.7037 | smallest per-seed paired difference (points of %), filter minus logreg, digits, noise 0.2 | results/runs.jsonl |
| `pdmin_dg_40` | 5.55556 | smallest per-seed paired difference (points of %), filter minus logreg, digits, noise 0.4 | results/runs.jsonl |
| `precision_bc_20_mean` | 76.353 | precision (%) of the filter (dropped samples that were truly flipped), breast_cancer, noise 0.2, mean over 5 seeds of per-seed ratios | results/runs.jsonl |
| `precision_bc_20_min` | 72.549 | lowest per-seed precision (%) of the filter over 5 seeds, breast_cancer, noise 0.2 | results/runs.jsonl |
| `precision_bc_40_mean` | 68.2508 | precision (%) of the filter (dropped samples that were truly flipped), breast_cancer, noise 0.4, mean over 5 seeds of per-seed ratios | results/runs.jsonl |
| `precision_bc_40_min` | 63.1016 | lowest per-seed precision (%) of the filter over 5 seeds, breast_cancer, noise 0.4 | results/runs.jsonl |
| `precision_dg_20_mean` | 64.6139 | precision (%) of the filter (dropped samples that were truly flipped), digits, noise 0.2, mean over 5 seeds of per-seed ratios | results/runs.jsonl |
| `precision_dg_20_min` | 61.0687 | lowest per-seed precision (%) of the filter over 5 seeds, digits, noise 0.2 | results/runs.jsonl |
| `precision_dg_40_mean` | 76.1051 | precision (%) of the filter (dropped samples that were truly flipped), digits, noise 0.4, mean over 5 seeds of per-seed ratios | results/runs.jsonl |
| `precision_dg_40_min` | 75.3106 | lowest per-seed precision (%) of the filter over 5 seeds, digits, noise 0.4 | results/runs.jsonl |
| `recall_bc_20_mean` | 92.5165 | recall (%) of the filter (flipped training samples that were dropped), breast_cancer, noise 0.2, mean over 5 seeds of per-seed ratios | results/runs.jsonl |
| `recall_bc_40_mean` | 78.9076 | recall (%) of the filter (flipped training samples that were dropped), breast_cancer, noise 0.4, mean over 5 seeds of per-seed ratios | results/runs.jsonl |
| `recall_dg_20_mean` | 98.4639 | recall (%) of the filter (flipped training samples that were dropped), digits, noise 0.2, mean over 5 seeds of per-seed ratios | results/runs.jsonl |
| `recall_dg_40_mean` | 97.5422 | recall (%) of the filter (flipped training samples that were dropped), digits, noise 0.4, mean over 5 seeds of per-seed ratios | results/runs.jsonl |
| `recovery_bc_20` | 0.657895 | fraction of accuracy lost to noise recovered by filter, (filter - noisy logreg)/(clean logreg - noisy logreg), breast_cancer, noise 0.2, 5-seed means | results/runs.jsonl |
| `recovery_bc_40` | 0.221429 | fraction of accuracy lost to noise recovered by filter, (filter - noisy logreg)/(clean logreg - noisy logreg), breast_cancer, noise 0.4, 5-seed means | results/runs.jsonl |
| `recovery_dg_20` | 0.778846 | fraction of accuracy lost to noise recovered by filter, (filter - noisy logreg)/(clean logreg - noisy logreg), digits, noise 0.2, 5-seed means | results/runs.jsonl |
| `recovery_dg_40` | 0.683473 | fraction of accuracy lost to noise recovered by filter, (filter - noisy logreg)/(clean logreg - noisy logreg), digits, noise 0.4, 5-seed means | results/runs.jsonl |
| `time_ratio_filter_logreg_digits` | 4.67125 | ratio of mean fit_seconds, filter over logreg, digits, all noise rates and seeds (machine-dependent) | results/runs.jsonl |
| `wins_bc_20_filter_over_logreg` | 4 | number of seeds (of 5) where filter accuracy is strictly above logreg, breast_cancer, noise 0.2 | results/runs.jsonl |
| `wins_bc_20_filter_over_mlp` | 5 | number of seeds (of 5) where filter accuracy is strictly above MLP, breast_cancer, noise 0.2 | results/runs.jsonl |
| `wins_bc_40_filter_over_logreg` | 5 | number of seeds (of 5) where filter accuracy is strictly above logreg, breast_cancer, noise 0.4 | results/runs.jsonl |
| `wins_bc_40_filter_over_mlp` | 5 | number of seeds (of 5) where filter accuracy is strictly above MLP, breast_cancer, noise 0.4 | results/runs.jsonl |
| `wins_dg_20_filter_over_logreg` | 5 | number of seeds (of 5) where filter accuracy is strictly above logreg, digits, noise 0.2 | results/runs.jsonl |
| `wins_dg_20_filter_over_mlp` | 5 | number of seeds (of 5) where filter accuracy is strictly above MLP, digits, noise 0.2 | results/runs.jsonl |
| `wins_dg_40_filter_over_logreg` | 5 | number of seeds (of 5) where filter accuracy is strictly above logreg, digits, noise 0.4 | results/runs.jsonl |
| `wins_dg_40_filter_over_mlp` | 5 | number of seeds (of 5) where filter accuracy is strictly above MLP, digits, noise 0.4 | results/runs.jsonl |
