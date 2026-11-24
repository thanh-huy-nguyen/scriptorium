"""The pipeline. Each stage prepares its inputs, hands agents their tasks, then checks the result in code.

Stages form a graph; a stage starts as soon as the stages it depends on are done, so independent teams work at the
same time (engine.py schedules them):

    scout -> { experiments | evidence -> stats } -> ledger -> story -> outline
          -> { notation | library | figures | tables } -> draft -> frame -> edit -> audit -> polish -> fit
          -> review0 -> (chair -> revise_r -> review_r)* -> final -> package

The specialist stages (experiments, stats, notation, audit, polish, fit, chair, package) live in team.py.

Agents do the reading and writing. Everything that can be checked without a model is checked here: recipes run,
the outline parses and names only numbers that exist, citations come from the bibliographic databases, the paper
compiles, every tagged number recomputes (PaperAnchor), and no agent touched the repository's data (the lock).
"""
from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from . import anchor, cite, consistency, contest, events, history, latex, ledger, lint, lock, state
from . import tables as T
from .config import TEMPLATES, Config
from .runner import Task

FILE_RE = re.compile(r"^(abstract|\d{2}_[a-z0-9_]+)$")
ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")


# ---------------------------------------------------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------------------------------------------------

def context(cfg: Config) -> str:
    return (
        f'Paper: "{cfg.title}" for {cfg.venue}, at most {cfg.page_limit} pages of main text (references excluded).\n'
        "The authors' brief is brief.md at the repository root. Shared notes live in .scriptorium/: inventory.md (what "
        "the repository holds), setup.md (the experimental setup, each fact quoted from its source file), numbers.md "
        "(every number the paper may print, with its recipe key), stats.md (the statistical test behind every "
        "comparison), ledger.md (every claim the paper may make, with its scope and strength), outline.json (the "
        "plan), notation.md (the one name for each method, dataset and metric, and the abbreviations), related.md "
        "(verified related work), style.md (how to write). Read the ones your task needs.\n"
        "You may create or edit files only in paper/ and .scriptorium/. Everything else in the repository is "
        "read-only data and code: never modify, create or delete files there.\n"
    )


def read_json(p: Path) -> dict | None:
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def outline(cfg: Config) -> dict:
    return read_json(cfg.work / "outline.json") or {}


def good_numbers(cfg: Config) -> dict:
    nums = read_json(cfg.work / "numbers.json") or {}
    return {k: v for k, v in nums.items() if k != "__module__" and "value" in v and "error" not in v}


def refresh_numbers(cfg: Config) -> dict:
    nums = anchor.numbers(cfg)
    (cfg.work / "numbers.json").write_text(json.dumps(nums, indent=1))
    (cfg.work / "numbers.md").write_text(
        "# Numbers the paper may print\n\nEach row is a recipe in paper/sources.py. Print a number with its key right "
        "after it, e.g. `81.8\\%\\src{acc}`; choose the precision in the text; the checker rounds the recipe's value "
        "to that precision. Values below are unrounded.\n\n" + anchor.numbers_table(nums) + "\n")
    return nums


def section_path(cfg: Config, sec: dict) -> Path:
    return cfg.paper / f"{sec['file']}.tex"


VAL_RE = re.compile(r"\\val(\[\d+\])?\{([^}]*)\}")


def val_problems(cfg: Config, files: list[str] | None = None) -> list[str]:
    """\\val prints nothing in the PDF; Scriptorium papers print digits followed by \\src{key}."""
    out = []
    paths = [Path(f) for f in files] if files else sorted(cfg.paper.glob("*.tex"))
    for p in paths:
        if p.name == "main.tex" or not p.exists():
            continue
        for i, line in enumerate(p.read_text().splitlines(), 1):
            for m in VAL_RE.finditer(re.sub(r"(?<!\\)%.*", "", line)):
                out.append(f"{p.name}:{i}: \\val{{{m.group(2)}}} prints nothing in the PDF; write the number in digits "
                           f"followed by \\src{{{m.group(2)}}} (value in .scriptorium/numbers.md)")
    return out


def checks(cfg: Config, files: list[str] | None = None, build: bool = True, page_limit: bool = False) -> list[str]:
    """The code-side checks shared by every writing stage."""
    errs: list[str] = val_problems(cfg, files)
    if (cfg.work / "tables").exists():
        errs += T.build(cfg, read_json(cfg.work / "numbers.json") or {})
    cerrs, _ = consistency.check(cfg, read_json(cfg.work / "numbers.json") or {})
    errs += [f"consistency: {e}" for e in cerrs]
    ok, out = anchor.check(cfg, *(files or []))
    if not ok:
        errs.append("numbers that do not recompute (PaperAnchor):\n" + out[-3000:])
    errs += cite.problems(cite.verify(cfg.root))
    if build:
        b = latex.build(cfg)
        (cfg.work / "build.json").write_text(json.dumps({"ok": b.ok, "pages": b.pages, "main_pages": b.main_pages,
                                                         "summary": b.summary()}, indent=1))
        errs += b.problems(cfg.page_limit if page_limit else None)
    return errs


