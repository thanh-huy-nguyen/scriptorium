import json
import numpy as np
from matplotlib.colors import to_rgb
from matplotlib.patches import Patch
import scriptorium_fig as sf

sf.use()
fig, axes = sf.figure("column", aspect=0.75, ncols=2, sharey=True)

rows = [json.loads(l) for l in open("results/runs.jsonl")]


def seed_diffs(ds, noise, base):
    f = {r["seed"]: 100 * r["test_acc"] for r in rows
         if r["dataset"] == ds and abs(r["noise"] - noise) < 1e-9 and r["method"] == "filter"}
    b = {r["seed"]: 100 * r["test_acc"] for r in rows
         if r["dataset"] == ds and abs(r["noise"] - noise) < 1e-9 and r["method"] == base}
    return [f[s] - b[s] for s in sorted(f)]


OURS = sf.color("out-of-fold filter", ours=True)
LIGHT = tuple(0.55 * c + 0.45 for c in to_rgb(OURS))   # lighter tint of our colour

panels = [("Digits", "digits", "dg"), ("Breast cancer", "breast_cancer", "bc")]
# Every bar is the filter's gain, so both bars use our method's colour:
# solid = gain over logistic regression, light tint = gain over the MLP.
bases = [("logreg", "lr", "Logistic regression", OURS),
         ("mlp", "mlp", "MLP", LIGHT)]
noises = [0, 20, 40]
w = 0.38
rng = np.random.default_rng(0)

for ax, (label, ds, pre) in zip(axes, panels):
    ax.axhline(0, color=sf.color("untrained", reference=True), lw=1.0, zorder=1)
    for j, (bkey, short, lab, col) in enumerate(bases):
        xs = np.arange(3) + (j - 0.5) * w
        m = np.array([sf.recipe(f"diff_filter_{bkey}_{ds}_n{n}") for n in noises])
        lo = np.array([sf.recipe(f"{pre}{n}_{short}_diff_ci_low") for n in noises])
        hi = np.array([sf.recipe(f"{pre}{n}_{short}_diff_ci_high") for n in noises])
        ax.bar(xs, m, w * 0.92, color=col, edgecolor=OURS, linewidth=0.8, zorder=2)
        ax.errorbar(xs, m, yerr=[m - lo, hi - m], fmt="none", ecolor="black", elinewidth=0.9,
                    capsize=2.5, zorder=3)
        for x, n in zip(xs, noises):
            d = seed_diffs(ds, n / 100, bkey)
            ax.scatter(x + rng.uniform(-0.05, 0.05, len(d)), d, s=10, color="0.15",
                       edgecolor="white", linewidths=0.4, zorder=4)
    ax.set_xticks(range(3))
    ax.set_xticklabels([f"{n}" for n in noises])
    ax.set_xlabel("Noise rate (%)")
    ax.text(0.04, 0.96, label, transform=ax.transAxes, ha="left", va="top")
    ax.set_ylim(-3, 33)

axes[0].set_ylabel("Accuracy gain (points)")
handles = [Patch(facecolor=c, edgecolor=OURS, linewidth=0.8, label=l) for _, _, l, c in bases]
fig.legend(handles=handles, loc="outside upper center", ncol=2, frameon=False,
           title="Filter (ours) minus", alignment="center")
sf.save(fig, "paired_gain")
