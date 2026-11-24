"""The visuals team: a figure planner, a plot maker and a diagram artist per figure, a figure lint in code, and a vision
critic that alternates with the makers until each figure passes.

    figplan   figure_planner   one spec per figure: the message, the chart form, the data keys   (figures/plan.json)
    figures   plotter / diagrammer, one per figure, in parallel; code lint (sizes, overlaps, contrast, colours)
    critique  figure_critic, one per figure; a "revise" verdict sends the figure back to its maker, then to a fresh
              critic, until it passes or the rounds run out ([figures] critic_rounds)

`scriptorium themes` renders the same sample plot and diagram in every theme, to choose one.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import figlint, latex, notation
from . import stages as S
from .config import PKG, Config
from .runner import Task

CHARTS = ("grouped bars", "bars", "line", "box", "scatter", "heatmap", "qualitative grid", "diagram", "teaser")


def plan(cfg: Config) -> dict:
    return S.read_json(cfg.work / "figures" / "plan.json") or {}


def spec(cfg: Config, fid: str) -> dict:
    for f in plan(cfg).get("figures", []):
        if f.get("id") == fid:
            return f
    return next((f for f in S.outline(cfg).get("figures", []) if f.get("id") == fid), {"id": fid})


def figure_ids(cfg: Config) -> list[str]:
    return [f["id"] for f in S.outline(cfg).get("figures", []) if f.get("id")]


def ours_labels(cfg: Config) -> list[str]:
    return [t["canonical"] for t in notation.load(cfg).get("terms", []) if t.get("kind") == "method"
            and t.get("canonical")]


class FigPlan(S.Stage):
    max_fix = 2

    def before(self, cfg):
        (cfg.work / "figures").mkdir(exist_ok=True)

    def tasks(self, cfg):
        return [Task("figure_planner", "figplan", S.context(cfg) + (
            "Task: plan every figure in .scriptorium/outline.json (`figures`) in detail and write "
            ".scriptorium/figures/plan.json as your instructions describe. Run `scriptorium validate "
            ".scriptorium/figures/plan.json` and fix every problem."))]

    def validate(self, cfg):
        return plan_problems(cfg)


def plan_problems(cfg: Config) -> list[str]:
    p = cfg.work / "figures" / "plan.json"
    d = S.read_json(p)
    if d is None:
        return [".scriptorium/figures/plan.json is missing or is not valid JSON"]
    errs = []
    nums = S.good_numbers(cfg)
    want = set(figure_ids(cfg))
    got = {f.get("id") for f in d.get("figures", [])}
    if want - got:
        errs.append("plan.json has no spec for: " + ", ".join(sorted(want - got)))
    if got - want:
        errs.append("plan.json plans figures the outline does not have: " + ", ".join(sorted(x for x in got - want if x)))
    for f in d.get("figures", []):
        fid = f.get("id", "?")
        if f.get("kind") not in ("plot", "diagram"):
            errs.append(f"{fid}: kind must be plot or diagram")
        if f.get("chart") not in CHARTS:
            errs.append(f"{fid}: chart must be one of {', '.join(CHARTS)}")
        if f.get("width") not in ("column", "full"):
            errs.append(f"{fid}: width must be column or full")
        for k in ("message", "caption_draft", "layout"):
            if not f.get(k):
                errs.append(f"{fid}: missing `{k}`")
        if f.get("kind") == "plot":
            keys = f.get("data_keys") or []
            if not keys:
                errs.append(f"{fid}: a plot lists the recipe keys it draws in `data_keys`")
            bad = [k for k in keys if k not in nums]
            if bad:
                errs.append(f"{fid}: data_keys that are not working recipes: {', '.join(bad[:8])}")
    fw_ids = {f["id"] for f in S.outline(cfg).get("figures", []) if f.get("role") == "framework" and f.get("id")}
    for f in d.get("figures", []):
        if f.get("id") in fw_ids and f.get("role") != "framework":
            errs.append(f"{f.get('id')}: the outline makes this the framework figure; keep \"role\": \"framework\"")
    teasers = [f for f in d.get("figures", []) if f.get("teaser")]
    if want and len(teasers) != 1:
        errs.append("exactly one figure is the teaser (Figure 1, `\"teaser\": true`)")
    return errs


def maker_task(cfg: Config, fid: str, extra: str = "") -> Task:
    sp = spec(cfg, fid)
    agent = "diagrammer" if sp.get("kind") == "diagram" else "plotter"
    return Task(agent, f"figure-{fid}", S.context(cfg) + (
        f"Task: make figure `{fid}` from its spec in .scriptorium/figures/plan.json:\n{json.dumps(sp, indent=1)}\n"
        f"Write paper/figures/{fid}.py and run it with `scriptorium figure paper/figures/{fid}.py`; it must save "
        f"through scriptorium_fig.save(fig, \"{fid}\") (diagrams: scriptorium_diagram's canvas.save(\"{fid}\")). "
        f"Run `scriptorium figlint {fid}` and fix every problem, look at paper/figures/{fid}.png, then write "
        f".scriptorium/figures/{fid}.md with the caption and what the figure shows." + extra))


class Figures(S.Stage):
    max_fix = 2

    def before(self, cfg):
        (cfg.paper / "figures").mkdir(exist_ok=True)
        (cfg.work / "figures").mkdir(exist_ok=True)

    def tasks(self, cfg):
        return [maker_task(cfg, fid) for fid in figure_ids(cfg)]

    def validate(self, cfg):
        return figure_problems(cfg)

    def fix_tasks(self, cfg, errors):
        msg = "\n\nThe checks found these problems with this figure. Fix them:\n- "
        out = []
        for fid in figure_ids(cfg):
            mine = [e for e in errors if e.startswith(f"{fid}:") or f"/{fid}." in e or f"{fid}.py" in e]
            if mine:
                t = maker_task(cfg, fid, msg + "\n- ".join(mine))
                t.label += "-fix"
                out.append(t)
        return out


def figure_problems(cfg: Config, ids: list[str] | None = None) -> list[str]:
    errs = latex.run_figures(cfg)
    ids = ids or figure_ids(cfg)
    specs = [dict(spec(cfg, fid), id=fid) for fid in ids]
    for fid, problems in figlint.lint(cfg, specs, ours_labels(cfg)).items():
        errs += problems
    for fid in ids:
        if not (cfg.work / "figures" / f"{fid}.md").exists():
            errs.append(f"{fid}: .scriptorium/figures/{fid}.md (caption and what the figure shows) is missing")
    return errs


def critique_path(cfg: Config, fid: str) -> Path:
    return cfg.work / "figures" / f"{fid}.critique.json"


def critique_problems(p: Path) -> list[str]:
    d = S.read_json(p)
    if d is None:
        return [f"{p.name} is missing or is not valid JSON"]
    errs = []
    if d.get("verdict") not in ("pass", "revise"):
        errs.append(f"{p.name}: verdict must be pass or revise")
    for i, x in enumerate(d.get("issues") or [], 1):
        if not isinstance(x, dict) or not x.get("issue") or not x.get("fix"):
            errs.append(f"{p.name}: issue {i} needs `issue` and `fix`")
    if d.get("verdict") == "revise" and not d.get("issues"):
        errs.append(f"{p.name}: a revise verdict lists the issues")
    return errs


class Critique(S.Stage):
    """A critic looks at each figure as printed; a figure it sends back goes to its maker, then to a fresh critic."""

    def __init__(self, name: str, rounds: int = 2):
        super().__init__(name)
        self.max_fix = max(0, 2 * rounds - 1)

    def critic_task(self, cfg, fid):
        sp = spec(cfg, fid)
        return Task("figure_critic", f"critique-{fid}", S.context(cfg) + (
            f"Task: critique figure `{fid}`. Its spec:\n{json.dumps(sp, indent=1)}\nLook at paper/figures/{fid}.png, "
            f"read paper/figures/{fid}.py and .scriptorium/figures/{fid}.md, and write your verdict to "
            f".scriptorium/figures/{fid}.critique.json as your instructions describe. Do not edit the figure."))

    def tasks(self, cfg):
        return [self.critic_task(cfg, fid) for fid in figure_ids(cfg)]

    def status(self, cfg) -> dict[str, str]:
        """fid -> 'pass', 'revise', 'missing' or 'invalid'."""
        out = {}
        for fid in figure_ids(cfg):
            p = critique_path(cfg, fid)
            if not p.exists():
                out[fid] = "missing"
            elif critique_problems(p):
                out[fid] = "invalid"
            else:
                out[fid] = (S.read_json(p) or {}).get("verdict")
        return out

    def validate(self, cfg):
        errs = figure_problems(cfg)
        for fid, st in self.status(cfg).items():
            if st == "revise":
                d = S.read_json(critique_path(cfg, fid)) or {}
                errs.append(f"{fid}: the critic asks for a revision: " + "; ".join(
                    f"{x.get('issue')} -> {x.get('fix')}" for x in d.get("issues", [])))
            elif st in ("missing", "invalid"):
                errs.append(f"{fid}: no valid critique yet")
        return errs

    def fix_tasks(self, cfg, errors):
        out = []
        lint = figure_problems(cfg)
        for fid, st in self.status(cfg).items():
            mine = [e for e in lint if e.startswith(f"{fid}:")]
            if st == "revise" or mine:
                d = S.read_json(critique_path(cfg, fid)) or {}
                items = [f"{x.get('issue')} -> {x.get('fix')}" for x in d.get("issues", [])] + mine
                t = maker_task(cfg, fid, "\n\nThe figure critic and the lint sent this figure back. Fix:\n- "
                               + "\n- ".join(items))
                t.label += "-revise"
                out.append(t)
                p = critique_path(cfg, fid)
                if p.exists():
                    p.rename(p.with_suffix(f".r{len(list(p.parent.glob(f'{fid}.critique.r*')))}.json"))
            elif st in ("missing", "invalid"):
                out.append(self.critic_task(cfg, fid))
        return out

    def on_fail(self, cfg, errors):
        return "continue"          # figures that never fully pass are kept; the problems go into the report


# ---------------------------------------------------------------------------------------------------------------------
# Theme gallery

GALLERY_PLOT = '''
import scriptorium_fig as sf
sf.use({theme!r})
fig, ax = sf.figure("column", aspect=0.7)
groups = ["digits", "wine", "cancer"]
data = {{"Cross-entropy": ([81.2, 88.0, 90.1], [1.4, 2.0, 1.1]), "Co-teaching": ([84.0, 89.9, 91.6], [1.1, 1.5, 1.0]),
        "MLP": ([83.5, 89.2, 91.0], [1.2, 1.8, 1.3]), "Ours": ([88.9, 93.1, 94.0], [0.9, 1.2, 0.8])}}
pts = {{m: [[v - 1.1, v, v + 0.9] for v in d[0]] for m, d in data.items()}}
sf.grouped_bars(ax, groups, data, ours="Ours", partner="Co-teaching", points=pts)
ax.set_ylabel("Test accuracy (%)")
ax.set_ylim(70, 100)
sf.legend_above(ax, ncol=4)
sf.save(fig, "plot_{theme}")
'''

GALLERY_DIAGRAM = '''
import scriptorium_diagram as sd
d = sd.canvas("full", height=1.9, theme={theme!r})
d.panel(0.08, 0.1, 2.05, 1.7, "Train with noisy labels", step=1, k=0)
d.icon("images", 0.6, 0.95, 0.65); d.icon("network", 1.55, 0.95, 0.55)
d.text(0.6, 0.35, "noisy data"); d.text(1.55, 0.35, "K-fold models")
d.panel(2.35, 0.1, 2.05, 1.7, "Flag disagreements", step=2, k=1)
d.icon("magnifier", 2.95, 0.95, 0.55); d.icon("cross", 3.85, 0.95, 0.42)
d.text(2.95, 0.35, "out-of-fold"); d.text(3.85, 0.35, "drop sample")
d.panel(4.62, 0.1, 2.05, 1.7, "Refit on the rest", step=3, k=2)
d.box(4.85, 0.7, 0.9, 0.5, "Filter", ours=True); d.icon("check", 6.25, 0.95, 0.42)
d.text(6.25, 0.35, "cleaner model")
d.arrow((2.0, 0.95), (2.5, 0.95)); d.arrow((4.27, 0.95), (4.77, 0.95))
d.save("diagram_{theme}")
'''


def gallery(out: Path, python: str | None = None) -> Path:
    """Render the sample plot and diagram in every theme into `out`, with an index.html to compare them."""
    import os
    import subprocess
    import sys
    sys.path.insert(0, str(PKG / "recipelib"))
    import scriptorium_fig as sf
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, SCRIPTORIUM_ROOT=str(out),
               PYTHONPATH=os.pathsep.join([str(PKG / "recipelib"), os.environ.get("PYTHONPATH", "")]))
    (out / "paper" / "figures").mkdir(parents=True, exist_ok=True)
    rows = []
    for theme in sf.THEMES:
        for kind, code in (("plot", GALLERY_PLOT), ("diagram", GALLERY_DIAGRAM)):
            r = subprocess.run([python or sys.executable, "-c", code.format(theme=theme)], env=env, cwd=out,
                               capture_output=True, text=True)
            if r.returncode != 0:
                raise RuntimeError(f"{theme} {kind}: {r.stderr.strip().splitlines()[-1:]}")
        rows.append(f"<section><h2>{theme}</h2><div class=row><img class=plot src='paper/figures/plot_{theme}.png'>"
                    f"<img class=diagram src='paper/figures/diagram_{theme}.png'></div></section>")
    (out / "index.html").write_text(
        "<!doctype html><meta charset=utf-8><title>Scriptorium figure themes</title><style>body{font:15px/1.5 "
        "system-ui,sans-serif;max-width:1150px;margin:30px auto;padding:0 20px;color:#1f1b24}h2{font-weight:600;"
        "border-bottom:2px solid #3A3F45}.row{display:flex;gap:24px;align-items:flex-start}.plot{width:340px}"
        ".diagram{width:720px}img{border:1px solid #e4e0ea;border-radius:8px;padding:8px;background:#fff}</style>"
        "<h1>Figure themes</h1><p>Set one in scriptorium.toml: <code>[figures] theme = \"harbor\"</code>. "
        "Your method takes the first colour, the strongest comparison its partner.</p>"
        + "".join(rows))
    return out / "index.html"
