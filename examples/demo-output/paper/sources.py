"""Recipes for the numbers in this paper. Each returns the unrounded value printed next to \\src{key}.

`source` and `load(path)` are provided by the checker; do not import or define them. Paths are relative to the
repository root. Read raw results, configs or scripts, never Markdown notes.

Per-seed helpers (underscore names) return one value per seed in seed order 0-4, so tests can pair them.
"""


def _rows(dataset=None, noise=None, method=None):
    out = []
    for r in load("results/runs.jsonl"):
        if dataset is not None and r["dataset"] != dataset:
            continue
        if noise is not None and abs(r["noise"] - noise) > 1e-9:
            continue
        if method is not None and r["method"] != method:
            continue
        out.append(r)
    return sorted(out, key=lambda r: r["seed"])


def _accs(dataset, noise, method):
    """Test accuracy (%) per seed."""
    return [100 * r["test_acc"] for r in _rows(dataset, noise, method)]


def _diff(dataset, noise, a, b):
    """Per-seed accuracy difference (points), a minus b, paired by seed."""
    return [x - y for x, y in zip(_accs(dataset, noise, a), _accs(dataset, noise, b))]


def _precisions(dataset, noise):
    """Per-seed filter precision (%): dropped samples that were truly flipped."""
    return [100 * r["n_dropped_noisy"] / r["n_dropped"] for r in _rows(dataset, noise, "filter")]


def _recalls(dataset, noise):
    """Per-seed filter recall (%): flipped samples that were dropped."""
    return [100 * r["n_dropped_noisy"] / r["n_noisy"] for r in _rows(dataset, noise, "filter")]


def _dropped(dataset, noise):
    """Per-seed number of dropped training samples."""
    return [r["n_dropped"] for r in _rows(dataset, noise, "filter")]


def _mean(xs):
    return sum(xs) / len(xs)


def _sd(xs):
    import statistics
    return statistics.stdev(xs)


def _gain(d, n, a, b):
    return _mean(_diff(d, n, a, b))


def _loss(d, n):
    return _mean(_accs(d, 0.0, "logreg")) - _mean(_accs(d, n, "logreg"))


def _recovered(d, n):
    return 100 * _gain(d, n, "filter", "logreg") / _loss(d, n)


# ---- main grid: mean test accuracy (%) -----------------------------------------------------------------
@source("acc_logreg_digits_n0", means="test accuracy (%) of logreg on digits at 0% label noise, mean over seeds 0-4")
def acc_logreg_digits_n0(): return _mean(_accs("digits", 0.0, "logreg"))
@source("acc_mlp_digits_n0", means="test accuracy (%) of mlp on digits at 0% label noise, mean over seeds 0-4")
def acc_mlp_digits_n0(): return _mean(_accs("digits", 0.0, "mlp"))
@source("acc_filter_digits_n0", means="test accuracy (%) of filter on digits at 0% label noise, mean over seeds 0-4")
def acc_filter_digits_n0(): return _mean(_accs("digits", 0.0, "filter"))
@source("acc_logreg_digits_n20", means="test accuracy (%) of logreg on digits at 20% label noise, mean over seeds 0-4")
def acc_logreg_digits_n20(): return _mean(_accs("digits", 0.2, "logreg"))
@source("acc_mlp_digits_n20", means="test accuracy (%) of mlp on digits at 20% label noise, mean over seeds 0-4")
def acc_mlp_digits_n20(): return _mean(_accs("digits", 0.2, "mlp"))
@source("acc_filter_digits_n20", means="test accuracy (%) of filter on digits at 20% label noise, mean over seeds 0-4")
def acc_filter_digits_n20(): return _mean(_accs("digits", 0.2, "filter"))
@source("acc_logreg_digits_n40", means="test accuracy (%) of logreg on digits at 40% label noise, mean over seeds 0-4")
def acc_logreg_digits_n40(): return _mean(_accs("digits", 0.4, "logreg"))
@source("acc_mlp_digits_n40", means="test accuracy (%) of mlp on digits at 40% label noise, mean over seeds 0-4")
def acc_mlp_digits_n40(): return _mean(_accs("digits", 0.4, "mlp"))
@source("acc_filter_digits_n40", means="test accuracy (%) of filter on digits at 40% label noise, mean over seeds 0-4")
def acc_filter_digits_n40(): return _mean(_accs("digits", 0.4, "filter"))
@source("acc_logreg_breast_cancer_n0", means="test accuracy (%) of logreg on breast_cancer at 0% label noise, mean over seeds 0-4")
def acc_logreg_breast_cancer_n0(): return _mean(_accs("breast_cancer", 0.0, "logreg"))
@source("acc_mlp_breast_cancer_n0", means="test accuracy (%) of mlp on breast_cancer at 0% label noise, mean over seeds 0-4")
def acc_mlp_breast_cancer_n0(): return _mean(_accs("breast_cancer", 0.0, "mlp"))
@source("acc_filter_breast_cancer_n0", means="test accuracy (%) of filter on breast_cancer at 0% label noise, mean over seeds 0-4")
def acc_filter_breast_cancer_n0(): return _mean(_accs("breast_cancer", 0.0, "filter"))
@source("acc_logreg_breast_cancer_n20", means="test accuracy (%) of logreg on breast_cancer at 20% label noise, mean over seeds 0-4")
def acc_logreg_breast_cancer_n20(): return _mean(_accs("breast_cancer", 0.2, "logreg"))
@source("acc_mlp_breast_cancer_n20", means="test accuracy (%) of mlp on breast_cancer at 20% label noise, mean over seeds 0-4")
def acc_mlp_breast_cancer_n20(): return _mean(_accs("breast_cancer", 0.2, "mlp"))
@source("acc_filter_breast_cancer_n20", means="test accuracy (%) of filter on breast_cancer at 20% label noise, mean over seeds 0-4")
def acc_filter_breast_cancer_n20(): return _mean(_accs("breast_cancer", 0.2, "filter"))
@source("acc_logreg_breast_cancer_n40", means="test accuracy (%) of logreg on breast_cancer at 40% label noise, mean over seeds 0-4")
def acc_logreg_breast_cancer_n40(): return _mean(_accs("breast_cancer", 0.4, "logreg"))
@source("acc_mlp_breast_cancer_n40", means="test accuracy (%) of mlp on breast_cancer at 40% label noise, mean over seeds 0-4")
def acc_mlp_breast_cancer_n40(): return _mean(_accs("breast_cancer", 0.4, "mlp"))
@source("acc_filter_breast_cancer_n40", means="test accuracy (%) of filter on breast_cancer at 40% label noise, mean over seeds 0-4")
def acc_filter_breast_cancer_n40(): return _mean(_accs("breast_cancer", 0.4, "filter"))


