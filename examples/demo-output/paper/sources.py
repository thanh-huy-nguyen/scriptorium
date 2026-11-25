"""Recipes for the numbers in this paper. Each returns the unrounded value printed next to \\src{key}.

`source` and `load(path)` are provided by the checker; do not import or define them. Paths are relative to the
repository root. Read raw results, configs or scripts, never Markdown notes.

Keys: <quantity>_<method>_<dataset>_<noise>, with dataset `digits` or `breast` (breast_cancer) and noise
`noise0`, `noise20`, `noise40`. Methods: `filter` (ours), `logreg`, `mlp`.
"""

import re
import statistics

from scriptorium_stats import cohens_dz, diff_ci95_high, diff_ci95_low, paired_t_p

RUNS = "results/runs.jsonl"
CONFIG = "experiments/config.json"


# ---------------------------------------------------------------------------
# Helpers. Every per-seed helper returns one value per seed, in seed order, so
# values from two methods on the same (dataset, noise rate) can be paired.
# `dataset` is the raw name ("digits", "breast_cancer"), `noise` is 0.0, 0.2 or 0.4.
# ---------------------------------------------------------------------------

def _runs(dataset, noise, method):
    """Raw records of one method on one (dataset, noise rate), sorted by seed."""
    rows = [r for r in load(RUNS)
            if r["dataset"] == dataset and r["noise"] == noise and r["method"] == method]
    rows.sort(key=lambda r: r["seed"])
    if [r["seed"] for r in rows] != sorted(load(CONFIG)["seeds"]):
        raise ValueError(f"incomplete or duplicated seeds: {dataset} {noise} {method}")
    return rows


def _accs(dataset, noise, method):
    """Test accuracy (%) per seed."""
    return [100 * r["test_acc"] for r in _runs(dataset, noise, method)]


def _diffs(dataset, noise, a, b):
    """Test accuracy of method a minus method b (percentage points), paired per seed."""
    return [x - y for x, y in zip(_accs(dataset, noise, a), _accs(dataset, noise, b))]


def _noise_costs(dataset, noise):
    """Clean-label logreg accuracy minus noisy-label logreg accuracy (points) per seed (same split)."""
    return [c - n for c, n in zip(_accs(dataset, 0.0, "logreg"), _accs(dataset, noise, "logreg"))]


def _recovered(dataset, noise):
    """Per-seed share (%) of the logreg noise cost won back by the filter. Unstable when a seed's cost is small."""
    return [100 * g / c for g, c in zip(_diffs(dataset, noise, "filter", "logreg"), _noise_costs(dataset, noise))]


def _drop_precisions(dataset, noise):
    """Share (%) of dropped training samples whose label had been flipped, per seed."""
    return [100 * r["n_dropped_noisy"] / r["n_dropped"] for r in _runs(dataset, noise, "filter")]


def _drop_recalls(dataset, noise):
    """Share (%) of flipped training labels that the filter dropped, per seed (noise > 0 only)."""
    return [100 * r["n_dropped_noisy"] / r["n_noisy"] for r in _runs(dataset, noise, "filter")]


def _drop_fractions(dataset, noise):
    """Share (%) of the training set that the filter dropped, per seed."""
    return [100 * r["n_dropped"] / r["n_train"] for r in _runs(dataset, noise, "filter")]


def _noisy_cells():
    cfg = load(CONFIG)
    return [(d, n) for d in cfg["datasets"] for n in cfg["noise_rates"] if n > 0]


def _unique(dataset, field):
    values = {r[field] for r in load(RUNS) if r["dataset"] == dataset}
    if len(values) != 1:
        raise ValueError(f"{field} is not constant for {dataset}: {values}")
    return values.pop()


# --- Test accuracy: mean and sample standard deviation over seeds, digits ---

@source("acc_filter_digits_noise0", means="mean test accuracy (%) of out-of-fold filtering + logistic regression (ours) on digits, clean training labels, mean over seeds 0-4")
def acc_filter_digits_noise0():
    return statistics.mean(_accs("digits", 0.0, "filter"))


@source("std_filter_digits_noise0", means="sample standard deviation (points) of test accuracy of ours (filter) on digits, clean training labels, over seeds 0-4")
def std_filter_digits_noise0():
    return statistics.stdev(_accs("digits", 0.0, "filter"))


@source("acc_logreg_digits_noise0", means="mean test accuracy (%) of logistic regression on digits, clean training labels (clean reference), mean over seeds 0-4")
def acc_logreg_digits_noise0():
    return statistics.mean(_accs("digits", 0.0, "logreg"))


@source("std_logreg_digits_noise0", means="sample standard deviation (points) of test accuracy of logistic regression on digits, clean training labels, over seeds 0-4")
def std_logreg_digits_noise0():
    return statistics.stdev(_accs("digits", 0.0, "logreg"))


@source("acc_mlp_digits_noise0", means="mean test accuracy (%) of the MLP on digits, clean training labels, mean over seeds 0-4")
def acc_mlp_digits_noise0():
    return statistics.mean(_accs("digits", 0.0, "mlp"))


@source("std_mlp_digits_noise0", means="sample standard deviation (points) of test accuracy of the MLP on digits, clean training labels, over seeds 0-4")
def std_mlp_digits_noise0():
    return statistics.stdev(_accs("digits", 0.0, "mlp"))


@source("acc_filter_digits_noise20", means="mean test accuracy (%) of ours (filter) on digits, 20% symmetric training-label noise, clean test labels, mean over seeds 0-4")
def acc_filter_digits_noise20():
    return statistics.mean(_accs("digits", 0.2, "filter"))


@source("std_filter_digits_noise20", means="sample standard deviation (points) of test accuracy of ours (filter) on digits, 20% training-label noise, over seeds 0-4")
def std_filter_digits_noise20():
    return statistics.stdev(_accs("digits", 0.2, "filter"))


@source("acc_logreg_digits_noise20", means="mean test accuracy (%) of logistic regression on digits, 20% symmetric training-label noise, clean test labels, mean over seeds 0-4")
def acc_logreg_digits_noise20():
    return statistics.mean(_accs("digits", 0.2, "logreg"))


@source("std_logreg_digits_noise20", means="sample standard deviation (points) of test accuracy of logistic regression on digits, 20% training-label noise, over seeds 0-4")
def std_logreg_digits_noise20():
    return statistics.stdev(_accs("digits", 0.2, "logreg"))


@source("acc_mlp_digits_noise20", means="mean test accuracy (%) of the MLP on digits, 20% symmetric training-label noise, clean test labels, mean over seeds 0-4")
def acc_mlp_digits_noise20():
    return statistics.mean(_accs("digits", 0.2, "mlp"))


@source("std_mlp_digits_noise20", means="sample standard deviation (points) of test accuracy of the MLP on digits, 20% training-label noise, over seeds 0-4")
def std_mlp_digits_noise20():
    return statistics.stdev(_accs("digits", 0.2, "mlp"))


@source("acc_filter_digits_noise40", means="mean test accuracy (%) of ours (filter) on digits, 40% symmetric training-label noise, clean test labels, mean over seeds 0-4")
def acc_filter_digits_noise40():
    return statistics.mean(_accs("digits", 0.4, "filter"))


@source("std_filter_digits_noise40", means="sample standard deviation (points) of test accuracy of ours (filter) on digits, 40% training-label noise, over seeds 0-4")
def std_filter_digits_noise40():
    return statistics.stdev(_accs("digits", 0.4, "filter"))


@source("acc_logreg_digits_noise40", means="mean test accuracy (%) of logistic regression on digits, 40% symmetric training-label noise, clean test labels, mean over seeds 0-4")
def acc_logreg_digits_noise40():
    return statistics.mean(_accs("digits", 0.4, "logreg"))


@source("std_logreg_digits_noise40", means="sample standard deviation (points) of test accuracy of logistic regression on digits, 40% training-label noise, over seeds 0-4")
def std_logreg_digits_noise40():
    return statistics.stdev(_accs("digits", 0.4, "logreg"))


@source("acc_mlp_digits_noise40", means="mean test accuracy (%) of the MLP on digits, 40% symmetric training-label noise, clean test labels, mean over seeds 0-4")
def acc_mlp_digits_noise40():
    return statistics.mean(_accs("digits", 0.4, "mlp"))


@source("std_mlp_digits_noise40", means="sample standard deviation (points) of test accuracy of the MLP on digits, 40% training-label noise, over seeds 0-4")
def std_mlp_digits_noise40():
    return statistics.stdev(_accs("digits", 0.4, "mlp"))


# --- Test accuracy: mean and sample standard deviation over seeds, breast_cancer ---

@source("acc_filter_breast_noise0", means="mean test accuracy (%) of ours (filter) on breast_cancer, clean training labels, mean over seeds 0-4")
def acc_filter_breast_noise0():
    return statistics.mean(_accs("breast_cancer", 0.0, "filter"))


@source("std_filter_breast_noise0", means="sample standard deviation (points) of test accuracy of ours (filter) on breast_cancer, clean training labels, over seeds 0-4")
def std_filter_breast_noise0():
    return statistics.stdev(_accs("breast_cancer", 0.0, "filter"))


@source("acc_logreg_breast_noise0", means="mean test accuracy (%) of logistic regression on breast_cancer, clean training labels (clean reference), mean over seeds 0-4")
def acc_logreg_breast_noise0():
    return statistics.mean(_accs("breast_cancer", 0.0, "logreg"))


@source("std_logreg_breast_noise0", means="sample standard deviation (points) of test accuracy of logistic regression on breast_cancer, clean training labels, over seeds 0-4")
def std_logreg_breast_noise0():
    return statistics.stdev(_accs("breast_cancer", 0.0, "logreg"))


@source("acc_mlp_breast_noise0", means="mean test accuracy (%) of the MLP on breast_cancer, clean training labels, mean over seeds 0-4")
def acc_mlp_breast_noise0():
    return statistics.mean(_accs("breast_cancer", 0.0, "mlp"))


@source("std_mlp_breast_noise0", means="sample standard deviation (points) of test accuracy of the MLP on breast_cancer, clean training labels, over seeds 0-4")
def std_mlp_breast_noise0():
    return statistics.stdev(_accs("breast_cancer", 0.0, "mlp"))


@source("acc_filter_breast_noise20", means="mean test accuracy (%) of ours (filter) on breast_cancer, 20% symmetric training-label noise, clean test labels, mean over seeds 0-4")
def acc_filter_breast_noise20():
    return statistics.mean(_accs("breast_cancer", 0.2, "filter"))


@source("std_filter_breast_noise20", means="sample standard deviation (points) of test accuracy of ours (filter) on breast_cancer, 20% training-label noise, over seeds 0-4")
def std_filter_breast_noise20():
    return statistics.stdev(_accs("breast_cancer", 0.2, "filter"))


@source("acc_logreg_breast_noise20", means="mean test accuracy (%) of logistic regression on breast_cancer, 20% symmetric training-label noise, clean test labels, mean over seeds 0-4")
def acc_logreg_breast_noise20():
    return statistics.mean(_accs("breast_cancer", 0.2, "logreg"))


@source("std_logreg_breast_noise20", means="sample standard deviation (points) of test accuracy of logistic regression on breast_cancer, 20% training-label noise, over seeds 0-4")
def std_logreg_breast_noise20():
    return statistics.stdev(_accs("breast_cancer", 0.2, "logreg"))


@source("acc_mlp_breast_noise20", means="mean test accuracy (%) of the MLP on breast_cancer, 20% symmetric training-label noise, clean test labels, mean over seeds 0-4")
def acc_mlp_breast_noise20():
    return statistics.mean(_accs("breast_cancer", 0.2, "mlp"))


@source("std_mlp_breast_noise20", means="sample standard deviation (points) of test accuracy of the MLP on breast_cancer, 20% training-label noise, over seeds 0-4")
def std_mlp_breast_noise20():
    return statistics.stdev(_accs("breast_cancer", 0.2, "mlp"))


@source("acc_filter_breast_noise40", means="mean test accuracy (%) of ours (filter) on breast_cancer, 40% symmetric training-label noise, clean test labels, mean over seeds 0-4")
def acc_filter_breast_noise40():
    return statistics.mean(_accs("breast_cancer", 0.4, "filter"))


@source("std_filter_breast_noise40", means="sample standard deviation (points) of test accuracy of ours (filter) on breast_cancer, 40% training-label noise, over seeds 0-4")
def std_filter_breast_noise40():
    return statistics.stdev(_accs("breast_cancer", 0.4, "filter"))


@source("acc_logreg_breast_noise40", means="mean test accuracy (%) of logistic regression on breast_cancer, 40% symmetric training-label noise, clean test labels, mean over seeds 0-4")
def acc_logreg_breast_noise40():
    return statistics.mean(_accs("breast_cancer", 0.4, "logreg"))


@source("std_logreg_breast_noise40", means="sample standard deviation (points) of test accuracy of logistic regression on breast_cancer, 40% training-label noise, over seeds 0-4")
def std_logreg_breast_noise40():
    return statistics.stdev(_accs("breast_cancer", 0.4, "logreg"))


@source("acc_mlp_breast_noise40", means="mean test accuracy (%) of the MLP on breast_cancer, 40% symmetric training-label noise, clean test labels, mean over seeds 0-4")
def acc_mlp_breast_noise40():
    return statistics.mean(_accs("breast_cancer", 0.4, "mlp"))


@source("std_mlp_breast_noise40", means="sample standard deviation (points) of test accuracy of the MLP on breast_cancer, 40% training-label noise, over seeds 0-4")
def std_mlp_breast_noise40():
    return statistics.stdev(_accs("breast_cancer", 0.4, "mlp"))


