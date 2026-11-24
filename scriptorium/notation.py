"""The paper's notation: one name per method, dataset and metric, abbreviations defined once, symbols with meanings.

The terminologist writes .scriptorium/notation.json:

    {"terms": [{"canonical": "LossFilter", "kind": "method", "definition": "...", "variants": ["Loss Filter", "loss-filter"]}],
     "abbreviations": [{"short": "CE", "long": "cross-entropy"}],
     "symbols": [{"symbol": "$\\tau$", "meaning": "the loss threshold"}]}

Code then holds the text to it: a listed variant may not appear anywhere in the paper, and an abbreviation used in the
body must be defined ("long (SHORT)") at or before its first use there.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .config import Config

KINDS = ("method", "dataset", "metric", "baseline", "task", "term")


def path(cfg: Config) -> Path:
    return cfg.work / "notation.json"


def load(cfg: Config) -> dict:
    try:
        d = json.loads(path(cfg).read_text())
        return d if isinstance(d, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def validate(cfg: Config) -> list[str]:
    if not path(cfg).exists():
        return [".scriptorium/notation.json is missing"]
    d = load(cfg)
    if not d:
        return [".scriptorium/notation.json is not a valid JSON object"]
    errs = []
    terms = d.get("terms") or []
    if len(terms) < 3:
        errs.append("list at least the method, the datasets, the baselines and the metrics under `terms`")
    canon = [str(t.get("canonical", "")) for t in terms]
    for t in terms:
        c = t.get("canonical")
        if not c:
            errs.append(f"term {t!r} needs `canonical`")
            continue
        if t.get("kind") not in KINDS:
            errs.append(f"term {c!r}: kind must be one of {', '.join(KINDS)}")
        if not t.get("definition"):
            errs.append(f"term {c!r} needs a one-line `definition`")
        for v in t.get("variants") or []:
            if v in canon:
                errs.append(f"term {c!r}: variant {v!r} is itself a canonical name")
            if v.lower() == c.lower() and v == c:
                errs.append(f"term {c!r}: a variant cannot equal the canonical name")
    if len(set(canon)) != len(canon):
        errs.append("canonical names must be unique")
    shorts = [a.get("short", "") for a in d.get("abbreviations") or []]
    for a in d.get("abbreviations") or []:
        if not a.get("short") or not a.get("long"):
            errs.append(f"abbreviation {a!r} needs `short` and `long`")
    if len(set(shorts)) != len(shorts):
        errs.append("each abbreviation is listed once")
    return errs


def _body(text: str) -> str:
    """Prose only: drop comments and the arguments of commands whose text is not prose (labels, refs, cites, files)."""
    t = re.sub(r"(?<!\\)%.*", "", text)
    t = re.sub(r"\\(sub)*section\*?(\[[^\]]*\])?\{[^}]*\}", " ", t)        # headings may use title case
    t = re.sub(r"\\(label|ref|cref|Cref|autoref|eqref|cite[a-zA-Z]*|input|include|includegraphics|src|url|href)"
               r"\*?(\[[^\]]*\])*\{[^}]*\}", " ", t)
    return t


def _word(s: str) -> re.Pattern:
    return re.compile(r"(?<![A-Za-z0-9-])" + re.escape(s) + r"(?![A-Za-z0-9-])")


def check_text(cfg: Config, order: list[str] | None = None) -> list[str]:
    """Problems in the paper's text against notation.json. `order` lists section files (no .tex) in reading order."""
    d = load(cfg)
    if not d:
        return []
    files = order or [p.stem for p in sorted(cfg.paper.glob("*.tex")) if p.name not in ("main.tex", "checklist.tex")]
    texts = {f: _body((cfg.paper / f"{f}.tex").read_text()) for f in files if (cfg.paper / f"{f}.tex").exists()}
    errs = []
    for t in d.get("terms") or []:
        for v in t.get("variants") or []:
            pat = _word(v)
            for f, body in texts.items():
                n = len(pat.findall(body))
                if n:
                    where = (f" (fix it in .scriptorium/tables/{f[6:]}.json and rerun `scriptorium table {f[6:]}`)"
                             if f.startswith("table_") else "")
                    errs.append(f"{f}.tex: {v!r} appears {n} time(s); the paper's name is {t.get('canonical')!r}"
                                + where)
    body_files = [f for f in files if f != "abstract" and f in texts]
    body = "\n".join(texts[f] for f in body_files)
    for a in d.get("abbreviations") or []:
        short, long_ = a.get("short", ""), a.get("long", "")
        if not short:
            continue
        uses = [m.start() for m in _word(short).finditer(body)]
        if not uses:
            continue
        dm = re.search(re.escape(long_) + r"\s*\(\s*" + re.escape(short) + r"\s*\)", body, re.I) if long_ else None
        if not dm:
            errs.append(f"abbreviation {short!r} is used but never defined in the body; write \"{long_} ({short})\" "
                        "at its first use")
        elif uses[0] < dm.start():
            errs.append(f"abbreviation {short!r} is used before it is defined; move \"{long_} ({short})\" to its "
                        "first use")
    return errs


def render_md(cfg: Config) -> None:
    d = load(cfg)
    lines = ["# Notation and names\n", "Use the canonical name every time; never a listed variant.\n",
             "| canonical | kind | definition | never write |", "|---|---|---|---|"]
    for t in d.get("terms") or []:
        lines.append(f"| {t.get('canonical')} | {t.get('kind')} | {t.get('definition')} | "
                     f"{', '.join(t.get('variants') or [])} |")
    if d.get("abbreviations"):
        lines += ["", "Abbreviations (define once in the body as \"long (SHORT)\" at first use, then use SHORT):", ""]
        lines += [f"- {a.get('short')}: {a.get('long')}" for a in d["abbreviations"]]
    if d.get("symbols"):
        lines += ["", "Symbols:", ""] + [f"- {s.get('symbol')}: {s.get('meaning')}" for s in d["symbols"]]
    (cfg.work / "notation.md").write_text("\n".join(lines) + "\n")