# ---- main grid: standard deviation over seeds (points) --------------------------------------------------
@source("sd_logreg_digits_n0", means="sample sd (points) over seeds 0-4 of test accuracy, logreg, digits, 0% noise")
def sd_logreg_digits_n0(): return _sd(_accs("digits", 0.0, "logreg"))
@source("sd_mlp_digits_n0", means="sample sd (points) over seeds 0-4 of test accuracy, mlp, digits, 0% noise")
def sd_mlp_digits_n0(): return _sd(_accs("digits", 0.0, "mlp"))
@source("sd_filter_digits_n0", means="sample sd (points) over seeds 0-4 of test accuracy, filter, digits, 0% noise")
def sd_filter_digits_n0(): return _sd(_accs("digits", 0.0, "filter"))
@source("sd_logreg_digits_n20", means="sample sd (points) over seeds 0-4 of test accuracy, logreg, digits, 20% noise")
def sd_logreg_digits_n20(): return _sd(_accs("digits", 0.2, "logreg"))
@source("sd_mlp_digits_n20", means="sample sd (points) over seeds 0-4 of test accuracy, mlp, digits, 20% noise")
def sd_mlp_digits_n20(): return _sd(_accs("digits", 0.2, "mlp"))
@source("sd_filter_digits_n20", means="sample sd (points) over seeds 0-4 of test accuracy, filter, digits, 20% noise")
def sd_filter_digits_n20(): return _sd(_accs("digits", 0.2, "filter"))
@source("sd_logreg_digits_n40", means="sample sd (points) over seeds 0-4 of test accuracy, logreg, digits, 40% noise")
def sd_logreg_digits_n40(): return _sd(_accs("digits", 0.4, "logreg"))
@source("sd_mlp_digits_n40", means="sample sd (points) over seeds 0-4 of test accuracy, mlp, digits, 40% noise")
def sd_mlp_digits_n40(): return _sd(_accs("digits", 0.4, "mlp"))
@source("sd_filter_digits_n40", means="sample sd (points) over seeds 0-4 of test accuracy, filter, digits, 40% noise")
def sd_filter_digits_n40(): return _sd(_accs("digits", 0.4, "filter"))
@source("sd_logreg_breast_cancer_n0", means="sample sd (points) over seeds 0-4 of test accuracy, logreg, breast_cancer, 0% noise")
def sd_logreg_breast_cancer_n0(): return _sd(_accs("breast_cancer", 0.0, "logreg"))
@source("sd_mlp_breast_cancer_n0", means="sample sd (points) over seeds 0-4 of test accuracy, mlp, breast_cancer, 0% noise")
def sd_mlp_breast_cancer_n0(): return _sd(_accs("breast_cancer", 0.0, "mlp"))
@source("sd_filter_breast_cancer_n0", means="sample sd (points) over seeds 0-4 of test accuracy, filter, breast_cancer, 0% noise")
def sd_filter_breast_cancer_n0(): return _sd(_accs("breast_cancer", 0.0, "filter"))
@source("sd_logreg_breast_cancer_n20", means="sample sd (points) over seeds 0-4 of test accuracy, logreg, breast_cancer, 20% noise")
def sd_logreg_breast_cancer_n20(): return _sd(_accs("breast_cancer", 0.2, "logreg"))
@source("sd_mlp_breast_cancer_n20", means="sample sd (points) over seeds 0-4 of test accuracy, mlp, breast_cancer, 20% noise")
def sd_mlp_breast_cancer_n20(): return _sd(_accs("breast_cancer", 0.2, "mlp"))
@source("sd_filter_breast_cancer_n20", means="sample sd (points) over seeds 0-4 of test accuracy, filter, breast_cancer, 20% noise")
def sd_filter_breast_cancer_n20(): return _sd(_accs("breast_cancer", 0.2, "filter"))
@source("sd_logreg_breast_cancer_n40", means="sample sd (points) over seeds 0-4 of test accuracy, logreg, breast_cancer, 40% noise")
def sd_logreg_breast_cancer_n40(): return _sd(_accs("breast_cancer", 0.4, "logreg"))
@source("sd_mlp_breast_cancer_n40", means="sample sd (points) over seeds 0-4 of test accuracy, mlp, breast_cancer, 40% noise")
def sd_mlp_breast_cancer_n40(): return _sd(_accs("breast_cancer", 0.4, "mlp"))
@source("sd_filter_breast_cancer_n40", means="sample sd (points) over seeds 0-4 of test accuracy, filter, breast_cancer, 40% noise")
def sd_filter_breast_cancer_n40(): return _sd(_accs("breast_cancer", 0.4, "filter"))


