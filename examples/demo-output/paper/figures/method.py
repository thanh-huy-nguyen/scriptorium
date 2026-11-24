import matplotlib
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
matplotlib.rcParams["font.weight"] = "normal"

import scriptorium_diagram as sd
from matplotlib.patches import FancyBboxPatch, Circle, Polygon

PURPLE, LAV, LIGHT = "#4E2A84", "#F1EEF7", "#B6ACD1"
FLIP = "#D8431F"                       # red-orange: flag on a flipped label
CLASS = ["#2F5D8A", "#B07D2B", "#3F7D4E"]
INK = "#2b2530"
GRAY = "#c9c4d3"
FS = 6.3

H_ = 4.1
d = sd.canvas("column", height=H_)
ax = d.ax
for t in ax.texts:          # nothing yet; fonts come from rcParams
    t.set_fontweight("normal")

pw, ph = 1.4, 1.85
x1, x2 = 0.07, 1.78
yb = 0.05
yt = yb + ph + 0.3
c1, c2 = x1 + pw / 2, x2 + pw / 2

for (x, y, t, n) in [(x1, yt, "Noisy labels", 1), (x2, yt, "Predict out of fold", 2),
                     (x1, yb, "Drop disagreements", 3), (x2, yb, "Refit", 4)]:
    d.panel(x, y, pw, ph, t, step=n, fill=LAV, k=0)

# ---- shared tile primitive -------------------------------------------------
FLIPS = {(0, 1), (1, 3), (2, 0), (3, 4)}          # flipped labels
ROWS, COLS = 4, 5


def true_cls(r, c):
    return (r + 2 * c) % 3


def given(r, c):
    t = true_cls(r, c)
    return (t + 1) % 3 if (r, c) in FLIPS else t


def pred(r, c):
    if (r, c) == (3, 4):          # a flip the model misses
        return given(r, c)
    if (r, c) == (1, 1):          # a clean sample the model gets wrong
        return (true_cls(r, c) + 1) % 3
    return true_cls(r, c)


def dropped(r, c):
    return pred(r, c) != given(r, c)


def label(x, y, s, **kw):
    ax.text(x, y, s, ha=kw.pop("ha", "center"), va="center", fontsize=FS, color=INK,
            fontweight="normal", family="sans-serif", zorder=10, **kw)


def tile(x, y, s, r, c, show_pred=False, cross=False):
    ax.add_patch(FancyBboxPatch((x, y), s, s, boxstyle="round,pad=0,rounding_size=0.025",
                                fc="white", ec="#9a93a8", lw=0.6, zorder=5))
    if show_pred:
        ax.add_patch(Circle((x + s / 2, y + s * 0.64), s * 0.19, fc=CLASS[pred(r, c)],
                            ec="none", zorder=6))
    else:
        ax.add_patch(Circle((x + s / 2, y + s * 0.64), s * 0.19, fc=GRAY, ec="none", zorder=6))
    ax.add_patch(FancyBboxPatch((x + s * 0.15, y + s * 0.1), s * 0.7, s * 0.2,
                                boxstyle="round,pad=0,rounding_size=0.015",
                                fc=CLASS[given(r, c)], ec="none", zorder=6))
    if (r, c) in FLIPS:       # red-orange corner flag
        f = s * 0.36
        ax.add_patch(Polygon([(x + s - f, y + s), (x + s, y + s), (x + s, y + s - f)],
                             closed=True, fc=FLIP, ec="none", zorder=7))
    if cross:
        m = s * 0.1
        for (p, q) in [((x + m, y + m), (x + s - m, y + s - m)),
                       ((x + m, y + s - m), (x + s - m, y + m))]:
            ax.plot([p[0], q[0]], [p[1], q[1]], color=INK, lw=1.6, solid_capstyle="round",
                    zorder=9)


S, P = 0.21, 0.25


def grid_x(cx):
    return cx - ((COLS - 1) * P + S) / 2


def grid(cx, top, **kw):
    gx = grid_x(cx)
    for c in range(COLS):
        for r in range(ROWS):
            tile(gx + c * P, top - S - r * P, S, r, c,
                 show_pred=kw.get("show_pred", False),
                 cross=kw.get("cross", False) and dropped(r, c))
    return gx