# --- Ours minus logistic regression (same split and noisy labels), signed ---

@source("gain_vs_logreg_digits_noise0", means="ours minus logistic regression test accuracy (points, signed; negative = ours lower) on digits, clean labels, mean of paired differences over seeds 0-4")
def gain_vs_logreg_digits_noise0():
    return statistics.mean(_diffs("digits", 0.0, "filter", "logreg"))


@source("gain_vs_logreg_digits_noise20", means="ours minus logistic regression (best baseline) test accuracy (points, signed) on digits, 20% noise, mean of paired differences over seeds 0-4")
def gain_vs_logreg_digits_noise20():
    return statistics.mean(_diffs("digits", 0.2, "filter", "logreg"))


@source("gain_vs_logreg_digits_noise40", means="ours minus logistic regression (best baseline) test accuracy (points, signed) on digits, 40% noise, mean of paired differences over seeds 0-4")
def gain_vs_logreg_digits_noise40():
    return statistics.mean(_diffs("digits", 0.4, "filter", "logreg"))


@source("gain_vs_logreg_breast_noise0", means="ours minus logistic regression test accuracy (points, signed; negative = ours lower) on breast_cancer, clean labels, mean of paired differences over seeds 0-4")
def gain_vs_logreg_breast_noise0():
    return statistics.mean(_diffs("breast_cancer", 0.0, "filter", "logreg"))


@source("gain_vs_logreg_breast_noise20", means="ours minus logistic regression (best baseline) test accuracy (points, signed) on breast_cancer, 20% noise, mean of paired differences over seeds 0-4")
def gain_vs_logreg_breast_noise20():
    return statistics.mean(_diffs("breast_cancer", 0.2, "filter", "logreg"))


@source("gain_vs_logreg_breast_noise40", means="ours minus logistic regression (best baseline) test accuracy (points, signed) on breast_cancer, 40% noise, mean of paired differences over seeds 0-4")
def gain_vs_logreg_breast_noise40():
    return statistics.mean(_diffs("breast_cancer", 0.4, "filter", "logreg"))


# --- Ours minus the MLP, signed ---

@source("gain_vs_mlp_digits_noise0", means="ours minus MLP (best baseline at this setting) test accuracy (points, signed; negative = ours lower) on digits, clean labels, mean of paired differences over seeds 0-4")
def gain_vs_mlp_digits_noise0():
    return statistics.mean(_diffs("digits", 0.0, "filter", "mlp"))


@source("gain_vs_mlp_digits_noise20", means="ours minus MLP test accuracy (points, signed) on digits, 20% noise, mean of paired differences over seeds 0-4")
def gain_vs_mlp_digits_noise20():
    return statistics.mean(_diffs("digits", 0.2, "filter", "mlp"))


@source("gain_vs_mlp_digits_noise40", means="ours minus MLP test accuracy (points, signed) on digits, 40% noise, mean of paired differences over seeds 0-4")
def gain_vs_mlp_digits_noise40():
    return statistics.mean(_diffs("digits", 0.4, "filter", "mlp"))


@source("gain_vs_mlp_breast_noise0", means="ours minus MLP test accuracy (points, signed) on breast_cancer, clean labels, mean of paired differences over seeds 0-4")
def gain_vs_mlp_breast_noise0():
    return statistics.mean(_diffs("breast_cancer", 0.0, "filter", "mlp"))


@source("gain_vs_mlp_breast_noise20", means="ours minus MLP test accuracy (points, signed) on breast_cancer, 20% noise, mean of paired differences over seeds 0-4")
def gain_vs_mlp_breast_noise20():
    return statistics.mean(_diffs("breast_cancer", 0.2, "filter", "mlp"))


@source("gain_vs_mlp_breast_noise40", means="ours minus MLP test accuracy (points, signed) on breast_cancer, 40% noise, mean of paired differences over seeds 0-4")
def gain_vs_mlp_breast_noise40():
    return statistics.mean(_diffs("breast_cancer", 0.4, "filter", "mlp"))


# --- Cost of label noise to logistic regression, and the share ours wins back ---

@source("noise_cost_digits_noise20", means="test accuracy lost by logistic regression (points) on digits: clean-label mean minus 20%-noise mean, seeds 0-4")
def noise_cost_digits_noise20():
    return statistics.mean(_noise_costs("digits", 0.2))


@source("noise_cost_digits_noise40", means="test accuracy lost by logistic regression (points) on digits: clean-label mean minus 40%-noise mean, seeds 0-4")
def noise_cost_digits_noise40():
    return statistics.mean(_noise_costs("digits", 0.4))


@source("noise_cost_breast_noise20", means="test accuracy lost by logistic regression (points) on breast_cancer: clean-label mean minus 20%-noise mean, seeds 0-4")
def noise_cost_breast_noise20():
    return statistics.mean(_noise_costs("breast_cancer", 0.2))


@source("noise_cost_breast_noise40", means="test accuracy lost by logistic regression (points) on breast_cancer: clean-label mean minus 40%-noise mean, seeds 0-4")
def noise_cost_breast_noise40():
    return statistics.mean(_noise_costs("breast_cancer", 0.4))


@source("recovered_digits_noise20", means="share (%) of logistic-regression accuracy lost to 20% noise that ours wins back on digits: (mean ours - mean noisy logreg) / (mean clean logreg - mean noisy logreg), means over seeds 0-4")
def recovered_digits_noise20():
    return 100 * sum(_diffs("digits", 0.2, "filter", "logreg")) / sum(_noise_costs("digits", 0.2))


@source("recovered_digits_noise40", means="share (%) of logistic-regression accuracy lost to 40% noise that ours wins back on digits: (mean ours - mean noisy logreg) / (mean clean logreg - mean noisy logreg), means over seeds 0-4")
def recovered_digits_noise40():
    return 100 * sum(_diffs("digits", 0.4, "filter", "logreg")) / sum(_noise_costs("digits", 0.4))


@source("recovered_breast_noise20", means="share (%) of logistic-regression accuracy lost to 20% noise that ours wins back on breast_cancer: (mean ours - mean noisy logreg) / (mean clean logreg - mean noisy logreg), means over seeds 0-4")
def recovered_breast_noise20():
    return 100 * sum(_diffs("breast_cancer", 0.2, "filter", "logreg")) / sum(_noise_costs("breast_cancer", 0.2))


@source("recovered_breast_noise40", means="share (%) of logistic-regression accuracy lost to 40% noise that ours wins back on breast_cancer: (mean ours - mean noisy logreg) / (mean clean logreg - mean noisy logreg), means over seeds 0-4")
def recovered_breast_noise40():
    return 100 * sum(_diffs("breast_cancer", 0.4, "filter", "logreg")) / sum(_noise_costs("breast_cancer", 0.4))


# --- What the filter drops ---

@source("drop_precision_digits_noise20", means="share (%) of dropped training samples that were truly mislabeled, digits, 20% noise, mean of per-seed ratios over seeds 0-4")
def drop_precision_digits_noise20():
    return statistics.mean(_drop_precisions("digits", 0.2))


@source("drop_precision_digits_noise40", means="share (%) of dropped training samples that were truly mislabeled, digits, 40% noise, mean of per-seed ratios over seeds 0-4")
def drop_precision_digits_noise40():
    return statistics.mean(_drop_precisions("digits", 0.4))


@source("drop_precision_breast_noise20", means="share (%) of dropped training samples that were truly mislabeled, breast_cancer, 20% noise, mean of per-seed ratios over seeds 0-4")
def drop_precision_breast_noise20():
    return statistics.mean(_drop_precisions("breast_cancer", 0.2))


@source("drop_precision_breast_noise40", means="share (%) of dropped training samples that were truly mislabeled, breast_cancer, 40% noise, mean of per-seed ratios over seeds 0-4")
def drop_precision_breast_noise40():
    return statistics.mean(_drop_precisions("breast_cancer", 0.4))


@source("drop_precision_min", means="lowest per-run share (%) of dropped samples that were truly mislabeled, over all noisy runs (both datasets, 20% and 40% noise, seeds 0-4)")
def drop_precision_min():
    return min(v for d, n in _noisy_cells() for v in _drop_precisions(d, n))


@source("drop_precision_max", means="highest per-run share (%) of dropped samples that were truly mislabeled, over all noisy runs (both datasets, 20% and 40% noise, seeds 0-4)")
def drop_precision_max():
    return max(v for d, n in _noisy_cells() for v in _drop_precisions(d, n))


@source("drop_recall_digits_noise20", means="share (%) of mislabeled training samples that the filter dropped, digits, 20% noise, mean of per-seed ratios over seeds 0-4")
def drop_recall_digits_noise20():
    return statistics.mean(_drop_recalls("digits", 0.2))


@source("drop_recall_digits_noise40", means="share (%) of mislabeled training samples that the filter dropped, digits, 40% noise, mean of per-seed ratios over seeds 0-4")
def drop_recall_digits_noise40():
    return statistics.mean(_drop_recalls("digits", 0.4))


@source("drop_recall_breast_noise20", means="share (%) of mislabeled training samples that the filter dropped, breast_cancer, 20% noise, mean of per-seed ratios over seeds 0-4")
def drop_recall_breast_noise20():
    return statistics.mean(_drop_recalls("breast_cancer", 0.2))


@source("drop_recall_breast_noise40", means="share (%) of mislabeled training samples that the filter dropped, breast_cancer, 40% noise, mean of per-seed ratios over seeds 0-4")
def drop_recall_breast_noise40():
    return statistics.mean(_drop_recalls("breast_cancer", 0.4))


@source("drop_fraction_digits_noise0", means="share (%) of the training set dropped by the filter, digits, clean labels (every drop is a correctly labeled sample), mean over seeds 0-4")
def drop_fraction_digits_noise0():
    return statistics.mean(_drop_fractions("digits", 0.0))


@source("drop_fraction_digits_noise20", means="share (%) of the training set dropped by the filter, digits, 20% noise, mean over seeds 0-4")
def drop_fraction_digits_noise20():
    return statistics.mean(_drop_fractions("digits", 0.2))


@source("drop_fraction_digits_noise40", means="share (%) of the training set dropped by the filter, digits, 40% noise, mean over seeds 0-4")
def drop_fraction_digits_noise40():
    return statistics.mean(_drop_fractions("digits", 0.4))


@source("drop_fraction_breast_noise0", means="share (%) of the training set dropped by the filter, breast_cancer, clean labels (every drop is a correctly labeled sample), mean over seeds 0-4")
def drop_fraction_breast_noise0():
    return statistics.mean(_drop_fractions("breast_cancer", 0.0))


@source("drop_fraction_breast_noise20", means="share (%) of the training set dropped by the filter, breast_cancer, 20% noise, mean over seeds 0-4")
def drop_fraction_breast_noise20():
    return statistics.mean(_drop_fractions("breast_cancer", 0.2))


@source("drop_fraction_breast_noise40", means="share (%) of the training set dropped by the filter, breast_cancer, 40% noise, mean over seeds 0-4")
def drop_fraction_breast_noise40():
    return statistics.mean(_drop_fractions("breast_cancer", 0.4))


# --- Run counts: how often one method is strictly more accurate ---

@source("n_noisy_runs", means="number of noisy (dataset, noise rate, seed) runs per method: 2 datasets x 2 non-zero noise rates x 5 seeds")
def n_noisy_runs():
    return sum(len(_accs(d, n, "filter")) for d, n in _noisy_cells())


@source("wins_vs_logreg_noisy", means="number of noisy runs (both datasets, 20% and 40% noise, seeds 0-4) where ours has strictly higher test accuracy than logistic regression")
def wins_vs_logreg_noisy():
    return sum(x > 0 for d, n in _noisy_cells() for x in _diffs(d, n, "filter", "logreg"))


@source("wins_vs_mlp_noisy", means="number of noisy runs (both datasets, 20% and 40% noise, seeds 0-4) where ours has strictly higher test accuracy than the MLP")
def wins_vs_mlp_noisy():
    return sum(x > 0 for d, n in _noisy_cells() for x in _diffs(d, n, "filter", "mlp"))


@source("wins_logreg_vs_mlp_noisy", means="number of noisy runs (both datasets, 20% and 40% noise, seeds 0-4) where plain logistic regression has strictly higher test accuracy than the MLP")
def wins_logreg_vs_mlp_noisy():
    return sum(x > 0 for d, n in _noisy_cells() for x in _diffs(d, n, "logreg", "mlp"))


# --- Dataset and split sizes ---

@source("n_train_digits", means="number of training samples per split on digits (same for every seed and noise rate)")
def n_train_digits():
    return _unique("digits", "n_train")


@source("n_test_digits", means="number of test samples per split on digits (same for every seed and noise rate)")
def n_test_digits():
    return _unique("digits", "n_test")


@source("n_total_digits", means="total number of samples in digits (training plus test of one split)")
def n_total_digits():
    return _unique("digits", "n_train") + _unique("digits", "n_test")


@source("n_train_breast", means="number of training samples per split on breast_cancer (same for every seed and noise rate)")
def n_train_breast():
    return _unique("breast_cancer", "n_train")


@source("n_test_breast", means="number of test samples per split on breast_cancer (same for every seed and noise rate)")
def n_test_breast():
    return _unique("breast_cancer", "n_test")


@source("n_total_breast", means="total number of samples in breast_cancer (training plus test of one split)")
def n_total_breast():
    return _unique("breast_cancer", "n_train") + _unique("breast_cancer", "n_test")


# --- Experimental settings ---

