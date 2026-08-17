import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

group_sizes = [1, 3, 5]
framings = {
    "neutral (presence only)": [0.47, 0.47, 0.27],
    "confessional": [0.13, 0.07, 0.03],
    "normative": [0.03, 0.03, 0.13],
    "reframe": [0.00, 0.03, 0.03],
    "refuser": [0.10, 0.10, 0.00],
}
baseline = 0.37

fig, ax = plt.subplots(figsize=(6.4, 3.8), dpi=200)
colors = ["#8c8c8c", "#c98a8a", "#5b7fa6", "#7fa65b", "#a65ba0"]
markers = ["o", "s", "^", "D", "v"]

for (label, vals), c, m in zip(framings.items(), colors, markers):
    ax.plot(group_sizes, vals, marker=m, color=c, label=label, linewidth=1.8, markersize=6)

ax.axhline(baseline, color="black", linestyle="--", linewidth=1, label="no-peer baseline (0.37)")

ax.set_xticks(group_sizes)
ax.set_xlabel("Number of peers")
ax.set_ylabel("Violation rate")
ax.set_ylim(-0.02, 0.75)
ax.set_title("Peer testimony suppresses violation for every content framing\n(conf-grid, corrected checker, Sonnet 5, n=30/cell)", fontsize=9)
ax.legend(fontsize=7.5, loc="upper right", ncol=1)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig("/Users/rheaacharya/digital-minds/digital-minds/results/fig_conformity.png")
print("done")
