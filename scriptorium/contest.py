"""Search within a stage: candidates compete, deterministic validators filter, the selection panel decides.

Used for the storyline (pitches), the abstract, the introduction and the Figure 1 caption. The votes and the
judges' reasons are sealed until the run ends; agents only see which candidate won (decisions.jsonl).
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from . import judges as J
from . import ledger, sealing
from .config import Config
from .runner import run_judge


def decide(cfg: Config, stage: str, what: str, **info) -> None:
    rec = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "stage": stage, "decision": what, **info}
    with (cfg.work / "decisions.jsonl").open("a") as f:
        f.write(json.dumps(rec) + "\n")


def tournament(cfg: Config, stage: str, task: str, cands: dict[str, str], incumbent: str | None = None,
               echo=print) -> tuple[str, dict[str, float]]:
    """Run the selection panel over text candidates; returns (winner, strengths) and records the decision."""
    names = list(cands)
    if len(names) == 1:
        decide(cfg, stage, f"only candidate {names[0]}", winner=names[0])
        return names[0], {names[0]: 1.0}
    cs = [J.Candidate(n, cands[n]) for n in names]
    echo(f"    tournament: {len(cs)} candidates, {len(cs) * (len(cs) - 1) // 2} pairs, selection panel")
    win, st, votes = J.tournament(cfg, "selection", task, cs, incumbent=incumbent,
                                  canary=sealing.run_canary(cfg), echo=echo)
    sealing.store(cfg, f"tournament_{stage}", {"task": task, "candidates": names, "strengths": st,
                                                "votes": [v.__dict__ | {"pair": getattr(v, "pair", None)}
                                                          for v in votes]})
    toks = {k: sum((v.tokens or {}).get(k, 0) for v in votes) for k in ("input_tokens", "output_tokens",
                                                                         "cache_read_input_tokens",
                                                                         "cache_creation_input_tokens")}
    from . import state
    state.add_usage(cfg, f"{stage}:judges", [{"turns": len(votes), "tokens": toks}])
    if votes and all(v.winner == "error" for v in votes):
        echo("    WARNING: every judge call failed; keeping the first candidate (see the sealed records after the run)")
        decide(cfg, stage, "judges failed; kept the first candidate", winner=win)
        return win, st
    decide(cfg, stage, f"tournament winner {win}", winner=win,
           strengths={k: round(v, 3) for k, v in sorted(st.items(), key=lambda x: -x[1])})
    echo(f"    tournament winner: {win} (" + ", ".join(f"{k} {v:.2f}" for k, v in
                                                 sorted(st.items(), key=lambda x: -x[1])) + ")")
    return win, st


# ---------------------------------------------------------------------------------------------------------------------
# Skim test: can a reader recover the intended claim from the front matter alone?

SKIM_READ = ("Here is the front matter of a research paper: its title, a short abstract, and a description of its "
             "Figure 1. In one sentence, state the paper's main claim. Answer with the sentence only.\n\n{front}")
SKIM_MATCH = ("Intended main claim of a paper: \"{intended}\"\nA reader's one-sentence summary after skimming: "
              "\"{read}\"\nDoes the reader's summary state the same main claim (same finding, same scope)? Answer "
              "with JSON only: {{\"match\": \"yes\" | \"partly\" | \"no\", \"why\": \"<20 words>\"}}")
MATCH_SCHEMA = {"type": "object", "properties": {"match": {"type": "string", "enum": ["yes", "partly", "no"]},
                                                 "why": {"type": "string"}}, "required": ["match", "why"]}


def skim(cfg: Config, front: str, intended: str, model: str = "sonnet") -> dict:
    r1 = run_judge(cfg, model, SKIM_READ.format(front=front))
    read = (r1.get("text") or "").strip()
    r2 = run_judge(cfg, model, SKIM_MATCH.format(intended=intended, read=read), json_schema=MATCH_SCHEMA)
    try:
        d = json.loads(r2["text"])
    except (json.JSONDecodeError, TypeError):
        d = {"match": "error", "why": (r2.get("error") or "")[:100]}
    return {"read": read, **d}


# ---------------------------------------------------------------------------------------------------------------------
# Pitches

FRAMINGS = ("problem-first", "insight-first", "capability-first", "evidence-first")
PITCH_KEYS = ("title", "insight", "abstract_sketch", "figure1", "contributions", "storyline", "sections", "claims")


def pitch_path(cfg: Config, framing: str) -> Path:
    return cfg.work / "pitches" / f"{framing}.json"


def load_pitch(cfg: Config, framing: str) -> dict | None:
    try:
        return json.loads(pitch_path(cfg, framing).read_text())
    except (OSError, json.JSONDecodeError):
        return None


def pitch_problems(cfg: Config, framing: str) -> list[str]:
    p = load_pitch(cfg, framing)
    if p is None:
        return [f".scriptorium/pitches/{framing}.json is missing or is not valid JSON"]
    errs = [f"pitch {framing}: missing `{k}`" for k in PITCH_KEYS if not p.get(k)]
    usable = set(ledger.claim_ids(cfg))
    for c in p.get("claims") or []:
        if c not in usable:
            errs.append(f"pitch {framing}: claim {c!r} is not a usable ledger claim")
    for s in p.get("sections") or []:
        for c in s.get("claims") or []:
            if c not in usable:
                errs.append(f"pitch {framing}: section {s.get('title')!r} uses claim {c!r}, not a usable ledger claim")
    if len(p.get("contributions") or []) not in (2, 3, 4):
        errs.append(f"pitch {framing}: give two to four contributions")
    return errs


def pitch_text(p: dict) -> str:
    secs = "\n".join(f"  {i + 1}. {s.get('title')}" for i, s in enumerate(p.get("sections") or []))
    contrib = "\n".join(f"  - {c}" for c in p.get("contributions") or [])
    return (f"Title: {p.get('title')}\n\nMain insight: {p.get('insight')}\n\nAbstract sketch: {p.get('abstract_sketch')}"
            f"\n\nFigure 1: {p.get('figure1')}\n\nContributions:\n{contrib}\n\nStoryline: {p.get('storyline')}\n\n"
            f"Sections:\n{secs}\n\nAnticipated objection and answer: {p.get('risks', '')}")


def front_text(p: dict) -> str:
    return f"Title: {p.get('title')}\n\nAbstract: {p.get('abstract_sketch')}\n\nFigure 1: {p.get('figure1')}"


PITCH_TASK = ("Both candidates are pitches for the same paper, built from the same evidence and the same allowed "
              "claims. Decide which pitch would make the stronger paper: a question that matters, one clear insight a "
              "reader will remember, a Figure 1 that shows it, and claims framed as broadly as the evidence allows "
              "but no broader.")


def select_story(cfg: Config, echo=print) -> dict:
    pitches = {f: load_pitch(cfg, f) for f in FRAMINGS}
    pitches = {f: p for f, p in pitches.items() if p and not pitch_problems(cfg, f)}
    if not pitches:
        raise RuntimeError("no valid pitch")
    skims = {}
    for f, p in pitches.items():
        skims[f] = skim(cfg, front_text(p), p.get("insight", ""))
        echo(f"    skim test {f}: {skims[f].get('match')}")
    passing = {f: p for f, p in pitches.items() if skims[f].get("match") in ("yes", "partly")} or pitches
    decide(cfg, "story", "skim test", results={f: s.get("match") for f, s in skims.items()})
    win, st = tournament(cfg, "story", PITCH_TASK, {f: pitch_text(p) for f, p in passing.items()}, echo=echo)
    story = dict(pitches[win])
    story["selected"] = {"framing": win, "strengths": st, "skim": skims[win]}
    (cfg.work / "story.json").write_text(json.dumps(story, indent=1))
    return story


def strip_tex(t: str) -> str:
    """LaTeX source to plain text for judging: drop comments, \\src tags, labels, and common commands."""
    t = re.sub(r"(?<!\\)%.*", "", t)
    t = re.sub(r"\\src\{[^}]*\}", "", t)
    t = re.sub(r"\\(label|input|includegraphics)(\[[^\]]*\])?\{[^}]*\}", "", t)
    t = re.sub(r"\\(cite[pt]?|ref|cref|autoref)\{([^}]*)\}", r"[\2]", t)
    t = re.sub(r"\\(section|subsection|paragraph)\*?\{([^}]*)\}", r"\n\2\n", t)
    t = re.sub(r"\\(textbf|emph|textit)\{([^}]*)\}", r"\2", t)
    t = t.replace("\\%", "%").replace("~", " ")
    return re.sub(r"\n{3,}", "\n\n", t).strip()
