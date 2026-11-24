"""Recipes for the numbers in this paper. Each returns the unrounded value printed next to \\src{key}.

`source` and `load(path)` are provided by the checker; do not import or define them. Paths are relative to the
repository root. Read raw results, configs or scripts, never Markdown notes.
"""


def _runs(dataset, noise, method):
    """Run records for one cell, in seed order (seeds 0-4)."""
    rs = [r for r in load("results/runs.jsonl")
          if r["dataset"] == dataset and abs(r["noise"] - noise) < 1e-9 and r["method"] == method]
    return sorted(rs, key=lambda r: r["seed"])


def _accs(dataset, noise, method):
    """Test accuracy (%) per seed, in seed order."""
    return [100 * r["acc"] if "acc" in r else 100 * r["test_acc"] for r in _runs(dataset, noise, method)]


def _mean(xs):
    return sum(xs) / len(xs)


def _sd(xs):
    import statistics
    return statistics.stdev(xs)


def _diff(dataset, noise, a, b):
    """Per-seed accuracy difference (%) a minus b, paired by seed."""
    return [x - y for x, y in zip(_accs(dataset, noise, a), _accs(dataset, noise, b))]


def _precisions(dataset, noise):
    """Per-seed filter precision (%): dropped samples that were truly flipped."""
    return [100 * r["n_dropped_noisy"] / r["n_dropped"] for r in _runs(dataset, noise, "filter")]


def _recalls(dataset, noise):
    """Per-seed filter recall (%): flipped samples that were dropped."""
    return [100 * r["n_dropped_noisy"] / r["n_noisy"] for r in _runs(dataset, noise, "filter")]


def _dropped_frac(dataset, noise):
    """Per-seed fraction (%) of training samples dropped."""
    return [100 * r["n_dropped"] / r["n_train"] for r in _runs(dataset, noise, "filter")]


def _recovery(dataset, noise):
    """Per-seed share (%) of the accuracy lost to noise that the filter wins back.
    (filter - noisy logreg) / (clean logreg - noisy logreg), clean logreg from the same seed at noise 0."""
    clean = _accs(dataset, 0.0, "logreg")
    noisy = _accs(dataset, noise, "logreg")
    filt = _accs(dataset, noise, "filter")
    return [100 * (f - n) / (c - n) for f, n, c in zip(filt, noisy, clean)]


def _cfg(k):
    return load("experiments/config.json")[k]


# ---------- accuracy: mean and sd per dataset x noise x method ----------
@source("acc_digits_n0_logreg", means="test accuracy (%) of logistic regression on digits, 0% label noise, mean over 5 seeds")
def acc_digits_n0_logreg():
    return _mean(_accs("digits", 0.0, "logreg"))


@source("sd_digits_n0_logreg", means="sd over 5 seeds of test accuracy (%) of logistic regression on digits, 0% noise")
def sd_digits_n0_logreg():
    return _sd(_accs("digits", 0.0, "logreg"))


@source("acc_digits_n0_mlp", means="test accuracy (%) of the MLP on digits, 0% label noise, mean over 5 seeds")
def acc_digits_n0_mlp():
    return _mean(_accs("digits", 0.0, "mlp"))


@source("sd_digits_n0_mlp", means="sd over 5 seeds of test accuracy (%) of the MLP on digits, 0% noise")
def sd_digits_n0_mlp():
    return _sd(_accs("digits", 0.0, "mlp"))


@source("acc_digits_n0_filter", means="test accuracy (%) of the out-of-fold filter on digits, 0% label noise, mean over 5 seeds")
def acc_digits_n0_filter():
    return _mean(_accs("digits", 0.0, "filter"))


@source("sd_digits_n0_filter", means="sd over 5 seeds of test accuracy (%) of the filter on digits, 0% noise")
def sd_digits_n0_filter():
    return _sd(_accs("digits", 0.0, "filter"))


@source("acc_digits_n20_logreg", means="test accuracy (%) of logistic regression on digits, 20% label noise, mean over 5 seeds")
def acc_digits_n20_logreg():
    return _mean(_accs("digits", 0.2, "logreg"))


@source("sd_digits_n20_logreg", means="sd over 5 seeds of test accuracy (%) of logistic regression on digits, 20% noise")
def sd_digits_n20_logreg():
    return _sd(_accs("digits", 0.2, "logreg"))


@source("acc_digits_n20_mlp", means="test accuracy (%) of the MLP on digits, 20% label noise, mean over 5 seeds")
def acc_digits_n20_mlp():
    return _mean(_accs("digits", 0.2, "mlp"))


@source("sd_digits_n20_mlp", means="sd over 5 seeds of test accuracy (%) of the MLP on digits, 20% noise")
def sd_digits_n20_mlp():
    return _sd(_accs("digits", 0.2, "mlp"))


@source("acc_digits_n20_filter", means="test accuracy (%) of the filter on digits, 20% label noise, mean over 5 seeds")
def acc_digits_n20_filter():
    return _mean(_accs("digits", 0.2, "filter"))


@source("sd_digits_n20_filter", means="sd over 5 seeds of test accuracy (%) of the filter on digits, 20% noise")
def sd_digits_n20_filter():
    return _sd(_accs("digits", 0.2, "filter"))


@source("acc_digits_n40_logreg", means="test accuracy (%) of logistic regression on digits, 40% label noise, mean over 5 seeds")
def acc_digits_n40_logreg():
    return _mean(_accs("digits", 0.4, "logreg"))


@source("sd_digits_n40_logreg", means="sd over 5 seeds of test accuracy (%) of logistic regression on digits, 40% noise")
def sd_digits_n40_logreg():
    return _sd(_accs("digits", 0.4, "logreg"))


