# Numbers the paper may print

Each row is a recipe in paper/sources.py. Print a number with its key right after it, e.g. `81.8\%\src{acc}`; choose the precision in the text; the checker rounds the recipe's value to that precision. Values below are unrounded.

| key | value | what it is | files read |
|---|---|---|---|
| `acc_bc_n0_filter` | 96.6082 | test accuracy (%) of the filter on breast_cancer, 0% label noise, mean over 5 seeds | results/runs.jsonl |
| `acc_bc_n0_logreg` | 96.7251 | test accuracy (%) of logistic regression on breast_cancer, 0% label noise, mean over 5 seeds | results/runs.jsonl |
| `acc_bc_n0_mlp` | 96.7251 | test accuracy (%) of the MLP on breast_cancer, 0% label noise, mean over 5 seeds | results/runs.jsonl |
| `acc_bc_n20_filter` | 95.2047 | test accuracy (%) of the filter on breast_cancer, 20% label noise, mean over 5 seeds | results/runs.jsonl |
| `acc_bc_n20_logreg` | 92.2807 | test accuracy (%) of logistic regression on breast_cancer, 20% label noise, mean over 5 seeds | results/runs.jsonl |
| `acc_bc_n20_mlp` | 84.2105 | test accuracy (%) of the MLP on breast_cancer, 20% label noise, mean over 5 seeds | results/runs.jsonl |
| `acc_bc_n40_filter` | 83.9766 | test accuracy (%) of the filter on breast_cancer, 40% label noise, mean over 5 seeds | results/runs.jsonl |
| `acc_bc_n40_logreg` | 80.3509 | test accuracy (%) of logistic regression on breast_cancer, 40% label noise, mean over 5 seeds | results/runs.jsonl |
| `acc_bc_n40_mlp` | 65.3801 | test accuracy (%) of the MLP on breast_cancer, 40% label noise, mean over 5 seeds | results/runs.jsonl |
| `acc_digits_n0_filter` | 96.5926 | test accuracy (%) of the out-of-fold filter on digits, 0% label noise, mean over 5 seeds | results/runs.jsonl |
| `acc_digits_n0_logreg` | 96.8148 | test accuracy (%) of logistic regression on digits, 0% label noise, mean over 5 seeds | results/runs.jsonl |
| `acc_digits_n0_mlp` | 97.3333 | test accuracy (%) of the MLP on digits, 0% label noise, mean over 5 seeds | results/runs.jsonl |
| `acc_digits_n20_filter` | 95.1111 | test accuracy (%) of the filter on digits, 20% label noise, mean over 5 seeds | results/runs.jsonl |
| `acc_digits_n20_logreg` | 89.1111 | test accuracy (%) of logistic regression on digits, 20% label noise, mean over 5 seeds | results/runs.jsonl |
| `acc_digits_n20_mlp` | 82.4074 | test accuracy (%) of the MLP on digits, 20% label noise, mean over 5 seeds | results/runs.jsonl |
| `acc_digits_n40_filter` | 92.6296 | test accuracy (%) of the filter on digits, 40% label noise, mean over 5 seeds | results/runs.jsonl |
| `acc_digits_n40_logreg` | 83.5926 | test accuracy (%) of logistic regression on digits, 40% label noise, mean over 5 seeds | results/runs.jsonl |
| `acc_digits_n40_mlp` | 64.8889 | test accuracy (%) of the MLP on digits, 40% label noise, mean over 5 seeds | results/runs.jsonl |
| `actual_noise_bc_n20` | 19.196 | actual share (%) of training labels flipped on breast_cancer at nominal 20% noise, mean over 5 seeds | results/runs.jsonl |
| `actual_noise_bc_n40` | 38.593 | actual share (%) of training labels flipped on breast_cancer at nominal 40% noise, mean over 5 seeds | results/runs.jsonl |
| `actual_noise_digits_n20` | 19.6977 | actual share (%) of training labels flipped on digits at nominal 20% noise, mean over 5 seeds | results/runs.jsonl |
| `actual_noise_digits_n40` | 39.3636 | actual share (%) of training labels flipped on digits at nominal 40% noise, mean over 5 seeds | results/runs.jsonl |
| `bc0_logreg_diff_ci_high` | 0 | upper end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, breast_cancer, noise 0.0, 5 seeds | results/runs.jsonl |
| `bc0_logreg_diff_ci_low` | -0.350877 | lower end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, breast_cancer, noise 0.0, 5 seeds | results/runs.jsonl |
| `bc20_logreg_diff_ci_high` | 5.49708 | upper end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, breast_cancer, noise 0.2, 5 seeds | results/runs.jsonl |
| `bc20_logreg_diff_ci_low` | 0.350877 | lower end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, breast_cancer, noise 0.2, 5 seeds | results/runs.jsonl |
| `bc20_mlp_diff_ci_high` | 14.0351 | upper end of the 95% interval (points) of the paired difference filter minus MLP, test accuracy, breast_cancer, noise 0.2, 5 seeds | results/runs.jsonl |
| `bc20_mlp_diff_ci_low` | 7.95322 | lower end of the 95% interval (points) of the paired difference filter minus MLP, test accuracy, breast_cancer, noise 0.2, 5 seeds | results/runs.jsonl |
| `bc40_logreg_diff_ci_high` | 4.79532 | upper end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, breast_cancer, noise 0.4, 5 seeds | results/runs.jsonl |
| `bc40_logreg_diff_ci_low` | 2.80702 | lower end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, breast_cancer, noise 0.4, 5 seeds | results/runs.jsonl |
| `bc40_mlp_diff_ci_high` | 21.6374 | upper end of the 95% interval (points) of the paired difference filter minus MLP, test accuracy, breast_cancer, noise 0.4, 5 seeds | results/runs.jsonl |
| `bc40_mlp_diff_ci_low` | 15.4386 | lower end of the 95% interval (points) of the paired difference filter minus MLP, test accuracy, breast_cancer, noise 0.4, 5 seeds | results/runs.jsonl |
| `dg0_logreg_diff_ci_high` | 0.333333 | upper end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, digits, noise 0.0, 5 seeds | results/runs.jsonl |
| `dg0_logreg_diff_ci_low` | -0.888889 | lower end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, digits, noise 0.0, 5 seeds | results/runs.jsonl |
| `dg20_logreg_diff_ci_high` | 6.96296 | upper end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, digits, noise 0.2, 5 seeds | results/runs.jsonl |
| `dg20_logreg_diff_ci_low` | 4.77778 | lower end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, digits, noise 0.2, 5 seeds | results/runs.jsonl |
| `dg20_mlp_diff_ci_high` | 14.3704 | upper end of the 95% interval (points) of the paired difference filter minus MLP, test accuracy, digits, noise 0.2, 5 seeds | results/runs.jsonl |
| `dg20_mlp_diff_ci_low` | 10.8519 | lower end of the 95% interval (points) of the paired difference filter minus MLP, test accuracy, digits, noise 0.2, 5 seeds | results/runs.jsonl |
| `dg40_logreg_diff_ci_high` | 10.8148 | upper end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, digits, noise 0.4, 5 seeds | results/runs.jsonl |
| `dg40_logreg_diff_ci_low` | 7.03704 | lower end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, digits, noise 0.4, 5 seeds | results/runs.jsonl |
| `dg40_mlp_diff_ci_high` | 31.1481 | upper end of the 95% interval (points) of the paired difference filter minus MLP, test accuracy, digits, noise 0.4, 5 seeds | results/runs.jsonl |
| `dg40_mlp_diff_ci_low` | 24.9259 | lower end of the 95% interval (points) of the paired difference filter minus MLP, test accuracy, digits, noise 0.4, 5 seeds | results/runs.jsonl |
| `dropped_frac_bc_n0` | 1.8593 | share (%) of training samples the filter drops on breast_cancer at 0% noise (all clean), mean over 5 seeds | results/runs.jsonl |
| `dropped_frac_bc_n20` | 23.3166 | share (%) of training samples dropped by the filter, breast_cancer, 20% noise, mean over 5 seeds | results/runs.jsonl |
| `dropped_frac_bc_n40` | 44.5226 | share (%) of training samples dropped by the filter, breast_cancer, 40% noise, mean over 5 seeds | results/runs.jsonl |
| `dropped_frac_digits_n0` | 3.46858 | share (%) of training samples the filter drops on digits at 0% noise (all clean), mean over 5 seeds | results/runs.jsonl |
| `dropped_frac_digits_n20` | 30.0239 | share (%) of training samples dropped by the filter, digits, 20% noise, mean over 5 seeds | results/runs.jsonl |
| `dropped_frac_digits_n40` | 50.4535 | share (%) of training samples dropped by the filter, digits, 40% noise, mean over 5 seeds | results/runs.jsonl |
| `dz_bc20_filter_vs_logreg` | 0.890871 | Cohen's dz (paired effect size), filter vs no-filter logistic regression test accuracy, breast_cancer, noise 0.2, 5 seeds | results/runs.jsonl |
| `dz_bc40_filter_vs_logreg` | 2.71888 | Cohen's dz (paired effect size), filter vs no-filter logistic regression test accuracy, breast_cancer, noise 0.4, 5 seeds | results/runs.jsonl |
| `dz_dg20_filter_vs_logreg` | 4.24337 | Cohen's dz (paired effect size), filter vs no-filter logistic regression test accuracy, digits, noise 0.2, 5 seeds | results/runs.jsonl |
| `dz_dg40_filter_vs_logreg` | 3.99517 | Cohen's dz (paired effect size), filter vs no-filter logistic regression test accuracy, digits, noise 0.4, 5 seeds | results/runs.jsonl |
| `filter_folds` | 5 | number of cross-validation folds used by the filter, from config | experiments/config.json |
| `fit_sec_digits_filter` | 0.0555166 | wall-clock fit time (s) of the filter (5-fold CV plus refit) on digits, mean over all 15 runs | results/runs.jsonl |
| `fit_sec_digits_logreg` | 0.0118847 | wall-clock fit time (s) of logistic regression on digits, mean over all 15 runs (3 noise rates x 5 seeds) | results/runs.jsonl |
| `fit_sec_digits_mlp` | 0.559031 | wall-clock fit time (s) of the MLP on digits, mean over all 15 runs | results/runs.jsonl |
| `gain_bc_n0_vs_logreg` | -0.116959 | filter minus logistic regression, test accuracy (points), breast_cancer, 0% noise (cost on clean labels, negative = cost), mean of 5 paired seeds | results/runs.jsonl |
| `gain_bc_n0_vs_mlp` | -0.116959 | filter minus MLP, test accuracy (points), breast_cancer, 0% noise, mean of 5 paired seeds | results/runs.jsonl |
| `gain_bc_n20_vs_logreg` | 2.92398 | filter minus no-filter logistic regression, test accuracy (points), breast_cancer, 20% noise, mean of 5 paired seeds | results/runs.jsonl |
| `gain_bc_n20_vs_mlp` | 10.9942 | filter minus MLP, test accuracy (points), breast_cancer, 20% noise, mean of 5 paired seeds | results/runs.jsonl |
| `gain_bc_n40_vs_logreg` | 3.62573 | filter minus no-filter logistic regression, test accuracy (points), breast_cancer, 40% noise, mean of 5 paired seeds | results/runs.jsonl |
| `gain_bc_n40_vs_mlp` | 18.5965 | filter minus MLP, test accuracy (points), breast_cancer, 40% noise, mean of 5 paired seeds | results/runs.jsonl |
| `gain_digits_n0_vs_logreg` | -0.222222 | filter minus logistic regression, test accuracy (points), digits, 0% noise (cost on clean labels, negative = cost), mean of 5 paired seeds | results/runs.jsonl |
| `gain_digits_n0_vs_mlp` | -0.740741 | filter minus MLP, test accuracy (points), digits, 0% noise, mean of 5 paired seeds | results/runs.jsonl |
| `gain_digits_n20_vs_logreg` | 6 | filter minus no-filter logistic regression, test accuracy (points), digits, 20% noise, mean of 5 paired seeds | results/runs.jsonl |
| `gain_digits_n20_vs_mlp` | 12.7037 | filter minus MLP, test accuracy (points), digits, 20% noise, mean of 5 paired seeds | results/runs.jsonl |
| `gain_digits_n40_vs_logreg` | 9.03704 | filter minus no-filter logistic regression, test accuracy (points), digits, 40% noise, mean of 5 paired seeds | results/runs.jsonl |
| `gain_digits_n40_vs_mlp` | 27.7407 | filter minus MLP, test accuracy (points), digits, 40% noise, mean of 5 paired seeds | results/runs.jsonl |
| `kept_bc_n40` | 220.8 | training samples kept by the filter on breast_cancer at 40% noise, mean over 5 seeds | results/runs.jsonl |
| `kept_digits_n40` | 622.8 | training samples kept by the filter on digits at 40% noise, mean over 5 seeds | results/runs.jsonl |
| `logreg_c` | 1 | inverse regularization strength C of logistic regression, from config | experiments/config.json |
| `loss_bc_n20` | 4.44444 | accuracy (points) lost by logistic regression on breast_cancer from 0% to 20% noise, mean over 5 seeds | results/runs.jsonl |
| `loss_bc_n40` | 16.3743 | accuracy (points) lost by logistic regression on breast_cancer from 0% to 40% noise, mean over 5 seeds | results/runs.jsonl |
| `loss_digits_n20` | 7.7037 | accuracy (points) lost by logistic regression on digits from 0% to 20% noise, mean over 5 seeds | results/runs.jsonl |
| `loss_digits_n40` | 13.2222 | accuracy (points) lost by logistic regression on digits from 0% to 40% noise, mean over 5 seeds | results/runs.jsonl |
| `mlp_hidden` | 64 | hidden units of the MLP's single hidden layer, from config | experiments/config.json |
| `mlp_max_iter` | 500 | maximum training iterations of the MLP, from config | experiments/config.json |
| `n_datasets` | 2 | number of datasets, from experiments/config.json | experiments/config.json |
| `n_noise_rates` | 3 | number of label-noise rates, from experiments/config.json | experiments/config.json |
| `n_runs_total` | 90 | number of records in results/runs.jsonl (2 datasets x 3 noise rates x 5 seeds x 3 methods) | results/runs.jsonl |
| `n_seeds` | 5 | number of seeds per cell, from experiments/config.json | experiments/config.json |
| `n_seeds_filter_wins_mlp_bc_n20` | 5 | number of 5 seeds in which the filter beats the MLP on breast_cancer at 20% noise | results/runs.jsonl |
| `n_seeds_filter_wins_mlp_bc_n40` | 5 | number of 5 seeds in which the filter beats the MLP on breast_cancer at 40% noise | results/runs.jsonl |
| `n_seeds_filter_wins_mlp_digits_n20` | 5 | number of 5 seeds in which the filter beats the MLP on digits at 20% noise | results/runs.jsonl |
| `n_seeds_filter_wins_mlp_digits_n40` | 5 | number of 5 seeds in which the filter beats the MLP on digits at 40% noise | results/runs.jsonl |
| `n_test_bc` | 171 | test samples on breast_cancer, from runs.jsonl; asserted equal in all runs | results/runs.jsonl |
| `n_test_digits` | 540 | test samples on digits (30% split), from runs.jsonl; asserted equal in all digits runs | results/runs.jsonl |
| `n_total_bc` | 569 | total samples on breast_cancer (train plus test) | results/runs.jsonl |
| `n_total_digits` | 1797 | total samples on digits (train plus test) | results/runs.jsonl |
| `n_train_bc` | 398 | training samples on breast_cancer, from runs.jsonl; asserted equal in all runs | results/runs.jsonl |
| `n_train_digits` | 1257 | training samples on digits (70% split), from runs.jsonl; asserted equal in all digits runs | results/runs.jsonl |
| `noise_max_pct` | 40 | highest symmetric label-noise rate (%), from experiments/config.json | experiments/config.json |
| `noise_mid_pct` | 20 | middle label-noise rate (%), from experiments/config.json | experiments/config.json |
| `p_bc0_filter_vs_logreg` | 0.373901 | p-value, paired t-test over 5 seeds, filter vs no-filter logistic regression test accuracy, breast_cancer, noise 0.0 (cost on clean labels) | results/runs.jsonl |
| `p_bc0_filter_vs_mlp` | 0.704 | p-value, paired t-test over 5 seeds, filter vs the MLP test accuracy, breast_cancer, noise 0.0 | results/runs.jsonl |
| `p_bc20_filter_vs_clean` | 0.0486302 | p-value, paired t-test over 5 seeds, filter at noise 0.2 vs logistic regression at noise 0.0, test accuracy, breast_cancer | results/runs.jsonl |
| `p_bc20_filter_vs_logreg` | 0.117176 | p-value, paired t-test over 5 seeds, filter vs no-filter logistic regression test accuracy, breast_cancer, noise 0.2 | results/runs.jsonl |
| `p_bc20_filter_vs_mlp` | 0.00326808 | p-value, paired t-test over 5 seeds, filter vs the MLP test accuracy, breast_cancer, noise 0.2 | results/runs.jsonl |
| `p_bc20_prec_vs_half` | 6.52046e-05 | p-value, paired t-test over 5 seeds, filter precision (%) vs 50%, breast_cancer, noise 0.2 | results/runs.jsonl |
| `p_bc40_filter_vs_clean` | 0.0275158 | p-value, paired t-test over 5 seeds, filter at noise 0.4 vs logistic regression at noise 0.0, test accuracy, breast_cancer | results/runs.jsonl |
| `p_bc40_filter_vs_logreg` | 0.00369925 | p-value, paired t-test over 5 seeds, filter vs no-filter logistic regression test accuracy, breast_cancer, noise 0.4 | results/runs.jsonl |
| `p_bc40_filter_vs_mlp` | 0.000491848 | p-value, paired t-test over 5 seeds, filter vs the MLP test accuracy, breast_cancer, noise 0.4 | results/runs.jsonl |
| `p_bc40_prec_vs_half` | 0.000545144 | p-value, paired t-test over 5 seeds, filter precision (%) vs 50%, breast_cancer, noise 0.4 | results/runs.jsonl |
| `p_bc_loss_n40` | 0.0143543 | p-value, paired t-test over 5 seeds, logistic regression test accuracy at noise 0.0 vs 0.4, breast_cancer | results/runs.jsonl |
| `p_dg0_filter_vs_logreg` | 0.552889 | p-value, paired t-test over 5 seeds, filter vs no-filter logistic regression test accuracy, digits, noise 0.0 (cost on clean labels) | results/runs.jsonl |
| `p_dg0_filter_vs_mlp` | 0.0309058 | p-value, paired t-test over 5 seeds, filter vs the MLP test accuracy, digits, noise 0.0 | results/runs.jsonl |
| `p_dg20_filter_vs_clean` | 0.0529848 | p-value, paired t-test over 5 seeds, filter at noise 0.2 vs logistic regression at noise 0.0, test accuracy, digits | results/runs.jsonl |
| `p_dg20_filter_vs_logreg` | 0.000688454 | p-value, paired t-test over 5 seeds, filter vs no-filter logistic regression test accuracy, digits, noise 0.2 | results/runs.jsonl |
| `p_dg20_filter_vs_mlp` | 0.000239335 | p-value, paired t-test over 5 seeds, filter vs the MLP test accuracy, digits, noise 0.2 | results/runs.jsonl |
| `p_dg20_prec_vs_half` | 0.000151772 | p-value, paired t-test over 5 seeds, filter precision (%) vs 50%, digits, noise 0.2 (are most dropped samples mislabeled) | results/runs.jsonl |
| `p_dg40_filter_vs_clean` | 0.0156594 | p-value, paired t-test over 5 seeds, filter at noise 0.4 vs logistic regression at noise 0.0, test accuracy, digits | results/runs.jsonl |
| `p_dg40_filter_vs_logreg` | 0.00086823 | p-value, paired t-test over 5 seeds, filter vs no-filter logistic regression test accuracy, digits, noise 0.4 | results/runs.jsonl |
| `p_dg40_filter_vs_mlp` | 0.000111491 | p-value, paired t-test over 5 seeds, filter vs the MLP test accuracy, digits, noise 0.4 | results/runs.jsonl |
| `p_dg40_prec_vs_half` | 2.1437e-07 | p-value, paired t-test over 5 seeds, filter precision (%) vs 50%, digits, noise 0.4 | results/runs.jsonl |
| `p_dg_loss_n40` | 6.10566e-06 | p-value, paired t-test over 5 seeds, logistic regression test accuracy at noise 0.0 vs 0.4, digits | results/runs.jsonl |
| `p_prec_vs_half_max` | 0.000545144 | largest of the four p-values (paired t-test over 5 seeds) of filter precision vs 50%, both datasets, noise 0.2 and 0.4 | results/runs.jsonl |
| `prec_bc_n20` | 76.353 | precision (%) of the filter on breast_cancer, 20% noise, mean over 5 seeds | results/runs.jsonl |
| `prec_bc_n40` | 68.2508 | precision (%) of the filter on breast_cancer, 40% noise, mean over 5 seeds | results/runs.jsonl |
| `prec_digits_n20` | 64.6139 | precision (%) of the filter on digits, 20% noise: dropped samples that were truly flipped, mean over 5 seeds | results/runs.jsonl |
| `prec_digits_n40` | 76.1051 | precision (%) of the filter on digits, 40% noise, mean over 5 seeds | results/runs.jsonl |
| `prec_min_any` | 61.0687 | lowest per-run precision (%) of the filter over all noisy cells (2 datasets x 20%/40% noise x 5 seeds) | results/runs.jsonl |
| `rec_bc_n20` | 92.5165 | recall (%) of the filter on breast_cancer, 20% noise, mean over 5 seeds | results/runs.jsonl |
| `rec_bc_n40` | 78.9076 | recall (%) of the filter on breast_cancer, 40% noise, mean over 5 seeds | results/runs.jsonl |
| `rec_digits_n20` | 98.4639 | recall (%) of the filter on digits, 20% noise: flipped samples that were dropped, mean over 5 seeds | results/runs.jsonl |
| `rec_digits_n40` | 97.5422 | recall (%) of the filter on digits, 40% noise, mean over 5 seeds | results/runs.jsonl |
| `recovery_bc_n20` | 65.7895 | share (%) of logistic-regression accuracy lost to 20% noise on breast_cancer that the filter wins back, using group means over 5 seeds | results/runs.jsonl |
| `recovery_bc_n40` | 22.1429 | share (%) of logistic-regression accuracy lost to 40% noise on breast_cancer that the filter wins back, using group means over 5 seeds | results/runs.jsonl |
| `recovery_digits_n20` | 77.8846 | share (%) of logistic-regression accuracy lost to 20% noise on digits that the filter wins back: (filter-noisy)/(clean-noisy) using group means over 5 seeds | results/runs.jsonl |
| `recovery_digits_n40` | 68.3473 | share (%) of logistic-regression accuracy lost to 40% noise on digits that the filter wins back, using group means over 5 seeds | results/runs.jsonl |
| `recovery_seed_mean_digits_n40` | 68.4731 | mean over 5 seeds of the per-seed share (%) of accuracy lost to 40% noise recovered by the filter, digits | results/runs.jsonl |
| `recovery_seed_min_bc_n20` | -66.6667 | minimum over 5 seeds of the per-seed recovered share (%) at 20% noise, breast_cancer (denominator can be near zero) | results/runs.jsonl |
| `sd_bc_n0_filter` | 0.960917 | sd over 5 seeds of test accuracy (%) of the filter on breast_cancer, 0% noise | results/runs.jsonl |
| `sd_bc_n0_logreg` | 1.21266 | sd over 5 seeds of test accuracy (%) of logistic regression on breast_cancer, 0% noise | results/runs.jsonl |
| `sd_bc_n0_mlp` | 1.21266 | sd over 5 seeds of test accuracy (%) of the MLP on breast_cancer, 0% noise | results/runs.jsonl |
| `sd_bc_n20_filter` | 0.76248 | sd over 5 seeds of test accuracy (%) of the filter on breast_cancer, 20% noise | results/runs.jsonl |
| `sd_bc_n20_logreg` | 3.73079 | sd over 5 seeds of test accuracy (%) of logistic regression on breast_cancer, 20% noise | results/runs.jsonl |
| `sd_bc_n20_mlp` | 3.98777 | sd over 5 seeds of test accuracy (%) of the MLP on breast_cancer, 20% noise | results/runs.jsonl |
| `sd_bc_n40_filter` | 8.95138 | sd over 5 seeds of test accuracy (%) of the filter on breast_cancer, 40% noise | results/runs.jsonl |
| `sd_bc_n40_logreg` | 9.38956 | sd over 5 seeds of test accuracy (%) of logistic regression on breast_cancer, 40% noise | results/runs.jsonl |
| `sd_bc_n40_mlp` | 5.42947 | sd over 5 seeds of test accuracy (%) of the MLP on breast_cancer, 40% noise | results/runs.jsonl |
| `sd_digits_n0_filter` | 0.360992 | sd over 5 seeds of test accuracy (%) of the filter on digits, 0% noise | results/runs.jsonl |
| `sd_digits_n0_logreg` | 0.821939 | sd over 5 seeds of test accuracy (%) of logistic regression on digits, 0% noise | results/runs.jsonl |
| `sd_digits_n0_mlp` | 0.549348 | sd over 5 seeds of test accuracy (%) of the MLP on digits, 0% noise | results/runs.jsonl |
| `sd_digits_n20_filter` | 0.874498 | sd over 5 seeds of test accuracy (%) of the filter on digits, 20% noise | results/runs.jsonl |
| `sd_digits_n20_logreg` | 0.974644 | sd over 5 seeds of test accuracy (%) of logistic regression on digits, 20% noise | results/runs.jsonl |
| `sd_digits_n20_mlp` | 1.63551 | sd over 5 seeds of test accuracy (%) of the MLP on digits, 20% noise | results/runs.jsonl |
| `sd_digits_n40_filter` | 1.59517 | sd over 5 seeds of test accuracy (%) of the filter on digits, 40% noise | results/runs.jsonl |
| `sd_digits_n40_logreg` | 1.25325 | sd over 5 seeds of test accuracy (%) of logistic regression on digits, 40% noise | results/runs.jsonl |
| `sd_digits_n40_mlp` | 3.11695 | sd over 5 seeds of test accuracy (%) of the MLP on digits, 40% noise | results/runs.jsonl |
| `sd_prec_bc_n20` | 3.40207 | sd over 5 seeds of filter precision (%), breast_cancer, 20% noise | results/runs.jsonl |
| `sd_prec_bc_n40` | 4.04903 | sd over 5 seeds of filter precision (%), breast_cancer, 40% noise | results/runs.jsonl |
| `sd_prec_digits_n20` | 2.3371 | sd over 5 seeds of filter precision (%), digits, 20% noise | results/runs.jsonl |
| `sd_prec_digits_n40` | 0.802788 | sd over 5 seeds of filter precision (%), digits, 40% noise | results/runs.jsonl |
| `test_fraction_pct` | 30 | share (%) of each dataset held out as the clean test set, from config | experiments/config.json |
