"""The run's event log, .scriptorium/events.jsonl: one JSON object per line, appended by the engine and the runner.

`scriptorium watch` and the HTML report read it. Events:

    run_start, run_end(status)
    stage_start(stage), stage_check(stage, status, errors), stage_done(stage), stage_failed(stage)
    task_start(stage, label, agent, model), task_end(stage, label, agent, ok, turns, seconds, output_tokens)
    limit_wait(minutes)
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path

from .config import Config

_lock = threading.Lock()


def path(cfg: Config) -> Path:
    return cfg.work / "events.jsonl"


def emit(cfg: Config, ev: str, **data) -> None:
    rec = {"t": round(time.time(), 2), "ev": ev, **data}
    with _lock:
        cfg.work.mkdir(parents=True, exist_ok=True)
        with path(cfg).open("a") as f:
            f.write(json.dumps(rec) + "\n")


def read(cfg: Config, last_run: bool = True) -> list[dict]:
    p = path(cfg)
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if last_run:
        starts = [i for i, e in enumerate(out) if e.get("ev") == "run_start"]
        if starts:
            out = out[starts[-1]:]
    return out


def running_tasks(evs: list[dict]) -> list[dict]:
    """task_start events with no matching task_end, oldest first."""
    open_: dict[tuple, dict] = {}
    for e in evs:
        key = (e.get("stage"), e.get("label"))
        if e["ev"] == "task_start":
            open_[key] = e
        elif e["ev"] == "task_end":
            open_.pop(key, None)
        elif e["ev"] in ("run_end", "run_start"):
            open_.clear()
    return sorted(open_.values(), key=lambda e: e["t"])
