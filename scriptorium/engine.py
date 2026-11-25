"""The scheduler behind `scriptorium run`: runs the stage graph, starting each stage as soon as its dependencies are
done, so independent teams (literature, figures, tables) work at the same time.

Each stage runs in its own thread: begin (prepare and list tasks), run the agent sessions, then finish (check in code)
and, when the checks fail, give the agents fix tasks until the stage passes or runs out of fixes. Agent sessions from
all stages share one cap ([run] parallel). The checks of different stages run one at a time.
"""
from __future__ import annotations

import time
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait

from . import events, state
from . import stages as S
from .config import Config
from .runner import run_tasks


def run_stage(cfg: Config, st: S.Stage, echo=print) -> dict:
    """Run one stage to the end. Returns the last result of stages.finish ({status, errors})."""
    if state.stage(state.load(cfg), st.name).get("status") != "running":
        st.prepare(cfg)                 # downloads and other slow work, outside the lock the checks share
    tasks = S.begin(cfg, st)
    recs = run_tasks(cfg, st.name, tasks, echo)
    state.add_usage(cfg, st.name, recs)
    while True:
        res = S.finish(cfg, st)
        for e in res["errors"]:
            lines = e.splitlines() or [""]
            echo("    check: " + lines[0][:220])
            for d in [l for l in lines[1:] if l.startswith(("FAIL", "MISSING", "ERROR"))][:3]:
                echo("      " + d[:220])        # the failing lines, so the log says what the check found
        if res["status"] != "fix":
            if res["status"] == "done":
                echo(f"{st.name} done" + (f" with {len(res['errors'])} open problem(s)" if res["errors"] else ""))
            return res
        echo(f"    asking the agents to fix {len(res['errors'])} problem(s)")
        recs = run_tasks(cfg, st.name, res["tasks"], echo)
        state.add_usage(cfg, st.name, recs)


def _echo_for(name: str, out):
    width = 11

    def echo(msg: str) -> None:
        for line in str(msg).splitlines() or [""]:
            out(f"[{name:<{width}}] {line.strip()}")
    return echo


def run_graph(cfg: Config, stop_after: str | None = None, out=print) -> str:
    """Run every stage that is not done. Returns 'done', 'paused' (stop_after reached) or 'failed'."""
    events.emit(cfg, "run_start", parallel=cfg.parallel)
    t0 = time.time()
    active: dict[str, Future] = {}
    failed: list[str] = []
    paused = False
    with ThreadPoolExecutor(max_workers=16) as ex:
        while True:
            if not failed and not paused:
                for st in S.ready(cfg, set(active)):
                    names = ", ".join(st.deps) if st.deps else "the start"
                    out(f"\n== {st.name} (after {names})")
                    active[st.name] = ex.submit(run_stage, cfg, st, _echo_for(st.name, out))
            if not active:
                break
            finished, _ = wait(active.values(), return_when=FIRST_COMPLETED)
            for name in [n for n, f in active.items() if f in finished]:
                f = active.pop(name)
                try:
                    res = f.result()
                except Exception as e:  # noqa: BLE001  a crash in one stage stops the run, not the other threads
                    state.mark(cfg, name, "failed", errors=[f"internal error: {e!r}"])
                    res = {"status": "failed", "errors": [f"internal error: {e!r}"]}
                if res["status"] == "failed":
                    failed.append(name)
                    out(f"\nstage {name} failed; see `scriptorium status`, fix by hand or rerun with "
                        f"`scriptorium run --from {name}`")
                if stop_after and name == stop_after:
                    paused = True
    status = "failed" if failed else ("paused" if paused and not S.all_finished(cfg) else
                                      ("done" if S.all_finished(cfg) else "stuck"))
    events.emit(cfg, "run_end", status=status, seconds=round(time.time() - t0))
    return status