@source("acc_digits_n40_mlp", means="test accuracy (%) of the MLP on digits, 40% label noise, mean over 5 seeds")
def acc_digits_n40_mlp():
    return _mean(_accs("digits", 0.4, "mlp"))


@source("sd_digits_n40_mlp", means="sd over 5 seeds of test accuracy (%) of the MLP on digits, 40% noise")
def sd_digits_n40_mlp():
    return _sd(_accs("digits", 0.4, "mlp"))


@source("acc_digits_n40_filter", means="test accuracy (%) of the filter on digits, 40% label noise, mean over 5 seeds")
def acc_digits_n40_filter():
    return _mean(_accs("digits", 0.4, "filter"))


@source("sd_digits_n40_filter", means="sd over 5 seeds of test accuracy (%) of the filter on digits, 40% noise")
def sd_digits_n40_filter():
    return _sd(_accs("digits", 0.4, "filter"))


@source("acc_bc_n0_logreg", means="test accuracy (%) of logistic regression on breast_cancer, 0% label noise, mean over 5 seeds")
def acc_bc_n0_logreg():
    return _mean(_accs("breast_cancer", 0.0, "logreg"))


@source("sd_bc_n0_logreg", means="sd over 5 seeds of test accuracy (%) of logistic regression on breast_cancer, 0% noise")
def sd_bc_n0_logreg():
    return _sd(_accs("breast_cancer", 0.0, "logreg"))


@source("acc_bc_n0_mlp", means="test accuracy (%) of the MLP on breast_cancer, 0% label noise, mean over 5 seeds")
def acc_bc_n0_mlp():
    return _mean(_accs("breast_cancer", 0.0, "mlp"))


@source("sd_bc_n0_mlp", means="sd over 5 seeds of test accuracy (%) of the MLP on breast_cancer, 0% noise")
def sd_bc_n0_mlp():
    return _sd(_accs("breast_cancer", 0.0, "mlp"))


@source("acc_bc_n0_filter", means="test accuracy (%) of the filter on breast_cancer, 0% label noise, mean over 5 seeds")
def acc_bc_n0_filter():
    return _mean(_accs("breast_cancer", 0.0, "filter"))


@source("sd_bc_n0_filter", means="sd over 5 seeds of test accuracy (%) of the filter on breast_cancer, 0% noise")
def sd_bc_n0_filter():
    return _sd(_accs("breast_cancer", 0.0, "filter"))


@source("acc_bc_n20_logreg", means="test accuracy (%) of logistic regression on breast_cancer, 20% label noise, mean over 5 seeds")
def acc_bc_n20_logreg():
    return _mean(_accs("breast_cancer", 0.2, "logreg"))


@source("sd_bc_n20_logreg", means="sd over 5 seeds of test accuracy (%) of logistic regression on breast_cancer, 20% noise")
def sd_bc_n20_logreg():
    return _sd(_accs("breast_cancer", 0.2, "logreg"))


@source("acc_bc_n20_mlp", means="test accuracy (%) of the MLP on breast_cancer, 20% label noise, mean over 5 seeds")
def acc_bc_n20_mlp():
    return _mean(_accs("breast_cancer", 0.2, "mlp"))


@source("sd_bc_n20_mlp", means="sd over 5 seeds of test accuracy (%) of the MLP on breast_cancer, 20% noise")
def sd_bc_n20_mlp():
    return _sd(_accs("breast_cancer", 0.2, "mlp"))


@source("acc_bc_n20_filter", means="test accuracy (%) of the filter on breast_cancer, 20% label noise, mean over 5 seeds")
def acc_bc_n20_filter():
    return _mean(_accs("breast_cancer", 0.2, "filter"))


@source("sd_bc_n20_filter", means="sd over 5 seeds of test accuracy (%) of the filter on breast_cancer, 20% noise")
def sd_bc_n20_filter():
    return _sd(_accs("breast_cancer", 0.2, "filter"))


@source("acc_bc_n40_logreg", means="test accuracy (%) of logistic regression on breast_cancer, 40% label noise, mean over 5 seeds")
def acc_bc_n40_logreg():
    return _mean(_accs("breast_cancer", 0.4, "logreg"))


@source("sd_bc_n40_logreg", means="sd over 5 seeds of test accuracy (%) of logistic regression on breast_cancer, 40% noise")
def sd_bc_n40_logreg():
    return _sd(_accs("breast_cancer", 0.4, "logreg"))


@source("acc_bc_n40_mlp", means="test accuracy (%) of the MLP on breast_cancer, 40% label noise, mean over 5 seeds")
def acc_bc_n40_mlp():
    return _mean(_accs("breast_cancer", 0.4, "mlp"))


@source("sd_bc_n40_mlp", means="sd over 5 seeds of test accuracy (%) of the MLP on breast_cancer, 40% noise")
def sd_bc_n40_mlp():
    return _sd(_accs("breast_cancer", 0.4, "mlp"))


@source("acc_bc_n40_filter", means="test accuracy (%) of the filter on breast_cancer, 40% label noise, mean over 5 seeds")
def acc_bc_n40_filter():
    return _mean(_accs("breast_cancer", 0.4, "filter"))


@source("sd_bc_n40_filter", means="sd over 5 seeds of test accuracy (%) of the filter on breast_cancer, 40% noise")
def sd_bc_n40_filter():
    return _sd(_accs("breast_cancer", 0.4, "filter"))


# ---------- differences (percentage points, mean over 5 paired seeds) ----------
@source("gain_digits_n20_vs_logreg", means="filter minus no-filter logistic regression, test accuracy (points), digits, 20% noise, mean of 5 paired seeds")
def gain_digits_n20_vs_logreg():
    return _mean(_diff("digits", 0.2, "filter", "logreg"))


