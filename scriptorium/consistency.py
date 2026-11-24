"""The code-first consistency pass: checks across the whole paper that need no model.

Errors (the stage fails until fixed):
- a float or table is defined but never referenced, or a reference has no label;
- "significant" or "significantly" in a sentence that prints a p-value recipe whose value is 0.05 or more;
- a \\src key that is not a working recipe (PaperAnchor reports this too, with more detail).

Warnings (handed to the editor and the red team):
- a number in the abstract or introduction that the results, tables or figures never show;
- sweeping scope words (all, every, always, consistently, universally, any) in the abstract, introduction or
  conclusion;
- "significant(ly)" with no p-value recipe in the paper at all;
- "first" or "novel" claims, which the novelty examiner must back.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import ledger
from .config import Config

SRC_RE = re.compile(r"\\src\{([^}]*)\}")
LABEL_RE = re.compile(r"\\label\{((?:fig|tab):[^}]*)\}")
REF_RE = re.compile(r"\\(?:ref|cref|Cref|autoref)\{([^}]*)\}")
SWEEP_RE = re.compile(r"\b(all|every|always|consistently|universally|any)\b", re.I)
SIGNIF_RE = re.compile(r"\bsignifican(t|tly|ce)\b", re.I)
NEG_RE = re.compile(r"(\b(not|no|nor|non|without|lacks?|fail(s|ed)? to reach|never)\b|n't\b|\bin)[\s-]*"
                    r"(\w+[\s-]+){0,2}$", re.I)


def significance_claims(s: str) -> tuple[int, int]:
    """(positive, negated) uses of "significant" in a sentence: "not significant" and "non-significant" are negated."""
    pos = neg = 0
    for m in SIGNIF_RE.finditer(s):
        before = s[max(0, m.start() - 40):m.start()]
        if NEG_RE.search(before) or re.search(r"\bin$", before, re.I) or s[max(0, m.start() - 2):m.start()].lower() == "in":
            neg += 1
        else:
            pos += 1
    return pos, neg
FIRST_RE = re.compile(r"\b(the first|first to|novel|unprecedented)\b", re.I)


def _strip(t: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", t)


def sentences(t: str) -> list[str]:
    t = re.sub(r"\s+", " ", _strip(t))
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", t) if s.strip()]


def files(cfg: Config) -> dict[str, str]:
    return {p.name: _strip(p.read_text()) for p in sorted(cfg.paper.glob("*.tex")) if p.name != "main.tex"}


def front(name: str) -> bool:
    return name == "abstract.tex" or name.startswith("01_")


def check(cfg: Config, numbers: dict) -> tuple[list[str], list[str]]:
    from . import notation
    fs = files(cfg)
    good = {k for k, v in numbers.items() if isinstance(v, dict) and "value" in v and not v.get("error")}
    errs, warns = [], []
    alltext = "\n".join(fs.values())
    labels = set(LABEL_RE.findall(alltext))
    refs = {r.strip() for grp in REF_RE.findall(alltext) for r in grp.split(",")}
    for lab in sorted(labels):
        if lab not in refs:
            errs.append(f"{lab} is defined but never referenced in the text")
    for r in sorted(refs):
        if r.startswith(("fig:", "tab:")) and r not in labels:
            errs.append(f"\\ref{{{r}}} has no matching \\label")
    pkeys = {k for k in good if ledger.is_pvalue(numbers[k])}
    body_keys = set()
    for name, t in fs.items():
        if not front(name):
            body_keys |= set(SRC_RE.findall(t))
    for name, t in fs.items():
        for k in SRC_RE.findall(t):
            if k not in good:
                errs.append(f"{name}: \\src{{{k}}} is not a working recipe")
        for s in sentences(t):
            pos, neg = significance_claims(s) if SIGNIF_RE.search(s) else (0, 0)
            if pos or neg:
                ps = [k for k in SRC_RE.findall(s) if k in pkeys]
                if pos and any(float(numbers[k]["value"]) >= 0.05 for k in ps):
                    errs.append(f"{name}: calls a result significant next to p >= 0.05: {s[:140]}")
                elif neg and not pos and ps and all(float(numbers[k]["value"]) < 0.05 for k in ps):
                    warns.append(f"{name}: says not significant next to p < 0.05: {s[:120]}")
                elif pos and not pkeys:
                    warns.append(f"{name}: says significant but the paper has no p-value recipe: {s[:120]}")
            if (front(name) or name.endswith(("conclusion.tex", "discussion.tex"))) and SWEEP_RE.search(s):
                warns.append(f"{name}: sweeping scope word '{SWEEP_RE.search(s).group(0)}': {s[:120]}")
            if FIRST_RE.search(s):
                warns.append(f"{name}: priority or novelty claim to back with the novelty check: {s[:120]}")
        if front(name):
            for k in SRC_RE.findall(t):
                if k in good and k not in body_keys:
                    warns.append(f"{name}: \\src{{{k}}} appears up front but never in the results, tables or figures")
    errs += [f"notation: {e}" for e in notation.check_text(cfg)]
    try:
        import json as _j
        planned = [f["id"] for f in (_j.loads((cfg.work / "outline.json").read_text()).get("figures") or [])
                   if f.get("id")]
    except (OSError, ValueError, KeyError, TypeError):
        planned = []
    for fid in planned:
        if not re.search(r"\\includegraphics(\[[^\]]*\])?\{figures/" + re.escape(fid) + r"(\.pdf|\.png)?\}", alltext):
            errs.append(f"figure {fid} is planned but never included (\\includegraphics{{figures/{fid}.pdf}})")
    return sorted(set(errs)), sorted(set(warns))


def write_report(cfg: Config, numbers: dict) -> Path:
    errs, warns = check(cfg, numbers)
    out = cfg.work / "consistency.md"
    lines = ["# Consistency pass", "", f"{len(errs)} error(s), {len(warns)} warning(s).", ""]
    if errs:
        lines += ["## Errors", ""] + [f"- {e}" for e in errs] + [""]
    if warns:
        lines += ["## Warnings (check each against the claim ledger)", ""] + [f"- {w}" for w in warns] + [""]
    out.write_text("\n".join(lines))
    return out
