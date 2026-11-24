import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import scriptorium_fig as sf

R = sf.recipe
PURPLE, LIGHT, LAV = "#4E2A84", "#B6ACD1", "#F1EEF7"
C_LR = "#2E8B8B"  # muted teal
C_MLP = sf.color("multilayer perceptron")
GRAY = "#8a8a8a"
C_PREC, C_REC = "#4F6D8F", "#A9BCD0"  # muted slate blue: diagnostic bars, not a method

sf.use()
fig, _ = sf.figure("full", aspect=0.42)
_.remove()
gs = fig.add_gridspec(1, 3, width_ratios=[26, 38, 36], wspace=0.35,
                      left=0.075, right=0.995, top=0.72, bottom=0.2)
gl = gs[0, 1].subgridspec(1, 2, wspace=0.12)
gr = gs[0, 2].subgridspec(1, 2, wspace=1.0)

# ---- (a) precision and recall
ax = fig.add_subplot(gs[0, 0])
cells = [("digits", "digits", "20"), ("digits", "digits", "40"),
         ("bc", "breast cancer", "20"), ("bc", "breast cancer", "40")]
x = np.arange(4)
w = 0.38
prec = [R(f"prec_{d}_n{n}") for d, _, n in cells]
sd = [R(f"sd_prec_{d}_n{n}") for d, _, n in cells]
rec = [R(f"rec_{d}_n{n}") for d, _, n in cells]
ax.bar(x - w / 2, prec, w, yerr=sd, color=C_PREC, capsize=2, error_kw={"lw": 0.8}, label="precision: drops that are flips")
ax.bar(x + w / 2, rec, w, color=C_REC, label="recall: flips that are dropped")
ax.axhline(50, color=GRAY, ls="--", lw=0.8, zorder=0)
ax.set_xlim(-0.6, 4.2)
ax.text(3.45, 51, "50%", color="#555555", ha="left", va="bottom", fontsize=6.5)
ax.set_xticks(x)
ax.set_xticklabels([f"{n}%" for _, nm, n in cells])
ax.set_ylim(0, 100)
ax.set_ylabel("Share (%)")
for xc, nm in [(0.5, "digits"), (2.5, "breast cancer")]:
    ax.annotate(nm, (xc, 0), xycoords=("data", "axes fraction"), xytext=(0, -17),
                textcoords="offset points", ha="center", va="top")
ax.legend(loc="lower left", bbox_to_anchor=(-0.1, 1.02), ncol=1, frameon=False, borderaxespad=0,
          handlelength=1.2, labelspacing=0.3)
fig.text(0.0, 0.97, "(a)", va="top")

# ---- (b) accuracy lines
noise = [0, 20, 40]
axs = []
for j, (d, name) in enumerate([("digits", "digits"), ("bc", "breast cancer")]):
    a = fig.add_subplot(gl[0, j])
    axs.append(a)

    def get(m, k):
        return np.array([R(f"{k}_{d}_n{n}_{m}") for n in noise])
    lr, mlp = get("logreg", "acc"), get("mlp", "acc")
    for m, col, lw, lab in [("logreg", C_LR, 1.2, "logistic regression"), ("mlp", C_MLP, 1.2, "MLP"),
                            ("filter", PURPLE, 2.0, "out-of-fold filter")]:
        mu, s = get(m, "acc"), get(m, "sd")
        a.plot(noise, mu, "-o", color=col, lw=lw, ms=3, label=lab, zorder=3)
        a.fill_between(noise, mu - s, mu + s, color=col, alpha=0.10, lw=0, zorder=2)
    clean = lr[0]
    flt = get("filter", "acc")[2]
    a.axhline(clean, color=GRAY, ls="--", lw=0.8, zorder=1)
    a.add_patch(Rectangle((42, lr[2]), 3.2, clean - lr[2], fc=LAV, ec=LIGHT, lw=0.8, zorder=1))
    a.plot([42, 45.2], [flt, flt], color=PURPLE, lw=2.0, zorder=4, solid_capstyle="butt")
    rec_pct = R(f"recovery_{d}_n40")
    a.text(43.6, lr[2] - 0.8, f"{rec_pct:.0f}% of\nmean gap", ha="center", va="top",
           fontsize=6.5, color=PURPLE, linespacing=1.0)
    a.set_xticks(noise)
    a.set_xticklabels([f"{n}%" for n in noise])
    a.set_xlim(-3, 52)
    a.set_xlabel("Label noise rate")
    a.set_title(name, pad=3)
    a.set_ylim(min(mlp[2], lr[2]) - 9, 100)
    if j == 0:
        a.set_ylabel("Test accuracy (%)")
    else:
        a.set_yticklabels([])
h, l = axs[0].get_legend_handles_labels()
cx = 0.5 * (axs[0].get_position().x0 + axs[1].get_position().x1)
fig.legend(h, l, loc="lower left", bbox_to_anchor=(axs[0].get_position().x0 - 0.04, 0.775), ncol=1, frameon=False,
           handlelength=1.4, labelspacing=0.3, borderaxespad=0)
fig.text(axs[0].get_position().x0 - 0.05, 0.97, "(b)", va="top")

# ---- (c) clean cost
ac = fig.add_subplot(gr[0, 0])
bd = fig.add_subplot(gr[0, 1])
g = np.array([R("gain_digits_n0_vs_logreg"), R("gain_bc_n0_vs_logreg")])
lo = np.array([R("dg0_logreg_diff_ci_low"), R("bc0_logreg_diff_ci_low")])
hi = np.array([R("dg0_logreg_diff_ci_high"), R("bc0_logreg_diff_ci_high")])
ac.bar([0, 1], g, 0.6, color=PURPLE, yerr=[g - lo, hi - g], capsize=2, error_kw={"lw": 0.8})
ac.axhline(0, color=GRAY, lw=0.8)
ac.set_xticks([0, 1])
ac.set_xticklabels(["digits", "breast\ncancer"])
ac.set_ylim(-1.2, 0.4)
ac.set_ylabel("points")
ac.set_title("accuracy\nchange", pad=3)
drop = [R("dropped_frac_digits_n0"), R("dropped_frac_bc_n0")]
bd.bar([0, 1], drop, 0.6, color=LIGHT)
bd.set_xticks([0, 1])
bd.set_xticklabels(["digits", "breast\ncancer"])
bd.set_ylim(0, 8)
bd.set_ylabel("% dropped")
bd.set_title("samples\ndropped", pad=3)
fig.text(ac.get_position().x0 - 0.06, 0.88, "(c)", va="top")

sf.save(fig, "teaser")
