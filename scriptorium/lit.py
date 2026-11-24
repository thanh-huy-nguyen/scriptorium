"""The literature team. Papers enter the pool only through real searches, are read from abstracts that code fetched,
and every citation in the paper is checked against what the cited paper says.

    search     searcher         queries from the brief and the inventory; shortlists papers from the search pool
                                (.scriptorium/lit/shortlist.json; every id must have come back from a search)
    read       readers          one per batch of papers, in parallel; one card per paper with a quote that code
                                finds in the fetched abstract (.scriptorium/lit/cards/*.json)
    citecheck  citation auditor every (sentence, cited paper) pair: supported, unsupported or unverifiable
                                (.scriptorium/lit/citecheck.json); the line editors must fix the rest

Search runs right after the scout, alongside the evidence work, so the architects know the field when they pitch.
"""
from __future__ import annotations

import json
import re
import urllib.parse
from pathlib import Path

from . import cite
from . import stages as S
from .config import Config
from .runner import Task

RELATIONS = ("baseline", "builds-on", "competing", "dataset", "tool", "background", "evaluation")
CITE_VERDICTS = ("supported", "unsupported", "unverifiable")
BATCH = 6


def lit_dir(cfg: Config) -> Path:
    return cfg.work / "lit"


def slug(cid: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", cid)[:120]


def _ws(t: str) -> str:
    return re.sub(r"\s+", " ", t or "").strip().lower()


# ---------------------------------------------------------------------------------------------------------------------
# The pool: every search result, recorded by code

def record(root: Path, query: str, hits: list[dict]) -> None:
    p = root / ".scriptorium" / "lit" / "pool.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        pool = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        pool = {}
    for h in hits:
        rec = pool.setdefault(h["id"], {k: h.get(k) for k in ("id", "title", "year", "venue", "authors")})
        rec.setdefault("queries", [])
        if query not in rec["queries"]:
            rec["queries"].append(query)
    p.write_text(json.dumps(pool, indent=1))


def pool(cfg: Config) -> dict:
    return S.read_json(lit_dir(cfg) / "pool.json") or {}


# ---------------------------------------------------------------------------------------------------------------------
# Abstracts, fetched by code

def _openalex_abstract(work: dict) -> str:
    inv = work.get("abstract_inverted_index") or {}
    pos = sorted((i, w) for w, idx in inv.items() for i in idx)
    return " ".join(w for _, w in pos)


def _from_openalex(ref: str) -> dict | None:
    w = cite._json(cite._get("https://api.openalex.org/works/" + urllib.parse.quote(ref, safe=":/")), "OpenAlex")
    ab = _openalex_abstract(w)
    return {"title": w.get("title") or "", "year": str(w.get("publication_year") or ""), "abstract": ab,
            "source": "openalex"} if ab else None


def _from_arxiv(aid: str) -> dict | None:
    import xml.etree.ElementTree as ET
    xml = cite._get("https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"id_list": aid}))
    ns = {"a": "http://www.w3.org/2005/Atom"}
    e = ET.fromstring(xml).find("a:entry", ns)
    ab = re.sub(r"\s+", " ", e.findtext("a:summary", "", ns) or "").strip() if e is not None else ""
    return {"title": re.sub(r"\s+", " ", e.findtext("a:title", "", ns) or "").strip(),
            "year": (e.findtext("a:published", "", ns) or "")[:4], "abstract": ab, "source": "arxiv"} if ab else None


def _from_s2(ref: str) -> dict | None:
    d = cite._json(cite._get_s2(f"https://api.semanticscholar.org/graph/v1/paper/{ref}?fields=title,year,abstract"),
                   "Semantic Scholar")
    ab = d.get("abstract") or ""
    return {"title": d.get("title") or "", "year": str(d.get("year") or ""), "abstract": ab, "source": "s2"} if ab else None


def fetch_abstract(cid: str) -> dict:
    """{title, year, abstract, source, errors} for an id. Tries every source that can know the paper, so one source
    rate-limiting this network (arXiv often does) does not leave a paper without its abstract."""
    kind, _, val = cid.partition(":")
    tries = {"arxiv": [(_from_openalex, f"https://doi.org/10.48550/arXiv.{val}"), (_from_arxiv, val),
                       (_from_s2, f"ARXIV:{val}")],
             "doi": [(_from_openalex, f"https://doi.org/{val}"), (_from_s2, f"DOI:{val}")],
             "openalex": [(_from_openalex, val)],
             "s2": [(_from_s2, val)],
             "dblp": []}.get(kind, [])
    errors = []
    for fn, ref in tries:
        try:
            d = fn(ref)
        except Exception as e:  # noqa: BLE001  try the next source
            errors.append(f"{fn.__name__[6:]}: {str(e)[:120]}")
            continue
        if d:
            return {**d, "errors": errors}
    return {"title": "", "year": "", "abstract": "", "source": "", "errors": errors}


def abstract(cfg: Config, cid: str, refresh: bool = False) -> dict:
    p = lit_dir(cfg) / "abstracts" / f"{slug(cid)}.json"
    if p.exists() and not refresh:
        return json.loads(p.read_text())
    d = {"id": cid, **fetch_abstract(cid)}
    if not d["abstract"] and d.get("errors"):
        return d                   # a network failure is not kept, so the next call tries again
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=1))
    return d