@source("gain_digits_n40_vs_logreg", means="filter minus no-filter logistic regression, test accuracy (points), digits, 40% noise, mean of 5 paired seeds")
def gain_digits_n40_vs_logreg():
    return _mean(_diff("digits", 0.4, "filter", "logreg"))


@source("gain_bc_n20_vs_logreg", means="filter minus no-filter logistic regression, test accuracy (points), breast_cancer, 20% noise, mean of 5 paired seeds")
def gain_bc_n20_vs_logreg():
    return _mean(_diff("breast_cancer", 0.2, "filter", "logreg"))


@source("gain_bc_n40_vs_logreg", means="filter minus no-filter logistic regression, test accuracy (points), breast_cancer, 40% noise, mean of 5 paired seeds")
def gain_bc_n40_vs_logreg():
    return _mean(_diff("breast_cancer", 0.4, "filter", "logreg"))


@source("gain_digits_n0_vs_logreg", means="filter minus logistic regression, test accuracy (points), digits, 0% noise (cost on clean labels, negative = cost), mean of 5 paired seeds")
def gain_digits_n0_vs_logreg():
    return _mean(_diff("digits", 0.0, "filter", "logreg"))


@source("gain_bc_n0_vs_logreg", means="filter minus logistic regression, test accuracy (points), breast_cancer, 0% noise (cost on clean labels, negative = cost), mean of 5 paired seeds")
def gain_bc_n0_vs_logreg():
    return _mean(_diff("breast_cancer", 0.0, "filter", "logreg"))


@source("gain_digits_n0_vs_mlp", means="filter minus MLP, test accuracy (points), digits, 0% noise, mean of 5 paired seeds")
def gain_digits_n0_vs_mlp():
    return _mean(_diff("digits", 0.0, "filter", "mlp"))


@source("gain_digits_n20_vs_mlp", means="filter minus MLP, test accuracy (points), digits, 20% noise, mean of 5 paired seeds")
def gain_digits_n20_vs_mlp():
    return _mean(_diff("digits", 0.2, "filter", "mlp"))


@source("gain_digits_n40_vs_mlp", means="filter minus MLP, test accuracy (points), digits, 40% noise, mean of 5 paired seeds")
def gain_digits_n40_vs_mlp():
    return _mean(_diff("digits", 0.4, "filter", "mlp"))


@source("gain_bc_n0_vs_mlp", means="filter minus MLP, test accuracy (points), breast_cancer, 0% noise, mean of 5 paired seeds")
def gain_bc_n0_vs_mlp():
    return _mean(_diff("breast_cancer", 0.0, "filter", "mlp"))


@source("gain_bc_n20_vs_mlp", means="filter minus MLP, test accuracy (points), breast_cancer, 20% noise, mean of 5 paired seeds")
def gain_bc_n20_vs_mlp():
    return _mean(_diff("breast_cancer", 0.2, "filter", "mlp"))


@source("gain_bc_n40_vs_mlp", means="filter minus MLP, test accuracy (points), breast_cancer, 40% noise, mean of 5 paired seeds")
def gain_bc_n40_vs_mlp():
    return _mean(_diff("breast_cancer", 0.4, "filter", "mlp"))


@source("n_seeds_filter_wins_mlp_digits_n40", means="number of 5 seeds in which the filter beats the MLP on digits at 40% noise")
def n_seeds_filter_wins_mlp_digits_n40():
    return sum(d > 0 for d in _diff("digits", 0.4, "filter", "mlp"))


@source("n_seeds_filter_wins_mlp_digits_n20", means="number of 5 seeds in which the filter beats the MLP on digits at 20% noise")
def n_seeds_filter_wins_mlp_digits_n20():
    return sum(d > 0 for d in _diff("digits", 0.2, "filter", "mlp"))


@source("n_seeds_filter_wins_mlp_bc_n20", means="number of 5 seeds in which the filter beats the MLP on breast_cancer at 20% noise")
def n_seeds_filter_wins_mlp_bc_n20():
    return sum(d > 0 for d in _diff("breast_cancer", 0.2, "filter", "mlp"))


@source("n_seeds_filter_wins_mlp_bc_n40", means="number of 5 seeds in which the filter beats the MLP on breast_cancer at 40% noise")
def n_seeds_filter_wins_mlp_bc_n40():
    return sum(d > 0 for d in _diff("breast_cancer", 0.4, "filter", "mlp"))


# ---------- accuracy lost to noise and recovered ----------
@source("loss_digits_n20", means="accuracy (points) lost by logistic regression on digits from 0% to 20% noise, mean over 5 seeds")
def loss_digits_n20():
    return _mean(_accs("digits", 0.0, "logreg")) - _mean(_accs("digits", 0.2, "logreg"))


@source("loss_digits_n40", means="accuracy (points) lost by logistic regression on digits from 0% to 40% noise, mean over 5 seeds")
def loss_digits_n40():
    return _mean(_accs("digits", 0.0, "logreg")) - _mean(_accs("digits", 0.4, "logreg"))


@source("loss_bc_n20", means="accuracy (points) lost by logistic regression on breast_cancer from 0% to 20% noise, mean over 5 seeds")
def loss_bc_n20():
    return _mean(_accs("breast_cancer", 0.0, "logreg")) - _mean(_accs("breast_cancer", 0.2, "logreg"))


@source("loss_bc_n40", means="accuracy (points) lost by logistic regression on breast_cancer from 0% to 40% noise, mean over 5 seeds")
def loss_bc_n40():
    return _mean(_accs("breast_cancer", 0.0, "logreg")) - _mean(_accs("breast_cancer", 0.4, "logreg"))


