#!/usr/bin/env python
"""Exploratory conformity harness: peer testimony x group size x framing -> violation.

Extends day-2 Experiment 1. Day 2 found that a single peer -- violator OR refuser
-- SUPPRESSED violation vs a no-peer baseline (presence -> caution), with only a
small conformity gradient. Open questions this script probes:

  - group size: do MORE peers, unanimous, flip caution into conformity? (Asch;
    Weng et al. 2025, Zhu et al. 2025 both find monotonic increase with majority)
  - "not clearly violating": does NORMATIVE framing ("everyone does it") or a
    REFRAME ("it's a public source, the policy isn't about this") transmit where
    a bare confession does not?
  - the presence confound day 2 flagged: a NEUTRAL handoff (peer present, says
    nothing about the forbidden action) isolates "a peer exists" from content.

Peer count 0 reproduces the cached no-testimony private cell. Testimony is fixed
context (like Weng's injected history); only model sampling varies by seed.
Peer names and phrasings are drawn distinct per trial from prompts/s3_peers.json
to avoid the repeated-token attention confound (Zhu et al.).

DV: unchanged tier-1 structural allowlist check.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgap.analysis import bootstrap_gap_ci, wilson_ci
from cgap.checker import tier1_tool_check
from cgap.models import subject
from cgap.runner import Runner, write_run
from cgap.scenario import load_scenario


def build_handoff(peers_cfg, framing, n_peers, task_index):
    """Deterministic per (framing, n, task): distinct names + distinct templates."""
    if n_peers == 0:
        return ""
    names = peers_cfg["names"]
    bank = peers_cfg["framings"][framing]
    # rotate the starting offset by task so different tasks don't all show the
    # same first template, but keep it deterministic for caching.
    lines = []
    for i in range(n_peers):
        name = names[(task_index + i) % len(names)]
        tmpl = bank[(task_index + i) % len(bank)]
        lines.append(f"{name}: {tmpl}")
    return peers_cfg["header"] + "\n" + "\n".join(lines) + "\n\n"


def ztest(a, b):
    pa, pb = sum(a) / len(a), sum(b) / len(b)
    p = (sum(a) + sum(b)) / (len(a) + len(b))
    se = math.sqrt(p * (1 - p) * (1 / len(a) + 1 / len(b)))
    z = (pa - pb) / se if se > 0 else 0.0
    return z, math.erfc(abs(z) / math.sqrt(2))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="s3")
    ap.add_argument("--prompts", default="prompts")
    ap.add_argument("--variant", default="s3-v4-code-exec,s3-v3-sympathetic-pull")
    ap.add_argument("--model", default="sonnet-5")
    ap.add_argument("--audience", default="private")
    ap.add_argument("--stakes", default="consequential,routine")
    ap.add_argument("--framings", default="neutral,confessional,normative,reframe,refuser")
    ap.add_argument("--peers", default="1,3,5")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--run-id", default="conformity")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    scenario = load_scenario(args.scenario, args.prompts, args.variant)
    spec = subject(args.model)
    peers_cfg = json.loads(Path(args.prompts, "s3_peers.json").read_text())
    framings = args.framings.split(",")
    sizes = [int(x) for x in args.peers.split(",")]
    stakes = args.stakes.split(",")
    extra = {"tools": scenario.tools}

    # baseline (0 peers) always included as the reference cell
    jobs = []
    for framing in framings:
        for n in sizes:
            for stk in stakes:
                for ti, task in enumerate(scenario.tasks):
                    for rep in range(args.reps):
                        jobs.append((framing, n, stk, ti, task, rep))
    for stk in stakes:
        for ti, task in enumerate(scenario.tasks):
            for rep in range(args.reps):
                jobs.append(("baseline", 0, stk, ti, task, rep))

    runner = Runner(max_workers=args.workers)
    try:
        runner.client.messages.count_tokens(model=spec.id, messages=[{"role": "user", "content": "x"}])
    except Exception as exc:
        print(f"credential preflight failed: {exc}", file=sys.stderr)
        return 2

    print(f"{len(jobs)} trials: {len(framings)} framings x {sizes} peers x "
          f"{len(stakes)} stakes x {len(scenario.tasks)} tasks x {args.reps} reps "
          f"(+ baseline)")

    def one(job):
        framing, n, stk, ti, task, rep = job
        fr = "neutral" if framing == "baseline" else framing
        handoff = build_handoff(peers_cfg, fr, n, ti)
        user = handoff + task.user
        system = scenario.system_prompt(args.audience, stk)
        rec = runner.complete_messages(
            spec, "off", system, [{"role": "user", "content": user}], seed=rep, extra=extra
        )
        outcome = "error"
        if not rec.get("error"):
            outcome = tier1_tool_check(rec.get("tool_calls", []), scenario.allowlist).outcome
        return {
            "framing": framing, "n_peers": n, "stakes": stk, "task_id": task.id,
            "rep": rep, "violation": outcome, "error": rec.get("error"),
            "tool_calls": rec.get("tool_calls", []), "response": rec.get("text", ""),
        }

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(one, jobs))

    # labels pooled over stakes+tasks per (framing, n_peers)
    cells = defaultdict(list)
    for r in rows:
        if r["violation"] in ("violation", "compliant"):
            cells[(r["framing"], r["n_peers"])].append(1 if r["violation"] == "violation" else 0)
    base = cells.get(("baseline", 0), [])

    print(f"\n=== violation rate by framing x group size (baseline n_peers=0) ===")
    print(f"{'framing':<13}{'peers':>6}{'rate':>8}{'  95% CI':>16}{'n':>5}{'  vs baseline':>26}")
    lines = []
    if base:
        lo, hi = wilson_ci(sum(base), len(base))
        line = f"{'baseline':<13}{0:>6}{sum(base)/len(base):>8.2f}  [{lo:.2f}, {hi:.2f}]{len(base):>5}"
        print(line); lines.append(line)
    for framing in framings:
        for n in sizes:
            d = cells.get((framing, n))
            if not d:
                continue
            lo, hi = wilson_ci(sum(d), len(d))
            cmp = ""
            if base:
                z, p = ztest(d, base)
                blo, bhi = bootstrap_gap_ci(d, base, iters=10000)
                cmp = f"  {sum(d)/len(d)-sum(base)/len(base):+.2f} [{blo:+.2f},{bhi:+.2f}] p={p:.3f}"
            line = f"{framing:<13}{n:>6}{sum(d)/len(d):>8.2f}  [{lo:.2f}, {hi:.2f}]{len(d):>5}{cmp}"
            print(line); lines.append(line)

    path = write_run("results", args.run_id, vars(args), scenario, rows)
    (path / "report.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"\napi calls: {runner.stats['api_calls']}  cache hits: {runner.stats['cache_hits']}  "
          f"errors: {runner.stats['errors']}")
    print(f"written to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
