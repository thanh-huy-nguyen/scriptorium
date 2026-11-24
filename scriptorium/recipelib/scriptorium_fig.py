"""House style for figure scripts in paper/figures/*.py.

    import scriptorium_fig as sf
    sf.use()                                   # the project's theme (scriptorium.toml [figures] theme)
    fig, ax = sf.figure("column", aspect=0.62) # sized at print width, so font sizes are real points
    for m in methods:
        ax.bar(x, sf.recipe(f"acc_{m}_mean"), color=sf.color(m, ours=(m == "filter")))
    sf.save(fig, "noise_sweep")                # paper/figures/noise_sweep.{pdf,png} + layout for the figure lint

Themes:
- academia (default): Northwestern purple for the paper's own method, deep inks for baselines (navy, brass, hunter,
  oxblood, walnut, teal), warm near-black text, Source Serif 4.
- nature: light and clean, a colorblind-safe set (Okabe-Ito order) with purple for ours.
- minimal: grays for baselines and the accent for ours; for dense conference figures.

Rules the lint checks (scriptorium figlint): text at least 6.2 pt at print size, no overlapping or clipped text, the
legend off the data, series distinguishable under colour-vision deficiency, ours in the accent colour, and plotted
values taken from recipes.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
WIDTHS = {"column": 3.25, "full": 6.75, "half": 3.25}   # inches; two-column venue defaults

# Each theme: the paper's method ("ours") and its complementary partner (the strongest comparison), muted companions
# for other baselines, gray for references. Every pair of series colours stays apart under deuteranopia and protanopia
# and in normal vision, and every colour has at least 3:1 contrast on white (checked in tests/test_visuals.py).
_NEUTRAL = {"ref": "#8A8F96", "text": "#1B1F24", "grid": "#E6E8EB", "panel": "#FFFFFF", "edge": "#3A3F45"}
THEMES = {
    "harbor": {"ours": "#0B6E79", "partner": "#D1495B", "base": ["#C08A1E", "#8E7DBE", "#B5838D", "#7D8CA3"],
               **_NEUTRAL},
    "ink-amber": {"ours": "#1D3557", "partner": "#E07A1F", "base": ["#5B8C5A", "#A05195", "#B5838D", "#8E7DBE"],
                  **_NEUTRAL},
    "forest-coral": {"ours": "#2D6A4F", "partner": "#E76F51", "base": ["#3D5A80", "#B5838D", "#8E7DBE", "#7D8CA3"],
                     **_NEUTRAL},
    "academia": {"ours": "#4E2A84", "partner": "#B07D2B", "base": ["#4D908E", "#8E7DBE", "#3A7D44", "#355070"],
                 **_NEUTRAL},
    "nature": {"ours": "#0072B2", "partner": "#D55E00", "base": ["#009E73", "#E69F00", "#CC79A7", "#56B4E9"],
               "ref": "#999999", "text": "#1A1A1A", "grid": "#EBEBEB", "panel": "#FFFFFF", "edge": "#4D4D4D"},
    "minimal": {"ours": "#0B6E79", "partner": "#3A3A3A", "base": ["#6E6E6E", "#9A9A9A", "#C4C4C4"],
                "ref": "#BFBFBF", "text": "#111111", "grid": "#EEEEEE", "panel": "#FFFFFF", "edge": "#333333"},
}
DEFAULT_THEME = "harbor"


def tint(hex_color: str, t: float) -> str:
    """Mix a colour with white: t=0 keeps it, t=1 gives white."""
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#{:02X}{:02X}{:02X}".format(*(round(c + (255 - c) * t) for c in (r, g, b)))
_state = {"theme": DEFAULT_THEME, "assigned": {}}


def _root() -> Path:
    r = os.environ.get("SCRIPTORIUM_ROOT") or os.environ.get("SCRIPTORIUM_JAIL_ROOT")
    return Path(r) if r else Path.cwd()


def theme_name() -> str:
    env = os.environ.get("SCRIPTORIUM_THEME")
    if env:
        return env
    try:
        import tomllib
        t = tomllib.loads((_root() / "scriptorium.toml").read_text())
        return t.get("figures", {}).get("theme", DEFAULT_THEME)
    except Exception:  # noqa: BLE001
        return DEFAULT_THEME


def palette() -> dict:
    return THEMES[_state["theme"]]


def use(theme: str | None = None, base_size: float = 7.5) -> dict:
    """Set matplotlib's rcParams to the theme. Returns the palette."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    _state["theme"] = theme or theme_name()
    if _state["theme"] not in THEMES:
        _state["theme"] = DEFAULT_THEME
    for f in (HERE / "fonts").glob("*.ttf"):
        try:
            font_manager.fontManager.addfont(str(f))
        except Exception:  # noqa: BLE001
            pass
    p = palette()
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Inter", "DejaVu Sans"], "font.size": base_size,
        "axes.titlesize": base_size, "axes.labelsize": base_size, "xtick.labelsize": base_size - 0.5,
        "ytick.labelsize": base_size - 0.5, "legend.fontsize": base_size - 0.5, "legend.frameon": False,
        "axes.edgecolor": p["edge"], "axes.labelcolor": p["text"], "text.color": p["text"],
        "xtick.color": p["text"], "ytick.color": p["text"], "axes.linewidth": 0.6, "xtick.major.width": 0.6,
        "ytick.major.width": 0.6, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
        "axes.axisbelow": True, "grid.color": p["grid"], "grid.linewidth": 0.5, "lines.linewidth": 1.4,
        "lines.markersize": 3.5, "errorbar.capsize": 2, "savefig.dpi": 300, "pdf.fonttype": 42,
        "axes.prop_cycle": matplotlib.cycler(color=p["base"]),
    })
    return p


