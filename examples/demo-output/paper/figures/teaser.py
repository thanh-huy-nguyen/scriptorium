"""Teaser: the out-of-fold filter (top row), what it removes and what the refit model gains (bottom row).

The scatter positions in the top row are hand-placed and schematic. Every number in the bottom row, the number of
folds and the noise rates come from recipes in paper/sources.py.
"""

import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyBboxPatch, Patch

import scriptorium_diagram as sd
import scriptorium_fig as sf

H = 3.33
d = sd.canvas("full", height=H)
W = d.W

OURS = sf.color("Ours", ours=True)
PARTNER = sf.color("Logistic regression", partner=True)
REF = sf.color("Clean-label reference", reference=True)
LIGHT = sf.tint(OURS, 0.74)
INK = d.pal["text"]
EDGE = d.pal["edge"]
GRID = d.pal["grid"]
TITLE = d.sizes["title"]
HEAD = d.sizes["heading"]
LABEL = d.sizes["text"]
NOTE = d.sizes["note"]
NEUTRAL = d.soft["fills"][3]


def line(p, q, color=EDGE, lw=0.7, z=5):
    d.ax.plot([p[0], q[0]], [p[1], q[1]], color=color, lw=lw, zorder=z, solid_capstyle="round")


def rounded(x, y, w, h, fill="white", edge=EDGE, lw=0.8, r=0.035, z=4):
    d.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", facecolor=fill,
                                  edgecolor=edge, linewidth=lw, zorder=z))


def marker(x, y, filled, r=0.028):
    """A schematic sample: the given class is the marker (filled or open), never a colour."""
    d.ax.add_patch(Circle((x, y), r, facecolor=INK if filled else "white", edgecolor=INK, linewidth=0.8,
                          zorder=6))


def cross(x, y, s=0.048, lw=1.2):
    """Long thin arms, so that the filled or open centre of a struck point stays visible."""
    for dy in (s, -s):
        line((x - s, y - dy), (x + s, y + dy), color=OURS, lw=lw, z=8)


def check(x, y, s=0.05, lw=1.8):
    d.ax.plot([x - s, x - 0.25 * s, x + s], [y, y - 0.75 * s, y + 0.8 * s], color=EDGE, lw=lw, zorder=8,
              solid_capstyle="round", solid_joinstyle="round")


def model_card(cx, cy, ours=False, w=0.40, h=0.28):
    """A small card with an S-shaped curve: a logistic regression."""
    color = OURS if ours else EDGE
    rounded(cx - w / 2, cy - h / 2, w, h, edge=color, lw=1.6 if ours else 0.9, r=0.045)
    t = np.linspace(-1, 1, 80)
    s = 1 / (1 + np.exp(-5.5 * t))
    s = (s - s[0]) / (s[-1] - s[0])
    d.ax.plot(cx + 0.34 * w * t, cy - 0.27 * h + 0.54 * h * s, color=color, lw=1.4, zorder=6,
              solid_capstyle="round")


# ---------------------------------------------------------------------------
# Row 1, panel (a): five equal tiles
# ---------------------------------------------------------------------------
ROW1_Y = 1.69
d.panel(0.0, ROW1_Y, W, H - ROW1_Y, fill=NEUTRAL)
d.text(0.09, H - 0.14, "(a) Filter noisy labels", size=TITLE, ha="left", bg=NEUTRAL, case=None)

MARGIN, GAP = 0.07, 0.17
TW = (W - 2 * MARGIN - 4 * GAP) / 5
TY, TOP = ROW1_Y + 0.05, H - 0.285
TITLE_Y = TOP - 0.13
SY, SW = TY + 0.50, 1.04                     # scatter area shared by the input, drop and refit tiles
LOW_Y = TY + 0.215                           # middle of the strip under the scatter
NOTE_Y = LOW_Y - 0.025                       # one height for the two-line notes of stages 1 and 3

STEP_R, STEP_GAP = 0.085, 0.055
tiles, xs = [], []
for i, title in enumerate(["Noisy labels", "Predict", "Compare", "Drop", "Refit once"]):
    x = MARGIN + i * (TW + GAP)
    xs.append(x)
    tiles.append(d.box(x, TY, TW, TOP - TY, fill="white", edge="white"))
    if i:                                    # stage number directly left of the stage title, centred as one unit
        left = x + (TW - 2 * STEP_R - STEP_GAP - sd.text_width(title, HEAD)) / 2
        d.step(left + STEP_R, TITLE_Y, i, r=STEP_R)
        d.text(left + 2 * STEP_R + STEP_GAP, TITLE_Y, title, size=HEAD, ha="left")
    else:
        d.text(x + TW / 2, TITLE_Y, title, size=HEAD)
