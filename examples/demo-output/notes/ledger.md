# Claim ledger

The paper may make only these claims, at this scope. Strong claims can be stated directly; weak claims are stated with their limits; unsupported claims are never made.

- **filter_method** (method, strong): The filter fits logistic regression with 5-fold cross-validation on the noisy labels, drops every training sample whose out-of-fold prediction disagrees with its given label, and refits on the rest.  
  Scope: logistic regression with standardized features, C = 1, 5 folds. Evidence: `filter_folds`, `logreg_c`.
- **filter_needs_no_side_information** (method, strong): The filter needs no clean validation set and no estimate of the noise rate.  
  Scope: the implementation in experiments/run.py. Evidence: `filter_folds`.
- **noise_hurts_logreg** (comparison, strong): Symmetric label noise at 40% lowers the test accuracy of logistic regression on both datasets, by about 13 points on digits and 16 points on breast cancer.  
  Scope: digits, breast cancer; 0% vs 40% symmetric noise; 5 paired seeds. Evidence: `loss_digits_n40`, `loss_bc_n40`, `acc_digits_n0_logreg`, `acc_digits_n40_logreg`, `acc_bc_n0_logreg`, `acc_bc_n40_logreg`, `p_dg_loss_n40`, `p_bc_loss_n40`.
- **filter_beats_logreg_digits** (comparison, strong): On digits, the filter beats logistic regression trained on the noisy labels at both 20% and 40% symmetric noise.  
  Scope: digits; 20% and 40% symmetric noise; 5 paired seeds. Evidence: `acc_digits_n20_filter`, `acc_digits_n20_logreg`, `acc_digits_n40_filter`, `acc_digits_n40_logreg`, `gain_digits_n20_vs_logreg`, `gain_digits_n40_vs_logreg`, `dz_dg20_filter_vs_logreg`, `dz_dg40_filter_vs_logreg`, `dg20_logreg_diff_ci_low`, `dg20_logreg_diff_ci_high`, `dg40_logreg_diff_ci_low`, `dg40_logreg_diff_ci_high`, `p_dg20_filter_vs_logreg`, `p_dg40_filter_vs_logreg`.
- **filter_beats_logreg_bc40** (comparison, strong): On breast cancer at 40% symmetric noise, the filter beats logistic regression trained on the noisy labels by about 4 points.  
  Scope: breast cancer; 40% symmetric noise; 5 paired seeds. Evidence: `acc_bc_n40_filter`, `acc_bc_n40_logreg`, `gain_bc_n40_vs_logreg`, `dz_bc40_filter_vs_logreg`, `bc40_logreg_diff_ci_low`, `bc40_logreg_diff_ci_high`, `p_bc40_filter_vs_logreg`.
- **filter_bc20_gain_not_significant** (limitation, weak): On breast cancer at 20% noise the filter gains about 3 points over logistic regression, but this gain is not statistically significant with 5 seeds.  
  Scope: breast cancer; 20% symmetric noise; 5 paired seeds. Evidence: `acc_bc_n20_filter`, `acc_bc_n20_logreg`, `gain_bc_n20_vs_logreg`, `dz_bc20_filter_vs_logreg`, `bc20_logreg_diff_ci_low`, `bc20_logreg_diff_ci_high`, `p_bc20_filter_vs_logreg`.
- **filter_recovers_most_on_digits** (result, strong): On digits, the filter wins back most of the accuracy that noise costs logistic regression: about 78% at 20% noise and 68% at 40% noise, measured against logistic regression on clean labels.  
  Scope: digits; 20% and 40% noise; ratio of 5-seed means; the clean-label logistic regression is the reference, no oracle run exists. Evidence: `recovery_digits_n20`, `recovery_digits_n40`, `recovery_seed_mean_digits_n40`, `loss_digits_n20`, `loss_digits_n40`, `gain_digits_n20_vs_logreg`, `gain_digits_n40_vs_logreg`, `p_dg20_filter_vs_logreg`, `p_dg40_filter_vs_logreg`.
- **filter_recovers_part_on_bc** (limitation, weak): On breast cancer the filter recovers about two thirds of the lost accuracy at 20% noise but only about one fifth at 40% noise, so the brief's 'most' does not hold at 40%.  
  Scope: breast cancer; 20% and 40% noise; ratio of 5-seed means; per-seed ratios at 20% are unstable because the loss is only 4.4 points. Evidence: `recovery_bc_n20`, `recovery_bc_n40`, `recovery_seed_min_bc_n20`, `loss_bc_n20`, `loss_bc_n40`, `gain_bc_n40_vs_logreg`, `sd_bc_n40_filter`, `sd_bc_n40_logreg`, `p_bc20_filter_vs_logreg`.
