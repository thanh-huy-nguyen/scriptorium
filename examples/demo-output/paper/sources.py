"""Recipes for the numbers in this paper. One function per key; values are unrounded.

Datasets: dg = digits, bc = breast_cancer. Noise: 00, 20, 40 = nominal label-flip rate 0.0, 0.2, 0.4.
Accuracies are in percent on the clean test split; mean/sd are over the 5 seeds (sd = sample sd).
"""

_DS = {"dg": "digits", "bc": "breast_cancer"}


def _rows(ds, nz, method):
    return sorted([r for r in load("results/runs.jsonl")
                   if r["dataset"] == _DS[ds] and abs(r["noise"] - nz / 100) < 1e-9 and r["method"] == method],
                  key=lambda r: r["seed"])


def _accs(ds, nz, m):
    return [100 * r["test_acc"] for r in _rows(ds, nz, m)]


def _mean(xs):
    return sum(xs) / len(xs)


def _sd(xs):
    import statistics
    return statistics.stdev(xs)


def _wins(ds, nz, a, b):
    return sum(x > y for x, y in zip(_accs(ds, nz, a), _accs(ds, nz, b)))


def _prec(ds, nz):
    return [100 * r["n_dropped_noisy"] / r["n_dropped"] for r in _rows(ds, nz, "filter")]


def _rec(ds, nz):
    return [100 * r["n_dropped_noisy"] / r["n_noisy"] for r in _rows(ds, nz, "filter")]


def _rcv(ds, nz):
    am = lambda n, m: _mean(_accs(ds, n, m))
    return (am(nz, "filter") - am(nz, "logreg")) / (am(0, "logreg") - am(nz, "logreg"))


# ---------------- main results: mean and sd of test accuracy (%) ----------------
# digits
@source("acc_dg_00_logreg_mean", means="test accuracy (%) on clean test split, digits, noise 0.0, logreg, mean over 5 seeds")
def acc_dg_00_logreg_mean(): return _mean(_accs("dg", 0, "logreg"))
@source("acc_dg_00_logreg_sd", means="sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.0, logreg")
def acc_dg_00_logreg_sd(): return _sd(_accs("dg", 0, "logreg"))
@source("acc_dg_00_mlp_mean", means="test accuracy (%) on clean test split, digits, noise 0.0, MLP, mean over 5 seeds")
def acc_dg_00_mlp_mean(): return _mean(_accs("dg", 0, "mlp"))
@source("acc_dg_00_mlp_sd", means="sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.0, MLP")
def acc_dg_00_mlp_sd(): return _sd(_accs("dg", 0, "mlp"))
@source("acc_dg_00_filter_mean", means="test accuracy (%) on clean test split, digits, noise 0.0, filter, mean over 5 seeds")
def acc_dg_00_filter_mean(): return _mean(_accs("dg", 0, "filter"))
@source("acc_dg_00_filter_sd", means="sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.0, filter")
def acc_dg_00_filter_sd(): return _sd(_accs("dg", 0, "filter"))

@source("acc_dg_20_logreg_mean", means="test accuracy (%) on clean test split, digits, noise 0.2, logreg on noisy labels, mean over 5 seeds")
def acc_dg_20_logreg_mean(): return _mean(_accs("dg", 20, "logreg"))
@source("acc_dg_20_logreg_sd", means="sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.2, logreg")
def acc_dg_20_logreg_sd(): return _sd(_accs("dg", 20, "logreg"))
@source("acc_dg_20_mlp_mean", means="test accuracy (%) on clean test split, digits, noise 0.2, MLP on noisy labels, mean over 5 seeds")
def acc_dg_20_mlp_mean(): return _mean(_accs("dg", 20, "mlp"))
@source("acc_dg_20_mlp_sd", means="sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.2, MLP")
def acc_dg_20_mlp_sd(): return _sd(_accs("dg", 20, "mlp"))
@source("acc_dg_20_filter_mean", means="test accuracy (%) on clean test split, digits, noise 0.2, filter, mean over 5 seeds")
def acc_dg_20_filter_mean(): return _mean(_accs("dg", 20, "filter"))
@source("acc_dg_20_filter_sd", means="sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.2, filter")
def acc_dg_20_filter_sd(): return _sd(_accs("dg", 20, "filter"))

