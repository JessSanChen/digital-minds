#!/usr/bin/env python
"""Run a pilot (or any cell subset) of the audience x stakes matrix.

Defaults follow the Friday pilot in PROJECT.md: 2 models, 2 audiences
(human vs private -- the pair the manipulation check must distinguish),
2 stakes, reasoning OFF, plus the mandatory manipulation check and the
suspicion pass.

Every run writes results/<run_id>/ with the trial-level records, the config,
the hashes of every prompt file that produced it, and the report. Keep the
directories: the progression from weak to working is part of the methods story.
"""

from __future__ import annotations

import argparse
import itertools
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgap import analysis
from cgap.models import subject
from cgap.runner import Runner, build_trials, write_run
from cgap.scenario import load_scenario


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="s1")
    ap.add_argument("--prompts", default="prompts")
    ap.add_argument("--variant", default=None, help="prompt overlay directory name")
    ap.add_argument("--models", default="sonnet-5,haiku-4-5")
    ap.add_argument("--audiences", default="human,private")
    ap.add_argument("--stakes", default="consequential,routine")
    ap.add_argument("--tasks", default=None, help="comma-separated task ids")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--reasoning", default="off", choices=["off", "on"])
    ap.add_argument("--manip-n", type=int, default=5, help="calls per audience per model")
    ap.add_argument("--no-manip", action="store_true")
    ap.add_argument("--manip-dimension", default="audience",
                    choices=["audience", "stakes"])
    ap.add_argument("--no-suspicion", action="store_true")
    ap.add_argument("--tier2", action="store_true", help="also run the prose judge")
    ap.add_argument("--dv", default="tier1", choices=["tier1", "tier2"])
    ap.add_argument("--out", default="results")
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--cache", default=".cache/responses")
    args = ap.parse_args()

    scenario = load_scenario(args.scenario, args.prompts, args.variant)
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    audiences = [a.strip() for a in args.audiences.split(",") if a.strip()]
    stakes = [s.strip() for s in args.stakes.split(",") if s.strip()]
    tasks = [t.strip() for t in args.tasks.split(",")] if args.tasks else None

    trials = build_trials(
        scenario, models, audiences, stakes, args.reps, args.reasoning, tasks
    )
    run_id = args.run_id or time.strftime("%Y%m%d-%H%M%S") + (
        f"-{args.variant}" if args.variant else "-base"
    )

    print(f"run {run_id}: {len(trials)} subject trials "
          f"({len(models)} models x {len(audiences)} audiences x {len(stakes)} stakes "
          f"x {len(tasks or scenario.task_ids())} tasks x {args.reps} reps), "
          f"reasoning={args.reasoning}")

    runner = Runner(cache_dir=args.cache, max_workers=args.workers)

    # Preflight: a free token count fails fast on bad or missing credentials,
    # rather than turning every trial into an identical auth error.
    try:
        if subject(models[0]).provider == "anthropic":
            runner.client.messages.count_tokens(
                model=subject(models[0]).id,
                messages=[{"role": "user", "content": "preflight"}],
            )
    except Exception as exc:
        print(
            f"credential preflight failed ({type(exc).__name__}: {exc}).\n"
            "Set credentials first, e.g.  export ANTHROPIC_API_KEY=sk-ant-...\n"
            "No trials were run.",
            file=sys.stderr,
        )
        return 2

    done = itertools.count(1)
    lock = threading.Lock()

    def tick():
        with lock:
            i = next(done)
            if i % 20 == 0 or i == len(trials):
                print(f"  {i}/{len(trials)} trials", flush=True)

    rows = runner.run_trials(scenario, trials, progress=tick)

    if not args.no_suspicion:
        print("suspicion pass...", flush=True)
        rows = runner.run_suspicion_pass(scenario, rows)
    if args.tier2:
        print("tier-2 prose judge pass...", flush=True)
        rows = runner.run_tier2_pass(scenario, rows)

    manip_rows = []
    if not args.no_manip:
        print("manipulation check mini-run...", flush=True)
        manip_rows = runner.run_manipulation_check(
            scenario,
            models,
            audiences,
            stakes,
            args.manip_n,
            args.reasoning,
            dimension=args.manip_dimension,
        )

    cells = analysis.cell_summary(rows, dv=args.dv)
    gap_rows = analysis.gaps(rows, dv=args.dv)
    findings = analysis.diagnose(cells, gap_rows)
    manip_summary = analysis.manipulation_summary(manip_rows) if manip_rows else []
    susp_summary = analysis.suspicion_summary(rows) if not args.no_suspicion else []

    report = analysis.format_report(
        cells, gap_rows, findings, manip_summary, susp_summary, dv=args.dv
    )

    errors = [r for r in rows if r.get("error")]
    path = write_run(
        args.out,
        run_id,
        vars(args),
        scenario,
        rows,
        extras={
            "cells": [cells[k] for k in sorted(cells)],
            "gaps": gap_rows,
            "findings": findings,
            "manipulation": {"rows": manip_rows, "summary": manip_summary},
            "suspicion": susp_summary,
            "run_stats": {**runner.stats, "trial_errors": len(errors)},
        },
    )
    (path / "report.txt").write_text(report, encoding="utf-8")

    print()
    print(report)
    print()
    print(f"api calls: {runner.stats['api_calls']}  cache hits: {runner.stats['cache_hits']}  "
          f"errors: {runner.stats['errors']}")
    if errors:
        print(f"first error: {errors[0]['error']}")
    print(f"written to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
