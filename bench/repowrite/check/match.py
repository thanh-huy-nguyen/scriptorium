"""Match extracted numbers against the answer key: identity first, then value.

Verdicts for a result number:
    supported        a key quantity with the stated identity has this value (at the printed precision)
    derived          the value follows from two key quantities of one identity (a ratio, a relative change, a
                     difference) and the paper's wording allows it
    misattributed    the value exists in the key, but only under another identity (the error a value lookup misses)
    unsupported      no key quantity has this value
    unclear          the paper gives no identity and the value is too common to place (small integers)
Setup numbers are matched against the key's setup facts; the rest are "not checkable" and go to a person.
"""
from __future__ import annotations

import itertools
import math

from common import decimals, exponent, num, word_num

FIELDS = ("dataset", "method", "versus", "condition", "metric", "statistic")
SCALES = {"fraction": (1.0, 100.0), "points": (1.0, 100.0), "count": (1.0,), "p": (1.0,), "ratio": (1.0,),
          "seconds": (1.0,)}


def tol(printed: str) -> float:
    """Half a unit in the last printed digit, on the printed power of ten (1.5e-4 -> 0.05e-4)."""
    if word_num(printed) is not None:
        return abs(word_num(printed)) * 0.08 + 1e-9         # words are approximate ("a fifth")
    return 0.5 * 10 ** (exponent(printed) - decimals(printed)) * (1 + 1e-9) + 1e-15


def value(printed: str):
    v = num(printed)
    return v if v is not None else word_num(printed)


def value_ok(printed: str, comparator: str, q: dict) -> bool:
    """The printed value equals the key value at the printed precision, on any scale the unit allows (a fraction may
    be printed as a percent). A difference may be printed without its sign ("drops 3.2 points")."""
    v = value(printed)
    if v is None:
        return False
    pct = "%" in printed
    signless = "difference" in str(q.get("statistic", "")) or q.get("unit") == "points"
    for s in SCALES.get(q.get("unit", "ratio"), (1.0,)):
        if pct and s == 1.0 and q.get("unit") in ("fraction", "points"):
            continue                                   # 92.6% is never the fraction 92.6
        x = q["value"] * s
        if comparator == "<" and x < v + tol(printed):
            return True
        if comparator == ">" and x > v - tol(printed):
            return True
        if comparator == "~" and abs(x - v) <= max(2 * tol(printed), abs(v) * 0.05):
            return True
        if comparator == "=" and (abs(x - v) <= tol(printed) or (signless and abs(abs(x) - abs(v)) <= tol(printed))):
            return True
    return False


def same_identity(n: dict, q: dict) -> bool:
    """Every field the paper states agrees with the key (unstated fields are free)."""
    for f in FIELDS:
        a = (n.get(f) or "").strip()
        if not a or a == "other":
            if a == "other" and f in ("dataset", "method"):
                return False
            continue
        b = str(q.get(f, "") or "")
        if f == "statistic" and a.startswith("p-value") and b.startswith("p-value"):
            if a != "p-value" and a != b:
                return False
            continue
        if a != b:
            return False
    return True


def stated(n: dict) -> int:
    return sum(1 for f in FIELDS if (n.get(f) or "").strip() not in ("", "other"))


def derived_ok(n: dict, key: dict) -> bool:
    """Relative change, ratio or difference of two key means that share dataset, condition and metric. Never for
    p-values or numbers too small to be told apart from chance."""
    v = value(n["printed"])
    if v is None or "p-value" in (n.get("statistic") or "") or abs(v) < 0.01:
        return False
    ds = (n.get("dataset") or "").strip()
    if not ds or ds == "other":
        return False                              # a derived value needs to say what it is about
    means = [q for q in key["quantities"] if q.get("dataset") == ds
             and q.get("statistic") in ("mean", "as reported") and q.get("unit") in ("fraction", "count", "ratio")
             and (not (n.get("condition") or "").strip() or n.get("condition") in ("other", q.get("condition")))]
    if len(means) > 400:
        return False
    pct = "%" in n["printed"]
    t = tol(n["printed"])
    for a, b in itertools.permutations(means, 2):
        if (a.get("metric"), a.get("dataset"), a.get("condition")) != (b.get("metric"), b.get("dataset"),
                                                                        b.get("condition")) and \
                (a.get("dataset"), a.get("condition"), a.get("method")) != (b.get("dataset"), b.get("condition"),
                                                                             b.get("method")):
            continue
        if b["value"] == 0:
            continue
        cands = [(a["value"] - b["value"]) / b["value"] * (100 if pct else 1), a["value"] / b["value"],
                 (a["value"] - b["value"]) * (100 if (pct or a.get("unit") == "fraction") else 1)]
        if any(abs(c - v) <= t for c in cands):
            return True
    return False