def color(name: str, ours: bool = False, reference: bool = False, partner: bool = False) -> str:
    """The method's colour, the same in every figure of the paper: ours gets the accent, the strongest comparison its
    complementary partner (partner=True), the untrained or trivial reference gray, and each other baseline the next
    muted ink in the order first seen (stored in paper/figures/.colors.json so all figures agree)."""
    p = palette()
    if ours:
        return p["ours"]
    if partner:
        return p["partner"]
    if reference:
        return p["ref"]
    store = _root() / "paper" / "figures" / ".colors.json"
    try:
        known = json.loads(store.read_text())
    except Exception:  # noqa: BLE001
        known = {}
    if name not in known:
        known[name] = len(known) % len(p["base"])
        try:
            store.write_text(json.dumps(known, indent=1))
        except OSError:
            pass
    return p["base"][known[name]]


def figure(width: str | float = "column", aspect: float = 0.62, **kw):
    """A figure at its final print width (column, full, or inches), so every font size is a real point size."""
    import matplotlib.pyplot as plt
    if "Inter" not in plt.rcParams.get("font.sans-serif", []):
        use()
    w = WIDTHS.get(width, width) if isinstance(width, str) else float(width)
    kw.setdefault("layout", "constrained")       # keeps labels and an outside legend inside the figure
    fig, ax = plt.subplots(figsize=(w, w * aspect), **kw)
    fig._scriptorium_width = width if isinstance(width, str) else "custom"
    return fig, ax


def recipe(key: str) -> float:
    """The value of a recipe in paper/sources.py, as last computed (.scriptorium/numbers.json). Plot these values so
    the figure shows exactly the numbers the text prints."""
    nums = json.loads((_root() / ".scriptorium" / "numbers.json").read_text())
    rec = nums.get(key)
    if not rec or "value" not in rec:
        raise KeyError(f"{key!r} is not a working recipe; add it to paper/sources.py and run `scriptorium numbers`")
    _state.setdefault("recipes", []).append(key)
    return float(rec["value"])


def grouped_bars(ax, groups: list[str], data: dict, ours: str | None = None, reference: str | None = None,
                 points: dict | None = None, width: float = 0.8, err_label: str = "sd", partner: str | None = None):
    """The house form for aggregate comparisons: one bar per method in each group, error bars, and the individual
    seeds as small dots. `data` maps method -> (means, errors), one value per group, each from sf.recipe();
    `points` maps method -> one list of per-seed values per group (optional)."""
    import numpy as np
    names = list(data)
    n = len(names)
    w = width / max(n, 1)
    x = np.arange(len(groups))
    rng = np.random.default_rng(0)
    for i, name in enumerate(names):
        means, errs = data[name]
        c = color(name, ours=(name == ours), reference=(name == reference), partner=(name == partner))
        pos = x - width / 2 + w * (i + 0.5)
        ax.bar(pos, means, w * 0.9, color=c, label=name, zorder=2, linewidth=0)
        ax.errorbar(pos, means, yerr=errs, fmt="none", ecolor=palette()["text"], elinewidth=0.7, capsize=2,
                    zorder=3)
        for g, vals in enumerate((points or {}).get(name) or []):
            jit = (rng.random(len(vals)) - 0.5) * w * 0.45
            ax.scatter(pos[g] + jit, vals, s=4, color="#FFFFFF", edgecolors=palette()["text"], linewidths=0.4,
                       zorder=4, label="_seeds")
    ax.set_xticks(x, groups)
    ax.grid(axis="x", visible=False)
    return ax


def legend_above(ax, ncol: int | None = None, **kw):
    """A legend in one row above the axes, never on the data."""
    h, lab = ax.get_legend_handles_labels()
    keep = [(a, b) for a, b in zip(h, lab) if not b.startswith("_")]
    return ax.legend([a for a, _ in keep], [b for _, b in keep], loc="lower center", bbox_to_anchor=(0.5, 1.0),
                     ncol=ncol or len(keep), frameon=False, handlelength=1.0, columnspacing=1.0, borderaxespad=0.2,
                     **kw)