@source("n_datasets", means="number of datasets")
def n_datasets():
    return len(load(CONFIG)["datasets"])


@source("n_seeds", means="number of seeds per setting (each sets the random split, noise draw, CV folds and MLP initialization)")
def n_seeds():
    return len(load(CONFIG)["seeds"])


@source("noise_rate_clean", means="lowest noise rate (%): clean training labels")
def noise_rate_clean():
    return 100 * load(CONFIG)["noise_rates"][0]


@source("noise_rate_low", means="lower non-zero symmetric training-label noise rate (%), requested flip probability")
def noise_rate_low():
    return 100 * load(CONFIG)["noise_rates"][1]


@source("noise_rate_high", means="higher symmetric training-label noise rate (%), requested flip probability")
def noise_rate_high():
    return 100 * load(CONFIG)["noise_rates"][2]


@source("test_fraction", means="share (%) of each dataset held out as the stratified test set")
def test_fraction():
    return 100 * load(CONFIG)["test_fraction"]


@source("filter_folds", means="number of cross-validation folds K used by the filter")
def filter_folds():
    return load(CONFIG)["filter_folds"]


@source("logreg_c", means="inverse regularization strength C of every logistic regression")
def logreg_c():
    return load(CONFIG)["logreg_C"]


@source("logreg_max_iter", means="maximum solver iterations of every logistic regression (hard-coded in experiments/run.py)")
def logreg_max_iter():
    return int(re.search(r"LogisticRegression\([^\n]*max_iter=(\d+)", load("experiments/run.py")).group(1))


@source("mlp_hidden", means="number of units in the single hidden layer of the MLP")
def mlp_hidden():
    return load(CONFIG)["mlp_hidden"]


@source("mlp_max_iter", means="maximum training iterations of the MLP")
def mlp_max_iter():
    return load(CONFIG)["mlp_max_iter"]


# ---------------------------------------------------------------------------
# Statistical tests. Every comparison pairs the same seeds in seed order (same
# split; at one noise rate also the same noisy labels). Every difference is
# "first minus second" in the order the description names them.
# Keys: p_<comparison>_<dataset>_<noise>, with ci95lo_, ci95hi_ and dz_ on the
# same stem where defined. .scriptorium/stats.json lists each comparison.
# p-values come from a paired t-test. The intervals (diff_ci95_*) resample the
# per-seed differences, so with 5 seeds they are narrower than a t interval and
# can exclude zero when p >= 0.05. Verdicts follow the p-value.
# ---------------------------------------------------------------------------

def _halfway(dataset, noise):
    """Per-seed accuracy (%) at which half of logreg's noise cost is won back: midpoint of clean and noisy logreg."""
    return [(c + x) / 2 for c, x in zip(_accs(dataset, 0.0, "logreg"), _accs(dataset, noise, "logreg"))]


def _method_costs(dataset, noise, method):
    """Clean-label accuracy minus noisy-label accuracy (points) of one method, per seed (same split)."""
    return [c - x for c, x in zip(_accs(dataset, 0.0, method), _accs(dataset, noise, method))]


def _against_half(values):
    """Pair per-seed shares (%) with a constant one half, for a one-sample test of 'most'."""
    return values, [50.0] * len(values)


def _pair(dataset, noise, a, b):
    """Per-seed test accuracy (%) of methods a and b on one (dataset, noise rate)."""
    return _accs(dataset, noise, a), _accs(dataset, noise, b)


def _gain_trend(dataset, other, high, low):
    """Per-seed gain of ours over `other` at the higher and at the lower noise rate."""
    return _diffs(dataset, high, "filter", other), _diffs(dataset, low, "filter", other)


# --- Headline 1: ours vs logistic regression on noisy labels ---

@source("p_filter_vs_logreg_digits_noise20", means="p-value, two-sided paired t-test over 5 seeds, ours (filter) vs logistic regression test accuracy, digits, 20% symmetric training-label noise")
def p_filter_vs_logreg_digits_noise20():
    return paired_t_p(*_pair("digits", 0.2, "filter", "logreg"))


@source("ci95lo_filter_vs_logreg_digits_noise20", means="lower end of the 95% bootstrap interval of ours (filter) minus logistic regression test accuracy (points), paired over 5 seeds, digits, 20% noise")
def ci95lo_filter_vs_logreg_digits_noise20():
    return diff_ci95_low(*_pair("digits", 0.2, "filter", "logreg"))


@source("ci95hi_filter_vs_logreg_digits_noise20", means="upper end of the 95% bootstrap interval of ours (filter) minus logistic regression test accuracy (points), paired over 5 seeds, digits, 20% noise")
def ci95hi_filter_vs_logreg_digits_noise20():
    return diff_ci95_high(*_pair("digits", 0.2, "filter", "logreg"))


@source("dz_filter_vs_logreg_digits_noise20", means="Cohen's dz of ours (filter) minus logistic regression test accuracy, paired over 5 seeds, digits, 20% noise")
def dz_filter_vs_logreg_digits_noise20():
    return cohens_dz(*_pair("digits", 0.2, "filter", "logreg"))


@source("p_filter_vs_logreg_digits_noise40", means="p-value, two-sided paired t-test over 5 seeds, ours (filter) vs logistic regression test accuracy, digits, 40% symmetric training-label noise")
def p_filter_vs_logreg_digits_noise40():
    return paired_t_p(*_pair("digits", 0.4, "filter", "logreg"))


@source("ci95lo_filter_vs_logreg_digits_noise40", means="lower end of the 95% bootstrap interval of ours (filter) minus logistic regression test accuracy (points), paired over 5 seeds, digits, 40% noise")
def ci95lo_filter_vs_logreg_digits_noise40():
    return diff_ci95_low(*_pair("digits", 0.4, "filter", "logreg"))


@source("ci95hi_filter_vs_logreg_digits_noise40", means="upper end of the 95% bootstrap interval of ours (filter) minus logistic regression test accuracy (points), paired over 5 seeds, digits, 40% noise")
def ci95hi_filter_vs_logreg_digits_noise40():
    return diff_ci95_high(*_pair("digits", 0.4, "filter", "logreg"))


@source("dz_filter_vs_logreg_digits_noise40", means="Cohen's dz of ours (filter) minus logistic regression test accuracy, paired over 5 seeds, digits, 40% noise")
def dz_filter_vs_logreg_digits_noise40():
    return cohens_dz(*_pair("digits", 0.4, "filter", "logreg"))


@source("p_filter_vs_logreg_breast_noise20", means="p-value, two-sided paired t-test over 5 seeds, ours (filter) vs logistic regression test accuracy, breast_cancer, 20% symmetric training-label noise")
def p_filter_vs_logreg_breast_noise20():
    return paired_t_p(*_pair("breast_cancer", 0.2, "filter", "logreg"))


@source("ci95lo_filter_vs_logreg_breast_noise20", means="lower end of the 95% bootstrap interval of ours (filter) minus logistic regression test accuracy (points), paired over 5 seeds, breast_cancer, 20% noise")
def ci95lo_filter_vs_logreg_breast_noise20():
    return diff_ci95_low(*_pair("breast_cancer", 0.2, "filter", "logreg"))


@source("ci95hi_filter_vs_logreg_breast_noise20", means="upper end of the 95% bootstrap interval of ours (filter) minus logistic regression test accuracy (points), paired over 5 seeds, breast_cancer, 20% noise")
def ci95hi_filter_vs_logreg_breast_noise20():
    return diff_ci95_high(*_pair("breast_cancer", 0.2, "filter", "logreg"))


@source("dz_filter_vs_logreg_breast_noise20", means="Cohen's dz of ours (filter) minus logistic regression test accuracy, paired over 5 seeds, breast_cancer, 20% noise")
def dz_filter_vs_logreg_breast_noise20():
    return cohens_dz(*_pair("breast_cancer", 0.2, "filter", "logreg"))


@source("p_filter_vs_logreg_breast_noise40", means="p-value, two-sided paired t-test over 5 seeds, ours (filter) vs logistic regression test accuracy, breast_cancer, 40% symmetric training-label noise")
def p_filter_vs_logreg_breast_noise40():
    return paired_t_p(*_pair("breast_cancer", 0.4, "filter", "logreg"))


@source("ci95lo_filter_vs_logreg_breast_noise40", means="lower end of the 95% bootstrap interval of ours (filter) minus logistic regression test accuracy (points), paired over 5 seeds, breast_cancer, 40% noise")
def ci95lo_filter_vs_logreg_breast_noise40():
    return diff_ci95_low(*_pair("breast_cancer", 0.4, "filter", "logreg"))


@source("ci95hi_filter_vs_logreg_breast_noise40", means="upper end of the 95% bootstrap interval of ours (filter) minus logistic regression test accuracy (points), paired over 5 seeds, breast_cancer, 40% noise")
def ci95hi_filter_vs_logreg_breast_noise40():
    return diff_ci95_high(*_pair("breast_cancer", 0.4, "filter", "logreg"))


@source("dz_filter_vs_logreg_breast_noise40", means="Cohen's dz of ours (filter) minus logistic regression test accuracy, paired over 5 seeds, breast_cancer, 40% noise")
def dz_filter_vs_logreg_breast_noise40():
    return cohens_dz(*_pair("breast_cancer", 0.4, "filter", "logreg"))


# --- Headline 2: ours vs the MLP on noisy labels ---

@source("p_filter_vs_mlp_digits_noise20", means="p-value, two-sided paired t-test over 5 seeds, ours (filter) vs MLP test accuracy, digits, 20% symmetric training-label noise")
def p_filter_vs_mlp_digits_noise20():
    return paired_t_p(*_pair("digits", 0.2, "filter", "mlp"))


@source("ci95lo_filter_vs_mlp_digits_noise20", means="lower end of the 95% bootstrap interval of ours (filter) minus MLP test accuracy (points), paired over 5 seeds, digits, 20% noise")
def ci95lo_filter_vs_mlp_digits_noise20():
    return diff_ci95_low(*_pair("digits", 0.2, "filter", "mlp"))


@source("ci95hi_filter_vs_mlp_digits_noise20", means="upper end of the 95% bootstrap interval of ours (filter) minus MLP test accuracy (points), paired over 5 seeds, digits, 20% noise")
def ci95hi_filter_vs_mlp_digits_noise20():
    return diff_ci95_high(*_pair("digits", 0.2, "filter", "mlp"))


@source("p_filter_vs_mlp_digits_noise40", means="p-value, two-sided paired t-test over 5 seeds, ours (filter) vs MLP test accuracy, digits, 40% symmetric training-label noise")
def p_filter_vs_mlp_digits_noise40():
    return paired_t_p(*_pair("digits", 0.4, "filter", "mlp"))


@source("ci95lo_filter_vs_mlp_digits_noise40", means="lower end of the 95% bootstrap interval of ours (filter) minus MLP test accuracy (points), paired over 5 seeds, digits, 40% noise")
def ci95lo_filter_vs_mlp_digits_noise40():
    return diff_ci95_low(*_pair("digits", 0.4, "filter", "mlp"))


@source("ci95hi_filter_vs_mlp_digits_noise40", means="upper end of the 95% bootstrap interval of ours (filter) minus MLP test accuracy (points), paired over 5 seeds, digits, 40% noise")
def ci95hi_filter_vs_mlp_digits_noise40():
    return diff_ci95_high(*_pair("digits", 0.4, "filter", "mlp"))


@source("p_filter_vs_mlp_breast_noise20", means="p-value, two-sided paired t-test over 5 seeds, ours (filter) vs MLP test accuracy, breast_cancer, 20% symmetric training-label noise")
def p_filter_vs_mlp_breast_noise20():
    return paired_t_p(*_pair("breast_cancer", 0.2, "filter", "mlp"))


@source("ci95lo_filter_vs_mlp_breast_noise20", means="lower end of the 95% bootstrap interval of ours (filter) minus MLP test accuracy (points), paired over 5 seeds, breast_cancer, 20% noise")
def ci95lo_filter_vs_mlp_breast_noise20():
    return diff_ci95_low(*_pair("breast_cancer", 0.2, "filter", "mlp"))


@source("ci95hi_filter_vs_mlp_breast_noise20", means="upper end of the 95% bootstrap interval of ours (filter) minus MLP test accuracy (points), paired over 5 seeds, breast_cancer, 20% noise")
def ci95hi_filter_vs_mlp_breast_noise20():
    return diff_ci95_high(*_pair("breast_cancer", 0.2, "filter", "mlp"))


@source("p_filter_vs_mlp_breast_noise40", means="p-value, two-sided paired t-test over 5 seeds, ours (filter) vs MLP test accuracy, breast_cancer, 40% symmetric training-label noise")
def p_filter_vs_mlp_breast_noise40():
    return paired_t_p(*_pair("breast_cancer", 0.4, "filter", "mlp"))


@source("ci95lo_filter_vs_mlp_breast_noise40", means="lower end of the 95% bootstrap interval of ours (filter) minus MLP test accuracy (points), paired over 5 seeds, breast_cancer, 40% noise")
def ci95lo_filter_vs_mlp_breast_noise40():
    return diff_ci95_low(*_pair("breast_cancer", 0.4, "filter", "mlp"))


@source("ci95hi_filter_vs_mlp_breast_noise40", means="upper end of the 95% bootstrap interval of ours (filter) minus MLP test accuracy (points), paired over 5 seeds, breast_cancer, 40% noise")
def ci95hi_filter_vs_mlp_breast_noise40():
    return diff_ci95_high(*_pair("breast_cancer", 0.4, "filter", "mlp"))


