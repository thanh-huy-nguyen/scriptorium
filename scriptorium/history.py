"""Stage history: a private git repository, .scriptorium/history.git, holding one commit per finished stage.

Each commit records paper/ and the run's notes (outline, ledger, story, reviews, state) as they stood when the stage
was accepted. `scriptorium history` lists the commits; `scriptorium rollback STAGE` puts paper/ and the notes back to
that point and marks every stage that had not finished then as pending, so `scriptorium run` continues from there.

The repository is separate from any git repository the research project has: it uses its own git directory with the
project root as work tree, adds only the paths below, and never reads the project's ignore files.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from . import state
from .config import WORK, Config

NOTES = ["inventory.md", "evidence_notes.md", "numbers.json", "numbers.md", "ledger.json", "ledger.md", "story.json",
         "outline.json", "related.md", "citations.json", "style.md", "state.json", "pitches", "tables", "figures",
         "reviews", "candidates", "decisions.json"]
EXCLUDE = ["*.aux", "*.log", "*.out", "*.bbl", "*.blg", "*.fls", "*.fdb_latexmk", "*.synctex.gz", "__pycache__",
           "*.pyc"]


def gitdir(cfg: Config) -> Path:
    return cfg.work / "history.git"


def available() -> bool:
    return shutil.which("git") is not None


def _git(cfg: Config, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    env = {**os.environ, "GIT_DIR": str(gitdir(cfg)), "GIT_WORK_TREE": str(cfg.root),
           "GIT_AUTHOR_NAME": "scriptorium", "GIT_AUTHOR_EMAIL": "scriptorium@localhost",
           "GIT_COMMITTER_NAME": "scriptorium", "GIT_COMMITTER_EMAIL": "scriptorium@localhost"}
    for k in ("GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY"):
        env.pop(k, None)
    return subprocess.run(["git", "-c", "core.excludesFile=/dev/null", "-c", "commit.gpgSign=false",
                           "-c", "core.autocrlf=false", *args], cwd=cfg.root, env=env, text=True,
                          capture_output=True, check=check)


def _paths(cfg: Config) -> list[str]:
    out = []
    if cfg.paper.exists():
        out.append("paper")
    out += [f"{WORK}/{n}" for n in NOTES if (cfg.work / n).exists()]
    return out


def init(cfg: Config) -> bool:
    if not available():
        return False
    if not (gitdir(cfg) / "HEAD").exists():
        gitdir(cfg).mkdir(parents=True, exist_ok=True)
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        subprocess.run(["git", "init", "-q", "--bare", str(gitdir(cfg))], env=env, capture_output=True, check=True)
        _git(cfg, "config", "core.bare", "false")
        (gitdir(cfg) / "info").mkdir(exist_ok=True)
        (gitdir(cfg) / "info" / "exclude").write_text("\n".join(EXCLUDE) + "\n")
    return True


def commit(cfg: Config, stage: str, message: str = "") -> str | None:
    """Record paper/ and the notes after `stage`. Returns the commit id, or None when git is missing."""
    if not init(cfg):
        return None
    with state.LOCK:
        _git(cfg, "add", "-A", "-f", "--", *_paths(cfg), *[f":(exclude,glob)**/{e}" for e in EXCLUDE], check=False)
        r = _git(cfg, "commit", "-q", "--allow-empty", "-m", f"{stage}: {message or 'done'}", "-m",
                 f"Scriptorium-Stage: {stage}", check=False)
        if r.returncode != 0:
            return None
        return _git(cfg, "rev-parse", "--short", "HEAD").stdout.strip()


def log(cfg: Config) -> list[dict]:
    """Commits, oldest first: {id, stage, subject, time}."""
    if not (gitdir(cfg) / "HEAD").exists():
        return []
    r = _git(cfg, "log", "--reverse", "--format=%h%x1f%s%x1f%ci%x1f%(trailers:key=Scriptorium-Stage,valueonly)%x1e",
             check=False)
    out = []
    for rec in r.stdout.split("\x1e"):
        parts = rec.strip().split("\x1f")
        if len(parts) >= 4:
            out.append({"id": parts[0], "subject": parts[1], "time": parts[2][:19], "stage": parts[3].strip()})
    return out


def find(cfg: Config, stage_or_id: str) -> dict | None:
    """The latest commit for a stage name, or the commit with that id."""
    hits = [c for c in log(cfg) if c["stage"] == stage_or_id or c["id"].startswith(stage_or_id)]
    return hits[-1] if hits else None


def rollback(cfg: Config, stage_or_id: str) -> dict:
    """Restore paper/ and the notes to a commit; stages unfinished at that commit become pending. Returns the commit."""
    c = find(cfg, stage_or_id)
    if not c:
        raise SystemExit(f"no history entry for {stage_or_id!r}; see `scriptorium history`")
    with state.LOCK:
        now = state.load(cfg)
        commit(cfg, "pre-rollback", f"before rolling back to {c['stage']} ({c['id']})")
        then_raw = _git(cfg, "show", f"{c['id']}:{WORK}/state.json", check=False)
        then = json.loads(then_raw.stdout) if then_raw.returncode == 0 else {"stages": {}}
        added = _git(cfg, "diff", "--name-only", "--diff-filter=A", c["id"], "HEAD").stdout.split()
        for rel in added:
            p = cfg.root / rel
            if p.is_file():
                p.unlink()
        tracked = _git(cfg, "ls-tree", "-r", "--name-only", c["id"]).stdout.split()
        if tracked:
            _git(cfg, "checkout", c["id"], "--", *tracked)
        # The stages finished at that commit stay done; everything else starts over. Token use is kept.
        new = dict(then)
        new.setdefault("stages", {})
        for name, rec in now.get("stages", {}).items():
            if name not in new["stages"] or new["stages"][name].get("status") not in ("done", "skipped"):
                new["stages"][name] = {"status": "pending", "fixes": 0}
        new["usage"] = now.get("usage", {})
        new["usage_earlier"] = now.get("usage_earlier", {})
        state.save(cfg, new)
        commit(cfg, "rollback", f"rolled back to {c['stage']} ({c['id']})")
    return c
