"""Tables set in code from recipes, so no table ever holds a typed number.

An agent writes a spec to .scriptorium/tables/<id>.json; `scriptorium table <id>` renders paper/table_<id>.tex:

    {"caption": "Test accuracy (%) at 40% label noise, mean and sd over 5 seeds.",
     "label": "tab:main",
     "columns": ["Method", "Digits", "Wine"],
     "rows": [
       {"cells": [{"text": "Cross-entropy"}, {"key": "acc_dg_40_ce_mean", "sd": "acc_dg_40_ce_sd"},
                  {"key": "acc_wi_40_ce_mean", "sd": "acc_wi_40_ce_sd"}]},
       {"cells": [{"text": "Loss filter (ours)"}, {"key": "acc_dg_40_filter_mean", "sd": "acc_dg_40_filter_sd"},
                  {"key": "acc_wi_40_filter_mean", "sd": "acc_wi_40_filter_sd"}], "ours": true}],
     "best": {"1": "max", "2": "max"},
     "decimals": 1,
     "rule_after": [0]}

Every cell holds a value: a table with an empty cell, a dash or a missing key is refused. The best value in each
column named in `best` is bold. Numbers carry their \\src tags, so PaperAnchor checks them like any other number.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .config import Config

ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
EMPTY_RE = re.compile(r"^\s*(-+|--|---|–|—|n/?a|N/?A|)\s*$")


def spec_path(cfg: Config, tid: str) -> Path:
    return cfg.work / "tables" / f"{tid}.json"


def out_path(cfg: Config, tid: str) -> Path:
    return cfg.paper / f"table_{tid}.tex"


def _fmt(v: float, dec: int) -> str:
    return f"{v:,.{dec}f}"


def render(cfg: Config, tid: str, numbers: dict) -> tuple[str | None, list[str]]:
    errs: list[str] = []
    if not ID_RE.match(tid):
        return None, [f"table id {tid!r} must be lowercase letters, digits and _"]
    try:
        spec = json.loads(spec_path(cfg, tid).read_text())
    except (OSError, json.JSONDecodeError) as e:
        return None, [f".scriptorium/tables/{tid}.json: {e}"]
    cols = spec.get("columns") or []
    rows = spec.get("rows") or []
    if not cols or not rows:
        return None, [f"table {tid}: needs `columns` and `rows`"]
    dec_default = int(spec.get("decimals", 1))
    vals: list[list[float | None]] = []
    for ri, r in enumerate(rows):
        cells = r.get("cells") or []
        if len(cells) != len(cols):
            errs.append(f"table {tid}, row {ri + 1}: {len(cells)} cells for {len(cols)} columns")
            continue
        rv: list[float | None] = []
        for ci, c in enumerate(cells):
            if "key" in c:
                n = numbers.get(c["key"])
                if not n or "value" not in n or n.get("error"):
                    errs.append(f"table {tid}, row {ri + 1}, column {cols[ci]!r}: {c['key']!r} is not a working recipe")
                    rv.append(None)
                    continue
                if c.get("sd") and (c["sd"] not in numbers or "value" not in numbers[c["sd"]]):
                    errs.append(f"table {tid}, row {ri + 1}: sd key {c['sd']!r} is not a working recipe")
                rv.append(float(numbers[c["key"]]["value"]))
            else:
                if EMPTY_RE.match(str(c.get("text", ""))):
                    errs.append(f"table {tid}, row {ri + 1}, column {cols[ci]!r}: empty or placeholder cell; "
                                "restructure the table so every cell holds a value")
                if re.search(r"\d+\.\d+|\d{2,}%", str(c.get("text", ""))):
                    errs.append(f"table {tid}, row {ri + 1}, column {cols[ci]!r}: a typed number in a text cell; "
                                "use a recipe key")
                rv.append(None)
        vals.append(rv)
    if errs:
        return None, errs
    best_cells: set[tuple[int, int]] = set()
    for ci_s, how in (spec.get("best") or {}).items():
        ci = int(ci_s)
        col = [(ri, v[ci]) for ri, v in enumerate(vals) if v[ci] is not None]
        if col:
            target = (max if how == "max" else min)(v for _, v in col)
            best_cells |= {(ri, ci) for ri, v in col if v == target}
    align = spec.get("align") or ("l" + "c" * (len(cols) - 1))
    env = "table*" if spec.get("width") == "full" else "table"
    fit = bool(spec.get("fit"))
    lines = [f"\\begin{{{env}}}[t]", "\\centering", "\\small", f"\\caption{{{spec.get('caption', '')}}}",
             f"\\label{{{spec.get('label', 'tab:' + tid)}}}"] + (["\\resizebox{\\linewidth}{!}{%"] if fit else []) + [
             f"\\begin{{tabular}}{{{align}}}", "\\toprule", " & ".join(cols) + " \\\\", "\\midrule"]
    after = set(spec.get("rule_after") or [])
    for ri, r in enumerate(rows):
        out = []
        for ci, c in enumerate(r["cells"]):
            if "key" in c:
                dec = int(c.get("decimals", dec_default))
                v = numbers[c["key"]]["value"]
                s = _fmt(float(v), dec)
                cell = (f"\\textbf{{{s}}}" if (ri, ci) in best_cells else s) + f"\\src{{{c['key']}}}"
                if c.get("sd"):
                    cell += f" $\\pm$ {_fmt(float(numbers[c['sd']]['value']), dec)}\\src{{{c['sd']}}}"
            else:
                cell = str(c.get("text"))
            out.append(cell)
        lines.append(" & ".join(out) + " \\\\")
        if ri in after:
            lines.append("\\midrule")
    lines += ["\\bottomrule", "\\end{tabular}"] + (["}"] if fit else []) + [f"\\end{{{env}}}", ""]
    return "\n".join(lines), []


def build(cfg: Config, numbers: dict, ids: list[str] | None = None) -> list[str]:
    """Render the given tables (all specs when None). Returns problems."""
    d = cfg.work / "tables"
    ids = ids or sorted(p.stem for p in d.glob("*.json")) if d.exists() else (ids or [])
    errs = []
    for tid in ids:
        tex, e = render(cfg, tid, numbers)
        errs += e
        if tex:
            out_path(cfg, tid).write_text(tex)
    return errs