def render_main(cfg: Config) -> None:
    """Write paper/main.tex from the template and the outline's section order (deterministic, never by an agent)."""
    tdir = TEMPLATES / "default" if cfg.template in ("", "default") else (cfg.root / cfg.template)
    tpl = (tdir / "main.tex").read_text()
    for f in tdir.iterdir():
        if f.name != "main.tex" and f.is_file() and not (cfg.paper / f.name).exists():
            shutil.copy2(f, cfg.paper / f.name)
    secs = [s for s in outline(cfg).get("sections", []) if s.get("file") != "abstract"]
    body = "\n".join(f"\\input{{{s['file']}}}" for s in secs)
    authors = " \\and ".join(cfg.authors) if cfg.authors else "Anonymous"
    tex = (tpl.replace("%%TITLE%%", outline(cfg).get("title") or cfg.title).replace("%%AUTHORS%%", authors)
           .replace("%%AFFILIATION%%", cfg.affiliation).replace("%%ABSTRACT%%", "\\input{abstract}")
           .replace("%%BODY%%", body))
    if "\\providecommand{\\src}" not in tex:
        tex = re.sub(r"(\\documentclass[^\n]*\n)", r"\1\\providecommand{\\src}[1]{}\n\\providecommand{\\val}[2][1]{}\n",
                     tex, count=1)
    (cfg.paper / "main.tex").write_text(tex)
    if not (cfg.paper / "refs.bib").exists():
        (cfg.paper / "refs.bib").write_text("")


# ---------------------------------------------------------------------------------------------------------------------
# Stage protocol
# ---------------------------------------------------------------------------------------------------------------------

@dataclass
class Stage:
    name: str
    max_fix: int = 1
    summary: str = ""
    deps: tuple[str, ...] = ()

    def before(self, cfg: Config) -> None:
        pass

    def tasks(self, cfg: Config) -> list[Task]:
        return []

    def collect(self, cfg: Config) -> None:
        """Deterministic work after the agents ran and before the checks."""

    def after(self, cfg: Config) -> None:
        """Deterministic work once the stage is accepted."""

    def validate(self, cfg: Config) -> list[str]:
        return []

    def fix_tasks(self, cfg: Config, errors: list[str]) -> list[Task]:
        """Default: give the same agents their task again, with what failed."""
        msg = "\n\nA previous attempt at this task left these problems. Fix them:\n- " + "\n- ".join(errors)
        return [Task(t.agent, t.label + "-fix", t.prompt + msg, t.role) for t in self.tasks(cfg)]

    def on_fail(self, cfg: Config, errors: list[str]) -> str:
        """What to do when fixes run out: 'stop' the run, or 'continue' (the stage handled it, e.g. by rollback)."""
        return "stop"


class Scout(Stage):
    def tasks(self, cfg):
        return [Task("scout", "scout", context(cfg) + (
            "Task: survey this repository and write .scriptorium/inventory.md. Cover the research question, the "
            "method and where it is implemented, the datasets, the baselines, every result file (path, format, what "
            "each field means, which runs it holds), the configs that set reported settings, existing figures, and "
            "anything the brief claims that you cannot find data for."))]

    def validate(self, cfg):
        p = cfg.work / "inventory.md"
        return [] if p.exists() and len(p.read_text().split()) > 80 else ["`.scriptorium/inventory.md` is missing or nearly empty"]


class Evidence(Stage):
    max_fix = 2

    def tasks(self, cfg):
        return [Task("evidence", "evidence", context(cfg) + (
            "Task: write paper/sources.py, one recipe for every number a paper about this work could print, using "
            ".scriptorium/inventory.md as the map. The statistician adds the statistical tests after you; you cover "
            "the values. Run `scriptorium numbers` until every recipe returns a value. "
            "Then write .scriptorium/evidence_notes.md: what the data supports, and every claim in brief.md that the "
            "data does not support."))]

    def collect(self, cfg):
        refresh_numbers(cfg)

    def validate(self, cfg):
        nums = read_json(cfg.work / "numbers.json") or {}
        if "__module__" in nums:
            return ["paper/sources.py fails as a whole: " + str(nums["__module__"].get("error", ""))[:600]]
        bad = [f"{k}: {v.get('error')}" for k, v in nums.items() if "error" in v or "value" not in v]
        errs = [f"recipe fails: {b}"[:300] for b in bad]
        if len(nums) - len(bad) < 3:
            errs.append(f"only {len(nums) - len(bad)} working recipes; a paper needs its main results covered")
        return errs


