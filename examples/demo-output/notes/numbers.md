# Numbers the paper may print

Each row is a recipe in paper/sources.py. Print a number with its key right after it, e.g. `81.8\%\src{acc}`; choose the precision in the text; the checker rounds the recipe's value to that precision. Values below are unrounded.

| key | value | what it is | files read |
|---|---|---|---|
| `acc_filter_breast_cancer_n0` | 96.6082 | test accuracy (%) of filter on breast_cancer at 0% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `acc_filter_breast_cancer_n20` | 95.2047 | test accuracy (%) of filter on breast_cancer at 20% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `acc_filter_breast_cancer_n40` | 83.9766 | test accuracy (%) of filter on breast_cancer at 40% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `acc_filter_digits_n0` | 96.5926 | test accuracy (%) of filter on digits at 0% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `acc_filter_digits_n20` | 95.1111 | test accuracy (%) of filter on digits at 20% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `acc_filter_digits_n40` | 92.6296 | test accuracy (%) of filter on digits at 40% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `acc_logreg_breast_cancer_n0` | 96.7251 | test accuracy (%) of logreg on breast_cancer at 0% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `acc_logreg_breast_cancer_n20` | 92.2807 | test accuracy (%) of logreg on breast_cancer at 20% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `acc_logreg_breast_cancer_n40` | 80.3509 | test accuracy (%) of logreg on breast_cancer at 40% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `acc_logreg_digits_n0` | 96.8148 | test accuracy (%) of logreg on digits at 0% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `acc_logreg_digits_n20` | 89.1111 | test accuracy (%) of logreg on digits at 20% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `acc_logreg_digits_n40` | 83.5926 | test accuracy (%) of logreg on digits at 40% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `acc_mlp_breast_cancer_n0` | 96.7251 | test accuracy (%) of mlp on breast_cancer at 0% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `acc_mlp_breast_cancer_n20` | 84.2105 | test accuracy (%) of mlp on breast_cancer at 20% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `acc_mlp_breast_cancer_n40` | 65.3801 | test accuracy (%) of mlp on breast_cancer at 40% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `acc_mlp_digits_n0` | 97.3333 | test accuracy (%) of mlp on digits at 0% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `acc_mlp_digits_n20` | 82.4074 | test accuracy (%) of mlp on digits at 20% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `acc_mlp_digits_n40` | 64.8889 | test accuracy (%) of mlp on digits at 40% label noise, mean over seeds 0-4 | results/runs.jsonl |
| `bc0_lr_diff_ci_high` | 0 | upper end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, breast_cancer, 0% noise | results/runs.jsonl |
| `bc0_lr_diff_ci_low` | -0.350877 | lower end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, breast_cancer, 0% noise | results/runs.jsonl |
| `bc0_mlp_diff_ci_high` | 0.350877 | upper end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, breast_cancer, 0% noise | results/runs.jsonl |
| `bc0_mlp_diff_ci_low` | -0.701754 | lower end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, breast_cancer, 0% noise | results/runs.jsonl |
| `bc20_lr_diff_ci_high` | 5.49708 | upper end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, breast_cancer, 20% noise | results/runs.jsonl |
| `bc20_lr_diff_ci_low` | 0.350877 | lower end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, breast_cancer, 20% noise | results/runs.jsonl |
| `bc20_mlp_diff_ci_high` | 14.0351 | upper end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, breast_cancer, 20% noise | results/runs.jsonl |
| `bc20_mlp_diff_ci_low` | 7.95322 | lower end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, breast_cancer, 20% noise | results/runs.jsonl |
| `bc40_lr_diff_ci_high` | 4.79532 | upper end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, breast_cancer, 40% noise | results/runs.jsonl |
| `bc40_lr_diff_ci_low` | 2.80702 | lower end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, breast_cancer, 40% noise | results/runs.jsonl |
| `bc40_mlp_diff_ci_high` | 21.6374 | upper end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, breast_cancer, 40% noise | results/runs.jsonl |
| `bc40_mlp_diff_ci_low` | 15.4386 | lower end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, breast_cancer, 40% noise | results/runs.jsonl |
| `cost_clean_breast_cancer` | 0.116959 | mean paired test-accuracy drop (points) of filter relative to logreg at 0% noise on breast_cancer, seeds 0-4 (logreg minus filter) | results/runs.jsonl |
| `cost_clean_digits` | 0.222222 | mean paired test-accuracy drop (points) of filter relative to logreg at 0% noise on digits, seeds 0-4 (logreg minus filter) | results/runs.jsonl |
| `dg0_lr_diff_ci_high` | 0.333333 | upper end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, digits, 0% noise | results/runs.jsonl |
| `dg0_lr_diff_ci_low` | -0.888889 | lower end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, digits, 0% noise | results/runs.jsonl |
| `dg0_mlp_diff_ci_high` | -0.37037 | upper end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, digits, 0% noise | results/runs.jsonl |
| `dg0_mlp_diff_ci_low` | -1.14815 | lower end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, digits, 0% noise | results/runs.jsonl |
| `dg20_lr_diff_ci_high` | 6.96296 | upper end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, digits, 20% noise | results/runs.jsonl |
| `dg20_lr_diff_ci_low` | 4.77778 | lower end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, digits, 20% noise | results/runs.jsonl |
| `dg20_mlp_diff_ci_high` | 14.3704 | upper end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, digits, 20% noise | results/runs.jsonl |
| `dg20_mlp_diff_ci_low` | 10.8519 | lower end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, digits, 20% noise | results/runs.jsonl |
| `dg40_lr_diff_ci_high` | 10.8148 | upper end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, digits, 40% noise | results/runs.jsonl |
| `dg40_lr_diff_ci_low` | 7.03704 | lower end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, digits, 40% noise | results/runs.jsonl |
| `dg40_mlp_diff_ci_high` | 31.1481 | upper end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, digits, 40% noise | results/runs.jsonl |
| `dg40_mlp_diff_ci_low` | 24.9259 | lower end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, digits, 40% noise | results/runs.jsonl |
| `diff_filter_logreg_breast_cancer_n0` | -0.116959 | mean paired test-accuracy difference (points), filter minus logreg, breast_cancer, 0% noise, seeds 0-4 | results/runs.jsonl |
| `diff_filter_logreg_breast_cancer_n20` | 2.92398 | mean paired test-accuracy difference (points), filter minus logreg, breast_cancer, 20% noise, seeds 0-4 | results/runs.jsonl |
| `diff_filter_logreg_breast_cancer_n40` | 3.62573 | mean paired test-accuracy difference (points), filter minus logreg, breast_cancer, 40% noise, seeds 0-4 | results/runs.jsonl |
| `diff_filter_logreg_digits_n0` | -0.222222 | mean paired test-accuracy difference (points), filter minus logreg, digits, 0% noise, seeds 0-4 | results/runs.jsonl |
| `diff_filter_logreg_digits_n20` | 6 | mean paired test-accuracy difference (points), filter minus logreg, digits, 20% noise, seeds 0-4 | results/runs.jsonl |
| `diff_filter_logreg_digits_n40` | 9.03704 | mean paired test-accuracy difference (points), filter minus logreg, digits, 40% noise, seeds 0-4 | results/runs.jsonl |
| `diff_filter_mlp_breast_cancer_n0` | -0.116959 | mean paired test-accuracy difference (points), filter minus mlp, breast_cancer, 0% noise, seeds 0-4 | results/runs.jsonl |
| `diff_filter_mlp_breast_cancer_n20` | 10.9942 | mean paired test-accuracy difference (points), filter minus mlp, breast_cancer, 20% noise, seeds 0-4 | results/runs.jsonl |
| `diff_filter_mlp_breast_cancer_n40` | 18.5965 | mean paired test-accuracy difference (points), filter minus mlp, breast_cancer, 40% noise, seeds 0-4 | results/runs.jsonl |
| `diff_filter_mlp_digits_n0` | -0.740741 | mean paired test-accuracy difference (points), filter minus mlp, digits, 0% noise, seeds 0-4 | results/runs.jsonl |
| `diff_filter_mlp_digits_n20` | 12.7037 | mean paired test-accuracy difference (points), filter minus mlp, digits, 20% noise, seeds 0-4 | results/runs.jsonl |
| `diff_filter_mlp_digits_n40` | 27.7407 | mean paired test-accuracy difference (points), filter minus mlp, digits, 40% noise, seeds 0-4 | results/runs.jsonl |
| `dropped_breast_cancer_n0` | 7.4 | mean number of training samples the filter drops on breast_cancer at 0% noise, seeds 0-4 | results/runs.jsonl |
| `dropped_breast_cancer_n20` | 92.8 | mean number of training samples the filter drops on breast_cancer at 20% noise, seeds 0-4 | results/runs.jsonl |
| `dropped_breast_cancer_n40` | 177.2 | mean number of training samples the filter drops on breast_cancer at 40% noise, seeds 0-4 | results/runs.jsonl |
| `dropped_digits_n0` | 43.6 | mean number of training samples the filter drops on digits at 0% noise, seeds 0-4 | results/runs.jsonl |
| `dropped_digits_n20` | 377.4 | mean number of training samples the filter drops on digits at 20% noise, seeds 0-4 | results/runs.jsonl |
| `dropped_digits_n40` | 634.2 | mean number of training samples the filter drops on digits at 40% noise, seeds 0-4 | results/runs.jsonl |
| `dropped_pct_breast_cancer_n0` | 1.8593 | mean percent of breast_cancer training samples dropped by the filter at 0% noise, seeds 0-4 | results/runs.jsonl |
| `dropped_pct_digits_n0` | 3.46858 | mean percent of the 1257 digits training samples dropped by the filter at 0% noise, seeds 0-4 | results/runs.jsonl |
| `dz_bc20_filter_vs_lr` | 0.890871 | Cohen's dz of paired filter minus logreg accuracy difference, 5 seeds, breast_cancer, 20% noise | results/runs.jsonl |
| `dz_bc20_filter_vs_mlp` | 2.81193 | Cohen's dz of paired filter minus mlp accuracy difference, 5 seeds, breast_cancer, 20% noise | results/runs.jsonl |
| `dz_bc40_filter_vs_lr` | 2.71888 | Cohen's dz of paired filter minus logreg accuracy difference, 5 seeds, breast_cancer, 40% noise | results/runs.jsonl |
| `dz_bc40_filter_vs_mlp` | 4.62867 | Cohen's dz of paired filter minus mlp accuracy difference, 5 seeds, breast_cancer, 40% noise | results/runs.jsonl |
| `dz_dg0_filter_vs_lr` | -0.289346 | Cohen's dz of paired filter minus logreg accuracy difference, 5 seeds, digits, 0% noise | results/runs.jsonl |
| `dz_dg20_filter_vs_lr` | 4.24337 | Cohen's dz of paired filter minus logreg accuracy difference, 5 seeds, digits, 20% noise | results/runs.jsonl |
| `dz_dg20_filter_vs_mlp` | 5.56786 | Cohen's dz of paired filter minus mlp accuracy difference, 5 seeds, digits, 20% noise | results/runs.jsonl |
| `dz_dg40_filter_vs_lr` | 3.99517 | Cohen's dz of paired filter minus logreg accuracy difference, 5 seeds, digits, 40% noise | results/runs.jsonl |
| `dz_dg40_filter_vs_mlp` | 6.76245 | Cohen's dz of paired filter minus mlp accuracy difference, 5 seeds, digits, 40% noise | results/runs.jsonl |
| `filter_folds` | 5 | number of cross-validation folds used by the filter, from the config | experiments/config.json |
| `lift_breast_cancer_n20` | 57.157 | mean filter precision minus mean realized flip rate (percentage points), breast_cancer, 20% noise | results/runs.jsonl |
| `lift_breast_cancer_n40` | 29.6578 | mean filter precision minus mean realized flip rate (percentage points), breast_cancer, 40% noise | results/runs.jsonl |
| `lift_digits_n20` | 44.9162 | mean filter precision minus mean realized flip rate (percentage points), digits, 20% noise | results/runs.jsonl |
| `lift_digits_n40` | 36.7416 | mean filter precision minus mean realized flip rate (percentage points), digits, 40% noise | results/runs.jsonl |
| `logreg_C` | 1 | inverse regularization strength C of logistic regression, from the config | experiments/config.json |
| `loss_logreg_breast_cancer_n20` | 4.44444 | accuracy (points) logreg loses on breast_cancer at 20% noise: mean at 0% minus mean at 20%, seeds 0-4 | results/runs.jsonl |
| `loss_logreg_breast_cancer_n40` | 16.3743 | accuracy (points) logreg loses on breast_cancer at 40% noise: mean at 0% minus mean at 40%, seeds 0-4 | results/runs.jsonl |
| `loss_logreg_digits_n20` | 7.7037 | accuracy (points) logreg loses on digits at 20% noise: mean at 0% minus mean at 20%, seeds 0-4 | results/runs.jsonl |
| `loss_logreg_digits_n40` | 13.2222 | accuracy (points) logreg loses on digits at 40% noise: mean at 0% minus mean at 40%, seeds 0-4 | results/runs.jsonl |
| `mlp_hidden` | 64 | hidden units of the MLP (one hidden layer), from the config | experiments/config.json |
| `mlp_max_iter` | 500 | maximum training iterations of the MLP, from the config | experiments/config.json |
| `n_datasets` | 2 | number of datasets in the config | experiments/config.json |
| `n_noise_rates` | 3 | number of noise rates in the config, including 0% | experiments/config.json |
| `n_runs` | 90 | number of records in results/runs.jsonl (datasets x noise rates x seeds x methods) | results/runs.jsonl |
| `n_seeds` | 5 | number of seeds in the config | experiments/config.json |
| `n_test_breast_cancer` | 171 | number of test samples in breast_cancer (30% split) | results/runs.jsonl |
| `n_test_digits` | 540 | number of test samples in digits (30% split) | results/runs.jsonl |
| `n_total_breast_cancer` | 569 | total samples in breast_cancer (n_train + n_test) | results/runs.jsonl |
| `n_total_digits` | 1797 | total samples in digits (n_train + n_test) | results/runs.jsonl |
| `n_train_breast_cancer` | 398 | number of training samples in breast_cancer (70% split) | results/runs.jsonl |
| `n_train_digits` | 1257 | number of training samples in digits (70% split) | results/runs.jsonl |
| `noise_high_pct` | 40 | highest label-noise rate (%) from the config | experiments/config.json |
| `noise_low_pct` | 20 | lower non-zero label-noise rate (%) from the config | experiments/config.json |
| `noisy_pct_breast_cancer_n20` | 19.196 | mean realized percent of breast_cancer training labels flipped at nominal 20% noise, seeds 0-4 | results/runs.jsonl |
| `noisy_pct_breast_cancer_n40` | 38.593 | mean realized percent of breast_cancer training labels flipped at nominal 40% noise, seeds 0-4 | results/runs.jsonl |
| `noisy_pct_digits_n20` | 19.6977 | mean realized percent of digits training labels flipped at nominal 20% noise, seeds 0-4 | results/runs.jsonl |
| `noisy_pct_digits_n40` | 39.3636 | mean realized percent of digits training labels flipped at nominal 40% noise, seeds 0-4 | results/runs.jsonl |
| `nwin_lr_breast_cancer_n20` | 4 | number of seeds out of 5 where filter beats logreg, breast_cancer, 20% noise | results/runs.jsonl |
| `nwin_lr_breast_cancer_n40` | 5 | number of seeds out of 5 where filter beats logreg, breast_cancer, 40% noise | results/runs.jsonl |
| `nwin_lr_digits_n20` | 5 | number of seeds out of 5 where filter beats logreg, digits, 20% noise | results/runs.jsonl |
| `nwin_lr_digits_n40` | 5 | number of seeds out of 5 where filter beats logreg, digits, 40% noise | results/runs.jsonl |
| `nwins_filter_logreg_clean` | 3 | number of (dataset, seed) runs at 0% noise, out of 10, where filter test accuracy exceeds logreg | results/runs.jsonl |
| `nwins_filter_logreg_noisy` | 19 | number of (dataset, noise in {20%, 40%}, seed) runs, out of 20, where filter test accuracy exceeds logreg | results/runs.jsonl |
| `nwins_filter_mlp_noisy` | 20 | number of (dataset, noise in {20%, 40%}, seed) runs, out of 20, where filter test accuracy exceeds mlp | results/runs.jsonl |
| `one_sample_pts_breast_cancer` | 0.584795 | accuracy points that one test sample is worth on breast_cancer: 100 / n_test | results/runs.jsonl |
| `one_sample_pts_digits` | 0.185185 | accuracy points that one test sample is worth on digits: 100 / n_test | results/runs.jsonl |
| `p_bc0_filter_vs_lr` | 0.373901 | p-value, two-sided paired t-test over 5 seeds, filter vs logreg test accuracy, breast_cancer, 0% noise | results/runs.jsonl |
| `p_bc0_filter_vs_mlp` | 0.704 | p-value, two-sided paired t-test over 5 seeds, filter vs mlp test accuracy, breast_cancer, 0% noise | results/runs.jsonl |
| `p_bc20_filter_vs_lr` | 0.117176 | p-value, two-sided paired t-test over 5 seeds, filter vs logreg test accuracy, breast_cancer, 20% noise | results/runs.jsonl |
| `p_bc20_filter_vs_mlp` | 0.00326808 | p-value, two-sided paired t-test over 5 seeds, filter vs mlp test accuracy, breast_cancer, 20% noise | results/runs.jsonl |
| `p_bc40_filter_vs_lr` | 0.00369925 | p-value, two-sided paired t-test over 5 seeds, filter vs logreg test accuracy, breast_cancer, 40% noise | results/runs.jsonl |
| `p_bc40_filter_vs_mlp` | 0.000491848 | p-value, two-sided paired t-test over 5 seeds, filter vs mlp test accuracy, breast_cancer, 40% noise | results/runs.jsonl |
| `p_dg0_filter_vs_lr` | 0.552889 | p-value, two-sided paired t-test over 5 seeds, filter vs logreg test accuracy, digits, 0% noise | results/runs.jsonl |
| `p_dg0_filter_vs_mlp` | 0.0309058 | p-value, two-sided paired t-test over 5 seeds, filter vs mlp test accuracy, digits, 0% noise | results/runs.jsonl |
| `p_dg20_filter_vs_lr` | 0.000688454 | p-value, two-sided paired t-test over 5 seeds, filter vs logreg test accuracy, digits, 20% noise | results/runs.jsonl |
| `p_dg20_filter_vs_mlp` | 0.000239335 | p-value, two-sided paired t-test over 5 seeds, filter vs mlp test accuracy, digits, 20% noise | results/runs.jsonl |
| `p_dg40_filter_vs_lr` | 0.00086823 | p-value, two-sided paired t-test over 5 seeds, filter vs logreg test accuracy, digits, 40% noise | results/runs.jsonl |
| `p_dg40_filter_vs_mlp` | 0.000111491 | p-value, two-sided paired t-test over 5 seeds, filter vs mlp test accuracy, digits, 40% noise | results/runs.jsonl |
| `p_prec_bc20_gt50` | 6.52046e-05 | p-value, two-sided one-sample t-test (paired against constant 50) over 5 seeds, filter precision (%), breast_cancer, 20% noise | results/runs.jsonl |
| `p_prec_bc40_gt50` | 0.000545144 | p-value, two-sided one-sample t-test (paired against constant 50) over 5 seeds, filter precision (%), breast_cancer, 40% noise | results/runs.jsonl |
| `p_prec_dg20_gt50` | 0.000151772 | p-value, two-sided one-sample t-test (paired against constant 50) over 5 seeds, filter precision (%), digits, 20% noise | results/runs.jsonl |
| `p_prec_dg40_gt50` | 2.1437e-07 | p-value, two-sided one-sample t-test (paired against constant 50) over 5 seeds, filter precision (%), digits, 40% noise | results/runs.jsonl |
| `p_trend_bc_gain_lr` | 0.663335 | p-value, two-sided paired t-test over 5 seeds, per-seed filter-minus-logreg gain at 40% vs 20% noise, breast_cancer | results/runs.jsonl |
| `p_trend_bc_gain_mlp` | 0.0531733 | p-value, two-sided paired t-test over 5 seeds, per-seed filter-minus-mlp gain at 40% vs 20% noise, breast_cancer | results/runs.jsonl |
| `p_trend_dg_gain_lr` | 0.00247732 | p-value, two-sided paired t-test over 5 seeds, per-seed filter-minus-logreg gain at 40% vs 20% noise, digits | results/runs.jsonl |
| `p_trend_dg_gain_mlp` | 0.00046115 | p-value, two-sided paired t-test over 5 seeds, per-seed filter-minus-mlp gain at 40% vs 20% noise, digits | results/runs.jsonl |
| `precision_breast_cancer_n20` | 76.353 | mean over seeds 0-4 of filter precision (%), dropped samples truly flipped, breast_cancer, 20% noise | results/runs.jsonl |
| `precision_breast_cancer_n40` | 68.2508 | mean over seeds 0-4 of filter precision (%), dropped samples truly flipped, breast_cancer, 40% noise | results/runs.jsonl |
| `precision_digits_n20` | 64.6139 | mean over seeds 0-4 of filter precision (%), dropped samples truly flipped, digits, 20% noise | results/runs.jsonl |
| `precision_digits_n40` | 76.1051 | mean over seeds 0-4 of filter precision (%), dropped samples truly flipped, digits, 40% noise | results/runs.jsonl |
| `precision_min_breast_cancer_n40` | 63.1016 | lowest per-seed filter precision (%) over seeds 0-4, breast_cancer, 40% noise | results/runs.jsonl |
| `precision_min_digits_n40` | 75.3106 | lowest per-seed filter precision (%) over seeds 0-4, digits, 40% noise | results/runs.jsonl |
| `precision_pooled_noisy` | 71.3307 | mean filter precision (%) over both datasets, 20% and 40% noise, seeds 0-4 (20 runs) | results/runs.jsonl |
| `recall_breast_cancer_n20` | 92.5165 | mean over seeds 0-4 of filter recall (%), flipped samples dropped, breast_cancer, 20% noise | results/runs.jsonl |
| `recall_breast_cancer_n40` | 78.9076 | mean over seeds 0-4 of filter recall (%), flipped samples dropped, breast_cancer, 40% noise | results/runs.jsonl |
| `recall_digits_n20` | 98.4639 | mean over seeds 0-4 of filter recall (%), flipped samples dropped, digits, 20% noise | results/runs.jsonl |
| `recall_digits_n40` | 97.5422 | mean over seeds 0-4 of filter recall (%), flipped samples dropped, digits, 40% noise | results/runs.jsonl |
| `recovered_breast_cancer_n20` | 65.7895 | percent of logreg's accuracy loss at 20% noise on breast_cancer regained by filter: (filter - logreg)/(logreg at 0% - logreg), means over seeds 0-4 | results/runs.jsonl |
| `recovered_breast_cancer_n40` | 22.1429 | percent of logreg's accuracy loss at 40% noise on breast_cancer regained by filter: (filter - logreg)/(logreg at 0% - logreg), means over seeds 0-4 | results/runs.jsonl |
| `recovered_digits_n20` | 77.8846 | percent of logreg's accuracy loss at 20% noise on digits regained by filter: (filter - logreg)/(logreg at 0% - logreg), means over seeds 0-4 | results/runs.jsonl |
| `recovered_digits_n40` | 68.3473 | percent of logreg's accuracy loss at 40% noise on digits regained by filter: (filter - logreg)/(logreg at 0% - logreg), means over seeds 0-4 | results/runs.jsonl |
| `sd_filter_breast_cancer_n0` | 0.960917 | sample sd (points) over seeds 0-4 of test accuracy, filter, breast_cancer, 0% noise | results/runs.jsonl |
| `sd_filter_breast_cancer_n20` | 0.76248 | sample sd (points) over seeds 0-4 of test accuracy, filter, breast_cancer, 20% noise | results/runs.jsonl |
| `sd_filter_breast_cancer_n40` | 8.95138 | sample sd (points) over seeds 0-4 of test accuracy, filter, breast_cancer, 40% noise | results/runs.jsonl |
| `sd_filter_digits_n0` | 0.360992 | sample sd (points) over seeds 0-4 of test accuracy, filter, digits, 0% noise | results/runs.jsonl |
| `sd_filter_digits_n20` | 0.874498 | sample sd (points) over seeds 0-4 of test accuracy, filter, digits, 20% noise | results/runs.jsonl |
| `sd_filter_digits_n40` | 1.59517 | sample sd (points) over seeds 0-4 of test accuracy, filter, digits, 40% noise | results/runs.jsonl |
| `sd_logreg_breast_cancer_n0` | 1.21266 | sample sd (points) over seeds 0-4 of test accuracy, logreg, breast_cancer, 0% noise | results/runs.jsonl |
| `sd_logreg_breast_cancer_n20` | 3.73079 | sample sd (points) over seeds 0-4 of test accuracy, logreg, breast_cancer, 20% noise | results/runs.jsonl |
| `sd_logreg_breast_cancer_n40` | 9.38956 | sample sd (points) over seeds 0-4 of test accuracy, logreg, breast_cancer, 40% noise | results/runs.jsonl |
| `sd_logreg_digits_n0` | 0.821939 | sample sd (points) over seeds 0-4 of test accuracy, logreg, digits, 0% noise | results/runs.jsonl |
| `sd_logreg_digits_n20` | 0.974644 | sample sd (points) over seeds 0-4 of test accuracy, logreg, digits, 20% noise | results/runs.jsonl |
| `sd_logreg_digits_n40` | 1.25325 | sample sd (points) over seeds 0-4 of test accuracy, logreg, digits, 40% noise | results/runs.jsonl |
| `sd_mlp_breast_cancer_n0` | 1.21266 | sample sd (points) over seeds 0-4 of test accuracy, mlp, breast_cancer, 0% noise | results/runs.jsonl |
| `sd_mlp_breast_cancer_n20` | 3.98777 | sample sd (points) over seeds 0-4 of test accuracy, mlp, breast_cancer, 20% noise | results/runs.jsonl |
| `sd_mlp_breast_cancer_n40` | 5.42947 | sample sd (points) over seeds 0-4 of test accuracy, mlp, breast_cancer, 40% noise | results/runs.jsonl |
| `sd_mlp_digits_n0` | 0.549348 | sample sd (points) over seeds 0-4 of test accuracy, mlp, digits, 0% noise | results/runs.jsonl |
| `sd_mlp_digits_n20` | 1.63551 | sample sd (points) over seeds 0-4 of test accuracy, mlp, digits, 20% noise | results/runs.jsonl |
| `sd_mlp_digits_n40` | 3.11695 | sample sd (points) over seeds 0-4 of test accuracy, mlp, digits, 40% noise | results/runs.jsonl |
| `test_fraction_pct` | 30 | test split fraction (%) from the config | experiments/config.json |
| `time_filter_over_logreg_digits_n0` | 5.02385 | ratio of mean fit_seconds, filter over logreg, digits, 0% noise, seeds 0-4 (indicative; machine unknown) | results/runs.jsonl |
| `trend_bc_gain_lr_ci_high` | 3.27485 | upper end of 95% CI (points) of per-seed filter-minus-logreg gain, 40% minus 20% noise, breast_cancer, 5 seeds | results/runs.jsonl |
| `trend_bc_gain_lr_ci_low` | -1.87135 | lower end of 95% CI (points) of per-seed filter-minus-logreg gain, 40% minus 20% noise, breast_cancer, 5 seeds | results/runs.jsonl |
| `trend_dg_gain_lr_ci_high` | 3.85185 | upper end of 95% CI (points) of per-seed filter-minus-logreg gain, 40% minus 20% noise, digits, 5 seeds | results/runs.jsonl |
| `trend_dg_gain_lr_ci_low` | 2.2963 | lower end of 95% CI (points) of per-seed filter-minus-logreg gain, 40% minus 20% noise, digits, 5 seeds | results/runs.jsonl |
