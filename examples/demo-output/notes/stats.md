# Statistical tests

| comparison | setting | test | p | verdict |
|---|---|---|---|---|
| filter vs logreg | digits, noise 0, 5 seeds (cost when labels are clean) | `p_dg0_filter_vs_lr` | 0.553 | not significant |
| filter vs logreg | digits, noise 0.2, 5 seeds | `p_dg20_filter_vs_lr` | 0.000688 | significant |
| filter vs logreg | digits, noise 0.4, 5 seeds | `p_dg40_filter_vs_lr` | 0.000868 | significant |
| filter vs logreg | breast_cancer, noise 0, 5 seeds (cost when labels are clean) | `p_bc0_filter_vs_lr` | 0.374 | not significant |
| filter vs logreg | breast_cancer, noise 0.2, 5 seeds | `p_bc20_filter_vs_lr` | 0.117 | not significant |
| filter vs logreg | breast_cancer, noise 0.4, 5 seeds | `p_bc40_filter_vs_lr` | 0.0037 | significant |
| filter vs mlp | digits, noise 0, 5 seeds (significant, but the MLP is better: filter minus mlp is negative) | `p_dg0_filter_vs_mlp` | 0.0309 | significant |
| filter vs mlp | digits, noise 0.2, 5 seeds | `p_dg20_filter_vs_mlp` | 0.000239 | significant |
| filter vs mlp | digits, noise 0.4, 5 seeds | `p_dg40_filter_vs_mlp` | 0.000111 | significant |
| filter vs mlp | breast_cancer, noise 0, 5 seeds | `p_bc0_filter_vs_mlp` | 0.704 | not significant |
| filter vs mlp | breast_cancer, noise 0.2, 5 seeds | `p_bc20_filter_vs_mlp` | 0.00327 | significant |
| filter vs mlp | breast_cancer, noise 0.4, 5 seeds | `p_bc40_filter_vs_mlp` | 0.000492 | significant |
| filter gain over logreg at noise 0.4 vs filter gain over logreg at noise 0.2 | digits, paired by seed, 5 seeds (gain grows with noise) | `p_trend_dg_gain_lr` | 0.00248 | significant |
| filter gain over logreg at noise 0.4 vs filter gain over logreg at noise 0.2 | breast_cancer, paired by seed, 5 seeds (gain grows with noise) | `p_trend_bc_gain_lr` | 0.663 | not significant |
| filter gain over mlp at noise 0.4 vs filter gain over mlp at noise 0.2 | digits, paired by seed, 5 seeds | `p_trend_dg_gain_mlp` | 0.000461 | significant |
| filter gain over mlp at noise 0.4 vs filter gain over mlp at noise 0.2 | breast_cancer, paired by seed, 5 seeds | `p_trend_bc_gain_mlp` | 0.0532 | not significant |
| filter precision vs 50% (chance of a dropped sample being flipped) | digits, noise 0.2, one-sample t over 5 seeds | `p_prec_dg20_gt50` | 0.000152 | significant |
| filter precision vs 50% | digits, noise 0.4, one-sample t over 5 seeds | `p_prec_dg40_gt50` | 2.14e-07 | significant |
| filter precision vs 50% | breast_cancer, noise 0.2, one-sample t over 5 seeds | `p_prec_bc20_gt50` | 6.52e-05 | significant |
| filter precision vs 50% | breast_cancer, noise 0.4, one-sample t over 5 seeds | `p_prec_bc40_gt50` | 0.000545 | significant |
| filter vs logreg loss under noise | share of logreg's accuracy loss regained, per dataset and noise rate | `-` |  | untestable |