class Ledger(Stage):
    max_fix = 2

    def tasks(self, cfg):
        return [Task("cartographer", "ledger", context(cfg) + (
            "Task: build the claim ledger, .scriptorium/ledger.json: every claim a paper about this work could make, "
            "with its scope, evidence keys and strength, and the status of every claim in brief.md. The tests and "
            "their verdicts are in .scriptorium/stats.md; the setup in .scriptorium/setup.md. Run `scriptorium "
            "ledger` until it reports no problems. If a comparison needs a statistical test that has no recipe yet, "
            "add the recipe to paper/sources.py (see the statistics rules there) and run `scriptorium numbers`."))]

    def collect(self, cfg):
        refresh_numbers(cfg)

    def validate(self, cfg):
        return ledger.validate(cfg, read_json(cfg.work / "numbers.json") or {}, [], [])

    def after(self, cfg):
        ledger.render_md(cfg)


class Story(Stage):
    """Architects pitch competing storylines; the skim test and the selection panel pick one (contest.py)."""

    def before(self, cfg):
        (cfg.work / "pitches").mkdir(exist_ok=True)

    def tasks(self, cfg):
        return [Task("architect", f"pitch-{f}", context(cfg) + (
            f"Task: pitch the paper's storyline under the {f} framing. Write .scriptorium/pitches/{f}.json as your "
            "instructions describe, using only claims from .scriptorium/ledger.md."), role="architect")
            for f in contest.FRAMINGS]

    def validate(self, cfg):
        ok = [f for f in contest.FRAMINGS if not contest.pitch_problems(cfg, f)]
        if len(ok) >= 2:
            return []
        return [e for f in contest.FRAMINGS for e in contest.pitch_problems(cfg, f)]

    def fix_tasks(self, cfg, errors):
        bad = {f for f in contest.FRAMINGS if contest.pitch_problems(cfg, f)}
        return [t for t in super().fix_tasks(cfg, errors) if t.label.removeprefix("pitch-").removesuffix("-fix") in bad]

    def after(self, cfg):
        contest.select_story(cfg)


class Outline(Stage):
    max_fix = 2

    def tasks(self, cfg):
        return [Task("outliner", "outline", context(cfg) + (
            "Task: plan the paper and write .scriptorium/outline.json. The storyline is chosen: expand the pitch in "
            ".scriptorium/story.json (its title, insight, Figure 1, contributions and section plan) into the full "
            f"outline, keeping its framing. Budget about {cfg.page_limit * 480} words of "
            "prose in total across sections, which leaves room for figures and tables at this page limit. Every "
            "number a section will print must be a key in .scriptorium/numbers.md."))]

    def validate(self, cfg):
        o = read_json(cfg.work / "outline.json")
        if o is None:
            return [".scriptorium/outline.json is missing or is not valid JSON"]
        errs, nums = [], good_numbers(cfg)
        secs, figs, tabs = o.get("sections") or [], o.get("figures") or [], o.get("tables") or []
        claims = set(ledger.claim_ids(cfg))
        tab_ids = [t.get("id") for t in tabs]
        if not isinstance(o.get("storyline"), str) or len(o.get("storyline", "")) < 40:
            errs.append("`storyline` must state the problem, the key idea, why it works and what it changes")
        files, ids = [s.get("file", "") for s in secs], [s.get("id", "") for s in secs]
        if "abstract" not in files:
            errs.append('sections must include one with "file": "abstract"')
        for s in secs:
            sid = s.get("id", "?")
            if not FILE_RE.match(s.get("file", "")):
                errs.append(f"section {sid}: file must be 'abstract' or like '03_method'")
            if not ID_RE.match(sid):
                errs.append(f"section id {sid!r} must be lowercase letters, digits and _")
            if s.get("wave") not in (1, 2):
                errs.append(f"section {sid}: wave must be 1 (written first) or 2 (written after wave 1)")
            for k in s.get("numbers", []):
                if k not in nums:
                    errs.append(f"section {sid}: number key {k!r} is not a working recipe in numbers.md")
            for f in s.get("figures", []):
                if f not in [x.get("id") for x in figs]:
                    errs.append(f"section {sid}: figure {f!r} is not defined in `figures`")
            for t in s.get("tables", []):
                if not isinstance(t, str) or t not in tab_ids:
                    errs.append(f"section {sid}: table {t!r} is not defined in the top-level `tables`")
            for c in s.get("claims", []):
                if claims and c not in claims:
                    errs.append(f"section {sid}: claim {c!r} is not a usable claim in the ledger")
        for t in tabs:
            if not ID_RE.match(str(t.get("id", ""))):
                errs.append(f"table id {t.get('id')!r} must be lowercase letters, digits and _")
            if claims and t.get("claim") not in claims:
                errs.append(f"table {t.get('id')}: `claim` must be a usable ledger claim id")
            for k in t.get("numbers", []):
                if k not in nums:
                    errs.append(f"table {t.get('id')}: number key {k!r} is not a working recipe")
        for f in figs:
            if claims and f.get("claim") not in claims:
                errs.append(f"figure {f.get('id')}: `claim` must be a usable ledger claim id")
        strong = {c["id"] for c in ledger.load(cfg).get("claims", []) if c.get("strength") == "strong"}
        covered = {c for s in secs for c in s.get("claims", [])}
        if strong - covered:
            errs.append("strong ledger claims no section states: " + ", ".join(sorted(strong - covered)))
        if len(set(files)) != len(files) or len(set(ids)) != len(ids):
            errs.append("section ids and files must be unique")
        for f in figs:
            if not ID_RE.match(f.get("id", "")):
                errs.append(f"figure id {f.get('id')!r} must be lowercase letters, digits and _")
            if f.get("kind") not in ("plot", "diagram"):
                errs.append(f"figure {f.get('id')}: kind must be 'plot' or 'diagram'")
        if not o.get("related"):
            errs.append("`related` must list the topics the related work needs, each with search queries")
        return errs

    def after(self, cfg):
        if read_json(cfg.work / "outline.json"):
            render_main(cfg)


