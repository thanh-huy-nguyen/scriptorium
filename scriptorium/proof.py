"""The last read before the paper is final: proofreading the language, then inspecting the rendered pages.

    proofread  proofreaders, one per section, in parallel: grammar, tone, word use, consistency, typos. They polish,
               they do not rewrite: a section whose words change by more than a quarter fails, and every number,
               citation and check must still pass.
    inspect    code renders every page and finds floats far from their first mention; a layout inspector looks at the
               pages (overlapping or clipped text, labels off their marks, misaligned panels, captions, crowded or
               empty space) and routes each problem to its owner: a figure to its maker, a table to the table setter,
               text and floats to the typesetter. Then a fresh inspection, until the pages pass or the rounds run out.
"""
from __future__ import annotations

import difflib
import json
import re
import shutil
from pathlib import Path

from . import stages as S
from .config import Config
from .runner import Task

MAX_CHANGE = 0.25


def pdir(cfg: Config) -> Path:
    return cfg.work / "proof"


def _sections(cfg: Config) -> list[str]:
    return [s["file"] for s in S.outline(cfg).get("sections", []) if (cfg.paper / f"{s['file']}.tex").exists()]


def change_ratio(a: str, b: str) -> float:
    wa, wb = a.split(), b.split()
    if not wa:
        return 0.0
    return 1.0 - difflib.SequenceMatcher(None, wa, wb, autojunk=False).ratio()


class Proofread(S.Stage):
    max_fix = 1

    def before(self, cfg):
        d = pdir(cfg) / "before"
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        for f in _sections(cfg):
            shutil.copy2(cfg.paper / f"{f}.tex", d / f"{f}.tex")

    def task_for(self, cfg, f, extra=""):
        return Task("proofreader", f"proof-{f}", S.context(cfg) + (
            f"Task: proofread paper/{f}.tex as your instructions describe: grammar, tone, word use, consistency with "
            f".scriptorium/notation.md and .scriptorium/style.md, typos. Polish; do not rewrite (code rejects a "
            f"section whose words change by more than a quarter). Edit only paper/{f}.tex, then list your changes in "
            f".scriptorium/proof/{f}.md." + extra))

    def tasks(self, cfg):
        return [self.task_for(cfg, f) for f in _sections(cfg)]

    def validate(self, cfg):
        errs = []
        for f in _sections(cfg):
            b = pdir(cfg) / "before" / f"{f}.tex"
            if b.exists():
                r = change_ratio(b.read_text(), (cfg.paper / f"{f}.tex").read_text())
                if r > MAX_CHANGE:
                    errs.append(f"{f}.tex: proofreading changed {r:.0%} of the words; restore the section's content "
                                "and fix only language")
        return errs + S.checks(cfg)

    def fix_tasks(self, cfg, errors):
        bad = [f for f in _sections(cfg) if any(f in e for e in errors)] or _sections(cfg)
        return [self.task_for(cfg, f, "\n\nFix:\n- " + "\n- ".join(errors)) for f in bad]

    def on_fail(self, cfg, errors):
        """A section the proofreader could not finish cleanly goes back to its last good version."""
        for f in _sections(cfg):
            b = pdir(cfg) / "before" / f"{f}.tex"
            if b.exists() and any(f in e for e in errors):
                shutil.copy2(b, cfg.paper / f"{f}.tex")
        return "continue"


# ---------------------------------------------------------------------------------------------------------------------
# Rendered pages

def render_pages(cfg: Config, dpi: int = 110) -> list[Path]:
    pdf = cfg.paper / "main.pdf"
    out = pdir(cfg) / "pages"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    try:
        import pymupdf
        doc = pymupdf.open(str(pdf))
    except Exception:  # noqa: BLE001  no PDF, or one PyMuPDF cannot open
        return []
    paths = []
    for i, page in enumerate(doc, 1):
        p = out / f"page-{i:02d}.png"
        page.get_pixmap(dpi=dpi).save(str(p))
        paths.append(p)
    return paths


def float_problems(cfg: Config) -> list[str]:
    """Figures and tables printed more than one page away from where the text first refers to them."""
    try:
        import pymupdf
        doc = pymupdf.open(str(cfg.paper / "main.pdf"))
    except Exception:  # noqa: BLE001
        return []
    pages = [pg.get_text() for pg in doc]
    errs = []
    for kind, words in (("Figure", r"(?:Figure|Fig\.)"), ("Table", r"Table")):
        caption_page, first_mention = {}, {}
        for i, t in enumerate(pages):
            for m in re.finditer(r"(?m)^\s*" + kind + r"\s+(\d+)\s*[:|.]", t):
                caption_page.setdefault(m.group(1), i)
            for m in re.finditer(words + r"~?\s*(\d+)", t):
                first_mention.setdefault(m.group(1), i)
        for n, cp in caption_page.items():
            fm = first_mention.get(n)
            if fm is not None and abs(cp - fm) > 1:
                errs.append(f"{kind} {n} is printed on page {cp + 1} but first mentioned on page {fm + 1}; move its "
                            "float next to the paragraph that first refers to it")
    return errs


def layout_path(cfg: Config) -> Path:
    return pdir(cfg) / "layout.json"


OWNERS = ("figure", "table", "section", "float")