# ---- paired differences (points), mean over seeds 0-4 ---------------------------------------------------
@source("diff_filter_logreg_digits_n0", means="mean paired test-accuracy difference (points), filter minus logreg, digits, 0% noise, seeds 0-4")
def diff_filter_logreg_digits_n0(): return _gain("digits", 0.0, "filter", "logreg")
@source("diff_filter_logreg_digits_n20", means="mean paired test-accuracy difference (points), filter minus logreg, digits, 20% noise, seeds 0-4")
def diff_filter_logreg_digits_n20(): return _gain("digits", 0.2, "filter", "logreg")
@source("diff_filter_logreg_digits_n40", means="mean paired test-accuracy difference (points), filter minus logreg, digits, 40% noise, seeds 0-4")
def diff_filter_logreg_digits_n40(): return _gain("digits", 0.4, "filter", "logreg")
@source("diff_filter_logreg_breast_cancer_n0", means="mean paired test-accuracy difference (points), filter minus logreg, breast_cancer, 0% noise, seeds 0-4")
def diff_filter_logreg_breast_cancer_n0(): return _gain("breast_cancer", 0.0, "filter", "logreg")
@source("diff_filter_logreg_breast_cancer_n20", means="mean paired test-accuracy difference (points), filter minus logreg, breast_cancer, 20% noise, seeds 0-4")
def diff_filter_logreg_breast_cancer_n20(): return _gain("breast_cancer", 0.2, "filter", "logreg")
@source("diff_filter_logreg_breast_cancer_n40", means="mean paired test-accuracy difference (points), filter minus logreg, breast_cancer, 40% noise, seeds 0-4")
def diff_filter_logreg_breast_cancer_n40(): return _gain("breast_cancer", 0.4, "filter", "logreg")
@source("diff_filter_mlp_digits_n0", means="mean paired test-accuracy difference (points), filter minus mlp, digits, 0% noise, seeds 0-4")
def diff_filter_mlp_digits_n0(): return _gain("digits", 0.0, "filter", "mlp")
@source("diff_filter_mlp_digits_n20", means="mean paired test-accuracy difference (points), filter minus mlp, digits, 20% noise, seeds 0-4")
def diff_filter_mlp_digits_n20(): return _gain("digits", 0.2, "filter", "mlp")
@source("diff_filter_mlp_digits_n40", means="mean paired test-accuracy difference (points), filter minus mlp, digits, 40% noise, seeds 0-4")
def diff_filter_mlp_digits_n40(): return _gain("digits", 0.4, "filter", "mlp")
@source("diff_filter_mlp_breast_cancer_n0", means="mean paired test-accuracy difference (points), filter minus mlp, breast_cancer, 0% noise, seeds 0-4")
def diff_filter_mlp_breast_cancer_n0(): return _gain("breast_cancer", 0.0, "filter", "mlp")
@source("diff_filter_mlp_breast_cancer_n20", means="mean paired test-accuracy difference (points), filter minus mlp, breast_cancer, 20% noise, seeds 0-4")
def diff_filter_mlp_breast_cancer_n20(): return _gain("breast_cancer", 0.2, "filter", "mlp")
@source("diff_filter_mlp_breast_cancer_n40", means="mean paired test-accuracy difference (points), filter minus mlp, breast_cancer, 40% noise, seeds 0-4")
def diff_filter_mlp_breast_cancer_n40(): return _gain("breast_cancer", 0.4, "filter", "mlp")

@source("nwins_filter_mlp_noisy", means="number of (dataset, noise in {20%, 40%}, seed) runs, out of 20, where filter test accuracy exceeds mlp")
def nwins_filter_mlp_noisy(): return sum(1 for d in ("digits", "breast_cancer") for n in (0.2, 0.4) for x in _diff(d, n, "filter", "mlp") if x > 0)
@source("nwins_filter_logreg_noisy", means="number of (dataset, noise in {20%, 40%}, seed) runs, out of 20, where filter test accuracy exceeds logreg")
def nwins_filter_logreg_noisy(): return sum(1 for d in ("digits", "breast_cancer") for n in (0.2, 0.4) for x in _diff(d, n, "filter", "logreg") if x > 0)
@source("nwins_filter_logreg_clean", means="number of (dataset, seed) runs at 0% noise, out of 10, where filter test accuracy exceeds logreg")
def nwins_filter_logreg_clean(): return sum(1 for d in ("digits", "breast_cancer") for x in _diff(d, 0.0, "filter", "logreg") if x > 0)


# ---- recovery of the accuracy that noise costs ----------------------------------------------------------
@source("loss_logreg_digits_n20", means="accuracy (points) logreg loses on digits at 20% noise: mean at 0% minus mean at 20%, seeds 0-4")
def loss_logreg_digits_n20(): return _loss("digits", 0.2)
@source("loss_logreg_digits_n40", means="accuracy (points) logreg loses on digits at 40% noise: mean at 0% minus mean at 40%, seeds 0-4")
def loss_logreg_digits_n40(): return _loss("digits", 0.4)
@source("loss_logreg_breast_cancer_n20", means="accuracy (points) logreg loses on breast_cancer at 20% noise: mean at 0% minus mean at 20%, seeds 0-4")
def loss_logreg_breast_cancer_n20(): return _loss("breast_cancer", 0.2)
@source("loss_logreg_breast_cancer_n40", means="accuracy (points) logreg loses on breast_cancer at 40% noise: mean at 0% minus mean at 40%, seeds 0-4")
def loss_logreg_breast_cancer_n40(): return _loss("breast_cancer", 0.4)
@source("recovered_digits_n20", means="percent of logreg's accuracy loss at 20% noise on digits regained by filter: (filter - logreg)/(logreg at 0% - logreg), means over seeds 0-4")
def recovered_digits_n20(): return _recovered("digits", 0.2)
@source("recovered_digits_n40", means="percent of logreg's accuracy loss at 40% noise on digits regained by filter: (filter - logreg)/(logreg at 0% - logreg), means over seeds 0-4")
def recovered_digits_n40(): return _recovered("digits", 0.4)
@source("recovered_breast_cancer_n20", means="percent of logreg's accuracy loss at 20% noise on breast_cancer regained by filter: (filter - logreg)/(logreg at 0% - logreg), means over seeds 0-4")
def recovered_breast_cancer_n20(): return _recovered("breast_cancer", 0.2)
@source("recovered_breast_cancer_n40", means="percent of logreg's accuracy loss at 40% noise on breast_cancer regained by filter: (filter - logreg)/(logreg at 0% - logreg), means over seeds 0-4")
def recovered_breast_cancer_n40(): return _recovered("breast_cancer", 0.4)


