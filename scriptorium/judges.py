"""Pairwise judges: panels of personas that compare two candidates in both orders, the keep rule and tournaments.

Panels (plan 3.3):
- working:     the reviewer agents (plugin/agents/reviewer.md); their reviews drive revisions. Not in this module.
- selection:   tournaments and keep-or-rollback during a run. Fable by default.
- development: milestone tests and stage ablations during development. Opus and Fable mixed.
- final:       benchmark only; its prompts are written after the system is frozen and live outside the package.

A candidate is either text (a section, an abstract, a pitch) or a set of files the judge reads (a compiled PDF,
figure images). Judges never see which candidate is the incumbent, and each persona judges both orders.
"""
from __future__ import annotations

import json
import math
import random
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from .config import Config
from .runner import run_judge
from .sealing import PROMPTS

SCHEMA = {"type": "object", "properties": {
    "preferred": {"type": "string", "enum": ["first", "second", "tie"]},
    "confidence": {"type": "integer", "enum": [1, 2, 3]},
    "reason": {"type": "string"}}, "required": ["preferred", "confidence", "reason"]}

# Models covered by a Claude subscription. Fable needs paid usage credits, which Scriptorium never uses, so panels
# run on Opus and Sonnet; a different model for a persona can be set with [models] judge_opus / judge_sonnet.
PANELS = {
    "selection": [("sel_area_chair", "opus"), ("sel_skeptic", "opus"), ("sel_reader", "opus")],
    "development": [("dev_chair", "opus"), ("dev_methods", "sonnet"), ("dev_editor", "opus")],
}
FALLBACK = {"fable": "opus", "opus": "sonnet"}


@dataclass
class Candidate:
    name: str
    text: str = ""                                          # inline content
    files: dict[str, Path] = field(default_factory=dict)    # name in the judge's folder -> local file


@dataclass
class Vote:
    persona: str
    model: str
    order: str          # "AB" or "BA": which candidate was shown first
    sample: int
    winner: str         # candidate name, or "tie", or "error"
    confidence: int = 0
    reason: str = ""
    tokens: dict = field(default_factory=dict)


def persona_text(name: str) -> str:
    t = (PROMPTS / f"{name}.md").read_text()
    return re.sub(r"^---.*?---\s*", "", t, flags=re.S).strip()


# Text that tries to steer a judge. Removed before judging and flagged by the lint.
INJECTION_RE = re.compile(
    r"(ignore (all |any )?(previous|prior|above) (instructions|prompts)|(as an?|to( the)?|dear|for) (ai|llm|language "
    r"models?|reviewers?|judges?|assistants?)\b[^.\n]{0,120}(rate|score|accept|prefer)[^.\n]*|give (this|the) "
    r"(paper|submission) (a )?(high|positive|strong)[^.\n]*|rate this (paper|submission) (highly|positively)"
    r"|you must (accept|prefer)[^.\n]*)", re.I)
HIDDEN_TEX_RE = re.compile(r"\\(textcolor|color)\{white\}|\\fontsize\{0|\\resizebox\{0|\\scalebox\{0(\.0+)?\}", re.I)


def strip_injections(text: str) -> tuple[str, int]:
    n = len(INJECTION_RE.findall(text)) + len(HIDDEN_TEX_RE.findall(text))
    text = INJECTION_RE.sub("[removed]", text)
    text = HIDDEN_TEX_RE.sub("", text)
    return text, n


def _prompt(persona: str, task: str, first: Candidate, second: Candidate, canary: str) -> str:
    parts = [persona_text(persona), "", "Task: " + task, ""]
    if first.files or second.files:
        parts.append("The two candidates are files in your working folder. Read every page of both before deciding.")
        parts.append("First candidate: " + ", ".join(sorted(first.files)))
        parts.append("Second candidate: " + ", ".join(sorted(second.files)))
    if first.text or second.text:
        parts += ["", "<first_candidate>", strip_injections(first.text)[0], "</first_candidate>", "",
                  "<second_candidate>", strip_injections(second.text)[0], "</second_candidate>"]
    parts += ["", f"(session {canary})"]
    return "\n".join(parts)


def _relabel(c: Candidate, slot: str) -> Candidate:
    """Copy a candidate under neutral file names (first_*, second_*) so names never reveal which is which."""
    files = {f"{slot}_{i + 1}{Path(k).suffix}": v for i, (k, v) in enumerate(sorted(c.files.items()))}
    return Candidate(c.name, c.text, files)


def pdf_text(path: Path) -> str:
    """The text of a compiled paper, page by page. Judges read text; figures are judged by the figure critic."""
    import pymupdf
    doc = pymupdf.open(str(path))
    return "\n".join(f"[page {i + 1}]\n{p.get_text()}" for i, p in enumerate(doc))


