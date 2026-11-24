"""`scriptorium audit PAPER_DIR`: check an existing LaTeX paper with the checking and review teams.

The paper is copied into an audit folder; nothing in PAPER_DIR is ever changed. The audit folder holds

    src/                   the copy, compiled as it is
    paper/01_paper.tex     the body, flattened (every \\input and \\include expanded), for the text checks
    paper/refs.bib         the bibliography files, joined
    .scriptorium/audit/    the findings, report.md and report.html

and runs this graph:

    prep (code: build, consistency, prose lint, figure lint) -> { resolve (code: every reference looked up in the
    bibliographic databases) -> citecheck | claims | review0 -> chair0 } -> report
"""
from __future__ import annotations

import difflib
import html
import json
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import cite, consistency, figlint, latex, lint, lit, lock, state
from . import config as C
from . import stages as S
from . import team as T
from .config import Config
from .runner import Task

INPUT_RE = re.compile(r"\\(input|include|subfile)\{([^}]+)\}")


def find_main(src: Path) -> Path:
    cands = [src / "main.tex"] + sorted(src.rglob("*.tex"))
    for p in cands:
        if p.exists() and re.search(r"^\s*\\documentclass", p.read_text(errors="replace"), re.M):
            return p
    raise SystemExit(f"scriptorium audit: no .tex file with \\documentclass in {src}")


def _strip_comments(t: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*", "", ln) for ln in t.splitlines())


def expand(path: Path, root: Path, depth: int = 0) -> str:
    """The file's text with every \\input / \\include replaced by the included file, recursively."""
    text = _strip_comments(path.read_text(errors="replace"))
    if depth > 12:
        return text

    def sub(m):
        name = m.group(2).strip()
        for cand in (root / name, root / f"{name}.tex", path.parent / name, path.parent / f"{name}.tex"):
            if cand.is_file():
                return expand(cand, root, depth + 1)
        return m.group(0)
    return INPUT_RE.sub(sub, text)


def split(full: str) -> dict:
    title = re.search(r"\\(?:icml)?title\{((?:[^{}]|\{[^{}]*\})*)\}", full)
    body = full.split("\\begin{document}", 1)[-1].split("\\end{document}", 1)[0]
    ab = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", body, re.S)
    bibs = []
    for m in re.finditer(r"\\bibliography\{([^}]+)\}", full):
        bibs += [b.strip() for b in m.group(1).split(",")]
    for m in re.finditer(r"\\addbibresource\{([^}]+)\}", full):
        bibs.append(m.group(1).strip())
    return {"title": re.sub(r"\s+", " ", title.group(1)).strip() if title else "Untitled",
            "abstract": ab.group(1).strip() if ab else "", "body": body, "bibs": bibs}


def setup(src: Path, out: Path, venue: str = "", template: str = "default") -> Config:
    """Create the audit folder. Returns its config."""
    src = src.resolve()
    if not src.is_dir():
        raise SystemExit(f"scriptorium audit: {src} is not a folder")
    out = out.resolve()
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"scriptorium audit: {out} exists and is not empty; choose another --out")
    shutil.copytree(src, out / "src", ignore=shutil.ignore_patterns(".git", "*.aux", "*.log", "*.synctex.gz"))
    main = find_main(out / "src")
    parts = split(expand(main, main.parent))
    toml = C.render_toml(title=parts["title"].replace('"', "'"), template=template, venue=venue or "the target venue",
                         preset="standard")
    toml = toml.replace("[run]\n", f"[run]\naudit = true\naudit_main = \"{main.relative_to(out / 'src')}\"\n", 1)
    (out / "scriptorium.toml").write_text(toml)
    (out / "paper").mkdir()
    (out / C.WORK / "audit").mkdir(parents=True)
    body = re.sub(r"\\begin\{abstract\}.*?\\end\{abstract\}", "", parts["body"], flags=re.S)
    (out / "paper" / "01_paper.tex").write_text(body)
    (out / "paper" / "abstract.tex").write_text(parts["abstract"] + "\n")
    bib = []
    for b in parts["bibs"]:
        p = main.parent / (b if b.endswith(".bib") else f"{b}.bib")
        if p.exists():
            bib.append(p.read_text(errors="replace"))
    (out / "paper" / "refs.bib").write_text("\n\n".join(bib))
    (out / C.WORK / "outline.json").write_text(json.dumps({"title": parts["title"], "storyline": "", "sections": [
        {"id": "abstract", "file": "abstract", "claims": ["paper"]}, {"id": "paper", "file": "01_paper", "claims": ["paper"]}],
        "figures": []}))
    shutil.copy2(C.TEMPLATES / "style.md", out / C.WORK / "style.md")
    lock.take(out)
    return C.load(out)


