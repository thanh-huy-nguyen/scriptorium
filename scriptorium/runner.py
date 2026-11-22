"""Run one agent session headless with `claude -p`, inside the research repository, with the Scriptorium plugin loaded.

The plugin supplies the agents (agents/*.md) and the hooks: PaperAnchor's number check on every edit to paper/*.tex,
and a guard that keeps file edits inside paper/ and .scriptorium/.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from . import anchor
from .config import PLUGIN_DIR, Config

ALLOWED = ["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "TodoWrite",
           "Bash(scriptorium *)", "Bash(ls *)", "Bash(wc *)", "Bash(head *)", "Bash(tail *)", "Bash(cat *)",
           "Bash(grep *)", "Bash(find *)", "Bash(diff *)", "Bash(python *)", "Bash(python3 *)"]


@dataclass
class Task:
    agent: str           # one of config.ROLES
    label: str           # unique within its stage, used for the log file
    prompt: str
    role: str = ""       # model role; defaults to the agent name


def session_env(cfg: Config, stage: str) -> dict[str, str]:
    env = os.environ.copy()
    env.update({
        "SCRIPTORIUM_STAGE": stage,
        "SCRIPTORIUM_ROOT": str(cfg.root),
        "SCRIPTORIUM_PYTHON": cfg.py(),
        "SCRIPTORIUM_PAPERANCHOR": anchor.package_path(),
        "PAPERANCHOR_MODE": cfg.check_mode,
    })
    env["PATH"] = os.pathsep.join([str(Path(sys.executable).parent), env.get("PATH", "")])
    if cfg.unset_api_key:
        env.pop("ANTHROPIC_API_KEY", None)
    return env


def run_task(cfg: Config, stage: str, task: Task) -> dict:
    cmd = [cfg.claude_bin(), "-p", "--plugin-dir", str(PLUGIN_DIR), "--agent", f"scriptorium:{task.agent}",
           "--model", cfg.model(task.role or task.agent), "--output-format", "json",
           "--permission-mode", "acceptEdits", "--allowedTools", *ALLOWED]
    logdir = cfg.work / "logs" / stage
    logdir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    try:
        p = subprocess.run(cmd, input=task.prompt, cwd=cfg.root, env=session_env(cfg, stage), text=True,
                           capture_output=True, timeout=cfg.session_timeout_min * 60)
        raw, err = p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        raw, err = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), "timeout"
    rec: dict = {"label": task.label, "agent": task.agent, "model": cfg.model(task.role or task.agent),
                 "seconds": round(time.time() - t0, 1)}
    try:
        out = json.loads(raw.strip().splitlines()[-1])
        u = out.get("usage", {}) or {}
        rec.update({"ok": not out.get("is_error", False), "turns": out.get("num_turns"),
                    "session_id": out.get("session_id"), "result": (out.get("result") or "")[-4000:],
                    "tokens": {k: u.get(k, 0) for k in ("input_tokens", "output_tokens", "cache_read_input_tokens",
                                                        "cache_creation_input_tokens")}})
    except (IndexError, json.JSONDecodeError):
        rec.update({"ok": False, "result": (raw or "")[-2000:], "error": (err or "")[-2000:]})
    (logdir / f"{task.label}.json").write_text(json.dumps({**rec, "prompt": task.prompt}, indent=1))
    return rec


def run_tasks(cfg: Config, stage: str, tasks: list[Task], echo=print) -> list[dict]:
    if not tasks:
        return []
    for t in tasks:
        echo(f"    start {t.label} ({t.agent}, {cfg.model(t.role or t.agent)})")
    with ThreadPoolExecutor(max_workers=max(1, cfg.parallel)) as ex:
        recs = list(ex.map(lambda t: run_task(cfg, stage, t), tasks))
    for r in recs:
        tok = r.get("tokens") or {}
        status = "done" if r.get("ok") else "FAILED"
        echo(f"    {status} {r['label']}: {r.get('turns') or 0} turns, {r['seconds']:.0f} s, "
             f"{tok.get('output_tokens', 0):,} output tokens"
             + ("" if r.get("ok") else f" ({(r.get('error') or r.get('result') or '')[-200:].strip()})"))
    return recs