@source("acc_dg_40_logreg_mean", means="test accuracy (%) on clean test split, digits, noise 0.4, logreg on noisy labels, mean over 5 seeds")
def acc_dg_40_logreg_mean(): return _mean(_accs("dg", 40, "logreg"))
@source("acc_dg_40_logreg_sd", means="sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.4, logreg")
def acc_dg_40_logreg_sd(): return _sd(_accs("dg", 40, "logreg"))
@source("acc_dg_40_mlp_mean", means="test accuracy (%) on clean test split, digits, noise 0.4, MLP on noisy labels, mean over 5 seeds")
def acc_dg_40_mlp_mean(): return _mean(_accs("dg", 40, "mlp"))
@source("acc_dg_40_mlp_sd", means="sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.4, MLP")
def acc_dg_40_mlp_sd(): return _sd(_accs("dg", 40, "mlp"))
@source("acc_dg_40_filter_mean", means="test accuracy (%) on clean test split, digits, noise 0.4, filter, mean over 5 seeds")
def acc_dg_40_filter_mean(): return _mean(_accs("dg", 40, "filter"))
@source("acc_dg_40_filter_sd", means="sample sd over 5 seeds of test accuracy (points of %), digits, noise 0.4, filter")
def acc_dg_40_filter_sd(): return _sd(_accs("dg", 40, "filter"))

# breast_cancer
@source("acc_bc_00_logreg_mean", means="test accuracy (%) on clean test split, breast_cancer, noise 0.0, logreg, mean over 5 seeds")
def acc_bc_00_logreg_mean(): return _mean(_accs("bc", 0, "logreg"))
@source("acc_bc_00_logreg_sd", means="sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.0, logreg")
def acc_bc_00_logreg_sd(): return _sd(_accs("bc", 0, "logreg"))
@source("acc_bc_00_mlp_mean", means="test accuracy (%) on clean test split, breast_cancer, noise 0.0, MLP, mean over 5 seeds")
def acc_bc_00_mlp_mean(): return _mean(_accs("bc", 0, "mlp"))
@source("acc_bc_00_mlp_sd", means="sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.0, MLP")
def acc_bc_00_mlp_sd(): return _sd(_accs("bc", 0, "mlp"))
@source("acc_bc_00_filter_mean", means="test accuracy (%) on clean test split, breast_cancer, noise 0.0, filter, mean over 5 seeds")
def acc_bc_00_filter_mean(): return _mean(_accs("bc", 0, "filter"))
@source("acc_bc_00_filter_sd", means="sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.0, filter")
def acc_bc_00_filter_sd(): return _sd(_accs("bc", 0, "filter"))

@source("acc_bc_20_logreg_mean", means="test accuracy (%) on clean test split, breast_cancer, noise 0.2, logreg on noisy labels, mean over 5 seeds")
def acc_bc_20_logreg_mean(): return _mean(_accs("bc", 20, "logreg"))
@source("acc_bc_20_logreg_sd", means="sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.2, logreg")
def acc_bc_20_logreg_sd(): return _sd(_accs("bc", 20, "logreg"))
@source("acc_bc_20_mlp_mean", means="test accuracy (%) on clean test split, breast_cancer, noise 0.2, MLP on noisy labels, mean over 5 seeds")
def acc_bc_20_mlp_mean(): return _mean(_accs("bc", 20, "mlp"))
@source("acc_bc_20_mlp_sd", means="sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.2, MLP")
def acc_bc_20_mlp_sd(): return _sd(_accs("bc", 20, "mlp"))
@source("acc_bc_20_filter_mean", means="test accuracy (%) on clean test split, breast_cancer, noise 0.2, filter, mean over 5 seeds")
def acc_bc_20_filter_mean(): return _mean(_accs("bc", 20, "filter"))
@source("acc_bc_20_filter_sd", means="sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.2, filter")
def acc_bc_20_filter_sd(): return _sd(_accs("bc", 20, "filter"))

