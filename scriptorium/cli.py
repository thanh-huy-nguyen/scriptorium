"""scriptorium: a team of agents that writes a paper from a research repository, with every number and citation checked.

Set up and run (from the root of the research repository):
    scriptorium init                 set up: venue, authors, preset (asks, or takes --venue --title ...); locks the data
    scriptorium doctor               check Claude Code, LaTeX, Python packages and the bibliographic databases
    scriptorium run                  run every remaining stage headless with `claude -p`
    scriptorium run --from outline   rerun from a stage (that stage and every stage that depends on it)
    scriptorium run --pause-at story stop once a stage is done, to read or edit its output before going on
    scriptorium watch                live view of a run: stages, agents working now, tokens (second terminal)
    scriptorium status               stages, review scores and token use
    scriptorium report               write .scriptorium/report.html: every number, citation, figure and session
    scriptorium history              one entry per finished stage (paper/ and notes as they were)
    scriptorium rollback STAGE       put paper/ and notes back to right after STAGE; later stages rerun
    scriptorium reset STAGE          mark a stage and every stage that depends on it as not done

Used by the agents, and handy by hand:
    scriptorium numbers              run every recipe in paper/sources.py and list the values
    scriptorium check [FILE ...]     every tagged number in paper/*.tex recomputes (PaperAnchor); exit 1 if not
    scriptorium cite search QUERY    look a paper up in OpenAlex, arXiv, Crossref and DBLP (--source s2 for Semantic Scholar)
    scriptorium cite add ID          add doi:DOI, arxiv:ID, openalex:W..., dblp:KEY or s2:ID to paper/refs.bib
    scriptorium cite verify          every \\cite resolves and every entry was fetched, not typed
    scriptorium cite abstract ID     fetch and keep a paper's abstract (OpenAlex, arXiv, Semantic Scholar)
    scriptorium cite card KEY        what a cited paper says: its reading card and abstract
    scriptorium figure SCRIPT        run one figure script from the repository root
    scriptorium build                rerun the figure scripts and compile paper/main.tex
    scriptorium audit PAPER_DIR      check an existing LaTeX paper: build, references, citations, claims, reviews
    scriptorium figlint [ID ...]     check figures at print size: text size, overlaps, contrast, colours, recipe values
    scriptorium themes               render a sample plot and diagram in every figure theme, to choose one
    scriptorium lint                 flag prose habits that read as machine-written
    scriptorium ledger               check the claim ledger and write .scriptorium/ledger.md
    scriptorium table [ID ...]       render paper/table_ID.tex from .scriptorium/tables/ID.json
    scriptorium consistency          cross-paper checks (references, significance, scope words)
    scriptorium peek PATH            first rows of a data file
    scriptorium validate FILE        check a handoff file (outline, ledger, pitch, table spec, review) before handing on

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

from . import __version__, anchor, cite, engine, events, handoffs, history, htmlreport, latex, lint, lock, state
from . import config as C
from . import stages as S
from . import watch as W

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


def _ask(prompt: str, default: str) -> str:
    try:
        got = input(f"{prompt} [{default}]: ").strip()
    except EOFError:
        got = ""
    return got or default


def init_answers(a) -> dict:
    """Settings for a new scriptorium.toml: from flags, else asked interactively (when a terminal is attached)."""
    from . import venues
    ans = {"title": a.title, "authors": [x.strip() for x in a.authors.split(",")] if a.authors else None,
           "affiliation": a.affiliation, "template": a.venue, "preset": a.preset, "mode": a.mode}
    interactive = sys.stdin.isatty() and not a.yes
    if interactive:
        print("Setting up Scriptorium. Press Enter to keep the value in brackets.\n")
        ans["title"] = ans["title"] or _ask("Working title", "Working title")
        au = _ask("Authors, comma-separated", ", ".join(ans["authors"] or []) or "First Author")
        ans["authors"] = [x.strip() for x in au.split(",") if x.strip()]
        ans["affiliation"] = ans["affiliation"] or _ask("Affiliation", "Your institution")
        print("Venues: " + ", ".join(f"{k} ({v['name']}, {v['page_limit']} pages)" for k, v in venues.VENUES.items())
              + ", default (a clean two-column layout)")
        ans["template"] = ans["template"] or _ask("Venue", "default")
        ans["mode"] = ans["mode"] or _ask("Mode: review (anonymous) or final", "review")
        ans["preset"] = ans["preset"] or _ask("Preset: lite, standard or max", "standard")
    t = ans.get("template") or "default"
    if t != "default" and not venues.is_venue(t) and not (Path(t) / "main.tex").exists():
        sys.exit(f"scriptorium init: unknown venue {t!r}; choose one of {', '.join(venues.VENUES)}, default, "
                 "or a folder holding main.tex")
    v = venues.VENUES.get(t, {})
    ans["venue"] = a.venue_text or v.get("name") or "workshop"
    ans["page_limit"] = a.page_limit or v.get("page_limit") or 8
    return ans


def cmd_init(a) -> None:
    root = Path.cwd().resolve()
    if not (root / "scriptorium.toml").exists():
        (root / "scriptorium.toml").write_text(C.render_toml(**init_answers(a)))
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
    from . import venues
    if venues.is_venue(cfg.template):
        try:
            got = venues.fetch(cfg.template, cfg.paper)
            print(f"fetched the official {venues.VENUES[cfg.template]['name']} style files: {', '.join(got)}")
        except Exception as e:  # noqa: BLE001  offline is fine; render_main retries before the first build
            print(f"could not fetch the {cfg.template} style files now ({e}); they are fetched again at the outline")
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
    history.init(cfg)
    real, sys.stdout = sys.stdout, Tee(sys.stdout, cfg.work / "run.log")
    try:
        status = engine.run_graph(cfg, stop_after=a.to_stage)
        if status == "done":
            print(f"\nall stages done. Paper: paper/main.pdf; report: .scriptorium/report.html (and report.md)")
            if (cfg.work / "report.md").exists():
                print("\n" + (cfg.work / "report.md").read_text())
        elif status == "paused":
            print(f"\npaused after {a.to_stage}. Read or edit its output, then `scriptorium run` to go on.")
        elif status == "stuck":
            print("\nno stage can start; see `scriptorium status`")
    finally:
        sys.stdout.f.close()
        sys.stdout = real
    if status in ("failed", "stuck"):
        sys.exit(1)


def descendants(cfg: C.Config, name: str) -> list[str]:
    """`name` and every stage that depends on it, directly or not, in pipeline order."""
    pipe = S.pipeline(cfg)
    out = {name}
    for st in pipe:
        if any(d in out for d in st.deps):
            out.add(st.name)
    return [st.name for st in pipe if st.name in out]


def reset(cfg: C.Config, name: str) -> None:
    names = [s.name for s in S.pipeline(cfg)]
    if name not in names:
        sys.exit(f"no stage {name!r}; stages: {', '.join(names)}")
    s = state.load(cfg)
    for n in descendants(cfg, name):
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


def cmd_watch(a) -> None:
    W.watch(need_root(), once=a.once)


def cmd_report(a) -> None:
    cfg = need_root()
    print(f"wrote {htmlreport.write(cfg).relative_to(cfg.root)}")


def cmd_history(a) -> None:
    cfg = need_root()
    log = history.log(cfg)
    if not log:
        print("no history yet (it starts with the first finished stage)" if history.available() else
              "git is not installed, so Scriptorium keeps no stage history")
        return
    for c in log:
        print(f"{c['id']}  {c['time']}  {c['subject']}")


def cmd_rollback(a) -> None:
    cfg = need_root()
    c = history.rollback(cfg, a.target)
    pending = [n for n, r in state.load(cfg)["stages"].items() if r.get("status") not in S.FINISHED]
    print(f"paper/ and notes restored to {c['stage']} ({c['id']}, {c['time']}). Stages to run again: "
          f"{', '.join(pending) or 'none'}. The state before the rollback is kept in the history.")


def cmd_validate(a) -> None:
    cfg = need_root()
    bad = 0
    for f in a.files:
        errs = handoffs.validate(cfg, f)
        bad += bool(errs)
        print(f"{f}: ok" if not errs else f"{f}: {len(errs)} problem(s)\n  - " + "\n  - ".join(errs))
    sys.exit(1 if bad else 0)


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
        root = C.find_root()
        if root:
            from . import lit
            lit.record(root, q, hits)
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
    elif a.action == "abstract":
        from . import lit
        for cid in a.args:
            d = lit.abstract(cfg, cid, refresh=a.refresh)
            print(f"{cid}: {d.get('title')} ({d.get('year')}), from {d.get('source') or 'nowhere'}\n"
                  f"{d.get('abstract') or '(no abstract could be fetched: mark the card unverifiable)'}\n")
    elif a.action == "card":
        from . import lit
        for key in a.args:
            cid, c, ab = lit.key_card(cfg, key)
            print(f"{key} -> {cid or '(not added with cite add)'}")
            print(json.dumps(c, indent=1) if c else "(no card)")
            print("abstract: " + ((ab or {}).get("abstract") or "(none fetched; try `scriptorium cite abstract ID`)")
                  + "\n")
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


def cmd_doctor(a) -> None:
    """Check everything a run needs, before it spends any tokens."""
    import importlib.util
    import urllib.request
    rows = []

    def row(ok, what, detail=""):
        rows.append((ok, what, detail))
    root = C.find_root()
    cfg = C.load(root) if root else None
    claude = (cfg.claude_bin() if cfg else "claude")
    path = shutil.which(claude) or (claude if Path(claude).exists() else None)
    ver = subprocess.run([path, "--version"], capture_output=True, text=True).stdout.strip() if path else ""
    row(bool(path), "Claude Code", ver or "install it from https://claude.com/claude-code")
    eng = cfg.latex_engine() if cfg else (shutil.which("tectonic") or shutil.which("latexmk"))
    row(bool(eng), "LaTeX engine", eng or "install tectonic (https://tectonic-typesetting.github.io) or latexmk")
    for mod, why in (("matplotlib", "figures"), ("numpy", "figures and statistics"), ("pymupdf", "page counts and "
                     "figure lint"), ("paperanchor", "number checks")):
        row(importlib.util.find_spec(mod) is not None, f"Python package {mod}", f"needed for {why}")
    for name, url in (("OpenAlex", "https://api.openalex.org/works?per-page=1"),
                      ("Crossref", "https://api.crossref.org/works?rows=1"),
                      ("arXiv", "https://export.arxiv.org/api/query?search_query=all:test&max_results=1")):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "scriptorium doctor"}),
                                        timeout=15) as r:
                row(r.status == 200, f"{name} reachable", "")
        except Exception as e:  # noqa: BLE001
            row(False, f"{name} reachable", f"{str(e)[:60]} (citations fall back to the other databases)")
    if cfg:
        row(True, "Project", f"{cfg.title} | venue {cfg.template} ({cfg.mode}) | preset {cfg.preset} | "
                             f"{len(S.pipeline(cfg))} stages")
        if cfg.template not in ("", "default"):
            from . import venues
            if venues.is_venue(cfg.template):
                have = all((cfg.paper / Path(f).name).exists() for f in venues.VENUES[cfg.template]["files"])
                row(have, "Venue style files", "in paper/" if have else "run `scriptorium init` again to fetch them")
    for ok, what, detail in rows:
        print(f"{'ok  ' if ok else 'FAIL'} {what}" + (f": {detail}" if detail else ""))
    sys.exit(0 if all(ok for ok, w, _ in rows if "reachable" not in w) else 1)


def cmd_audit(a) -> None:
    from . import audit
    src = Path(a.paper)
    out = Path(a.out) if a.out else Path.cwd() / f"{src.resolve().name}-audit"
    cfg = audit.setup(src, out, venue=a.venue_text, template=a.venue or "default")
    print(f"audit folder: {out} (your paper is copied to {out}/src and never changed)")
    if a.setup_only:
        return
    if shutil.which(cfg.claude_bin()) is None and not Path(cfg.claude_bin()).exists():
        sys.exit("scriptorium: the `claude` command was not found; install Claude Code first")
    history.init(cfg)
    real, sys.stdout = sys.stdout, Tee(sys.stdout, cfg.work / "run.log")
    try:
        status = engine.run_graph(cfg)
    finally:
        sys.stdout.f.close()
        sys.stdout = real
    rep = cfg.work / "audit" / "report.md"
    if rep.exists():
        print("\n" + rep.read_text())
        print(f"\nreport: {rep} (and report.html)")
    if status != "done":
        sys.exit(1)


def cmd_figlint(a) -> None:
    cfg = need_root()
    from . import figlint, visuals
    ids = a.ids or visuals.figure_ids(cfg)
    specs = [dict(visuals.spec(cfg, i), id=i) for i in ids]
    res = figlint.lint(cfg, specs, visuals.ours_labels(cfg))
    bad = 0
    for fid, probs in res.items():
        bad += bool(probs)
        print(f"{fid}: ok" if not probs else f"{fid}: {len(probs)} problem(s)\n  - " + "\n  - ".join(probs))
    sys.exit(1 if bad else 0)


def cmd_themes(a) -> None:
    from . import visuals
    root = C.find_root()
    out = Path(a.out) if a.out else ((root / C.WORK / "themes") if root else Path.cwd() / "scriptorium-themes")
    page = visuals.gallery(out)
    print(f"wrote {page}: the same plot and diagram in every theme. Set one with [figures] theme = \"...\"")


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


def cmd_ledger(a) -> None:
    from . import ledger, tables as T
    cfg = need_root()
    nums = S.good_numbers(cfg)
    figs = [f.get("id") for f in S.outline(cfg).get("figures", [])]
    tabs = [p.stem for p in (cfg.work / "tables").glob("*.json")] if (cfg.work / "tables").exists() else []
    errs = ledger.validate(cfg, S.read_json(cfg.work / "numbers.json") or {}, figs, tabs)
    ledger.render_md(cfg)
    print("\n".join("- " + e for e in errs) if errs else
          f"ok: {len(ledger.load(cfg).get('claims', []))} claims; wrote .scriptorium/ledger.md")
    sys.exit(1 if errs else 0)


def cmd_table(a) -> None:
    from . import tables as T
    cfg = need_root()
    nums = S.read_json(cfg.work / "numbers.json") or S.refresh_numbers(cfg)
    errs = T.build(cfg, nums, a.ids or None)
    print("\n".join("- " + e for e in errs) if errs else "ok: rendered " + ", ".join(
        f"paper/table_{t}.tex" for t in (a.ids or sorted(p.stem for p in (cfg.work / "tables").glob("*.json")))))
    sys.exit(1 if errs else 0)


def cmd_consistency(a) -> None:
    from . import consistency
    cfg = need_root()
    p = consistency.write_report(cfg, S.read_json(cfg.work / "numbers.json") or {})
    print(p.read_text())


def cmd_peek(a) -> None:
    """First rows of a data file inside the repository (agents cannot run Python themselves)."""
    cfg = need_root()
    p = (cfg.root / a.path).resolve()
    if not p.is_relative_to(cfg.root) or any(w in str(p) for w in ("sealed", "judging")):
        sys.exit("scriptorium peek: only files inside the repository")
    if not p.exists():
        sys.exit(f"scriptorium peek: {a.path} does not exist")
    if p.is_dir():
        for q in sorted(p.iterdir())[:200]:
            print(q.name + ("/" if q.is_dir() else f"  ({q.stat().st_size:,} bytes)"))
        return
    suf = p.suffix.lower()
    if suf in (".npz", ".npy"):
        r = subprocess.run([cfg.py(), "-c", "import sys, numpy as np\nx = np.load(sys.argv[1], allow_pickle=False)\n"
                            "items = x.items() if hasattr(x, 'items') else [('array', x)]\n"
                            "for k, v in items: print(k, v.shape, v.dtype, v.ravel()[:8])", str(p)],
                           capture_output=True, text=True, env=__import__("scriptorium.sealing", fromlist=["x"]).jail_env(cfg),
                           timeout=120)
        print(r.stdout or r.stderr)
        return
    if suf in (".parquet", ".pkl", ".pickle", ".pt", ".pth", ".h5", ".hdf5"):
        print(f"{p.name}: {p.stat().st_size:,} bytes; binary format, describe it from the code that writes or reads it")
        return
    with p.open(errors="replace") as f:
        lines = [next(f, None) for _ in range(a.n)]
    print("".join(l for l in lines if l is not None)[:20000])
    try:
        total = sum(1 for _ in p.open(errors="replace"))
        print(f"... {total:,} lines in total")
    except OSError:
        pass


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
    p = sub.add_parser("init")
    p.add_argument("--venue", default="", help="neurips, iclr, icml, cvpr, acl, miccai, ieee, default, or a folder")
    p.add_argument("--title", default="")
    p.add_argument("--authors", default="", help="comma-separated")
    p.add_argument("--affiliation", default="")
    p.add_argument("--preset", default="", choices=["", "lite", "standard", "max"])
    p.add_argument("--mode", default="", choices=["", "review", "final"])
    p.add_argument("--page-limit", dest="page_limit", type=int, default=0)
    p.add_argument("--venue-text", dest="venue_text", default="", help="the venue as the agents should see it")
    p.add_argument("--yes", "-y", action="store_true", help="never ask; use flags and defaults")
    p.set_defaults(f=cmd_init)
    p = sub.add_parser("run")
    p.add_argument("--from", dest="from_stage")
    p.add_argument("--to", "--pause-at", dest="to_stage")
    p.set_defaults(f=cmd_run)
    p = sub.add_parser("watch")
    p.add_argument("--once", action="store_true")
    p.set_defaults(f=cmd_watch)
    sub.add_parser("report").set_defaults(f=cmd_report)
    sub.add_parser("history").set_defaults(f=cmd_history)
    p = sub.add_parser("rollback")
    p.add_argument("target", help="a stage name or a history id")
    p.set_defaults(f=cmd_rollback)
    p = sub.add_parser("validate")
    p.add_argument("files", nargs="+")
    p.set_defaults(f=cmd_validate)
    p = sub.add_parser("reset")
    p.add_argument("stage")
    p.set_defaults(f=lambda a: (reset(need_root(), a.stage),
                                print(f"pending again: {', '.join(descendants(need_root(), a.stage))}")))
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
    p.add_argument("action", choices=["search", "add", "verify", "abstract", "card"])
    p.add_argument("--refresh", action="store_true")
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
    sub.add_parser("doctor").set_defaults(f=cmd_doctor)
    p = sub.add_parser("audit", help="check an existing LaTeX paper (it is copied; the original is never changed)")
    p.add_argument("paper", help="the folder holding the paper's .tex and .bib files")
    p.add_argument("--out", default="", help="the audit folder (default: <paper>-audit here)")
    p.add_argument("--venue", default="", help="neurips, iclr, icml, cvpr, acl, miccai, ieee: sets limits and reviewers")
    p.add_argument("--venue-text", dest="venue_text", default="", help="the venue as the reviewers should see it")
    p.add_argument("--setup-only", action="store_true")
    p.set_defaults(f=cmd_audit)
    p = sub.add_parser("figlint")
    p.add_argument("ids", nargs="*")
    p.set_defaults(f=cmd_figlint)
    p = sub.add_parser("themes")
    p.add_argument("--out", default="")
    p.set_defaults(f=cmd_themes)
    sub.add_parser("ledger").set_defaults(f=cmd_ledger)
    p = sub.add_parser("table")
    p.add_argument("ids", nargs="*")
    p.set_defaults(f=cmd_table)
    sub.add_parser("consistency").set_defaults(f=cmd_consistency)
    p = sub.add_parser("peek")
    p.add_argument("path")
    p.add_argument("-n", type=int, default=15)
    p.set_defaults(f=cmd_peek)
    p = sub.add_parser("lock")
    p.add_argument("--verify", action="store_true")
    p.set_defaults(f=cmd_lock)
    a = ap.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    main()
