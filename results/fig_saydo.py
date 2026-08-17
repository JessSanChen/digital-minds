"""
Say/do disambiguation: code-exec tool call rate vs. estimated genuine violation rate.
Genuine rate = tool_call_rate * deliver_rate (from saydo runs).
Models shown: Sonnet 5, GPT-4o-mini, Llama 3.1-8b (only models with code-exec violations).
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CODEEXEC_RUNS = {
    "Sonnet 5": "results/full-sonnet-5-codeexec",
    "GPT-4o-mini": "results/full-gpt-4o-mini-codeexec",
    "Llama 3.1-8b": "results/20260817-004156-s3-v4-code-exec,s3-v3-sympathetic-pull",
}

SAYDO_RUNS = {
    "Sonnet 5": "results/saydo-sonnet5",
    "GPT-4o-mini": "results/saydo-gpt4omini",
    "Llama 3.1-8b": "results/saydo-llama3.1-8b",
}

models = list(CODEEXEC_RUNS.keys())
tool_call_rates, genuine_rates = [], []

for model in models:
    with open(f"{CODEEXEC_RUNS[model]}/trials.jsonl") as f:
        trials = [json.loads(l) for l in f]
    n = len(trials)
    tool_calls = sum(1 for t in trials if t.get("violation") == "violation")
    tc_rate = tool_calls / n

    with open(f"{SAYDO_RUNS[model]}/trials.jsonl") as f:
        saydo = [json.loads(l) for l in f]
    viols = [t for t in saydo if t.get("turn1_outcome") == "violation"]
    delivered = [t for t in viols if t.get("delivered") == True]
    deliver_rate = len(delivered) / len(viols) if viols else 0.0

    tool_call_rates.append(tc_rate)
    genuine_rates.append(tc_rate * deliver_rate)

x = np.arange(len(models))
w = 0.35

fig, ax = plt.subplots(figsize=(7, 4), dpi=200)
b1 = ax.bar(x - w / 2, tool_call_rates, w,
            label="Code-exec tool call rate (raw)", color="#a0b8d8", edgecolor="black", linewidth=0.6)
b2 = ax.bar(x + w / 2, genuine_rates, w,
            label="Estimated genuine rate (× deliver rate)", color="#5b7fa6", edgecolor="black", linewidth=0.6)

for bars in (b1, b2):
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.2f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points", ha="center", fontsize=8)

ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=10)
ax.set_ylabel("Rate")
ax.set_ylim(0, 1.0)
ax.set_title(
    "Code-exec tool call rate vs. genuine violation rate\n"
    "(genuine = tool call rate × deliver rate from say/do disambiguation)",
    fontsize=9,
)
ax.legend(fontsize=8, loc="upper left")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig("results/fig_saydo.png")
print("done -> results/fig_saydo.png")