d.flow(tiles, width=2.4, color=EDGE, gap=0.015)

# Schematic points as offsets inside the scatter area
FILLED = [(0.06, 0.08), (0.19, 0.04), (0.33, 0.07), (0.05, 0.21), (0.28, 0.19), (0.42, 0.18), (0.32, 0.31),
          (0.07, 0.34)]
OPEN = [(0.70, 0.49), (0.85, 0.53), (0.99, 0.46), (0.68, 0.34), (0.80, 0.41), (1.00, 0.29), (0.74, 0.21),
        (0.91, 0.14)]
# (x, y, filled): three given labels that disagree with the cluster the point sits deep inside
WRONG = [(0.18, 0.21, False), (0.91, 0.36, True), (0.84, 0.24, True)]
ACROSS = (0.635, 0.115, True)                # correctly labeled, just across the border between the clusters


def scatter(i, dropped=True):
    ox = xs[i] + (TW - SW) / 2
    points = [(x, y, True) for x, y in FILLED] + [(x, y, False) for x, y in OPEN]
    if dropped:
        points += WRONG + [ACROSS]
    for x, y, filled in points:
        marker(ox + x, SY + y, filled)
    return ox


# Input: the noisy training set, and what the filter does without. One wrong label is marked, and so is the
# correctly labeled sample that stage 3 drops.
ox = scatter(0)
wx, wy = ox + WRONG[0][0], SY + WRONG[0][1]
d.text(ox - 0.01, SY + 0.47, "Wrong label", size=NOTE, ha="left")
line((wx, SY + 0.40), (wx, wy + 0.04))
cx0, cy0 = ox + ACROSS[0], SY + ACROSS[1]
# "Correct label" sits low and to the right of its point, clear of the filled cluster and of the pills
d.text(ox + 0.75, SY - 0.025, "Correct label", size=NOTE)
line((cx0 + 0.030, cy0 - 0.029), (ox + 0.72, SY + 0.036))
PILL_H, PILL_GAP, PILL_FOOT = 0.15, 0.025, 0.05             # PILL_FOOT: white space under the lower pill
for k, text in enumerate(["Needs no clean set", "Needs no noise rate"]):
    cy = TY + PILL_FOOT + PILL_H / 2 + (1 - k) * (PILL_H + PILL_GAP)
    pw = sd.text_width(text, NOTE) + 0.14
    rounded(xs[0] + (TW - pw) / 2, cy - PILL_H / 2, pw, PILL_H, lw=0.7, r=PILL_H / 2 - 0.001)
    d.text(xs[0] + TW / 2, cy, text, size=NOTE)

# Stage 1: fit on the other folds, predict the held-out fold
folds = int(sf.recipe("filter_folds"))
STRIP_W, FG = 1.04, 0.022
BW = (STRIP_W - (folds - 1) * FG) / folds
sx = xs[1] + (TW - STRIP_W) / 2
by, bh = TY + 0.36, 0.19
for j in range(folds):
    held = j == folds - 1
    rounded(sx + j * (BW + FG), by, BW, bh, fill=OURS if held else GRID, edge=OURS if held else EDGE, lw=0.7,
            r=0.025)
rest_w = (folds - 1) * (BW + FG) - FG        # width of the folds that the model is fit on
card_x = sx + rest_w / 2
card_y = by + bh + 0.275
model_card(card_x, card_y)
# fit: a bracket over the other folds, with an arrow up into the card
brace_y = by + bh + 0.04
d.ax.plot([sx + 0.012, sx + 0.012, sx + rest_w - 0.012, sx + rest_w - 0.012],
          [brace_y - 0.025, brace_y, brace_y, brace_y - 0.025], color=EDGE, lw=0.8, zorder=5,
          solid_capstyle="round", solid_joinstyle="round")
d.arrow((card_x, brace_y), (card_x, card_y - 0.15), width=1.1, color=EDGE, head=0.65)
# predict: from the card into the held-out fold
held_x = sx + (folds - 1) * (BW + FG) + BW / 2
d.arrow((card_x + 0.235, card_y + 0.02), (held_x + 0.005, by + bh + 0.025), curve=0.38, width=1.6, color=EDGE,
        head=0.85)
