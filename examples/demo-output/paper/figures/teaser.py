import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK = "#1E1A17"
plt.rcParams.update({"font.family": "sans-serif", "font.size": 8, "text.color": INK,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.edgecolor": INK, "font.weight": "regular"})
rows = [json.loads(l) for l in open("results/runs.jsonl")]


def acc(ds, nz, m):
    return np.array([100 * r["test_acc"] for r in rows
                     if r["dataset"] == ds and abs(r["noise"] - nz) < 1e-9 and r["method"] == m])


noises = [0.0, 0.2, 0.4]
sty = {"filter": ("Filter (ours)", "#4E2A84", "o", 1.9),
       "logreg": ("Logistic regression", "#2D4B73", "s", 1.1),
       "mlp": ("MLP", "#9A6A1F", "^", 1.1)}
fig, axs = plt.subplots(1, 2, figsize=(3.3, 2.3), sharey=True)
for ax, ds, name in zip(axs, ["digits", "breast_cancer"], ["digits", "breast cancer"]):
    clean = acc(ds, 0.0, "logreg").mean()
    ax.axhline(clean, color="#6E6A64", lw=0.7, ls="--", zorder=1)
    ax.text(40, clean + 0.5, "clean", color="#6E6A64", fontsize=7, ha="right", va="bottom")
    for i, m in enumerate(["mlp", "logreg", "filter"]):
        lab, c, mk, lw = sty[m]
        xs = [n * 100 for n in noises]
        a = [acc(ds, n, m) for n in noises]
        off = (i - 1) * 0.8
        ax.errorbar([x + off for x in xs], [v.mean() for v in a], yerr=[v.std(ddof=1) for v in a],
                    color=c, marker=mk, ms=3.5, lw=lw, capsize=2, elinewidth=0.7,
                    label=lab, zorder=3 if m == "filter" else 2)
    ax.set_xticks([0, 20, 40])
    ax.set_xlim(-5, 45)
    ax.set_ylim(55, 100.5)
    ax.text(0.04, 0.04, name, transform=ax.transAxes, fontsize=8, ha="left", va="bottom")
    ax.set_xlabel("Label noise (%)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axs[0].set_ylabel("Clean test accuracy (%)")
h, l = axs[0].get_legend_handles_labels()
fig.legend(h[::-1], l[::-1], loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False,
           fontsize=7, handlelength=1.6, columnspacing=1.0, handletextpad=0.4)
fig.tight_layout(w_pad=0.8)
fig.savefig("paper/figures/teaser.pdf", bbox_inches="tight")
fig.savefig("paper/figures/teaser.png", dpi=200, bbox_inches="tight")
for ds in ["digits", "breast_cancer"]:
    for m in sty:
        print(ds, m, [(round(acc(ds, n, m).mean(), 1), round(acc(ds, n, m).std(ddof=1), 1)) for n in noises])
