"""scriptorium: a team of agents that writes a paper from a research repository, with every number and citation checked.

Set up and run (from the root of the research repository):
    scriptorium init                 create scriptorium.toml, brief.md and paper/, and lock the repository's data
    scriptorium run                  run every remaining stage headless with `claude -p`
    scriptorium run --from outline   rerun from a stage (that stage and every later one)
    scriptorium reset STAGE          mark a stage and every later one as not done
    scriptorium status               stages, review scores and token use

Used by the agents, and handy by hand:
    scriptorium numbers              run every recipe in paper/sources.py and list the values
    scriptorium check [FILE ...]     every tagged number in paper/*.tex recomputes (PaperAnchor); exit 1 if not
    scriptorium cite search QUERY    look a paper up in OpenAlex, arXiv, Crossref and DBLP (--source s2 for Semantic Scholar)
    scriptorium cite add ID          add doi:DOI, arxiv:ID, openalex:W..., dblp:KEY or s2:ID to paper/refs.bib
    scriptorium cite verify          every \\cite resolves and every entry was fetched, not typed
    scriptorium figure SCRIPT        run one figure script from the repository root
    scriptorium build                rerun the figure scripts and compile paper/main.tex
    scriptorium lint                 flag prose habits that read as machine-written

Inside a Claude Code session (the /scriptorium:write-paper skill drives these):
    scriptorium next                 start the next stage and print its agent tasks as JSON
    scriptorium done STAGE           check a stage after its agents ran; prints done, fix tasks, or failure
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from . import __version__, anchor, cite, latex, lint, lock, state
from . import config as C
from . import stages as S
from .runner import run_tasks

BRIEF = """# Brief for the paper

Write a few lines under each heading. The agents read this first; the data in the repository decides what the paper
can claim, so it is fine to be rough here.

## Working title

## The idea in one paragraph

## What we want to claim
(One line per claim. The evidence agent will tell you which ones the data supports.)

## Where the results live
(Folders or files with the final runs, and which runs to ignore.)