@source("recovery_digits_n20", means="share (%) of logistic-regression accuracy lost to 20% noise on digits that the filter wins back: (filter-noisy)/(clean-noisy) using group means over 5 seeds")
def recovery_digits_n20():
    return 100 * (_mean(_accs("digits", 0.2, "filter")) - _mean(_accs("digits", 0.2, "logreg"))) / (_mean(_accs("digits", 0.0, "logreg")) - _mean(_accs("digits", 0.2, "logreg")))


@source("recovery_digits_n40", means="share (%) of logistic-regression accuracy lost to 40% noise on digits that the filter wins back, using group means over 5 seeds")
def recovery_digits_n40():
    return 100 * (_mean(_accs("digits", 0.4, "filter")) - _mean(_accs("digits", 0.4, "logreg"))) / (_mean(_accs("digits", 0.0, "logreg")) - _mean(_accs("digits", 0.4, "logreg")))


@source("recovery_bc_n20", means="share (%) of logistic-regression accuracy lost to 20% noise on breast_cancer that the filter wins back, using group means over 5 seeds")
def recovery_bc_n20():
    return 100 * (_mean(_accs("breast_cancer", 0.2, "filter")) - _mean(_accs("breast_cancer", 0.2, "logreg"))) / (_mean(_accs("breast_cancer", 0.0, "logreg")) - _mean(_accs("breast_cancer", 0.2, "logreg")))


@source("recovery_bc_n40", means="share (%) of logistic-regression accuracy lost to 40% noise on breast_cancer that the filter wins back, using group means over 5 seeds")
def recovery_bc_n40():
    return 100 * (_mean(_accs("breast_cancer", 0.4, "filter")) - _mean(_accs("breast_cancer", 0.4, "logreg"))) / (_mean(_accs("breast_cancer", 0.0, "logreg")) - _mean(_accs("breast_cancer", 0.4, "logreg")))


@source("recovery_seed_mean_digits_n40", means="mean over 5 seeds of the per-seed share (%) of accuracy lost to 40% noise recovered by the filter, digits")
def recovery_seed_mean_digits_n40():
    return _mean(_recovery("digits", 0.4))


@source("recovery_seed_min_bc_n20", means="minimum over 5 seeds of the per-seed recovered share (%) at 20% noise, breast_cancer (denominator can be near zero)")
def recovery_seed_min_bc_n20():
    return min(_recovery("breast_cancer", 0.2))


# ---------- what the filter drops ----------
@source("prec_digits_n20", means="precision (%) of the filter on digits, 20% noise: dropped samples that were truly flipped, mean over 5 seeds")
def prec_digits_n20():
    return _mean(_precisions("digits", 0.2))


@source("prec_digits_n40", means="precision (%) of the filter on digits, 40% noise, mean over 5 seeds")
def prec_digits_n40():
    return _mean(_precisions("digits", 0.4))


@source("prec_bc_n20", means="precision (%) of the filter on breast_cancer, 20% noise, mean over 5 seeds")
def prec_bc_n20():
    return _mean(_precisions("breast_cancer", 0.2))


@source("prec_bc_n40", means="precision (%) of the filter on breast_cancer, 40% noise, mean over 5 seeds")
def prec_bc_n40():
    return _mean(_precisions("breast_cancer", 0.4))


@source("prec_min_any", means="lowest per-run precision (%) of the filter over all noisy cells (2 datasets x 20%/40% noise x 5 seeds)")
def prec_min_any():
    return min(p for d in ("digits", "breast_cancer") for n in (0.2, 0.4) for p in _precisions(d, n))


@source("sd_prec_digits_n20", means="sd over 5 seeds of filter precision (%), digits, 20% noise")
def sd_prec_digits_n20():
    return _sd(_precisions("digits", 0.2))


@source("sd_prec_digits_n40", means="sd over 5 seeds of filter precision (%), digits, 40% noise")
def sd_prec_digits_n40():
    return _sd(_precisions("digits", 0.4))


@source("sd_prec_bc_n20", means="sd over 5 seeds of filter precision (%), breast_cancer, 20% noise")
def sd_prec_bc_n20():
    return _sd(_precisions("breast_cancer", 0.2))


@source("sd_prec_bc_n40", means="sd over 5 seeds of filter precision (%), breast_cancer, 40% noise")
def sd_prec_bc_n40():
    return _sd(_precisions("breast_cancer", 0.4))


@source("rec_digits_n20", means="recall (%) of the filter on digits, 20% noise: flipped samples that were dropped, mean over 5 seeds")
def rec_digits_n20():
    return _mean(_recalls("digits", 0.2))


@source("rec_digits_n40", means="recall (%) of the filter on digits, 40% noise, mean over 5 seeds")
def rec_digits_n40():
    return _mean(_recalls("digits", 0.4))


@source("rec_bc_n20", means="recall (%) of the filter on breast_cancer, 20% noise, mean over 5 seeds")
def rec_bc_n20():
    return _mean(_recalls("breast_cancer", 0.2))


@source("rec_bc_n40", means="recall (%) of the filter on breast_cancer, 40% noise, mean over 5 seeds")
def rec_bc_n40():
    return _mean(_recalls("breast_cancer", 0.4))


@source("dropped_frac_digits_n0", means="share (%) of training samples the filter drops on digits at 0% noise (all clean), mean over 5 seeds")
def dropped_frac_digits_n0():
    return _mean(_dropped_frac("digits", 0.0))


@source("dropped_frac_bc_n0", means="share (%) of training samples the filter drops on breast_cancer at 0% noise (all clean), mean over 5 seeds")
def dropped_frac_bc_n0():
    return _mean(_dropped_frac("breast_cancer", 0.0))


