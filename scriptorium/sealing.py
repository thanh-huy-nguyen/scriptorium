"""What keeps the judges' material away from the agents they judge.

Layers, from strongest to weakest on this kind of machine (no root, no user namespaces, so no OS sandbox):

1. Judges leave nothing on disk. They run with no tools (or Read, confined to a temporary folder that is deleted), no
   plugin, no settings and no saved transcript (runner.run_judge). Their verdicts and reasons are kept in
   ~/.scriptorium/sealed/<run>/ until the run ends, and agents only learn "kept" or "rolled back".
2. Agents cannot reach sealed places. File tools may not read outside the repository (inline settings plus the guard
   hook); shell commands come from a short read-only list with every path checked; Python runs only through
   `scriptorium` commands and inside the jail (jail/sitecustomize.py), which refuses the sealed folders.
3. Canaries. Every judge prompt carries canary strings. After each stage the orchestrator scans the agents'
   transcripts and the paper for them; a hit fails the run.
"""
from __future__ import annotations

import json
import os
import secrets
import time
from pathlib import Path

from .config import PKG, Config
from .runner import JAIL_DIR, sealed_home

PROMPTS = PKG / "judging"
STATIC_CANARY_RE = "SCR-CANARY-"


def jail_env(cfg: Config, base: dict | None = None) -> dict[str, str]:
    """Environment for running agent-written code (recipes, figure scripts) from the orchestrator."""
    env = dict(base if base is not None else os.environ)
    env["SCRIPTORIUM_JAIL_ROOT"] = str(cfg.root)
    env["PYTHONPATH"] = os.pathsep.join(p for p in [str(JAIL_DIR), env.get("PYTHONPATH", "")] if p)
    return env


def run_dir(cfg: Config) -> Path:
    """The sealed folder for this repository's run (outside the repository)."""
    import hashlib
    h = hashlib.sha1(str(cfg.root).encode()).hexdigest()[:12]
    d = sealed_home() / h
    d.mkdir(parents=True, exist_ok=True)
    os.chmod(sealed_home(), 0o700)
    return d


def run_canary(cfg: Config) -> str:
    p = run_dir(cfg) / "canary.txt"
    if not p.exists():
        p.write_text("SCR-RUN-" + secrets.token_hex(8))
    return p.read_text().strip()


def static_canaries() -> list[str]:
    out = []
    for f in sorted(PROMPTS.glob("*.md")) if PROMPTS.exists() else []:
        for line in f.read_text().splitlines():
            if STATIC_CANARY_RE in line:
                out.append(line[line.index(STATIC_CANARY_RE):].split()[0].strip("`.,;:)"))
    return out


def canaries(cfg: Config) -> list[str]:
    return [*static_canaries(), run_canary(cfg)]


def transcript_path(cfg: Config, session_id: str) -> Path | None:
    """Claude Code keeps a session's transcript in ~/.claude/projects/<cwd with / replaced by ->/<id>.jsonl."""
    base = Path.home() / ".claude" / "projects"
    enc = str(cfg.root).replace("/", "-").replace(".", "-").replace("_", "-")
    for cand in (base / enc / f"{session_id}.jsonl", *base.glob(f"*/{session_id}.jsonl")):
        if cand.exists():
            return cand
    return None


def scan(cfg: Config, recs: list[dict]) -> list[str]:
    """Canary hits in the given agent sessions' transcripts and results, and in paper/ and .scriptorium/."""
    cs = [c for c in canaries(cfg) if c]
    hits = []
    for r in recs:
        texts = [r.get("result") or ""]
        sid = r.get("session_id")
        tp = transcript_path(cfg, sid) if sid else None
        if tp:
            texts.append(tp.read_text(errors="ignore"))
        for c in cs:
            if any(c in t for t in texts):
                hits.append(f"session {r.get('label')} ({sid}) contains canary {c[:14]}...")
    for d in (cfg.paper, cfg.work):
        if not d.exists():
            continue
        for f in d.rglob("*"):
            if f.is_file() and f.suffix in {".tex", ".md", ".json", ".py", ".bib", ".txt", ".jsonl"}:
                t = f.read_text(errors="ignore")
                for c in cs:
                    if c in t:
                        hits.append(f"{f.relative_to(cfg.root)} contains canary {c[:14]}...")
    return hits


def store(cfg: Config, kind: str, record: dict) -> Path:
    """Keep a judge record sealed until the run ends."""
    d = run_dir(cfg) / kind
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{time.strftime('%Y%m%d-%H%M%S')}-{secrets.token_hex(3)}.json"
    p.write_text(json.dumps(record, indent=1))
    return p


def release(cfg: Config) -> Path:
    """At the end of a run, copy the sealed records into .scriptorium/atlas/judges/ for the human reader."""
    import shutil
    src, dst = run_dir(cfg), cfg.work / "atlas" / "judges"
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.rglob("*.json"):
        rel = f.relative_to(src)
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dst / rel)
    return dst