@source("acc_bc_40_logreg_mean", means="test accuracy (%) on clean test split, breast_cancer, noise 0.4, logreg on noisy labels, mean over 5 seeds")
def acc_bc_40_logreg_mean(): return _mean(_accs("bc", 40, "logreg"))
@source("acc_bc_40_logreg_sd", means="sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.4, logreg")
def acc_bc_40_logreg_sd(): return _sd(_accs("bc", 40, "logreg"))
@source("acc_bc_40_mlp_mean", means="test accuracy (%) on clean test split, breast_cancer, noise 0.4, MLP on noisy labels, mean over 5 seeds")
def acc_bc_40_mlp_mean(): return _mean(_accs("bc", 40, "mlp"))
@source("acc_bc_40_mlp_sd", means="sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.4, MLP")
def acc_bc_40_mlp_sd(): return _sd(_accs("bc", 40, "mlp"))
@source("acc_bc_40_filter_mean", means="test accuracy (%) on clean test split, breast_cancer, noise 0.4, filter, mean over 5 seeds")
def acc_bc_40_filter_mean(): return _mean(_accs("bc", 40, "filter"))
@source("acc_bc_40_filter_sd", means="sample sd over 5 seeds of test accuracy (points of %), breast_cancer, noise 0.4, filter")
def acc_bc_40_filter_sd(): return _sd(_accs("bc", 40, "filter"))


# ---------------- differences the story rests on (points of %, difference of 5-seed means) ----------------
@source("diff_dg_20_filter_minus_logreg", means="accuracy difference (points of %), filter minus logreg on same noisy labels, digits, noise 0.2, difference of 5-seed means")
def diff_dg_20_filter_minus_logreg(): return _mean(_accs("dg", 20, "filter")) - _mean(_accs("dg", 20, "logreg"))
@source("diff_dg_40_filter_minus_logreg", means="accuracy difference (points of %), filter minus logreg on same noisy labels, digits, noise 0.4, difference of 5-seed means")
def diff_dg_40_filter_minus_logreg(): return _mean(_accs("dg", 40, "filter")) - _mean(_accs("dg", 40, "logreg"))
@source("diff_bc_20_filter_minus_logreg", means="accuracy difference (points of %), filter minus logreg on same noisy labels, breast_cancer, noise 0.2, difference of 5-seed means")
def diff_bc_20_filter_minus_logreg(): return _mean(_accs("bc", 20, "filter")) - _mean(_accs("bc", 20, "logreg"))
@source("diff_bc_40_filter_minus_logreg", means="accuracy difference (points of %), filter minus logreg on same noisy labels, breast_cancer, noise 0.4, difference of 5-seed means")
def diff_bc_40_filter_minus_logreg(): return _mean(_accs("bc", 40, "filter")) - _mean(_accs("bc", 40, "logreg"))

@source("diff_dg_00_filter_minus_mlp", means="accuracy difference (points of %), filter minus MLP, digits, noise 0.0, difference of 5-seed means")
def diff_dg_00_filter_minus_mlp(): return _mean(_accs("dg", 0, "filter")) - _mean(_accs("dg", 0, "mlp"))
@source("diff_dg_20_filter_minus_mlp", means="accuracy difference (points of %), filter minus MLP, digits, noise 0.2, difference of 5-seed means")
def diff_dg_20_filter_minus_mlp(): return _mean(_accs("dg", 20, "filter")) - _mean(_accs("dg", 20, "mlp"))
@source("diff_dg_40_filter_minus_mlp", means="accuracy difference (points of %), filter minus MLP, digits, noise 0.4, difference of 5-seed means")
def diff_dg_40_filter_minus_mlp(): return _mean(_accs("dg", 40, "filter")) - _mean(_accs("dg", 40, "mlp"))
@source("diff_bc_00_filter_minus_mlp", means="accuracy difference (points of %), filter minus MLP, breast_cancer, noise 0.0, difference of 5-seed means")
def diff_bc_00_filter_minus_mlp(): return _mean(_accs("bc", 0, "filter")) - _mean(_accs("bc", 0, "mlp"))
@source("diff_bc_20_filter_minus_mlp", means="accuracy difference (points of %), filter minus MLP, breast_cancer, noise 0.2, difference of 5-seed means")
def diff_bc_20_filter_minus_mlp(): return _mean(_accs("bc", 20, "filter")) - _mean(_accs("bc", 20, "mlp"))
@source("diff_bc_40_filter_minus_mlp", means="accuracy difference (points of %), filter minus MLP, breast_cancer, noise 0.4, difference of 5-seed means")
def diff_bc_40_filter_minus_mlp(): return _mean(_accs("bc", 40, "filter")) - _mean(_accs("bc", 40, "mlp"))

