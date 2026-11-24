import json
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle
import scriptorium_diagram as sd

import scriptorium_fig as sf
from matplotlib.colors import to_rgb


def mix(c, t):
    return tuple(t + (1 - t) * v for v in to_rgb(c))


PUR = sf.color("filter", ours=True)
LIGHT, LAV = mix(PUR, 0.6), mix(PUR, 0.9)
RED, BLUE, ORANGE = sf.color("flip", partner=True), sf.color("logreg"), sf.color("mlp")
GRAY, INK, EDGE = "#D9D9D9", "#2B2B2B", "#999999"

# ---- data from the repository's raw runs
rows = [json.loads(l) for l in open("results/runs.jsonl")]
acc = {}
for r in rows:
    acc.setdefault((r["dataset"], round(r["noise"] * 100), r["method"]), []).append(100 * r["test_acc"])
prec = [100 * r["n_dropped_noisy"] / r["n_dropped"] for r in rows
        if r["method"] == "filter" and r["dataset"] == "digits" and abs(r["noise"] - 0.4) < 1e-9
        and r["n_dropped"] > 0]
PREC = float(np.mean(prec))

try:
    from sklearn.datasets import load_digits
    _D = load_digits()
    IMAGES, TARGET, REAL = _D.images, _D.target, True
except ImportError:
    # sklearn is not installed here: draw schematic 5x7 pixel digits (the caption says so)
    G = ["01110 10001 10011 10101 11001 10001 01110", "00100 01100 00100 00100 00100 00100 01110",
         "01110 10001 00001 00110 01000 10000 11111", "11110 00001 00001 01110 00001 00001 11110",
         "00010 00110 01010 10010 11111 00010 00010", "11111 10000 11110 00001 00001 10001 01110",
         "00110 01000 10000 11110 10001 10001 01110", "11111 00001 00010 00100 01000 01000 01000",
         "01110 10001 10001 01110 10001 10001 01110", "01110 10001 10001 01111 00001 00010 01100"]
    IMAGES = np.array([[[int(c) for c in row] for row in g.split()] for g in G], dtype=float)
    TARGET, REAL = np.arange(10), False

d = sd.canvas("full", height=2.0)
ax = d.ax


