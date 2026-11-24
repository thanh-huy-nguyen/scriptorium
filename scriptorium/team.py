"""The specialist stages added to the core pipeline: each gives one agent (or one per section) a narrow job and checks
its output file in code before anything downstream uses it.

    experiments   experimentalist  setup facts quoted verbatim from configs and code       (.scriptorium/setup.json)
    stats         statistician     a paired test per comparison, verdict matches p-value   (.scriptorium/stats.json)
    notation      terminologist    canonical names, abbreviations, symbols                 (.scriptorium/notation.json)
    audit         auditor          every claim sentence checked against the ledger         (.scriptorium/audit.json)
    polish        line editors     one per section, in parallel; every flagged sentence must change
    fit           typesetter       overfull lines and the page limit, only when the build reports them
    chair<r>      area chair       the reviews merged into a ranked list of changes        (reviews/<round>_meta.json)
    package       (code)           the arXiv bundle in .scriptorium/dist/
"""
from __future__ import annotations

import json
import re
import shutil
import tarfile
from pathlib import Path

from . import consistency, latex, lint, notation, state
from . import stages as S
from .config import Config
from .runner import Task

VERDICTS = ("ok", "overclaim", "unsupported", "mismatch", "unclear")


def _ws(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip()


def _jsonfile(p: Path) -> tuple[dict | None, list[str]]:
    if not p.exists():
        return None, [f"{p.relative_to(p.parents[1]) if len(p.parents) > 1 else p} is missing"]
    try:
        d = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        return None, [f"{p.name} is not valid JSON: {e}"]
    return (d, []) if isinstance(d, dict) else (None, [f"{p.name} must hold a JSON object"])


# ---------------------------------------------------------------------------------------------------------------------
# Discovery team

class Experiments(S.Stage):
    max_fix = 2

    def tasks(self, cfg):
        return [Task("experimentalist", "setup", S.context(cfg) + (
            "Task: extract the experimental setup from the repository's code and configs into .scriptorium/setup.json, "
            "as your instructions describe. Every fact quotes the exact text of the file it comes from. Then run "
            "`scriptorium validate .scriptorium/setup.json` and fix every problem."))]

    def validate(self, cfg):
        return setup_problems(cfg)

    def after(self, cfg):
        d = S.read_json(cfg.work / "setup.json") or {}
        lines = ["# Experimental setup (each fact quoted from its source file)\n"]
        for topic in sorted({f.get("topic", "other") for f in d.get("facts", [])}):
            lines.append(f"## {topic}\n")
            for f in d.get("facts", []):
                if f.get("topic", "other") == topic:
                    lines.append(f"- {f.get('text')} (`{f.get('source')}`: \"{f.get('quote')}\")")
            lines.append("")
        if d.get("gaps"):
            lines += ["## Not found in the repository\n"] + [f"- {g}" for g in d["gaps"]]
        (cfg.work / "setup.md").write_text("\n".join(lines) + "\n")


def setup_problems(cfg: Config) -> list[str]:
    d, errs = _jsonfile(cfg.work / "setup.json")
    if d is None:
        return errs
    facts = d.get("facts") or []
    if len(facts) < 5:
        errs.append(f"setup.json lists {len(facts)} facts; cover data, splits, models, training, evaluation and "
                    "hardware where the repository states them")
    ids = [f.get("id") for f in facts]
    if len(set(ids)) != len(ids):
        errs.append("fact ids must be unique")
    root = cfg.root.resolve()
    for f in facts:
        fid = f.get("id", "?")
        for k in ("id", "topic", "text", "source", "quote"):
            if not f.get(k):
                errs.append(f"fact {fid}: missing `{k}`")
        src = f.get("source")
        if not src:
            continue
        p = (root / src).resolve()
        if root not in p.parents or not p.is_file():
            errs.append(f"fact {fid}: source {src!r} is not a file in the repository")
            continue
        if p.is_relative_to(cfg.paper.resolve()) or p.is_relative_to(cfg.work.resolve()):
            errs.append(f"fact {fid}: source must be the repository's own code or configs, not paper/ or notes")
            continue
        try:
            body = _ws(p.read_text(errors="replace"))
        except OSError:
            body = ""
        if f.get("quote") and _ws(f["quote"]) not in body:
            errs.append(f"fact {fid}: the quote {f['quote'][:80]!r} does not appear in {src}; copy it exactly")
    return errs


class Stats(S.Stage):
    max_fix = 2

    def tasks(self, cfg):
        return [Task("statistician", "stats", S.context(cfg) + (
            "Task: for every comparison and trend the paper could claim, add the statistical test (and the 95% "
            "interval of the difference for the headline ones) as recipes in paper/sources.py, run `scriptorium "
            "numbers`, then record every comparison in .scriptorium/stats.json as your instructions describe. Run "
            "`scriptorium validate .scriptorium/stats.json` and fix every problem."))]

    def collect(self, cfg):
        S.refresh_numbers(cfg)

    def validate(self, cfg):
        return S.Evidence("evidence").validate(cfg) + stats_problems(cfg)

    def after(self, cfg):
        d = S.read_json(cfg.work / "stats.json") or {}
        nums = S.good_numbers(cfg)
        lines = ["# Statistical tests\n", "| comparison | setting | test | p | verdict |", "|---|---|---|---|---|"]
        for c in d.get("comparisons", []):
            p = nums.get(c.get("test_key") or "", {}).get("value")
            lines.append(f"| {c.get('a')} vs {c.get('b')} | {c.get('setting', '')} | `{c.get('test_key') or '-'}` | "
                         f"{'' if p is None else f'{p:.3g}'} | {c.get('verdict')} |")
        (cfg.work / "stats.md").write_text("\n".join(lines) + "\n")


def stats_problems(cfg: Config) -> list[str]:
    d, errs = _jsonfile(cfg.work / "stats.json")
    if d is None:
        return errs
    nums = S.good_numbers(cfg)
    comps = d.get("comparisons") or []
    if not comps:
        errs.append("stats.json lists no comparisons; record every comparison the paper could make, including "
                    "untestable ones")
    for c in comps:
        cid = c.get("id", "?")
        v = c.get("verdict")
        if v not in ("significant", "not significant", "untestable"):
            errs.append(f"comparison {cid}: verdict must be significant, not significant or untestable")
            continue
        if v == "untestable":
            if not c.get("why"):
                errs.append(f"comparison {cid}: say `why` it cannot be tested (e.g. one seed)")
            continue
        k = c.get("test_key")
        if k not in nums:
            errs.append(f"comparison {cid}: test_key {k!r} is not a working recipe")
            continue
        if "p-value" not in str(nums[k].get("means", "")).lower():
            errs.append(f"comparison {cid}: recipe {k} must say \"p-value\" in its means= and name the test")
        p = nums[k].get("value")
        if isinstance(p, (int, float)) and (p < 0.05) != (v == "significant"):
            errs.append(f"comparison {cid}: p = {p:.3g} but the verdict says {v!r}")
        for ck in ("ci_low_key", "ci_high_key"):
            if c.get(ck) and c[ck] not in nums:
                errs.append(f"comparison {cid}: {ck} {c[ck]!r} is not a working recipe")
    return errs


# ---------------------------------------------------------------------------------------------------------------------
# Story team

class Notation(S.Stage):
    max_fix = 2

    def tasks(self, cfg):
        return [Task("terminologist", "notation", S.context(cfg) + (
            "Task: fix the paper's names and notation before anyone writes: write .scriptorium/notation.json as your "
            "instructions describe, from the outline, the ledger, the setup and the inventory. Run `scriptorium "
            "validate .scriptorium/notation.json` and fix every problem."))]

    def validate(self, cfg):
        return notation.validate(cfg)

    def after(self, cfg):
        notation.render_md(cfg)


# ---------------------------------------------------------------------------------------------------------------------
# Writing and checking teams

def section_files(cfg: Config) -> list[str]:
    return [s["file"] for s in S.outline(cfg).get("sections", []) if (cfg.paper / f"{s['file']}.tex").exists()]


class Audit(S.Stage):
    max_fix = 2

    def tasks(self, cfg):
        return [Task("auditor", "audit", S.context(cfg) + (
            "Task: audit every sentence of the paper that states a result, a comparison, a trend, a scope or a "
            "contribution against .scriptorium/ledger.md, .scriptorium/numbers.md and .scriptorium/stats.md. Write "
            ".scriptorium/audit.json as your instructions describe. Do not edit the paper. Run `scriptorium validate "
            ".scriptorium/audit.json` and fix every problem."))]

    def validate(self, cfg):
        return audit_problems(cfg)


def audit_problems(cfg: Config) -> list[str]:
    from . import ledger
    d, errs = _jsonfile(cfg.work / "audit.json")
    if d is None:
        return errs
    fs = d.get("findings") or []
    claims = set(ledger.claim_ids(cfg))
    texts = {f: _ws((cfg.paper / f"{f}.tex").read_text()) for f in section_files(cfg)}
    audited = set()
    for i, f in enumerate(fs, 1):
        file = str(f.get("file", "")).removesuffix(".tex")
        if file not in texts:
            errs.append(f"finding {i}: file {f.get('file')!r} is not a section of the paper")
            continue
        audited.add(file)
        if not f.get("quote") or _ws(f["quote"]) not in texts[file]:
            errs.append(f"finding {i}: the quote is not in {file}.tex; copy the sentence exactly from the source")
        if f.get("verdict") not in VERDICTS:
            errs.append(f"finding {i}: verdict must be one of {', '.join(VERDICTS)}")
        if f.get("claim") and claims and f["claim"] not in claims:
            errs.append(f"finding {i}: claim {f['claim']!r} is not a ledger claim id")
        if f.get("verdict") not in (None, "ok") and not f.get("fix"):
            errs.append(f"finding {i}: a {f.get('verdict')} finding needs a concrete `fix`")
    claimful = [s["file"] for s in S.outline(cfg).get("sections", []) if s.get("claims") and s["file"] in texts]
    for f in claimful:
        if f not in audited:
            errs.append(f"{f}.tex states ledger claims but has no findings; audit its claim sentences")
    return errs


def open_findings(cfg: Config, file: str | None = None) -> list[dict]:
    d = S.read_json(cfg.work / "audit.json") or {}
    return [f for f in d.get("findings") or [] if f.get("verdict") not in (None, "ok")
            and (file is None or str(f.get("file", "")).removesuffix(".tex") == file)]


class Polish(S.Stage):
    """One line editor per section, in parallel. Each fixes the audit's findings in its file, the notation and lint
    problems there, and tightens the prose; every flagged sentence must be gone from the file afterwards."""
    max_fix = 2

    def task_for(self, cfg, f, extra=""):
        from . import lit
        fnd = open_findings(cfg, f) + [dict(x, verdict=f"{x['verdict']} citation \\cite{{{x.get('key')}}}")
                                       for x in lit.open_citations(cfg, f)]
        flags = [x for x in lint.lint(cfg.paper) if x.startswith(f"{f}.tex")]
        notes = [x for x in notation.check_text(cfg) if x.startswith(f"{f}.tex")]
        items = ([f"- [{x['verdict']}] \"{x['quote']}\" -> {x['fix']}" for x in fnd] +
                 [f"- [lint] {x}" for x in flags] + [f"- [notation] {x}" for x in notes])
        todo = ("These sentences and problems must be fixed (a flagged sentence must not remain word for word):\n"
                + "\n".join(items)) if items else "The audit found no problem in this file."
        return Task("line_editor", f"polish-{f}", S.context(cfg) + (
            f"Task: line-edit paper/{f}.tex. {todo}\nThen tighten the prose as your instructions describe. Edit "
            f"only paper/{f}.tex. Run `scriptorium check paper/{f}.tex` and `scriptorium lint` before you finish."
            + extra))

    def tasks(self, cfg):
        return [self.task_for(cfg, f) for f in section_files(cfg)]

    def validate(self, cfg):
        from . import lit
        errs = []
        for x in lit.open_citations(cfg):
            f = str(x.get("file", "")).removesuffix(".tex")
            p = cfg.paper / f"{f}.tex"
            if p.exists() and x.get("quote") and _ws(x["quote"]) in _ws(p.read_text()):
                errs.append(f"{f}.tex: the {x['verdict']} citation of {x.get('key')} is unchanged: "
                            f"\"{x['quote'][:120]}\"")
        for x in open_findings(cfg):
            f = str(x.get("file", "")).removesuffix(".tex")
            p = cfg.paper / f"{f}.tex"
            if p.exists() and x.get("quote") and _ws(x["quote"]) in _ws(p.read_text()):
                errs.append(f"{f}.tex: the {x['verdict']} sentence is unchanged: \"{x['quote'][:120]}\"")
        return errs + S.checks(cfg)

    def fix_tasks(self, cfg, errors):
        bad = {f for f in section_files(cfg) if any(f in e for e in errors)} or set(section_files(cfg))
        msg = "\n\nThe checks found these problems. Fix the ones in your file:\n- " + "\n- ".join(errors)
        return [self.task_for(cfg, f, msg) for f in section_files(cfg) if f in bad]


class Fit(S.Stage):
    """The typesetter runs only when the build reports layout problems: the page limit or overfull lines."""
    max_fix = 2
    MAX_OVERFULL = 2

    def layout(self, cfg) -> list[str]:
        errs = S.checks(cfg, page_limit=True)
        b = S.read_json(cfg.work / "build.json") or {}
        src = b.get("overfull_in") or []
        tables = sorted({f for f in src if f.startswith("table_")})
        for t in tables:
            errs.append(f"{t}.tex runs into the margin: in .scriptorium/tables/{t[6:]}.json set \"width\": \"full\" "
                        "(both columns), or drop or merge columns; \"fit\": true shrinks it as a last resort")
        rest = [f for f in src if not f.startswith("table_")]
        if len(rest) > self.MAX_OVERFULL:
            errs.append(f"{len(rest)} overfull lines (text running into the margin) in "
                        f"{', '.join(sorted(set(rest)))}; see .scriptorium/logs/build.log")
        return errs

    def tasks(self, cfg):
        errs = self.layout(cfg)
        if not errs:
            return []
        out = []
        tab = [e for e in errs if e.startswith("table_")]
        other = [e for e in errs if not e.startswith("table_")]
        for e in tab:
            tid = e.split(".tex", 1)[0][6:]
            out.append(Task("tablesetter", f"fit-table-{tid}", S.context(cfg) + (
                f"Task: table `{tid}` is too wide for the page: {e}. Edit .scriptorium/tables/{tid}.json and run "
                f"`scriptorium table {tid}`, then `scriptorium build` to check it fits. Keep every number.")))
        if other:
            out.append(Task("typesetter", "fit", S.context(cfg) + (
                "Task: fix the layout problems the build reports, without changing what the paper says:\n- "
                + "\n- ".join(other) + "\nRun `scriptorium build` until it reports none.")))
        return out

    def fix_tasks(self, cfg, errors):
        return [Task(t.agent, t.label + "-fix", t.prompt, t.role) for t in self.tasks(cfg)]

    def validate(self, cfg):
        return self.layout(cfg)

    def on_fail(self, cfg, errors):
        """Layout problems left after the fixes go into the report; they never stop the paper."""
        return "continue"


# ---------------------------------------------------------------------------------------------------------------------
# Review team

class Chair(S.Stage):
    max_fix = 1

    def __init__(self, name: str, review_stage: str):
        super().__init__(name)
        self.review_stage = review_stage

    def out(self, cfg) -> Path:
        return cfg.work / "reviews" / f"{self.review_stage}_meta.json"

    def tasks(self, cfg):
        return [Task("chair", f"chair-{self.review_stage}", S.context(cfg) + (
            f"Task: you are the area chair. Read the reviews .scriptorium/reviews/{self.review_stage}_*.json, the "
            f"paper, and .scriptorium/ledger.md. Write the meta-review to .scriptorium/reviews/"
            f"{self.review_stage}_meta.json as your instructions describe. Do not edit the paper. Run `scriptorium "
            f"validate .scriptorium/reviews/{self.review_stage}_meta.json` and fix every problem."))]

    def validate(self, cfg):
        return meta_problems(self.out(cfg))

    def on_fail(self, cfg, errors):
        return "continue"          # the reviser can still work from the raw reviews


def meta_problems(p: Path) -> list[str]:
    d, errs = _jsonfile(p)
    if d is None:
        return errs
    if d.get("decision") not in ("accept", "minor revision", "major revision", "reject"):
        errs.append("`decision` must be accept, minor revision, major revision or reject")
    ch = d.get("required_changes")
    if not isinstance(ch, list) or not ch:
        errs.append("`required_changes` must list the changes, most important first")
        ch = []
    for i, c in enumerate(ch, 1):
        if not isinstance(c, dict) or not c.get("change") or not c.get("where"):
            errs.append(f"required change {i} needs `change` and `where`")
        elif c.get("action") not in ("edit text", "add analysis from existing data", "narrow claim",
                                     "state as limitation"):
            errs.append(f"required change {i}: `action` must be edit text, add analysis from existing data, narrow "
                        "claim or state as limitation")
    return errs


# ---------------------------------------------------------------------------------------------------------------------
# Release

class Package(S.Stage):
    """Code only: the arXiv bundle (sources without comments, figures, bibliography, the compiled .bbl) and a copy of
    the PDF, in .scriptorium/dist/."""

    def after(self, cfg):
        build(cfg)

    def validate(self, cfg):
        b = S.read_json(cfg.work / "build.json") or {}
        return [] if b.get("ok") else ["the paper does not build; nothing to package"]


KEEP = (".tex", ".bib", ".bbl", ".sty", ".cls", ".bst", ".pdf", ".png", ".jpg", ".eps")


def build(cfg: Config) -> Path:
    dist = cfg.work / "dist"
    src = dist / "arxiv"
    if src.exists():
        shutil.rmtree(src)
    src.mkdir(parents=True)
    for p in sorted(cfg.paper.rglob("*")):
        rel = p.relative_to(cfg.paper)
        if not p.is_file() or p.suffix not in KEEP or rel.name == "main.pdf" or "__pycache__" in rel.parts:
            continue
        if rel.parts[0] == "figures" and p.suffix == ".png" and p.with_suffix(".pdf").exists():
            continue
        dst = src / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if p.suffix == ".tex":
            text = "\n".join(re.sub(r"(?<!\\)%.*", "%", ln) if not ln.lstrip().startswith("%") else ""
                             for ln in p.read_text().splitlines())
            dst.write_text(text + "\n")
        else:
            shutil.copy2(p, dst)
    tar = dist / "arxiv.tar.gz"
    with tarfile.open(tar, "w:gz") as t:
        t.add(src, arcname=".")
    if (cfg.paper / "main.pdf").exists():
        shutil.copy2(cfg.paper / "main.pdf", dist / "paper.pdf")
    return tar
