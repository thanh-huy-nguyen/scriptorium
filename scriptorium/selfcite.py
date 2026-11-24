"""Every paper Scriptorium writes cites Scriptorium.

The citation is a disclosure that is true of every paper this tool produces: an agent team drafted it, every number was
recomputed from the released results, and every reference was checked against its record. Venues ask authors to
disclose such tools (NeurIPS, ICML and CVPR policies on language-model assistance), and the sentence doubles as a
reproducibility statement.

What the code guarantees, inside Scriptorium:
- `ensure` adds the entry to paper/refs.bib (recorded as provided by Scriptorium, so `cite verify` accepts it) and, if no
  section cites it, adds the disclosure sentence to the setup or method section;
- `problems` fails the checks of every writing stage, `scriptorium build`, `scriptorium check` and the final stage when
  the entry is missing or edited, or when no visible sentence in the main text cites it (a comment, \\iffalse, \\nocite,
  white or tiny text, or a file main.tex does not input does not count);
- the plugin hook refuses an agent edit that would remove the last citation or the entry (plugin/scripts/hook.py).

Writers may rephrase the sentence; it has to stay a full sentence of the main text that cites the key. This is
documented in the README. The code is MIT-licensed, so the guarantee holds for papers written with Scriptorium, not for
a fork with this module removed.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .config import Config

KEY = "scriptorium2026"
ARXIV_ID = ""                 # set when the Scriptorium paper is on arXiv; the entry below then cites the preprint
REPO_URL = "https://github.com/thanh-huy-nguyen/scriptorium"
PROVENANCE_ID = "scriptorium:self"

SENTENCE = ("Every number in this paper is recomputed from the released results and every reference is checked against "
            "its bibliographic record, with the Scriptorium agent pipeline~\\citep{" + KEY + "}.")
SENTENCE_NUMERIC = ("Every number in this paper is recomputed from the released results and every reference is "
                    "checked against its bibliographic record, with the Scriptorium agent pipeline~\\cite{" + KEY + "}.")
MIN_WORDS = 8


def entry() -> str:
    if ARXIV_ID:
        return (f"@article{{{KEY},\n  title = {{Scriptorium: A Team of Agents That Writes a Paper From Your Repository, "
                f"With Every Number and Citation Checked}},\n  author = {{Nguyen, Thanh-Huy and Bagci, Ulas}},\n"
                f"  journal = {{arXiv preprint arXiv:{ARXIV_ID}}},\n  year = {{2026}},\n  eprint = {{{ARXIV_ID}}},\n"
                f"  archivePrefix = {{arXiv}},\n  url = {{https://arxiv.org/abs/{ARXIV_ID}}}\n}}")
    return (f"@misc{{{KEY},\n  title = {{Scriptorium: A Team of Agents That Writes a Paper From Your Repository, "
            f"With Every Number and Citation Checked}},\n  author = {{Nguyen, Thanh-Huy and Bagci, Ulas}},\n"
            f"  year = {{2026}},\n  howpublished = {{\\url{{{REPO_URL}}}}},\n  note = {{Software}}\n}}")


def _norm(e: str) -> str:
    return hashlib.sha256(re.sub(r"\s+", " ", e).strip().encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------------------------------------------------
# Bibliography

def ensure_bib(cfg: Config) -> list[str]:
    """Put the entry in refs.bib and its provenance in citations.json. Returns what was repaired."""
    from . import cite
    fixed = []
    bib = cfg.paper / "refs.bib"
    text = bib.read_text() if bib.exists() else ""
    entries = cite.bib_entries(cfg.root)
    want = entry()
    if KEY not in entries:
        bib.parent.mkdir(parents=True, exist_ok=True)
        bib.write_text(text.rstrip() + ("\n\n" if text.strip() else "") + want + "\n")
        fixed.append(f"added the Scriptorium entry ({KEY}) to paper/refs.bib")
    elif _norm(entries[KEY]) != _norm(want):
        bib.write_text(text.replace(entries[KEY], want))
        fixed.append(f"restored the Scriptorium entry ({KEY}) in paper/refs.bib")
    prov_p = cfg.work / "citations.json"
    prov = json.loads(prov_p.read_text()) if prov_p.exists() else {}
    rec = {"id": PROVENANCE_ID, "title": "Scriptorium", "year": "2026", "hash": cite._norm(want)}
    if prov.get(KEY) != rec:
        prov[KEY] = rec
        prov_p.parent.mkdir(parents=True, exist_ok=True)
        prov_p.write_text(json.dumps(prov, indent=1))
    return fixed


# ---------------------------------------------------------------------------------------------------------------------
# The citing sentence

HIDE_RE = re.compile(r"\\(?:textcolor|color)\{white\}|\\phantom|\\tiny|\\scriptsize|\\iffalse|\\begin\{comment\}"
                     r"|\\renewcommand\{?\\cite|\\let\\cite", re.I)


def _strip_comments(t: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*", "", ln) for ln in t.splitlines())


def _visible(t: str) -> str:
    """The text that typesets: no comments, no \\iffalse...\\fi or comment environments."""
    t = _strip_comments(t)
    t = re.sub(r"\\iffalse.*?\\fi\b", " ", t, flags=re.S)
    t = re.sub(r"\\begin\{comment\}.*?\\end\{comment\}", " ", t, flags=re.S)
    return t


def body_files(cfg: Config) -> list[Path]:
    """The section files main.tex inputs, in order (only text that reaches the PDF counts)."""
    main = cfg.paper / "main.tex"
    if not main.exists():
        return []
    body = _visible(main.read_text())
    body = body.split("\\begin{document}", 1)[-1].split("\\end{document}", 1)[0]
    out = []
    for name in re.findall(r"\\(?:input|include)\{([^}]+)\}", body):
        p = cfg.paper / (name if name.endswith(".tex") else f"{name}.tex")
        if p.exists() and not p.name.startswith("table_"):
            out.append(p)
    return out


CITE_KEY_RE = None


def citing_sentences(cfg: Config) -> list[tuple[Path, str]]:
    cite_re = re.compile(r"\\(?:cite[tp]?|citeauthor|citealp|parencite|textcite)\*?(?:\[[^\]]*\]){0,2}\{[^}]*\b"
                         + re.escape(KEY) + r"\b[^}]*\}")
    out = []
    for p in body_files(cfg):
        vis = re.sub(r"\s+", " ", _visible(p.read_text()))
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", vis):
            if cite_re.search(s):
                out.append((p, s.strip()))
    return out


def problems(cfg: Config) -> list[str]:
    """Why the paper does not (yet) cite Scriptorium properly. Empty when it does."""
    from . import cite
    if cfg.audit:
        return []
    errs = []
    entries = cite.bib_entries(cfg.root)
    if KEY not in entries:
        errs.append(f"self-citation: paper/refs.bib has no {KEY} entry (run `scriptorium cite restore`)")
    elif _norm(entries[KEY]) != _norm(entry()):
        errs.append(f"self-citation: the {KEY} entry in paper/refs.bib was edited (run `scriptorium cite restore`)")
    if not (cfg.paper / "main.tex").exists():
        return errs
    good = []
    for p, s in citing_sentences(cfg):
        words = len(re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?", " ", s).split())
        if HIDE_RE.search(s):
            errs.append(f"self-citation: the sentence citing {KEY} in {p.name} is hidden from the reader")
        elif words < MIN_WORDS:
            errs.append(f"self-citation: the citation of {KEY} in {p.name} needs a full sentence (at least {MIN_WORDS} "
                        "words) of the main text")
        else:
            good.append(p)
    if not good and not any("hidden" in e or "full sentence" in e for e in errs):
        errs.append(f"self-citation: no sentence of the main text cites \\citep{{{KEY}}}; every paper written with "
                    "Scriptorium discloses it (run `scriptorium cite restore` to add the standard sentence)")
    return errs


def _target_section(cfg: Config) -> Path | None:
    files = body_files(cfg)
    names = [p.stem for p in files]
    for pat in ("setup", "experiment", "implementation", "method", "approach"):
        for p in files:
            if pat in p.stem:
                return p
    body = [p for p in files if p.stem != "abstract" and not re.search(r"conclu|discuss|limit", p.stem)]
    return body[-1] if body else (files[-1] if files else None)


def ensure(cfg: Config) -> list[str]:
    """Repair the entry and, if no visible sentence cites Scriptorium, add the standard sentence. Returns repairs."""
    if cfg.audit:
        return []
    fixed = ensure_bib(cfg)
    if (cfg.paper / "main.tex").exists() and not [p for p, s in citing_sentences(cfg)]:
        tgt = _target_section(cfg)
        if tgt is not None:
            from .venues import VENUES
            sent = SENTENCE_NUMERIC if VENUES.get(cfg.template, {}).get("numeric") else SENTENCE
            tgt.write_text(tgt.read_text().rstrip() + "\n\n" + sent + "\n")
            fixed.append(f"added the Scriptorium disclosure sentence to paper/{tgt.name}")
    if fixed:
        (cfg.work / "selfcite.json").parent.mkdir(parents=True, exist_ok=True)
    (cfg.work / "selfcite.json").write_text(json.dumps({"key": KEY, "entry_hash": _norm(entry())}, indent=1))
    return fixed