class Library(Stage):
    def tasks(self, cfg):
        return [Task("librarian", "library", context(cfg) + (
            "Task: build the bibliography for the topics in .scriptorium/outline.json (`related`), plus the "
            "datasets, baselines and tools named in .scriptorium/inventory.md. Find each paper with `scriptorium cite "
            "search`, add it with `scriptorium cite add`, and write .scriptorium/related.md."))]

    def validate(self, cfg):
        rep = cite.verify(cfg.root)
        errs = cite.problems(rep)
        n = len(cite.bib_entries(cfg.root))
        if n < 6:
            errs.append(f"paper/refs.bib holds {n} entries; find more of the work the paper builds on")
        if not (cfg.work / "related.md").exists():
            errs.append(".scriptorium/related.md is missing")
        return errs


class Figures(Stage):
    def tasks(self, cfg):
        out = []
        for f in outline(cfg).get("figures", []):
            out.append(Task("illustrator", f"figure-{f['id']}", context(cfg) + (
                f"Task: make figure `{f['id']}` as planned in .scriptorium/outline.json:\n{json.dumps(f, indent=1)}\n"
                f"Write paper/figures/{f['id']}.py, which reads the repository's data and saves "
                f"paper/figures/{f['id']}.pdf and paper/figures/{f['id']}.png. Run it with `scriptorium figure "
                f"paper/figures/{f['id']}.py`, look at the PNG, and fix what looks wrong. Then write "
                f".scriptorium/figures/{f['id']}.md with a draft caption and what the figure shows.")))
        return out

    def before(self, cfg):
        (cfg.paper / "figures").mkdir(exist_ok=True)
        (cfg.work / "figures").mkdir(exist_ok=True)

    def validate(self, cfg):
        errs = latex.run_figures(cfg)
        for f in outline(cfg).get("figures", []):
            if not (cfg.paper / "figures" / f"{f['id']}.pdf").exists():
                errs.append(f"paper/figures/{f['id']}.pdf was not produced")
        return errs


class Tables(Stage):
    def tables(self, cfg):
        return outline(cfg).get("tables", [])

    def before(self, cfg):
        (cfg.work / "tables").mkdir(exist_ok=True)

    def tasks(self, cfg):
        return [Task("tablesetter", f"table-{t['id']}", context(cfg) + (
            f"Task: set table `{t['id']}` as planned in .scriptorium/outline.json:\n{json.dumps(t, indent=1)}\n"
            f"Write .scriptorium/tables/{t['id']}.json and run `scriptorium table {t['id']}` until it reports no "
            "problems.")) for t in self.tables(cfg)]

    def collect(self, cfg):
        self.errors = T.build(cfg, read_json(cfg.work / "numbers.json") or {}, [t["id"] for t in self.tables(cfg)])

    def validate(self, cfg):
        errs = list(getattr(self, "errors", []))
        for t in self.tables(cfg):
            if not T.out_path(cfg, t["id"]).exists():
                errs.append(f"paper/table_{t['id']}.tex was not rendered")
        return errs


