"""Storytelling rules in code: few numbers in the prose, emphasis where strong papers put it, and a framework figure.

Numbers. The prose tells the story; tables and figures hold the numbers. Tagged numbers (\\src) in running text are
counted per paragraph outside tables, figures and captions: at most two in the abstract, three in the introduction,
none in related work, and two per paragraph elsewhere (four in the setup, which states settings).

Emphasis, the way CVPR and NeurIPS papers use it:
- the contribution list at the end of the introduction is a list whose items open with a bold lead-in;
- related-work paragraphs open with a bold run-in head (\\paragraph{...} or \\textbf{...}.);
- one to three italic phrases in the abstract and introduction carry the central claim;
- bold is not scattered through running text (at most two bold phrases per section outside heads and lead-ins).

Framework figure. At least one diagram has "role": "framework": it shows the main idea, carries the central claim and
the contributions, and the introduction refers to it.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .config import Config

FLOAT_RE = re.compile(r"\\begin\{(figure\*?|table\*?|tabular|algorithm\*?)\}.*?\\end\{\1\}", re.S)
SRC_RE = re.compile(r"\\src\{[^}]*\}")
BOLD_RE = re.compile(r"\\textbf\{|\\bfseries|\{\\bf\s")
EMPH_RE = re.compile(r"\\emph\{|\\textit\{|\{\\it\s|\\itshape")


def kind(name: str) -> str:
    n = name.lower()
    if n == "abstract":
        return "abstract"
    if n.startswith("01_") or "intro" in n:
        return "intro"
    if "related" in n or "background" in n or "prior" in n:
        return "related"
    if "setup" in n or "experimental" in n or "implementation" in n:
        return "setup"
    if re.search(r"conclu|discuss|limitation", n):
        return "discussion"
    return "body"


BUDGET = {"abstract": ("total", 2), "intro": ("total", 3), "related": ("total", 0), "discussion": ("total", 2),
          "setup": ("paragraph", 4), "body": ("paragraph", 2)}


def _clean(t: str) -> str:
    t = "\n".join(re.sub(r"(?<!\\)%.*", "", ln) for ln in t.splitlines())
    t = FLOAT_RE.sub("\n\n", t)
    t = re.sub(r"\\input\{table_[^}]*\}", "", t)
    return t


def paragraphs(t: str) -> list[str]:
    t = re.sub(r"\\(sub)*section\*?\{[^}]*\}(\\label\{[^}]*\})?", "\n\n", t)
    return [p for p in re.split(r"\n\s*\n|\\paragraph\{", t) if p.strip()]


def section_files(cfg: Config) -> list[Path]:
    try:
        o = json.loads((cfg.work / "outline.json").read_text())
        files = [s["file"] for s in o.get("sections", [])]
    except (OSError, json.JSONDecodeError, KeyError):
        files = [p.stem for p in sorted(cfg.paper.glob("*.tex")) if p.stem != "main" and not p.stem.startswith("table_")]
    return [cfg.paper / f"{f}.tex" for f in files if (cfg.paper / f"{f}.tex").exists()]


def number_problems(cfg: Config) -> list[str]:
    errs = []
    for p in section_files(cfg):
        k = kind(p.stem)
        how, cap = BUDGET[k]
        paras = paragraphs(_clean(p.read_text()))
        counts = [len(SRC_RE.findall(x)) for x in paras]
        if how == "total" and sum(counts) > cap:
            errs.append(f"{p.name}: {sum(counts)} numbers in the prose; the {k} carries at most {cap}"
                        + (" (related work carries none)" if cap == 0 else "")
                        + ". Keep the headline number, say the rest in words, and point to the table or figure")
        elif how == "paragraph":
            for i, c in enumerate(counts, 1):
                if c > cap:
                    first = re.sub(r"\s+", " ", paras[i - 1]).strip()[:70]
                    errs.append(f"{p.name}: paragraph {i} (\"{first}...\") prints {c} numbers; at most {cap} per "
                                "paragraph. Open with the insight, keep one headline number, move the rest to a table")
    return errs


def _contribution_list(t: str) -> list[str] | None:
    lists = re.findall(r"\\begin\{(itemize|enumerate)\}(.*?)\\end\{\1\}", t, re.S)
    if not lists:
        return None
    items = [x.strip() for x in re.split(r"\\item\b", lists[-1][1]) if x.strip()]
    return items


def emphasis_problems(cfg: Config) -> list[str]:
    errs = []
    files = {p.stem: p for p in section_files(cfg)}
    intro = next((p for s, p in files.items() if kind(s) == "intro"), None)
    if intro is not None:
        t = _clean(intro.read_text())
        items = _contribution_list(t)
        if items is None:
            errs.append(f"{intro.name}: end the introduction with the contributions as a list (itemize), two to four "
                        "items")
        else:
            for i, it in enumerate(items, 1):
                if not re.match(r"\s*(\\textbf\{|\{\\bf\s)", it):
                    errs.append(f"{intro.name}: contribution {i} should open with a bold lead-in, e.g. "
                                "\"\\textbf{A framework for ...} We ...\"")
    front = "".join(_clean(p.read_text()) for s, p in files.items() if kind(s) in ("abstract", "intro"))
    n_emph = len(EMPH_RE.findall(front))
    if front and n_emph == 0:
        errs.append("abstract/introduction: put the central claim, once, in italics (\\emph{...}) where it is stated")
    elif n_emph > 3:
        errs.append(f"abstract/introduction: {n_emph} italic phrases; keep one to three, for the central claim")
    for s, p in files.items():
        t = _clean(p.read_text())
        if kind(s) == "related":
            for i, para in enumerate(paragraphs(t), 1):
                if len(para.split()) > 25 and not re.match(r"\s*(\\noindent\s*)?(\\textbf\{|[^}]*\}|\{\\bf\s)", para):
                    errs.append(f"{p.name}: related-work paragraph {i} should open with a bold run-in head "
                                "(\\paragraph{Topic.} or \\textbf{Topic.})")
        body = re.sub(r"\\paragraph\{[^}]*\}", "", t)
        body = re.sub(r"\\item\s*\\textbf\{[^}]*\}", "", body)
        body = re.sub(r"(^|\n\n)\s*(\\noindent\s*)?\\textbf\{[^}]*\}", r"\1", body)
        n_bold = len(BOLD_RE.findall(body))
        if n_bold > 2:
            errs.append(f"{p.name}: {n_bold} bold phrases in running text; bold belongs to run-in heads and "
                        "contribution lead-ins, at most two elsewhere")
    return errs


def framework_problems(cfg: Config) -> list[str]:
    """Outline-level: at least one framework diagram that the introduction refers to."""
    try:
        o = json.loads((cfg.work / "outline.json").read_text())
    except (OSError, json.JSONDecodeError):
        return []
    figs = o.get("figures") or []
    fw = [f for f in figs if f.get("role") == "framework"]
    if not fw:
        return ["the outline needs a framework figure (`\"role\": \"framework\"`, kind diagram): the main idea of the "
                "paper in one picture, carrying the central claim and the contributions"]
    errs = []
    for f in fw:
        if f.get("kind") != "diagram":
            errs.append(f"figure {f.get('id')}: a framework figure is a diagram")
    intro = [s for s in o.get("sections", []) if kind(s.get("file", "")) == "intro"]
    if intro and not any(f.get("id") in (intro[0].get("figures") or []) or f.get("teaser") for f in fw):
        errs.append("the introduction should present the framework figure (list it in the introduction's `figures`)")
    return errs


def framework_ref_problems(cfg: Config) -> list[str]:
    """Text-level: the introduction refers to the framework figure."""
    try:
        o = json.loads((cfg.work / "outline.json").read_text())
    except (OSError, json.JSONDecodeError):
        return []
    fw = [f["id"] for f in o.get("figures") or [] if f.get("role") == "framework" and f.get("id")]
    intro = next((p for p in section_files(cfg) if kind(p.stem) == "intro"), None)
    if not fw or intro is None:
        return []
    t = intro.read_text()
    if not any(re.search(r"\\(c|C|auto)?ref\{fig:" + re.escape(i) + r"\}", t) for i in fw):
        return [f"{intro.name}: refer to the framework figure (Figure~\\ref{{fig:{fw[0]}}}) where the idea is introduced"]
    return []


def problems(cfg: Config) -> list[str]:
    return number_problems(cfg) + emphasis_problems(cfg) + framework_ref_problems(cfg)