# --- Headline 3: the cost on clean labels ---

@source("p_filter_vs_logreg_digits_noise0", means="p-value, two-sided paired t-test over 5 seeds, ours (filter) vs logistic regression test accuracy, digits, clean training labels")
def p_filter_vs_logreg_digits_noise0():
    return paired_t_p(*_pair("digits", 0.0, "filter", "logreg"))


@source("ci95lo_filter_vs_logreg_digits_noise0", means="lower end of the 95% bootstrap interval of ours (filter) minus logistic regression test accuracy (points, negative = ours lower), paired over 5 seeds, digits, clean labels")
def ci95lo_filter_vs_logreg_digits_noise0():
    return diff_ci95_low(*_pair("digits", 0.0, "filter", "logreg"))


@source("ci95hi_filter_vs_logreg_digits_noise0", means="upper end of the 95% bootstrap interval of ours (filter) minus logistic regression test accuracy (points, negative = ours lower), paired over 5 seeds, digits, clean labels")
def ci95hi_filter_vs_logreg_digits_noise0():
    return diff_ci95_high(*_pair("digits", 0.0, "filter", "logreg"))


@source("p_filter_vs_logreg_breast_noise0", means="p-value, two-sided paired t-test over 5 seeds, ours (filter) vs logistic regression test accuracy, breast_cancer, clean training labels")
def p_filter_vs_logreg_breast_noise0():
    return paired_t_p(*_pair("breast_cancer", 0.0, "filter", "logreg"))


@source("ci95lo_filter_vs_logreg_breast_noise0", means="lower end of the 95% bootstrap interval of ours (filter) minus logistic regression test accuracy (points, negative = ours lower), paired over 5 seeds, breast_cancer, clean labels")
def ci95lo_filter_vs_logreg_breast_noise0():
    return diff_ci95_low(*_pair("breast_cancer", 0.0, "filter", "logreg"))


@source("ci95hi_filter_vs_logreg_breast_noise0", means="upper end of the 95% bootstrap interval of ours (filter) minus logistic regression test accuracy (points, negative = ours lower), paired over 5 seeds, breast_cancer, clean labels")
def ci95hi_filter_vs_logreg_breast_noise0():
    return diff_ci95_high(*_pair("breast_cancer", 0.0, "filter", "logreg"))


# --- Headline 4: is more than half of the lost accuracy won back? ---
# Ours minus the midpoint of clean and noisy logreg has the sign of (recovered share - 50%), without per-seed ratios.

@source("p_filter_vs_halfway_digits_noise20", means="p-value, two-sided paired t-test over 5 seeds, ours (filter) vs the half-recovery accuracy (per-seed midpoint of clean-label and noisy-label logistic regression), digits, 20% noise")
def p_filter_vs_halfway_digits_noise20():
    return paired_t_p(_accs("digits", 0.2, "filter"), _halfway("digits", 0.2))


@source("ci95lo_filter_vs_halfway_digits_noise20", means="lower end of the 95% bootstrap interval of ours minus the half-recovery accuracy (points, positive = more than half won back), paired over 5 seeds, digits, 20% noise")
def ci95lo_filter_vs_halfway_digits_noise20():
    return diff_ci95_low(_accs("digits", 0.2, "filter"), _halfway("digits", 0.2))


@source("ci95hi_filter_vs_halfway_digits_noise20", means="upper end of the 95% bootstrap interval of ours minus the half-recovery accuracy (points, positive = more than half won back), paired over 5 seeds, digits, 20% noise")
def ci95hi_filter_vs_halfway_digits_noise20():
    return diff_ci95_high(_accs("digits", 0.2, "filter"), _halfway("digits", 0.2))


@source("p_filter_vs_halfway_digits_noise40", means="p-value, two-sided paired t-test over 5 seeds, ours (filter) vs the half-recovery accuracy (per-seed midpoint of clean-label and noisy-label logistic regression), digits, 40% noise")
def p_filter_vs_halfway_digits_noise40():
    return paired_t_p(_accs("digits", 0.4, "filter"), _halfway("digits", 0.4))


@source("ci95lo_filter_vs_halfway_digits_noise40", means="lower end of the 95% bootstrap interval of ours minus the half-recovery accuracy (points, positive = more than half won back), paired over 5 seeds, digits, 40% noise")
def ci95lo_filter_vs_halfway_digits_noise40():
    return diff_ci95_low(_accs("digits", 0.4, "filter"), _halfway("digits", 0.4))


@source("ci95hi_filter_vs_halfway_digits_noise40", means="upper end of the 95% bootstrap interval of ours minus the half-recovery accuracy (points, positive = more than half won back), paired over 5 seeds, digits, 40% noise")
def ci95hi_filter_vs_halfway_digits_noise40():
    return diff_ci95_high(_accs("digits", 0.4, "filter"), _halfway("digits", 0.4))


@source("p_filter_vs_halfway_breast_noise20", means="p-value, two-sided paired t-test over 5 seeds, ours (filter) vs the half-recovery accuracy (per-seed midpoint of clean-label and noisy-label logistic regression), breast_cancer, 20% noise")
def p_filter_vs_halfway_breast_noise20():
    return paired_t_p(_accs("breast_cancer", 0.2, "filter"), _halfway("breast_cancer", 0.2))


@source("ci95lo_filter_vs_halfway_breast_noise20", means="lower end of the 95% bootstrap interval of ours minus the half-recovery accuracy (points, positive = more than half won back), paired over 5 seeds, breast_cancer, 20% noise")
def ci95lo_filter_vs_halfway_breast_noise20():
    return diff_ci95_low(_accs("breast_cancer", 0.2, "filter"), _halfway("breast_cancer", 0.2))


@source("ci95hi_filter_vs_halfway_breast_noise20", means="upper end of the 95% bootstrap interval of ours minus the half-recovery accuracy (points, positive = more than half won back), paired over 5 seeds, breast_cancer, 20% noise")
def ci95hi_filter_vs_halfway_breast_noise20():
    return diff_ci95_high(_accs("breast_cancer", 0.2, "filter"), _halfway("breast_cancer", 0.2))


@source("p_filter_vs_halfway_breast_noise40", means="p-value, two-sided paired t-test over 5 seeds, ours (filter) vs the half-recovery accuracy (per-seed midpoint of clean-label and noisy-label logistic regression), breast_cancer, 40% noise")
def p_filter_vs_halfway_breast_noise40():
    return paired_t_p(_accs("breast_cancer", 0.4, "filter"), _halfway("breast_cancer", 0.4))


@source("ci95lo_filter_vs_halfway_breast_noise40", means="lower end of the 95% bootstrap interval of ours minus the half-recovery accuracy (points, positive = more than half won back), paired over 5 seeds, breast_cancer, 40% noise")
def ci95lo_filter_vs_halfway_breast_noise40():
    return diff_ci95_low(_accs("breast_cancer", 0.4, "filter"), _halfway("breast_cancer", 0.4))


@source("ci95hi_filter_vs_halfway_breast_noise40", means="upper end of the 95% bootstrap interval of ours minus the half-recovery accuracy (points, positive = more than half won back), paired over 5 seeds, breast_cancer, 40% noise")
def ci95hi_filter_vs_halfway_breast_noise40():
    return diff_ci95_high(_accs("breast_cancer", 0.4, "filter"), _halfway("breast_cancer", 0.4))


# --- Headline 5: are most dropped samples truly mislabeled? ---

@source("p_drop_precision_vs_half_digits_noise20", means="p-value, two-sided one-sample t-test over 5 seeds, share of dropped samples truly mislabeled vs 50%, digits, 20% noise")
def p_drop_precision_vs_half_digits_noise20():
    return paired_t_p(*_against_half(_drop_precisions("digits", 0.2)))


@source("ci95lo_drop_precision_vs_half_digits_noise20", means="lower end of the 95% bootstrap interval of (share of dropped samples truly mislabeled minus 50%), in points, over 5 seeds, digits, 20% noise")
def ci95lo_drop_precision_vs_half_digits_noise20():
    return diff_ci95_low(*_against_half(_drop_precisions("digits", 0.2)))


@source("ci95hi_drop_precision_vs_half_digits_noise20", means="upper end of the 95% bootstrap interval of (share of dropped samples truly mislabeled minus 50%), in points, over 5 seeds, digits, 20% noise")
def ci95hi_drop_precision_vs_half_digits_noise20():
    return diff_ci95_high(*_against_half(_drop_precisions("digits", 0.2)))


@source("p_drop_precision_vs_half_digits_noise40", means="p-value, two-sided one-sample t-test over 5 seeds, share of dropped samples truly mislabeled vs 50%, digits, 40% noise")
def p_drop_precision_vs_half_digits_noise40():
    return paired_t_p(*_against_half(_drop_precisions("digits", 0.4)))


@source("ci95lo_drop_precision_vs_half_digits_noise40", means="lower end of the 95% bootstrap interval of (share of dropped samples truly mislabeled minus 50%), in points, over 5 seeds, digits, 40% noise")
def ci95lo_drop_precision_vs_half_digits_noise40():
    return diff_ci95_low(*_against_half(_drop_precisions("digits", 0.4)))


@source("ci95hi_drop_precision_vs_half_digits_noise40", means="upper end of the 95% bootstrap interval of (share of dropped samples truly mislabeled minus 50%), in points, over 5 seeds, digits, 40% noise")
def ci95hi_drop_precision_vs_half_digits_noise40():
    return diff_ci95_high(*_against_half(_drop_precisions("digits", 0.4)))


@source("p_drop_precision_vs_half_breast_noise20", means="p-value, two-sided one-sample t-test over 5 seeds, share of dropped samples truly mislabeled vs 50%, breast_cancer, 20% noise")
def p_drop_precision_vs_half_breast_noise20():
    return paired_t_p(*_against_half(_drop_precisions("breast_cancer", 0.2)))


@source("ci95lo_drop_precision_vs_half_breast_noise20", means="lower end of the 95% bootstrap interval of (share of dropped samples truly mislabeled minus 50%), in points, over 5 seeds, breast_cancer, 20% noise")
def ci95lo_drop_precision_vs_half_breast_noise20():
    return diff_ci95_low(*_against_half(_drop_precisions("breast_cancer", 0.2)))


@source("ci95hi_drop_precision_vs_half_breast_noise20", means="upper end of the 95% bootstrap interval of (share of dropped samples truly mislabeled minus 50%), in points, over 5 seeds, breast_cancer, 20% noise")
def ci95hi_drop_precision_vs_half_breast_noise20():
    return diff_ci95_high(*_against_half(_drop_precisions("breast_cancer", 0.2)))


@source("p_drop_precision_vs_half_breast_noise40", means="p-value, two-sided one-sample t-test over 5 seeds, share of dropped samples truly mislabeled vs 50%, breast_cancer, 40% noise")
def p_drop_precision_vs_half_breast_noise40():
    return paired_t_p(*_against_half(_drop_precisions("breast_cancer", 0.4)))


@source("ci95lo_drop_precision_vs_half_breast_noise40", means="lower end of the 95% bootstrap interval of (share of dropped samples truly mislabeled minus 50%), in points, over 5 seeds, breast_cancer, 40% noise")
def ci95lo_drop_precision_vs_half_breast_noise40():
    return diff_ci95_low(*_against_half(_drop_precisions("breast_cancer", 0.4)))


@source("ci95hi_drop_precision_vs_half_breast_noise40", means="upper end of the 95% bootstrap interval of (share of dropped samples truly mislabeled minus 50%), in points, over 5 seeds, breast_cancer, 40% noise")
def ci95hi_drop_precision_vs_half_breast_noise40():
    return diff_ci95_high(*_against_half(_drop_precisions("breast_cancer", 0.4)))


# --- Are most mislabeled samples caught? ---

@source("p_drop_recall_vs_half_digits_noise20", means="p-value, two-sided one-sample t-test over 5 seeds, share of mislabeled samples dropped vs 50%, digits, 20% noise")
def p_drop_recall_vs_half_digits_noise20():
    return paired_t_p(*_against_half(_drop_recalls("digits", 0.2)))


@source("p_drop_recall_vs_half_digits_noise40", means="p-value, two-sided one-sample t-test over 5 seeds, share of mislabeled samples dropped vs 50%, digits, 40% noise")
def p_drop_recall_vs_half_digits_noise40():
    return paired_t_p(*_against_half(_drop_recalls("digits", 0.4)))


@source("p_drop_recall_vs_half_breast_noise20", means="p-value, two-sided one-sample t-test over 5 seeds, share of mislabeled samples dropped vs 50%, breast_cancer, 20% noise")
def p_drop_recall_vs_half_breast_noise20():
    return paired_t_p(*_against_half(_drop_recalls("breast_cancer", 0.2)))


@source("p_drop_recall_vs_half_breast_noise40", means="p-value, two-sided one-sample t-test over 5 seeds, share of mislabeled samples dropped vs 50%, breast_cancer, 40% noise")
def p_drop_recall_vs_half_breast_noise40():
    return paired_t_p(*_against_half(_drop_recalls("breast_cancer", 0.4)))


# --- MLP comparisons on clean labels (the higher mean comes first) ---

@source("p_mlp_vs_filter_digits_noise0", means="p-value, two-sided paired t-test over 5 seeds, MLP vs ours (filter) test accuracy, digits, clean training labels")
def p_mlp_vs_filter_digits_noise0():
    return paired_t_p(*_pair("digits", 0.0, "mlp", "filter"))