d.text(xs[1] + TW / 2, NOTE_Y, "Out-of-fold,\neach in turn", size=NOTE)

# Stage 2: compare the given label with the out-of-fold prediction
cg, cp, ci = xs[2] + 0.25, xs[2] + 0.70, xs[2] + 1.04
head_y = TITLE_Y - 0.21
d.text(cg, head_y, "Given", size=NOTE)
d.text(cp, head_y, "Predicted", size=NOTE)
line((xs[2] + 0.08, head_y - 0.095), (xs[2] + TW - 0.08, head_y - 0.095), color=GRID, lw=1.0)
for k, (given, predicted) in enumerate([(True, True), (False, True), (True, False)]):
    y = head_y - 0.245 - 0.23 * k
    marker(cg, y, given, r=0.043)
    marker(cp, y, predicted, r=0.043)
    if given == predicted:
        check(ci, y)
    else:
        cross(ci, y, s=0.045, lw=1.8)

# Stage 3: drop every mismatch, here three wrong labels and one correct one
ox = scatter(3)
for x, y, _ in WRONG + [ACROSS]:
    cross(ox + x, SY + y)
d.text(xs[3] + TW / 2, NOTE_Y, "Correct label,\ndropped", size=NOTE)
line((ox + ACROSS[0], SY + ACROSS[1] - 0.06), (ox + ACROSS[0], NOTE_Y + 0.15))

# Stage 4: refit once on the kept set; the decision line spans only the height of the points
ox = scatter(4, dropped=False)
line((ox + 0.424, SY + 0.52), (ox + 0.651, SY + 0.03), color=OURS, lw=2.0)
model_card(xs[4] + TW / 2, LOW_Y + 0.025, ours=True)

# ---------------------------------------------------------------------------
# Row 2: measured outcomes
# ---------------------------------------------------------------------------
ROW2_H = ROW1_Y - 0.04
B_W = 3.36
CX = B_W + 0.05
TITLE2_Y = ROW2_H - 0.14
LEGEND_Y = ROW2_H - 0.345
AY, AH = 0.50, 0.69
for x0, w0, title in ((0.0, B_W, "(b) What it removes"), (CX, W - CX, "(c) What it gains and costs")):
    d.panel(x0, 0.0, w0, ROW2_H, fill=NEUTRAL)
    d.text(x0 + 0.09, TITLE2_Y, title, size=TITLE, ha="left", bg=NEUTRAL, case=None)

DATASETS = [("digits", "Digits"), ("breast", "Breast cancer")]
RATES = [("noise0", "Clean"), ("noise20", f"{sf.recipe('noise_rate_low'):.0f}%"),
         ("noise40", f"{sf.recipe('noise_rate_high'):.0f}%")]
SETTINGS = [(ds, rate) for ds, _ in DATASETS for rate, _ in RATES]
POS = np.array([0.0, 1.0, 2.0, 3.45, 4.45, 5.45])      # the same six settings, with a small gap between datasets
XLIM = (-0.55, 6.0)