# ---------------------------------------------------------------------------------------------------------------------
# Stages

class Search(S.Stage):
    max_fix = 2
    MIN = 12

    def before(self, cfg):
        lit_dir(cfg).mkdir(parents=True, exist_ok=True)

    def tasks(self, cfg):
        return [Task("searcher", "search", S.context(cfg) + (
            "Task: map the literature this work sits in. Search with `scriptorium cite search` (every result is "
            "recorded in .scriptorium/lit/pool.json) and write .scriptorium/lit/shortlist.json with the "
            f"{self.MIN} to 40 papers the paper will most likely need, as your instructions describe. Run "
            "`scriptorium validate .scriptorium/lit/shortlist.json` and fix every problem."))]

    def validate(self, cfg):
        return shortlist_problems(cfg, self.MIN)


def shortlist(cfg: Config) -> list[dict]:
    d = S.read_json(lit_dir(cfg) / "shortlist.json") or {}
    return [p for p in d.get("papers", []) if isinstance(p, dict) and p.get("id")]


def shortlist_problems(cfg: Config, minimum: int = 12) -> list[str]:
    d = S.read_json(lit_dir(cfg) / "shortlist.json")
    if d is None:
        return [".scriptorium/lit/shortlist.json is missing or is not valid JSON"]
    errs = []
    pl = pool(cfg)
    papers = d.get("papers") or []
    if len(papers) < minimum:
        errs.append(f"shortlist.json has {len(papers)} papers; find at least {minimum}")
    ids = [p.get("id") for p in papers]
    if len(set(ids)) != len(ids):
        errs.append("each paper is listed once")
    for p in papers:
        if p.get("id") not in pl:
            errs.append(f"{p.get('id')!r} never came back from `scriptorium cite search`; shortlist only search results")
        if p.get("relation") not in RELATIONS:
            errs.append(f"{p.get('id')}: relation must be one of {', '.join(RELATIONS)}")
        if not p.get("why"):
            errs.append(f"{p.get('id')}: say `why` the paper matters to this work")
    if not d.get("topics"):
        errs.append("list the `topics` the literature splits into")
    return errs


def card_path(cfg: Config, cid: str) -> Path:
    return lit_dir(cfg) / "cards" / f"{slug(cid)}.json"


def card(cfg: Config, cid: str) -> dict:
    return S.read_json(card_path(cfg, cid)) or {}