@source("p_filter_vs_mlp_breast_noise0", means="p-value, two-sided paired t-test over 5 seeds, ours (filter) vs MLP test accuracy, breast_cancer, clean training labels")
def p_filter_vs_mlp_breast_noise0():
    return paired_t_p(*_pair("breast_cancer", 0.0, "filter", "mlp"))


@source("p_mlp_vs_logreg_digits_noise0", means="p-value, two-sided paired t-test over 5 seeds, MLP vs logistic regression test accuracy, digits, clean training labels")
def p_mlp_vs_logreg_digits_noise0():
    return paired_t_p(*_pair("digits", 0.0, "mlp", "logreg"))


@source("p_logreg_vs_mlp_breast_noise0", means="p-value, two-sided paired t-test over 5 seeds, logistic regression vs MLP test accuracy, breast_cancer, clean training labels")
def p_logreg_vs_mlp_breast_noise0():
    return paired_t_p(*_pair("breast_cancer", 0.0, "logreg", "mlp"))


# --- Logistic regression without filtering vs the MLP on noisy labels ---

@source("p_logreg_vs_mlp_digits_noise20", means="p-value, two-sided paired t-test over 5 seeds, logistic regression vs MLP test accuracy, digits, 20% noise")
def p_logreg_vs_mlp_digits_noise20():
    return paired_t_p(*_pair("digits", 0.2, "logreg", "mlp"))


@source("p_logreg_vs_mlp_digits_noise40", means="p-value, two-sided paired t-test over 5 seeds, logistic regression vs MLP test accuracy, digits, 40% noise")
def p_logreg_vs_mlp_digits_noise40():
    return paired_t_p(*_pair("digits", 0.4, "logreg", "mlp"))


@source("p_logreg_vs_mlp_breast_noise20", means="p-value, two-sided paired t-test over 5 seeds, logistic regression vs MLP test accuracy, breast_cancer, 20% noise")
def p_logreg_vs_mlp_breast_noise20():
    return paired_t_p(*_pair("breast_cancer", 0.2, "logreg", "mlp"))


@source("p_logreg_vs_mlp_breast_noise40", means="p-value, two-sided paired t-test over 5 seeds, logistic regression vs MLP test accuracy, breast_cancer, 40% noise")
def p_logreg_vs_mlp_breast_noise40():
    return paired_t_p(*_pair("breast_cancer", 0.4, "logreg", "mlp"))


# --- Cost of noise to logistic regression (clean vs noisy labels, same split) ---

@source("p_noise_cost_logreg_digits_noise20", means="p-value, two-sided paired t-test over 5 seeds, logistic regression with clean vs 20%-noise training labels (same splits), test accuracy, digits")
def p_noise_cost_logreg_digits_noise20():
    return paired_t_p(_accs("digits", 0.0, "logreg"), _accs("digits", 0.2, "logreg"))


@source("p_noise_cost_logreg_digits_noise40", means="p-value, two-sided paired t-test over 5 seeds, logistic regression with clean vs 40%-noise training labels (same splits), test accuracy, digits")
def p_noise_cost_logreg_digits_noise40():
    return paired_t_p(_accs("digits", 0.0, "logreg"), _accs("digits", 0.4, "logreg"))


@source("p_noise_cost_logreg_breast_noise20", means="p-value, two-sided paired t-test over 5 seeds, logistic regression with clean vs 20%-noise training labels (same splits), test accuracy, breast_cancer")
def p_noise_cost_logreg_breast_noise20():
    return paired_t_p(_accs("breast_cancer", 0.0, "logreg"), _accs("breast_cancer", 0.2, "logreg"))


@source("p_noise_cost_logreg_breast_noise40", means="p-value, two-sided paired t-test over 5 seeds, logistic regression with clean vs 40%-noise training labels (same splits), test accuracy, breast_cancer")
def p_noise_cost_logreg_breast_noise40():
    return paired_t_p(_accs("breast_cancer", 0.0, "logreg"), _accs("breast_cancer", 0.4, "logreg"))


# --- Does the MLP lose more to noise than logistic regression? ---

@source("p_noise_cost_mlp_vs_logreg_digits_noise20", means="p-value, two-sided paired t-test over 5 seeds, test accuracy lost to noise by the MLP vs by logistic regression, digits, 20% noise")
def p_noise_cost_mlp_vs_logreg_digits_noise20():
    return paired_t_p(_method_costs("digits", 0.2, "mlp"), _method_costs("digits", 0.2, "logreg"))


@source("p_noise_cost_mlp_vs_logreg_digits_noise40", means="p-value, two-sided paired t-test over 5 seeds, test accuracy lost to noise by the MLP vs by logistic regression, digits, 40% noise")
def p_noise_cost_mlp_vs_logreg_digits_noise40():
    return paired_t_p(_method_costs("digits", 0.4, "mlp"), _method_costs("digits", 0.4, "logreg"))


@source("p_noise_cost_mlp_vs_logreg_breast_noise20", means="p-value, two-sided paired t-test over 5 seeds, test accuracy lost to noise by the MLP vs by logistic regression, breast_cancer, 20% noise")
def p_noise_cost_mlp_vs_logreg_breast_noise20():
    return paired_t_p(_method_costs("breast_cancer", 0.2, "mlp"), _method_costs("breast_cancer", 0.2, "logreg"))


@source("p_noise_cost_mlp_vs_logreg_breast_noise40", means="p-value, two-sided paired t-test over 5 seeds, test accuracy lost to noise by the MLP vs by logistic regression, breast_cancer, 40% noise")
def p_noise_cost_mlp_vs_logreg_breast_noise40():
    return paired_t_p(_method_costs("breast_cancer", 0.4, "mlp"), _method_costs("breast_cancer", 0.4, "logreg"))


# --- The gap ours leaves to clean-label logistic regression ---

@source("p_clean_logreg_vs_filter_digits_noise20", means="p-value, two-sided paired t-test over 5 seeds, clean-label logistic regression vs ours (filter) trained at 20% noise, test accuracy, digits")
def p_clean_logreg_vs_filter_digits_noise20():
    return paired_t_p(_accs("digits", 0.0, "logreg"), _accs("digits", 0.2, "filter"))


@source("p_clean_logreg_vs_filter_digits_noise40", means="p-value, two-sided paired t-test over 5 seeds, clean-label logistic regression vs ours (filter) trained at 40% noise, test accuracy, digits")
def p_clean_logreg_vs_filter_digits_noise40():
    return paired_t_p(_accs("digits", 0.0, "logreg"), _accs("digits", 0.4, "filter"))


@source("p_clean_logreg_vs_filter_breast_noise20", means="p-value, two-sided paired t-test over 5 seeds, clean-label logistic regression vs ours (filter) trained at 20% noise, test accuracy, breast_cancer")
def p_clean_logreg_vs_filter_breast_noise20():
    return paired_t_p(_accs("breast_cancer", 0.0, "logreg"), _accs("breast_cancer", 0.2, "filter"))


@source("p_clean_logreg_vs_filter_breast_noise40", means="p-value, two-sided paired t-test over 5 seeds, clean-label logistic regression vs ours (filter) trained at 40% noise, test accuracy, breast_cancer")
def p_clean_logreg_vs_filter_breast_noise40():
    return paired_t_p(_accs("breast_cancer", 0.0, "logreg"), _accs("breast_cancer", 0.4, "filter"))


# --- Trends over the noise rate (paired across rates: a seed keeps its split) ---

@source("p_trend_noise_cost_logreg_digits", means="p-value, two-sided paired t-test over 5 seeds, accuracy lost by logistic regression at 40% vs at 20% noise, digits")
def p_trend_noise_cost_logreg_digits():
    return paired_t_p(_noise_costs("digits", 0.4), _noise_costs("digits", 0.2))


@source("p_trend_noise_cost_logreg_breast", means="p-value, two-sided paired t-test over 5 seeds, accuracy lost by logistic regression at 40% vs at 20% noise, breast_cancer")
def p_trend_noise_cost_logreg_breast():
    return paired_t_p(_noise_costs("breast_cancer", 0.4), _noise_costs("breast_cancer", 0.2))


@source("p_trend_gain_vs_logreg_digits_noise40_vs_noise0", means="p-value, two-sided paired t-test over 5 seeds, gain of ours over logistic regression at 40% noise vs with clean labels, digits")
def p_trend_gain_vs_logreg_digits_noise40_vs_noise0():
    return paired_t_p(*_gain_trend("digits", "logreg", 0.4, 0.0))


@source("p_trend_gain_vs_logreg_digits_noise40_vs_noise20", means="p-value, two-sided paired t-test over 5 seeds, gain of ours over logistic regression at 40% vs at 20% noise, digits")
def p_trend_gain_vs_logreg_digits_noise40_vs_noise20():
    return paired_t_p(*_gain_trend("digits", "logreg", 0.4, 0.2))


@source("p_trend_gain_vs_logreg_breast_noise40_vs_noise0", means="p-value, two-sided paired t-test over 5 seeds, gain of ours over logistic regression at 40% noise vs with clean labels, breast_cancer")
def p_trend_gain_vs_logreg_breast_noise40_vs_noise0():
    return paired_t_p(*_gain_trend("breast_cancer", "logreg", 0.4, 0.0))


@source("p_trend_gain_vs_logreg_breast_noise40_vs_noise20", means="p-value, two-sided paired t-test over 5 seeds, gain of ours over logistic regression at 40% vs at 20% noise, breast_cancer")
def p_trend_gain_vs_logreg_breast_noise40_vs_noise20():
    return paired_t_p(*_gain_trend("breast_cancer", "logreg", 0.4, 0.2))


@source("p_trend_gain_vs_mlp_digits_noise40_vs_noise0", means="p-value, two-sided paired t-test over 5 seeds, gain of ours over the MLP at 40% noise vs with clean labels, digits")
def p_trend_gain_vs_mlp_digits_noise40_vs_noise0():
    return paired_t_p(*_gain_trend("digits", "mlp", 0.4, 0.0))


@source("p_trend_gain_vs_mlp_digits_noise40_vs_noise20", means="p-value, two-sided paired t-test over 5 seeds, gain of ours over the MLP at 40% vs at 20% noise, digits")
def p_trend_gain_vs_mlp_digits_noise40_vs_noise20():
    return paired_t_p(*_gain_trend("digits", "mlp", 0.4, 0.2))


@source("p_trend_gain_vs_mlp_breast_noise40_vs_noise0", means="p-value, two-sided paired t-test over 5 seeds, gain of ours over the MLP at 40% noise vs with clean labels, breast_cancer")
def p_trend_gain_vs_mlp_breast_noise40_vs_noise0():
    return paired_t_p(*_gain_trend("breast_cancer", "mlp", 0.4, 0.0))


@source("p_trend_gain_vs_mlp_breast_noise40_vs_noise20", means="p-value, two-sided paired t-test over 5 seeds, gain of ours over the MLP at 40% vs at 20% noise, breast_cancer")
def p_trend_gain_vs_mlp_breast_noise40_vs_noise20():
    return paired_t_p(*_gain_trend("breast_cancer", "mlp", 0.4, 0.2))


@source("p_trend_recovered_digits", means="p-value, two-sided paired t-test over 5 seeds, per-seed share of the logistic-regression noise cost won back at 20% vs at 40% noise (per-seed ratios, not the ratio of means), digits")
def p_trend_recovered_digits():
    return paired_t_p(_recovered("digits", 0.2), _recovered("digits", 0.4))


@source("p_trend_recovered_breast", means="p-value, two-sided paired t-test over 5 seeds, per-seed share of the logistic-regression noise cost won back at 20% vs at 40% noise (per-seed ratios, not the ratio of means), breast_cancer")
def p_trend_recovered_breast():
    return paired_t_p(_recovered("breast_cancer", 0.2), _recovered("breast_cancer", 0.4))


@source("p_trend_drop_precision_digits", means="p-value, two-sided paired t-test over 5 seeds, share of dropped samples truly mislabeled at 40% vs at 20% noise, digits")
def p_trend_drop_precision_digits():
    return paired_t_p(_drop_precisions("digits", 0.4), _drop_precisions("digits", 0.2))


@source("p_trend_drop_precision_breast", means="p-value, two-sided paired t-test over 5 seeds, share of dropped samples truly mislabeled at 20% vs at 40% noise, breast_cancer")
def p_trend_drop_precision_breast():
    return paired_t_p(_drop_precisions("breast_cancer", 0.2), _drop_precisions("breast_cancer", 0.4))


@source("p_trend_drop_recall_digits", means="p-value, two-sided paired t-test over 5 seeds, share of mislabeled samples dropped at 20% vs at 40% noise, digits")
def p_trend_drop_recall_digits():
    return paired_t_p(_drop_recalls("digits", 0.2), _drop_recalls("digits", 0.4))


@source("p_trend_drop_recall_breast", means="p-value, two-sided paired t-test over 5 seeds, share of mislabeled samples dropped at 20% vs at 40% noise, breast_cancer")
def p_trend_drop_recall_breast():
    return paired_t_p(_drop_recalls("breast_cancer", 0.2), _drop_recalls("breast_cancer", 0.4))


@source("p_trend_drop_fraction_digits", means="p-value, two-sided paired t-test over 5 seeds, share of the training set dropped at 40% noise vs with clean labels, digits")
def p_trend_drop_fraction_digits():
    return paired_t_p(_drop_fractions("digits", 0.4), _drop_fractions("digits", 0.0))


@source("p_trend_drop_fraction_breast", means="p-value, two-sided paired t-test over 5 seeds, share of the training set dropped at 40% noise vs with clean labels, breast_cancer")
def p_trend_drop_fraction_breast():
    return paired_t_p(_drop_fractions("breast_cancer", 0.4), _drop_fractions("breast_cancer", 0.0))