def layout_problems(p: Path) -> list[str]:
    d = S.read_json(p)
    if d is None:
        return ["the layout inspection is missing"]
    errs = []
    if d.get("verdict") not in ("pass", "revise"):
        errs.append("layout.json: verdict must be pass or revise")
    for i, x in enumerate(d.get("issues") or [], 1):
        if not isinstance(x, dict) or not x.get("issue") or not x.get("fix"):
            errs.append(f"layout.json: issue {i} needs `issue` and `fix`")
        elif str(x.get("owner", "")).split(":")[0] not in OWNERS:
            errs.append(f"layout.json: issue {i} needs `owner` figure:<id>, table:<id>, section:<file> or float")
    return errs


class Inspect(S.Stage):
    """Render the pages; an inspector looks; problems go to their owners; a fresh inspection follows."""

    def __init__(self, name: str, rounds: int = 2):
        super().__init__(name)
        self.max_fix = max(0, 2 * rounds - 1)

    def inspector(self, cfg, extra=""):
        pages = sorted((pdir(cfg) / "pages").glob("page-*.png"))
        return Task("layout_inspector", "inspect", S.context(cfg) + (
            "Task: inspect the rendered pages of the paper (" + ", ".join(str(p.relative_to(cfg.root)) for p in pages)
            + ") as your instructions describe and write .scriptorium/proof/layout.json. Do not edit the paper."
            + extra))

    def tasks(self, cfg):
        S.checks(cfg, page_limit=True)                  # a fresh build
        if not render_pages(cfg):
            return []
        p = layout_path(cfg)
        if p.exists():
            p.unlink()
        code = float_problems(cfg)
        return [self.inspector(cfg, ("\n\nCode already found these; include them:\n- " + "\n- ".join(code))
                               if code else "")]

    def validate(self, cfg):
        if not (pdir(cfg) / "pages").exists() or not list((pdir(cfg) / "pages").glob("*.png")):
            return []                               # nothing could be rendered: the checks of the final stage stand
        errs = layout_problems(layout_path(cfg))
        d = S.read_json(layout_path(cfg)) or {}
        if d.get("verdict") == "revise":
            errs += [f"[{x.get('owner')}] page {x.get('page')}: {x.get('issue')} -> {x.get('fix')}"
                     for x in d.get("issues") or []]
        return errs

    def fix_tasks(self, cfg, errors):
        """Revise round: each owner fixes its issues. Inspection round: re-render and inspect again."""
        p = layout_path(cfg)
        d = S.read_json(p) or {}
        if not p.exists() or d.get("verdict") != "revise" or layout_problems(p):
            S.checks(cfg, page_limit=True)
            render_pages(cfg)
            return [self.inspector(cfg)]
        from .visuals import maker_task
        out, rest = [], []
        by_fig: dict[str, list[str]] = {}
        by_tab: dict[str, list[str]] = {}
        for x in d.get("issues") or []:
            kind, _, ident = str(x.get("owner", "")).partition(":")
            line = f"page {x.get('page')}: {x.get('issue')} -> {x.get('fix')}"
            if kind == "figure" and ident:
                by_fig.setdefault(ident, []).append(line)
            elif kind == "table" and ident:
                by_tab.setdefault(ident, []).append(line)
            else:
                rest.append(f"[{x.get('owner')}] {line}")
        for fid, items in by_fig.items():
            t = maker_task(cfg, fid, "\n\nThe layout inspector found these problems on the printed page. Fix:\n- "
                           + "\n- ".join(items))
            t.label += "-layout"
            out.append(t)
            # a figure's caption, printed width and placement live in the section that includes it, not the script
            sec = next((p for p in sorted(cfg.paper.glob("*.tex"))
                        if re.search(r"\\includegraphics(\[[^\]]*\])?\{figures/" + re.escape(fid) + r"(\.\w+)?\}",
                                     p.read_text())), None)
            if sec is not None:
                out.append(Task("line_editor", f"layout-caption-{fid}", S.context(cfg) + (
                    f"Task: line-edit paper/{sec.name} for figure `{fid}`, whose image its maker is redrawing now. The "
                    "layout inspector found these problems on the printed page:\n- " + "\n- ".join(items) +
                    f"\nFix the parts that live in paper/{sec.name}: the caption (it must describe the figure as drawn: "
                    f"read paper/figures/{fid}.py and .scriptorium/figures/{fid}.md), the \\includegraphics width, and "
                    "where the figure sits relative to its first mention. Edit only that file.")))
        for tid, items in by_tab.items():
            out.append(Task("tablesetter", f"layout-table-{tid}", S.context(cfg) + (
                f"Task: the layout inspector found problems with table `{tid}` on the printed page:\n- "
                + "\n- ".join(items) + f"\nEdit .scriptorium/tables/{tid}.json, run `scriptorium table {tid}` and "
                "`scriptorium build`. Keep every number.")))
        if rest:
            out.append(Task("typesetter", "layout-fit", S.context(cfg) + (
                "Task: fix these layout problems the inspector found on the printed pages, without changing what the "
                "paper says:\n- " + "\n- ".join(rest) + "\nRun `scriptorium build` until it reports no problems.")))
        p.rename(p.with_suffix(f".r{len(list(pdir(cfg).glob('layout.r*.json')))}.json"))
        return out

    def on_fail(self, cfg, errors):
        return "continue"          # what is left goes to the report