# ---------------------------------------------------------------------------------------------------------------------
# Stages

def adir(cfg: Config) -> Path:
    return cfg.work / "audit"


class Prep(S.Stage):
    """Code only: compile the copy as it is, then the consistency pass, the prose lint and the figure lint."""

    def validate(self, cfg):
        src = cfg.root / "src"
        main = Path(cfg.audit_main)
        b = latex.build(cfg, src=src / main.parent, main=main.name)
        (cfg.work / "build.json").write_text(json.dumps({"ok": b.ok, "pages": b.pages, "main_pages": b.main_pages,
                                                         "summary": b.summary()}, indent=1))
        errs, warns = consistency.check(cfg, {})
        figs = sorted({p for p in src.rglob("*.pdf") if p.name != f"{main.stem}.pdf"})
        fl = {}
        for p in figs:
            probs = figlint.lint_pdf(p.stem, p)
            if probs:
                fl[str(p.relative_to(src))] = probs
        code = {"build": b.summary(), "build_ok": b.ok, "build_problems": b.problems(cfg.page_limit),
                "pages": b.pages, "main_pages": b.main_pages, "consistency_errors": errs, "consistency_warnings": warns,
                "prose_flags": lint.lint(cfg.paper), "figure_problems": fl}
        (adir(cfg) / "code.json").write_text(json.dumps(code, indent=1))
        return []


def _match(title: str, hits: list[dict]) -> tuple[dict | None, float]:
    best, score = None, 0.0
    for h in hits:
        r = difflib.SequenceMatcher(None, cite._tnorm(title), cite._tnorm(h.get("title", ""))).ratio()
        if r > score:
            best, score = h, r
    return best, score


def resolve_one(key: str, entry: str) -> dict:
    title = re.sub(r"[{}\\]", "", cite.entry_field(entry, "title"))
    year = cite.entry_field(entry, "year")
    author = cite.entry_field(entry, "author")
    first = re.split(r"\s+and\s+", author)[0] if author else ""
    surname = (first.split(",")[0] if "," in first else (first.split()[-1] if first.split() else "")).strip("{} ")
    rec = {"key": key, "title": title, "year": year, "first_author": surname, "found": False, "issues": []}
    if not title:
        rec["issues"].append("the entry has no title")
        return rec
    try:
        hits = cite.search(title, 5, ("openalex", "crossref", "arxiv"))
    except Exception as e:  # noqa: BLE001
        rec["issues"].append(f"lookup failed: {str(e)[:100]}")
        rec["unchecked"] = True
        return rec
    hit, score = _match(title, hits)
    rec["score"] = round(score, 3)
    if not hit or score < 0.9:
        rec["issues"].append("no paper with this title was found in OpenAlex, Crossref or arXiv")
        return rec
    rec.update(found=True, id=hit["id"], matched_title=hit["title"], matched_year=hit.get("year"))
    if year and hit.get("year") and abs(int(re.sub(r"\D", "", year) or 0) - int(re.sub(r"\D", "", hit["year"]) or 0)) > 1:
        rec["issues"].append(f"year {year} in the entry, {hit['year']} in the record")
    if surname and hit.get("authors") and not any(cite._tnorm(surname) in cite._tnorm(a) for a in hit["authors"]):
        rec["issues"].append(f"first author {surname} is not among the record's authors")
    return rec