def rbox(x, y, w, h, fc, ec, lw=0.8, r=0.02, z=3):
    ax.add_patch(FancyBboxPatch((x + r, y + r), w - 2 * r, h - 2 * r,
                                boxstyle=f"round,pad={r},rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=z))


def cross(cx, cy, s=0.035, z=8):
    for a, b in (((-s, -s), (s, s)), ((-s, s), (s, -s))):
        ax.plot([cx + a[0], cx + b[0]], [cy + a[1], cy + b[1]], color=RED, lw=1.4,
                zorder=z, solid_capstyle="round")


def thumb(x, y, w, h, idx):
    # real 8x8 sklearn digit image, upscaled
    ax.imshow(IMAGES[idx % len(IMAGES)], cmap="gray_r", extent=(x, x + w, y, y + h), zorder=5,
              interpolation="nearest", aspect="auto")
    ax.add_patch(Rectangle((x, y), w, h, fc="none", ec=EDGE, lw=0.4, zorder=6))


def tag(x, y, w, h, val, flipped):
    rbox(x, y, w, h, "white", RED if flipped else EDGE, lw=1.1 if flipped else 0.4, r=0.01)
    ax.text(x + w / 2, y + h / 2 - 0.003, str(val), fontsize=8, ha="center", va="center",
            color=INK, zorder=6)


# ---- panels
X1, W1 = 0.08, 1.45
X2, W2 = 1.75, 1.85
X3, W3 = 3.82, 2.85
d.panel(X1, 0.08, W1, 1.84, "Noisy labels", step=1, k=0)
d.panel(X2, 0.08, W2, 1.84, "Drop disagreements", step=2, k=0)
d.panel(X3, 0.08, W3, 1.84, "Refit", step=3, k=0)
d.arrow((X1 + W1 + 0.01, 1.0), (X2 - 0.01, 1.0), color=LIGHT, width=3.0)
d.arrow((X2 + W2 + 0.01, 1.0), (X3 - 0.01, 1.0), color=LIGHT, width=3.0)

# ---- panel 1: digit thumbnails with class tags
flipped = {2, 7, 10, 13, 19, 22}
cw, ch = 0.225, 0.29
gx = X1 + (W1 - 6 * cw) / 2
top = 1.63
for i in range(24):
    r, c = divmod(i, 6)
    x = gx + c * cw
    y = top - (r + 1) * ch
    idx = i * 13
    t = int(TARGET[idx % len(IMAGES)])
    fl = i in flipped
    thumb(x + 0.02, y + 0.12, 0.185, 0.17, idx)
    tag(x + 0.04, y + 0.01, 0.145, 0.1, (t + 3) % 10 if fl else t, fl)
rbox(X1 + 0.28, 0.29, 0.145, 0.1, "white", RED, lw=1.1, r=0.01)
d.text(X1 + 0.47, 0.34, "flipped tag", size=7.5, ha="left")
d.text(X1 + W1 / 2, 0.16, "~20-40% flipped", size=7.5)

# ---- panel 2: out-of-fold prediction
fw, fg = 0.28, 0.05
fx0 = X2 + 0.125
fy, fh = 1.5, 0.17
for k in range(5):
    x = fx0 + k * (fw + fg)
    last = k == 4
    rbox(x, fy, fw, fh, LAV if last else GRAY, PUR if last else EDGE, lw=1.2 if last else 0.5, r=0.02)
    d.text(x + fw / 2, fy + fh / 2, str(k + 1), size=7, color=INK)
# bracket under folds 1-4 -> network card
bl, br, by_ = fx0, fx0 + 4 * fw + 3 * fg, fy - 0.06
bc = (bl + br) / 2
ax.plot([bl, bl, br, br], [by_ + 0.03, by_, by_, by_ + 0.03], color=PUR, lw=1.0, zorder=4)
d.arrow((bc, by_ - 0.005), (bc, 1.3), color=PUR, width=1.4)
d.icon("network", bc, 1.14, 0.3, color=PUR)
d.text(bc, 0.88, "fit on 4", size=7.5)
# held-out fold 5 container
cx0, cx1, cy0, cy1 = X2 + 1.08, X2 + 1.80, 0.78, 1.26
rbox(cx0, cy0, cx1 - cx0, cy1 - cy0, LAV, PUR, lw=1.0, r=0.03, z=2)
f5 = fx0 + 4 * (fw + fg) + fw / 2
d.arrow((f5, fy - 0.01), (f5, cy1 + 0.01), color=PUR, width=1.4)
d.arrow((bc + 0.2, 1.14), (cx0 - 0.01, 1.14), color=PUR, width=1.4)
for j, (idx, fl) in enumerate([(5, False), (6, True), (8, False)]):
    x = cx0 + 0.05 + j * 0.225
    t = int(TARGET[idx % len(IMAGES)])
    thumb(x, 1.04, 0.17, 0.16, idx)
    tag(x + 0.015, 0.93, 0.14, 0.09, (t + 3) % 10 if fl else t, fl)
    if fl:
        cross(x + 0.085, 1.12, s=0.05, z=9)
d.text(cx0 + 0.03, 0.845, "predict 5", size=7.5, ha="left")
# stacked precision bar
bx, bw, bb, bh = X2 + 0.1, W2 - 0.2, 0.32, 0.18
cxl = cx1 - 0.08
ax.plot([cxl, cxl], [cy0, bb + bh], color=PUR, lw=0.8, ls=(0, (2, 2)), zorder=3)
d.text(bx, 0.68, "crossed = dropped", size=7.5, ha="left", color=INK)
wf = bw * PREC / 100
ax.add_patch(Rectangle((bx + wf, bb), bw - wf, bh, fc=LAV, ec=PUR, lw=1.0, zorder=3))
ax.add_patch(Rectangle((bx, bb), wf, bh, fc=PUR, ec=PUR, lw=1.0, zorder=4))
d.text(bx + wf / 2, bb + bh / 2, f"flipped {PREC:.0f}%", size=7.5, color="white", bg=PUR)
d.text(bx + bw, bb - 0.09, f"clean {100 - PREC:.0f}%", size=7.5, color=PUR, ha="right")
d.text(bx, 0.55, "all dropped, digits, 40% noise", size=7, ha="left")
ax.set_xlim(0, d.W)
ax.set_ylim(0, d.H)

# ---- panel 3: grouped bars
methods = [("logreg", "Logistic regression", BLUE), ("mlp", "MLP", ORANGE), ("filter", "Filter (ours)", PUR)]
lx = X3 + 0.1
for (name, lab, col), wl in zip(methods, [0.98, 0.3, 0.72]):
    ax.add_patch(Rectangle((lx, 1.57), 0.09, 0.09, fc=col, ec="none", zorder=4))
    d.text(lx + 0.12, 1.615, lab, size=7.5, ha="left")
    lx += 0.12 + wl + 0.02
fig = d.fig
aw, ah = 1.05, 0.78
for g, (ds, title) in enumerate([("digits", "Digits"), ("breast_cancer", "Breast cancer")]):
    gx0 = X3 + 0.38 + g * 1.32
    ax0 = fig.add_axes([gx0 / d.W, 0.45 / d.H, aw / d.W, ah / d.H])
    ax0.set_facecolor("none")
    rng = np.random.default_rng(0)
    for m, (key, lab, col) in enumerate(methods):
        for n, noise in enumerate([0, 20, 40]):
            v = np.array(acc[(ds, noise, key)])
            x = n + (m - 1) * 0.28
            ax0.bar(x, v.mean(), 0.26, color=col, ec="none", zorder=2)
            ax0.errorbar(x, v.mean(), yerr=v.std(ddof=1), color=INK, lw=0.7, capsize=1.2, capthick=0.7, zorder=3)
            ax0.scatter(x + rng.uniform(-0.06, 0.06, len(v)), v, s=7, color="white", ec=INK, lw=0.4, zorder=4)
    ref = np.mean(acc[(ds, 0, "filter")])
    ax0.axhline(ref, color=PUR, lw=0.6, ls=(0, (3, 2)), zorder=1)
    ax0.set_ylim(50, 100)
    ax0.set_xlim(-0.55, 2.55)
    ax0.set_xticks([0, 1, 2], ["0", "20", "40"], fontsize=7.5)
    ax0.set_yticks([50, 75, 100])
    ax0.tick_params(length=2, width=0.5, pad=1.5, labelsize=7.5)
    ax0.set_title(title, fontsize=8, pad=3)
    if g == 0:
        ax0.set_ylabel("test accuracy (%)", fontsize=7.5, labelpad=1)
    for s in ("top", "right"):
        ax0.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax0.spines[s].set_linewidth(0.5)
    ax0.grid(axis="y", color="#E6E8EB", lw=0.4, zorder=0)
d.text(X3 + W3 / 2 + 0.1, 0.17, "label noise (%)", size=7.5)

d.save("teaser")