def plot_axes(x, w):
    ax = d.fig.add_axes([x / W, AY / H, w / W, AH / H])
    ax.set_facecolor("white")
    ax.set_xlim(*XLIM)
    ax.set_xticks(POS, [name for _ in DATASETS for _, name in RATES])
    ax.tick_params(axis="x", length=0, pad=2.0, labelsize=NOTE)
    ax.tick_params(axis="y", length=2.0, pad=1.0, labelsize=NOTE)
    ax.grid(False)
    ax.grid(True, axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for g, (_, name) in enumerate(DATASETS):
        mid = POS[3 * g + 1]
        d.text(x + (mid - XLIM[0]) / (XLIM[1] - XLIM[0]) * w, 0.277, name, size=NOTE, bg=NEUTRAL)
    d.text(x + w / 2, 0.112, "Training label noise", size=LABEL, bg=NEUTRAL)
    return ax


def legend(ax, handles, labels, xc, **kw):
    """One legend row above the axes, at the same height in both panels (xc in inches)."""
    return ax.legend(handles, labels, loc="center", bbox_to_anchor=(xc / W, LEGEND_Y / H),
                     bbox_transform=d.fig.transFigure, ncol=len(labels), frameon=False, fontsize=NOTE,
                     handlelength=1.1, handletextpad=0.4, borderaxespad=0.0, borderpad=0.0, **kw)


# (b) share of the training set removed, split by whether the dropped sample was mislabeled
BX = 0.56
axb = plot_axes(BX, B_W - BX - 0.06)
axb.set_ylim(0, 55)
axb.set_yticks([0, 20, 40])
axb.set_ylabel("Training set\nremoved (%)", fontsize=LABEL, labelpad=1.5, linespacing=1.1)
BAR = 0.52
# The mislabeled share of the training set: a tick in two stubs, one on each side of the bar, so that it never
# covers the boundary between the two segments.
SHARE_TICK = dict(color=INK, lw=1.5, solid_capstyle="butt")
STUB_GAP, STUB = 0.05, 0.16                   # from the bar edge to the stub, and the stub's length (x units)
for x, (ds, rate) in zip(POS, SETTINGS):
    if rate == "noise0":                      # clean labels: every drop is a correctly labeled sample
        wrong, right = 0.0, sf.recipe(f"drop_fraction_{ds}_{rate}")
    else:
        wrong = sf.recipe(f"drop_share_mislabeled_{ds}_{rate}")
        right = sf.recipe(f"drop_share_correct_{ds}_{rate}")
        axb.bar(x, wrong, BAR, color=OURS, edgecolor=OURS, linewidth=0.8, zorder=2)
    axb.bar(x, right, BAR, bottom=wrong, color=LIGHT, edgecolor=OURS, linewidth=0.8, zorder=2)
    if rate != "noise0":
        share = sf.recipe(f"noisy_share_{ds}_{rate}")
        # dark, not gray: gray stands only for the clean-label reference of panel (c)
        for side in (-1, 1):
            inner = x + side * (BAR / 2 + STUB_GAP)
            axb.plot([inner, inner + side * STUB], [share, share], zorder=4, **SHARE_TICK)
legend(axb, [Patch(facecolor=OURS, edgecolor=OURS, linewidth=0.8),
             Patch(facecolor=LIGHT, edgecolor=OURS, linewidth=0.8),
             # the same two stubs: dash lengths are in line widths and fill the 1.1 em handle
             Line2D([], [], color=INK, lw=SHARE_TICK["lw"], linestyle=(0, (2.0, 1.5)), dash_capstyle="butt")],
       ["Mislabeled", "Correctly labeled", "Mislabeled in training set"], B_W / 2, columnspacing=0.8)

# (c) paired gain of ours over logistic regression (a true zero), with the clean-label reference on the same
# scale: its height above zero is the accuracy that noise costs logistic regression.
CAX = CX + 0.53                               # the y label clears its panel edge by as much as in (b)
axc = plot_axes(CAX, W - CAX - 0.07)
axc.set_ylim(-3, 18)
axc.set_yticks([0, 5, 10, 15])
axc.set_ylabel("Accuracy gain\n(points)", fontsize=LABEL, labelpad=1.5, linespacing=1.1)
CBAR = 0.60
JITTER = np.array([-0.22, -0.12, 0.10, 0.17, 0.24])             # fixed by seed, clear of the error bar
for x, (ds, rate) in zip(POS, SETTINGS):
    mean = sf.recipe(f"gain_vs_logreg_{ds}_{rate}")
    sdev = sf.recipe(f"std_gain_vs_logreg_{ds}_{rate}")
    seeds = [sf.recipe(f"gain_vs_logreg_{ds}_{rate}_seed{s}") for s in range(5)]
    axc.bar(x, mean, CBAR, color=OURS, linewidth=0, zorder=2)
    axc.errorbar(x, mean, yerr=sdev, fmt="none", ecolor=INK, elinewidth=0.8, capsize=2.0, capthick=0.8,
                 zorder=4)
    axc.plot(x + JITTER, seeds, ls="none", marker="o", ms=2.3, mfc="white", mec=INK, mew=0.5, zorder=5)
    if rate != "noise0":
        cost = sf.recipe(f"noise_cost_{ds}_{rate}")
        axc.plot([x - 0.45, x + 0.45], [cost, cost], color=REF, lw=2.0, solid_capstyle="butt", zorder=3)
# zero is logistic regression itself, so the line takes that method's color
axc.axhline(0, color=PARTNER, lw=1.1, zorder=3)
legend(axc, [Patch(facecolor=OURS, linewidth=0), Line2D([], [], color=PARTNER, lw=1.1),
             Line2D([], [], color=REF, lw=2.0)],
       ["Ours", "Logistic regression", "Clean-label reference"], (CX + W) / 2, columnspacing=0.9)

d.save("teaser")
