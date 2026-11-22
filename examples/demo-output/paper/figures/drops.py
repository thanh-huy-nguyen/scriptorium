import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK = "#1E1A17"
plt.rcParams.update({"font.size": 8, "font.family": "sans-serif", "text.color": INK,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.edgecolor": INK})
R = [json.loads(l) for l in open("results/runs.jsonl")]
R = [r for r in R if r["method"] == "filter"]


def rows(d, n):
    return [r for r in R if r["dataset"] == d and abs(r["noise"] - n) < 1e-9]


xs, fl, cl, sd, tk, pr, stats = [], [], [], [], [], [], []
x = 0
for d in ["digits", "breast_cancer"]:
    for n in [0.0, 0.2, 0.4]:
        rs = rows(d, n)
        assert len(rs) == 5
        t = np.array([100 * r["n_dropped"] / r["n_train"] for r in rs])
        f = np.array([100 * r["n_dropped_noisy"] / r["n_train"] for r in rs])
        nz = np.array([100 * r["n_noisy"] / r["n_train"] for r in rs])
        p = [100 * r["n_dropped_noisy"] / r["n_dropped"] for r in rs if r["n_dropped"] > 0]
        xs.append(x)
        fl.append(f.mean())
        cl.append(t.mean() - f.mean())
        sd.append(t.std(ddof=1))
        tk.append(nz.mean())
        pr.append(np.mean(p) if n > 0 else None)
        stats.append((d, n, round(t.mean(), 2), round(f.mean(), 2), round(nz.mean(), 2), pr[-1],
                      round(t.std(ddof=1), 2)))
        x += 1
    x += 0.6

fig, ax = plt.subplots(figsize=(3.3, 2.4))
ax.bar(xs, fl, 0.7, color="#4E2A84", label="dropped, flipped")
ax.bar(xs, cl, 0.7, bottom=fl, color="#D2CFCA", label="dropped, clean")
ax.errorbar(xs, np.array(fl) + cl, yerr=sd, fmt="none", ecolor=INK, capsize=2, lw=0.8)
for xi, t in zip(xs, tk):
    if t > 0:
        ax.plot([xi - 0.42, xi + 0.42], [t, t], color="k", lw=1.6, solid_capstyle="butt")
ax.plot([], [], color="k", lw=1.6, label="flipped labels")
for xi, f, c, s, p in zip(xs, fl, cl, sd, pr):
    if p is not None:
        ax.text(xi, f + c + s + 0.8, f"{p:.0f}%", ha="center", va="bottom", fontsize=7.5)
ax.set_xticks(xs)
ax.set_xticklabels(["0", "20", "40"] * 2)
ax.set_xlabel("nominal label noise (%)")
ax.set_ylabel("share of training set (%)")
for lab, a, b in [("digits", xs[0], xs[2]), ("breast cancer", xs[3], xs[5])]:
    ax.text((a + b) / 2, -0.12, lab, transform=ax.get_xaxis_transform(), ha="center", va="top")
ax.xaxis.labelpad = 15
ax.set_ylim(0, 62)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False, fontsize=7,
          handlelength=1.2, columnspacing=1)
fig.savefig("paper/figures/drops.pdf", bbox_inches="tight")
fig.savefig("paper/figures/drops.png", dpi=200, bbox_inches="tight")
for s in stats:
    print(s)