@source("wins_dg_20_filter_over_mlp", means="number of seeds (of 5) where filter accuracy is strictly above MLP, digits, noise 0.2")
def wins_dg_20_filter_over_mlp(): return _wins("dg", 20, "filter", "mlp")
@source("wins_dg_40_filter_over_mlp", means="number of seeds (of 5) where filter accuracy is strictly above MLP, digits, noise 0.4")
def wins_dg_40_filter_over_mlp(): return _wins("dg", 40, "filter", "mlp")
@source("wins_bc_20_filter_over_mlp", means="number of seeds (of 5) where filter accuracy is strictly above MLP, breast_cancer, noise 0.2")
def wins_bc_20_filter_over_mlp(): return _wins("bc", 20, "filter", "mlp")
@source("wins_bc_40_filter_over_mlp", means="number of seeds (of 5) where filter accuracy is strictly above MLP, breast_cancer, noise 0.4")
def wins_bc_40_filter_over_mlp(): return _wins("bc", 40, "filter", "mlp")
@source("wins_dg_20_filter_over_logreg", means="number of seeds (of 5) where filter accuracy is strictly above logreg, digits, noise 0.2")
def wins_dg_20_filter_over_logreg(): return _wins("dg", 20, "filter", "logreg")
@source("wins_dg_40_filter_over_logreg", means="number of seeds (of 5) where filter accuracy is strictly above logreg, digits, noise 0.4")
def wins_dg_40_filter_over_logreg(): return _wins("dg", 40, "filter", "logreg")
@source("wins_bc_20_filter_over_logreg", means="number of seeds (of 5) where filter accuracy is strictly above logreg, breast_cancer, noise 0.2")
def wins_bc_20_filter_over_logreg(): return _wins("bc", 20, "filter", "logreg")
@source("wins_bc_40_filter_over_logreg", means="number of seeds (of 5) where filter accuracy is strictly above logreg, breast_cancer, noise 0.4")
def wins_bc_40_filter_over_logreg(): return _wins("bc", 40, "filter", "logreg")

# recovery: (filter - noisy logreg) / (clean logreg - noisy logreg), 5-seed means; 1 = full recovery
@source("recovery_dg_20", means="fraction of accuracy lost to noise recovered by filter, (filter - noisy logreg)/(clean logreg - noisy logreg), digits, noise 0.2, 5-seed means")
def recovery_dg_20(): return _rcv("dg", 20)
@source("recovery_dg_40", means="fraction of accuracy lost to noise recovered by filter, (filter - noisy logreg)/(clean logreg - noisy logreg), digits, noise 0.4, 5-seed means")
def recovery_dg_40(): return _rcv("dg", 40)
@source("recovery_bc_20", means="fraction of accuracy lost to noise recovered by filter, (filter - noisy logreg)/(clean logreg - noisy logreg), breast_cancer, noise 0.2, 5-seed means")
def recovery_bc_20(): return _rcv("bc", 20)
@source("recovery_bc_40", means="fraction of accuracy lost to noise recovered by filter, (filter - noisy logreg)/(clean logreg - noisy logreg), breast_cancer, noise 0.4, 5-seed means")
def recovery_bc_40(): return _rcv("bc", 40)

