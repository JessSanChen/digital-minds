"""
E1 Figure 1: Policy violation rate on the direct-call task (named http_get tool).
All 6 models. Calling the tool IS the act — no ambiguity about intent.
Note: Llama data is private-audience only (n=24); all others n=192, 4 audiences.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RUNS = {
    "Sonnet 5": "results/full-sonnet-5-named",
    "Haiku 4.5": "results/full-haiku-4-5-named",
    "Opus 5": "results/full-opus-5-named",
    "GPT-4o": "results/full-gpt-4o-named",
    "GPT-4o-mini": "results/full-gpt-4o-mini-named",
    "Llama\n3.1-8b*": "results/named-llama3.1-8b",
}
COLORS = ["#5b7fa6"] * 5 + ["#c98a8a"]


def wilson_ci(v, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    rate = v / n
    center = (v + z**2 / 2) / (n + z**2)
    margin = z * np.sqrt(v * (n - v) / n + z**2 / 4) / (n + z**2)
    return rate, margin


labels, rates, cis = [], [], []
for label, path in RUNS.items():
    with open(f"{path}/trials.jsonl") as f:
        trials = [json.loads(l) for l in f]
    v = sum(1 for t in trials if t.get("violation") == "violation")
    n = len(trials)
    rate, ci = wilson_ci(v, n)
    labels.append(label)
    rates.append(rate)
    cis.append(ci)

x = np.arange(len(labels))
fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200)
bars = ax.bar(x, rates, color=COLORS, edgecolor="black", linewidth=0.6,
              yerr=cis, capsize=4, error_kw={"linewidth": 1.2, "ecolor": "#444"})

for bar, rate in zip(bars, rates):
    h = bar.get_height()
    ax.annotate(f"{rate:.2f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                xytext=(0, 5), textcoords="offset points", ha="center", fontsize=9)

ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("Fraction of trials with policy violation", fontsize=10)
ax.set_ylim(0, 1.05)
ax.set_title(
    "Policy violation rate — direct-call task\n"
    "(model given http_get tool; calling a forbidden URL = violation; 95% CI)\n"
    "* Llama: private audience only (n=24); all others n=192 across 4 audience conditions",
    fontsize=8.5,
)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig("results/fig_named_tool.png")
print("done -> results/fig_named_tool.png")
