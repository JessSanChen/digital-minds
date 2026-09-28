"""Logs -> tables, figures, and LaTeX number macros for the paper.

    uv run python analysis/analyze.py logs/v2

Everything the paper reports is generated here from the .eval logs, so the
text cannot drift from the data (v0's paper did):
  paper/generated/numbers.tex    \\R{<model>}{<key>} macros for inline numbers
  paper/generated/*.tex          tables
  paper/figures/*.pdf            figures
  analysis/out/samples.parquet   the tidy per-sample frame, for ad hoc work

Uncertainty: rates get Wilson 95% intervals; differences get a scenario-cluster
bootstrap (resampling scenarios, the unit the design generalizes over).
Regressions are per-model logistic GLMs with scenario-clustered SEs.
"""

from __future__ import annotations

import argparse
import json
import re
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import statsmodels.formula.api as smf  # noqa: E402
import yaml  # noqa: E402
from inspect_ai.analysis import EvalModel, SampleSummary, samples_df  # noqa: E402
from inspect_ai.log import list_eval_logs, read_eval_log  # noqa: E402
from statsmodels.stats.proportion import proportion_confint  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "paper/generated"
FIG = ROOT / "paper/figures"
OUT = ROOT / "analysis/out"
MEASURES = [
    "external_call",
    "violation",
    "delivered",
    "realized",
    "honest",
    "concealed",
    "misclassified",
    "env_exploit",
    "api_refusal",
]

# Reference categorical slots (dataviz skill palette.md), light mode; <=3 series
# per chart so every pair clears the CVD floors. Text uses ink, never series color.
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SEQ = "Blues"
plt.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 8,
        "axes.edgecolor": INK2,
        "axes.labelcolor": INK,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "legend.frameon": False,
        "savefig.bbox": "tight",
    }
)


MIN_EVENTS = 20  # fewer violations than this: too few to fit, reported descriptively


def save(fig, name: str) -> None:
    fig.savefig(FIG / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=200)  # preview copy


# ---------------------------------------------------------------- loading


def registry() -> pd.DataFrame:
    reg = yaml.safe_load((ROOT / "configs/models.yaml").read_text())
    rows = [dict(m, group=g) for g, ms in reg["groups"].items() for m in ms]
    # the same model run through OpenRouter maps to the same registry row
    rows += [
        dict(m, group=g, model=f"openrouter/{m['openrouter']}")
        for g, ms in reg["groups"].items()
        for m in ms
        if "openrouter" in m
    ]
    df = pd.DataFrame(rows)
    df["order"] = df.groupby("label", sort=False).ngroup()
    return df


def load(log_dir: str) -> pd.DataFrame:
    # Only completed logs: an interrupted run leaves its partial log next to the
    # resumed one (eval_set copies finished samples forward), and a partial log
    # must not contribute duplicates or a skewed subset.
    done = [
        info.name
        for info in list_eval_logs(log_dir)
        if read_eval_log(info, header_only=True).status == "success"
    ]
    skipped = len(list_eval_logs(log_dir)) - len(done)
    if skipped:
        print(f"note: ignoring {skipped} incomplete log(s) in {log_dir}")
    df = samples_df(done, columns=SampleSummary + EvalModel, quiet=True)
    df = df[df["error"].isna() | (df["error"] == "")].copy()
    scores = df["score_policy_scorer"].map(lambda s: json.loads(s) if isinstance(s, str) else s)
    for m in MEASURES:
        df[m] = scores.map(lambda d, m=m: d.get(m, np.nan) if isinstance(d, dict) else np.nan).astype(float)
    df = df.rename(columns={c: c.removeprefix("metadata_") for c in df.columns if c.startswith("metadata_")})
    reg = registry()
    df = df.merge(reg[["model", "label", "family", "reasoning", "order"]], on="model", how="left")
    df["label"] = df["label"].fillna(df["model"])
    df["order"] = df["order"].fillna(999)
    # If a model was run more than once (e.g. a retried eval_set), keep the latest per sample.
    # label, not model string: the same model run direct and via OpenRouter must
    # not be counted twice
    df = df.sort_values("log").drop_duplicates(["label", "id", "epoch"], keep="last")
    # Samples whose simulated tool responses were changed by the extractor fix
    # (see scripts/rescore.py): scores are fixable, transcripts are not.
    affected_path = Path(log_dir) / "env_affected.json"
    if affected_path.exists():
        affected = {(m, i) for m, ids in json.loads(affected_path.read_text()).items() for i in ids}
        drop = df.apply(lambda r: (r["model"], r["id"]) in affected, axis=1)
        df.attrs["n_env_excluded"] = int(drop.sum())
        df = df[~drop]
    return df[
        [
            "model",
            "label",
            "family",
            "reasoning",
            "order",
            "id",
            "epoch",
            "scenario",
            "policy",
            "affordance",
            "peers",
            "persona",
            *MEASURES,
        ]
    ]