@source("loss_dg_20_logreg", means="accuracy lost by logreg to noise (points of %), clean logreg minus noisy logreg, digits, noise 0.2, 5-seed means")
def loss_dg_20_logreg(): return _mean(_accs("dg", 0, "logreg")) - _mean(_accs("dg", 20, "logreg"))
@source("loss_dg_40_logreg", means="accuracy lost by logreg to noise (points of %), clean logreg minus noisy logreg, digits, noise 0.4, 5-seed means")
def loss_dg_40_logreg(): return _mean(_accs("dg", 0, "logreg")) - _mean(_accs("dg", 40, "logreg"))
@source("loss_bc_20_logreg", means="accuracy lost by logreg to noise (points of %), clean logreg minus noisy logreg, breast_cancer, noise 0.2, 5-seed means")
def loss_bc_20_logreg(): return _mean(_accs("bc", 0, "logreg")) - _mean(_accs("bc", 20, "logreg"))
@source("loss_bc_40_logreg", means="accuracy lost by logreg to noise (points of %), clean logreg minus noisy logreg, breast_cancer, noise 0.4, 5-seed means")
def loss_bc_40_logreg(): return _mean(_accs("bc", 0, "logreg")) - _mean(_accs("bc", 40, "logreg"))

@source("gap_dg_20_filter_to_clean", means="accuracy (points of %) by which filter at noise 0.2 is below clean-label logreg, digits, 5-seed means")
def gap_dg_20_filter_to_clean(): return _mean(_accs("dg", 0, "logreg")) - _mean(_accs("dg", 20, "filter"))
@source("gap_dg_40_filter_to_clean", means="accuracy (points of %) by which filter at noise 0.4 is below clean-label logreg, digits, 5-seed means")
def gap_dg_40_filter_to_clean(): return _mean(_accs("dg", 0, "logreg")) - _mean(_accs("dg", 40, "filter"))
@source("gap_bc_20_filter_to_clean", means="accuracy (points of %) by which filter at noise 0.2 is below clean-label logreg, breast_cancer, 5-seed means")
def gap_bc_20_filter_to_clean(): return _mean(_accs("bc", 0, "logreg")) - _mean(_accs("bc", 20, "filter"))
@source("gap_bc_40_filter_to_clean", means="accuracy (points of %) by which filter at noise 0.4 is below clean-label logreg, breast_cancer, 5-seed means")
def gap_bc_40_filter_to_clean(): return _mean(_accs("bc", 0, "logreg")) - _mean(_accs("bc", 40, "filter"))

# ---------------- cost when labels are clean ----------------
@source("clean_cost_dg", means="accuracy difference (points of %), filter minus logreg, clean labels, digits, difference of 5-seed means")
def clean_cost_dg(): return _mean(_accs("dg", 0, "filter")) - _mean(_accs("dg", 0, "logreg"))
@source("clean_cost_bc", means="accuracy difference (points of %), filter minus logreg, clean labels, breast_cancer, difference of 5-seed means")
def clean_cost_bc(): return _mean(_accs("bc", 0, "filter")) - _mean(_accs("bc", 0, "logreg"))
@source("clean_worse_seeds_dg", means="number of seeds (of 5) where filter is strictly below logreg, clean labels, digits")
def clean_worse_seeds_dg(): return _wins("dg", 0, "logreg", "filter")
@source("clean_worse_seeds_bc", means="number of seeds (of 5) where filter is strictly below logreg, clean labels, breast_cancer")
def clean_worse_seeds_bc(): return _wins("bc", 0, "logreg", "filter")
@source("dropped_dg_00_mean", means="training samples dropped by the filter with clean labels, digits, mean over 5 seeds")
def dropped_dg_00_mean(): return _mean([r["n_dropped"] for r in _rows("dg", 0, "filter")])
@source("dropped_bc_00_mean", means="training samples dropped by the filter with clean labels, breast_cancer, mean over 5 seeds")
def dropped_bc_00_mean(): return _mean([r["n_dropped"] for r in _rows("bc", 0, "filter")])
@source("dropped_frac_dg_00_mean", means="percentage of training samples dropped by the filter with clean labels, digits, mean over 5 seeds")
def dropped_frac_dg_00_mean(): return _mean([100 * r["n_dropped"] / r["n_train"] for r in _rows("dg", 0, "filter")])
@source("dropped_frac_bc_00_mean", means="percentage of training samples dropped by the filter with clean labels, breast_cancer, mean over 5 seeds")
def dropped_frac_bc_00_mean(): return _mean([100 * r["n_dropped"] / r["n_train"] for r in _rows("bc", 0, "filter")])

