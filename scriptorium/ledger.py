"""The claim ledger: every claim the paper may make, with its scope, evidence and strength.

.scriptorium/ledger.json, written by the claim cartographer and checked here:

    {"claims": [
      {"id": "filter_beats_ce_high_noise",
       "text": "At 40% symmetric label noise, the loss filter beats cross-entropy training on all three datasets.",
       "kind": "comparison",
       "scope": "digits, wine, breast cancer; 40% symmetric noise; 5 seeds",
       "evidence": {"numbers": ["acc_dg_40_filter_mean", "acc_dg_40_ce_mean"], "tests": ["p_dg_40_filter_vs_ce"],
                    "figures": ["noise_sweep"], "tables": ["main"]},
       "strength": "strong",
       "why": "Gains of 6 to 9 points, p < 0.001 on every dataset."}],
     "brief": [{"claim": "the filter is robust to any noise rate", "status": "narrowed",
                "ledger": ["filter_beats_ce_high_noise"], "why": "only 0 to 40% was run"}]}

Rules checked in code:
- every evidence key is a working recipe;
- a comparison or trend claim marked strong names a test key whose recipe is a p-value below 0.05 (a recipe whose
  `means` says "p-value"), so "better" always rests on a paired test;
- every claim in the brief is mapped: supported, narrowed or unsupported.
Writers may make only ledger claims that are not unsupported; weak claims are stated with their limits.
"""
from __future__ import annotations

import json
import re

from .config import Config

KINDS = ("result", "comparison", "trend", "method", "scope", "limitation", "contribution")
STRENGTHS = ("strong", "weak", "unsupported")
ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def path(cfg: Config):
    return cfg.work / "ledger.json"


def load(cfg: Config) -> dict:
    try:
        return json.loads(path(cfg).read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def is_pvalue(rec: dict) -> bool:
    return bool(re.search(r"p[- ]?value", str(rec.get("means", "")), re.I))


def validate(cfg: Config, numbers: dict, figures: list[str], tables: list[str]) -> list[str]:
    led = load(cfg)
    if not led:
        return [".scriptorium/ledger.json is missing or is not valid JSON"]
    claims = led.get("claims") or []
    errs: list[str] = []
    good = {k: v for k, v in numbers.items() if isinstance(v, dict) and "value" in v and not v.get("error")}
    ids = [c.get("id") for c in claims]
    if len(set(ids)) != len(ids):
        errs.append("claim ids must be unique")
    for c in claims:
        cid = c.get("id", "?")
        if not ID_RE.match(str(cid)):
            errs.append(f"claim id {cid!r} must be lowercase letters, digits and _")
        if c.get("kind") not in KINDS:
            errs.append(f"claim {cid}: kind must be one of {', '.join(KINDS)}")
        if c.get("strength") not in STRENGTHS:
            errs.append(f"claim {cid}: strength must be one of {', '.join(STRENGTHS)}")
        if not c.get("text") or not c.get("scope"):
            errs.append(f"claim {cid}: needs `text` and `scope`")
        ev = c.get("evidence") or {}
        for k in (ev.get("numbers") or []) + (ev.get("tests") or []):
            if k not in good:
                errs.append(f"claim {cid}: evidence key {k!r} is not a working recipe")
        for f in ev.get("figures") or []:
            if figures and f not in figures:
                errs.append(f"claim {cid}: figure {f!r} is not planned")
        for t in ev.get("tables") or []:
            if tables and t not in tables:
                errs.append(f"claim {cid}: table {t!r} has no spec in .scriptorium/tables/")
        if c.get("strength") == "strong" and c.get("kind") in ("result", "comparison", "trend") and not (
                ev.get("numbers") or ev.get("tests")):
            errs.append(f"claim {cid}: a strong {c.get('kind')} claim needs evidence keys")
        if c.get("strength") == "strong" and c.get("kind") in ("comparison", "trend"):
            tests = [k for k in ev.get("tests") or [] if k in good]
            ps = [(k, float(good[k]["value"])) for k in tests if is_pvalue(good[k])]
            if not ps:
                errs.append(f"claim {cid}: a strong {c['kind']} claim needs a test key whose recipe returns a "
                            "p-value (its `means` must say p-value), e.g. scriptorium_stats.paired_t_p")
            elif any(p >= 0.05 for _, p in ps):
                bad = ", ".join(f"{k} = {p:.3g}" for k, p in ps if p >= 0.05)
                errs.append(f"claim {cid}: marked strong but its test gives {bad}; mark it weak, or narrow it to the "
                            "settings where the test passes")
    if sum(c.get("strength") == "strong" for c in claims) < 2:
        errs.append("the ledger has fewer than 2 strong claims; a paper needs claims the data supports")
    for b in led.get("brief") or []:
        if b.get("status") not in ("supported", "narrowed", "unsupported"):
            errs.append(f"brief claim {str(b.get('claim'))[:60]!r}: status must be supported, narrowed or unsupported")
    return errs


def render_md(cfg: Config) -> str:
    led = load(cfg)
    lines = ["# Claim ledger", "", "The paper may make only these claims, at this scope. Strong claims can be stated "
             "directly; weak claims are stated with their limits; unsupported claims are never made.", ""]
    for c in led.get("claims") or []:
        ev = c.get("evidence") or {}
        keys = ", ".join(f"`{k}`" for k in (ev.get("numbers") or []) + (ev.get("tests") or []))
        lines.append(f"- **{c.get('id')}** ({c.get('kind')}, {c.get('strength')}): {c.get('text')}  ")
        lines.append(f"  Scope: {c.get('scope')}. Evidence: {keys or 'none'}"
                     + (f"; figures {', '.join(ev.get('figures'))}" if ev.get("figures") else "")
                     + (f"; tables {', '.join(ev.get('tables'))}" if ev.get("tables") else "") + ".")
    if led.get("brief"):
        lines += ["", "## Claims in the brief", ""]
        for b in led["brief"]:
            lines.append(f"- {b.get('claim')}: {b.get('status')}. {b.get('why', '')}")
    out = "\n".join(lines) + "\n"
    (cfg.work / "ledger.md").write_text(out)
    return out


def claim_ids(cfg: Config, usable_only: bool = True) -> list[str]:
    return [c["id"] for c in load(cfg).get("claims") or []
            if not usable_only or c.get("strength") != "unsupported"]