def classifier(cx, cy, s):
    """Neutral classifier glyph: a line separating two dot clusters on a purple card."""
    ax.add_patch(FancyBboxPatch((cx - s / 2, cy - s / 2), s, s,
                                boxstyle="round,pad=0,rounding_size=0.04",
                                fc=PURPLE, ec="none", zorder=6))
    for (dx, dy) in [(-.26, .22), (-.1, .3), (-.28, .06)]:
        ax.add_patch(Circle((cx + dx * s, cy + dy * s), s * 0.07, fc="white", ec="none", zorder=7))
    for (dx, dy) in [(.26, -.22), (.1, -.3), (.28, -.06)]:
        ax.add_patch(Circle((cx + dx * s, cy + dy * s), s * 0.07, fc=LIGHT, ec="none", zorder=7))
    ax.plot([cx - .3 * s, cx + .3 * s], [cy - .3 * s, cy + .3 * s], color="white", lw=1.2,
            solid_capstyle="round", zorder=7)


def check(cx, cy, s):
    ax.plot([cx - .4 * s, cx - .1 * s, cx + .45 * s], [cy, cy - .35 * s, cy + .4 * s],
            color=PURPLE, lw=2.6, solid_capstyle="round", solid_joinstyle="round", zorder=8)


top = 1.43

# ---- 1 Noisy labels --------------------------------------------------------
grid(c1, yt + top)
ax.add_patch(Polygon([(c1 - 0.46, yt + 0.22), (c1 - 0.34, yt + 0.22), (c1 - 0.34, yt + 0.1)],
                     closed=True, fc=FLIP, ec="none", zorder=7))
label(c1 - 0.28, yt + 0.16, "flipped label", ha="left")

# ---- 2 Predict out of fold -------------------------------------------------
gx = grid_x(c2)
bot2 = yt + top - (ROWS - 1) * P - S
for c in range(COLS):
    held = c == COLS - 1
    ax.add_patch(FancyBboxPatch((gx + c * P - 0.025, bot2 - 0.03), S + 0.05,
                                ROWS * P - (P - S) + 0.06,
                                boxstyle="round,pad=0,rounding_size=0.03",
                                fc="white" if held else LIGHT,
                                ec=PURPLE if held else "none", lw=1.6, zorder=3))
for c in range(COLS):
    for r in range(ROWS):
        tile(gx + c * P, yt + top - S - r * P, S, r, c)
mid = gx + 1.5 * P + S / 2                  # centre of the four training strips
hx = gx + 4 * P + S / 2                     # held-out strip
ncy = yt + 0.16
d.arrow((mid, bot2 - 0.05), (mid, ncy + 0.14))
label(mid - 0.07, bot2 - 0.16, "train on 4", ha="right")
classifier(mid, ncy, 0.24)
d.elbow((mid + 0.15, ncy), (hx, bot2 - 0.05))
label(hx - 0.08, bot2 - 0.16, "predict 5th", ha="right")

# ---- 3 Drop disagreements --------------------------------------------------
grid(c1, yb + top, show_pred=True, cross=True)
label(c1, yb + 0.3, "dot = predicted")
label(c1, yb + 0.14, "4 dropped")

# ---- 4 Refit ---------------------------------------------------------------
kept = [(r, c) for r in range(ROWS) for c in range(COLS) if not dropped(r, c)]
s4, p4 = 0.19, 0.22
gx4 = c2 - (5 * p4 + s4) / 2
for i, (r, c) in enumerate(kept):
    rr, cc = divmod(i, 6)
    tile(gx4 + cc * p4, yb + top - s4 - rr * p4, s4, r, c)
bot4 = yb + top - s4 - 2 * p4
label(c2, bot4 - 0.1, "kept samples")
d.arrow((c2, bot4 - 0.17), (c2, yb + 0.5))
classifier(c2 - 0.18, yb + 0.3, 0.3)
check(c2 + 0.28, yb + 0.3, 0.3)

# ---- arrows between panels ---------------------------------------------------
my = yt + ph / 2
d.arrow((x1 + pw + 0.04, my), (x2 - 0.04, my))
d.arrow((x1 + pw + 0.04, yb + ph / 2), (x2 - 0.04, yb + ph / 2))
d.elbow((c2, yt - 0.02), (c1, yb + ph + 0.02))
for t in ax.texts:
    t.set_fontfamily("DejaVu Sans")
    t.set_fontweight("normal")
d.save("method")