# ---- cost when labels are clean -------------------------------------------------------------------------
@source("cost_clean_digits", means="mean paired test-accuracy drop (points) of filter relative to logreg at 0% noise on digits, seeds 0-4 (logreg minus filter)")
def cost_clean_digits(): return -_gain("digits", 0.0, "filter", "logreg")
@source("cost_clean_breast_cancer", means="mean paired test-accuracy drop (points) of filter relative to logreg at 0% noise on breast_cancer, seeds 0-4 (logreg minus filter)")
def cost_clean_breast_cancer(): return -_gain("breast_cancer", 0.0, "filter", "logreg")
@source("time_filter_over_logreg_digits_n0", means="ratio of mean fit_seconds, filter over logreg, digits, 0% noise, seeds 0-4 (indicative; machine unknown)")
def time_filter_over_logreg_digits_n0():
    return _mean([r["fit_seconds"] for r in _rows("digits", 0.0, "filter")]) / _mean([r["fit_seconds"] for r in _rows("digits", 0.0, "logreg")])


# ---- filter diagnostics ---------------------------------------------------------------------------------
@source("dropped_digits_n0", means="mean number of training samples the filter drops on digits at 0% noise, seeds 0-4")
def dropped_digits_n0(): return _mean(_dropped("digits", 0.0))
@source("dropped_digits_n20", means="mean number of training samples the filter drops on digits at 20% noise, seeds 0-4")
def dropped_digits_n20(): return _mean(_dropped("digits", 0.2))
@source("dropped_digits_n40", means="mean number of training samples the filter drops on digits at 40% noise, seeds 0-4")
def dropped_digits_n40(): return _mean(_dropped("digits", 0.4))
@source("dropped_breast_cancer_n0", means="mean number of training samples the filter drops on breast_cancer at 0% noise, seeds 0-4")
def dropped_breast_cancer_n0(): return _mean(_dropped("breast_cancer", 0.0))
@source("dropped_breast_cancer_n20", means="mean number of training samples the filter drops on breast_cancer at 20% noise, seeds 0-4")
def dropped_breast_cancer_n20(): return _mean(_dropped("breast_cancer", 0.2))
@source("dropped_breast_cancer_n40", means="mean number of training samples the filter drops on breast_cancer at 40% noise, seeds 0-4")
def dropped_breast_cancer_n40(): return _mean(_dropped("breast_cancer", 0.4))
@source("dropped_pct_digits_n0", means="mean percent of the 1257 digits training samples dropped by the filter at 0% noise, seeds 0-4")
def dropped_pct_digits_n0(): return _mean([100 * r["n_dropped"] / r["n_train"] for r in _rows("digits", 0.0, "filter")])
@source("dropped_pct_breast_cancer_n0", means="mean percent of breast_cancer training samples dropped by the filter at 0% noise, seeds 0-4")
def dropped_pct_breast_cancer_n0(): return _mean([100 * r["n_dropped"] / r["n_train"] for r in _rows("breast_cancer", 0.0, "filter")])

@source("precision_digits_n20", means="mean over seeds 0-4 of filter precision (%), dropped samples truly flipped, digits, 20% noise")
def precision_digits_n20(): return _mean(_precisions("digits", 0.2))
@source("precision_digits_n40", means="mean over seeds 0-4 of filter precision (%), dropped samples truly flipped, digits, 40% noise")
def precision_digits_n40(): return _mean(_precisions("digits", 0.4))
@source("precision_breast_cancer_n20", means="mean over seeds 0-4 of filter precision (%), dropped samples truly flipped, breast_cancer, 20% noise")
def precision_breast_cancer_n20(): return _mean(_precisions("breast_cancer", 0.2))
@source("precision_breast_cancer_n40", means="mean over seeds 0-4 of filter precision (%), dropped samples truly flipped, breast_cancer, 40% noise")
def precision_breast_cancer_n40(): return _mean(_precisions("breast_cancer", 0.4))
@source("precision_min_digits_n40", means="lowest per-seed filter precision (%) over seeds 0-4, digits, 40% noise")
def precision_min_digits_n40(): return min(_precisions("digits", 0.4))
@source("precision_min_breast_cancer_n40", means="lowest per-seed filter precision (%) over seeds 0-4, breast_cancer, 40% noise")
def precision_min_breast_cancer_n40(): return min(_precisions("breast_cancer", 0.4))
@source("precision_pooled_noisy", means="mean filter precision (%) over both datasets, 20% and 40% noise, seeds 0-4 (20 runs)")
def precision_pooled_noisy(): return _mean([p for d in ("digits", "breast_cancer") for n in (0.2, 0.4) for p in _precisions(d, n)])
@source("recall_digits_n20", means="mean over seeds 0-4 of filter recall (%), flipped samples dropped, digits, 20% noise")
def recall_digits_n20(): return _mean(_recalls("digits", 0.2))
@source("recall_digits_n40", means="mean over seeds 0-4 of filter recall (%), flipped samples dropped, digits, 40% noise")
def recall_digits_n40(): return _mean(_recalls("digits", 0.4))
@source("recall_breast_cancer_n20", means="mean over seeds 0-4 of filter recall (%), flipped samples dropped, breast_cancer, 20% noise")
def recall_breast_cancer_n20(): return _mean(_recalls("breast_cancer", 0.2))
@source("recall_breast_cancer_n40", means="mean over seeds 0-4 of filter recall (%), flipped samples dropped, breast_cancer, 40% noise")
def recall_breast_cancer_n40(): return _mean(_recalls("breast_cancer", 0.4))
@source("noisy_pct_digits_n40", means="mean realized percent of digits training labels flipped at nominal 40% noise, seeds 0-4")
def noisy_pct_digits_n40(): return _mean([100 * r["n_noisy"] / r["n_train"] for r in _rows("digits", 0.4, "filter")])
@source("noisy_pct_breast_cancer_n40", means="mean realized percent of breast_cancer training labels flipped at nominal 40% noise, seeds 0-4")
def noisy_pct_breast_cancer_n40(): return _mean([100 * r["n_noisy"] / r["n_train"] for r in _rows("breast_cancer", 0.4, "filter")])


