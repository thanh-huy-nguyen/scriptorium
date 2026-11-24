"""`scriptorium watch`: a live view of a run, read from .scriptorium/state.json and events.jsonl.

It only reads files, so it can run in a second terminal while `scriptorium run` works, or after the run ends.
"""
from __future__ import annotations

import sys
import time

from . import events, state
from . import stages as S
from .config import Config

MARK = {"done": "done", "skipped": "skip", "running": "RUN", "failed": "FAIL", "pending": "."}


def _dur(s: float) -> str:
    s = int(max(0, s))
    return f"{s // 3600}h{s % 3600 // 60:02d}m" if s >= 3600 else f"{s // 60}m{s % 60:02d}s"


def render(cfg: Config, width: int = 100) -> str:
    s = state.load(cfg)
    evs = events.read(cfg)
    now = time.time()
    run_t0 = evs[0]["t"] if evs and evs[0]["ev"] == "run_start" else None
    ended = next((e for e in reversed(evs) if e["ev"] == "run_end"), None)
    tot_out = sum(u.get("output_tokens", 0) for u in s["usage"].values())
    tot_sess = sum(u.get("sessions", 0) for u in s["usage"].values())
    head = f"Scriptorium  {S.outline(cfg).get('title') or cfg.title}"
    if run_t0:
        head += f"   run {_dur((ended['t'] if ended else now) - run_t0)}"
        head += f" ({ended['status']})" if ended else ""
    lines = [head, f"{tot_sess} agent sessions, {tot_out:,} output tokens", ""]

    started = {e["stage"]: e["t"] for e in evs if e["ev"] == "stage_start"}
    done_at = {e["stage"]: e["t"] for e in evs if e["ev"] in ("stage_done", "stage_failed")}
    lines.append(f"{'stage':<12} {'state':<5} {'after':<24} {'sessions':>8} {'out tokens':>11} {'time':>7}  note")
    for st in S.pipeline(cfg):
        rec = s["stages"].get(st.name, {})
        status = rec.get("status", "pending")
        u = s["usage"].get(st.name, {})
        t = ""
        if st.name in started:
            t = _dur(done_at.get(st.name, now if status == "running" else started[st.name]) - started[st.name])
        note = ""
        if st.name in s["scores"]:
            note = f"review {s['scores'][st.name]['mean']}"
        if rec.get("fixes"):
            note += ("; " if note else "") + f"{rec['fixes']} fix round(s)"
        if status == "failed" and rec.get("errors"):
            note += ("; " if note else "") + rec["errors"][0].splitlines()[0][:50]
        lines.append(f"{st.name:<12} {MARK.get(status, status):<5} {', '.join(st.deps)[:24]:<24} "
                     f"{u.get('sessions', 0):>8} {u.get('output_tokens', 0):>11,} {t:>7}  {note}"[:width])

    run = events.running_tasks(evs) if not ended else []
    lines += ["", f"Agents working now ({len(run)})"]
    for e in run:
        lines.append(f"  {e['stage']:<12} {e['agent']:<15} {e['label']:<28} {e.get('model', ''):<8} "
                     f"{_dur(now - e['t']):>7}"[:width])
    waits = [e for e in evs if e["ev"] == "limit_wait"]
    if waits and not ended and now - waits[-1]["t"] < waits[-1]["minutes"] * 60:
        left = waits[-1]["minutes"] * 60 - (now - waits[-1]["t"])
        lines.append(f"  usage limit reached: sessions resume in about {_dur(left)}")

    recent = [e for e in evs if e["ev"] in ("stage_start", "stage_check", "stage_done", "stage_failed", "task_end")]
    lines += ["", "Recent"]
    for e in recent[-8:]:
        ts = time.strftime("%H:%M", time.localtime(e["t"]))
        if e["ev"] == "task_end":
            msg = (f"{e['label']} {'finished' if e.get('ok') else 'FAILED'} in {_dur(e.get('seconds') or 0)}, "
                   f"{e.get('output_tokens', 0):,} output tokens")
        elif e["ev"] == "stage_check":
            msg = ("checks pass" if e["status"] == "done" and not e.get("errors") else
                   f"checks: {e['status']}, {len(e.get('errors') or [])} problem(s)"
                   + (f": {e['errors'][0][:60]}" if e.get("errors") else ""))
        elif e["ev"] == "stage_start":
            msg = "started"
        elif e["ev"] == "stage_done":
            msg = "skipped" if e.get("skipped") else "accepted" + (f" (history {e['commit']})" if e.get("commit") else "")
        else:
            msg = "FAILED"
        lines.append(f"  {ts} {e.get('stage', ''):<12} {msg}"[:width])
    return "\n".join(lines)


def watch(cfg: Config, once: bool = False, interval: float = 2.0) -> None:
    if once or not sys.stdout.isatty():
        print(render(cfg))
        return
    try:
        while True:
            import shutil
            w = shutil.get_terminal_size((100, 40)).columns
            sys.stdout.write("\x1b[H\x1b[2J" + render(cfg, w) + "\n\n(ctrl-c to stop watching; the run continues)\n")
            sys.stdout.flush()
            evs = events.read(cfg)
            if evs and evs[-1]["ev"] == "run_end":
                return
            time.sleep(interval)
    except KeyboardInterrupt:
        print()
