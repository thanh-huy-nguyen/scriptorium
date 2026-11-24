"""Venues: the official style files, fetched from the venue's own source at init, plus a Scriptorium skeleton for
main.tex (templates/<venue>/main.tex) that uses them exactly as the venue's sample paper does.

The style files are copied into paper/ unchanged. The skeleton switches between the review (anonymous) and the
camera-ready version with [paper] mode. Each venue also sets the page limit, a words-per-page budget for the outline,
and the reviewer personas.
"""
from __future__ import annotations

import io
import os
import urllib.request
import zipfile
from pathlib import Path

from .config import TEMPLATES

VENUES: dict[str, dict] = {
    "neurips": {
        "name": "NeurIPS 2025", "url": "https://media.neurips.cc/Conferences/NeurIPS2025/Styles.zip",
        "files": ["neurips_2025.sty"], "page_limit": 9, "words_per_page": 650,
        "mode": {"review": "main", "final": "main, final"}, "checklist": "neurips_2025.tex",
        "reviewers": ["soundness", "clarity", "significance", "reproducibility"]},
    "iclr": {
        "name": "ICLR 2027", "url": "https://github.com/ICLR/Master-Template/archive/refs/heads/master.zip",
        "files": ["iclr2027/iclr2027_conference.sty", "iclr2027/iclr2027_conference.bst", "iclr2027/fancyhdr.sty",
                  "iclr2027/natbib.sty", "iclr2027/math_commands.tex"],
        "page_limit": 9, "words_per_page": 650, "mode": {"review": "", "final": "\\iclrfinalcopy"},
        "reviewers": ["soundness", "clarity", "significance", "reproducibility"]},
    "icml": {
        "name": "ICML 2025", "url": "https://media.icml.cc/Conferences/ICML2025/Styles/icml2025.zip",
        "files": ["icml2025.sty", "icml2025.bst", "fancyhdr.sty", "algorithm.sty", "algorithmic.sty"],
        "page_limit": 8, "words_per_page": 520, "mode": {"review": "", "final": "accepted"},
        "requires": [{"title": "Impact Statement", "why": "ICML asks every paper for an impact statement after the "
                      "conclusion, before the references; it does not count toward the page limit"}],
        "reviewers": ["soundness", "clarity", "significance", "reproducibility"]},
    "cvpr": {
        "name": "CVPR", "url": "https://github.com/cvpr-org/author-kit/archive/refs/heads/main.zip",
        "files": ["cvpr.sty", "ieeenat_fullname.bst"], "page_limit": 8, "words_per_page": 500,
        "mode": {"review": "review", "final": ""},
        "reviewers": ["soundness", "clarity", "significance", "experiments"]},
    "acl": {
        "name": "ACL / *ACL", "url": "https://github.com/acl-org/acl-style-files/archive/refs/heads/master.zip",
        "files": ["acl.sty", "acl_natbib.bst"], "page_limit": 8, "words_per_page": 550,
        "requires": [{"title": "Limitations", "why": "ACL desk-rejects papers without a Limitations section after the "
                      "conclusion; it does not count toward the page limit"}],
        "mode": {"review": "review", "final": "final"},
        "reviewers": ["soundness", "clarity", "significance", "reproducibility"]},
    "miccai": {
        "name": "MICCAI (Springer LNCS)", "url": "https://mirrors.ctan.org/macros/latex/contrib/llncs.zip",
        "files": ["llncs.cls", "splncs04.bst"], "page_limit": 8, "words_per_page": 420, "numeric": True,
        "mode": {"review": "review", "final": "final"},
        "reviewers": ["soundness", "clinical relevance", "clarity", "validation"]},
    "ieee": {
        "name": "IEEE conference (ISBI, ICASSP, ...)", "url": "https://mirrors.ctan.org/macros/latex/contrib/IEEEtran.zip",
        "files": ["IEEEtran.cls", "bibtex/IEEEtranN.bst"], "page_limit": 4, "words_per_page": 560, "numeric": True,
        "mode": {"review": "review", "final": "final"},
        "reviewers": ["soundness", "clarity", "significance"]},
}


def cache_dir() -> Path:
    return Path(os.environ.get("SCRIPTORIUM_HOME") or Path.home() / ".scriptorium") / "templates"


def _download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "scriptorium/1.0 (template fetch)"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def fetch(venue: str, dest: Path, refresh: bool = False) -> list[str]:
    """Copy the venue's official style files into `dest` (paper/). Downloads once into ~/.scriptorium/templates.
    Returns the file names copied."""
    v = VENUES[venue]
    cache = cache_dir() / f"{venue}.zip"
    if refresh or not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(_download(v["url"]))
    z = zipfile.ZipFile(io.BytesIO(cache.read_bytes()))
    names = [n for n in z.namelist() if not n.endswith("/")]
    out = []
    if v.get("checklist") and not (dest / "checklist.tex").exists():
        sample = next((n for n in names if n.endswith("/" + v["checklist"]) or n == v["checklist"]), None)
        if sample:
            from .venuestudy import checklist_template
            dest.mkdir(parents=True, exist_ok=True)
            (dest / "checklist.tex").write_text(checklist_template(z.read(sample).decode("utf-8", "replace")))
            out.append("checklist.tex")
    for want in v["files"]:
        hits = sorted((n for n in names if n == want or n.endswith("/" + want)), key=len)
        if not hits:
            raise RuntimeError(f"{v['name']}: {want} is not in {v['url']} (the venue may have moved its files; "
                               "run with --refresh or set [paper] template to a folder)")
        dest.mkdir(parents=True, exist_ok=True)
        (dest / Path(want).name).write_bytes(z.read(hits[0]))
        out.append(Path(want).name)
    return out


def note(venue: str) -> str:
    """What writers must know about the venue's citation style."""
    v = VENUES.get(venue)
    if not v:
        return ""
    if v.get("numeric"):
        return (f"Citations in {v['name']} are numeric: write \\citep{{key}} after the claim, and name authors in "
                "the text yourself (\"Doe et al.~\\citep{key} show...\"); never \\citet.\n")
    return f"Citations in {v['name']} are author-year: \\citet{{key}} in running text, \\citep{{key}} in parentheses.\n"


def skeleton(venue: str) -> Path:
    return TEMPLATES / venue / "main.tex"


def is_venue(name: str) -> bool:
    return name in VENUES