# ---- dataset sizes and settings -------------------------------------------------------------------------
@source("n_train_digits", means="number of training samples in digits (70% split)")
def n_train_digits(): return _rows("digits", 0.0, "logreg")[0]["n_train"]
@source("n_test_digits", means="number of test samples in digits (30% split)")
def n_test_digits(): return _rows("digits", 0.0, "logreg")[0]["n_test"]
@source("n_total_digits", means="total samples in digits (n_train + n_test)")
def n_total_digits(): return _rows("digits", 0.0, "logreg")[0]["n_train"] + _rows("digits", 0.0, "logreg")[0]["n_test"]
@source("n_train_breast_cancer", means="number of training samples in breast_cancer (70% split)")
def n_train_breast_cancer(): return _rows("breast_cancer", 0.0, "logreg")[0]["n_train"]
@source("n_test_breast_cancer", means="number of test samples in breast_cancer (30% split)")
def n_test_breast_cancer(): return _rows("breast_cancer", 0.0, "logreg")[0]["n_test"]
@source("n_total_breast_cancer", means="total samples in breast_cancer (n_train + n_test)")
def n_total_breast_cancer(): return _rows("breast_cancer", 0.0, "logreg")[0]["n_train"] + _rows("breast_cancer", 0.0, "logreg")[0]["n_test"]
@source("n_seeds", means="number of seeds in the config")
def n_seeds(): return len(load("experiments/config.json")["seeds"])
@source("n_runs", means="number of records in results/runs.jsonl (datasets x noise rates x seeds x methods)")
def n_runs(): return len(load("results/runs.jsonl"))
@source("n_datasets", means="number of datasets in the config")
def n_datasets(): return len(load("experiments/config.json")["datasets"])
@source("n_noise_rates", means="number of noise rates in the config, including 0%")
def n_noise_rates(): return len(load("experiments/config.json")["noise_rates"])
@source("noise_low_pct", means="lower non-zero label-noise rate (%) from the config")
def noise_low_pct(): return 100 * sorted(load("experiments/config.json")["noise_rates"])[1]
@source("noise_high_pct", means="highest label-noise rate (%) from the config")
def noise_high_pct(): return 100 * max(load("experiments/config.json")["noise_rates"])
@source("test_fraction_pct", means="test split fraction (%) from the config")
def test_fraction_pct(): return 100 * load("experiments/config.json")["test_fraction"]
@source("logreg_C", means="inverse regularization strength C of logistic regression, from the config")
def logreg_C(): return load("experiments/config.json")["logreg_C"]
@source("mlp_hidden", means="hidden units of the MLP (one hidden layer), from the config")
def mlp_hidden(): return load("experiments/config.json")["mlp_hidden"]
@source("mlp_max_iter", means="maximum training iterations of the MLP, from the config")
def mlp_max_iter(): return load("experiments/config.json")["mlp_max_iter"]
@source("filter_folds", means="number of cross-validation folds used by the filter, from the config")
def filter_folds(): return load("experiments/config.json")["filter_folds"]


# ---- statistical tests (paired by seed; same split, noise draw and folds within a seed) -------------------
from scriptorium_stats import paired_t_p, diff_ci95_low, diff_ci95_high, cohens_dz


def _pr(ds, n, base):
    """(filter accuracies, baseline accuracies) per seed, in seed order."""
    return _accs(ds, n, "filter"), _accs(ds, n, base)


# digits vs logreg
@source("p_dg0_filter_vs_lr", means="p-value, two-sided paired t-test over 5 seeds, filter vs logreg test accuracy, digits, 0% noise")
def p_dg0_filter_vs_lr(): return paired_t_p(*_pr("digits", 0.0, "logreg"))
@source("dg0_lr_diff_ci_low", means="lower end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, digits, 0% noise")
def dg0_lr_diff_ci_low(): return diff_ci95_low(*_pr("digits", 0.0, "logreg"))
@source("dg0_lr_diff_ci_high", means="upper end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, digits, 0% noise")
def dg0_lr_diff_ci_high(): return diff_ci95_high(*_pr("digits", 0.0, "logreg"))
@source("dz_dg0_filter_vs_lr", means="Cohen's dz of paired filter minus logreg accuracy difference, 5 seeds, digits, 0% noise")
def dz_dg0_filter_vs_lr(): return cohens_dz(*_pr("digits", 0.0, "logreg"))
@source("p_dg20_filter_vs_lr", means="p-value, two-sided paired t-test over 5 seeds, filter vs logreg test accuracy, digits, 20% noise")
def p_dg20_filter_vs_lr(): return paired_t_p(*_pr("digits", 0.2, "logreg"))
@source("dg20_lr_diff_ci_low", means="lower end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, digits, 20% noise")
def dg20_lr_diff_ci_low(): return diff_ci95_low(*_pr("digits", 0.2, "logreg"))
@source("dg20_lr_diff_ci_high", means="upper end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, digits, 20% noise")
def dg20_lr_diff_ci_high(): return diff_ci95_high(*_pr("digits", 0.2, "logreg"))
@source("dz_dg20_filter_vs_lr", means="Cohen's dz of paired filter minus logreg accuracy difference, 5 seeds, digits, 20% noise")
def dz_dg20_filter_vs_lr(): return cohens_dz(*_pr("digits", 0.2, "logreg"))
@source("p_dg40_filter_vs_lr", means="p-value, two-sided paired t-test over 5 seeds, filter vs logreg test accuracy, digits, 40% noise")
def p_dg40_filter_vs_lr(): return paired_t_p(*_pr("digits", 0.4, "logreg"))
@source("dg40_lr_diff_ci_low", means="lower end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, digits, 40% noise")
def dg40_lr_diff_ci_low(): return diff_ci95_low(*_pr("digits", 0.4, "logreg"))
@source("dg40_lr_diff_ci_high", means="upper end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, digits, 40% noise")
def dg40_lr_diff_ci_high(): return diff_ci95_high(*_pr("digits", 0.4, "logreg"))
@source("dz_dg40_filter_vs_lr", means="Cohen's dz of paired filter minus logreg accuracy difference, 5 seeds, digits, 40% noise")
def dz_dg40_filter_vs_lr(): return cohens_dz(*_pr("digits", 0.4, "logreg"))

