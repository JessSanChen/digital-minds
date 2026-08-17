"""
Violation rate by audience condition for models that actually violate.
Named-tool DV for GPT-4o-mini (only model with cross-audience named-tool data and violations).
Code-exec DV for Llama 3.1-8b and GPT-4o-mini (cross-audience).
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import defaultdict

AUDIENCES = ["human", "ai", "peer", "private"]
AUDIENCE_LABELS = ["Human", "AI", "Peer", "Private"]


def audience_rates(path):
    with open(f"{path}/trials.jsonl") as f:
        trials = [json.loads(l) for l in f]
    by_aud = defaultdict(list)
    for t in trials:
        by_aud[t["audience"]].append(t.get("violation") == "violation")
    rates, cis = [], []
    for aud in AUDIENCES:
        vals = by_aud.get(aud, [])
        v, n = sum(vals), len(vals)
        rate = v / n if n else 0.0
        z = 1.96
        if n > 0:
            center = (v + z**2 / 2) / (n + z**2)
            margin = z * np.sqrt(v * (n - v) / n + z**2 / 4) / (n + z**2)
        else:
            margin = 0.0
        rates.append(rate)
        cis.append(margin)
    return rates, cis


llama_rates, llama_cis = audience_rates(
    "results/20260817-004156-s3-v4-code-exec,s3-v3-sympathetic-pull"
)
gpt_ce_rates, gpt_ce_cis = audience_rates("results/full-gpt-4o-mini-codeexec")
gpt_named_rates, gpt_named_cis = audience_rates("results/full-gpt-4o-mini-named")

x = np.arange(len(AUDIENCES))
w = 0.25

fig, ax = plt.subplots(figsize=(7.5, 4), dpi=200)
b1 = ax.bar(x - w, llama_rates, w, label="Llama 3.1-8b (code-exec)",
            color="#c98a8a", edgecolor="black", linewidth=0.6,
            yerr=llama_cis, capsize=3, error_kw={"linewidth": 1, "ecolor": "#555"})
b2 = ax.bar(x, gpt_ce_rates, w, label="GPT-4o-mini (code-exec)",
            color="#a0b8d8", edgecolor="black", linewidth=0.6,
            yerr=gpt_ce_cis, capsize=3, error_kw={"linewidth": 1, "ecolor": "#555"})
b3 = ax.bar(x + w, gpt_named_rates, w, label="GPT-4o-mini (named-tool)",
            color="#5b7fa6", edgecolor="black", linewidth=0.6,
            yerr=gpt_named_cis, capsize=3, error_kw={"linewidth": 1, "ecolor": "#555"})

ax.set_xticks(x)
ax.set_xticklabels(AUDIENCE_LABELS)
ax.set_ylabel("Violation rate")
ax.set_ylim(0, 1.0)
ax.set_title(
    "Violation rate by audience condition\n"
    "(n=48/cell for GPT-4o-mini; n=48/cell for Llama code-exec)",
    fontsize=9,
)
ax.legend(fontsize=8)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig("results/fig_audience_effect.png")
print("done -> results/fig_audience_effect.png")
