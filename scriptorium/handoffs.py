"""Typed handoffs: every file one agent hands to the next has a checker in code.

`scriptorium validate PATH` runs the checker for a handoff file, so an agent can check its own output before it
finishes; the stage runs the same checker before the next agent starts. Each checker returns a list of problems.

    .scriptorium/inventory.md          long enough to be a real survey
    .scriptorium/setup.json            team.setup_problems (every fact quoted from its source file)
    .scriptorium/stats.json            team.stats_problems (verdicts match the p-values)
    .scriptorium/notation.json         notation.validate
    .scriptorium/audit.json            team.audit_problems
    .scriptorium/reviews/<s>_meta.json team.meta_problems
    .scriptorium/ledger.json           ledger.validate (claims, scope, evidence keys)
    .scriptorium/pitches/<f>.json      contest.pitch_problems
    .scriptorium/outline.json          stages.Outline.validate
    .scriptorium/tables/<id>.json      tables.build
    .scriptorium/reviews/<s>_<p>.json  review_problems
"""
from __future__ import annotations

import json
from pathlib import Path

from .config import Config

SEVERITIES = ("major", "minor")


def _json(p: Path) -> tuple[dict | None, list[str]]:
    if not p.exists():
        return None, [f"{p.name} is missing"]
    try:
        d = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        return None, [f"{p.name} is not valid JSON: {e}"]
    if not isinstance(d, dict):
        return None, [f"{p.name} must hold a JSON object"]
    return d, []


def review_problems(p: Path) -> list[str]:
    r, errs = _json(p)
    if r is None:
        return errs
    n = p.name
    if not isinstance(r.get("overall"), (int, float)) or not 1 <= r["overall"] <= 10:
        errs.append(f"{n} needs a numeric `overall` score (1 to 10)")
    if not isinstance(r.get("summary"), str) or not r["summary"].strip():
        errs.append(f"{n}: `summary` must say in a few sentences what the paper claims and how well it supports it")
    ws = r.get("weaknesses")
    if not isinstance(ws, list):
        errs.append(f"{n}: `weaknesses` must be a list")
        ws = []
    for i, w in enumerate(ws):
        if not isinstance(w, dict) or not w.get("issue"):
            errs.append(f"{n}: weakness {i + 1} needs an `issue`")
            continue
        if str(w.get("severity", "")).lower() not in SEVERITIES:
            errs.append(f"{n}: weakness {i + 1} needs `severity` major or minor")
    return errs


def validate(cfg: Config, path: str | Path) -> list[str]:
    """Check one handoff file by its location. Unknown files return a single problem saying so."""
    from . import contest, ledger, stages
    from . import tables as T
    p = Path(path)
    p = (cfg.root / p).resolve() if not p.is_absolute() else p.resolve()
    try:
        rel = p.relative_to(cfg.work.resolve())
    except ValueError:
        return [f"{path}: not a handoff file (handoffs live in .scriptorium/)"]
    parts = rel.parts
    nums = stages.read_json(cfg.work / "numbers.json") or {}
    from . import notation, team
    if parts == ("setup.json",):
        return team.setup_problems(cfg)
    if parts == ("stats.json",):
        return team.stats_problems(cfg)
    if parts == ("notation.json",):
        return notation.validate(cfg)
    if parts == ("audit.json",):
        return team.audit_problems(cfg)
    if len(parts) == 2 and parts[0] == "reviews" and p.name.endswith("_meta.json"):
        return team.meta_problems(p)
    if parts == ("inventory.md",):
        return stages.Scout("scout").validate(cfg)
    if parts == ("ledger.json",):
        return ledger.validate(cfg, nums, [], [])
    if parts == ("outline.json",):
        return stages.Outline("outline").validate(cfg)
    if len(parts) == 2 and parts[0] == "pitches" and p.suffix == ".json":
        return contest.pitch_problems(cfg, p.stem)
    if len(parts) == 2 and parts[0] == "tables" and p.suffix == ".json":
        return T.build(cfg, nums, [p.stem])
    if len(parts) == 2 and parts[0] == "reviews" and p.suffix == ".json":
        return review_problems(p)
    return [f"{rel}: no checker for this file"]