# digits vs mlp
@source("p_dg0_filter_vs_mlp", means="p-value, two-sided paired t-test over 5 seeds, filter vs mlp test accuracy, digits, 0% noise")
def p_dg0_filter_vs_mlp(): return paired_t_p(*_pr("digits", 0.0, "mlp"))
@source("dg0_mlp_diff_ci_low", means="lower end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, digits, 0% noise")
def dg0_mlp_diff_ci_low(): return diff_ci95_low(*_pr("digits", 0.0, "mlp"))
@source("dg0_mlp_diff_ci_high", means="upper end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, digits, 0% noise")
def dg0_mlp_diff_ci_high(): return diff_ci95_high(*_pr("digits", 0.0, "mlp"))
@source("p_dg20_filter_vs_mlp", means="p-value, two-sided paired t-test over 5 seeds, filter vs mlp test accuracy, digits, 20% noise")
def p_dg20_filter_vs_mlp(): return paired_t_p(*_pr("digits", 0.2, "mlp"))
@source("dg20_mlp_diff_ci_low", means="lower end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, digits, 20% noise")
def dg20_mlp_diff_ci_low(): return diff_ci95_low(*_pr("digits", 0.2, "mlp"))
@source("dg20_mlp_diff_ci_high", means="upper end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, digits, 20% noise")
def dg20_mlp_diff_ci_high(): return diff_ci95_high(*_pr("digits", 0.2, "mlp"))
@source("dz_dg20_filter_vs_mlp", means="Cohen's dz of paired filter minus mlp accuracy difference, 5 seeds, digits, 20% noise")
def dz_dg20_filter_vs_mlp(): return cohens_dz(*_pr("digits", 0.2, "mlp"))
@source("p_dg40_filter_vs_mlp", means="p-value, two-sided paired t-test over 5 seeds, filter vs mlp test accuracy, digits, 40% noise")
def p_dg40_filter_vs_mlp(): return paired_t_p(*_pr("digits", 0.4, "mlp"))
@source("dg40_mlp_diff_ci_low", means="lower end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, digits, 40% noise")
def dg40_mlp_diff_ci_low(): return diff_ci95_low(*_pr("digits", 0.4, "mlp"))
@source("dg40_mlp_diff_ci_high", means="upper end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, digits, 40% noise")
def dg40_mlp_diff_ci_high(): return diff_ci95_high(*_pr("digits", 0.4, "mlp"))
@source("dz_dg40_filter_vs_mlp", means="Cohen's dz of paired filter minus mlp accuracy difference, 5 seeds, digits, 40% noise")
def dz_dg40_filter_vs_mlp(): return cohens_dz(*_pr("digits", 0.4, "mlp"))

# breast_cancer vs logreg
@source("p_bc0_filter_vs_lr", means="p-value, two-sided paired t-test over 5 seeds, filter vs logreg test accuracy, breast_cancer, 0% noise")
def p_bc0_filter_vs_lr(): return paired_t_p(*_pr("breast_cancer", 0.0, "logreg"))
@source("bc0_lr_diff_ci_low", means="lower end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, breast_cancer, 0% noise")
def bc0_lr_diff_ci_low(): return diff_ci95_low(*_pr("breast_cancer", 0.0, "logreg"))
@source("bc0_lr_diff_ci_high", means="upper end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, breast_cancer, 0% noise")
def bc0_lr_diff_ci_high(): return diff_ci95_high(*_pr("breast_cancer", 0.0, "logreg"))
@source("p_bc20_filter_vs_lr", means="p-value, two-sided paired t-test over 5 seeds, filter vs logreg test accuracy, breast_cancer, 20% noise")
def p_bc20_filter_vs_lr(): return paired_t_p(*_pr("breast_cancer", 0.2, "logreg"))
@source("bc20_lr_diff_ci_low", means="lower end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, breast_cancer, 20% noise")
def bc20_lr_diff_ci_low(): return diff_ci95_low(*_pr("breast_cancer", 0.2, "logreg"))
@source("bc20_lr_diff_ci_high", means="upper end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, breast_cancer, 20% noise")
def bc20_lr_diff_ci_high(): return diff_ci95_high(*_pr("breast_cancer", 0.2, "logreg"))
@source("dz_bc20_filter_vs_lr", means="Cohen's dz of paired filter minus logreg accuracy difference, 5 seeds, breast_cancer, 20% noise")
def dz_bc20_filter_vs_lr(): return cohens_dz(*_pr("breast_cancer", 0.2, "logreg"))
@source("p_bc40_filter_vs_lr", means="p-value, two-sided paired t-test over 5 seeds, filter vs logreg test accuracy, breast_cancer, 40% noise")
def p_bc40_filter_vs_lr(): return paired_t_p(*_pr("breast_cancer", 0.4, "logreg"))
@source("bc40_lr_diff_ci_low", means="lower end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, breast_cancer, 40% noise")
def bc40_lr_diff_ci_low(): return diff_ci95_low(*_pr("breast_cancer", 0.4, "logreg"))
@source("bc40_lr_diff_ci_high", means="upper end of 95% CI (points) of paired filter minus logreg accuracy difference, 5 seeds, breast_cancer, 40% noise")
def bc40_lr_diff_ci_high(): return diff_ci95_high(*_pr("breast_cancer", 0.4, "logreg"))
@source("dz_bc40_filter_vs_lr", means="Cohen's dz of paired filter minus logreg accuracy difference, 5 seeds, breast_cancer, 40% noise")
def dz_bc40_filter_vs_lr(): return cohens_dz(*_pr("breast_cancer", 0.4, "logreg"))