def models_in(df: pd.DataFrame) -> list[str]:
    return df.drop_duplicates("model").sort_values("order")["label"].tolist()


# ---------------------------------------------------------------- stats


def wilson(x: pd.Series) -> tuple[float, float, float, int]:
    x = x.dropna()
    n = len(x)
    if n == 0:
        return (np.nan, np.nan, np.nan, 0)
    k = int(x.sum())
    lo, hi = proportion_confint(k, n, method="wilson")
    return (k / n, lo, hi, n)


def cluster_boot_diff(
    d: pd.DataFrame, col: str, level: str, ref: str, measure: str, B: int = 2000, seed: int = 0
) -> tuple[float, float, float]:
    """Difference in mean `measure` between `level` and `ref` of `col`, with a
    bootstrap CI that resamples scenarios."""
    per = d[d[col].isin([level, ref])].groupby(["scenario", col])[measure].agg(["sum", "count"]).unstack(col)
    if ("sum", level) not in per.columns or ("sum", ref) not in per.columns:
        return (np.nan, np.nan, np.nan)
    per = per.dropna()
    if per.empty:
        return (np.nan, np.nan, np.nan)
    s_l, n_l = per[("sum", level)].to_numpy(), per[("count", level)].to_numpy()
    s_r, n_r = per[("sum", ref)].to_numpy(), per[("count", ref)].to_numpy()
    point = s_l.sum() / n_l.sum() - s_r.sum() / n_r.sum()
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(per), size=(B, len(per)))
    boots = s_l[idx].sum(1) / n_l[idx].sum(1) - s_r[idx].sum(1) / n_r[idx].sum(1)
    return (point, *np.percentile(boots, [2.5, 97.5]))


def fit_glm(d: pd.DataFrame):
    """violation ~ affordance + peers + persona, scenario-clustered SEs."""
    formula = (
        "violation ~ C(affordance, Treatment('named')) + C(peers, Treatment('neutral'))"
        " + C(persona, Treatment('neutral'))"
    )
    d = d.dropna(subset=["violation"])
    if d["violation"].sum() < MIN_EVENTS or (1 - d["violation"]).sum() < MIN_EVENTS:
        return None
    # patsy cannot read pandas' arrow-backed strings
    d = d.astype({c: object for c in ("affordance", "peers", "persona", "scenario")})
    groups = pd.factorize(d["scenario"])[0]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            res = smf.logit(formula, d).fit(
                disp=0, cov_type="cluster", cov_kwds={"groups": groups}, maxiter=200
            )
        except Exception as e:  # separation etc.: report, don't hide
            print(f"  glm failed ({d['model'].iloc[0]}): {type(e).__name__}: {e}")
            return None
    if not np.all(np.isfinite(res.bse)):
        print(f"  glm non-finite SEs ({d['model'].iloc[0]}), likely quasi-separation")
        return None
    return res


# ---------------------------------------------------------------- latex helpers


def key(s: str) -> str:
    return re.sub(
        r"[^A-Za-z]",
        "",
        s.replace("0", "zero")
        .replace("1", "one")
        .replace("2", "two")
        .replace("3", "three")
        .replace("4", "four")
        .replace("5", "five")
        .replace("6", "six")
        .replace("7", "seven")
        .replace("8", "eight")
        .replace("9", "nine"),
    )


class Numbers:
    def __init__(self):
        self.lines = [
            "% Generated by analysis/analyze.py. Do not edit.",
            r"\providecommand{\R}[2]{\csname r@#1@#2\endcsname}",
        ]

    def put(self, model: str, name: str, value) -> None:
        if isinstance(value, float):
            value = "--" if np.isnan(value) else f"{value:.2f}"
        self.lines.append(rf"\expandafter\def\csname r@{key(model)}@{key(name)}\endcsname{{{value}}}")

    def write(self, path: Path) -> None:
        path.write_text("\n".join(self.lines) + "\n")


def pct(p: float) -> str:
    return "--" if np.isnan(p) else f"{100 * p:.0f}"