def match_number(n: dict, key: dict) -> dict:
    out = dict(n)
    printed, comp = n.get("printed", ""), n.get("comparator", "=")
    v = value(printed)
    if word_num(printed) is not None and comp == "=":
        comp = "~"
    if v is None:
        out["verdict"] = "unparsed"
        return out
    if n.get("kind") == "setup":
        ok = any(abs(float(s["value"]) * k - v) <= tol(printed) for s in key.get("setup", [])
                 for k in ((1.0, 100.0) if isinstance(s["value"], float) and s["value"] <= 1 else (1.0,))
                 if isinstance(s["value"], (int, float)))
        out["verdict"] = "supported" if ok else "not checkable"
        return out
    if n.get("kind") == "other":
        out["verdict"] = "ignored"
        return out
    Q = key["quantities"]
    same = [q for q in Q if same_identity(n, q)]
    hit = [q for q in same if value_ok(printed, comp, q)]
    if hit and stated(n) >= 2:
        out["verdict"], out["key_ids"] = "supported", [q["id"] for q in hit[:3]]
        return out
    anywhere = [q for q in Q if value_ok(printed, comp, q)]
    no_stat = {**n, "statistic": ""}
    if not hit and stated(no_stat) >= 2:          # right quantity, statistic named differently ("ratio of means")
        loose = [q for q in Q if same_identity(no_stat, q) and value_ok(printed, comp, q)]
        if loose:
            out["verdict"], out["key_ids"] = "supported", [q["id"] for q in loose[:3]]
            out["note"] = "statistic named differently"
            return out
    if hit:                                                   # identity barely stated: a match, but weakly placed
        common = float(v).is_integer() and abs(v) < 20
        out["verdict"] = "unclear" if common and len(anywhere) > 3 else "supported"
        out["key_ids"] = [q["id"] for q in hit[:3]]
        return out
    if derived_ok(n, key):
        out["verdict"] = "derived"
        return out
    if anywhere:
        out["verdict"], out["key_ids"] = "misattributed", [q["id"] for q in anywhere[:3]]
        if float(v).is_integer() and abs(v) < 20 and stated(n) < 2:
            out["verdict"] = "unclear"
        return out
    out["verdict"] = "unsupported"
    return out


def match_all(extracted: dict, key: dict) -> list[dict]:
    return [match_number(n, key) for n in extracted.get("numbers", [])]


def text_table(matched: list[dict], tables: dict[str, str]) -> list[dict]:
    """Every prose number attributed to a table must appear among that table's cells (at its printed precision)."""
    from common import num as _num
    import re
    out = []
    for n in matched:
        t = (n.get("attributed_to") or "").strip()
        if n.get("where") in ("table",) or not (t.lower().startswith("table") or t.startswith(("tab:", "\\ref{tab"))):
            continue
        tex = tables.get(t.title()) or tables.get(t) or tables.get(re.sub(r"^\\ref\{|\}$", "", t))
        v = value(n.get("printed", ""))
        if tex is None or v is None:
            out.append({**n, "table_verdict": "table not found"})
            continue
        cells = [_num(c) for c in re.findall(r"[-+]?\d*\.?\d+", tex.replace("{,}", ""))]
        ok = any(c is not None and (abs(c - v) <= tol(n["printed"]) or abs(c * 100 - v) <= tol(n["printed"])
                                    or abs(c - v * 100) <= 0.5) for c in cells)
        out.append({**n, "table_verdict": "in table" if ok else "not in table"})
    return out


def summary(matched: list[dict]) -> dict:
    from collections import Counter
    c = Counter(n["verdict"] for n in matched)
    res = [n for n in matched if n.get("kind") == "result"]
    return {"numbers": len(matched), "result_numbers": len(res), "verdicts": dict(c),
            "errors": c.get("misattributed", 0) + c.get("unsupported", 0),
            "error_rate": round((c.get("misattributed", 0) + c.get("unsupported", 0)) / max(len(res), 1), 4)}


_ = math
