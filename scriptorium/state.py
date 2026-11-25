"""Run state in .scriptorium/state.json, and snapshots of paper/ for revisions that may be rolled back."""
from __future__ import annotations

import json
import shutil
import threading
import time
from pathlib import Path

from .config import Config

# Stages run in parallel threads; every read-modify-write of state.json holds this lock (it is reentrant).
LOCK = threading.RLock()


def path(cfg: Config) -> Path:
    return cfg.work / "state.json"


def load(cfg: Config) -> dict:
    p = path(cfg)
    s = json.loads(p.read_text()) if p.exists() else {}
    s.setdefault("stages", {})
    s.setdefault("scores", {})
    s.setdefault("usage", {})
    return s


def save(cfg: Config, s: dict) -> None:
    p = path(cfg)
    p.parent.mkdir(parents=True, exist_ok=True)
    with LOCK:
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(s, indent=1))
        tmp.replace(p)


def stage(s: dict, name: str) -> dict:
    return s["stages"].setdefault(name, {"status": "pending", "fixes": 0})


def mark(cfg: Config, name: str, status: str, **extra) -> None:
    with LOCK:
        s = load(cfg)
        st = stage(s, name)
        st["status"] = status
        st[status + "_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        st.update(extra)
        save(cfg, s)


def add_usage(cfg: Config, name: str, recs: list[dict]) -> None:
    with LOCK:
        _add_usage(cfg, name, recs)


def _add_usage(cfg: Config, name: str, recs: list[dict]) -> None:
    s = load(cfg)
    u = s["usage"].setdefault(name, {"sessions": 0, "turns": 0, "input_tokens": 0, "output_tokens": 0,
                                     "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0})
    for r in recs:
        u["sessions"] += 1
        u["turns"] += r.get("turns") or 0
        for k, v in (r.get("tokens") or {}).items():
            u[k] = u.get(k, 0) + (v or 0)
    save(cfg, s)


# notes in .scriptorium that paper files are regenerated from; a rollback restores them with paper/, or a later
# stage rebuilds a rolled-back table from its spec and prints numbers whose recipes were rolled back
NOTES_BUILT_FROM = ("tables", "numbers.json", "numbers.md")


def snapshot(cfg: Config, name: str) -> Path:
    dst = cfg.work / "snapshots" / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(cfg.paper, dst, ignore=shutil.ignore_patterns("*.pdf", "*.log", "*.aux", "__pycache__"))
    for pdf in (cfg.paper / "figures").glob("*.pdf") if (cfg.paper / "figures").exists() else []:
        (dst / "figures").mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf, dst / "figures" / pdf.name)
    notes = cfg.work / "snapshots" / f"{name}.notes"     # the notes paper files are built from (table specs)
    if notes.exists():
        shutil.rmtree(notes)
    notes.mkdir(parents=True)
    for rel in NOTES_BUILT_FROM:
        src = cfg.work / rel
        if src.is_dir():
            shutil.copytree(src, notes / rel)
        elif src.is_file():
            shutil.copy2(src, notes / rel)
    return dst


def restore(cfg: Config, name: str) -> None:
    src = cfg.work / "snapshots" / name
    if not src.exists():
        raise FileNotFoundError(f"no snapshot {name}")
    keep = cfg.work / "snapshots" / f"{name}.rejected"
    if keep.exists():
        shutil.rmtree(keep)
    shutil.copytree(cfg.paper, keep, ignore=shutil.ignore_patterns("*.log", "*.aux", "__pycache__"))
    shutil.rmtree(cfg.paper)
    shutil.copytree(src, cfg.paper)
    notes = cfg.work / "snapshots" / f"{name}.notes"
    if notes.exists():                   # snapshots from before this was kept have no notes; leave those as they are
        for rel in NOTES_BUILT_FROM:
            cur, old = cfg.work / rel, notes / rel
            if cur.is_dir():
                shutil.rmtree(cur)
            elif cur.is_file():
                cur.unlink()
            if old.is_dir():
                shutil.copytree(old, cur)
            elif old.is_file():
                shutil.copy2(old, cur)