def card_problems(cfg: Config, cid: str) -> list[str]:
    p = card_path(cfg, cid)
    c = S.read_json(p)
    if c is None:
        return [f"card for {cid} is missing ({p.relative_to(cfg.root)})"]
    errs = []
    for k in ("id", "title", "summary", "relation"):
        if not c.get(k):
            errs.append(f"card {cid}: missing `{k}`")
    if c.get("relation") and c["relation"] not in RELATIONS:
        errs.append(f"card {cid}: relation must be one of {', '.join(RELATIONS)}")
    ab = abstract_cached(cfg, cid)
    if ab is None and c.get("unverifiable"):
        return errs                # no source returned the abstract; the card says so
    if ab is None:
        errs.append(f"card {cid}: fetch the abstract first with `scriptorium cite abstract {cid}`; if no source "
                    "returns it, set \"unverifiable\": true")
    elif ab.get("abstract"):
        for q in c.get("quotes") or []:
            if _ws(q) not in _ws(ab["abstract"]):
                errs.append(f"card {cid}: the quote {q[:60]!r} is not in the fetched abstract; copy it exactly")
        if not c.get("quotes"):
            errs.append(f"card {cid}: quote at least one sentence of the abstract that backs the summary")
    elif not c.get("unverifiable"):
        errs.append(f"card {cid}: no abstract could be fetched; set \"unverifiable\": true")
    return errs


def abstract_cached(cfg: Config, cid: str) -> dict | None:
    return S.read_json(lit_dir(cfg) / "abstracts" / f"{slug(cid)}.json")


class Read(S.Stage):
    max_fix = 2

    def batches(self, cfg) -> list[list[dict]]:
        sl = shortlist(cfg)
        return [sl[i:i + BATCH] for i in range(0, len(sl), BATCH)]

    def task_for(self, cfg, i, batch, extra=""):
        ids = "\n".join(f"- {p['id']}: {pool(cfg).get(p['id'], {}).get('title', '')}" for p in batch)
        return Task("reader", f"read-{i + 1}", S.context(cfg) + (
            f"Task: read these papers and write one card each in .scriptorium/lit/cards/, as your instructions "
            f"describe:\n{ids}\nFetch each abstract with `scriptorium cite abstract ID`; quote it exactly." + extra))

    def tasks(self, cfg):
        """Only batches with a missing or failing card: a rerun does not reread papers already carded."""
        (lit_dir(cfg) / "cards").mkdir(parents=True, exist_ok=True)
        return [self.task_for(cfg, i, b) for i, b in enumerate(self.batches(cfg))
                if any(card_problems(cfg, p["id"]) for p in b)]

    def validate(self, cfg):
        return [e for p in shortlist(cfg) for e in card_problems(cfg, p["id"])]

    def fix_tasks(self, cfg, errors):
        out = []
        for i, b in enumerate(self.batches(cfg)):
            mine = [e for e in errors if any(p["id"] in e for p in b)]
            if mine:
                t = self.task_for(cfg, i, b, "\n\nFix these problems:\n- " + "\n- ".join(mine))
                t.label += "-fix"
                out.append(t)
        return out

    def after(self, cfg):
        render_cards(cfg)

    def on_fail(self, cfg, errors):
        """Cards that still fail are left out of cards.md; the literature never stops the paper."""
        bad = {p["id"] for p in shortlist(cfg) if card_problems(cfg, p["id"])}
        (lit_dir(cfg) / "dropped.json").write_text(json.dumps(sorted(bad), indent=1))
        return "continue"


def render_cards(cfg: Config) -> None:
    d = S.read_json(lit_dir(cfg) / "shortlist.json") or {}
    lines = ["# What the literature says (one card per paper, from its abstract)\n"]
    for topic in d.get("topics") or ["papers"]:
        rows = [p for p in shortlist(cfg) if p.get("topic", topic) == topic or topic == "papers"]
        if not rows:
            continue
        lines.append(f"## {topic}\n")
        dropped = set(S.read_json(lit_dir(cfg) / "dropped.json") or [])
        for p in rows:
            if p["id"] in dropped:
                continue
            c = card(cfg, p["id"])
            lines.append(f"- `{p['id']}` {c.get('title', '')} ({c.get('year', '')}), {c.get('relation', '')}: "
                         f"{c.get('summary', '')}" + (" (abstract unavailable)" if c.get("unverifiable") else ""))
        lines.append("")
    (lit_dir(cfg) / "cards.md").write_text("\n".join(lines))