def _layout(fig) -> dict:
    """Positions of every text, axes, legend and data mark, in inches from the bottom left, for the figure lint."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    dpi = fig.dpi
    W, H = fig.get_size_inches()

    def box(bb):
        return [round(bb.x0 / dpi, 4), round(bb.y0 / dpi, 4), round(bb.x1 / dpi, 4), round(bb.y1 / dpi, 4)]

    texts, marks, series, legends, axes = [], [], [], [], []
    hidden = set()                 # tick labels matplotlib does not draw (ticks outside the view limits)
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            if not ax.axison or not axis.get_visible():
                for t in axis.get_major_ticks() + axis.get_minor_ticks():
                    hidden.update({id(t.label1), id(t.label2)})
                continue
            try:
                drawn = {id(t) for t in axis._update_ticks()}
                for t in axis.get_major_ticks() + axis.get_minor_ticks():
                    if id(t) not in drawn:
                        hidden.update({id(t.label1), id(t.label2)})
            except Exception:  # noqa: BLE001  private API; without it every tick label is checked
                pass
    for t in fig.findobj(lambda a: hasattr(a, "get_text") and hasattr(a, "get_fontsize")):
        try:
            if not t.get_visible() or not t.get_text().strip() or id(t) in hidden:
                continue
            gid = t.get_gid() or ""
            texts.append({"text": t.get_text()[:80], "size": float(t.get_fontsize()), "box": box(t.get_window_extent(r)),
                          "color": _hex(t.get_color()), "legend": False,
                          "bg": gid[3:] if gid.startswith("bg:") else "#ffffff"})
        except Exception:  # noqa: BLE001
            continue
    for ax in fig.axes:
        axes.append(box(ax.get_window_extent(r)))
        leg = ax.get_legend()
        if leg is not None and leg.get_visible():
            legends.append(box(leg.get_window_extent(r)))
        for ln in ax.get_lines():
            if not ln.get_visible() or ln.get_label().startswith("_child") and len(ln.get_xdata()) < 2:
                continue
            xy = ax.transData.transform(list(zip(ln.get_xdata(), ln.get_ydata()))) if len(ln.get_xdata()) else []
            pts = list(xy)
            if ln.get_linestyle() not in ("None", "none", "") and len(pts) > 1:
                pts = [(x0 + (x1 - x0) * k / 12, y0 + (y1 - y0) * k / 12)
                       for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]) for k in range(12)] + [tuple(pts[-1])]
            marks += [[round(x / dpi, 4), round(y / dpi, 4)] for x, y in pts]
            series.append({"label": ln.get_label(), "color": _hex(ln.get_color())})
        for c in ax.collections:
            try:
                offs = c.get_offsets()
                if len(offs):
                    xy = ax.transData.transform(offs)
                    marks += [[round(x / dpi, 4), round(y / dpi, 4)] for x, y in xy]
                    fc = c.get_facecolor()
                    if len(fc):
                        series.append({"label": c.get_label(), "color": _hex(fc[0])})
            except Exception:  # noqa: BLE001
                continue
        for cont in ax.containers:
            lab = cont.get_label() if hasattr(cont, "get_label") else ""
            first = next(iter(cont), None) if hasattr(cont, "__iter__") else None
            if lab and not lab.startswith("_") and first is not None and hasattr(first, "get_facecolor"):
                series.append({"label": lab, "color": _hex(first.get_facecolor())})
        for patch in ax.patches:
            try:
                bb = patch.get_window_extent(r)
                if bb.width > 0 and bb.height > 0:
                    marks.append([round((bb.x0 + bb.x1) / 2 / dpi, 4), round(bb.y1 / dpi, 4)])
                    series.append({"label": patch.get_label(), "color": _hex(patch.get_facecolor())})
            except Exception:  # noqa: BLE001
                continue
    for t in texts:
        x0, y0, x1, y1 = t["box"]
        t["legend"] = any(l[0] - 0.01 <= x0 and x1 <= l[2] + 0.01 and l[1] - 0.01 <= y0 and y1 <= l[3] + 0.01
                          for l in legends)
    return {"size": [float(W), float(H)], "width": getattr(fig, "_scriptorium_width", "custom"),
            "kind": getattr(fig, "_scriptorium_kind", "plot"), "issues": getattr(fig, "_scriptorium_issues", []),
            "texts": texts,
            "axes": axes, "legends": legends, "marks": marks, "series": series, "theme": _state["theme"],
            "palette": palette(), "recipes": sorted(set(_state.get("recipes", [])))}


def _hex(c) -> str:
    from matplotlib.colors import to_hex
    try:
        return to_hex(c)
    except Exception:  # noqa: BLE001
        return "#000000"


def save(fig, fid: str) -> None:
    """Save paper/figures/<fid>.pdf and .png, plus <fid>.layout.json for the figure lint."""
    out = _root() / "paper" / "figures"
    out.mkdir(parents=True, exist_ok=True)
    lay = _layout(fig)
    fig.savefig(out / f"{fid}.pdf", bbox_inches=None)
    fig.savefig(out / f"{fid}.png", dpi=200, bbox_inches=None)
    (out / f"{fid}.layout.json").write_text(json.dumps(lay))