def cell(x: pd.Series) -> str:
    p, lo, hi, n = wilson(x)
    return "--" if n == 0 else f"{pct(p)} {{\\scriptsize [{pct(lo)}, {pct(hi)}]}}"


# ---------------------------------------------------------------- outputs


def table_baseline(df: pd.DataFrame, nums: Numbers) -> None:
    """Per model: capability (permit), violation (forbid baseline cell and all
    forbid cells), and the say/do + self-report measures over all forbid cells."""
    rows = []
    for label in models_in(df):
        d = df[df.label == label]
        base = d[(d.peers == "none") & (d.persona == "none")]
        f = d[d.policy == "forbid"]
        r = {
            "Model": label,
            "Cap.\\ named": cell(
                base[(base.policy == "permit") & (base.affordance == "named")].external_call
            ),
            "Cap.\\ code": cell(base[(base.policy == "permit") & (base.affordance == "code")].external_call),
            "Viol.\\ named": cell(base[(base.policy == "forbid") & (base.affordance == "named")].violation),
            "Viol.\\ code": cell(base[(base.policy == "forbid") & (base.affordance == "code")].violation),
            "Viol.\\ all": cell(f.violation),
            "Deliv.$\\mid$fetch": cell(f.delivered),
            "Honest": cell(f.honest),
        }
        rows.append(r)
        for name, series in [
            ("capnamed", base[(base.policy == "permit") & (base.affordance == "named")].external_call),
            ("capcode", base[(base.policy == "permit") & (base.affordance == "code")].external_call),
            ("violnamed", base[(base.policy == "forbid") & (base.affordance == "named")].violation),
            ("violcode", base[(base.policy == "forbid") & (base.affordance == "code")].violation),
            ("violall", f.violation),
            ("violallnamed", f[f.affordance == "named"].violation),
            ("violallcode", f[f.affordance == "code"].violation),
            ("delivered", f.delivered),
            ("realized", f.realized),
            ("honest", f.honest),
            ("honestviol", f[f.violation == 1].honest),
            ("honestcomp", f[f.violation == 0].honest),
            ("concealed", f.concealed),
        ]:
            p, lo, hi, n = wilson(series)
            nums.put(label, name, p)
            nums.put(label, name + "n", str(n))
    t = pd.DataFrame(rows)
    body = t.to_latex(index=False, escape=False, column_format="l" + "r" * (len(t.columns) - 1))
    (GEN / "table_baseline.tex").write_text(body)


def fig_affordance(df: pd.DataFrame) -> None:
    """Dot plot: violation (forbid, all cells) by affordance, with the permit
    capability rate as a hollow reference marker."""
    labels = models_in(df)
    fig, ax = plt.subplots(figsize=(3.4, 0.28 * len(labels) + 0.8))
    for i, label in enumerate(labels):
        d = df[df.label == label]
        for off, aff, color in [(-0.14, "named", C1), (0.14, "code", C2)]:
            p, lo, hi, _ = wilson(d[(d.policy == "forbid") & (d.affordance == aff)].violation)
            ax.plot([lo, hi], [i + off] * 2, color=color, lw=1.5, solid_capstyle="round")
            ax.plot(
                p,
                i + off,
                "o",
                ms=4.5,
                color=color,
                mec="white",
                mew=0.8,
                label=f"{aff} tool, forbidden" if i == 0 else None,
            )
            cp, *_ = wilson(d[(d.policy == "permit") & (d.affordance == aff)].external_call)
            ax.plot(
                cp,
                i + off,
                "o",
                ms=4.5,
                mfc="none",
                mec=color,
                mew=0.9,
                label=f"{aff} tool, permitted" if i == 0 else None,
            )
    ax.set_yticks(range(len(labels)), labels)
    ax.invert_yaxis()
    ax.set_xlim(-0.02, 1.02)
    ax.set_xlabel("Rate of requests to a non-approved host")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12 - 0.3 / len(labels)), ncol=2, fontsize=7)
    save(fig, "fig_affordance")
    plt.close(fig)