def _noisy_shares(dataset, noise):
    """Per seed, the percentage of all training labels that were flipped. A random set of drops would match it on average."""
    return [100 * r["n_noisy"] / r["n_train"] for r in _runs(dataset, noise, "filter")]


@source("noisy_share_digits_noise20", means="share (%) of all training samples whose label was flipped, digits, 20% noise, mean over seeds 0-4")
def noisy_share_digits_noise20():
    return statistics.mean(_noisy_shares("digits", 0.2))


@source("noisy_share_digits_noise40", means="share (%) of all training samples whose label was flipped, digits, 40% noise, mean over seeds 0-4")
def noisy_share_digits_noise40():
    return statistics.mean(_noisy_shares("digits", 0.4))


@source("noisy_share_breast_noise20", means="share (%) of all training samples whose label was flipped, breast_cancer, 20% noise, mean over seeds 0-4")
def noisy_share_breast_noise20():
    return statistics.mean(_noisy_shares("breast_cancer", 0.2))


@source("noisy_share_breast_noise40", means="share (%) of all training samples whose label was flipped, breast_cancer, 40% noise, mean over seeds 0-4")
def noisy_share_breast_noise40():
    return statistics.mean(_noisy_shares("breast_cancer", 0.4))


@source("p_drop_precision_vs_noisy_share_digits_noise20", means="p-value, two-sided paired t-test over 5 seeds, share of dropped samples truly mislabeled vs share of all training samples mislabeled in the same run, digits, 20% noise")
def p_drop_precision_vs_noisy_share_digits_noise20():
    return paired_t_p(_drop_precisions("digits", 0.2), _noisy_shares("digits", 0.2))


@source("p_drop_precision_vs_noisy_share_digits_noise40", means="p-value, two-sided paired t-test over 5 seeds, share of dropped samples truly mislabeled vs share of all training samples mislabeled in the same run, digits, 40% noise")
def p_drop_precision_vs_noisy_share_digits_noise40():
    return paired_t_p(_drop_precisions("digits", 0.4), _noisy_shares("digits", 0.4))


@source("p_drop_precision_vs_noisy_share_breast_noise20", means="p-value, two-sided paired t-test over 5 seeds, share of dropped samples truly mislabeled vs share of all training samples mislabeled in the same run, breast_cancer, 20% noise")
def p_drop_precision_vs_noisy_share_breast_noise20():
    return paired_t_p(_drop_precisions("breast_cancer", 0.2), _noisy_shares("breast_cancer", 0.2))


@source("p_drop_precision_vs_noisy_share_breast_noise40", means="p-value, two-sided paired t-test over 5 seeds, share of dropped samples truly mislabeled vs share of all training samples mislabeled in the same run, breast_cancer, 40% noise")
def p_drop_precision_vs_noisy_share_breast_noise40():
    return paired_t_p(_drop_precisions("breast_cancer", 0.4), _noisy_shares("breast_cancer", 0.4))


# ---------------------------------------------------------------------------
# Values drawn only in figures: per-seed points, the spread of the paired gain,
# and the split of the removed share into mislabeled and correct samples.
# `_runs` guarantees seeds 0-4 in order, so index k of a per-seed list is seed k.
# ---------------------------------------------------------------------------

def _drop_shares_of_train(dataset, noise, mislabeled):
    """Per seed, dropped samples of one kind (mislabeled or correct) as a percentage of the training set."""
    return [100 * (r["n_dropped_noisy"] if mislabeled else r["n_dropped"] - r["n_dropped_noisy"]) / r["n_train"]
            for r in _runs(dataset, noise, "filter")]


# --- Share of the training set removed, split by kind (noisy settings) ---

@source("drop_share_mislabeled_digits_noise20", means="mislabeled samples dropped by the filter as a share (%) of the training set, digits, 20% noise, mean over seeds 0-4")
def drop_share_mislabeled_digits_noise20():
    return statistics.mean(_drop_shares_of_train("digits", 0.2, True))


@source("drop_share_correct_digits_noise20", means="correctly labeled samples dropped by the filter as a share (%) of the training set, digits, 20% noise, mean over seeds 0-4")
def drop_share_correct_digits_noise20():
    return statistics.mean(_drop_shares_of_train("digits", 0.2, False))


@source("drop_share_mislabeled_digits_noise40", means="mislabeled samples dropped by the filter as a share (%) of the training set, digits, 40% noise, mean over seeds 0-4")
def drop_share_mislabeled_digits_noise40():
    return statistics.mean(_drop_shares_of_train("digits", 0.4, True))


@source("drop_share_correct_digits_noise40", means="correctly labeled samples dropped by the filter as a share (%) of the training set, digits, 40% noise, mean over seeds 0-4")
def drop_share_correct_digits_noise40():
    return statistics.mean(_drop_shares_of_train("digits", 0.4, False))


@source("drop_share_mislabeled_breast_noise20", means="mislabeled samples dropped by the filter as a share (%) of the training set, breast_cancer, 20% noise, mean over seeds 0-4")
def drop_share_mislabeled_breast_noise20():
    return statistics.mean(_drop_shares_of_train("breast_cancer", 0.2, True))


@source("drop_share_correct_breast_noise20", means="correctly labeled samples dropped by the filter as a share (%) of the training set, breast_cancer, 20% noise, mean over seeds 0-4")
def drop_share_correct_breast_noise20():
    return statistics.mean(_drop_shares_of_train("breast_cancer", 0.2, False))


@source("drop_share_mislabeled_breast_noise40", means="mislabeled samples dropped by the filter as a share (%) of the training set, breast_cancer, 40% noise, mean over seeds 0-4")
def drop_share_mislabeled_breast_noise40():
    return statistics.mean(_drop_shares_of_train("breast_cancer", 0.4, True))


@source("drop_share_correct_breast_noise40", means="correctly labeled samples dropped by the filter as a share (%) of the training set, breast_cancer, 40% noise, mean over seeds 0-4")
def drop_share_correct_breast_noise40():
    return statistics.mean(_drop_shares_of_train("breast_cancer", 0.4, False))


# --- Spread of the paired gain (ours minus logistic regression) ---

@source("std_gain_vs_logreg_digits_noise0", means="sample sd (points) over seeds 0-4 of the paired difference ours minus logistic regression test accuracy, digits, clean labels")
def std_gain_vs_logreg_digits_noise0():
    return statistics.stdev(_diffs("digits", 0.0, "filter", "logreg"))


@source("std_gain_vs_logreg_digits_noise20", means="sample sd (points) over seeds 0-4 of the paired difference ours minus logistic regression test accuracy, digits, 20% noise")
def std_gain_vs_logreg_digits_noise20():
    return statistics.stdev(_diffs("digits", 0.2, "filter", "logreg"))


@source("std_gain_vs_logreg_digits_noise40", means="sample sd (points) over seeds 0-4 of the paired difference ours minus logistic regression test accuracy, digits, 40% noise")
def std_gain_vs_logreg_digits_noise40():
    return statistics.stdev(_diffs("digits", 0.4, "filter", "logreg"))


@source("std_gain_vs_logreg_breast_noise0", means="sample sd (points) over seeds 0-4 of the paired difference ours minus logistic regression test accuracy, breast_cancer, clean labels")
def std_gain_vs_logreg_breast_noise0():
    return statistics.stdev(_diffs("breast_cancer", 0.0, "filter", "logreg"))


@source("std_gain_vs_logreg_breast_noise20", means="sample sd (points) over seeds 0-4 of the paired difference ours minus logistic regression test accuracy, breast_cancer, 20% noise")
def std_gain_vs_logreg_breast_noise20():
    return statistics.stdev(_diffs("breast_cancer", 0.2, "filter", "logreg"))


@source("std_gain_vs_logreg_breast_noise40", means="sample sd (points) over seeds 0-4 of the paired difference ours minus logistic regression test accuracy, breast_cancer, 40% noise")
def std_gain_vs_logreg_breast_noise40():
    return statistics.stdev(_diffs("breast_cancer", 0.4, "filter", "logreg"))


# --- Per-seed paired gain (ours minus logistic regression, same split and labels) ---

@source("gain_vs_logreg_digits_noise0_seed0", means="ours minus logistic regression test accuracy (points), digits, clean labels, seed 0")
def gain_vs_logreg_digits_noise0_seed0():
    return _diffs("digits", 0.0, "filter", "logreg")[0]


@source("gain_vs_logreg_digits_noise0_seed1", means="ours minus logistic regression test accuracy (points), digits, clean labels, seed 1")
def gain_vs_logreg_digits_noise0_seed1():
    return _diffs("digits", 0.0, "filter", "logreg")[1]


@source("gain_vs_logreg_digits_noise0_seed2", means="ours minus logistic regression test accuracy (points), digits, clean labels, seed 2")
def gain_vs_logreg_digits_noise0_seed2():
    return _diffs("digits", 0.0, "filter", "logreg")[2]


@source("gain_vs_logreg_digits_noise0_seed3", means="ours minus logistic regression test accuracy (points), digits, clean labels, seed 3")
def gain_vs_logreg_digits_noise0_seed3():
    return _diffs("digits", 0.0, "filter", "logreg")[3]


@source("gain_vs_logreg_digits_noise0_seed4", means="ours minus logistic regression test accuracy (points), digits, clean labels, seed 4")
def gain_vs_logreg_digits_noise0_seed4():
    return _diffs("digits", 0.0, "filter", "logreg")[4]


@source("gain_vs_logreg_digits_noise20_seed0", means="ours minus logistic regression test accuracy (points), digits, 20% noise, seed 0")
def gain_vs_logreg_digits_noise20_seed0():
    return _diffs("digits", 0.2, "filter", "logreg")[0]


@source("gain_vs_logreg_digits_noise20_seed1", means="ours minus logistic regression test accuracy (points), digits, 20% noise, seed 1")
def gain_vs_logreg_digits_noise20_seed1():
    return _diffs("digits", 0.2, "filter", "logreg")[1]


@source("gain_vs_logreg_digits_noise20_seed2", means="ours minus logistic regression test accuracy (points), digits, 20% noise, seed 2")
def gain_vs_logreg_digits_noise20_seed2():
    return _diffs("digits", 0.2, "filter", "logreg")[2]


@source("gain_vs_logreg_digits_noise20_seed3", means="ours minus logistic regression test accuracy (points), digits, 20% noise, seed 3")
def gain_vs_logreg_digits_noise20_seed3():
    return _diffs("digits", 0.2, "filter", "logreg")[3]


@source("gain_vs_logreg_digits_noise20_seed4", means="ours minus logistic regression test accuracy (points), digits, 20% noise, seed 4")
def gain_vs_logreg_digits_noise20_seed4():
    return _diffs("digits", 0.2, "filter", "logreg")[4]


@source("gain_vs_logreg_digits_noise40_seed0", means="ours minus logistic regression test accuracy (points), digits, 40% noise, seed 0")
def gain_vs_logreg_digits_noise40_seed0():
    return _diffs("digits", 0.4, "filter", "logreg")[0]


@source("gain_vs_logreg_digits_noise40_seed1", means="ours minus logistic regression test accuracy (points), digits, 40% noise, seed 1")
def gain_vs_logreg_digits_noise40_seed1():
    return _diffs("digits", 0.4, "filter", "logreg")[1]


@source("gain_vs_logreg_digits_noise40_seed2", means="ours minus logistic regression test accuracy (points), digits, 40% noise, seed 2")
def gain_vs_logreg_digits_noise40_seed2():
    return _diffs("digits", 0.4, "filter", "logreg")[2]


@source("gain_vs_logreg_digits_noise40_seed3", means="ours minus logistic regression test accuracy (points), digits, 40% noise, seed 3")
def gain_vs_logreg_digits_noise40_seed3():
    return _diffs("digits", 0.4, "filter", "logreg")[3]


@source("gain_vs_logreg_digits_noise40_seed4", means="ours minus logistic regression test accuracy (points), digits, 40% noise, seed 4")
def gain_vs_logreg_digits_noise40_seed4():
    return _diffs("digits", 0.4, "filter", "logreg")[4]


@source("gain_vs_logreg_breast_noise0_seed0", means="ours minus logistic regression test accuracy (points), breast_cancer, clean labels, seed 0")
def gain_vs_logreg_breast_noise0_seed0():
    return _diffs("breast_cancer", 0.0, "filter", "logreg")[0]


@source("gain_vs_logreg_breast_noise0_seed1", means="ours minus logistic regression test accuracy (points), breast_cancer, clean labels, seed 1")
def gain_vs_logreg_breast_noise0_seed1():
    return _diffs("breast_cancer", 0.0, "filter", "logreg")[1]


@source("gain_vs_logreg_breast_noise0_seed2", means="ours minus logistic regression test accuracy (points), breast_cancer, clean labels, seed 2")
def gain_vs_logreg_breast_noise0_seed2():
    return _diffs("breast_cancer", 0.0, "filter", "logreg")[2]


@source("gain_vs_logreg_breast_noise0_seed3", means="ours minus logistic regression test accuracy (points), breast_cancer, clean labels, seed 3")
def gain_vs_logreg_breast_noise0_seed3():
    return _diffs("breast_cancer", 0.0, "filter", "logreg")[3]


@source("gain_vs_logreg_breast_noise0_seed4", means="ours minus logistic regression test accuracy (points), breast_cancer, clean labels, seed 4")
def gain_vs_logreg_breast_noise0_seed4():
    return _diffs("breast_cancer", 0.0, "filter", "logreg")[4]


