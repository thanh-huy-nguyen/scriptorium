"""Statistics for recipes in paper/sources.py. Pure Python, so any project interpreter can run them.

    from scriptorium_stats import mean, sd, ci95, paired_p, diff_ci95, cohens_dz, wins

Every function takes plain lists of numbers (one per seed, fold or subject). A claim that one method is better than
another needs a paired test across the same seeds or folds: `paired_p(ours, baseline)` gives the two-sided p-value of
an exact sign-flip permutation test (all 2^n sign patterns for n <= 16, else 20,000 random ones with a fixed seed),
and `diff_ci95(ours, baseline)` a bootstrap interval for the mean difference.
"""
from __future__ import annotations

import itertools
import math
import random
from collections.abc import Sequence


def _f(xs: Sequence[float]) -> list[float]:
    out = [float(x) for x in xs]
    if not out:
        raise ValueError("no values")
    return out


def mean(xs: Sequence[float]) -> float:
    xs = _f(xs)
    return sum(xs) / len(xs)


def sd(xs: Sequence[float]) -> float:
    """Sample standard deviation (n - 1)."""
    xs = _f(xs)
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def sem(xs: Sequence[float]) -> float:
    return sd(xs) / math.sqrt(len(_f(xs)))


# Two-sided 97.5% quantiles of Student's t for small samples; beyond 30 the normal value is used.
_T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
         11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093,
         20: 2.086, 21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048,
         29: 2.045, 30: 2.042}


def ci95(xs: Sequence[float]) -> tuple[float, float]:
    """t-based 95% confidence interval of the mean."""
    xs = _f(xs)
    if len(xs) < 2:
        return xs[0], xs[0]
    t = _T975.get(len(xs) - 1, 1.96)
    h = t * sem(xs)
    m = mean(xs)
    return m - h, m + h


def ci95_low(xs):
    return ci95(xs)[0]


def ci95_high(xs):
    return ci95(xs)[1]


def _pairs(a: Sequence[float], b: Sequence[float]) -> list[float]:
    a, b = _f(a), _f(b)
    if len(a) != len(b):
        raise ValueError(f"paired values need equal lengths, got {len(a)} and {len(b)}")
    return [x - y for x, y in zip(a, b)]


def paired_p(a: Sequence[float], b: Sequence[float], seed: int = 0) -> float:
    """Two-sided p-value that the mean of a - b is zero (exact sign-flip permutation test)."""
    d = _pairs(a, b)
    obs = abs(sum(d))
    n = len(d)
    if all(x == 0 for x in d):
        return 1.0
    if n <= 16:
        hits = total = 0
        for signs in itertools.product((1, -1), repeat=n):
            total += 1
            hits += abs(sum(s * x for s, x in zip(signs, d))) >= obs - 1e-12
        return hits / total
    rng = random.Random(seed)
    k = 20000
    hits = sum(abs(sum(x if rng.random() < 0.5 else -x for x in d)) >= obs - 1e-12 for _ in range(k))
    return (hits + 1) / (k + 1)


def diff_ci95(a: Sequence[float], b: Sequence[float], reps: int = 10000, seed: int = 0) -> tuple[float, float]:
    """Percentile bootstrap 95% interval for the mean of a - b."""
    d = _pairs(a, b)
    rng = random.Random(seed)
    n = len(d)
    ms = sorted(sum(d[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps))
    return ms[int(0.025 * reps)], ms[int(0.975 * reps) - 1]


def diff_ci95_low(a, b):
    return diff_ci95(a, b)[0]


def diff_ci95_high(a, b):
    return diff_ci95(a, b)[1]


def cohens_dz(a: Sequence[float], b: Sequence[float]) -> float:
    """Effect size of a paired difference: mean(a - b) / sd(a - b)."""
    d = _pairs(a, b)
    s = sd(d)
    return mean(d) / s if s else float("inf") if mean(d) else 0.0


def wins(a: Sequence[float], b: Sequence[float]) -> int:
    """How many paired runs a beats b."""
    return sum(x > 0 for x in _pairs(a, b))


def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the regularized incomplete beta (Numerical Recipes, Lentz's method)."""
    tiny, qab, qap, qam = 1e-300, a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-14:
            break
    return h


def _betainc(a: float, b: float, x: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lb) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lb) * _betacf(b, a, 1 - x) / b


def t_two_sided_p(t: float, df: float) -> float:
    """Two-sided p-value of Student's t."""
    if math.isinf(t):
        return 0.0
    return _betainc(df / 2, 0.5, df / (df + t * t))


def paired_t_p(a: Sequence[float], b: Sequence[float]) -> float:
    """Two-sided p-value of a paired t-test on a - b. Prefer this to paired_p when there are fewer than 6 pairs: the
    sign-flip test cannot go below 2 / 2^n (0.0625 for 5 seeds)."""
    d = _pairs(a, b)
    n = len(d)
    if n < 2:
        raise ValueError("a paired t-test needs at least 2 pairs")
    s = sd(d)
    if s == 0:
        return 0.0 if mean(d) != 0 else 1.0
    return t_two_sided_p(mean(d) / (s / math.sqrt(n)), n - 1)