@source("dropped_frac_digits_n20", means="share (%) of training samples dropped by the filter, digits, 20% noise, mean over 5 seeds")
def dropped_frac_digits_n20():
    return _mean(_dropped_frac("digits", 0.2))


@source("dropped_frac_digits_n40", means="share (%) of training samples dropped by the filter, digits, 40% noise, mean over 5 seeds")
def dropped_frac_digits_n40():
    return _mean(_dropped_frac("digits", 0.4))


@source("dropped_frac_bc_n20", means="share (%) of training samples dropped by the filter, breast_cancer, 20% noise, mean over 5 seeds")
def dropped_frac_bc_n20():
    return _mean(_dropped_frac("breast_cancer", 0.2))


@source("dropped_frac_bc_n40", means="share (%) of training samples dropped by the filter, breast_cancer, 40% noise, mean over 5 seeds")
def dropped_frac_bc_n40():
    return _mean(_dropped_frac("breast_cancer", 0.4))


@source("actual_noise_digits_n40", means="actual share (%) of training labels flipped on digits at nominal 40% noise, mean over 5 seeds")
def actual_noise_digits_n40():
    return _mean([100 * r["n_noisy"] / r["n_train"] for r in _runs("digits", 0.4, "logreg")])


@source("actual_noise_bc_n40", means="actual share (%) of training labels flipped on breast_cancer at nominal 40% noise, mean over 5 seeds")
def actual_noise_bc_n40():
    return _mean([100 * r["n_noisy"] / r["n_train"] for r in _runs("breast_cancer", 0.4, "logreg")])


# ---------- cost ----------
@source("fit_sec_digits_logreg", means="wall-clock fit time (s) of logistic regression on digits, mean over all 15 runs (3 noise rates x 5 seeds)")
def fit_sec_digits_logreg():
    return _mean([r["fit_seconds"] for n in (0.0, 0.2, 0.4) for r in _runs("digits", n, "logreg")])


@source("fit_sec_digits_filter", means="wall-clock fit time (s) of the filter (5-fold CV plus refit) on digits, mean over all 15 runs")
def fit_sec_digits_filter():
    return _mean([r["fit_seconds"] for n in (0.0, 0.2, 0.4) for r in _runs("digits", n, "filter")])


@source("fit_sec_digits_mlp", means="wall-clock fit time (s) of the MLP on digits, mean over all 15 runs")
def fit_sec_digits_mlp():
    return _mean([r["fit_seconds"] for n in (0.0, 0.2, 0.4) for r in _runs("digits", n, "mlp")])


# ---------- sizes and settings ----------
@source("n_runs_total", means="number of records in results/runs.jsonl (2 datasets x 3 noise rates x 5 seeds x 3 methods)")
def n_runs_total():
    return len(load("results/runs.jsonl"))


@source("n_seeds", means="number of seeds per cell, from experiments/config.json")
def n_seeds():
    return len(_cfg("seeds"))


@source("n_noise_rates", means="number of label-noise rates, from experiments/config.json")
def n_noise_rates():
    return len(_cfg("noise_rates"))


@source("n_datasets", means="number of datasets, from experiments/config.json")
def n_datasets():
    return len(_cfg("datasets"))


@source("noise_max_pct", means="highest symmetric label-noise rate (%), from experiments/config.json")
def noise_max_pct():
    return 100 * max(_cfg("noise_rates"))


@source("noise_mid_pct", means="middle label-noise rate (%), from experiments/config.json")
def noise_mid_pct():
    return 100 * sorted(_cfg("noise_rates"))[1]


@source("test_fraction_pct", means="share (%) of each dataset held out as the clean test set, from config")
def test_fraction_pct():
    return 100 * _cfg("test_fraction")


@source("filter_folds", means="number of cross-validation folds used by the filter, from config")
def filter_folds():
    return _cfg("filter_folds")


@source("logreg_c", means="inverse regularization strength C of logistic regression, from config")
def logreg_c():
    return _cfg("logreg_C")


@source("mlp_hidden", means="hidden units of the MLP's single hidden layer, from config")
def mlp_hidden():
    return _cfg("mlp_hidden")


@source("mlp_max_iter", means="maximum training iterations of the MLP, from config")
def mlp_max_iter():
    return _cfg("mlp_max_iter")


@source("n_train_digits", means="training samples on digits (70% split), from runs.jsonl; asserted equal in all digits runs")
def n_train_digits():
    v = {r["n_train"] for r in load("results/runs.jsonl") if r["dataset"] == "digits"}
    assert len(v) == 1
    return v.pop()


@source("n_test_digits", means="test samples on digits (30% split), from runs.jsonl; asserted equal in all digits runs")
def n_test_digits():
    v = {r["n_test"] for r in load("results/runs.jsonl") if r["dataset"] == "digits"}
    assert len(v) == 1
    return v.pop()


@source("n_train_bc", means="training samples on breast_cancer, from runs.jsonl; asserted equal in all runs")
def n_train_bc():
    v = {r["n_train"] for r in load("results/runs.jsonl") if r["dataset"] == "breast_cancer"}
    assert len(v) == 1
    return v.pop()


@source("n_test_bc", means="test samples on breast_cancer, from runs.jsonl; asserted equal in all runs")
def n_test_bc():
    v = {r["n_test"] for r in load("results/runs.jsonl") if r["dataset"] == "breast_cancer"}
    assert len(v) == 1
    return v.pop()


@source("n_total_digits", means="total samples on digits (train plus test)")
def n_total_digits():
    r = _runs("digits", 0.0, "logreg")[0]
    return r["n_train"] + r["n_test"]


@source("n_total_bc", means="total samples on breast_cancer (train plus test)")
def n_total_bc():
    r = _runs("breast_cancer", 0.0, "logreg")[0]
    return r["n_train"] + r["n_test"]