@source("gain_vs_logreg_breast_noise20_seed0", means="ours minus logistic regression test accuracy (points), breast_cancer, 20% noise, seed 0")
def gain_vs_logreg_breast_noise20_seed0():
    return _diffs("breast_cancer", 0.2, "filter", "logreg")[0]


@source("gain_vs_logreg_breast_noise20_seed1", means="ours minus logistic regression test accuracy (points), breast_cancer, 20% noise, seed 1")
def gain_vs_logreg_breast_noise20_seed1():
    return _diffs("breast_cancer", 0.2, "filter", "logreg")[1]


@source("gain_vs_logreg_breast_noise20_seed2", means="ours minus logistic regression test accuracy (points), breast_cancer, 20% noise, seed 2")
def gain_vs_logreg_breast_noise20_seed2():
    return _diffs("breast_cancer", 0.2, "filter", "logreg")[2]


@source("gain_vs_logreg_breast_noise20_seed3", means="ours minus logistic regression test accuracy (points), breast_cancer, 20% noise, seed 3")
def gain_vs_logreg_breast_noise20_seed3():
    return _diffs("breast_cancer", 0.2, "filter", "logreg")[3]


@source("gain_vs_logreg_breast_noise20_seed4", means="ours minus logistic regression test accuracy (points), breast_cancer, 20% noise, seed 4")
def gain_vs_logreg_breast_noise20_seed4():
    return _diffs("breast_cancer", 0.2, "filter", "logreg")[4]


@source("gain_vs_logreg_breast_noise40_seed0", means="ours minus logistic regression test accuracy (points), breast_cancer, 40% noise, seed 0")
def gain_vs_logreg_breast_noise40_seed0():
    return _diffs("breast_cancer", 0.4, "filter", "logreg")[0]


@source("gain_vs_logreg_breast_noise40_seed1", means="ours minus logistic regression test accuracy (points), breast_cancer, 40% noise, seed 1")
def gain_vs_logreg_breast_noise40_seed1():
    return _diffs("breast_cancer", 0.4, "filter", "logreg")[1]


@source("gain_vs_logreg_breast_noise40_seed2", means="ours minus logistic regression test accuracy (points), breast_cancer, 40% noise, seed 2")
def gain_vs_logreg_breast_noise40_seed2():
    return _diffs("breast_cancer", 0.4, "filter", "logreg")[2]


@source("gain_vs_logreg_breast_noise40_seed3", means="ours minus logistic regression test accuracy (points), breast_cancer, 40% noise, seed 3")
def gain_vs_logreg_breast_noise40_seed3():
    return _diffs("breast_cancer", 0.4, "filter", "logreg")[3]


@source("gain_vs_logreg_breast_noise40_seed4", means="ours minus logistic regression test accuracy (points), breast_cancer, 40% noise, seed 4")
def gain_vs_logreg_breast_noise40_seed4():
    return _diffs("breast_cancer", 0.4, "filter", "logreg")[4]


# --- Per-seed test accuracy: logistic regression ---

@source("acc_logreg_digits_noise0_seed0", means="test accuracy (%) of logistic regression, digits, clean labels, seed 0")
def acc_logreg_digits_noise0_seed0():
    return _accs("digits", 0.0, "logreg")[0]


@source("acc_logreg_digits_noise0_seed1", means="test accuracy (%) of logistic regression, digits, clean labels, seed 1")
def acc_logreg_digits_noise0_seed1():
    return _accs("digits", 0.0, "logreg")[1]


@source("acc_logreg_digits_noise0_seed2", means="test accuracy (%) of logistic regression, digits, clean labels, seed 2")
def acc_logreg_digits_noise0_seed2():
    return _accs("digits", 0.0, "logreg")[2]


@source("acc_logreg_digits_noise0_seed3", means="test accuracy (%) of logistic regression, digits, clean labels, seed 3")
def acc_logreg_digits_noise0_seed3():
    return _accs("digits", 0.0, "logreg")[3]


@source("acc_logreg_digits_noise0_seed4", means="test accuracy (%) of logistic regression, digits, clean labels, seed 4")
def acc_logreg_digits_noise0_seed4():
    return _accs("digits", 0.0, "logreg")[4]


@source("acc_logreg_digits_noise20_seed0", means="test accuracy (%) of logistic regression, digits, 20% noise, seed 0")
def acc_logreg_digits_noise20_seed0():
    return _accs("digits", 0.2, "logreg")[0]


@source("acc_logreg_digits_noise20_seed1", means="test accuracy (%) of logistic regression, digits, 20% noise, seed 1")
def acc_logreg_digits_noise20_seed1():
    return _accs("digits", 0.2, "logreg")[1]


@source("acc_logreg_digits_noise20_seed2", means="test accuracy (%) of logistic regression, digits, 20% noise, seed 2")
def acc_logreg_digits_noise20_seed2():
    return _accs("digits", 0.2, "logreg")[2]


@source("acc_logreg_digits_noise20_seed3", means="test accuracy (%) of logistic regression, digits, 20% noise, seed 3")
def acc_logreg_digits_noise20_seed3():
    return _accs("digits", 0.2, "logreg")[3]


@source("acc_logreg_digits_noise20_seed4", means="test accuracy (%) of logistic regression, digits, 20% noise, seed 4")
def acc_logreg_digits_noise20_seed4():
    return _accs("digits", 0.2, "logreg")[4]


@source("acc_logreg_digits_noise40_seed0", means="test accuracy (%) of logistic regression, digits, 40% noise, seed 0")
def acc_logreg_digits_noise40_seed0():
    return _accs("digits", 0.4, "logreg")[0]


@source("acc_logreg_digits_noise40_seed1", means="test accuracy (%) of logistic regression, digits, 40% noise, seed 1")
def acc_logreg_digits_noise40_seed1():
    return _accs("digits", 0.4, "logreg")[1]


@source("acc_logreg_digits_noise40_seed2", means="test accuracy (%) of logistic regression, digits, 40% noise, seed 2")
def acc_logreg_digits_noise40_seed2():
    return _accs("digits", 0.4, "logreg")[2]


@source("acc_logreg_digits_noise40_seed3", means="test accuracy (%) of logistic regression, digits, 40% noise, seed 3")
def acc_logreg_digits_noise40_seed3():
    return _accs("digits", 0.4, "logreg")[3]


@source("acc_logreg_digits_noise40_seed4", means="test accuracy (%) of logistic regression, digits, 40% noise, seed 4")
def acc_logreg_digits_noise40_seed4():
    return _accs("digits", 0.4, "logreg")[4]


@source("acc_logreg_breast_noise0_seed0", means="test accuracy (%) of logistic regression, breast_cancer, clean labels, seed 0")
def acc_logreg_breast_noise0_seed0():
    return _accs("breast_cancer", 0.0, "logreg")[0]


@source("acc_logreg_breast_noise0_seed1", means="test accuracy (%) of logistic regression, breast_cancer, clean labels, seed 1")
def acc_logreg_breast_noise0_seed1():
    return _accs("breast_cancer", 0.0, "logreg")[1]


@source("acc_logreg_breast_noise0_seed2", means="test accuracy (%) of logistic regression, breast_cancer, clean labels, seed 2")
def acc_logreg_breast_noise0_seed2():
    return _accs("breast_cancer", 0.0, "logreg")[2]


@source("acc_logreg_breast_noise0_seed3", means="test accuracy (%) of logistic regression, breast_cancer, clean labels, seed 3")
def acc_logreg_breast_noise0_seed3():
    return _accs("breast_cancer", 0.0, "logreg")[3]


@source("acc_logreg_breast_noise0_seed4", means="test accuracy (%) of logistic regression, breast_cancer, clean labels, seed 4")
def acc_logreg_breast_noise0_seed4():
    return _accs("breast_cancer", 0.0, "logreg")[4]


@source("acc_logreg_breast_noise20_seed0", means="test accuracy (%) of logistic regression, breast_cancer, 20% noise, seed 0")
def acc_logreg_breast_noise20_seed0():
    return _accs("breast_cancer", 0.2, "logreg")[0]


@source("acc_logreg_breast_noise20_seed1", means="test accuracy (%) of logistic regression, breast_cancer, 20% noise, seed 1")
def acc_logreg_breast_noise20_seed1():
    return _accs("breast_cancer", 0.2, "logreg")[1]


@source("acc_logreg_breast_noise20_seed2", means="test accuracy (%) of logistic regression, breast_cancer, 20% noise, seed 2")
def acc_logreg_breast_noise20_seed2():
    return _accs("breast_cancer", 0.2, "logreg")[2]


@source("acc_logreg_breast_noise20_seed3", means="test accuracy (%) of logistic regression, breast_cancer, 20% noise, seed 3")
def acc_logreg_breast_noise20_seed3():
    return _accs("breast_cancer", 0.2, "logreg")[3]


@source("acc_logreg_breast_noise20_seed4", means="test accuracy (%) of logistic regression, breast_cancer, 20% noise, seed 4")
def acc_logreg_breast_noise20_seed4():
    return _accs("breast_cancer", 0.2, "logreg")[4]


@source("acc_logreg_breast_noise40_seed0", means="test accuracy (%) of logistic regression, breast_cancer, 40% noise, seed 0")
def acc_logreg_breast_noise40_seed0():
    return _accs("breast_cancer", 0.4, "logreg")[0]


@source("acc_logreg_breast_noise40_seed1", means="test accuracy (%) of logistic regression, breast_cancer, 40% noise, seed 1")
def acc_logreg_breast_noise40_seed1():
    return _accs("breast_cancer", 0.4, "logreg")[1]


@source("acc_logreg_breast_noise40_seed2", means="test accuracy (%) of logistic regression, breast_cancer, 40% noise, seed 2")
def acc_logreg_breast_noise40_seed2():
    return _accs("breast_cancer", 0.4, "logreg")[2]


@source("acc_logreg_breast_noise40_seed3", means="test accuracy (%) of logistic regression, breast_cancer, 40% noise, seed 3")
def acc_logreg_breast_noise40_seed3():
    return _accs("breast_cancer", 0.4, "logreg")[3]


@source("acc_logreg_breast_noise40_seed4", means="test accuracy (%) of logistic regression, breast_cancer, 40% noise, seed 4")
def acc_logreg_breast_noise40_seed4():
    return _accs("breast_cancer", 0.4, "logreg")[4]


# --- Per-seed test accuracy: ours (filter) ---

@source("acc_filter_digits_noise0_seed0", means="test accuracy (%) of ours (filter), digits, clean labels, seed 0")
def acc_filter_digits_noise0_seed0():
    return _accs("digits", 0.0, "filter")[0]


@source("acc_filter_digits_noise0_seed1", means="test accuracy (%) of ours (filter), digits, clean labels, seed 1")
def acc_filter_digits_noise0_seed1():
    return _accs("digits", 0.0, "filter")[1]


@source("acc_filter_digits_noise0_seed2", means="test accuracy (%) of ours (filter), digits, clean labels, seed 2")
def acc_filter_digits_noise0_seed2():
    return _accs("digits", 0.0, "filter")[2]


@source("acc_filter_digits_noise0_seed3", means="test accuracy (%) of ours (filter), digits, clean labels, seed 3")
def acc_filter_digits_noise0_seed3():
    return _accs("digits", 0.0, "filter")[3]


@source("acc_filter_digits_noise0_seed4", means="test accuracy (%) of ours (filter), digits, clean labels, seed 4")
def acc_filter_digits_noise0_seed4():
    return _accs("digits", 0.0, "filter")[4]


@source("acc_filter_digits_noise20_seed0", means="test accuracy (%) of ours (filter), digits, 20% noise, seed 0")
def acc_filter_digits_noise20_seed0():
    return _accs("digits", 0.2, "filter")[0]


@source("acc_filter_digits_noise20_seed1", means="test accuracy (%) of ours (filter), digits, 20% noise, seed 1")
def acc_filter_digits_noise20_seed1():
    return _accs("digits", 0.2, "filter")[1]


@source("acc_filter_digits_noise20_seed2", means="test accuracy (%) of ours (filter), digits, 20% noise, seed 2")
def acc_filter_digits_noise20_seed2():
    return _accs("digits", 0.2, "filter")[2]


@source("acc_filter_digits_noise20_seed3", means="test accuracy (%) of ours (filter), digits, 20% noise, seed 3")
def acc_filter_digits_noise20_seed3():
    return _accs("digits", 0.2, "filter")[3]


@source("acc_filter_digits_noise20_seed4", means="test accuracy (%) of ours (filter), digits, 20% noise, seed 4")
def acc_filter_digits_noise20_seed4():
    return _accs("digits", 0.2, "filter")[4]


@source("acc_filter_digits_noise40_seed0", means="test accuracy (%) of ours (filter), digits, 40% noise, seed 0")
def acc_filter_digits_noise40_seed0():
    return _accs("digits", 0.4, "filter")[0]


@source("acc_filter_digits_noise40_seed1", means="test accuracy (%) of ours (filter), digits, 40% noise, seed 1")
def acc_filter_digits_noise40_seed1():
    return _accs("digits", 0.4, "filter")[1]


@source("acc_filter_digits_noise40_seed2", means="test accuracy (%) of ours (filter), digits, 40% noise, seed 2")
def acc_filter_digits_noise40_seed2():
    return _accs("digits", 0.4, "filter")[2]


@source("acc_filter_digits_noise40_seed3", means="test accuracy (%) of ours (filter), digits, 40% noise, seed 3")
def acc_filter_digits_noise40_seed3():
    return _accs("digits", 0.4, "filter")[3]