# breast_cancer vs mlp
@source("p_bc0_filter_vs_mlp", means="p-value, two-sided paired t-test over 5 seeds, filter vs mlp test accuracy, breast_cancer, 0% noise")
def p_bc0_filter_vs_mlp(): return paired_t_p(*_pr("breast_cancer", 0.0, "mlp"))
@source("bc0_mlp_diff_ci_low", means="lower end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, breast_cancer, 0% noise")
def bc0_mlp_diff_ci_low(): return diff_ci95_low(*_pr("breast_cancer", 0.0, "mlp"))
@source("bc0_mlp_diff_ci_high", means="upper end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, breast_cancer, 0% noise")
def bc0_mlp_diff_ci_high(): return diff_ci95_high(*_pr("breast_cancer", 0.0, "mlp"))
@source("p_bc20_filter_vs_mlp", means="p-value, two-sided paired t-test over 5 seeds, filter vs mlp test accuracy, breast_cancer, 20% noise")
def p_bc20_filter_vs_mlp(): return paired_t_p(*_pr("breast_cancer", 0.2, "mlp"))
@source("bc20_mlp_diff_ci_low", means="lower end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, breast_cancer, 20% noise")
def bc20_mlp_diff_ci_low(): return diff_ci95_low(*_pr("breast_cancer", 0.2, "mlp"))
@source("bc20_mlp_diff_ci_high", means="upper end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, breast_cancer, 20% noise")
def bc20_mlp_diff_ci_high(): return diff_ci95_high(*_pr("breast_cancer", 0.2, "mlp"))
@source("dz_bc20_filter_vs_mlp", means="Cohen's dz of paired filter minus mlp accuracy difference, 5 seeds, breast_cancer, 20% noise")
def dz_bc20_filter_vs_mlp(): return cohens_dz(*_pr("breast_cancer", 0.2, "mlp"))
@source("p_bc40_filter_vs_mlp", means="p-value, two-sided paired t-test over 5 seeds, filter vs mlp test accuracy, breast_cancer, 40% noise")
def p_bc40_filter_vs_mlp(): return paired_t_p(*_pr("breast_cancer", 0.4, "mlp"))
@source("bc40_mlp_diff_ci_low", means="lower end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, breast_cancer, 40% noise")
def bc40_mlp_diff_ci_low(): return diff_ci95_low(*_pr("breast_cancer", 0.4, "mlp"))
@source("bc40_mlp_diff_ci_high", means="upper end of 95% CI (points) of paired filter minus mlp accuracy difference, 5 seeds, breast_cancer, 40% noise")
def bc40_mlp_diff_ci_high(): return diff_ci95_high(*_pr("breast_cancer", 0.4, "mlp"))
@source("dz_bc40_filter_vs_mlp", means="Cohen's dz of paired filter minus mlp accuracy difference, 5 seeds, breast_cancer, 40% noise")
def dz_bc40_filter_vs_mlp(): return cohens_dz(*_pr("breast_cancer", 0.4, "mlp"))


# ---- trends: does the filter's gain grow with noise? paired comparison of the two ends (40% vs 20%) ------
@source("p_trend_dg_gain_lr", means="p-value, two-sided paired t-test over 5 seeds, per-seed filter-minus-logreg gain at 40% vs 20% noise, digits")
def p_trend_dg_gain_lr(): return paired_t_p(_diff("digits", 0.4, "filter", "logreg"), _diff("digits", 0.2, "filter", "logreg"))
@source("trend_dg_gain_lr_ci_low", means="lower end of 95% CI (points) of per-seed filter-minus-logreg gain, 40% minus 20% noise, digits, 5 seeds")
def trend_dg_gain_lr_ci_low(): return diff_ci95_low(_diff("digits", 0.4, "filter", "logreg"), _diff("digits", 0.2, "filter", "logreg"))
@source("trend_dg_gain_lr_ci_high", means="upper end of 95% CI (points) of per-seed filter-minus-logreg gain, 40% minus 20% noise, digits, 5 seeds")
def trend_dg_gain_lr_ci_high(): return diff_ci95_high(_diff("digits", 0.4, "filter", "logreg"), _diff("digits", 0.2, "filter", "logreg"))
@source("p_trend_bc_gain_lr", means="p-value, two-sided paired t-test over 5 seeds, per-seed filter-minus-logreg gain at 40% vs 20% noise, breast_cancer")
def p_trend_bc_gain_lr(): return paired_t_p(_diff("breast_cancer", 0.4, "filter", "logreg"), _diff("breast_cancer", 0.2, "filter", "logreg"))
@source("trend_bc_gain_lr_ci_low", means="lower end of 95% CI (points) of per-seed filter-minus-logreg gain, 40% minus 20% noise, breast_cancer, 5 seeds")
def trend_bc_gain_lr_ci_low(): return diff_ci95_low(_diff("breast_cancer", 0.4, "filter", "logreg"), _diff("breast_cancer", 0.2, "filter", "logreg"))
@source("trend_bc_gain_lr_ci_high", means="upper end of 95% CI (points) of per-seed filter-minus-logreg gain, 40% minus 20% noise, breast_cancer, 5 seeds")
def trend_bc_gain_lr_ci_high(): return diff_ci95_high(_diff("breast_cancer", 0.4, "filter", "logreg"), _diff("breast_cancer", 0.2, "filter", "logreg"))
@source("p_trend_dg_gain_mlp", means="p-value, two-sided paired t-test over 5 seeds, per-seed filter-minus-mlp gain at 40% vs 20% noise, digits")
def p_trend_dg_gain_mlp(): return paired_t_p(_diff("digits", 0.4, "filter", "mlp"), _diff("digits", 0.2, "filter", "mlp"))
@source("p_trend_bc_gain_mlp", means="p-value, two-sided paired t-test over 5 seeds, per-seed filter-minus-mlp gain at 40% vs 20% noise, breast_cancer")
def p_trend_bc_gain_mlp(): return paired_t_p(_diff("breast_cancer", 0.4, "filter", "mlp"), _diff("breast_cancer", 0.2, "filter", "mlp"))


