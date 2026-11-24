"""Venue study: learn how strong recent papers at the target venue, on this topic, are written.

For a top-tier venue Scriptorium reads the venue's own open-access proceedings index for the last two years, ranks
every title by relevance to the brief and the repository inventory, weighs relevance with citation counts from
OpenAlex, and downloads the PDFs of the top exemplars. Readers (one per exemplar, in parallel) study each paper's
framing, Figure 1, contribution list, emphasis, structure and how its results are told, with quotes that code finds in
the PDF's text. An analyst turns their notes into .scriptorium/venue_style.md, which the architects, outliner, figure
planner, writers and reviewers follow. Nothing is copied: the papers teach structure and craft, never wording.

    venuefetch  (code)   proceedings index -> ranked exemplars -> PDFs        (.scriptorium/venue/exemplars.json)
    venueread   readers  one note per exemplar, quotes checked                 (.scriptorium/venue/notes/*.json)
    venuestyle  analyst  the venue's writing playbook for this topic          (.scriptorium/venue_style.md)

Sources: CVF open access (CVPR, ICCV, WACV), proceedings.neurips.cc, PMLR (ICML), papers.miccai.org, the ACL Anthology
(ACL, EMNLP, NAACL) and, for ICLR, the conference's paper list with PDFs from arXiv (OpenReview refuses automated
downloads). Other venues skip the study and keep the built-in style guide.
"""
from __future__ import annotations

import datetime
import html
import json
import math
import os
import re
import urllib.request
from collections import Counter
from pathlib import Path

from . import cite
from . import stages as S
from .config import Config
from .runner import Task

UA = "Mozilla/5.0 (scriptorium venue study)"

SOURCES = {
    "cvpr": ("cvf", "CVPR"), "iccv": ("cvf", "ICCV"), "wacv": ("cvf", "WACV"),
    "neurips": ("nips", None), "icml": ("pmlr", None), "iclr": ("iclr", None), "miccai": ("miccai", None),
    "acl": ("acl", "acl"), "emnlp": ("acl", "emnlp"), "naacl": ("acl", "naacl"),
}
NAMES = {"cvpr": "CVPR", "iccv": "ICCV", "wacv": "WACV", "neurips": "NeurIPS", "icml": "ICML", "iclr": "ICLR",
         "miccai": "MICCAI", "acl": "ACL", "emnlp": "EMNLP", "naacl": "NAACL"}
STOP = set("a an the of and or in on for to with by from at as is are was were be this that these those via using use "
           "we our its it into than under over based towards toward new method methods approach learning model models "
           "data results paper study task tasks deep neural network networks not only run runs seed seeds test train "
           "training one two three each per all any can may will would should what which when where how why who also "
           "more most less same other than then there their they them here file files line lines code config repo "
           "repository folder json csv value values mean std number numbers write paragraph brief claim claims want "
           "working title idea where live avoid must cite few rough every set sets cost costs count counts make makes "
           "general simple first good better best large small high low".split())


def vdir(cfg: Config) -> Path:
    return cfg.work / "venue"


def cache_dir() -> Path:
    return Path(os.environ.get("SCRIPTORIUM_HOME") or Path.home() / ".scriptorium") / "venues"


def _get(url: str, binary: bool = False, timeout: int = 90):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "replace")


def _cached(url: str, name: str) -> str:
    p = cache_dir() / name
    if p.exists() and p.stat().st_size > 10000:
        return p.read_text(errors="replace")
    t = _get(url)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(t)
    return t