# ---------------- what the filter drops ----------------
@source("dropped_dg_20_mean", means="training samples dropped by the filter, digits, noise 0.2, mean over 5 seeds")
def dropped_dg_20_mean(): return _mean([r["n_dropped"] for r in _rows("dg", 20, "filter")])
@source("dropped_dg_40_mean", means="training samples dropped by the filter, digits, noise 0.4, mean over 5 seeds")
def dropped_dg_40_mean(): return _mean([r["n_dropped"] for r in _rows("dg", 40, "filter")])
@source("dropped_bc_20_mean", means="training samples dropped by the filter, breast_cancer, noise 0.2, mean over 5 seeds")
def dropped_bc_20_mean(): return _mean([r["n_dropped"] for r in _rows("bc", 20, "filter")])
@source("dropped_bc_40_mean", means="training samples dropped by the filter, breast_cancer, noise 0.4, mean over 5 seeds")
def dropped_bc_40_mean(): return _mean([r["n_dropped"] for r in _rows("bc", 40, "filter")])

@source("noisy_frac_dg_20_mean", means="realised percentage of flipped training labels, digits, nominal noise 0.2, mean over 5 seeds")
def noisy_frac_dg_20_mean(): return _mean([100 * r["n_noisy"] / r["n_train"] for r in _rows("dg", 20, "filter")])
@source("noisy_frac_dg_40_mean", means="realised percentage of flipped training labels, digits, nominal noise 0.4, mean over 5 seeds")
def noisy_frac_dg_40_mean(): return _mean([100 * r["n_noisy"] / r["n_train"] for r in _rows("dg", 40, "filter")])
@source("noisy_frac_bc_20_mean", means="realised percentage of flipped training labels, breast_cancer, nominal noise 0.2, mean over 5 seeds")
def noisy_frac_bc_20_mean(): return _mean([100 * r["n_noisy"] / r["n_train"] for r in _rows("bc", 20, "filter")])
@source("noisy_frac_bc_40_mean", means="realised percentage of flipped training labels, breast_cancer, nominal noise 0.4, mean over 5 seeds")
def noisy_frac_bc_40_mean(): return _mean([100 * r["n_noisy"] / r["n_train"] for r in _rows("bc", 40, "filter")])

@source("precision_dg_20_mean", means="precision (%) of the filter (dropped samples that were truly flipped), digits, noise 0.2, mean over 5 seeds of per-seed ratios")
def precision_dg_20_mean(): return _mean(_prec("dg", 20))
@source("precision_dg_40_mean", means="precision (%) of the filter (dropped samples that were truly flipped), digits, noise 0.4, mean over 5 seeds of per-seed ratios")
def precision_dg_40_mean(): return _mean(_prec("dg", 40))
@source("precision_bc_20_mean", means="precision (%) of the filter (dropped samples that were truly flipped), breast_cancer, noise 0.2, mean over 5 seeds of per-seed ratios")
def precision_bc_20_mean(): return _mean(_prec("bc", 20))
@source("precision_bc_40_mean", means="precision (%) of the filter (dropped samples that were truly flipped), breast_cancer, noise 0.4, mean over 5 seeds of per-seed ratios")
def precision_bc_40_mean(): return _mean(_prec("bc", 40))
@source("precision_dg_20_min", means="lowest per-seed precision (%) of the filter over 5 seeds, digits, noise 0.2")
def precision_dg_20_min(): return min(_prec("dg", 20))
@source("precision_dg_40_min", means="lowest per-seed precision (%) of the filter over 5 seeds, digits, noise 0.4")
def precision_dg_40_min(): return min(_prec("dg", 40))
@source("precision_bc_20_min", means="lowest per-seed precision (%) of the filter over 5 seeds, breast_cancer, noise 0.2")
def precision_bc_20_min(): return min(_prec("bc", 20))
@source("precision_bc_40_min", means="lowest per-seed precision (%) of the filter over 5 seeds, breast_cancer, noise 0.4")
def precision_bc_40_min(): return min(_prec("bc", 40))

