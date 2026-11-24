"""README and social visuals for Scriptorium: banner.png, pipeline.png, social_preview.png in assets/.

Run: python tools/make_assets.py   (needs matplotlib; fonts are in tools/fonts, SIL OFL / DejaVu licenses)
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "assets"
for f in (HERE / "fonts").glob("*.ttf"):
    font_manager.fontManager.addfont(str(f))
SERIF, DISPLAY, MONO = "Source Serif 4", "Cormorant Garamond", "DejaVu Sans Mono"

NIGHT, NIGHT2 = "#17121F", "#211A2D"
PARCH, PARCH_EDGE, PARCH2 = "#F4EDE0", "#C9B994", "#EADFCB"
BRASS, BRASS_DK = "#D2AE62", "#9A7A36"
OXBLOOD, PURPLE, PURPLE_DK, LILAC, LAV = "#A3202B", "#4E2A84", "#2E1A52", "#C3B6DD", "#ECE8F2"
INK, MUTED, TEAL, ARROW = "#1E1A17", "#4B443D", "#2F5D62", "#2B2530"


def canvas(w, h, dpi, bg):
    fig = plt.figure(figsize=(w, h), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    fig.patch.set_facecolor(bg)
    return fig, ax


def ledger(ax, w, h, step=0.24):
    y = step
    while y < h:
        ax.plot([0, w], [y, y], color=NIGHT2, lw=0.6, zorder=0)
        y += step
    ax.add_patch(FancyBboxPatch((0.12, 0.12), w - 0.24, h - 0.24, boxstyle="round,pad=0,rounding_size=0.12",
                                fc="none", ec=BRASS_DK, lw=0.9, zorder=1))


def box(ax, x, y, w, h, fc, ec, lw=1.0, r=0.08, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw,
                                zorder=z))


def arrow(ax, a, b, color=ARROW, lw=1.3, z=3):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>,head_length=0.62,head_width=0.3", mutation_scale=5.5 + 2.6 * lw,
                                 color=color, lw=lw, shrinkA=0, shrinkB=0, zorder=z))


def quill(ax, cx, cy, s, color):
    """A small quill: a curved feather and a nib, drawn with two filled paths."""
    from matplotlib.path import Path as MP
    from matplotlib.patches import PathPatch
    v = [(0.0, 0.0), (0.18, 0.35), (0.55, 0.9), (1.0, 1.0), (0.85, 0.55), (0.45, 0.18), (0.0, 0.0)]
    codes = [MP.MOVETO, MP.CURVE3, MP.CURVE3, MP.LINETO, MP.CURVE3, MP.CURVE3, MP.CLOSEPOLY]
    pts = [(cx + s * (x - 0.5), cy + s * (y - 0.5)) for x, y in v]
    ax.add_patch(PathPatch(MP(pts, codes), fc=color, ec="none", zorder=6))
    ax.plot([cx - 0.5 * s, cx + 0.42 * s], [cy - 0.5 * s, cy + 0.42 * s], color=NIGHT, lw=0.8 * s / 0.5, zorder=7,
            solid_capstyle="round")


def logo_tile(ax, x, y, s):
    box(ax, x, y, s, s, PURPLE, BRASS, lw=1.4, r=0.16 * s, z=5)
    quill(ax, x + 0.5 * s, y + 0.52 * s, 0.62 * s, PARCH)
    ax.plot([x + 0.2 * s, x + 0.8 * s], [y + 0.16 * s, y + 0.16 * s], color=BRASS, lw=1.4, zorder=6)


def paper_card(ax, x, y, w, h, fs=1.0):
    box(ax, x, y, w, h, PARCH, PARCH_EDGE, lw=1.0, r=0.06, z=4)
    t = lambda yy, s, **k: ax.text(x + 0.22, yy, s, fontfamily=SERIF, color=INK, zorder=6, va="center", **k)
    t(y + h - 0.32, "4  Results", fontsize=13 * fs, fontweight="semibold")
    t(y + h - 0.68, "The filter recovers most of the", fontsize=10.5 * fs)
    t(y + h - 0.98, "accuracy that label noise costs:", fontsize=10.5 * fs)
    ax.text(x + 0.22, y + h - 1.30, "92.6%", fontfamily=SERIF, fontsize=10.5 * fs, color=INK, zorder=6, va="center")
    ax.text(x + 0.92, y + h - 1.30, "\\src{acc}", fontfamily=MONO, fontsize=8.5 * fs, color=PURPLE, zorder=6,
            va="center")
    ax.text(x + w - 0.24, y + h - 1.30, "✓ recomputes", fontfamily="DejaVu Sans", fontsize=9 * fs, color=TEAL, zorder=6,
            va="center", ha="right", fontweight="semibold")
    t(y + h - 1.62, "vs. 83.6% for logistic regression [5].", fontsize=10.5 * fs)
    ax.text(x + w - 0.24, y + h - 1.62, "✓ cited", fontfamily="DejaVu Sans", fontsize=9 * fs, color=TEAL, zorder=6,
            va="center", ha="right", fontweight="semibold")
    for i, ww in enumerate([0.86]):
        ax.plot([x + 0.22, x + 0.22 + (w - 0.44) * ww], [y + 0.24] * 2, color=PARCH_EDGE, lw=2.2,
                zorder=5, solid_capstyle="round")


def banner(w=10.0, h=3.2, dpi=200, name="banner.png", tagline=True):
    fig, ax = canvas(w, h, dpi, NIGHT)
    ledger(ax, w, h)
    logo_tile(ax, 0.55, h - 1.25, 0.72)
    ax.text(1.48, h - 0.89, "Scriptorium", fontfamily=DISPLAY, fontweight="bold", fontsize=42, color=PARCH,
            va="center")
    ax.text(0.58, h - 1.72, "A team of agents writes your paper from your repository.", fontfamily=SERIF,
            fontsize=13.5, color=BRASS, va="center", style="italic")
    lines = ["Every number recomputes from your data.", "Every citation is fetched and checked.",
             "Every hand-off between 25 agents is checked in code."]
    for i, s in enumerate(lines):
        yy = h - 2.15 - 0.3 * i
        ax.add_patch(Circle((0.66, yy), 0.05, fc=BRASS, ec="none", zorder=4))
        ax.text(0.82, yy, s, fontfamily=SERIF, fontsize=11.5, color=LILAC, va="center")
    # the team, as a row of numbered seals feeding the paper card
    names = ["discovery", "literature", "story", "visuals", "writing", "checking", "review", "release"]
    x0, y0, dx = 6.71, h - 0.38, 0.34
    for i, nm in enumerate(names):
        cx = x0 + i * dx
        ax.add_patch(Circle((cx, y0), 0.1, fc=PURPLE if i < 6 else OXBLOOD, ec=BRASS, lw=0.9, zorder=5))
        ax.text(cx, y0, str(i + 1), fontfamily=SERIF, fontsize=7, color=PARCH, ha="center", va="center", zorder=6)
        if i:
            ax.plot([cx - dx + 0.1, cx - 0.1], [y0, y0], color=BRASS_DK, lw=0.9, zorder=4)
    ax.text(x0 - 0.18, y0, "eight teams", fontfamily=SERIF, fontsize=9, color=LILAC, ha="right", va="center",
            style="italic")
    paper_card(ax, 5.55, 0.34, 3.95, 2.3)
    fig.savefig(OUT / name, dpi=dpi, facecolor=NIGHT)
    plt.close(fig)


WRITES = ["sources.py  setup.json  lit/cards", "ledger.json  outline.json  figures/", "paper/*.tex  audit.json",
          "reviews/  report.html  arxiv.tar.gz"]


def pipeline(dpi=200):
    w, h = 10.0, 4.6
    fig, ax = canvas(w, h, dpi, "white")
    phases = [
        ("1", "Understand", [("Discovery", "scout, experimentalist, results analyst, statistician"),
                             ("Literature", "searcher, readers in parallel, librarian")],
         ["setup quotes its source file", "verdicts match their p-values", "only papers a search returned"]),
        ("2", "Plan", [("Story", "cartographer, architects, outliner, terminologist"),
                       ("Visuals", "figure planner, plot maker, diagram artist, critic, tables")],
         ["claims carry their evidence", "figures pass lint and a critic", "one name per thing"]),
        ("3", "Write", [("Writing", "writers in parallel, contests, editor, line editors"),
                        ("Checking", "claim auditor, citation auditor, typesetter")],
         ["PaperAnchor at every edit", "flagged lines must change", "citations match the paper"]),
        ("4", "Review", [("Review", "venue reviewers, area chair, reviser"),
                         ("Release", "arXiv bundle, HTML report")],
         ["kept only if the score holds", "else rolled back", "every stage in git history"]),
    ]
    pw, gap, x = 2.16, 0.3, 0.19
    top = h - 0.22
    for k, (num, title, teams, checks) in enumerate(phases):
        box(ax, x, 1.32, pw, top - 1.32, LAV if k % 2 else PARCH, PARCH_EDGE if k % 2 == 0 else LILAC, lw=1.0, r=0.1)
        ax.add_patch(Circle((x + 0.3, top - 0.3), 0.15, fc=PURPLE, ec="none", zorder=4))
        ax.text(x + 0.3, top - 0.3, num, fontfamily=SERIF, fontsize=10, color="white", ha="center", va="center",
                zorder=5)
        ax.text(x + 0.55, top - 0.3, title, fontfamily=SERIF, fontsize=13, color=INK, va="center")
        for i, (nm, who) in enumerate(teams):
            yy = top - 0.98 - i * 0.86
            box(ax, x + 0.16, yy - 0.36, pw - 0.32, 0.74, "white", PURPLE if k % 2 else PARCH_EDGE, lw=0.9, r=0.06)
            ax.text(x + 0.3, yy + 0.18, nm, fontfamily=SERIF, fontsize=10.5, color=PURPLE_DK, va="center",
                    fontweight="semibold")
            words, line, lines = who.split(), "", []
            for wd in words:
                if len(line) + len(wd) > 30:
                    lines.append(line.strip())
                    line = ""
                line += wd + " "
            lines.append(line.strip())
            for j, ln in enumerate(lines[:2]):
                ax.text(x + 0.3, yy - 0.06 - j * 0.19, ln, fontfamily=SERIF, fontsize=8.2, color=MUTED, va="center")
        ax.text(x + 0.18, 1.5, WRITES[k], fontfamily=MONO, fontsize=6.4, color=MUTED, va="center")
        if k < len(phases) - 1:
            arrow(ax, (x + pw + 0.04, 2.9), (x + pw + gap - 0.04, 2.9))
        box(ax, x, 0.16, pw, 1.0, "#FBF6EA", BRASS_DK, lw=0.9, r=0.08)
        ax.text(x + 0.16, 0.98, "checked in code", fontfamily=SERIF, fontsize=8.4, color=BRASS_DK, va="center",
                style="italic")
        for i, c in enumerate(checks):
            ax.text(x + 0.16, 0.72 - i * 0.22, "✓", fontfamily="DejaVu Sans", fontsize=9, color=TEAL, va="center",
                    fontweight="semibold")
            ax.text(x + 0.36, 0.72 - i * 0.22, c, fontfamily=SERIF, fontsize=8.3, color=INK, va="center")
        x += pw + gap
    fig.savefig(OUT / "pipeline.png", dpi=dpi, facecolor="white")
    plt.close(fig)


def social():
    fig, ax = canvas(6.4, 3.2, 200, NIGHT)
    ledger(ax, 6.4, 3.2)
    logo_tile(ax, 0.55, 2.05, 0.72)
    ax.text(1.45, 2.42, "Scriptorium", fontfamily=DISPLAY, fontweight="bold", fontsize=34, color=PARCH, va="center")
    ax.text(0.58, 1.6, "A team of agents writes your paper", fontfamily=SERIF, fontsize=15, color=BRASS,
            va="center", style="italic")
    ax.text(0.58, 1.25, "from your research repository.", fontfamily=SERIF, fontsize=15, color=BRASS, va="center",
            style="italic")
    ax.text(0.58, 0.72, "25 agents  ·  Numbers recompute  ·  Citations checked", fontfamily=SERIF,
            fontsize=11, color=LILAC, va="center")
    fig.savefig(OUT / "social_preview.png", dpi=200, facecolor=NIGHT)
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    banner()
    pipeline()
    social()
    print("wrote", ", ".join(sorted(p.name for p in OUT.glob("*.png"))))