def _clean(t: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", t))).strip()


# ---------------------------------------------------------------------------------------------------------------------
# Proceedings indexes: [{title, pdf}] per venue and year

def index(venue: str, year: int) -> list[dict]:
    kind, arg = SOURCES[venue]
    if kind == "cvf":
        t = _cached(f"https://openaccess.thecvf.com/{arg}{year}?day=all", f"{venue}{year}.html")
        out = []
        for m in re.finditer(r'<a href="(/content/[^"]+?/html/[^"]+?_paper\.html)">([^<]+)</a>', t):
            out.append({"title": _clean(m.group(2)), "pdf": "https://openaccess.thecvf.com"
                        + m.group(1).replace("/html/", "/papers/").replace(".html", ".pdf")})
        return out
    if kind == "nips":
        t = _cached(f"https://papers.nips.cc/paper_files/paper/{year}", f"neurips{year}.html")
        out = []
        for m in re.finditer(r'href="(/paper_files/paper/\d+/hash/(\w+)-Abstract([-\w]*)\.html)">([^<]+)</a>', t):
            out.append({"title": _clean(m.group(4)), "pdf": f"https://papers.nips.cc/paper_files/paper/{year}/file/"
                        f"{m.group(2)}-Paper{m.group(3)}.pdf"})
        return out
    if kind == "pmlr":
        root = _cached("https://proceedings.mlr.press/", "pmlr_volumes.html")
        m = re.search(r'href="(v\d+)"><b>Volume \d+</b></a> Proceedings of ICML ' + str(year) + r"\b", root)
        if not m:
            return []
        vol = m.group(1)
        t = _cached(f"https://proceedings.mlr.press/{vol}/", f"icml{year}.html")
        out = []
        for m in re.finditer(r'<p class="title">(.*?)</p>.*?href="(https://[^"]+?\.pdf)"', t, re.S):
            out.append({"title": _clean(m.group(1)), "pdf": m.group(2)})
        return out
    if kind == "miccai":
        t = _cached(f"https://papers.miccai.org/miccai-{year}/", f"miccai{year}.html")
        out = []
        for m in re.finditer(r'&bullet;\s*<b>(.*?)</b>.*?href="(https://papers\.miccai\.org/[^"]+?_paper\.pdf)"', t,
                             re.S):
            out.append({"title": _clean(m.group(1)), "pdf": m.group(2)})
        return out
    if kind == "acl":
        t = _cached(f"https://aclanthology.org/events/{arg}-{year}/", f"{arg}{year}.html")
        out = []
        for m in re.finditer(r'<strong><a class=align-middle href=/(\d{4}\.' + arg + r'-(?:long|short|main)\.(\d+))/>'
                             r'(.*?)</a>', t):
            if m.group(2) != "0":
                out.append({"title": _clean(m.group(3)), "pdf": f"https://aclanthology.org/{m.group(1)}.pdf"})
        return out
    if kind == "iclr":
        t = _cached(f"https://iclr.cc/virtual/{year}/papers.html", f"iclr{year}.html")
        return [{"title": _clean(m.group(1)), "pdf": ""}
                for m in re.finditer(r'<a href="/virtual/\d+/poster/\d+">([^<]+)</a>', t)]
    return []


def recent_years(venue: str, n: int = 2) -> list[tuple[int, list[dict]]]:
    """The last n years whose proceedings are online (each with at least 50 papers)."""
    this = datetime.date.today().year
    out = []
    for y in range(this, this - 4, -1):
        try:
            papers = index(venue, y)
        except Exception:  # noqa: BLE001  not online yet, or the site is down
            papers = []
        if len(papers) >= 50:
            out.append((y, papers))
        if len(out) == n:
            break
    return out


# ---------------------------------------------------------------------------------------------------------------------
# Ranking: relevance of titles to the work (BM25), weighed with citations

def terms(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z][a-z0-9\-]{2,}", text.lower()) if w not in STOP]


def _section(md: str, *names: str) -> str:
    out = []
    for m in re.finditer(r"^#+\s*(.+?)\s*$(.*?)(?=^#|\Z)", md, re.M | re.S):
        if any(n in m.group(1).lower() for n in names):
            out.append(m.group(2))
    return " ".join(out)


def query_terms(cfg: Config, k: int = 20) -> list[str]:
    """What the work is about: the title (weighted most), the brief's idea and claims, the inventory's research
    question. Code words and file names are left out."""
    brief = (cfg.root / "brief.md").read_text() if (cfg.root / "brief.md").exists() else ""
    inv = (cfg.work / "inventory.md").read_text() if (cfg.work / "inventory.md").exists() else ""
    weighted = [(cfg.title + " " + _section(brief, "title"), 3), (_section(brief, "idea", "claim"), 2),
                (_section(inv, "research question", "method"), 1)]
    c = Counter()
    for text, w in weighted:
        for t in terms(re.sub(r"`[^`]*`|\S+\.(py|json|jsonl|csv|md|yaml)\b", " ", text)):
            c[t] += w
    return [w for w, _ in c.most_common(k)]


def bm25(query: list[str], docs: list[str], k1: float = 1.2, b: float = 0.75) -> list[float]:
    toks = [terms(d) for d in docs]
    n = len(toks)
    avg = sum(len(t) for t in toks) / max(n, 1)
    df = Counter(w for t in toks for w in set(t))
    out = []
    for t in toks:
        tf = Counter(t)
        s = 0.0
        for q in query:
            if q in tf:
                idf = math.log(1 + (n - df[q] + 0.5) / (df[q] + 0.5))
                s += idf * tf[q] * (k1 + 1) / (tf[q] + k1 * (1 - b + b * len(t) / max(avg, 1)))
        out.append(s)
    return out


def citations(title: str) -> tuple[int | None, str]:
    """(cited_by_count, arXiv id or '') for a title, from OpenAlex (OPENALEX_API_KEY gives it its own budget), else
    Semantic Scholar when S2_API_KEY is set. None when no source answered: selection then ranks by relevance alone."""
    import urllib.parse
    params = {"search": title, "per-page": 3, "select": "title,cited_by_count,locations,ids"}
    if os.environ.get("OPENALEX_API_KEY"):
        params["api_key"] = os.environ["OPENALEX_API_KEY"]
    try:
        d = json.loads(_get("https://api.openalex.org/works?" + urllib.parse.urlencode(params), timeout=30))
    except Exception:  # noqa: BLE001
        d = None
    if d is None:
        if not (os.environ.get("S2_API_KEY") or os.environ.get("SEMANTIC_SCHOLAR_API_KEY")):
            return None, ""
        try:
            r = json.loads(cite._get_s2("https://api.semanticscholar.org/graph/v1/paper/search/match?" +
                                        urllib.parse.urlencode({"query": title,
                                                                "fields": "title,citationCount,externalIds"})))
            w = (r.get("data") or [{}])[0]
            return int(w.get("citationCount") or 0), (w.get("externalIds") or {}).get("ArXiv", "")
        except Exception:  # noqa: BLE001
            return None, ""
    for w in d.get("results", []):
        if cite._tnorm(w.get("title") or "") == cite._tnorm(title):
            arx = ""
            for loc in w.get("locations") or []:
                u = (loc.get("landing_page_url") or "")
                m = re.search(r"arxiv\.org/abs/([\d.]+)", u)
                if m:
                    arx = m.group(1)
            return int(w.get("cited_by_count") or 0), arx
    return 0, ""


def select(cfg: Config, venue: str, n: int = 6, pool: int = 25) -> list[dict]:
    q = query_terms(cfg)
    cands = []
    for year, papers in recent_years(venue):
        scores = bm25(q, [p["title"] for p in papers])
        for p, s in zip(papers, scores):
            if s > 0 and len(set(terms(p["title"])) & set(q)) >= 2:      # at least two topic terms in the title
                cands.append({**p, "year": year, "relevance": round(s, 3)})
    cands.sort(key=lambda c: -c["relevance"])
    cands = cands[:pool]
    top = max((c["relevance"] for c in cands), default=1.0)
    for c in cands:
        c["citations"], arx = citations(c["title"])
        if not c["pdf"] and arx:
            c["pdf"] = f"https://arxiv.org/pdf/{arx}"
        c["score"] = round(c["relevance"] / top * (1 + math.log1p(c["citations"] or 0)), 3)
    cands = [c for c in cands if c["pdf"]]
    cands.sort(key=lambda c: -c["score"])
    return cands[:n]


def slug(title: str, i: int) -> str:
    return f"{i:02d}_" + re.sub(r"[^a-z0-9]+", "_", title.lower())[:50].strip("_")


def fetch(cfg: Config) -> list[dict]:
    """Choose the exemplars, download their PDFs and extract their text. Returns the exemplars."""
    venue = venue_of(cfg)
    vd = vdir(cfg)
    (vd / "papers").mkdir(parents=True, exist_ok=True)
    picked = select(cfg, venue, n=cfg.venue_exemplars)
    out = []
    for i, c in enumerate(picked, 1):
        sid = slug(c["title"], i)
        pdf = vd / "papers" / f"{sid}.pdf"
        try:
            if not pdf.exists():
                data = _get(c["pdf"], binary=True, timeout=180)
                if not data.startswith(b"%PDF") or len(data) > 40_000_000:
                    continue
                pdf.write_bytes(data)
            import pymupdf
            doc = pymupdf.open(str(pdf))
            (vd / "papers" / f"{sid}.txt").write_text("\n".join(pg.get_text() for pg in doc))
        except Exception:  # noqa: BLE001  one paper failing does not stop the study
            continue
        out.append({**c, "id": sid, "file": f".scriptorium/venue/papers/{sid}.pdf"})
    (vd / "exemplars.json").write_text(json.dumps({"venue": venue, "query": query_terms(cfg), "exemplars": out},
                                                  indent=1))
    return out


def exemplars(cfg: Config) -> list[dict]:
    return (S.read_json(vdir(cfg) / "exemplars.json") or {}).get("exemplars", [])


def studied(cfg: Config) -> bool:
    return venue_of(cfg) in SOURCES and cfg.venue_study


def venue_of(cfg: Config) -> str:
    return cfg.conference or cfg.template


# ---------------------------------------------------------------------------------------------------------------------
# Stages

class VenueRead(S.Stage):
    """Code fetches the exemplars (outside the run's lock), then one reader per paper takes notes."""
    max_fix = 2

    def prepare(self, cfg):
        if studied(cfg) and not exemplars(cfg):
            try:
                fetch(cfg)
            except Exception as e:  # noqa: BLE001
                (vdir(cfg)).mkdir(parents=True, exist_ok=True)
                (vdir(cfg) / "fetch_error.txt").write_text(str(e)[:500])

    def task_for(self, cfg, ex, extra=""):
        return Task("venue_reader", f"venue-{ex['id'][:2]}", S.context(cfg) + (
            f"Task: study how this {NAMES.get(venue_of(cfg), venue_of(cfg))} {ex['year']} paper is written: "
            f"{ex['file']} (\"{ex['title']}\"). Write .scriptorium/venue/notes/{ex['id']}.json as your instructions "
            "describe; every quote must be copied exactly from the paper." + extra))

    def tasks(self, cfg):
        (vdir(cfg) / "notes").mkdir(parents=True, exist_ok=True)
        return [self.task_for(cfg, ex) for ex in exemplars(cfg) if note_problems(cfg, ex)]

    def validate(self, cfg):
        return [e for ex in exemplars(cfg) for e in note_problems(cfg, ex)]

    def fix_tasks(self, cfg, errors):
        return [self.task_for(cfg, ex, "\n\nFix:\n- " + "\n- ".join(e for e in errors if ex["id"] in e))
                for ex in exemplars(cfg) if any(ex["id"] in e for e in errors)]

    def on_fail(self, cfg, errors):
        return "continue"          # a paper that could not be read is left out of the playbook


NOTE_KEYS = ("framing", "key_idea", "figure1", "contributions", "emphasis", "structure", "results", "tone")


def _norm(t: str) -> str:
    """Letters and digits only, after Unicode normalization and with words hyphenated across PDF lines joined, so a
    quote matches the extracted text despite ligatures (fi), line-break hyphens and spacing."""
    import unicodedata
    t = unicodedata.normalize("NFKC", t).replace("\u00ad", "")
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)
    return re.sub(r"[^a-z0-9]+", "", t.lower())


