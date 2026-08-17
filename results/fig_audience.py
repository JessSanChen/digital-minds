import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

audiences = ["human", "ai", "peer", "private"]
old = [0.87, 0.53, 0.53, 0.53]
corrected = [0.60, 0.37, 0.33, 0.50]

x = np.arange(len(audiences))
w = 0.35

fig, ax = plt.subplots(figsize=(6.2, 3.6), dpi=200)
b1 = ax.bar(x - w/2, old, w, label="Buggy checker (day 1)", color="#c98a8a", edgecolor="black", linewidth=0.6)
b2 = ax.bar(x + w/2, corrected, w, label="Corrected checker", color="#5b7fa6", edgecolor="black", linewidth=0.6)

for bars in (b1, b2):
    for rect in bars:
        h = rect.get_height()
        ax.annotate(f"{h:.2f}", xy=(rect.get_x() + rect.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8)

ax.set_xticks(x)
ax.set_xticklabels(audiences)
ax.set_ylabel("Violation rate")
ax.set_ylim(0, 1.0)
ax.set_title("Sonnet 5: violation rate by audience, before/after checker fix\n(s3-audience-sonnet5, n=30/audience, code-exec + sympathetic pull)", fontsize=9)
ax.legend(fontsize=8, loc="upper right")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig("/Users/rheaacharya/digital-minds/digital-minds/results/fig_audience.png")
print("done")