class Draft(Stage):
    """Write the sections of one wave in parallel, each by its own writer."""

    def __init__(self, name: str, wave: int):
        super().__init__(name)
        self.wave = wave

    def sections(self, cfg):
        return [s for s in outline(cfg).get("sections", []) if s.get("wave") == self.wave]

    def task_for(self, cfg, s, extra=""):
        others = ", ".join(f"paper/{x['file']}.tex" for x in outline(cfg).get("sections", []) if x is not s)
        kind = ("the abstract: plain text, no \\section command, one paragraph" if s["file"] == "abstract"
                else f"a section that starts with \\section{{{s.get('title', s['id'])}}}\\label{{sec:{s['id']}}}")
        wave_note = ("Wave 1 sections are already written; read them so this section matches what they show."
                     if self.wave == 2 else "")
        return Task("writer", f"write-{s['file']}", context(cfg) + (
            f"Task: write paper/{s['file']}.tex, {kind}. The plan for it, from .scriptorium/outline.json:\n"
            f"{json.dumps(s, indent=1)}\n{wave_note}\nEdit only paper/{s['file']}.tex (and paper/sources.py if a "
            f"number you need has no recipe). Other writers own: {others}." + extra))

    VARIANTS = ("Follow the plan closely.",
                "Lead with the single finding a reader should remember; write the shortest version that carries the "
                "storyline.",
                "Lead with the problem as practitioners experience it and why current practice falls short; then the "
                "idea.")

    def contested(self, cfg):
        if self.wave != 2 or cfg.contest_n < 2:
            return []
        return [s for s in self.sections(cfg) if s["file"] == "abstract" or s["file"].startswith("01_")]

    def tasks(self, cfg):
        out = []
        cont = {s["file"] for s in self.contested(cfg)}
        for s in self.sections(cfg):
            if s["file"] not in cont:
                out.append(self.task_for(cfg, s))
                continue
            for i in range(cfg.contest_n):
                t = self.task_for(cfg, s, f"\n\nThis is candidate {i + 1} of {cfg.contest_n} for this section; the "
                                  "best one is chosen by comparison. " + self.VARIANTS[i % len(self.VARIANTS)])
                t.prompt = t.prompt.replace(f"paper/{s['file']}.tex", f"paper/{s['file']}__v{i + 1}.tex")
                t.label = f"write-{s['file']}-v{i + 1}"
                out.append(t)
        return out

    def collect(self, cfg):
        """Settle each contested section: candidates that fail the checks drop out, the panel picks among the rest."""
        for s in self.contested(cfg):
            f = s["file"]
            cands = {}
            for i in range(cfg.contest_n):
                p = cfg.paper / f"{f}__v{i + 1}.tex"
                if not p.exists() or len(p.read_text().split()) < 40:
                    continue
                ok, _ = anchor.check(cfg, str(p))
                probs = val_problems(cfg, [str(p)])
                if ok and not probs:
                    cands[f"v{i + 1}"] = p
            keep = cfg.work / "candidates" / f
            keep.mkdir(parents=True, exist_ok=True)
            if cands:
                what = "abstract" if f == "abstract" else "introduction"
                task = (f"Both candidates are the {what} of the same paper, written from the same plan and evidence. "
                        f"Decide which {what} makes the stronger paper.")
                win, _ = contest.tournament(cfg, self.name + ":" + f, task,
                                            {n: contest.strip_tex(p.read_text()) for n, p in cands.items()})
                shutil.copy2(cands[win], cfg.paper / f"{f}.tex")
            for i in range(cfg.contest_n):
                p = cfg.paper / f"{f}__v{i + 1}.tex"
                if p.exists():
                    shutil.move(str(p), keep / p.name)

    def validate(self, cfg):
        errs = []
        for s in self.sections(cfg):
            p = section_path(cfg, s)
            if not p.exists() or len(p.read_text().split()) < 40:
                errs.append(f"paper/{s['file']}.tex is missing or nearly empty")
        files = [str(section_path(cfg, s)) for s in self.sections(cfg) if section_path(cfg, s).exists()]
        if files:
            ok, out = anchor.check(cfg, *files)
            if not ok:
                errs.append("numbers that do not recompute (PaperAnchor):\n" + out[-3000:])
        rep = cite.verify(cfg.root)
        errs += [e for e in cite.problems(rep)]
        errs += val_problems(cfg, files)
        return errs

    def fix_tasks(self, cfg, errors):
        msg = "\n\nThe checks found these problems. Fix the ones in your file:\n- " + "\n- ".join(errors)
        out = []
        for s in self.sections(cfg):
            if (cfg.paper / f"{s['file']}.tex").exists() and not any(s["file"] in e for e in errors):
                continue
            t = self.task_for(cfg, s, msg)
            t.label += "-fix"
            out.append(t)
        return out


class Edit(Stage):
    max_fix = 2

    def collect(self, cfg):
        self.comp = None
        if not cfg.comprehension:
            return
        pdf = cfg.paper / "main.pdf"
        rec = state.stage(state.load(cfg), self.name)
        if pdf.exists() and rec.get("fixes", 0) == 0:
            from . import comprehension
            self.comp = comprehension.run(cfg, pdf)
            contest.decide(cfg, self.name, "comprehension test", score=self.comp.get("score"),
                           discriminative=self.comp.get("discriminative"))

    def validate(self, cfg):
        errs = checks(cfg, page_limit=True)
        c = getattr(self, "comp", None)
        if c and c.get("ok") and c.get("score", 1) < cfg.comprehension_min and c.get("missed"):
            errs.append(f"comprehension: a reader with only the PDF answered {c['reader_right']} of "
                        f"{c['discriminative']} questions right. Make the paper state these clearly (the question, the "
                        "right answer, what the reader answered):\n" + "\n".join(
                            f"  - {m['q']} | right: {m['key']} | reader: {m['reader']}" for m in c["missed"]))
        return errs

    def tasks(self, cfg):
        return [Task("editor", "edit", context(cfg) + (
            "Task: turn the drafted sections into one paper. Read paper/main.tex and every file it inputs. Make the "
            "storyline in .scriptorium/outline.json carry through, remove repetition, make terms and names "
            "consistent, check that every figure and table is referenced and every claim matches the results. Then "
            f"run `scriptorium build` and fix every problem it reports, including a main text over {cfg.page_limit} "
            "pages. Run `scriptorium consistency`: fix every error, and check each warning against .scriptorium/ledger.md "
            "(narrow any sentence that claims more than its ledger claim). Finish with `scriptorium lint` and fix the "
            "flagged prose."))]