def note_problems(cfg: Config, ex: dict) -> list[str]:
    p = vdir(cfg) / "notes" / f"{ex['id']}.json"
    d = S.read_json(p)
    if d is None:
        return [f"{ex['id']}: notes are missing"]
    errs = [f"{ex['id']}: notes need `{k}`" for k in NOTE_KEYS if not d.get(k)]
    txt_p = vdir(cfg) / "papers" / f"{ex['id']}.txt"
    text = _norm(txt_p.read_text()) if txt_p.exists() else ""
    quotes = d.get("quotes") or []
    if len(quotes) < 3:
        errs.append(f"{ex['id']}: quote at least three sentences that show the patterns you describe")
    for q in quotes:
        if text and _norm(q) not in text:
            errs.append(f"{ex['id']}: the quote {q[:60]!r} is not in the paper; copy it exactly")
    return errs


PLAYBOOK_HEADINGS = ("Framing", "Figure 1", "Contributions", "Emphasis", "Structure", "Results", "Tone")


class VenueStyle(S.Stage):
    max_fix = 2

    def tasks(self, cfg):
        if not studied(cfg) or not [ex for ex in exemplars(cfg) if not note_problems(cfg, ex)]:
            return []
        return [Task("venue_analyst", "venue-style", S.context(cfg) + (
            f"Task: write .scriptorium/venue_style.md, the playbook for writing this paper for "
            f"{NAMES.get(venue_of(cfg), venue_of(cfg))}, from the readers' notes in .scriptorium/venue/notes/ (exemplars "
            "in .scriptorium/venue/exemplars.json), as your instructions describe."))]

    def validate(self, cfg):
        if not studied(cfg):
            return []
        ok = [ex["id"] for ex in exemplars(cfg) if not note_problems(cfg, ex)]
        if not ok:
            return []              # nothing could be read: the built-in style guide stands
        p = cfg.work / "venue_style.md"
        if not p.exists():
            return [".scriptorium/venue_style.md is missing"]
        t = p.read_text()
        errs = [f"venue_style.md needs a `## {h}` section" for h in PLAYBOOK_HEADINGS if f"## {h}" not in t]
        used = {i for i in ok if i in t or re.search(r"\b" + i[:2] + r"\b", t)}       # full id or its number
        if len(used) < min(3, len(ok)):
            errs.append("venue_style.md should ground its rules in the exemplars: name the exemplar ids (e.g. "
                        f"{ok[0]}) next to the patterns they show")
        return errs

    def on_fail(self, cfg, errors):
        return "continue"


