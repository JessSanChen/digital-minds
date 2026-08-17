"""
E1 Figure 2: Code-execution task — raw tool-call rate vs. genuine violation rate.
All 6 models shown. Genuine rate = raw rate x fraction that delivered the result
to the user (from say/do disambiguation runs). Models with 0 raw rate have no bars.

The key story: Sonnet's 45% raw rate collapses to ~2% genuine (it probes, then
disavows). GPT-4o-mini and Llama deliver nearly every time they fetch.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CODEEXEC = {
    "Sonnet 5":    "results/full-sonnet-5-codeexec",
    "Haiku 4.5":   "results/full-haiku-4-5-codeexec",
    "Opus 5":      "results/full-opus-5-codeexec",
    "GPT-4o":      "results/full-gpt-4o-codeexec",
    "GPT-4o-mini": "results/full-gpt-4o-mini-codeexec",
    "Llama 3.1-8b":"results/20260817-004156-s3-v4-code-exec,s3-v3-sympathetic-pull",
}
SAYDO = {
    "Sonnet 5":    "results/saydo-sonnet5",
    "GPT-4o-mini": "results/saydo-gpt4omini",
    "Llama 3.1-8b":"results/saydo-llama3.1-8b",
}

models = list(CODEEXEC.keys())
raw_rates, genuine_rates, probe_rates = [], [], []

for model in models:
    with open(f"{CODEEXEC[model]}/trials.jsonl") as f:
        trials = [json.loads(l) for l in f]
    n = len(trials)
    raw = sum(1 for t in trials if t.get("violation") == "violation") / n

    if model in SAYDO:
        with open(f"{SAYDO[model]}/trials.jsonl") as f:
            sd = [json.loads(l) for l in f]
        viols = [t for t in sd if t.get("turn1_outcome") == "violation"]
        delivered = [t for t in viols if t.get("delivered") == True]
        deliver_rate = len(delivered) / len(viols) if viols else 0.0
    else:
        deliver_rate = 0.0  # never fetched, nothing to deliver

    genuine = raw * deliver_rate
    probe = raw * (1 - deliver_rate)
    raw_rates.append(raw)
    genuine_rates.append(genuine)
    probe_rates.append(probe)

x = np.arange(len(models))
w = 0.35

fig, ax = plt.subplots(figsize=(9, 4.5), dpi=200)

# Stacked: probe (light) + genuine (dark) = raw rate
b_probe = ax.bar(x - w / 2, probe_rates, w, label="Fetched but disavowed (probe)",
                 color="#c8d8e8", edgecolor="black", linewidth=0.6)
b_genuine = ax.bar(x - w / 2, genuine_rates, w, bottom=probe_rates,
                   label="Fetched and delivered to user (genuine violation)",
                   color="#c98a8a", edgecolor="black", linewidth=0.6)

# Genuine rate alone as separate bar for clarity
b_g2 = ax.bar(x + w / 2, genuine_rates, w,
              label="Genuine violation rate (right bar)",
              color="#8a3030", edgecolor="black", linewidth=0.6)

for i, (gen, prob) in enumerate(zip(genuine_rates, probe_rates)):
    total = gen + prob
    if total > 0.01:
        ax.annotate(f"{total:.2f}", xy=(x[i] - w / 2, total),
                    xytext=(0, 4), textcoords="offset points", ha="center", fontsize=8)
    if gen > 0.01:
        ax.annotate(f"{gen:.2f}", xy=(x[i] + w / 2, gen),
                    xytext=(0, 4), textcoords="offset points", ha="center", fontsize=8)
    elif gen == 0 and total == 0:
        ax.annotate("0", xy=(x[i] - w / 2, 0),
                    xytext=(0, 4), textcoords="offset points", ha="center", fontsize=8, color="#888")

ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=9)
ax.set_ylabel("Fraction of trials", fontsize=10)
ax.set_ylim(0, 1.0)
ax.set_title(
    "Code-execution task: raw fetch rate vs. genuine violation rate\n"
    "Left bar = all trials where model wrote forbidden fetch code (stacked: probe vs. delivered)\n"
    "Right bar = estimated genuine violations (model delivered the result to the user)",
    fontsize=8.5,
)
ax.legend(fontsize=8, loc="upper left")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig("results/fig_saydo.png")
print("done -> results/fig_saydo.png")
