"""Run agent sessions headless with `claude -p`.

Two kinds of session:

- Agent sessions run inside the research repository with the Scriptorium plugin loaded. The plugin supplies the agents
  (agents/*.md) and the hooks: PaperAnchor's number check on every edit, and a guard that confines every file access
  to the repository and every edit to paper/ and .scriptorium/.
- Judge sessions run with no tools (or only Read, confined to a fresh temporary directory), no plugin, no settings,
  and no saved transcript, so nothing a judge reads or writes is ever on disk where an agent could find it.

Both retry when the subscription's usage limit is hit: they wait for the reset time when the CLI reports one, or back
off, then resume the same session when it had started.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from . import anchor
from .config import PKG, PLUGIN_DIR, Config

JAIL_DIR = PKG / "jail"

# Shell commands an agent may run. The guard hook also checks every path they name stays inside the repository, and
# Python runs only through `scriptorium` commands, inside the import-time jail (see jail.py).
ALLOWED = ["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "TodoWrite",
           "Bash(scriptorium *)", "Bash(ls *)", "Bash(wc *)", "Bash(head *)", "Bash(tail *)", "Bash(cat *)",
           "Bash(grep *)", "Bash(diff *)"]

TOKEN_KEYS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")

LIMIT_RE = re.compile(r"usage limit|limit reached|hit your limit|rate.?limit|too many requests|overloaded|\b429\b|\b529\b"
                      r"|quota|try again later", re.I)
RESET_EPOCH_RE = re.compile(r"limit reached\|(\d{9,11})")
_limit_lock = threading.Lock()
_resume_after = [0.0]          # shared across threads: when the subscription is expected to accept requests again


@dataclass
class Task:
    agent: str           # one of config.ROLES
    label: str           # unique within its stage, used for the log file
    prompt: str
    role: str = ""       # model role; defaults to the agent name


def session_env(cfg: Config, stage: str, role: str = "") -> dict[str, str]:
    env = os.environ.copy()
    env.update({
        "SCRIPTORIUM_STAGE": stage,
        "SCRIPTORIUM_ROLE": role,
        "SCRIPTORIUM_ROOT": str(cfg.root),
        "SCRIPTORIUM_PYTHON": cfg.py(),
        "SCRIPTORIUM_PAPERANCHOR": anchor.package_path(),
        "SCRIPTORIUM_JAIL_ROOT": str(cfg.root),
        "PAPERANCHOR_MODE": cfg.check_mode,
    })
    env["PATH"] = os.pathsep.join([str(Path(sys.executable).parent), env.get("PATH", "")])
    env["PYTHONPATH"] = os.pathsep.join(p for p in [str(JAIL_DIR), env.get("PYTHONPATH", "")] if p)
    env["PAPERANCHOR_EXTRA_PATH"] = os.pathsep.join([str(PKG / "recipelib"), str(JAIL_DIR)])
    env["PAPERANCHOR_PRELOAD"] = "scriptorium_jail"
    if cfg.unset_api_key:
        env.pop("ANTHROPIC_API_KEY", None)
    for k in [k for k in env if k.startswith("SCRIPTORIUM_SEALED")]:
        env.pop(k)
    return env


RESET_AT_RE = re.compile(r"resets\s+(?:([A-Z][a-z]{2})\s+(\d{1,2}),\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)"
                         r"(?:\s*\(([^)]+)\))?", re.I)
MONTHS = {m: i for i, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov",
                                      "dec"), 1)}


def reset_seconds(text: str) -> float | None:
    """Seconds until a reset time such as 'resets Nov 23, 7pm (America/New_York)' or 'resets 3:30pm'."""
    m = RESET_AT_RE.search(text or "")
    if not m:
        return None
    from datetime import datetime, timedelta
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(m.group(6)) if m.group(6) else None
    except Exception:  # noqa: BLE001
        tz = None
    now = datetime.now(tz) if tz else datetime.now()
    hour = int(m.group(3)) % 12 + (12 if m.group(5).lower() == "pm" else 0)
    minute = int(m.group(4) or 0)
    if m.group(1):
        t = now.replace(month=MONTHS.get(m.group(1).lower()[:3], now.month), day=int(m.group(2)), hour=hour,
                        minute=minute, second=0, microsecond=0)
        if t < now - timedelta(days=180):
            t = t.replace(year=t.year + 1)
    else:
        t = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if t < now:
            t += timedelta(days=1)
    return max(60.0, (t - now).total_seconds() + 120)


def limit_wait(text: str, attempt: int, cfg: Config, status: int | None = None) -> float | None:
    """Seconds to wait if the session hit a usage or rate limit (by its HTTP status or its message), else None. Waits
    for the stated reset time when there is one (weekly limits can be days away), else backs off."""
    if status not in (429, 529) and (not text or not LIMIT_RE.search(text)):
        return None
    m = RESET_EPOCH_RE.search(text or "")
    if m:
        return max(60.0, int(m.group(1)) - time.time() + 60)
    r = reset_seconds(text)
    if r is not None:
        return r
    return min(cfg.limit_max_wait_min * 60, 60 * (2 ** min(attempt, 8)))


def _wait_for_window(echo) -> None:
    while True:
        with _limit_lock:
            left = _resume_after[0] - time.time()
        if left <= 0:
            return
        echo(f"    usage limit: waiting {left / 60:.0f} min")
        time.sleep(min(left, 600))


def _parse(raw: str) -> dict | None:
    for line in reversed((raw or "").strip().splitlines()):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(d, dict) and ("result" in d or "is_error" in d):
            return d
    return None


def _tokens(out: dict) -> dict:
    u = out.get("usage", {}) or {}
    return {k: int(u.get(k, 0) or 0) for k in TOKEN_KEYS}


def _call(cfg: Config, cmd: list[str], prompt: str, cwd: Path, env: dict, echo=print) -> dict:
    """Run one `claude -p` command with limit handling. Returns {ok, out, raw, err, attempts, waited, tokens}."""
    tokens = {k: 0 for k in TOKEN_KEYS}
    waited, attempt, session = 0.0, 0, None
    while True:
        _wait_for_window(echo)
        c = list(cmd)
        p_in = prompt
        if session:
            c += ["--resume", session]
            p_in = "You were interrupted by a usage limit. Continue the task exactly where you stopped."
        try:
            p = subprocess.run(c, input=p_in, cwd=cwd, env=env, text=True, capture_output=True,
                               timeout=cfg.session_timeout_min * 60)
            raw, err = p.stdout, p.stderr
        except subprocess.TimeoutExpired as e:
            raw = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
            err = "timeout"
        out = _parse(raw)
        if out:
            for k, v in _tokens(out).items():
                tokens[k] += v
        text = " ".join(str(x) for x in ((out or {}).get("result"), err, raw) if x)
        failed = (not out) or out.get("is_error")
        status = (out or {}).get("api_error_status")
        w = limit_wait(text, attempt, cfg, status) if failed else None
        if w is None or attempt >= cfg.limit_max_retries:
            return {"ok": bool(out) and not out.get("is_error"), "out": out or {}, "raw": raw, "err": err,
                    "attempts": attempt + 1, "waited_s": round(waited), "tokens": tokens}
        with _limit_lock:
            _resume_after[0] = max(_resume_after[0], time.time() + w)
        waited += w
        attempt += 1
        if out and out.get("session_id") and (out.get("num_turns") or 0) > 0:
            session = out["session_id"]


def agent_settings() -> str:
    """Inline settings for agent sessions. Passed inline (not as a file an agent could edit) and ranked above every
    user, project and local settings file. File tools may not read outside the working directory (the repository)."""
    sealed = str(sealed_home())
    return json.dumps({"permissions": {
        "blockReadsOutsideWorkingDirectories": True,
        "deny": [f"Read(/{sealed}/**)", f"Edit(/{sealed}/**)", "WebFetch", "WebSearch"]}})


def sealed_home() -> Path:
    return Path(os.environ.get("SCRIPTORIUM_HOME") or Path.home() / ".scriptorium") / "sealed"


def run_task(cfg: Config, stage: str, task: Task, echo=print) -> dict:
    model = cfg.model(task.role or task.agent)
    cmd = [cfg.claude_bin(), "-p", "--plugin-dir", str(PLUGIN_DIR), "--agent", f"scriptorium:{task.agent}",
           "--model", model, "--output-format", "json", "--permission-mode", "acceptEdits",
           "--settings", agent_settings(), "--allowedTools", *ALLOWED]
    logdir = cfg.work / "logs" / stage
    logdir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    r = _call(cfg, cmd, task.prompt, cfg.root, session_env(cfg, stage, task.agent), echo)
    out = r["out"]
    rec: dict = {"label": task.label, "agent": task.agent, "model": model, "seconds": round(time.time() - t0, 1),
                 "ok": r["ok"], "turns": out.get("num_turns"), "session_id": out.get("session_id"),
                 "attempts": r["attempts"], "waited_s": r["waited_s"], "tokens": r["tokens"],
                 "result": (out.get("result") or r["raw"] or "")[-4000:]}
    if not r["ok"]:
        rec["error"] = (r["err"] or "")[-2000:]
    (logdir / f"{task.label}.json").write_text(json.dumps({**rec, "prompt": task.prompt}, indent=1))
    return rec


def run_tasks(cfg: Config, stage: str, tasks: list[Task], echo=print) -> list[dict]:
    if not tasks:
        return []
    for t in tasks:
        echo(f"    start {t.label} ({t.agent}, {cfg.model(t.role or t.agent)})")
    with ThreadPoolExecutor(max_workers=max(1, cfg.parallel)) as ex:
        recs = list(ex.map(lambda t: run_task(cfg, stage, t, echo), tasks))
    for r in recs:
        tok = r.get("tokens") or {}
        status = "done" if r.get("ok") else "FAILED"
        echo(f"    {status} {r['label']}: {r.get('turns') or 0} turns, {r['seconds']:.0f} s, "
             f"{tok.get('output_tokens', 0):,} output tokens"
             + (f", waited {r['waited_s'] / 60:.0f} min for the usage limit" if r.get("waited_s") else "")
             + ("" if r.get("ok") else f" ({(r.get('error') or r.get('result') or '')[-200:].strip()})"))
    return recs


# ---------------------------------------------------------------------------------------------------------------------
# Judge sessions

JUDGE_FLAGS = ["--output-format", "json", "--no-session-persistence", "--setting-sources", "",
               "--strict-mcp-config", "--permission-mode", "default",
               "--system-prompt", "You are a careful scientific peer reviewer. Follow the task exactly and answer only in "
                                  "the requested format."]


def run_judge(cfg: Config, model: str, prompt: str, files: dict[str, Path] | None = None, echo=print,
              json_schema: dict | None = None) -> dict:
    """One sealed judge call. `files` maps a name to a file that is copied into a fresh temporary directory the judge may
    Read (PDFs, page images); without files the judge has no tools at all. Nothing is persisted: the temporary
    directory is deleted and the session is not saved. Returns {ok, text, tokens, seconds, attempts, waited_s}."""
    tmp = Path(tempfile.mkdtemp(prefix="scr-judge-"))
    try:
        for name, src in (files or {}).items():
            dst = tmp / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        cmd = [cfg.claude_bin(), "-p", "--model", model, *JUDGE_FLAGS]
        if files:
            cmd += ["--tools", "Read", "--restricted", "--allowedTools", "Read"]
        else:
            cmd += ["--tools", ""]
        if json_schema:
            cmd += ["--json-schema", json.dumps(json_schema)]
        env = os.environ.copy()
        for k in [k for k in env if k.startswith("SCRIPTORIUM_")]:
            env.pop(k)
        if cfg.unset_api_key:
            env.pop("ANTHROPIC_API_KEY", None)
        t0 = time.time()
        r = _call(cfg, cmd, prompt, tmp, env, echo)
        out = r["out"]
        text = out.get("result") or ""
        if json_schema and out.get("structured_output") is not None:
            text = json.dumps(out["structured_output"])
        return {"ok": r["ok"], "text": text, "tokens": r["tokens"], "seconds": round(time.time() - t0, 1),
                "attempts": r["attempts"], "waited_s": r["waited_s"], "model": model,
                "error": "" if r["ok"] else (r["err"] or r["raw"] or "")[-500:]}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