@source("recall_dg_20_mean", means="recall (%) of the filter (flipped training samples that were dropped), digits, noise 0.2, mean over 5 seeds of per-seed ratios")
def recall_dg_20_mean(): return _mean(_rec("dg", 20))
@source("recall_dg_40_mean", means="recall (%) of the filter (flipped training samples that were dropped), digits, noise 0.4, mean over 5 seeds of per-seed ratios")
def recall_dg_40_mean(): return _mean(_rec("dg", 40))
@source("recall_bc_20_mean", means="recall (%) of the filter (flipped training samples that were dropped), breast_cancer, noise 0.2, mean over 5 seeds of per-seed ratios")
def recall_bc_20_mean(): return _mean(_rec("bc", 20))
@source("recall_bc_40_mean", means="recall (%) of the filter (flipped training samples that were dropped), breast_cancer, noise 0.4, mean over 5 seeds of per-seed ratios")
def recall_bc_40_mean(): return _mean(_rec("bc", 40))


# ---------------- dataset sizes, settings ----------------
@source("n_total_digits", means="number of samples in digits (n_train + n_test of seed 0)")
def n_total_digits():
    r = _rows("dg", 0, "logreg")[0]
    return r["n_train"] + r["n_test"]


@source("n_total_bc", means="number of samples in breast_cancer (n_train + n_test of seed 0)")
def n_total_bc():
    r = _rows("bc", 0, "logreg")[0]
    return r["n_train"] + r["n_test"]


@source("n_train_digits", means="training set size, digits")
def n_train_digits(): return _rows("dg", 0, "logreg")[0]["n_train"]
@source("n_test_digits", means="test set size, digits")
def n_test_digits(): return _rows("dg", 0, "logreg")[0]["n_test"]
@source("n_train_bc", means="training set size, breast_cancer")
def n_train_bc(): return _rows("bc", 0, "logreg")[0]["n_train"]
@source("n_test_bc", means="test set size, breast_cancer")
def n_test_bc(): return _rows("bc", 0, "logreg")[0]["n_test"]
@source("n_seeds", means="number of seeds in the config")
def n_seeds(): return len(load("experiments/config.json")["seeds"])
@source("n_runs", means="total number of run records in results/runs.jsonl")
def n_runs(): return len(load("results/runs.jsonl"))
@source("cfg_test_fraction_pct", means="test fraction (%) of the train/test split, from the config")
def cfg_test_fraction_pct(): return 100 * load("experiments/config.json")["test_fraction"]
@source("cfg_folds", means="number of cross-validation folds K of the filter, from the config")
def cfg_folds(): return load("experiments/config.json")["filter_folds"]
@source("cfg_logreg_C", means="inverse L2 regularisation strength C of logistic regression, from the config")
def cfg_logreg_C(): return load("experiments/config.json")["logreg_C"]
@source("cfg_mlp_hidden", means="hidden units of the single-hidden-layer MLP, from the config")
def cfg_mlp_hidden(): return load("experiments/config.json")["mlp_hidden"]
@source("cfg_mlp_max_iter", means="max_iter of the MLP, from the config")
def cfg_mlp_max_iter(): return load("experiments/config.json")["mlp_max_iter"]
@source("cfg_n_noise_rates", means="number of nominal noise rates in the config (0.0, 0.2, 0.4)")
def cfg_n_noise_rates(): return len(load("experiments/config.json")["noise_rates"])


@source("time_ratio_filter_logreg_digits", means="ratio of mean fit_seconds, filter over logreg, digits, all noise rates and seeds (machine-dependent)")
def time_ratio_filter_logreg_digits():
    rs = [r for r in load("results/runs.jsonl") if r["dataset"] == "digits"]
    f = [r["fit_seconds"] for r in rs if r["method"] == "filter"]
    g = [r["fit_seconds"] for r in rs if r["method"] == "logreg"]
    return (sum(f) / len(f)) / (sum(g) / len(g))


