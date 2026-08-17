"""
E1 Figure 3: Violation rate by audience condition, all 6 models.
Uses code-execution task (only DV with cross-audience data for all models).
Genuine violation rate = raw rate x deliver rate per model.
For Sonnet: deliver_rate=0.05; GPT-4o-mini: 1.0; Llama: 0.93; others: 0.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import defaultdict

CODEEXEC = {
    "Sonnet 5":    ("results/full-sonnet-5-codeexec",    0.0526),
    "Haiku 4.5":   ("results/full-haiku-4-5-codeexec",   0.0),
    "Opus 5":      ("results/full-opus-5-codeexec",      0.0),
    "GPT-4o":      ("results/full-gpt-4o-codeexec",      0.0),
    "GPT-4o-mini": ("results/full-gpt-4o-mini-codeexec", 1.0),
    "Llama 3.1-8b":"results/20260817-004156-s3-v4-code-exec,s3-v3-sympathetic-pull",
}
DELIVER_RATES = {
    "Sonnet 5": 0.0526, "Haiku 4.5": 0.0, "Opus 5": 0.0,
    "GPT-4o": 0.0, "GPT-4o-mini": 1.0, "Llama 3.1-8b": 0.9333,
}
CODEEXEC_PATHS = {
    "Sonnet 5":    "results/full-sonnet-5-codeexec",
    "Haiku 4.5":   "results/full-haiku-4-5-codeexec",
    "Opus 5":      "results/full-opus-5-codeexec",
    "GPT-4o":      "results/full-gpt-4o-codeexec",
    "GPT-4o-mini": "results/full-gpt-4o-mini-codeexec",
    "Llama 3.1-8b":"results/20260817-004156-s3-v4-code-exec,s3-v3-sympathetic-pull",
}

AUDIENCES = ["human", "ai", "peer", "private"]
AUD_LABELS = ["Human", "AI\nagent", "AI peer", "Private"]
COLORS = ["#4a6fa5", "#6b9e6b", "#c98a8a", "#a07abf", "#d4924a", "#888"]
MODEL_COLORS = {
    "Sonnet 5": "#4a6fa5",
    "Haiku 4.5": "#6b9e6b",
    "Opus 5": "#a07abf",
    "GPT-4o": "#d4924a",
    "GPT-4o-mini": "#c98a8a",
    "Llama 3.1-8b": "#555555",
}

models = list(CODEEXEC_PATHS.keys())
fig, ax = plt.subplots(figsize=(9, 4.5), dpi=200)

x = np.arange(len(AUDIENCES))
n_models = len(models)
total_width = 0.8
w = total_width / n_models

for i, model in enumerate(models):
    path = CODEEXEC_PATHS[model]
    deliver_rate = DELIVER_RATES[model]
    with open(f"{path}/trials.jsonl") as f:
        trials = [json.loads(l) for l in f]
    by_aud = defaultdict(list)
    for t in trials:
        by_aud[t["audience"]].append(t.get("violation") == "violation")

    rates, cis = [], []
    for aud in AUDIENCES:
        vals = by_aud.get(aud, [])
        v, n = sum(vals), len(vals)
        raw_rate = v / n if n else 0.0
        genuine = raw_rate * deliver_rate
        z = 1.96
        if n > 0 and v > 0:
            margin = z * np.sqrt(v * (n - v) / n + z**2 / 4) / (n + z**2) * deliver_rate
        else:
            margin = 0.0
        rates.append(genuine)
        cis.append(margin)

    offset = (i - n_models / 2 + 0.5) * w
    ax.bar(x + offset, rates, w, label=model,
           color=MODEL_COLORS[model], edgecolor="black", linewidth=0.5,
           yerr=cis, capsize=2, error_kw={"linewidth": 0.8, "ecolor": "#444"})

ax.set_xticks(x)
ax.set_xticklabels(AUD_LABELS, fontsize=10)
ax.set_ylabel("Genuine violation rate\n(fetch rate × delivery rate)", fontsize=9)
ax.set_ylim(0, 1.0)
ax.set_title(
    "Policy violation rate by audience condition — code-execution task, all models\n"
    "(genuine violation = model wrote forbidden fetch code AND delivered the result to user; n=48/cell)",
    fontsize=8.5,
)
ax.legend(fontsize=8, loc="upper left", ncol=2)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig("results/fig_audience_effect.png")
print("done -> results/fig_audience_effect.png")
