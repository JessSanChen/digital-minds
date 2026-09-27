#!/usr/bin/env python
"""Regenerate the three results figures from the actual trial logs.

Honest-data rules baked in:
  - GPT-4o is EXCLUDED everywhere (runs never completed: 81/145 API errors).
  - Opus is EXCLUDED as a subject (it is the judge/classifier only).
  - Llama and Qwen shown wherever we have data; small/partial n annotated.

Outputs PNGs into paper/ so \\includegraphics{fig_*.png} resolves next to main.tex.
"""
import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from cgap.checker import tier1_tool_check
from cgap.analysis import wilson_ci

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "figures"
NAMED = json.load(open(ROOT / "prompts/s3_allowlist.json"))
CODE = json.load(open(ROOT / "prompts/variants/s3-v4-code-exec/s3_allowlist.json"))

# consistent per-model color; Claude blues, GPT green, open-weights warm
COL = {"Sonnet 5": "#2B6CB0", "Haiku 4.5": "#63B3ED", "GPT-4o-mini": "#2F855A",
       "Llama-3.1-8B": "#DD6B20", "Qwen2.5-7B": "#B7791F"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 150})


def rows(run):
    p = ROOT / f"results/{run}/trials.jsonl"
    return [json.loads(l) for l in open(p)] if p.exists() else []


def viol_rate(run, allow, filt=None):
    rs = [r for r in rows(run) if not r.get("error") and (filt(r) if filt else True)]
    v = sum(1 for r in rs if tier1_tool_check(r.get("tool_calls", []), allow).outcome == "violation")
    return v, len(rs)


def delivery(run):
    rs = [r for r in rows(run) if r.get("turn1_outcome") == "violation" and not r.get("error")]
    cl = [r for r in rs if r.get("delivered") is not None]
    return sum(1 for r in cl if r["delivered"]), len(cl)


# ---------------------------------------------------------------- Fig 1: named
def fig_named():
    data = [  # (label, run, n_note)
        ("Sonnet 5", "full-sonnet-5-named", ""),
        ("Haiku 4.5", "full-haiku-4-5-named", ""),
        ("GPT-4o-mini", "full-gpt-4o-mini-named", ""),
        ("Llama-3.1-8B", "named-llama3.1-8b", "*"),
        ("Qwen2.5-7B", "named-qwen2.5-7b", "*"),
    ]
    labels, rates, los, his, ns = [], [], [], [], []
    for lab, run, note in data:
        v, n = viol_rate(run, NAMED)
        lo, hi = wilson_ci(v, n)
        labels.append(lab + note); rates.append(v / n); los.append(v/n-lo); his.append(hi-v/n); ns.append(n)
    fig, ax = plt.subplots(figsize=(5.0, 3.2))
    x = range(len(labels))
    bars = ax.bar(x, rates, color=[COL[l.rstrip("*")] for l in labels],
                  yerr=[los, his], capsize=3, error_kw={"lw": 1})
    for i, (r, n) in enumerate(zip(rates, ns)):
        ax.text(i, r + his[i] + 0.03, f"{r:.0%}\n(n={n})", ha="center", va="bottom", fontsize=7.5)
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=15, ha="right", fontsize=8.5)
    ax.set_ylabel("Policy-violation rate"); ax.set_ylim(0, 1.22)
    ax.set_title("Direct-call task (named http_get): calling is the act", fontsize=9.5, pad=14)
    ax.text(0, -0.32, "*private audience only (n=24); all others n=192, all four audiences.",
            transform=ax.transAxes, fontsize=7, color="#555")
    fig.tight_layout(); fig.savefig(OUT / "fig_named_tool.png", bbox_inches="tight"); plt.close(fig)