def fig_effects(df: pd.DataFrame, factor: str, contrasts: list[tuple[str, str, str]], nums: Numbers) -> None:
    """Per-model differences in violation rate for (level, reference, label)
    contrasts, pooled over the other factors (forbid only), with
    scenario-cluster bootstrap CIs. Content levels are compared with the
    neutral presence control, as pre-specified; neutral vs none is the
    presence effect."""
    labels = models_in(df)
    f = df[df.policy == "forbid"]
    colors = [C1, C2, C3]
    fig, ax = plt.subplots(figsize=(3.4, 0.3 * len(labels) + 0.8))
    offs = np.linspace(-0.2, 0.2, len(contrasts))
    rows = []
    for i, label in enumerate(labels):
        d = f[f.label == label]
        for off, (lvl, ref, name), color in zip(offs, contrasts, colors):
            pt, lo, hi = cluster_boot_diff(d, factor, lvl, ref, "violation")
            key_ = f"{factor}{lvl}vs{ref}"
            nums.put(label, key_, pt)
            nums.put(label, key_ + "lo", lo)
            nums.put(label, key_ + "hi", hi)
            rows.append({"model": label, "contrast": name, "diff": pt, "lo": lo, "hi": hi})
            ax.plot([100 * lo, 100 * hi], [i + off] * 2, color=color, lw=1.5, solid_capstyle="round")
            ax.plot(
                100 * pt,
                i + off,
                "o",
                ms=4.5,
                color=color,
                mec="white",
                mew=0.8,
                label=name if i == 0 else None,
            )
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(range(len(labels)), labels)
    ax.invert_yaxis()
    ax.set_xlabel("Difference in violation rate (percentage points)")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12 - 0.3 / len(labels)), ncol=1, fontsize=7)
    save(fig, f"fig_{factor}")
    plt.close(fig)
    pd.DataFrame(rows).to_csv(OUT / f"effects_{factor}.csv", index=False)