class Review(Stage):
    max_fix = 1

    def __init__(self, name: str, rnd: int):
        super().__init__(name)
        self.rnd = rnd

    def tasks(self, cfg):
        return [Task("reviewer", f"review-{p}", context(cfg) + (
            f"Task: review the paper as a reviewer for {cfg.venue} whose focus is {p}. Read paper/main.tex, every "
            f"file it inputs, and the figure PNGs in paper/figures/. Write your review as JSON to "
            f".scriptorium/reviews/{self.name}_{p}.json. Do not edit the paper."), role="reviewer")
            for p in cfg.reviewers]

    def before(self, cfg):
        (cfg.work / "reviews").mkdir(exist_ok=True)

    def reviews(self, cfg) -> list[dict]:
        out = []
        for p in cfg.reviewers:
            r = read_json(cfg.work / "reviews" / f"{self.name}_{p}.json")
            if r is not None:
                r["persona"] = p
                out.append(r)
        return out

    def validate(self, cfg):
        from .handoffs import review_problems
        errs = []
        for p in cfg.reviewers:
            errs += [e if f"{self.name}_{p}.json" in e else f"{self.name}_{p}.json: {e}"
                     for e in review_problems(cfg.work / "reviews" / f"{self.name}_{p}.json")]
        return errs

    def fix_tasks(self, cfg, errors):
        bad = {p for p in cfg.reviewers if any(f"_{p}.json" in e for e in errors)}
        return [t for t in super().fix_tasks(cfg, errors) if t.label.removeprefix("review-").removesuffix("-fix") in bad]

    def after(self, cfg):
        rs = self.reviews(cfg)
        scores = [float(r["overall"]) for r in rs if isinstance(r.get("overall"), (int, float))]
        if not scores:
            return
        mean = sum(scores) / len(scores)
        s = state.load(cfg)
        s["scores"][self.name] = {"mean": round(mean, 2), "each": {r["persona"]: r.get("overall") for r in rs}}
        if self.rnd == 0:
            s["accepted"] = self.name
        else:
            prev = s["scores"].get(s.get("accepted", "review0"), {}).get("mean", 0)
            if mean + 1e-9 >= prev:
                s["accepted"] = self.name
                s.setdefault("decisions", {})[f"revise{self.rnd}"] = f"kept: mean score {prev:.2f} -> {mean:.2f}"
            else:
                state.save(cfg, s)
                state.restore(cfg, f"pre_revise{self.rnd}")
                s = state.load(cfg)
                s.setdefault("decisions", {})[f"revise{self.rnd}"] = (
                    f"rolled back: mean score fell {prev:.2f} -> {mean:.2f}; the paper before this revision is kept")
                s["stop_reviews"] = True
        state.save(cfg, s)
        consolidate(cfg, self.name)

    def on_fail(self, cfg, errors):
        return "continue" if self.reviews(cfg) else "stop"


def consolidate(cfg: Config, review_stage: str) -> Path:
    """Merge one round of reviews into a single list for the reviser, major points first."""
    lines = [f"# Reviews from {review_stage}\n"]
    for p in cfg.reviewers:
        r = read_json(cfg.work / "reviews" / f"{review_stage}_{p}.json")
        if not r:
            continue
        lines.append(f"## Reviewer: {p} (overall {r.get('overall')}/10)\n\n{r.get('summary', '')}\n")
        ws = sorted(r.get("weaknesses", []), key=lambda w: 0 if str(w.get("severity", "")).lower() == "major" else 1)
        for w in ws:
            lines.append(f"- [{w.get('severity', 'minor')}] {w.get('issue', '')} (where: {w.get('where', '?')}). "
                         f"Suggested: {w.get('suggestion', '')}")
        for q in r.get("questions", []):
            lines.append(f"- [question] {q}")
        lines.append("")
    out = cfg.work / "reviews" / f"{review_stage}_all.md"
    out.write_text("\n".join(lines))
    return out