def compare(cfg: Config, panel: str, task: str, a: Candidate, b: Candidate, samples: int = 1, canary: str = "",
            personas: list[tuple[str, str]] | None = None, echo=print, parallel: int | None = None,
            one_order: int | None = None) -> list[Vote]:
    """Every persona of the panel judges (a, b) and (b, a), `samples` times each. With `one_order` set, each persona
    judges a single order instead, alternating across personas starting from that offset (half the calls; position
    bias then averages out across personas and pairs rather than within each)."""
    jobs = []
    for k, (persona, model) in enumerate(personas or PANELS[panel]):
        orders = ("AB", "BA") if one_order is None else (("AB", "BA")[(k + one_order) % 2],)
        for order in orders:
            for s in range(samples):
                jobs.append((persona, cfg.models.get(f"judge_{model}", model), order, s))

    def one(job) -> Vote:
        persona, model, order, s = job
        first, second = (a, b) if order == "AB" else (b, a)
        f1, f2 = _relabel(first, "first"), _relabel(second, "second")
        files = {**f1.files, **f2.files}
        prompt = _prompt(persona, task, f1, f2, canary)
        r = run_judge(cfg, model, prompt, files=files or None, echo=echo, json_schema=SCHEMA)
        if not r["ok"] and model in FALLBACK and (r.get("unavailable") or "model" in (r.get("error") or "").lower()):
            model = FALLBACK[model]
            r = run_judge(cfg, model, prompt, files=files or None, echo=echo, json_schema=SCHEMA)
        try:
            d = json.loads(r["text"])
            pick = d.get("preferred")
            winner = first.name if pick == "first" else second.name if pick == "second" else "tie"
            return Vote(persona, model, order, s, winner, int(d.get("confidence") or 0), str(d.get("reason", ""))[:600],
                        r["tokens"])
        except (json.JSONDecodeError, TypeError):
            return Vote(persona, model, order, s, "error", 0, (r.get("error") or r.get("text") or "")[:300], r["tokens"])

    with ThreadPoolExecutor(max_workers=max(1, parallel or cfg.judge_parallel)) as ex:
        return list(ex.map(one, jobs))


def tally(votes: list[Vote], name: str) -> tuple[int, int]:
    """(votes for `name`, total votes). Ties and errors count as votes not for `name`."""
    return sum(v.winner == name for v in votes), len(votes)


def keep(votes: list[Vote], candidate: str, need: float = 1.0) -> bool:
    """The keep rule: the candidate needs at least `need` of all votes (all 6 of 6 by default: 3 personas, both
    orders); ties and errors count against it. The gate measures how often this keeps a revision that changed
    nothing."""
    k, n = tally(votes, candidate)
    return n > 0 and k >= math.ceil(need * n - 1e-9)


def bradley_terry(names: list[str], votes: list[Vote], iters: int = 200) -> dict[str, float]:
    """Bradley-Terry strengths from pairwise votes (a tie gives half a win to each side). Each vote must carry the
    pair in `reason`-independent form, so callers pass votes from compare() of every pair."""
    wins = {(i, j): 0.0 for i in names for j in names if i != j}
    for v in votes:
        pair = getattr(v, "pair", None)
        if not pair:
            continue
        x, y = pair
        if v.winner == x:
            wins[(x, y)] += 1
        elif v.winner == y:
            wins[(y, x)] += 1
        elif v.winner == "tie":
            wins[(x, y)] += 0.5
            wins[(y, x)] += 0.5
    p = {n: 1.0 for n in names}
    for _ in range(iters):
        new = {}
        for i in names:
            w = sum(wins[(i, j)] for j in names if j != i) + 0.1
            d = sum((wins[(i, j)] + wins[(j, i)] + 0.2) / (p[i] + p[j]) for j in names if j != i)
            new[i] = w / d if d else p[i]
        s = sum(new.values())
        p = {k: v * len(names) / s for k, v in new.items()}
    return p


def tournament(cfg: Config, panel: str, task: str, cands: list[Candidate], incumbent: str | None = None,
               samples: int = 1, canary: str = "", echo=print) -> tuple[str, dict[str, float], list[Vote]]:
    """Round-robin over the candidates; returns (winner, strengths, votes). The incumbent (or the first candidate)
    wins ties in strength."""
    names = [c.name for c in cands]
    if len(cands) == 1:
        return names[0], {names[0]: 1.0}, []
    allv: list[Vote] = []
    for i in range(len(cands)):
        for j in range(i + 1, len(cands)):
            vs = compare(cfg, panel, task, cands[i], cands[j], samples=samples, canary=canary, echo=echo)
            for v in vs:
                v.pair = (cands[i].name, cands[j].name)  # type: ignore[attr-defined]
            allv += vs
    st = bradley_terry(names, allv)
    first = incumbent or names[0]
    best = max(names, key=lambda n: (round(st[n], 6), n == first))
    return best, st, allv


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 1.0
    ph = k / n
    d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def shuffle_seed(seed: int) -> random.Random:
    return random.Random(seed)