# ---------- statistical tests (paired by seed: same split, noise draw and folds) ----------
from scriptorium_stats import paired_t_p, diff_ci95_low, diff_ci95_high, cohens_dz


def _half(v):
    return [50.0] * len(v)


# filter vs no-filter logistic regression
@source("p_dg0_filter_vs_logreg", means="p-value, paired t-test over 5 seeds, filter vs no-filter logistic regression test accuracy, digits, noise 0.0 (cost on clean labels)")
def p_dg0_filter_vs_logreg():
    return paired_t_p(_accs("digits", 0.0, "filter"), _accs("digits", 0.0, "logreg"))


@source("dg0_logreg_diff_ci_low", means="lower end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, digits, noise 0.0, 5 seeds")
def dg0_logreg_diff_ci_low():
    return diff_ci95_low(_accs("digits", 0.0, "filter"), _accs("digits", 0.0, "logreg"))


@source("dg0_logreg_diff_ci_high", means="upper end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, digits, noise 0.0, 5 seeds")
def dg0_logreg_diff_ci_high():
    return diff_ci95_high(_accs("digits", 0.0, "filter"), _accs("digits", 0.0, "logreg"))


@source("p_bc0_filter_vs_logreg", means="p-value, paired t-test over 5 seeds, filter vs no-filter logistic regression test accuracy, breast_cancer, noise 0.0 (cost on clean labels)")
def p_bc0_filter_vs_logreg():
    return paired_t_p(_accs("breast_cancer", 0.0, "filter"), _accs("breast_cancer", 0.0, "logreg"))


@source("bc0_logreg_diff_ci_low", means="lower end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, breast_cancer, noise 0.0, 5 seeds")
def bc0_logreg_diff_ci_low():
    return diff_ci95_low(_accs("breast_cancer", 0.0, "filter"), _accs("breast_cancer", 0.0, "logreg"))


@source("bc0_logreg_diff_ci_high", means="upper end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, breast_cancer, noise 0.0, 5 seeds")
def bc0_logreg_diff_ci_high():
    return diff_ci95_high(_accs("breast_cancer", 0.0, "filter"), _accs("breast_cancer", 0.0, "logreg"))


@source("p_dg20_filter_vs_logreg", means="p-value, paired t-test over 5 seeds, filter vs no-filter logistic regression test accuracy, digits, noise 0.2")
def p_dg20_filter_vs_logreg():
    return paired_t_p(_accs("digits", 0.2, "filter"), _accs("digits", 0.2, "logreg"))


@source("dg20_logreg_diff_ci_low", means="lower end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, digits, noise 0.2, 5 seeds")
def dg20_logreg_diff_ci_low():
    return diff_ci95_low(_accs("digits", 0.2, "filter"), _accs("digits", 0.2, "logreg"))


@source("dg20_logreg_diff_ci_high", means="upper end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, digits, noise 0.2, 5 seeds")
def dg20_logreg_diff_ci_high():
    return diff_ci95_high(_accs("digits", 0.2, "filter"), _accs("digits", 0.2, "logreg"))


@source("dz_dg20_filter_vs_logreg", means="Cohen's dz (paired effect size), filter vs no-filter logistic regression test accuracy, digits, noise 0.2, 5 seeds")
def dz_dg20_filter_vs_logreg():
    return cohens_dz(_accs("digits", 0.2, "filter"), _accs("digits", 0.2, "logreg"))


@source("p_dg40_filter_vs_logreg", means="p-value, paired t-test over 5 seeds, filter vs no-filter logistic regression test accuracy, digits, noise 0.4")
def p_dg40_filter_vs_logreg():
    return paired_t_p(_accs("digits", 0.4, "filter"), _accs("digits", 0.4, "logreg"))


@source("dg40_logreg_diff_ci_low", means="lower end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, digits, noise 0.4, 5 seeds")
def dg40_logreg_diff_ci_low():
    return diff_ci95_low(_accs("digits", 0.4, "filter"), _accs("digits", 0.4, "logreg"))


@source("dg40_logreg_diff_ci_high", means="upper end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, digits, noise 0.4, 5 seeds")
def dg40_logreg_diff_ci_high():
    return diff_ci95_high(_accs("digits", 0.4, "filter"), _accs("digits", 0.4, "logreg"))


@source("dz_dg40_filter_vs_logreg", means="Cohen's dz (paired effect size), filter vs no-filter logistic regression test accuracy, digits, noise 0.4, 5 seeds")
def dz_dg40_filter_vs_logreg():
    return cohens_dz(_accs("digits", 0.4, "filter"), _accs("digits", 0.4, "logreg"))


@source("p_bc20_filter_vs_logreg", means="p-value, paired t-test over 5 seeds, filter vs no-filter logistic regression test accuracy, breast_cancer, noise 0.2")
def p_bc20_filter_vs_logreg():
    return paired_t_p(_accs("breast_cancer", 0.2, "filter"), _accs("breast_cancer", 0.2, "logreg"))


@source("bc20_logreg_diff_ci_low", means="lower end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, breast_cancer, noise 0.2, 5 seeds")
def bc20_logreg_diff_ci_low():
    return diff_ci95_low(_accs("breast_cancer", 0.2, "filter"), _accs("breast_cancer", 0.2, "logreg"))


@source("bc20_logreg_diff_ci_high", means="upper end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, breast_cancer, noise 0.2, 5 seeds")
def bc20_logreg_diff_ci_high():
    return diff_ci95_high(_accs("breast_cancer", 0.2, "filter"), _accs("breast_cancer", 0.2, "logreg"))