- **filter_below_clean_at_40** (comparison, strong): At 40% noise the filter does not return to the clean-label accuracy of logistic regression on either dataset.  
  Scope: digits and breast cancer; 40% symmetric noise; filter vs logistic regression at 0% noise; 5 paired seeds. Evidence: `acc_digits_n40_filter`, `acc_digits_n0_logreg`, `acc_bc_n40_filter`, `acc_bc_n0_logreg`, `p_dg40_filter_vs_clean`, `p_bc40_filter_vs_clean`.
- **dropped_samples_mostly_mislabeled** (result, strong): Most of the samples the filter drops are truly mislabeled: mean precision is 65 to 76% across both datasets at 20% and 40% noise.  
  Scope: digits, breast cancer; 20% and 40% symmetric noise; 5 seeds; not defined at 0% noise. Evidence: `prec_digits_n20`, `prec_digits_n40`, `prec_bc_n20`, `prec_bc_n40`, `prec_min_any`, `sd_prec_digits_n20`, `sd_prec_digits_n40`, `sd_prec_bc_n20`, `sd_prec_bc_n40`, `p_dg20_prec_vs_half`, `p_dg40_prec_vs_half`, `p_bc20_prec_vs_half`, `p_bc40_prec_vs_half`.
- **filter_recall_high** (result, strong): The filter drops most of the flipped labels: recall is 79 to 98% across the four noisy cells, highest on digits.  
  Scope: digits, breast cancer; 20% and 40% noise; 5 seeds. Evidence: `rec_digits_n20`, `rec_digits_n40`, `rec_bc_n20`, `rec_bc_n40`, `dropped_frac_digits_n20`, `dropped_frac_digits_n40`, `dropped_frac_bc_n20`, `dropped_frac_bc_n40`.
- **filter_drops_clean_samples** (limitation, strong): The filter also discards correct samples: a quarter to a third of the dropped samples are clean at 20% and 40% noise, and it drops 3.5% (digits) and 1.9% (breast cancer) of the training set when labels are clean.  
  Scope: digits, breast cancer; all noise rates; 5 seeds. Evidence: `prec_digits_n20`, `prec_digits_n40`, `prec_bc_n20`, `prec_bc_n40`, `prec_min_any`, `dropped_frac_digits_n0`, `dropped_frac_bc_n0`.
- **filter_beats_mlp_noisy** (comparison, strong): At 20% and 40% symmetric noise the filter beats an MLP trained on the same noisy labels on both datasets, by 11 to 28 points, and wins in all 5 seeds in every cell.  
  Scope: digits, breast cancer; 20% and 40% symmetric noise; one MLP (64 hidden units, sklearn defaults, 500 iterations, untuned); 5 paired seeds. Evidence: `acc_digits_n20_filter`, `acc_digits_n20_mlp`, `acc_digits_n40_filter`, `acc_digits_n40_mlp`, `acc_bc_n20_filter`, `acc_bc_n20_mlp`, `acc_bc_n40_filter`, `acc_bc_n40_mlp`, `gain_digits_n20_vs_mlp`, `gain_digits_n40_vs_mlp`, `gain_bc_n20_vs_mlp`, `gain_bc_n40_vs_mlp`, `n_seeds_filter_wins_mlp_digits_n20`, `n_seeds_filter_wins_mlp_digits_n40`, `n_seeds_filter_wins_mlp_bc_n20`, `n_seeds_filter_wins_mlp_bc_n40`, `dg20_mlp_diff_ci_low`, `dg20_mlp_diff_ci_high`, `dg40_mlp_diff_ci_low`, `dg40_mlp_diff_ci_high`, `bc20_mlp_diff_ci_low`, `bc20_mlp_diff_ci_high`, `bc40_mlp_diff_ci_low`, `bc40_mlp_diff_ci_high`, `mlp_hidden`, `mlp_max_iter`, `p_dg20_filter_vs_mlp`, `p_dg40_filter_vs_mlp`, `p_bc20_filter_vs_mlp`, `p_bc40_filter_vs_mlp`.
- **mlp_collapses_under_noise** (trend, weak): The untuned MLP degrades faster with label noise than the linear model and falls to about 65% accuracy at 40% noise on both datasets.  
  Scope: digits, breast cancer; 0, 20, 40% noise; one untuned MLP; no test on the MLP's own trend. Evidence: `acc_digits_n0_mlp`, `acc_digits_n20_mlp`, `acc_digits_n40_mlp`, `acc_bc_n0_mlp`, `acc_bc_n20_mlp`, `acc_bc_n40_mlp`, `acc_digits_n40_logreg`, `acc_bc_n40_logreg`.
