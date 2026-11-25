"""Resolve every cited reference in public bibliographic databases.

Verdicts per cited entry:
    found          a record with this title exists, and its year and first author agree
    wrong metadata the record exists, but the year (off by more than one) or the first author differs
    not found      no record with a title this close in Crossref, OpenAlex or arXiv
Requests carry a generic client name and no personal details.
"""
from __future__ import annotations

import difflib
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from common import body, main_tex

UA = {"User-Agent": "repowrite-checker/0.1 (research benchmark)"}


def _get(url: str, tries: int = 3):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001  rate limits and network errors: wait and retry
            time.sleep(3 * (k + 1))
    return None


def norm(t: str) -> str:
    t = re.sub(r"\\[a-zA-Z]+\s*", " ", t)
    return re.sub(r"[^a-z0-9 ]", "", re.sub(r"[{}]", "", t.lower())).strip()


def parse_bib(text: str) -> dict[str, dict]:
    out = {}
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)(?=\n@|\Z)", text, re.S):
        typ, key, rest = m.group(1).lower(), m.group(2), m.group(3)
        if typ in ("comment", "string", "preamble"):
            continue
        f = {}
        for fm in re.finditer(r"(\w+)\s*=\s*(\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}|\"[^\"]*\"|\d+)", rest):
            f[fm.group(1).lower()] = fm.group(2).strip("{}\"").strip()
        out[key] = {"type": typ, **f}
    return out


def cited_keys(paper: Path) -> list[str]:
    keys = []
    for m in re.finditer(r"\\(?:no)?cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", body(paper)):
        for k in m.group(1).split(","):
            k = k.strip()
            if k and k not in keys:
                keys.append(k)
    return keys


def bib_text(paper: Path) -> str:
    tex = main_tex(paper).read_text(errors="replace")
    names = re.findall(r"\\(?:bibliography|addbibresource)\{([^}]*)\}", tex)
    files = [paper / (n if n.endswith(".bib") else n + ".bib") for ns in names for n in ns.split(",")]
    files = [f for f in files if f.exists()] or sorted(paper.glob("*.bib"))
    return "\n".join(f.read_text(errors="replace") for f in files)


def surname(author_field: str) -> str:
    a = author_field.split(" and ")[0].strip()
    a = a.split(",")[0] if "," in a else (a.split()[-1] if a.split() else a)
    return norm(a)


def lookup(title: str) -> list[dict]:
    """Candidate records {title, year, first} from Crossref, then OpenAlex, then arXiv."""
    q = urllib.parse.quote(title)
    out = []
    r = _get(f"https://api.crossref.org/works?query.bibliographic={q}&rows=5&select=title,author,issued")
    if r:
        for it in json.loads(r).get("message", {}).get("items", []):
            yr = ((it.get("issued") or {}).get("date-parts") or [[None]])[0][0]
            au = (it.get("author") or [{}])[0].get("family", "")
            out.append({"title": (it.get("title") or [""])[0], "year": yr, "first": norm(au), "src": "crossref"})
    r = _get(f"https://api.openalex.org/works?search={q}&per-page=5&select=title,publication_year,authorships")
    if r:
        for it in json.loads(r).get("results", []):
            au = ((it.get("authorships") or [{}])[0].get("author") or {}).get("display_name", "")
            out.append({"title": it.get("title") or "", "year": it.get("publication_year"),
                        "first": norm(au.split()[-1]) if au else "", "src": "openalex"})
    r = _get("https://export.arxiv.org/api/query?max_results=5&search_query=" + urllib.parse.quote(f'ti:"{title}"'))
    if r:
        for e in re.findall(r"<entry>(.*?)</entry>", r, re.S):
            t = re.search(r"<title>(.*?)</title>", e, re.S)
            y = re.search(r"<published>(\d{4})", e)
            a = re.search(r"<name>(.*?)</name>", e)
            out.append({"title": " ".join(t.group(1).split()) if t else "", "year": int(y.group(1)) if y else None,
                        "first": norm(a.group(1).split()[-1]) if a else "", "src": "arxiv"})
    return out


def check_entry(e: dict) -> dict:
    title = e.get("title", "")
    if not title:
        return {"verdict": "not found", "why": "no title"}
    want = norm(title)
    best, score = None, 0.0
    for c in lookup(title):
        s = difflib.SequenceMatcher(None, want, norm(c["title"])).ratio()
        if s > score:
            best, score = c, s
    if not best or score < 0.9:
        return {"verdict": "not found", "closest": best and best["title"], "similarity": round(score, 2)}
    why = []
    try:
        if e.get("year") and best.get("year") and abs(int(re.sub(r"\D", "", e["year"])[:4]) - int(best["year"])) > 1:
            why.append(f"year {e['year']} vs {best['year']}")
    except ValueError:
        pass
    if e.get("author") and best.get("first") and surname(e["author"]) and surname(e["author"]) != best["first"] \
            and best["first"] not in norm(e["author"]):
        why.append(f"first author {surname(e['author'])} vs {best['first']}")
    return {"verdict": "wrong metadata" if why else "found", "why": "; ".join(why), "source": best["src"],
            "similarity": round(score, 2)}


def check_refs(paper: Path) -> list[dict]:
    bib = parse_bib(bib_text(paper))
    out = []
    for k in cited_keys(paper):
        e = bib.get(k)
        if e is None:
            out.append({"key": k, "verdict": "missing entry"})
            continue
        out.append({"key": k, "title": e.get("title", ""), **check_entry(e)})
        time.sleep(0.5)
    return out