@source("dz_bc20_filter_vs_logreg", means="Cohen's dz (paired effect size), filter vs no-filter logistic regression test accuracy, breast_cancer, noise 0.2, 5 seeds")
def dz_bc20_filter_vs_logreg():
    return cohens_dz(_accs("breast_cancer", 0.2, "filter"), _accs("breast_cancer", 0.2, "logreg"))


@source("p_bc40_filter_vs_logreg", means="p-value, paired t-test over 5 seeds, filter vs no-filter logistic regression test accuracy, breast_cancer, noise 0.4")
def p_bc40_filter_vs_logreg():
    return paired_t_p(_accs("breast_cancer", 0.4, "filter"), _accs("breast_cancer", 0.4, "logreg"))


@source("bc40_logreg_diff_ci_low", means="lower end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, breast_cancer, noise 0.4, 5 seeds")
def bc40_logreg_diff_ci_low():
    return diff_ci95_low(_accs("breast_cancer", 0.4, "filter"), _accs("breast_cancer", 0.4, "logreg"))


@source("bc40_logreg_diff_ci_high", means="upper end of the 95% interval (points) of the paired difference filter minus logistic regression, test accuracy, breast_cancer, noise 0.4, 5 seeds")
def bc40_logreg_diff_ci_high():
    return diff_ci95_high(_accs("breast_cancer", 0.4, "filter"), _accs("breast_cancer", 0.4, "logreg"))


@source("dz_bc40_filter_vs_logreg", means="Cohen's dz (paired effect size), filter vs no-filter logistic regression test accuracy, breast_cancer, noise 0.4, 5 seeds")
def dz_bc40_filter_vs_logreg():
    return cohens_dz(_accs("breast_cancer", 0.4, "filter"), _accs("breast_cancer", 0.4, "logreg"))


# filter vs MLP
@source("p_dg0_filter_vs_mlp", means="p-value, paired t-test over 5 seeds, filter vs the MLP test accuracy, digits, noise 0.0")
def p_dg0_filter_vs_mlp():
    return paired_t_p(_accs("digits", 0.0, "filter"), _accs("digits", 0.0, "mlp"))


@source("p_bc0_filter_vs_mlp", means="p-value, paired t-test over 5 seeds, filter vs the MLP test accuracy, breast_cancer, noise 0.0")
def p_bc0_filter_vs_mlp():
    return paired_t_p(_accs("breast_cancer", 0.0, "filter"), _accs("breast_cancer", 0.0, "mlp"))


@source("p_dg20_filter_vs_mlp", means="p-value, paired t-test over 5 seeds, filter vs the MLP test accuracy, digits, noise 0.2")
def p_dg20_filter_vs_mlp():
    return paired_t_p(_accs("digits", 0.2, "filter"), _accs("digits", 0.2, "mlp"))


@source("dg20_mlp_diff_ci_low", means="lower end of the 95% interval (points) of the paired difference filter minus MLP, test accuracy, digits, noise 0.2, 5 seeds")
def dg20_mlp_diff_ci_low():
    return diff_ci95_low(_accs("digits", 0.2, "filter"), _accs("digits", 0.2, "mlp"))


@source("dg20_mlp_diff_ci_high", means="upper end of the 95% interval (points) of the paired difference filter minus MLP, test accuracy, digits, noise 0.2, 5 seeds")
def dg20_mlp_diff_ci_high():
    return diff_ci95_high(_accs("digits", 0.2, "filter"), _accs("digits", 0.2, "mlp"))


@source("p_dg40_filter_vs_mlp", means="p-value, paired t-test over 5 seeds, filter vs the MLP test accuracy, digits, noise 0.4")
def p_dg40_filter_vs_mlp():
    return paired_t_p(_accs("digits", 0.4, "filter"), _accs("digits", 0.4, "mlp"))


@source("dg40_mlp_diff_ci_low", means="lower end of the 95% interval (points) of the paired difference filter minus MLP, test accuracy, digits, noise 0.4, 5 seeds")
def dg40_mlp_diff_ci_low():
    return diff_ci95_low(_accs("digits", 0.4, "filter"), _accs("digits", 0.4, "mlp"))


@source("dg40_mlp_diff_ci_high", means="upper end of the 95% interval (points) of the paired difference filter minus MLP, test accuracy, digits, noise 0.4, 5 seeds")
def dg40_mlp_diff_ci_high():
    return diff_ci95_high(_accs("digits", 0.4, "filter"), _accs("digits", 0.4, "mlp"))


@source("p_bc20_filter_vs_mlp", means="p-value, paired t-test over 5 seeds, filter vs the MLP test accuracy, breast_cancer, noise 0.2")
def p_bc20_filter_vs_mlp():
    return paired_t_p(_accs("breast_cancer", 0.2, "filter"), _accs("breast_cancer", 0.2, "mlp"))


@source("bc20_mlp_diff_ci_low", means="lower end of the 95% interval (points) of the paired difference filter minus MLP, test accuracy, breast_cancer, noise 0.2, 5 seeds")
def bc20_mlp_diff_ci_low():
    return diff_ci95_low(_accs("breast_cancer", 0.2, "filter"), _accs("breast_cancer", 0.2, "mlp"))


@source("bc20_mlp_diff_ci_high", means="upper end of the 95% interval (points) of the paired difference filter minus MLP, test accuracy, breast_cancer, noise 0.2, 5 seeds")
def bc20_mlp_diff_ci_high():
    return diff_ci95_high(_accs("breast_cancer", 0.2, "filter"), _accs("breast_cancer", 0.2, "mlp"))


@source("p_bc40_filter_vs_mlp", means="p-value, paired t-test over 5 seeds, filter vs the MLP test accuracy, breast_cancer, noise 0.4")
def p_bc40_filter_vs_mlp():
    return paired_t_p(_accs("breast_cancer", 0.4, "filter"), _accs("breast_cancer", 0.4, "mlp"))