## Must-cite work
(Papers the related work cannot miss, and the baselines' papers.)

## Anything to avoid
"""


class Tee:
    """Print to the terminal and append to .scriptorium/run.log (a log written elsewhere in the repository would be
    quarantined by the data lock)."""

    def __init__(self, stream, path: Path):
        self.stream, self.f = stream, path.open("a", buffering=1)

    def write(self, s):
        self.stream.write(s)
        self.f.write(s)
        return len(s)

    def flush(self):
        self.stream.flush()
        self.f.flush()


def need_root() -> C.Config:
    root = C.find_root()
    if not root:
        sys.exit("scriptorium: no scriptorium.toml here or above; run `scriptorium init` at the repository root")
    return C.load(root)


def cmd_init(a) -> None:
    root = Path.cwd().resolve()
    if not (root / "scriptorium.toml").exists():
        (root / "scriptorium.toml").write_text(C.DEFAULT_TOML)
        print("created scriptorium.toml")
    if not (root / "brief.md").exists():
        (root / "brief.md").write_text(BRIEF)
        print("created brief.md (fill it in)")
    cfg = C.load(root)
    cfg.paper.mkdir(exist_ok=True)
    cfg.work.mkdir(exist_ok=True)
    if not (cfg.work / "style.md").exists():
        shutil.copy2(C.TEMPLATES / "style.md", cfg.work / "style.md")
    anchor.init(cfg)
    gi = root / ".gitignore"
    lines = gi.read_text().splitlines() if gi.exists() else []
    if ".scriptorium/" not in lines:
        gi.write_text("\n".join(lines + [".scriptorium/"]) + "\n")
    p = lock.take(root, cfg.lock_ignore)
    n = len(json.loads(p.read_text()))
    print(f"locked {n} files outside paper/ as read-only data ({p.relative_to(root)})")
    print("next: fill in brief.md and scriptorium.toml, then `scriptorium run`")


def cmd_run(a) -> None:
    cfg = need_root()
    if not (cfg.work / "lock.json").exists():
        sys.exit("scriptorium: run `scriptorium init` first")
    if shutil.which(cfg.claude_bin()) is None and not Path(cfg.claude_bin()).exists():
        sys.exit("scriptorium: the `claude` command was not found; install Claude Code first")
    if a.from_stage:
        reset(cfg, a.from_stage)
    real, sys.stdout = sys.stdout, Tee(sys.stdout, cfg.work / "run.log")
    try:
        run_loop(cfg, a)
    finally:
        sys.stdout.f.close()
        sys.stdout = real


def run_loop(cfg: C.Config, a) -> None:
    while True:
        st = S.next_stage(cfg)
        if st is None:
            print(f"\nall stages done. Report: {(cfg.work / 'report.md').relative_to(cfg.root)}; "
                  f"paper: paper/main.pdf")
            break
        print(f"\n== {st.name}")
        tasks = S.begin(cfg, st)
        recs = run_tasks(cfg, st.name, tasks)
        state.add_usage(cfg, st.name, recs)
        while True:
            res = S.finish(cfg, st)
            for e in res["errors"]:
                print("    check: " + e.splitlines()[0][:220])
            if res["status"] == "fix":
                print(f"    asking the agents to fix {len(res['errors'])} problem(s)")
                recs = run_tasks(cfg, st.name, res["tasks"])
                state.add_usage(cfg, st.name, recs)
                continue
            break
        if res["status"] == "failed":
            print(f"\nstage {st.name} failed; see `scriptorium status`, fix by hand or rerun with "
                  f"`scriptorium run --from {st.name}`")
            sys.exit(1)
        print(f"    {st.name} done")
        if a.to_stage and st.name == a.to_stage:
            break
    if (cfg.work / "report.md").exists() and S.next_stage(cfg) is None:
        print("\n" + (cfg.work / "report.md").read_text())


def reset(cfg: C.Config, name: str) -> None:
    names = [s.name for s in S.pipeline(cfg)]
    if name not in names:
        sys.exit(f"no stage {name!r}; stages: {', '.join(names)}")
    s = state.load(cfg)
    for n in names[names.index(name):]:
        s["stages"][n] = {"status": "pending", "fixes": 0}
        s["scores"].pop(n, None)
        if n in s["usage"]:          # keep what earlier passes spent, apart from the current pass
            old = s.setdefault("usage_earlier", {}).setdefault(n, {})
            for k, v in s["usage"].pop(n).items():
                old[k] = old.get(k, 0) + v
    if name.startswith(("review", "revise")) or names.index(name) <= names.index("review0"):
        s.pop("stop_reviews", None)
        s.pop("decisions", None)
    save_names = set(names[:names.index(name)])
    if s.get("accepted") and s["accepted"] not in save_names:
        s.pop("accepted", None)
    state.save(cfg, s)


def cmd_status(a) -> None:
    cfg = need_root()
    s = state.load(cfg)
    print(f"{'stage':<10} {'status':<9} {'sessions':>8} {'output tok':>11}  notes")
    for st in S.pipeline(cfg):
        rec = s["stages"].get(st.name, {})
        u = s["usage"].get(st.name, {})
        note = ""
        if st.name in s["scores"]:
            note = f"mean review {s['scores'][st.name]['mean']}"
        if rec.get("errors"):
            note += ("; " if note else "") + rec["errors"][0].splitlines()[0][:70]
        print(f"{st.name:<10} {rec.get('status', 'pending'):<9} {u.get('sessions', 0):>8} "
              f"{u.get('output_tokens', 0):>11,}  {note}")
    for k, v in (s.get("decisions") or {}).items():
        print(f"{k}: {v}")


def cmd_next(a) -> None:
    cfg = need_root()
    st = S.next_stage(cfg)
    if st is None:
        print(json.dumps({"stage": None, "message": "all stages done; see .scriptorium/report.md"}))
        return
    tasks = S.begin(cfg, st)
    print(json.dumps({"stage": st.name, "tasks": [
        {"agent": f"scriptorium:{t.agent}", "label": t.label, "model": cfg.model(t.role or t.agent), "prompt": t.prompt}
        for t in tasks]}, indent=1))


def cmd_done(a) -> None:
    cfg = need_root()
    st = S.get(cfg, a.stage)
    res = S.finish(cfg, st)
    out = {"stage": st.name, "status": res["status"], "errors": res["errors"]}
    if res["status"] == "fix":
        out["tasks"] = [{"agent": f"scriptorium:{t.agent}", "label": t.label, "model": cfg.model(t.role or t.agent),
                         "prompt": t.prompt} for t in res["tasks"]]
    print(json.dumps(out, indent=1))


def cmd_numbers(a) -> None:
    cfg = need_root()
    nums = S.refresh_numbers(cfg)
    print(anchor.numbers_table(nums))
    bad = [k for k, v in nums.items() if "error" in v or "value" not in v]
    sys.exit(1 if bad else 0)


def cmd_check(a) -> None:
    cfg = need_root()
    ok, out = anchor.check(cfg, *a.files)
    print(out)
    sys.exit(0 if ok else 1)


def cmd_cite(a) -> None:
    if a.action == "search":
        q = " ".join(a.args)
        if not q:
            sys.exit("usage: scriptorium cite search QUERY")
        srcs = tuple(a.source.split(",")) if a.source else cite.DEFAULT_SOURCES
        hits = cite.search(q, a.n, srcs)
        for h in hits:
            au = ", ".join(h["authors"][:3]) + (" et al." if len(h["authors"]) > 3 else "")
            print(f"{h['id']}\n    {h['title']} ({h['year']}, {h['venue']})\n    {au}")
        for e in getattr(cite.search, "errors", []):
            print(f"(skipped {e})")
        return
    cfg = need_root()
    if a.action == "add":
        for cid in a.args:
            print(cite.add(cfg.root, cid, a.key))
    elif a.action == "verify":
        rep = cite.verify(cfg.root)
        probs = cite.problems(rep)
        print("\n".join(probs) if probs else f"ok: {len(cite.bib_entries(cfg.root))} entries, every \\cite resolves")
        if rep["unused"]:
            print("not cited yet: " + ", ".join(rep["unused"]))
        sys.exit(1 if probs else 0)
    else:
        sys.exit("usage: scriptorium cite search|add|verify")


def cmd_figure(a) -> None:
    cfg = need_root()
    from .sealing import jail_env
    script = (cfg.root / a.script).resolve()
    if not (script.is_relative_to(cfg.paper) and script.suffix == ".py"):
        sys.exit(f"scriptorium figure: {a.script} is not a .py file under paper/")
    r = subprocess.run([cfg.py(), str(script)], cwd=cfg.root, capture_output=True, text=True, env=jail_env(cfg),
                       timeout=900)
    sys.stdout.write(r.stdout[-3000:])
    sys.stderr.write(r.stderr[-3000:])
    stem = Path(a.script).with_suffix("")
    made = [str(p.relative_to(cfg.root)) for p in (cfg.root / stem.parent).glob(stem.name + ".*") if p.suffix != ".py"]
    print(("wrote: " + ", ".join(sorted(made))) if made else "no output file next to the script")
    sys.exit(r.returncode)


def cmd_build(a) -> None:
    cfg = need_root()
    b = latex.build(cfg, figures=not a.no_figures)
    print(b.summary())
    probs = b.problems(cfg.page_limit)
    for p in probs:
        print("- " + p)
    ok, out = anchor.check(cfg)
    if not ok:
        print("- numbers that do not recompute:\n" + out)
    cp = cite.problems(cite.verify(cfg.root)) + S.val_problems(cfg)
    for p in cp:
        print("- " + p)
    sys.exit(0 if (b.ok and not probs and ok and not cp) else 1)


def cmd_lint(a) -> None:
    cfg = need_root()
    flags = lint.lint(cfg.paper)
    print("\n".join(flags) if flags else "no flags")


def cmd_lock(a) -> None:
    cfg = need_root()
    if a.verify:
        print(json.dumps(lock.verify(cfg.root, cfg.lock_ignore, quarantine=False), indent=1))
    else:
        p = lock.take(cfg.root, cfg.lock_ignore)
        print(f"locked {len(json.loads(p.read_text()))} files")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="scriptorium", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=f"scriptorium {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init").set_defaults(f=cmd_init)
    p = sub.add_parser("run")
    p.add_argument("--from", dest="from_stage")
    p.add_argument("--to", dest="to_stage")
    p.set_defaults(f=cmd_run)
    p = sub.add_parser("reset")
    p.add_argument("stage")
    p.set_defaults(f=lambda a: (reset(need_root(), a.stage), print(f"{a.stage} and every later stage set to pending")))
    sub.add_parser("status").set_defaults(f=cmd_status)
    sub.add_parser("next").set_defaults(f=cmd_next)
    p = sub.add_parser("done")
    p.add_argument("stage")
    p.set_defaults(f=cmd_done)
    sub.add_parser("numbers").set_defaults(f=cmd_numbers)
    p = sub.add_parser("check")
    p.add_argument("files", nargs="*")
    p.set_defaults(f=cmd_check)
    p = sub.add_parser("cite")
    p.add_argument("action", choices=["search", "add", "verify"])
    p.add_argument("args", nargs="*")
    p.add_argument("-n", type=int, default=5)
    p.add_argument("--source", default="")
    p.add_argument("--key", default=None)
    p.set_defaults(f=cmd_cite)
    p = sub.add_parser("figure")
    p.add_argument("script")
    p.set_defaults(f=cmd_figure)
    p = sub.add_parser("build")
    p.add_argument("--no-figures", action="store_true")
    p.set_defaults(f=cmd_build)
    sub.add_parser("lint").set_defaults(f=cmd_lint)
    p = sub.add_parser("lock")
    p.add_argument("--verify", action="store_true")
    p.set_defaults(f=cmd_lock)
    a = ap.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    main()