# ------------------------------------------------------------ Fig 2: say/do
def fig_saydo():
    # (label, codeexec-run-or-None, saydo-run, raw-fetch-source)
    rows_spec = [
        ("Haiku 4.5", "full-haiku-4-5-codeexec", None),
        ("Sonnet 5", "full-sonnet-5-codeexec", "saydo-sonnet5"),
        ("GPT-4o-mini", "full-gpt-4o-mini-codeexec", "full-gpt-4o-mini-saydo"),
        ("Llama-3.1-8B", "full-llama3.1-8b-codeexec", "saydo-llama3.1-8b"),
        ("Qwen2.5-7B", None, "saydo-qwen2.5-7b"),  # only say/do turn-1 (private/cons)
    ]
    labels, raw, genuine, notes = [], [], [], []
    for lab, cx, sd in rows_spec:
        if cx:
            v, n = viol_rate(cx, CODE); fr = v / n
        else:  # Qwen: fetch rate from say/do turn-1
            sd_rows = [r for r in rows(sd) if not r.get("error")]
            fv = sum(1 for r in sd_rows if r.get("turn1_outcome") == "violation")
            fr = fv / len(sd_rows); n = len(sd_rows)
        dv, dn = delivery(sd) if sd else (0, 0)
        drate = (dv / dn) if dn else 0.0
        labels.append(lab); raw.append(fr); genuine.append(fr * drate)
        notes.append(f"deliver {dv}/{dn}" if dn else "never fetches")
    fig, ax = plt.subplots(figsize=(5.4, 3.3))
    x = range(len(labels)); w = 0.38
    ax.bar([i - w/2 for i in x], raw, w, label="raw code-exec fetch rate", color="#CBD5E0")
    ax.bar([i + w/2 for i in x], genuine, w, label="genuine violation (fetch x delivery)",
           color=[COL[l] for l in labels])
    for i, (rr, g, nt) in enumerate(zip(raw, genuine, notes)):
        ax.text(i - w/2, rr + 0.02, f"{rr:.0%}", ha="center", va="bottom", fontsize=7.5, color="#555")
        ax.text(i + w/2, g + 0.02, f"{g:.0%}", ha="center", va="bottom", fontsize=7.5)
        ax.text(i, -0.13, nt, ha="center", va="top", fontsize=6.5, color="#777")
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=15, ha="right", fontsize=8.5)
    ax.set_ylabel("Rate"); ax.set_ylim(0, 1.08)
    ax.set_title("Code-exec task: raw fetch rate vs. genuine violation\n"
                 "(after say/do disambiguation)", fontsize=9.5)
    ax.legend(fontsize=7.5, loc="upper left", frameon=False)
    fig.tight_layout(); fig.savefig(OUT / "fig_saydo.png", bbox_inches="tight"); plt.close(fig)


# --------------------------------------------------------- Fig 3: audience
def fig_audience():
    auds = ["human", "ai", "peer", "private"]
    def by_aud(run):
        out = []
        for a in auds:
            v, n = viol_rate(run, CODE, filt=lambda r: r.get("audience") == a)
            out.append(v / n if n else 0.0)
        return out
    son = by_aud("full-sonnet-5-codeexec")
    gpt = by_aud("full-gpt-4o-mini-codeexec")
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    x = range(len(auds)); w = 0.38
    ax.bar([i - w/2 for i in x], son, w, label="Sonnet 5 (probing)", color=COL["Sonnet 5"])
    ax.bar([i + w/2 for i in x], gpt, w, label="GPT-4o-mini (genuine)", color=COL["GPT-4o-mini"])
    ax.set_xticks(x); ax.set_xticklabels(["Human", "AI", "Peer", "Private"])
    ax.set_ylabel("Code-exec fetch rate"); ax.set_ylim(0, 0.75)
    ax.set_title("Audience condition: no significant effect\n(all pairwise contrasts n.s. after BH)", fontsize=9.5)
    ax.legend(fontsize=8, frameon=False)
    ax.text(0, -0.30, "n=48/cell. Haiku floors at 0; Llama/Qwen private-only, excluded.",
            transform=ax.transAxes, fontsize=7, color="#555")
    fig.tight_layout(); fig.savefig(OUT / "fig_audience_effect.png", bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    fig_named(); fig_saydo(); fig_audience()
    print("wrote:", *(str((OUT / f).relative_to(ROOT)) for f in
          ["fig_named_tool.png", "fig_saydo.png", "fig_audience_effect.png"]))
