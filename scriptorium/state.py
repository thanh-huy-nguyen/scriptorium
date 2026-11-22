"""Run state in .scriptorium/state.json, and snapshots of paper/ for revisions that may be rolled back."""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

from .config import Config


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
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(s, indent=1))
    tmp.replace(p)


def stage(s: dict, name: str) -> dict:
    return s["stages"].setdefault(name, {"status": "pending", "fixes": 0})


def mark(cfg: Config, name: str, status: str, **extra) -> None:
    s = load(cfg)
    st = stage(s, name)
    st["status"] = status
    st[status + "_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    st.update(extra)
    save(cfg, s)


def add_usage(cfg: Config, name: str, recs: list[dict]) -> None:
    s = load(cfg)
    u = s["usage"].setdefault(name, {"sessions": 0, "turns": 0, "input_tokens": 0, "output_tokens": 0,
                                     "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0})
    for r in recs:
        u["sessions"] += 1
        u["turns"] += r.get("turns") or 0
        for k, v in (r.get("tokens") or {}).items():
            u[k] = u.get(k, 0) + (v or 0)
    save(cfg, s)


def snapshot(cfg: Config, name: str) -> Path:
    dst = cfg.work / "snapshots" / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(cfg.paper, dst, ignore=shutil.ignore_patterns("*.pdf", "*.log", "*.aux", "__pycache__"))
    for pdf in (cfg.paper / "figures").glob("*.pdf") if (cfg.paper / "figures").exists() else []:
        (dst / "figures").mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf, dst / "figures" / pdf.name)
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
