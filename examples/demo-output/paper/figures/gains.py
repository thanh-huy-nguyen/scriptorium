import json
import numpy as np
import scriptorium_fig as sf

sf.use()
fig, axes = sf.figure("column", aspect=0.62, ncols=2, sharey=True)

rows = [json.loads(l) for l in open("results/runs.jsonl")]


def seed_diffs(ds, noise, base):
    f = {r["seed"]: 100 * r["test_acc"] for r in rows
         if r["dataset"] == ds and abs(r["noise"] - noise) < 1e-9 and r["method"] == "filter"}
    b = {r["seed"]: 100 * r["test_acc"] for r in rows
         if r["dataset"] == ds and abs(r["noise"] - noise) < 1e-9 and r["method"] == base}
    return [f[s] - b[s] for s in sorted(f)]


panels = [("Digits", "digits", "dg"), ("Breast cancer", "breast_cancer", "bc")]
# Baseline hues are the ones Figure 1 (teaser.py) uses; purple is reserved for our method and kept out of this plot.
BLUE, ORANGE = "#5B84B1", "#E0A25A"
bases = [("logreg", "lr", "vs. logistic regression", BLUE),
         ("mlp", "mlp", "vs. MLP", ORANGE)]
noises = [0, 20, 40]
w = 0.36
rng = np.random.default_rng(0)
handles = {}

for ax, (label, ds, pre) in zip(axes, panels):
    ax.axhline(0, color=sf.color("untrained", reference=True), lw=1.0, zorder=1)
    for j, (bkey, short, lab, cname) in enumerate(bases):
        col = cname
        xs = np.arange(3) + (j - 0.5) * w
        means = [sf.recipe(f"diff_filter_{bkey}_{ds}_n{n}") for n in noises]
        lo = np.array([sf.recipe(f"{pre}{n}_{short}_diff_ci_low") for n in noises])
        hi = np.array([sf.recipe(f"{pre}{n}_{short}_diff_ci_high") for n in noises])
        m = np.array(means)
        b = ax.bar(xs, m, w * 0.92, color=col, zorder=2, label=lab)
        handles[lab] = b
        ax.errorbar(xs, m, yerr=[m - lo, hi - m], fmt="none", ecolor="black", elinewidth=0.8,
                    capsize=2, zorder=3)
        for x, n in zip(xs, noises):
            d = seed_diffs(ds, n / 100, bkey)
            ax.scatter(x + rng.uniform(-0.04, 0.04, len(d)), d, s=9, color="0.15",
                       edgecolor="white", linewidths=0.4, zorder=4)
    ax.set_xticks(range(3))
    ax.set_xticklabels([f"{n}" for n in noises])
    ax.set_xlabel("Noise rate (%)")
    ax.text(0.04, 0.95, label, transform=ax.transAxes, ha="left", va="top")
    ax.set_ylim(-3, 33)

axes[0].set_ylabel("Accuracy gain of filter (points)")
fig.legend(handles=list(handles.values()), labels=list(handles.keys()), loc="outside upper center",
           ncol=2, frameon=False, title="Filter (ours) compared with", alignment="center")
sf.save(fig, "gains")