class Revise(Stage):
    max_fix = 1

    def __init__(self, name: str, rnd: int):
        super().__init__(name)
        self.rnd = rnd

    def before(self, cfg):
        state.snapshot(cfg, f"pre_revise{self.rnd}")

    def tasks(self, cfg):
        src = state.load(cfg).get("accepted", "review0")
        meta = cfg.work / "reviews" / f"{src}_meta.json"
        lead = (f"the area chair's meta-review .scriptorium/reviews/{src}_meta.json (its required changes, in order), "
                f"with the full reviews in .scriptorium/reviews/{src}_all.md" if meta.exists()
                else f".scriptorium/reviews/{src}_all.md")
        return [Task("reviser", f"revise-{self.rnd}", context(cfg) + (
            f"Task: revise the paper in response to {lead}. Address the major points first. "
            "A point that would need a new experiment is answered by narrowing the claim or stating the limit, never "
            f"by inventing a result. Run `scriptorium build` and fix what it reports. Write what you changed for each "
            f"point to .scriptorium/reviews/response{self.rnd}.md."))]

    def validate(self, cfg):
        return checks(cfg, page_limit=True)

    def on_fail(self, cfg, errors):
        state.restore(cfg, f"pre_revise{self.rnd}")
        s = state.load(cfg)
        s.setdefault("decisions", {})[self.name] = "rolled back: the revision failed the checks: " + "; ".join(errors)[:400]
        s["stop_reviews"] = True
        state.save(cfg, s)
        return "continue"


class Final(Stage):
    def validate(self, cfg):
        errs = checks(cfg, page_limit=True)
        report(cfg, errs)
        return []          # the final report records problems; it never loops


def report(cfg: Config, errs: list[str]) -> Path:
    s = state.load(cfg)
    b = read_json(cfg.work / "build.json") or {}
    cites = cite.verify(cfg.root)
    nums = good_numbers(cfg)
    flags = lint.lint(cfg.paper)
    tagged = sum(len(re.findall(r"\\src\{", p.read_text())) for p in cfg.paper.glob("*.tex"))
    tot = {k: sum(u.get(k, 0) for u in s["usage"].values()) for k in
           ("sessions", "turns", "input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")}
    lines = [
        f"# Scriptorium report: {outline(cfg).get('title') or cfg.title}\n",
        ("All checks pass." if not errs else f"{len(errs)} check(s) still fail; see below."),
        "",
        "| Check | Result |", "|---|---|",
        f"| Build | {b.get('summary', 'not run')} |",
        f"| Numbers | {tagged} tagged numbers in the text, {len(nums)} recipes; "
        f"{'all recompute' if not any('PaperAnchor' in e for e in errs) else 'some fail'} |",
        f"| Citations | {len(cite.bib_entries(cfg.root))} entries, all fetched from bibliographic databases"
        f"{'' if not (cites['untracked'] or cites['edited']) else ' (some are not)'}; "
        f"{len(cites['missing'])} missing, {len(cites['unused'])} unused |",
        f"| Prose lint | {len(flags)} flag(s) |",
        f"| Review scores | " + ", ".join(f"{k}: {v['mean']}" for k, v in s["scores"].items()) + " |",
        f"| Agent sessions | {tot['sessions']} sessions, {tot['turns']} turns, {tot['output_tokens']:,} output tokens, "
        f"{tot['input_tokens'] + tot['cache_read_input_tokens'] + tot['cache_creation_input_tokens']:,} input tokens |",
        "",
    ]
    if s.get("decisions"):
        lines += ["## Revision decisions", ""] + [f"- {k}: {v}" for k, v in s["decisions"].items()] + [""]
    if errs:
        lines += ["## Open problems", ""] + [f"- {e}" for e in errs] + [""]
    if flags:
        lines += ["## Prose flags", ""] + [f"- {f}" for f in flags[:40]] + [""]
    out = cfg.work / "report.md"
    out.write_text("\n".join(lines))
    (cfg.work / "final_errors.json").write_text(json.dumps({"errors": errs}, indent=1))
    from . import htmlreport
    htmlreport.write(cfg, errs)
    return out


def _after(st: Stage, *deps: str) -> Stage:
    st.deps = tuple(deps)
    return st


def pipeline(cfg: Config) -> list[Stage]:
    """Every stage, in an order that respects its dependencies (the order the interactive mode walks)."""
    from . import team as T
    st: list[Stage] = [
        _after(Scout("scout")),
        _after(T.Experiments("experiments"), "scout"),
        _after(Evidence("evidence"), "scout"),
        _after(T.Stats("stats"), "evidence"),
        _after(Ledger("ledger"), "stats", "experiments"),
        _after(Story("story"), "ledger"),
        _after(Outline("outline"), "story"),
        _after(T.Notation("notation"), "outline"),
        _after(Library("library"), "outline"),
        _after(Figures("figures"), "outline"),
        _after(Tables("tables"), "outline"),
        _after(Draft("draft", 1), "notation", "library", "figures", "tables"),
        _after(Draft("frame", 2), "draft"),
        _after(Edit("edit"), "frame"),
        _after(T.Audit("audit"), "edit"),
        _after(T.Polish("polish"), "audit"),
        _after(T.Fit("fit"), "polish"),
        _after(Review("review0", 0), "fit"),
    ]
    prev = "review0"
    for r in range(1, cfg.review_rounds + 1):
        st += [_after(T.Chair(f"chair{r - 1}", f"review{r - 1}"), prev),
               _after(Revise(f"revise{r}", r), f"chair{r - 1}"),
               _after(Review(f"review{r}", r), f"revise{r}")]
        prev = f"review{r}"
    st += [_after(Final("final"), prev), _after(T.Package("package"), "final")]
    return st