class Resolve(S.Stage):
    """Code only: look every reference up; record which exist, which do not, and metadata that disagrees."""

    def validate(self, cfg):
        entries = cite.bib_entries(cfg.root)
        with ThreadPoolExecutor(max_workers=6) as ex:
            recs = list(ex.map(lambda kv: resolve_one(*kv), sorted(entries.items())))
        (adir(cfg) / "refs.json").write_text(json.dumps(recs, indent=1))
        prov = {r["key"]: {"id": r["id"], "title": r["matched_title"], "year": r.get("matched_year"), "hash": ""}
                for r in recs if r.get("found")}
        (cfg.work / "citations.json").write_text(json.dumps(prov, indent=1))
        for r in recs:
            if r.get("found"):
                lit.abstract(cfg, r["id"])
        return []


class Claims(T.Audit):
    def tasks(self, cfg):
        return [Task("auditor", "claims", S.context(cfg) + (
            "Task: this is an audit of an existing paper; there is no claim ledger and no recipes. The paper's body is "
            "paper/01_paper.tex (flattened) and its abstract paper/abstract.tex; the compiled PDF is in src/. Audit "
            "every sentence that states a result, comparison, trend, scope or contribution against what the paper "
            "itself shows in its tables, figures and method: a number in the text that differs from its table, a "
            "claim broader than the experiments, \"significant\" without a test, a contribution the paper does not "
            "deliver. Leave `claim` empty. Write .scriptorium/audit.json as your instructions describe, then run "
            "`scriptorium validate .scriptorium/audit.json`. Do not edit any file except your findings."))]


class AuditReview(S.Review):
    def tasks(self, cfg):
        pdf = sorted((cfg.root / "src").rglob(f"{Path(cfg.audit_main).stem}.pdf"))
        where = f"the compiled paper {pdf[0].relative_to(cfg.root)}" if pdf else "paper/01_paper.tex"
        return [Task("reviewer", f"review-{p}", S.context(cfg) + (
            f"Task: review this existing paper as a reviewer for {cfg.venue} whose focus is {p}. Read {where} "
            f"(and paper/01_paper.tex for the text). Write your review as JSON to .scriptorium/reviews/{self.name}_"
            f"{p}.json. Do not edit any file except your review."), role="reviewer") for p in cfg.reviewers]


class Report(S.Stage):
    def validate(self, cfg):
        write_report(cfg)
        return []


def pipeline(cfg: Config) -> list[S.Stage]:
    def after(st, *d):
        st.deps = tuple(d)
        return st
    return [after(Prep("prep")), after(Resolve("resolve"), "prep"), after(lit.CiteCheck("citecheck"), "resolve"),
            after(Claims("claims"), "prep"), after(AuditReview("review0", 0), "prep"),
            after(T.Chair("chair0", "review0"), "review0"),
            after(Report("report"), "citecheck", "claims", "chair0")]


# ---------------------------------------------------------------------------------------------------------------------
# Report