# ---- "most dropped samples are truly mislabeled": per-seed precision against 50% (paired against a constant)
@source("p_prec_dg20_gt50", means="p-value, two-sided one-sample t-test (paired against constant 50) over 5 seeds, filter precision (%), digits, 20% noise")
def p_prec_dg20_gt50(): return paired_t_p(_precisions("digits", 0.2), [50.0] * 5)
@source("p_prec_dg40_gt50", means="p-value, two-sided one-sample t-test (paired against constant 50) over 5 seeds, filter precision (%), digits, 40% noise")
def p_prec_dg40_gt50(): return paired_t_p(_precisions("digits", 0.4), [50.0] * 5)
@source("p_prec_bc20_gt50", means="p-value, two-sided one-sample t-test (paired against constant 50) over 5 seeds, filter precision (%), breast_cancer, 20% noise")
def p_prec_bc20_gt50(): return paired_t_p(_precisions("breast_cancer", 0.2), [50.0] * 5)
@source("p_prec_bc40_gt50", means="p-value, two-sided one-sample t-test (paired against constant 50) over 5 seeds, filter precision (%), breast_cancer, 40% noise")
def p_prec_bc40_gt50(): return paired_t_p(_precisions("breast_cancer", 0.4), [50.0] * 5)


# ---- revision: per-cell flip rate, precision lift, seed counts, test-set resolution -----------------------
def _flip_pct(d, n):
    return _mean([100 * r["n_noisy"] / r["n_train"] for r in _rows(d, n, "filter")])


def _lift(d, n):
    return _mean(_precisions(d, n)) - _flip_pct(d, n)


def _nwin(d, n, base):
    return sum(1 for x in _diff(d, n, "filter", base) if x > 0)


@source("noisy_pct_digits_n20", means="mean realized percent of digits training labels flipped at nominal 20% noise, seeds 0-4")
def noisy_pct_digits_n20(): return _flip_pct("digits", 0.2)
@source("noisy_pct_breast_cancer_n20", means="mean realized percent of breast_cancer training labels flipped at nominal 20% noise, seeds 0-4")
def noisy_pct_breast_cancer_n20(): return _flip_pct("breast_cancer", 0.2)
@source("lift_digits_n20", means="mean filter precision minus mean realized flip rate (percentage points), digits, 20% noise")
def lift_digits_n20(): return _lift("digits", 0.2)
@source("lift_digits_n40", means="mean filter precision minus mean realized flip rate (percentage points), digits, 40% noise")
def lift_digits_n40(): return _lift("digits", 0.4)
@source("lift_breast_cancer_n20", means="mean filter precision minus mean realized flip rate (percentage points), breast_cancer, 20% noise")
def lift_breast_cancer_n20(): return _lift("breast_cancer", 0.2)
@source("lift_breast_cancer_n40", means="mean filter precision minus mean realized flip rate (percentage points), breast_cancer, 40% noise")
def lift_breast_cancer_n40(): return _lift("breast_cancer", 0.4)

@source("nwin_lr_digits_n20", means="number of seeds out of 5 where filter beats logreg, digits, 20% noise")
def nwin_lr_digits_n20(): return _nwin("digits", 0.2, "logreg")
@source("nwin_lr_digits_n40", means="number of seeds out of 5 where filter beats logreg, digits, 40% noise")
def nwin_lr_digits_n40(): return _nwin("digits", 0.4, "logreg")
@source("nwin_lr_breast_cancer_n20", means="number of seeds out of 5 where filter beats logreg, breast_cancer, 20% noise")
def nwin_lr_breast_cancer_n20(): return _nwin("breast_cancer", 0.2, "logreg")
@source("nwin_lr_breast_cancer_n40", means="number of seeds out of 5 where filter beats logreg, breast_cancer, 40% noise")
def nwin_lr_breast_cancer_n40(): return _nwin("breast_cancer", 0.4, "logreg")

@source("one_sample_pts_breast_cancer", means="accuracy points that one test sample is worth on breast_cancer: 100 / n_test")
def one_sample_pts_breast_cancer(): return 100 / _rows("breast_cancer", 0.0, "logreg")[0]["n_test"]
@source("one_sample_pts_digits", means="accuracy points that one test sample is worth on digits: 100 / n_test")
def one_sample_pts_digits(): return 100 / _rows("digits", 0.0, "logreg")[0]["n_test"]
