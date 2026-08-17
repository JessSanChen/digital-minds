import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

RUNS = {
    "Sonnet 5": "results/full-sonnet-5-named",
    "Haiku 4.5": "results/full-haiku-4-5-named",
    "Opus 5": "results/full-opus-5-named",
    "GPT-4o": "results/full-gpt-4o-named",
    "GPT-4o-mini": "results/full-gpt-4o-mini-named",
    "Llama 3.1-8b\n(private only)": "results/named-llama3.1-8b",
}

labels, rates, cis = [], [], []
for label, path in RUNS.items():
    with open(f"{path}/trials.jsonl") as f:
        trials = [json.loads(l) for l in f]
    v = sum(1 for t in trials if t.get("violation") == "violation")
    n = len(trials)
    rate = v / n
    # Wilson score interval
    z = 1.96
    center = (v + z**2 / 2) / (n + z**2)
    margin = z * np.sqrt(v * (n - v) / n + z**2 / 4) / (n + z**2)
    labels.append(label)
    rates.append(rate)
    cis.append(margin)

colors = ["#5b7fa6"] * 5 + ["#c98a8a"]
x = np.arange(len(labels))

fig, ax = plt.subplots(figsize=(7.5, 4), dpi=200)
bars = ax.bar(x, rates, color=colors, edgecolor="black", linewidth=0.6,
              yerr=cis, capsize=4, error_kw={"linewidth": 1.2, "ecolor": "#444"})

for bar, rate in zip(bars, rates):
    h = bar.get_height()
    ax.annotate(f"{rate:.2f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                xytext=(0, 5), textcoords="offset points", ha="center", fontsize=8)

ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("Violation rate (named-tool DV)")
ax.set_ylim(0, 1.0)
ax.set_title(
    "Named-tool violation rate by model\n"
    "(Claude/GPT: 192 trials, 4 audiences; Llama: 24 trials, private only)",
    fontsize=9,
)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig("results/fig_named_tool.png")
print("done -> results/fig_named_tool.png")