@source("cfg_noise_low_pct", means="lower nonzero nominal noise rate (%) in the config")
def cfg_noise_low_pct(): return 100 * sorted(load("experiments/config.json")["noise_rates"])[1]
@source("cfg_noise_high_pct", means="highest nominal noise rate (%) in the config")
def cfg_noise_high_pct(): return 100 * max(load("experiments/config.json")["noise_rates"])


# ---------------- paired per-seed differences and drop shares (review round 1) ----------------
def _pd(ds, nz):
    return [a - b for a, b in zip(_accs(ds, nz, "filter"), _accs(ds, nz, "logreg"))]


def _dfrac(ds, nz):
    return _mean([100 * r["n_dropped"] / r["n_train"] for r in _rows(ds, nz, "filter")])


@source("pdmin_dg_00", means="smallest per-seed paired difference (points of %), filter minus logreg, digits, noise 0")
def pdmin_dg_00(): return min(_pd("dg", 0))
@source("pdmax_dg_00", means="largest per-seed paired difference (points of %), filter minus logreg, digits, noise 0")
def pdmax_dg_00(): return max(_pd("dg", 0))
@source("pdmin_bc_00", means="smallest per-seed paired difference (points of %), filter minus logreg, breast_cancer, noise 0")
def pdmin_bc_00(): return min(_pd("bc", 0))
@source("pdmax_bc_00", means="largest per-seed paired difference (points of %), filter minus logreg, breast_cancer, noise 0")
def pdmax_bc_00(): return max(_pd("bc", 0))
@source("pdmin_dg_20", means="smallest per-seed paired difference (points of %), filter minus logreg, digits, noise 0.2")
def pdmin_dg_20(): return min(_pd("dg", 20))
@source("pdmax_dg_20", means="largest per-seed paired difference (points of %), filter minus logreg, digits, noise 0.2")
def pdmax_dg_20(): return max(_pd("dg", 20))
@source("pdmin_dg_40", means="smallest per-seed paired difference (points of %), filter minus logreg, digits, noise 0.4")
def pdmin_dg_40(): return min(_pd("dg", 40))
@source("pdmax_dg_40", means="largest per-seed paired difference (points of %), filter minus logreg, digits, noise 0.4")
def pdmax_dg_40(): return max(_pd("dg", 40))
@source("pdmin_bc_20", means="smallest per-seed paired difference (points of %), filter minus logreg, breast_cancer, noise 0.2")
def pdmin_bc_20(): return min(_pd("bc", 20))
@source("pdmax_bc_20", means="largest per-seed paired difference (points of %), filter minus logreg, breast_cancer, noise 0.2")
def pdmax_bc_20(): return max(_pd("bc", 20))
@source("pdmin_bc_40", means="smallest per-seed paired difference (points of %), filter minus logreg, breast_cancer, noise 0.4")
def pdmin_bc_40(): return min(_pd("bc", 40))
@source("pdmax_bc_40", means="largest per-seed paired difference (points of %), filter minus logreg, breast_cancer, noise 0.4")
def pdmax_bc_40(): return max(_pd("bc", 40))

@source("droppedshare_dg_20", means="mean share (%) of training set dropped by the filter, digits, noise 0.2")
def droppedshare_dg_20(): return _dfrac("dg", 20)
@source("droppedshare_dg_40", means="mean share (%) of training set dropped by the filter, digits, noise 0.4")
def droppedshare_dg_40(): return _dfrac("dg", 40)
@source("droppedshare_bc_20", means="mean share (%) of training set dropped by the filter, breast_cancer, noise 0.2")
def droppedshare_bc_20(): return _dfrac("bc", 20)
@source("droppedshare_bc_40", means="mean share (%) of training set dropped by the filter, breast_cancer, noise 0.4")
def droppedshare_bc_40(): return _dfrac("bc", 40)