def write_report(cfg: Config) -> Path:
    code = S.read_json(adir(cfg) / "code.json") or {}
    refs = S.read_json(adir(cfg) / "refs.json") or []
    cc = (S.read_json(lit.lit_dir(cfg) / "citecheck.json") or {}).get("findings", [])
    claims = (S.read_json(cfg.work / "audit.json") or {}).get("findings", [])
    meta = S.read_json(cfg.work / "reviews" / "review0_meta.json") or {}
    scores = state.load(cfg)["scores"].get("review0", {})
    missing = [r for r in refs if not r.get("found") and not r.get("unchecked")]
    meta_bad = [r for r in refs if r.get("found") and r.get("issues")]
    bad_cites = [f for f in cc if f.get("verdict") != "supported"]
    bad_claims = [f for f in claims if f.get("verdict") not in (None, "ok")]
    L = [f"# Audit: {S.outline(cfg).get('title', '')}\n"]
    L.append(f"| Check | Result |\n|---|---|\n"
             f"| Build | {code.get('build', 'not run')} |\n"
             f"| Pages (main text) | {code.get('main_pages') or code.get('pages') or '?'} (limit {cfg.page_limit}) |\n"
             f"| References | {len(refs)} entries; {len(missing)} not found in any database; {len(meta_bad)} with "
             f"metadata that disagrees with the record |\n"
             f"| Citations | {len(cc)} checked; {sum(f.get('verdict') == 'unsupported' for f in cc)} unsupported, "
             f"{sum(f.get('verdict') == 'unverifiable' for f in cc)} unverifiable |\n"
             f"| Claims | {len(claims)} checked; {len(bad_claims)} to fix |\n"
             f"| Cross-references and wording | {len(code.get('consistency_errors', []))} errors, "
             f"{len(code.get('consistency_warnings', []))} warnings |\n"
             f"| Prose | {len(code.get('prose_flags', []))} flags |\n"
             f"| Figures | {sum(len(v) for v in (code.get('figure_problems') or {}).values())} layout problems |\n"
             f"| Reviews | mean {scores.get('mean', '?')}; area chair: {meta.get('decision', 'none')} |\n")
    if meta.get("required_changes"):
        L.append("## What to change first (area chair)\n")
        L += [f"{i}. {c.get('change')} ({c.get('where')}; {c.get('action')})" for i, c in
              enumerate(meta["required_changes"], 1)]
        L.append("")
    if missing or meta_bad:
        L.append("## References to check\n")
        L += [f"- `{r['key']}` {r['title'][:90]}: {'; '.join(r['issues'])}" for r in missing + meta_bad]
        L.append("")
    if bad_cites:
        L.append("## Citations that do not support their sentence\n")
        L += [f"- [{f.get('verdict')}] `{f.get('key')}`: \"{f.get('quote', '')[:140]}\" -> {f.get('fix', '')}"
              for f in bad_cites]
        L.append("")
    if bad_claims:
        L.append("## Claims to fix\n")
        L += [f"- [{f.get('verdict')}] \"{f.get('quote', '')[:140]}\" -> {f.get('fix', '')}" for f in bad_claims]
        L.append("")
    probs = code.get("build_problems", []) + code.get("consistency_errors", [])
    if probs:
        L.append("## Build and cross-reference problems\n")
        L += [f"- {p}" for p in probs]
        L.append("")
    if code.get("consistency_warnings") or code.get("prose_flags"):
        L.append("## Wording to look at\n")
        L += [f"- {w}" for w in code.get("consistency_warnings", [])[:30]]
        L += [f"- {w}" for w in code.get("prose_flags", [])[:30]]
        L.append("")
    md = "\n".join(L)
    (adir(cfg) / "report.md").write_text(md)
    (adir(cfg) / "report.html").write_text(_html(md))
    return adir(cfg) / "report.md"


def _html(md: str) -> str:
    out, in_list, in_table = [], False, False
    for ln in md.splitlines():
        e = html.escape(ln)
        e = re.sub(r"`([^`]+)`", r"<code>\1</code>", e)
        if ln.startswith("|"):
            if set(ln.replace("|", "").strip()) <= {"-"}:
                continue
            cells = [c.strip() for c in e.strip("|").split("|")]
            if not in_table:
                out.append("<table>")
                in_table = True
                out.append("<tr>" + "".join(f"<th>{c}</th>" for c in cells) + "</tr>")
            else:
                out.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
            continue
        if in_table:
            out.append("</table>")
            in_table = False
        if re.match(r"^(- |\d+\. )", ln):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append("<li>" + re.sub(r"^(- |\d+\. )", "", e) + "</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if ln.startswith("# "):
            out.append(f"<h1>{e[2:]}</h1>")
        elif ln.startswith("## "):
            out.append(f"<h2>{e[3:]}</h2>")
        elif ln.strip():
            out.append(f"<p>{e}</p>")
    out += ["</ul>"] if in_list else []
    out += ["</table>"] if in_table else []
    return ("<!doctype html><meta charset=utf-8><title>Scriptorium audit</title><style>body{font:15px/1.55 system-ui,"
            "sans-serif;max-width:980px;margin:32px auto;padding:0 20px;color:#1f1b24}h1{font-weight:600}h2{font-weight:"
            "600;border-bottom:2px solid #4E2A84;padding-bottom:3px;margin-top:32px}table{border-collapse:collapse;"
            "width:100%}td,th{border-bottom:1px solid #e4e0ea;padding:6px 8px;text-align:left;vertical-align:top}"
            "th{color:#6b6475;font-weight:500}code{background:#F1EEF7;padding:1px 4px;border-radius:4px}li{margin:4px 0}"
            "</style>" + "\n".join(out))