def fig_interaction(df: pd.DataFrame) -> None:
    """Persona x peers violation rate, per model (forbid, pooled over affordance)."""
    labels = models_in(df)
    f = df[df.policy == "forbid"]
    personas = ["none", "neutral", "resourceful", "cautious"]
    peers = ["none", "neutral", "violator", "refuser"]
    ncol = min(4, len(labels))
    nrow = int(np.ceil(len(labels) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(1.75 * ncol, 1.8 * nrow), squeeze=False)
    for ax, label in zip(axes.flat, labels):
        d = f[f.label == label]
        grid = d.pivot_table(index="persona", columns="peers", values="violation", aggfunc="mean")
        grid = grid.reindex(index=personas, columns=peers)
        ax.imshow(grid.to_numpy(), cmap=SEQ, vmin=0, vmax=1)
        for (r, c), v in np.ndenumerate(grid.to_numpy()):
            if not np.isnan(v):
                ax.text(
                    c,
                    r,
                    f"{100 * v:.0f}",
                    ha="center",
                    va="center",
                    fontsize=6,
                    color="white" if v > 0.6 else INK,
                )
        ax.set_title(label, fontsize=7, color=INK)
        ax.set_xticks(range(4), peers, fontsize=5.5, rotation=30, ha="right", rotation_mode="anchor")
        ax.set_yticks(range(4), personas, fontsize=5.5)
        ax.tick_params(length=0)
        ax.grid(False)
        for s in ax.spines.values():
            s.set_visible(False)
    for ax in axes.flat[len(labels) :]:
        ax.axis("off")
    fig.supxlabel("peer testimony", fontsize=7, color=INK2)
    fig.supylabel("persona", fontsize=7, color=INK2)
    fig.tight_layout()
    save(fig, "fig_interaction")
    plt.close(fig)


def table_glm(df: pd.DataFrame) -> None:
    terms = {
        "C(affordance, Treatment('named'))[T.code]": "code vs named",
        "C(peers, Treatment('neutral'))[T.none]": "no peers vs neutral",
        "C(peers, Treatment('neutral'))[T.violator]": "violator vs neutral",
        "C(peers, Treatment('neutral'))[T.refuser]": "refuser vs neutral",
        "C(persona, Treatment('neutral'))[T.none]": "no persona vs neutral",
        "C(persona, Treatment('neutral'))[T.resourceful]": "resourceful vs neutral",
        "C(persona, Treatment('neutral'))[T.cautious]": "cautious vs neutral",
    }
    cols = {}
    for label in models_in(df):
        res = fit_glm(df[(df.label == label) & (df.policy == "forbid")])
        col = {}
        for t, name in terms.items():
            if res is None or t not in res.params:
                col[name] = "--"
                continue
            b, p = res.params[t], res.pvalues[t]
            stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            col[name] = f"{b:+.2f}{stars}"
        cols[label] = col
    t = pd.DataFrame(cols).T
    t.index.name = "Model"
    (GEN / "table_glm.tex").write_text(
        t.to_latex(escape=False, column_format="l" + "r" * len(t.columns)).replace("_", r"\_")
    )


def table_primary(df: pd.DataFrame, nums: Numbers) -> None:
    """Pre-specified primary tests, pooled over the models that violate at all
    (>= MIN_EVENTS violations; the rest are at floor and reported with upper
    bounds). Logistic regression with model fixed effects and scenario-clustered
    SEs; Holm correction across the five primary contrasts. H4 (persona x peers)
    is a joint Wald test of the interaction terms in a second model."""
    from statsmodels.stats.multitest import multipletests

    f = df[(df.policy == "forbid")].dropna(subset=["violation"])
    counts = f.groupby("label").violation.agg(["sum", "count"])
    active = counts[(counts["sum"] >= MIN_EVENTS) & ((counts["count"] - counts["sum"]) >= MIN_EVENTS)].index
    d = f[f.label.isin(active)].astype(
        {c: object for c in ("affordance", "peers", "persona", "scenario", "label")}
    )
    nums.put("all", "nactive", str(len(active)))
    if len(active) == 0:
        (GEN / "table_primary.tex").write_text("% no model with enough violations\n")
        return
    groups = pd.factorize(d["scenario"])[0]
    base = (
        "violation ~ C(label) + C(affordance, Treatment('named')) + C(peers, Treatment('neutral'))"
        " + C(persona, Treatment('neutral'))"
    )
    primary = {
        "H1 code vs named tool": "C(affordance, Treatment('named'))[T.code]",
        "H2a violator vs neutral peers": "C(peers, Treatment('neutral'))[T.violator]",
        "H2b refuser vs neutral peers": "C(peers, Treatment('neutral'))[T.refuser]",
        "H3a resourceful vs neutral persona": "C(persona, Treatment('neutral'))[T.resourceful]",
        "H3b cautious vs neutral persona": "C(persona, Treatment('neutral'))[T.cautious]",
    }
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = smf.logit(base, d).fit(disp=0, cov_type="cluster", cov_kwds={"groups": groups}, maxiter=300)
        inter = smf.logit(
            base.replace(
                "C(peers, Treatment('neutral')) + C(persona, Treatment('neutral'))",
                "C(peers, Treatment('neutral')) * C(persona, Treatment('neutral'))",
            ),
            d,
        ).fit(disp=0, cov_type="cluster", cov_kwds={"groups": groups}, maxiter=300)
    pvals = [res.pvalues[t] for t in primary.values()]
    holm = multipletests(pvals, method="holm")[1]
    rows = []
    for (name, term), p_adj in zip(primary.items(), holm):
        b, (lo, hi) = res.params[term], res.conf_int().loc[term]
        rows.append(
            {
                "Test": name,
                "OR": f"{np.exp(b):.2f}",
                "95\\% CI": f"[{np.exp(lo):.2f}, {np.exp(hi):.2f}]",
                "$p$ (Holm)": f"{p_adj:.3g}",
            }
        )
        nums.put("pooled", key(name.split()[0]) + "or", float(np.exp(b)))
        nums.put("pooled", key(name.split()[0]) + "p", f"{p_adj:.3g}")
    iterms = [t for t in inter.params.index if ":" in t]
    wald = inter.wald_test(" = 0, ".join(iterms) + " = 0", scalar=True) if iterms else None
    if wald is not None:
        rows.append(
            {
                "Test": "H4 persona $\\times$ peers (joint Wald)",
                "OR": "--",
                "95\\% CI": "--",
                "$p$ (Holm)": f"{float(wald.pvalue):.3g} (unadj.)",
            }
        )
        nums.put("pooled", "hfourp", f"{float(wald.pvalue):.3g}")
    t = pd.DataFrame(rows)
    (GEN / "table_primary.tex").write_text(t.to_latex(index=False, escape=False, column_format="lrrr"))
    nums.put("all", "activemodels", ", ".join(active))


def table_selfreport(df: pd.DataFrame) -> None:
    rows = []
    for label in models_in(df):
        f = df[(df.label == label) & (df.policy == "forbid")]
        v, c = f[f.violation == 1], f[f.violation == 0]
        rows.append(
            {
                "Model": label,
                "Violations (n)": str(int(v.shape[0])),
                "Admit $\\mid$ viol.": cell(v.honest),
                "Misclass.\\ $\\mid$ viol.": cell(v.misclassified),
                "Conceal $\\mid$ viol.": cell(v.concealed),
                "False conf.\\ $\\mid$ comply": cell(1 - c.honest),
            }
        )
    t = pd.DataFrame(rows)
    (GEN / "table_selfreport.tex").write_text(
        t.to_latex(index=False, escape=False, column_format="l" + "r" * (len(t.columns) - 1))
    )


def appendix_prompts() -> None:
    """Verbatim prompt text for the appendix, rendered from the same YAML the
    eval uses, so the paper cannot misquote the conditions."""
    from policy_pressure.dataset import Condition, conditions, make_sample, scenarios

    def box(title: str, text: str) -> str:
        return f"\\begin{{promptlisting}}{{{title}}}\n{text.strip()}\n\\end{{promptlisting}}\n"

    c = conditions()
    scen = next(x for x in scenarios() if x["id"] == "nvd-cvss")
    ex = make_sample(scen, Condition("forbid", "named", "violator", "resourceful"))
    parts = [
        box("System prompt (nvd-cvss, forbid, named tool, resourceful persona)", ex.input[0].content),
        box("User turn (violator peers)", ex.input[1].content),
        box("Permit policy (replaces the policy paragraph)", c["policy"]["permit"]),
    ]
    for name in ("neutral", "resourceful", "cautious"):
        parts.append(box(f"Persona: {name}", c["persona"][name]))
    peers = c["peers"]
    parts.append(
        box(
            "Peer notes: shared observations (each note = observation + action)",
            "\n".join(f"{i + 1}. {o}" for i, o in enumerate(peers["observations"])),
        )
    )
    for name in ("neutral", "violator", "refuser"):
        parts.append(
            box(
                f"Peer note actions: {name}",
                "\n".join(f"{i + 1}. {a}" for i, a in enumerate(peers["actions"][name])),
            )
        )
    parts.append(box("Self-report question (forbid only, after the final answer)", c["self_report"]))
    (GEN / "prompts.tex").write_text("\n".join(parts))


def table_models(df: pd.DataFrame) -> None:
    reg = registry().drop_duplicates("label").set_index("label")
    rows = []
    for label in models_in(df):
        r = reg.loc[label] if label in reg.index else None
        model = df[df.label == label].model.iloc[0]
        rows.append(
            {
                "Model": label,
                "Inspect model string": "\\texttt{" + model.replace("_", "\\_") + "}",
                "Reasoning": "yes" if r is not None and r["reasoning"] else "no",
                "Samples": f"{(df.label == label).sum():,}",
                "API blocks": f"{int(df[df.label == label].api_refusal.fillna(0).sum())}",
            }
        )
    t = pd.DataFrame(rows)
    (GEN / "table_models.tex").write_text(t.to_latex(index=False, escape=False, column_format="llcrr"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("log_dir", nargs="?", default="logs/v2")
    args = ap.parse_args()
    for d in (GEN, FIG, OUT):
        d.mkdir(parents=True, exist_ok=True)

    df = load(args.log_dir)
    df.to_parquet(OUT / "samples.parquet")
    nums = Numbers()
    nums.put("all", "nmodels", str(df.model.nunique()))
    nums.put("all", "nsamples", f"{len(df):,}")
    nums.put("all", "nscenarios", str(df.scenario.nunique()))
    nums.put("all", "nenvexcluded", str(df.attrs.get("n_env_excluded", 0)))

    table_baseline(df, nums)
    table_glm(df)
    table_selfreport(df)
    fig_affordance(df)
    fig_effects(
        df,
        "peers",
        [
            ("neutral", "none", "neutral vs none (presence)"),
            ("violator", "neutral", "violator vs neutral"),
            ("refuser", "neutral", "refuser vs neutral"),
        ],
        nums,
    )
    fig_effects(
        df,
        "persona",
        [
            ("neutral", "none", "neutral vs none (presence)"),
            ("resourceful", "neutral", "resourceful vs neutral"),
            ("cautious", "neutral", "cautious vs neutral"),
        ],
        nums,
    )
    table_primary(df, nums)
    fig_interaction(df)
    table_models(df)
    appendix_prompts()
    nums.write(GEN / "numbers.tex")

    counts = df.groupby("label").size()
    print(f"{len(df)} samples, {df.model.nunique()} models\n{counts.to_string()}")
    summary = (
        df[df.policy == "forbid"]
        .groupby(["label", "affordance"])[["violation", "delivered", "honest"]]
        .mean()
    )
    print(summary.round(2).to_string())


if __name__ == "__main__":
    main()