# ---------------------------------------------------------------------------------------------------------------------
# Citation check

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\\])")


def citing_sentences(cfg: Config) -> list[dict]:
    """Every (file, sentence, key) where a sentence cites a key, in reading order."""
    out = []
    for p in sorted(cfg.paper.glob("*.tex")):
        if p.name == "main.tex" or p.name.startswith("table_"):
            continue
        body = re.sub(r"\s+", " ", re.sub(r"(?<!\\)%.*", "", p.read_text()))
        for sent in SENT_SPLIT.split(body):
            for m in cite.CITE_RE.finditer(sent):
                for k in m.group(1).split(","):
                    if k.strip():
                        out.append({"file": p.name, "sentence": sent.strip(), "key": k.strip()})
    return out


def key_card(cfg: Config, key: str) -> tuple[str, dict, dict | None]:
    """The cited key's id, its card and its fetched abstract."""
    cid = (cite._prov(cfg.root).get(key) or {}).get("id", "")
    return cid, card(cfg, cid) if cid else {}, abstract_cached(cfg, cid) if cid else None


class CiteCheck(S.Stage):
    max_fix = 2

    def before(self, cfg):
        todo = citing_sentences(cfg)
        lit_dir(cfg).mkdir(parents=True, exist_ok=True)
        (lit_dir(cfg) / "citations_todo.json").write_text(json.dumps(todo, indent=1))

    def tasks(self, cfg):
        n = len(citing_sentences(cfg))
        if not n:
            return []
        return [Task("cite_auditor", "citecheck", S.context(cfg) + (
            f"Task: check all {n} citations listed in .scriptorium/lit/citations_todo.json (each sentence with one "
            "cited key). For each, read what the cited paper says with `scriptorium cite card KEY` and decide whether "
            "it supports the sentence. Write .scriptorium/lit/citecheck.json as your instructions describe. Do not "
            "edit the paper. Run `scriptorium validate .scriptorium/lit/citecheck.json` and fix every problem."))]

    def validate(self, cfg):
        return citecheck_problems(cfg)


def citecheck_problems(cfg: Config) -> list[str]:
    todo = citing_sentences(cfg)
    if not todo:
        return []
    d = S.read_json(lit_dir(cfg) / "citecheck.json")
    if d is None:
        return [".scriptorium/lit/citecheck.json is missing or is not valid JSON"]
    errs = []
    done = set()
    for i, f in enumerate(d.get("findings") or [], 1):
        if f.get("verdict") not in CITE_VERDICTS:
            errs.append(f"finding {i}: verdict must be one of {', '.join(CITE_VERDICTS)}")
        if f.get("verdict") in ("unsupported", "unverifiable") and not f.get("fix"):
            errs.append(f"finding {i}: an {f.get('verdict')} citation needs a `fix`")
        if f.get("verdict") == "supported" and not f.get("evidence"):
            errs.append(f"finding {i}: say which part of the cited paper supports the sentence in `evidence`")
        done.add((f.get("file"), _ws(f.get("quote", "")), f.get("key")))
    missing = [t for t in todo if not any(fl == t["file"] and k == t["key"] and q and q in _ws(t["sentence"])
                                          for fl, q, k in done)]
    for t in missing[:15]:
        errs.append(f"no finding for \\cite{{{t['key']}}} in {t['file']}: \"{t['sentence'][:90]}\"")
    if len(missing) > 15:
        errs.append(f"... and {len(missing) - 15} more citations without a finding")
    return errs


def open_citations(cfg: Config, file: str | None = None) -> list[dict]:
    d = S.read_json(lit_dir(cfg) / "citecheck.json") or {}
    return [f for f in d.get("findings") or [] if f.get("verdict") in ("unsupported", "unverifiable")
            and (file is None or str(f.get("file", "")).removesuffix(".tex") == file)]
