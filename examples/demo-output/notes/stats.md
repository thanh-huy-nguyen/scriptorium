# Statistical tests

| comparison | setting | test | p | verdict |
|---|---|---|---|---|
| filter vs logistic regression | digits, noise 0.2, 5 paired seeds | `p_dg20_filter_vs_logreg` | 0.000688 | significant |
| filter vs logistic regression | digits, noise 0.4, 5 paired seeds | `p_dg40_filter_vs_logreg` | 0.000868 | significant |
| filter vs logistic regression | breast_cancer, noise 0.2, 5 paired seeds | `p_bc20_filter_vs_logreg` | 0.117 | not significant |
| filter vs logistic regression | breast_cancer, noise 0.4, 5 paired seeds | `p_bc40_filter_vs_logreg` | 0.0037 | significant |
| filter vs logistic regression | digits, noise 0.0 (cost on clean labels), 5 paired seeds | `p_dg0_filter_vs_logreg` | 0.553 | not significant |
| filter vs logistic regression | breast_cancer, noise 0.0 (cost on clean labels), 5 paired seeds | `p_bc0_filter_vs_logreg` | 0.374 | not significant |
| filter vs MLP | digits, noise 0.2, 5 paired seeds | `p_dg20_filter_vs_mlp` | 0.000239 | significant |
| filter vs MLP | digits, noise 0.4, 5 paired seeds | `p_dg40_filter_vs_mlp` | 0.000111 | significant |
| filter vs MLP | breast_cancer, noise 0.2, 5 paired seeds | `p_bc20_filter_vs_mlp` | 0.00327 | significant |
| filter vs MLP | breast_cancer, noise 0.4, 5 paired seeds | `p_bc40_filter_vs_mlp` | 0.000492 | significant |
| filter vs MLP | digits, noise 0.0, 5 paired seeds (the MLP is ahead here) | `p_dg0_filter_vs_mlp` | 0.0309 | significant |
| filter vs MLP | breast_cancer, noise 0.0, 5 paired seeds | `p_bc0_filter_vs_mlp` | 0.704 | not significant |
| filter precision vs 50% | digits, noise 0.2, 5 seeds (most dropped samples are mislabeled) | `p_dg20_prec_vs_half` | 0.000152 | significant |
| filter precision vs 50% | digits, noise 0.4, 5 seeds | `p_dg40_prec_vs_half` | 2.14e-07 | significant |
| filter precision vs 50% | breast_cancer, noise 0.2, 5 seeds | `p_bc20_prec_vs_half` | 6.52e-05 | significant |
| filter precision vs 50% | breast_cancer, noise 0.4, 5 seeds | `p_bc40_prec_vs_half` | 0.000545 | significant |
| filter at noise 0.2 vs logistic regression on clean labels | digits, 5 paired seeds | `p_dg20_filter_vs_clean` | 0.053 | not significant |
| filter at noise 0.4 vs logistic regression on clean labels | digits, 5 paired seeds (filter is below clean) | `p_dg40_filter_vs_clean` | 0.0157 | significant |
| filter at noise 0.2 vs logistic regression on clean labels | breast_cancer, 5 paired seeds (filter is below clean; p is close to 0.05) | `p_bc20_filter_vs_clean` | 0.0486 | significant |
| filter at noise 0.4 vs logistic regression on clean labels | breast_cancer, 5 paired seeds (filter is below clean) | `p_bc40_filter_vs_clean` | 0.0275 | significant |
| logistic regression, noise 0.0 vs logistic regression, noise 0.4 | digits, 5 paired seeds (noise hurts) | `p_dg_loss_n40` | 6.11e-06 | significant |
| logistic regression, noise 0.0 vs logistic regression, noise 0.4 | breast_cancer, 5 paired seeds (noise hurts) | `p_bc_loss_n40` | 0.0144 | significant |
| filter vs co-teaching, confident learning | not run | `-` |  | untestable |
| filter recovery share vs 50% | share of lost accuracy recovered | `-` |  | untestable |