- **mlp_ahead_on_clean_digits** (comparison, strong): On clean digits the MLP is ahead of the filter by about 0.7 points.  
  Scope: digits; 0% noise; 5 paired seeds. Evidence: `acc_digits_n0_mlp`, `acc_digits_n0_filter`, `gain_digits_n0_vs_mlp`, `p_dg0_filter_vs_mlp`.
- **mlp_level_on_clean_bc** (comparison, weak): On clean breast cancer the filter and the MLP are level.  
  Scope: breast cancer; 0% noise; 5 paired seeds; no difference detected, not proof of equality. Evidence: `acc_bc_n0_mlp`, `acc_bc_n0_filter`, `gain_bc_n0_vs_mlp`, `p_bc0_filter_vs_mlp`.
- **clean_cost_small** (result, strong): On clean labels the filter costs little: the mean accuracy change against logistic regression is -0.2 points on digits and -0.1 points on breast cancer, and neither is statistically significant.  
  Scope: digits, breast cancer; 0% noise; 5 paired seeds; interval from about -0.9 to +0.3 (digits) and -0.35 to 0 (breast cancer). Evidence: `gain_digits_n0_vs_logreg`, `gain_bc_n0_vs_logreg`, `acc_digits_n0_filter`, `acc_digits_n0_logreg`, `acc_bc_n0_filter`, `acc_bc_n0_logreg`, `dg0_logreg_diff_ci_low`, `dg0_logreg_diff_ci_high`, `bc0_logreg_diff_ci_low`, `bc0_logreg_diff_ci_high`, `p_dg0_filter_vs_logreg`, `p_bc0_filter_vs_logreg`.
- **filter_compute_cost** (result, weak): The filter is about 5 times slower to fit than plain logistic regression on digits (0.056 s against 0.012 s), still faster than the MLP.  
  Scope: digits; mean of 15 runs; single wall-clock timing on an unrecorded machine. Evidence: `fit_sec_digits_filter`, `fit_sec_digits_logreg`, `fit_sec_digits_mlp`.
- **study_scope_limits** (scope, strong): The study covers two small scikit-learn datasets, symmetric noise only, rates up to 40%, 5 seeds, one fixed K and C, and no hyperparameter sensitivity analysis.  
  Scope: whole study; 90 runs; the sampled flip rate is slightly below nominal (39.4% and 38.6% at 40%). Evidence: `n_runs_total`, `n_datasets`, `n_noise_rates`, `n_seeds`, `noise_max_pct`, `n_train_digits`, `n_test_digits`, `n_train_bc`, `n_test_bc`, `test_fraction_pct`, `actual_noise_digits_n40`, `actual_noise_bc_n40`.
- **no_prior_method_comparison** (limitation, strong): The filter was not compared with co-teaching or confident learning, so the paper cannot claim it outperforms other noise-robust methods.  
  Scope: whole study; those methods were not run. Evidence: `n_runs_total`.
- **scales_to_deep_or_large_unsupported** (scope, unsupported): The filter scales to deep networks or large datasets.  
  Scope: not tested; the data are two small datasets and linear and one-hidden-layer models. Evidence: `n_total_digits`, `n_total_bc`.
- **contribution_filter_study** (contribution, weak): We propose a simple out-of-fold filter for linear models under label noise and show on two small datasets that it recovers much of the lost accuracy, drops mostly mislabeled samples, beats an untuned MLP under noise and costs little on clean labels.  
  Scope: digits, breast cancer; symmetric noise up to 40%; see the claims it rests on. Evidence: `gain_digits_n40_vs_logreg`, `prec_digits_n40`, `p_dg40_filter_vs_logreg`, `p_dg40_filter_vs_mlp`.

## Claims in the brief

- The filter recovers most of the accuracy that label noise costs a linear model.: narrowed. Holds on digits (68 to 78%); on breast cancer about 66% at 20% noise but only 22% at 40%.
- Most of the samples it drops are truly mislabeled.: supported. Precision is 65 to 76% with p < 0.001 in each noisy cell; a quarter to a third of drops are clean.
- It beats a larger model (an MLP) trained on the same noisy labels.: narrowed. True at 20% and 40% noise for one untuned MLP; the MLP is ahead on clean digits.
- It costs little when the labels are clean.: supported. Changes of -0.2 and -0.1 points, not significant; training time is about 5 times higher.
- Do not claim it scales to deep networks or large data.: unsupported. Only two small datasets were run.
- Cite co-teaching, confident learning and the Song et al. survey.: narrowed. They can be cited as related work but were not run, so no comparison is claimed.
