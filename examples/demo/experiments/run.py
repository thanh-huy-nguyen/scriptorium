"""Label-noise study: does dropping training samples that out-of-fold predictions disagree with help a linear model?

Writes one JSON line per (dataset, noise rate, seed, method) to results/runs.jsonl. Needs scikit-learn and numpy.
Methods:
  logreg   logistic regression on standardized features, trained on the noisy labels
  mlp      one-hidden-layer MLP, trained on the noisy labels
  filter   ours: fit logistic regression with K-fold cross-validation, drop every training sample whose out-of-fold
           prediction disagrees with its (noisy) label, and refit on the rest
"""
import json
import time
from pathlib import Path

import numpy as np
from sklearn.datasets import load_breast_cancer, load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "experiments" / "config.json").read_text())
LOADERS = {"digits": load_digits, "breast_cancer": load_breast_cancer}


def flip(y, rate, n_classes, rng):
    y = y.copy()
    noisy = rng.random(len(y)) < rate
    for i in np.where(noisy)[0]:
        y[i] = rng.choice([c for c in range(n_classes) if c != y[i]])
    return y, noisy & True


def logreg():
    return make_pipeline(StandardScaler(), LogisticRegression(C=CFG["logreg_C"], max_iter=5000))


def main():
    out = ROOT / "results" / "runs.jsonl"
    rows = []
    for ds in CFG["datasets"]:
        X, y = LOADERS[ds](return_X_y=True)
        k = len(np.unique(y))
        for rate in CFG["noise_rates"]:
            for seed in CFG["seeds"]:
                rng = np.random.default_rng(seed)
                Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=CFG["test_fraction"], stratify=y,
                                                      random_state=seed)
                ytr_noisy, is_noisy = flip(ytr, rate, k, rng)
                base = {"dataset": ds, "noise": rate, "seed": seed, "n_train": int(len(ytr)), "n_test": int(len(yte)),
                        "n_noisy": int(is_noisy.sum())}
                t = time.time()
                m = logreg().fit(Xtr, ytr_noisy)
                rows.append({**base, "method": "logreg", "test_acc": float(m.score(Xte, yte)),
                             "fit_seconds": time.time() - t})
                t = time.time()
                m = make_pipeline(StandardScaler(), MLPClassifier(hidden_layer_sizes=(CFG["mlp_hidden"],),
                                                                  max_iter=CFG["mlp_max_iter"], random_state=seed))
                m.fit(Xtr, ytr_noisy)
                rows.append({**base, "method": "mlp", "test_acc": float(m.score(Xte, yte)),
                             "fit_seconds": time.time() - t})
                t = time.time()
                cv = StratifiedKFold(CFG["filter_folds"], shuffle=True, random_state=seed)
                oof = cross_val_predict(logreg(), Xtr, ytr_noisy, cv=cv)
                keep = oof == ytr_noisy
                m = logreg().fit(Xtr[keep], ytr_noisy[keep])
                dropped = ~keep
                rows.append({**base, "method": "filter", "test_acc": float(m.score(Xte, yte)),
                             "fit_seconds": time.time() - t, "n_dropped": int(dropped.sum()),
                             "n_dropped_noisy": int((dropped & is_noisy).sum())})
                print(ds, rate, seed, " ".join(f"{r['method']}={r['test_acc']:.3f}" for r in rows[-3:]))
    out.write_text("".join(json.dumps(r) + "\n" for r in rows))


if __name__ == "__main__":
    main()