# ---------------------------------------------------------------------------------------------------------------------
# Venue requirements: sections a venue makes mandatory, and the NeurIPS checklist

def required_sections(cfg: Config) -> list[dict]:
    from .venues import VENUES
    return VENUES.get(cfg.template, {}).get("requires", [])


def requirement_problems(cfg: Config) -> list[str]:
    errs = []
    body = "\n".join(p.read_text() for p in sorted(cfg.paper.glob("*.tex")) if p.name != "main.tex")
    for r in required_sections(cfg):
        if not re.search(r"\\(?:sub)?section\*?\{\s*" + re.escape(r["title"]) + r"\s*\}", body, re.I):
            errs.append(f"{cfg.template} requires a \"{r['title']}\" section ({r['why']})")
    from .venues import VENUES
    if VENUES.get(cfg.template, {}).get("checklist"):
        ck = cfg.paper / "checklist.tex"
        if not ck.exists():
            errs.append("NeurIPS requires the paper checklist (paper/checklist.tex is missing)")
        else:
            t = ck.read_text()
            todo = len(re.findall(r"\\answerTODO|\\justificationTODO", t))
            if todo:
                errs.append(f"paper/checklist.tex still has {todo} TODO answers or justifications")
    return errs


def checklist_template(official_tex: str) -> str:
    """The NeurIPS checklist from the official sample paper, with the instruction block removed as it asks."""
    a = official_tex.index("\\section*{NeurIPS Paper Checklist}")
    b = official_tex.index("\\end{document}", a)
    t = official_tex[a:b]
    t = re.sub(r"%%% BEGIN INSTRUCTIONS %%%.*?%%% END INSTRUCTIONS %%%", "", t, flags=re.S)
    return t.strip() + "\n"


class Comply(S.Stage):
    """Venue requirements: required sections exist, and the NeurIPS checklist is answered honestly."""
    max_fix = 2

    def tasks(self, cfg):
        probs = requirement_problems(cfg)
        if not probs:
            return []
        return [Task("compliance", "comply", S.context(cfg) + (
            f"Task: make the paper meet {cfg.template}'s requirements:\n- " + "\n- ".join(probs)
            + "\nAnswer the checklist (if any) honestly from what the paper and .scriptorium/ledger.md show, as your "
            "instructions describe. Then run `scriptorium build`."))]

    def validate(self, cfg):
        return requirement_problems(cfg) + [e for e in S.checks(cfg) if e.startswith("self-citation")]