@source("bc40_mlp_diff_ci_low", means="lower end of the 95% interval (points) of the paired difference filter minus MLP, test accuracy, breast_cancer, noise 0.4, 5 seeds")
def bc40_mlp_diff_ci_low():
    return diff_ci95_low(_accs("breast_cancer", 0.4, "filter"), _accs("breast_cancer", 0.4, "mlp"))


@source("bc40_mlp_diff_ci_high", means="upper end of the 95% interval (points) of the paired difference filter minus MLP, test accuracy, breast_cancer, noise 0.4, 5 seeds")
def bc40_mlp_diff_ci_high():
    return diff_ci95_high(_accs("breast_cancer", 0.4, "filter"), _accs("breast_cancer", 0.4, "mlp"))


# precision above one half
@source("p_dg20_prec_vs_half", means="p-value, paired t-test over 5 seeds, filter precision (%) vs 50%, digits, noise 0.2 (are most dropped samples mislabeled)")
def p_dg20_prec_vs_half():
    return paired_t_p(_precisions("digits", 0.2), _half(_precisions("digits", 0.2)))


@source("p_dg40_prec_vs_half", means="p-value, paired t-test over 5 seeds, filter precision (%) vs 50%, digits, noise 0.4")
def p_dg40_prec_vs_half():
    return paired_t_p(_precisions("digits", 0.4), _half(_precisions("digits", 0.4)))


@source("p_bc20_prec_vs_half", means="p-value, paired t-test over 5 seeds, filter precision (%) vs 50%, breast_cancer, noise 0.2")
def p_bc20_prec_vs_half():
    return paired_t_p(_precisions("breast_cancer", 0.2), _half(_precisions("breast_cancer", 0.2)))


@source("p_bc40_prec_vs_half", means="p-value, paired t-test over 5 seeds, filter precision (%) vs 50%, breast_cancer, noise 0.4")
def p_bc40_prec_vs_half():
    return paired_t_p(_precisions("breast_cancer", 0.4), _half(_precisions("breast_cancer", 0.4)))


# does the filter fully close the gap to clean-label logistic regression
@source("p_dg20_filter_vs_clean", means="p-value, paired t-test over 5 seeds, filter at noise 0.2 vs logistic regression at noise 0.0, test accuracy, digits")
def p_dg20_filter_vs_clean():
    return paired_t_p(_accs("digits", 0.2, "filter"), _accs("digits", 0.0, "logreg"))


@source("p_dg40_filter_vs_clean", means="p-value, paired t-test over 5 seeds, filter at noise 0.4 vs logistic regression at noise 0.0, test accuracy, digits")
def p_dg40_filter_vs_clean():
    return paired_t_p(_accs("digits", 0.4, "filter"), _accs("digits", 0.0, "logreg"))


@source("p_bc20_filter_vs_clean", means="p-value, paired t-test over 5 seeds, filter at noise 0.2 vs logistic regression at noise 0.0, test accuracy, breast_cancer")
def p_bc20_filter_vs_clean():
    return paired_t_p(_accs("breast_cancer", 0.2, "filter"), _accs("breast_cancer", 0.0, "logreg"))


@source("p_bc40_filter_vs_clean", means="p-value, paired t-test over 5 seeds, filter at noise 0.4 vs logistic regression at noise 0.0, test accuracy, breast_cancer")
def p_bc40_filter_vs_clean():
    return paired_t_p(_accs("breast_cancer", 0.4, "filter"), _accs("breast_cancer", 0.0, "logreg"))


# noise hurts logistic regression (trend: ends of the noise range)
@source("p_dg_loss_n40", means="p-value, paired t-test over 5 seeds, logistic regression test accuracy at noise 0.0 vs 0.4, digits")
def p_dg_loss_n40():
    return paired_t_p(_accs("digits", 0.0, "logreg"), _accs("digits", 0.4, "logreg"))


@source("p_bc_loss_n40", means="p-value, paired t-test over 5 seeds, logistic regression test accuracy at noise 0.0 vs 0.4, breast_cancer")
def p_bc_loss_n40():
    return paired_t_p(_accs("breast_cancer", 0.0, "logreg"), _accs("breast_cancer", 0.4, "logreg"))


@source("actual_noise_digits_n20", means="actual share (%) of training labels flipped on digits at nominal 20% noise, mean over 5 seeds")
def actual_noise_digits_n20():
    return _mean([100 * r["n_noisy"] / r["n_train"] for r in _runs("digits", 0.2, "logreg")])


@source("actual_noise_bc_n20", means="actual share (%) of training labels flipped on breast_cancer at nominal 20% noise, mean over 5 seeds")
def actual_noise_bc_n20():
    return _mean([100 * r["n_noisy"] / r["n_train"] for r in _runs("breast_cancer", 0.2, "logreg")])


@source("kept_digits_n40", means="training samples kept by the filter on digits at 40% noise, mean over 5 seeds")
def kept_digits_n40():
    return _mean([r["n_train"] - r["n_dropped"] for r in _runs("digits", 0.4, "filter")])


@source("kept_bc_n40", means="training samples kept by the filter on breast_cancer at 40% noise, mean over 5 seeds")
def kept_bc_n40():
    return _mean([r["n_train"] - r["n_dropped"] for r in _runs("breast_cancer", 0.4, "filter")])


@source("p_prec_vs_half_max", means="largest of the four p-values (paired t-test over 5 seeds) of filter precision vs 50%, both datasets, noise 0.2 and 0.4")
def p_prec_vs_half_max():
    return max(paired_t_p(_precisions(d, n), _half(_precisions(d, n)))
               for d in ("digits", "breast_cancer") for n in (0.2, 0.4))