@source("acc_filter_digits_noise40_seed4", means="test accuracy (%) of ours (filter), digits, 40% noise, seed 4")
def acc_filter_digits_noise40_seed4():
    return _accs("digits", 0.4, "filter")[4]


@source("acc_filter_breast_noise0_seed0", means="test accuracy (%) of ours (filter), breast_cancer, clean labels, seed 0")
def acc_filter_breast_noise0_seed0():
    return _accs("breast_cancer", 0.0, "filter")[0]


@source("acc_filter_breast_noise0_seed1", means="test accuracy (%) of ours (filter), breast_cancer, clean labels, seed 1")
def acc_filter_breast_noise0_seed1():
    return _accs("breast_cancer", 0.0, "filter")[1]


@source("acc_filter_breast_noise0_seed2", means="test accuracy (%) of ours (filter), breast_cancer, clean labels, seed 2")
def acc_filter_breast_noise0_seed2():
    return _accs("breast_cancer", 0.0, "filter")[2]


@source("acc_filter_breast_noise0_seed3", means="test accuracy (%) of ours (filter), breast_cancer, clean labels, seed 3")
def acc_filter_breast_noise0_seed3():
    return _accs("breast_cancer", 0.0, "filter")[3]


@source("acc_filter_breast_noise0_seed4", means="test accuracy (%) of ours (filter), breast_cancer, clean labels, seed 4")
def acc_filter_breast_noise0_seed4():
    return _accs("breast_cancer", 0.0, "filter")[4]


@source("acc_filter_breast_noise20_seed0", means="test accuracy (%) of ours (filter), breast_cancer, 20% noise, seed 0")
def acc_filter_breast_noise20_seed0():
    return _accs("breast_cancer", 0.2, "filter")[0]


@source("acc_filter_breast_noise20_seed1", means="test accuracy (%) of ours (filter), breast_cancer, 20% noise, seed 1")
def acc_filter_breast_noise20_seed1():
    return _accs("breast_cancer", 0.2, "filter")[1]


@source("acc_filter_breast_noise20_seed2", means="test accuracy (%) of ours (filter), breast_cancer, 20% noise, seed 2")
def acc_filter_breast_noise20_seed2():
    return _accs("breast_cancer", 0.2, "filter")[2]


@source("acc_filter_breast_noise20_seed3", means="test accuracy (%) of ours (filter), breast_cancer, 20% noise, seed 3")
def acc_filter_breast_noise20_seed3():
    return _accs("breast_cancer", 0.2, "filter")[3]


@source("acc_filter_breast_noise20_seed4", means="test accuracy (%) of ours (filter), breast_cancer, 20% noise, seed 4")
def acc_filter_breast_noise20_seed4():
    return _accs("breast_cancer", 0.2, "filter")[4]


@source("acc_filter_breast_noise40_seed0", means="test accuracy (%) of ours (filter), breast_cancer, 40% noise, seed 0")
def acc_filter_breast_noise40_seed0():
    return _accs("breast_cancer", 0.4, "filter")[0]


@source("acc_filter_breast_noise40_seed1", means="test accuracy (%) of ours (filter), breast_cancer, 40% noise, seed 1")
def acc_filter_breast_noise40_seed1():
    return _accs("breast_cancer", 0.4, "filter")[1]


@source("acc_filter_breast_noise40_seed2", means="test accuracy (%) of ours (filter), breast_cancer, 40% noise, seed 2")
def acc_filter_breast_noise40_seed2():
    return _accs("breast_cancer", 0.4, "filter")[2]


@source("acc_filter_breast_noise40_seed3", means="test accuracy (%) of ours (filter), breast_cancer, 40% noise, seed 3")
def acc_filter_breast_noise40_seed3():
    return _accs("breast_cancer", 0.4, "filter")[3]


@source("acc_filter_breast_noise40_seed4", means="test accuracy (%) of ours (filter), breast_cancer, 40% noise, seed 4")
def acc_filter_breast_noise40_seed4():
    return _accs("breast_cancer", 0.4, "filter")[4]


# ---------------------------------------------------------------------------
# What the filter leaves in the training set. Both are means over seeds of
# per-seed ratios. Random removal of the same number of samples would leave the
# mislabeled share of the kept set equal, in expectation, to the flipped share.
# ---------------------------------------------------------------------------

def _kept_noisy_shares(dataset, noise):
    """Per seed, the percentage of the kept set whose label was flipped."""
    return [100 * (r["n_noisy"] - r["n_dropped_noisy"]) / (r["n_train"] - r["n_dropped"])
            for r in _runs(dataset, noise, "filter")]


def _correct_dropped_shares(dataset, noise):
    """Per seed, the percentage of correctly labeled training samples that the filter dropped."""
    return [100 * (r["n_dropped"] - r["n_dropped_noisy"]) / (r["n_train"] - r["n_noisy"])
            for r in _runs(dataset, noise, "filter")]


@source("kept_noisy_share_digits_noise20", means="share (%) of the kept set that is mislabeled, (n_noisy - n_dropped_noisy) / (n_train - n_dropped), digits, 20% noise, mean of per-seed ratios over seeds 0-4")
def kept_noisy_share_digits_noise20():
    return statistics.mean(_kept_noisy_shares("digits", 0.2))


@source("kept_noisy_share_digits_noise40", means="share (%) of the kept set that is mislabeled, (n_noisy - n_dropped_noisy) / (n_train - n_dropped), digits, 40% noise, mean of per-seed ratios over seeds 0-4")
def kept_noisy_share_digits_noise40():
    return statistics.mean(_kept_noisy_shares("digits", 0.4))


@source("kept_noisy_share_breast_noise20", means="share (%) of the kept set that is mislabeled, (n_noisy - n_dropped_noisy) / (n_train - n_dropped), breast_cancer, 20% noise, mean of per-seed ratios over seeds 0-4")
def kept_noisy_share_breast_noise20():
    return statistics.mean(_kept_noisy_shares("breast_cancer", 0.2))


@source("kept_noisy_share_breast_noise40", means="share (%) of the kept set that is mislabeled, (n_noisy - n_dropped_noisy) / (n_train - n_dropped), breast_cancer, 40% noise, mean of per-seed ratios over seeds 0-4")
def kept_noisy_share_breast_noise40():
    return statistics.mean(_kept_noisy_shares("breast_cancer", 0.4))


@source("correct_dropped_digits_noise20", means="share (%) of correctly labeled training samples that the filter dropped, (n_dropped - n_dropped_noisy) / (n_train - n_noisy), digits, 20% noise, mean of per-seed ratios over seeds 0-4")
def correct_dropped_digits_noise20():
    return statistics.mean(_correct_dropped_shares("digits", 0.2))


@source("correct_dropped_digits_noise40", means="share (%) of correctly labeled training samples that the filter dropped, (n_dropped - n_dropped_noisy) / (n_train - n_noisy), digits, 40% noise, mean of per-seed ratios over seeds 0-4")
def correct_dropped_digits_noise40():
    return statistics.mean(_correct_dropped_shares("digits", 0.4))


@source("correct_dropped_breast_noise20", means="share (%) of correctly labeled training samples that the filter dropped, (n_dropped - n_dropped_noisy) / (n_train - n_noisy), breast_cancer, 20% noise, mean of per-seed ratios over seeds 0-4")
def correct_dropped_breast_noise20():
    return statistics.mean(_correct_dropped_shares("breast_cancer", 0.2))


@source("correct_dropped_breast_noise40", means="share (%) of correctly labeled training samples that the filter dropped, (n_dropped - n_dropped_noisy) / (n_train - n_noisy), breast_cancer, 40% noise, mean of per-seed ratios over seeds 0-4")
def correct_dropped_breast_noise40():
    return statistics.mean(_correct_dropped_shares("breast_cancer", 0.4))


# --- Drop precision relative to the flipped share (what random removal would reach) ---

def _precision_over_flipped(dataset, noise):
    """Seed-mean drop precision divided by the seed-mean flipped share of the training set."""
    return statistics.mean(_drop_precisions(dataset, noise)) / statistics.mean(_noisy_shares(dataset, noise))


@source("precision_over_flipped_digits_noise20", means="seed-mean drop precision divided by seed-mean flipped share of the training set, digits, 20% noise")
def precision_over_flipped_digits_noise20():
    return _precision_over_flipped("digits", 0.2)


@source("precision_over_flipped_digits_noise40", means="seed-mean drop precision divided by seed-mean flipped share of the training set, digits, 40% noise")
def precision_over_flipped_digits_noise40():
    return _precision_over_flipped("digits", 0.4)


@source("precision_over_flipped_breast_noise20", means="seed-mean drop precision divided by seed-mean flipped share of the training set, breast_cancer, 20% noise")
def precision_over_flipped_breast_noise20():
    return _precision_over_flipped("breast_cancer", 0.2)


@source("precision_over_flipped_breast_noise40", means="seed-mean drop precision divided by seed-mean flipped share of the training set, breast_cancer, 40% noise")
def precision_over_flipped_breast_noise40():
    return _precision_over_flipped("breast_cancer", 0.4)


# ---------------------------------------------------------------------------
# Breast cancer at 40% noise: the two least accurate seeds against the other
# three (an association over five seeds, not a test).
# ---------------------------------------------------------------------------

def _split_least_accurate(values):
    """Split per-seed values on breast_cancer at 40% noise into the two least accurate seeds and the other three.

    Raises if the filter and logistic regression do not have the same two least accurate seeds.
    """
    pairs = []
    for method in ("filter", "logreg"):
        accs = _accs("breast_cancer", 0.4, method)
        pairs.append(set(sorted(range(len(accs)), key=lambda i: accs[i])[:2]))
    if pairs[0] != pairs[1]:
        raise ValueError("the two least accurate seeds differ between ours and logistic regression")
    low = [v for i, v in enumerate(values) if i in pairs[0]]
    other = [v for i, v in enumerate(values) if i not in pairs[0]]
    return low, other


@source("flipped_low_seeds_min_breast_noise40", means="smallest flipped share (%) of the training set among the two seeds where ours and logistic regression are least accurate, breast_cancer, 40% noise")
def flipped_low_seeds_min_breast_noise40():
    return min(_split_least_accurate(_noisy_shares("breast_cancer", 0.4))[0])


@source("flipped_low_seeds_max_breast_noise40", means="largest flipped share (%) of the training set among the two seeds where ours and logistic regression are least accurate, breast_cancer, 40% noise")
def flipped_low_seeds_max_breast_noise40():
    return max(_split_least_accurate(_noisy_shares("breast_cancer", 0.4))[0])


@source("flipped_other_seeds_min_breast_noise40", means="smallest flipped share (%) of the training set among the other three seeds, breast_cancer, 40% noise")
def flipped_other_seeds_min_breast_noise40():
    return min(_split_least_accurate(_noisy_shares("breast_cancer", 0.4))[1])


@source("flipped_other_seeds_max_breast_noise40", means="largest flipped share (%) of the training set among the other three seeds, breast_cancer, 40% noise")
def flipped_other_seeds_max_breast_noise40():
    return max(_split_least_accurate(_noisy_shares("breast_cancer", 0.4))[1])


@source("kept_noisy_low_seeds_min_breast_noise40", means="smallest mislabeled share (%) of the kept set among the two seeds where ours and logistic regression are least accurate, breast_cancer, 40% noise")
def kept_noisy_low_seeds_min_breast_noise40():
    return min(_split_least_accurate(_kept_noisy_shares("breast_cancer", 0.4))[0])


@source("kept_noisy_other_seeds_max_breast_noise40", means="largest mislabeled share (%) of the kept set among the other three seeds, breast_cancer, 40% noise")
def kept_noisy_other_seeds_max_breast_noise40():
    return max(_split_least_accurate(_kept_noisy_shares("breast_cancer", 0.4))[1])


# --- Spread across seeds: recovered share at the lower rate, and the clean-label cost ---

@source("recovered_seed_min_breast_noise20", means="smallest per-seed share (%) of the logistic-regression noise cost that ours wins back, breast_cancer, 20% noise, seeds 0-4")
def recovered_seed_min_breast_noise20():
    return min(_recovered("breast_cancer", 0.2))


@source("recovered_seed_max_breast_noise20", means="largest per-seed share (%) of the logistic-regression noise cost that ours wins back, breast_cancer, 20% noise, seeds 0-4")
def recovered_seed_max_breast_noise20():
    return max(_recovered("breast_cancer", 0.2))


@source("gain_seed_min_digits_noise0", means="smallest per-seed difference ours minus logistic regression test accuracy (points), digits, clean labels, seeds 0-4")
def gain_seed_min_digits_noise0():
    return min(_diffs("digits", 0.0, "filter", "logreg"))


@source("gain_seed_max_digits_noise0", means="largest per-seed difference ours minus logistic regression test accuracy (points), digits, clean labels, seeds 0-4")
def gain_seed_max_digits_noise0():
    return max(_diffs("digits", 0.0, "filter", "logreg"))


@source("n_seeds_differ_breast_noise0", means="number of seeds in which ours and logistic regression differ in test accuracy, breast_cancer, clean labels")
def n_seeds_differ_breast_noise0():
    return sum(d != 0 for d in _diffs("breast_cancer", 0.0, "filter", "logreg"))


@source("test_samples_differ_breast_noise0", means="largest per-seed difference between ours and logistic regression counted in test samples, breast_cancer, clean labels")
def test_samples_differ_breast_noise0():
    return max(abs(d) for d in _diffs("breast_cancer", 0.0, "filter", "logreg")) * _unique("breast_cancer", "n_test") / 100
