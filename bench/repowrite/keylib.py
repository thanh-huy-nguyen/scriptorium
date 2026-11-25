"""Standard quantities for answer keys: what careful authors compute for a paired comparison, so a key does not miss
a legitimate number. Used by each task's key/make_key.py (it needs numpy and scipy; it never imports Scriptorium).

    from keylib import paired, holm
    paired(q, a, b, dataset=..., method=..., versus=..., metric=..., condition=..., unit="fraction")
"""
from __future__ import annotations

import numpy as np
from scipy import stats

UNIT_OF_DIFF = {"fraction": "points", "count": "count", "ratio": "ratio", "seconds": "seconds", "points": "points"}


def paired(q, a, b, unit="fraction", **ident) -> list[tuple[str, float]]:
    """Every standard statistic of method a against method b over paired seeds; returns the p-values for a Holm
    family. `q(value, unit, **identity)` adds one key quantity."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = a - b
    n = len(d)
    du = UNIT_OF_DIFF.get(unit, unit)
    q(d.mean(), du, statistic="mean difference", **ident)
    q(np.median(d), du, statistic="median difference", **ident)
    q(d.min(), du, statistic="min difference over seeds", **ident)
    q(d.max(), du, statistic="max difference over seeds", **ident)
    q(int((d > 1e-12).sum()), "count", statistic="seeds where method is higher", **ident)
    q(int((d < -1e-12).sum()), "count", statistic="seeds where method is lower", **ident)
    q(int((np.abs(d) <= 1e-12).sum()), "count", statistic="seeds tied", **ident)
    if b.mean() != 0:
        q((a.mean() - b.mean()) / abs(b.mean()), "fraction", statistic="relative difference of means", **ident)
        q(a.mean() / b.mean(), "ratio", statistic="ratio of means", **ident)
    pvals = []
    if n > 1:
        sd = d.std(ddof=1)
        q(sd, du, statistic="sd of difference", **ident)
        if sd > 0:
            half = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)
            q(d.mean() - half, du, statistic="95% CI lower", **ident)
            q(d.mean() + half, du, statistic="95% CI upper", **ident)
            q(d.mean() / sd, "ratio", statistic="Cohen's d (paired)", **ident)
            t = stats.ttest_rel(a, b)
            q(t.pvalue, "p", statistic="p-value, paired t-test", **ident)
            q(t.statistic, "ratio", statistic="t statistic", **ident)
            q(t.pvalue / 2, "p", statistic="p-value, paired t-test, one-sided", **ident)
            pvals.append(("p-value, paired t-test", t.pvalue))
            if not np.allclose(d, 0):
                w = stats.wilcoxon(a, b)
                q(w.pvalue, "p", statistic="p-value, Wilcoxon signed-rank", **ident)
                pvals.append(("p-value, Wilcoxon signed-rank", w.pvalue))
            q(stats.sign_test(d).pvalue if hasattr(stats, "sign_test") else
              stats.binomtest(int((d > 0).sum()), int((d != 0).sum())).pvalue, "p", statistic="p-value, sign test",
              **ident)
    return pvals


def holm(q, family: list[tuple[dict, str, float]], label: str) -> None:
    """Holm-adjusted p-values over a family of (identity, test name, p) and the count significant after adjustment."""
    if not family:
        return
    order = sorted(range(len(family)), key=lambda i: family[i][2])
    m, running, adj = len(family), 0.0, [0.0] * len(family)
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * family[i][2]))
        adj[i] = running
    for (ident, test, _), p in zip(family, adj):
        q(p, "p", statistic=f"{test}, Holm-adjusted over {label}", **ident)


def ci_mean(q, v, unit="fraction", **ident) -> None:
    """95% t interval of a mean over seeds."""
    v = np.asarray(v, float)
    if len(v) > 1 and v.std(ddof=1) > 0:
        half = stats.t.ppf(0.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v))
        q(v.mean() - half, unit, statistic="95% CI lower of mean", **ident)
        q(v.mean() + half, unit, statistic="95% CI upper of mean", **ident)