# ---------------------------------------------------------------------------------------------------------------------
# Engine shared by `scriptorium run` (headless) and `scriptorium next/done` (inside a Claude Code session)
# ---------------------------------------------------------------------------------------------------------------------

def get(cfg: Config, name: str) -> Stage:
    for s in pipeline(cfg):
        if s.name == name:
            return s
    raise SystemExit(f"no stage {name!r}; stages: " + ", ".join(s.name for s in pipeline(cfg)))


FINISHED = ("done", "skipped")


def ready(cfg: Config, active: set[str] | frozenset = frozenset()) -> list[Stage]:
    """Stages that may start now: not finished, not in `active`, and every dependency finished (a stage that failed in
    an earlier run is tried again). Review rounds after a rollback are marked skipped here."""
    with state.LOCK:
        s = state.load(cfg)
        out = []
        for st in pipeline(cfg):
            status = s["stages"].get(st.name, {}).get("status", "pending")
            if status in FINISHED or st.name in active:
                continue
            if not all(s["stages"].get(d, {}).get("status") in FINISHED for d in st.deps):
                continue
            from .team import Chair
            if s.get("stop_reviews") and isinstance(st, (Revise, Review, Chair)):
                state.mark(cfg, st.name, "skipped")
                events.emit(cfg, "stage_done", stage=st.name, skipped=True)
                return ready(cfg, active)
            out.append(st)
        return out


def next_stage(cfg: Config) -> Stage | None:
    """The first stage that may start (or is already running), for the interactive mode, which runs one at a time."""
    s = state.load(cfg)
    for st in pipeline(cfg):
        if s["stages"].get(st.name, {}).get("status") == "running":
            return st
    r = ready(cfg)
    return r[0] if r else None


def all_finished(cfg: Config) -> bool:
    s = state.load(cfg)
    return all(s["stages"].get(st.name, {}).get("status") in FINISHED for st in pipeline(cfg))


def begin(cfg: Config, st: Stage) -> list[Task]:
    with state.LOCK:
        s = state.load(cfg)
        if state.stage(s, st.name).get("status") != "running":
            st.before(cfg)
            state.mark(cfg, st.name, "running", fixes=0)
            events.emit(cfg, "stage_start", stage=st.name, deps=list(st.deps))
        return st.tasks(cfg)


def finish(cfg: Config, st: Stage) -> dict:
    """After the agents ran: post-process, check, and decide. Returns {status: done|fix|failed, errors, tasks}.
    Checks of parallel stages run one at a time (they build the paper and rewrite shared notes)."""
    with state.LOCK:
        res = _finish(cfg, st)
    events.emit(cfg, "stage_check", stage=st.name, status=res["status"], errors=[e.splitlines()[0][:200]
                                                                                for e in res["errors"]][:20])
    if res["status"] == "done":
        cid = history.commit(cfg, st.name, "accepted" if not res["errors"] else
                             f"accepted with {len(res['errors'])} open problem(s)")
        events.emit(cfg, "stage_done", stage=st.name, commit=cid)
        if isinstance(st, Final):
            from . import htmlreport
            htmlreport.write(cfg)          # again, now that the final stage is marked done
    elif res["status"] == "failed":
        events.emit(cfg, "stage_failed", stage=st.name)
    return res


def _finish(cfg: Config, st: Stage) -> dict:
    moved = lock.verify(cfg.root, cfg.lock_ignore)
    if moved.get("modified") or moved.get("deleted"):
        errs = ([f"modified outside paper/: {f}" for f in moved["modified"]]
                + [f"deleted outside paper/: {f}" for f in moved["deleted"]])
        state.mark(cfg, st.name, "failed", errors=errs)
        return {"status": "failed", "errors": errs + ["the repository's data changed; restore it (e.g. git checkout) "
                                                      "and rerun `scriptorium lock` only if the change is intended"]}
    if moved.get("created"):
        s = state.load(cfg)
        state.stage(s, st.name).setdefault("quarantined", []).extend(moved["created"])
        state.save(cfg, s)
    st.collect(cfg)
    errs = st.validate(cfg)
    if not errs:
        st.after(cfg)
        state.mark(cfg, st.name, "done", errors=[])
        return {"status": "done", "errors": []}
    s = state.load(cfg)
    rec = state.stage(s, st.name)
    if rec.get("fixes", 0) < st.max_fix:
        rec["fixes"] = rec.get("fixes", 0) + 1
        state.save(cfg, s)
        return {"status": "fix", "errors": errs, "tasks": st.fix_tasks(cfg, errs)}
    if st.on_fail(cfg, errs) == "continue":
        st.after(cfg)
        state.mark(cfg, st.name, "done", errors=errs)
        return {"status": "done", "errors": errs}
    state.mark(cfg, st.name, "failed", errors=errs)
    return {"status": "failed", "errors": errs}
