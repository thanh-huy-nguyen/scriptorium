"""Resolve every cited reference in public bibliographic databases.

Verdicts per cited entry:
    found          a record with this title exists, and its year and first author agree
    wrong metadata the record exists, but the year (off by more than one) or the first author differs
    not found      no record with a title this close in Crossref, OpenAlex, Semantic Scholar or arXiv, all of which
                   answered
    unverified     not found, but at least one database did not answer (rate limit); rerun later
Requests carry a generic client name and no personal details. Without a key, OpenAlex shares one free daily budget
among everyone on the network's IP address; set OPENALEX_API_KEY (free at openalex.org) to use your own.
"""
from __future__ import annotations

import difflib
import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from common import body, main_tex

UA = {"User-Agent": "repowrite-checker/0.1 (research benchmark)"}


FAILED: list[str] = []          # sources that did not answer during the current lookup


def _get(url: str, tries: int = 3):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                body_ = r.read().decode("utf-8", "replace")
                if "not a bot" in body_[:2000]:
                    break                      # a bot check, not an answer
                return body_
        except Exception:  # noqa: BLE001  rate limits and network errors: wait and retry
            time.sleep(3 * (k + 1))
    FAILED.append(urllib.parse.urlparse(url).netloc)
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
    r = _get(f"https://api.crossref.org/works?query.bibliographic={q}&rows=10&select=title,author,issued")
    if r:
        for it in json.loads(r).get("message", {}).get("items", []):
            yr = ((it.get("issued") or {}).get("date-parts") or [[None]])[0][0]
            au = (it.get("author") or [{}])[0].get("family", "")
            out.append({"title": (it.get("title") or [""])[0], "year": yr, "first": norm(au), "src": "crossref"})
    key = os.environ.get("OPENALEX_API_KEY", "")
    r = _get(f"https://api.openalex.org/works?search={q}&per-page=5&select=title,publication_year,authorships"
             + (f"&api_key={urllib.parse.quote(key)}" if key else ""))
    if r:
        for it in json.loads(r).get("results", []):
            au = ((it.get("authorships") or [{}])[0].get("author") or {}).get("display_name", "")
            out.append({"title": it.get("title") or "", "year": it.get("publication_year"),
                        "first": norm(au.split()[-1]) if au else "", "src": "openalex"})
    for url in (f"https://api.semanticscholar.org/graph/v1/paper/search/match?query={q}&fields=title,year,authors",
                f"https://api.semanticscholar.org/graph/v1/paper/search?query={q}&limit=5&fields=title,year,authors"):
        r = _get(url)
        if r:
            try:
                data = json.loads(r).get("data") or []
            except json.JSONDecodeError:
                data = []
            for it in data:
                au = (it.get("authors") or [{}])[0].get("name", "")
                out.append({"title": it.get("title") or "", "year": it.get("year"),
                            "first": norm(au.split()[-1]) if au else "", "src": "semanticscholar"})
            if data and url.find("/match?") > 0 and difflib.SequenceMatcher(None, norm(title),
                                                                           norm(data[0].get("title") or "")).ratio() > 0.9:
                break
        time.sleep(1.0)
    r = _get(f"https://dblp.org/search/publ/api?q={q}&format=json&h=8")     # often behind a bot check
    if r:
        try:
            hits = json.loads(r).get("result", {}).get("hits", {}).get("hit", []) or []
        except json.JSONDecodeError:
            hits = []
        for h in hits:
            info = h.get("info", {})
            au = (info.get("authors") or {}).get("author") or []
            au = au[0] if isinstance(au, list) and au else au
            name = au.get("text", "") if isinstance(au, dict) else str(au)
            name = re.sub(r"\s+\d{4}$", "", name)
            out.append({"title": info.get("title", "").rstrip("."), "year": int(info["year"]) if info.get("year") else None,
                        "first": norm(name.split()[-1]) if name else "", "src": "dblp"})
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
    FAILED.clear()
    scored = [(difflib.SequenceMatcher(None, want, norm(c["title"])).ratio(), c) for c in lookup(title)]
    close = [(sc, c) for sc, c in scored if sc >= 0.9]
    if not close:
        best = max(scored, key=lambda x: x[0], default=(0.0, None))
        failed = sorted(set(f for f in FAILED if "dblp" not in f))
        return {"verdict": "unverified" if failed else "not found", "why": ("lookup failed: " + ", ".join(failed))
                if failed else "", "closest": best[1] and best[1]["title"], "similarity": round(best[0], 2)}
    try:
        year = int(re.sub(r"\D", "", e.get("year", ""))[:4]) if e.get("year") else None
    except ValueError:
        year = None
    who = surname(e.get("author", "")) if e.get("author") else ""

    def problems(c):
        why = []
        if year and c.get("year") and abs(year - int(c["year"])) > 1:
            why.append(f"year {year} vs {c['year']}")
        if who and c.get("first") and who != c["first"] and c["first"] not in norm(e.get("author", "")):
            why.append(f"first author {who} vs {c['first']}")
        return why
    # the entry is right if any record with this title agrees with it (databases list reprints and later versions)
    best = min(close, key=lambda x: (len(problems(x[1])), -x[0]))
    why = problems(best[1])
    failed = sorted(set(f for f in FAILED if "dblp" not in f))
    if why and failed:                          # the record that agrees may sit in the database that did not answer
        return {"verdict": "unverified", "why": "; ".join(why) + "; lookup failed: " + ", ".join(failed),
                "source": best[1]["src"], "similarity": round(best[0], 2)}
    return {"verdict": "wrong metadata" if why else "found", "why": "; ".join(why), "source": best[1]["src"],
            "similarity": round(best[0], 2)}


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
