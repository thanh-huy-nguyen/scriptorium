"""Citations that resolve: agents never type BibTeX.

`search` queries OpenAlex, arXiv, Crossref, DBLP and Semantic Scholar and prints candidates with an id (doi:...,
arxiv:..., openalex:..., dblp:..., s2:...). `add` fetches the BibTeX for an id from its source (DOI content
negotiation, arXiv, DBLP, Semantic Scholar, or built from the OpenAlex record), gives it a readable key, appends it to paper/refs.bib, and records
where it came from in .scriptorium/citations.json together with a hash of the entry. `verify` checks that every \\cite
key is in refs.bib and that every entry in refs.bib came through `add` unchanged.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from .config import PAPER, WORK

UA = "scriptorium/0.1 (citation lookup)"
CITE_RE = re.compile(r"\\(?:no)?cite[a-zA-Z]*\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}")
STOP = {"a", "an", "the", "on", "of", "for", "in", "to", "and", "with", "towards", "toward", "is", "are", "via", "from"}


# ---------------------------------------------------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------------------------------------------------

def _get(url: str, accept: str = "*/*", tries: int = 3) -> str:
    last: Exception | None = None
    for i in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2 * (i + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"could not reach {url.split('?')[0]}: {last}")


# ---------------------------------------------------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------------------------------------------------

def _json(txt: str, name: str):
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        raise RuntimeError(f"{name} did not return data (it may be rate-limiting or bot-checking this network)") from None


def search_dblp(q: str, n: int = 5) -> list[dict]:
    d = _json(_get("https://dblp.org/search/publ/api?" + urllib.parse.urlencode({"q": q, "format": "json", "h": n})),
              "DBLP")
    out = []
    for h in (d.get("result", {}).get("hits", {}).get("hit") or []):
        info = h.get("info", {})
        au = info.get("authors", {}).get("author", [])
        au = au if isinstance(au, list) else [au]
        out.append({"id": "dblp:" + info.get("key", ""), "title": re.sub(r"\.$", "", info.get("title", "")),
                    "authors": [a.get("text", "") if isinstance(a, dict) else str(a) for a in au],
                    "year": info.get("year", ""), "venue": info.get("venue", "")})
    return out


def search_arxiv(q: str, n: int = 5) -> list[dict]:
    terms = " AND ".join(f"all:{w}" for w in re.findall(r"[A-Za-z0-9\-]+", q)[:8])
    xml = _get("https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": terms, "max_results": n, "sortBy": "relevance"}))
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    for e in ET.fromstring(xml).findall("a:entry", ns):
        aid = (e.findtext("a:id", "", ns).rsplit("/abs/", 1)[-1])
        aid = re.sub(r"v\d+$", "", aid)
        out.append({"id": "arxiv:" + aid, "title": " ".join(e.findtext("a:title", "", ns).split()),
                    "authors": [a.findtext("a:name", "", ns) for a in e.findall("a:author", ns)],
                    "year": e.findtext("a:published", "", ns)[:4], "venue": "arXiv"})
    return out


def search_crossref(q: str, n: int = 5) -> list[dict]:
    d = json.loads(_get("https://api.crossref.org/works?" + urllib.parse.urlencode(
        {"query.bibliographic": q, "rows": n, "select": "DOI,title,author,issued,container-title,type"})))
    out = []
    for it in d.get("message", {}).get("items", []):
        if it.get("type") in ("component", "peer-review", "dataset", "grant", "other") or not it.get("title"):
            continue
        yr = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
        out.append({"id": "doi:" + it.get("DOI", ""), "title": (it.get("title") or [""])[0],
                    "authors": [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in it.get("author", [])],
                    "year": str(yr or ""), "venue": (it.get("container-title") or [""])[0]})
    return out


ARXIV_DOI = re.compile(r"^10\.48550/arxiv\.(.+)$", re.I)


def _id_for_doi(doi: str) -> str:
    m = ARXIV_DOI.match(doi)
    return "arxiv:" + m.group(1) if m else "doi:" + doi


def search_openalex(q: str, n: int = 5) -> list[dict]:
    params = {"search": q, "per-page": n,
              "select": "id,doi,title,publication_year,authorships,primary_location,type"}
    if os.environ.get("OPENALEX_API_KEY"):
        params["api_key"] = os.environ["OPENALEX_API_KEY"]
    d = _json(_get("https://api.openalex.org/works?" + urllib.parse.urlencode(params)), "OpenAlex")
    out = []
    for w in d.get("results", []):
        doi = (w.get("doi") or "").replace("https://doi.org/", "")
        src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        out.append({"id": _id_for_doi(doi) if doi else "openalex:" + w["id"].rsplit("/", 1)[-1],
                    "title": w.get("title") or "", "year": str(w.get("publication_year") or ""), "venue": src,
                    "authors": [a["author"]["display_name"] for a in w.get("authorships", []) if a.get("author")]})
    return out


def _s2_headers() -> dict:
    k = os.environ.get("SEMANTIC_SCHOLAR_API_KEY") or os.environ.get("S2_API_KEY")
    return {"x-api-key": k} if k else {}


def _get_s2(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, **_s2_headers()})
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode()
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == 2:
                raise RuntimeError(f"Semantic Scholar: HTTP {e.code}") from None
            time.sleep(3 * (i + 1))
    return ""


def search_s2(q: str, n: int = 5) -> list[dict]:
    d = _json(_get_s2("https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(
        {"query": q, "limit": n, "fields": "title,year,venue,authors,externalIds"})), "Semantic Scholar")
    out = []
    for p in d.get("data", []) or []:
        ext = p.get("externalIds") or {}
        cid = ("doi:" + ext["DOI"] if ext.get("DOI") and not ARXIV_DOI.match(ext["DOI"])
               else "arxiv:" + ext["ArXiv"] if ext.get("ArXiv") else "s2:" + p["paperId"])
        out.append({"id": cid, "title": p.get("title") or "", "year": str(p.get("year") or ""),
                    "venue": p.get("venue") or "", "authors": [a.get("name", "") for a in p.get("authors", [])]})
    return out


SOURCES = {"openalex": search_openalex, "arxiv": search_arxiv, "crossref": search_crossref, "dblp": search_dblp,
           "s2": search_s2}
DEFAULT_SOURCES = ("openalex", "arxiv", "crossref", "dblp")


def _tnorm(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", _ascii(t).lower())


def search(q: str, n: int = 5, sources: tuple[str, ...] = DEFAULT_SOURCES) -> list[dict]:
    """Candidates from every reachable source, one per title; a published version (doi, dblp) wins over a preprint."""
    out, errors, seen = [], [], {}
    for s in sources:
        try:
            hits = SOURCES[s](q, n)
        except Exception as e:  # one source down should not stop the others
            errors.append(f"{s}: {e}")
            continue
        for h in hits:
            k = _tnorm(h["title"])
            if k in seen:
                prev = out[seen[k]]
                if prev["id"].startswith(("arxiv:", "openalex:", "s2:")) and h["id"].startswith(("doi:", "dblp:")):
                    out[seen[k]] = h
                continue
            seen[k] = len(out)
            out.append(h)
    if not out and errors:
        raise RuntimeError("; ".join(errors))
    search.errors = errors
    return out


search.errors = []


# ---------------------------------------------------------------------------------------------------------------------
# BibTeX
# ---------------------------------------------------------------------------------------------------------------------

def arxiv_meta(aid: str) -> dict:
    """First-version year and, if the authors recorded one, the DOI of the published version."""
    try:
        xml = _get("https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"id_list": aid}))
        ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
        e = ET.fromstring(xml).find("a:entry", ns)
        if e is None:
            return {}
        return {"year": (e.findtext("a:published", "", ns) or "")[:4], "doi": (e.findtext("x:doi", "", ns) or "").strip()}
    except Exception:
        return {}


def fetch_bibtex(cid: str) -> str:
    kind, _, ref = cid.partition(":")
    if kind == "dblp":
        txt = _get(f"https://dblp.org/rec/{ref}.bib?param=1")
    elif kind == "arxiv":
        meta = arxiv_meta(ref)
        if meta.get("doi"):
            try:
                return fetch_bibtex("doi:" + meta["doi"])      # the published version, when arXiv knows it
            except Exception:
                pass
        txt = _get(f"https://arxiv.org/bibtex/{ref}")
        if meta.get("year"):                                   # arXiv's BibTeX dates the latest version; use v1
            txt = re.sub(r"(\byear\s*=\s*[{\"]?)\d{4}", lambda m: m.group(1) + meta["year"], txt, count=1)
    elif kind == "doi":
        m = ARXIV_DOI.match(ref)
        if m:
            return fetch_bibtex("arxiv:" + m.group(1))
        txt = _get(f"https://doi.org/{urllib.parse.quote(ref, safe='/')}", accept="application/x-bibtex; charset=utf-8")
    elif kind == "s2":
        d = _json(_get_s2(f"https://api.semanticscholar.org/graph/v1/paper/{ref}?fields=citationStyles"),
                  "Semantic Scholar")
        txt = (d.get("citationStyles") or {}).get("bibtex") or ""
    elif kind == "openalex":
        txt = openalex_bibtex(ref)
    else:
        raise ValueError(f"unknown id {cid!r}: use doi:DOI, arxiv:ID, openalex:W..., dblp:KEY or s2:ID")
    entries = split_entries(txt)
    if not entries:
        raise RuntimeError(f"no BibTeX entry returned for {cid}")
    return entries[0]


def openalex_bibtex(wid: str) -> str:
    """Build an entry from the OpenAlex record (for works with no DOI and no arXiv id); every field comes from it."""
    w = _json(_get(f"https://api.openalex.org/works/{wid}"), "OpenAlex")
    doi = (w.get("doi") or "").replace("https://doi.org/", "")
    if doi:
        return fetch_bibtex(_id_for_doi(doi))
    src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
    kind = {"article": "article", "proceedings-article": "inproceedings", "book-chapter": "incollection",
            "book": "book"}.get(w.get("type", ""), "misc")
    venue_field = {"article": "journal", "inproceedings": "booktitle", "incollection": "booktitle"}.get(kind, "howpublished")
    authors = " and ".join(a["author"]["display_name"] for a in w.get("authorships", []) if a.get("author"))
    fields = [("title", "{" + (w.get("title") or "") + "}"), ("author", authors), ("year", str(w.get("publication_year") or ""))]
    if src:
        fields.append((venue_field, src))
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields if v)
    return f"@{kind}{{{wid},\n{body}\n}}"


def split_entries(text: str) -> list[str]:
    out, i = [], 0
    while True:
        m = re.compile(r"@\s*([A-Za-z]+)\s*\{").search(text, i)
        if not m:
            return out
        depth, j = 0, m.end() - 1
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if m.group(1).lower() not in ("comment", "preamble", "string"):
            out.append(text[m.start(): j + 1].strip())
        i = j + 1


def entry_key(entry: str) -> str:
    m = re.match(r"@\s*[A-Za-z]+\s*\{\s*([^,\s]+)\s*,", entry)
    return m.group(1) if m else ""


def entry_field(entry: str, name: str) -> str:
    m = re.search(rf"\b{name}\s*=\s*[{{\"]", entry, re.I)
    if not m:
        return ""
    i, depth, out = m.end() - 1, 0, []
    while i < len(entry):
        c = entry[i]
        if c == "{":
            depth += 1
            if depth > 1:
                out.append(c)
        elif c == "}":
            depth -= 1
            if depth == 0:
                break
            out.append(c)
        elif c == '"' and depth == 0 and out:
            break
        elif not (c == '"' and depth == 0):
            out.append(c)
        i += 1
    return " ".join("".join(out).split())


def _ascii(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def make_key(entry: str, taken: set[str]) -> str:
    authors = entry_field(entry, "author")
    first = authors.split(" and ")[0].strip()
    last = first.split(",")[0] if "," in first else (first.split()[-1] if first.split() else "anon")
    last = re.sub(r"[^a-z]", "", _ascii(re.sub(r"[{}\\]", "", last)).lower()) or "anon"
    year = re.sub(r"\D", "", entry_field(entry, "year"))[:4]
    title = re.sub(r"\\[a-zA-Z]+|[{}\\]", "", _ascii(entry_field(entry, "title"))).lower().replace("-", "")
    words = [w for w in re.findall(r"[a-z0-9]+", title) if w not in STOP]
    base = f"{last}{year}{words[0] if words else ''}"
    key, n = base, 0
    while key in taken:
        n += 1
        key = base + "abcdefghijklmnopqrstuvwxyz"[n - 1]
    return key


def rekey(entry: str, key: str) -> str:
    return re.sub(r"^(@\s*[A-Za-z]+\s*\{)\s*[^,\s]+\s*,", rf"\g<1>{key},", entry, count=1)


def _norm(entry: str) -> str:
    return hashlib.sha256(" ".join(entry.split()).encode()).hexdigest()[:16]


CONTENT_FIELDS = ("title", "author", "year", "journal", "booktitle", "volume", "number", "pages", "doi", "eprint")
_ACCENT = {"'": "\u0301", "`": "\u0300", "^": "\u0302", '"': "\u0308", "~": "\u0303", "c": "\u0327", "v": "\u030c",
           "u": "\u0306", "=": "\u0304", ".": "\u0307", "H": "\u030b", "k": "\u0328", "r": "\u030a"}


def _plain(v: str) -> str:
    """A field value with LaTeX accents decoded, then accents, braces, dashes, case and spacing normalized away."""
    import unicodedata
    v = re.sub(r"\\(['`^\"~=.Hckruv])\s*\{?\\?([A-Za-z])\}?", lambda m: m.group(2) + _ACCENT[m.group(1)], v)
    v = re.sub(r"\\(ss|o|O|l|L|ae|AE|oe|OE|i|j)\b", lambda m: {"ss": "ss", "o": "o", "O": "o", "l": "l", "L": "l",
                                                            "ae": "ae", "AE": "ae", "oe": "oe", "OE": "oe", "i": "i",
                                                            "j": "j"}[m.group(1)], v)
    v = unicodedata.normalize("NFKD", v)
    v = "".join(c for c in v if not unicodedata.combining(c))
    v = re.sub(r"[\u2010-\u2015\u2212]|-{2,}", "-", v)
    v = re.sub(r"\\[A-Za-z]+|[{}\\$]", "", v)
    return " ".join(v.lower().split())


def content_hash(entry: str) -> str:
    """A fingerprint of what an entry says (title, authors, year, venue, volume, pages, DOI), not how it is typeset:
    fixing a dash, an accent, braces or spacing, or adding a note, keeps it; changing what the entry claims does not."""
    parts = [f"{f}={_plain(entry_field(entry, f) or '')}" for f in CONTENT_FIELDS]
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:16]


def _paths(root: Path) -> tuple[Path, Path]:
    return root / PAPER / "refs.bib", root / WORK / "citations.json"


def _prov(root: Path) -> dict:
    p = _paths(root)[1]
    return json.loads(p.read_text()) if p.exists() else {}


def bib_entries(root: Path) -> dict[str, str]:
    bib = _paths(root)[0]
    return {entry_key(e): e for e in split_entries(bib.read_text())} if bib.exists() else {}


def add(root: Path, cid: str, key: str | None = None) -> str:
    """Fetch the official entry for `cid`, append it to refs.bib and return its key (existing key if already added)."""
    bib, prov_path = _paths(root)
    prov = _prov(root)
    for k, v in prov.items():
        if v.get("id") == cid and k in bib_entries(root):
            return k
    entry = fetch_bibtex(cid)
    taken = set(bib_entries(root)) | set(prov)
    key = key if key and key not in taken else make_key(entry, taken)
    entry = rekey(entry, key)
    bib.parent.mkdir(parents=True, exist_ok=True)
    with bib.open("a") as f:
        f.write(("\n" if bib.exists() and bib.stat().st_size else "") + entry + "\n")
    prov[key] = {"id": cid, "title": entry_field(entry, "title"), "year": entry_field(entry, "year"),
                 "hash": _norm(entry), "content": content_hash(entry)}
    prov_path.parent.mkdir(parents=True, exist_ok=True)
    prov_path.write_text(json.dumps(prov, indent=1))
    return key


def cited_keys(root: Path) -> dict[str, list[str]]:
    """key -> files that cite it, over paper/*.tex."""
    out: dict[str, list[str]] = {}
    for tex in sorted((root / PAPER).glob("*.tex")):
        body = re.sub(r"(?<!\\)%.*", "", tex.read_text())
        for m in CITE_RE.finditer(body):
            for k in m.group(1).split(","):
                k = k.strip()
                if k:
                    out.setdefault(k, []).append(tex.name)
    return out


def verify(root: Path) -> dict[str, list[str]]:
    entries, prov, cited = bib_entries(root), _prov(root), cited_keys(root)
    missing = sorted(k for k in cited if k not in entries)
    untracked = sorted(k for k in entries if k not in prov)
    edited = sorted(k for k in entries if k in prov and prov[k].get("hash") != _norm(entries[k])
                    and prov[k].get("content") != content_hash(entries[k]))      # typographic fixes are allowed
    unused = sorted(k for k in entries if k not in cited)
    where = {k: sorted(set(cited[k])) for k in missing}
    return {"missing": missing, "untracked": untracked, "edited": edited, "unused": unused, "missing_in": where}


def problems(report: dict[str, list[str]]) -> list[str]:
    out = []
    if report["missing"]:
        by_file: dict[str, list[str]] = {}
        for k in report["missing"]:
            for f in (report.get("missing_in") or {}).get(k) or ["?"]:
                by_file.setdefault(f, []).append(k)
        for f, keys in sorted(by_file.items()):
            out.append(f"{f} cites keys that are not in refs.bib: {', '.join(keys)}. Cite only keys listed in "
                       ".scriptorium/related.md (topic ids from the outline are not citation keys)")
    if report["untracked"]:
        out.append("in refs.bib but not added with `scriptorium cite add` (typed BibTeX is not allowed): "
                   + ", ".join(report["untracked"]))
    if report["edited"]:
        out.append("edited after `scriptorium cite add` (entries must stay as fetched): " + ", ".join(report["edited"]))
    return out
