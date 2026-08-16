#!/usr/bin/env python
"""Validate the checkers before scaling up (PROJECT.md build order, Friday).

Two modes:

  --tier1                Run the deterministic structural checker against the
                         hand-labeled fixture transcripts. No API calls.
                         Any disagreement is a checker bug: exits non-zero.

  --tier2 RUN LABELS     Compare the tier-2 prose judge against hand labels for
                         a run's transcripts and report Cohen's kappa. LABELS is
                         a JSONL file of {"index": int, "violation": bool}, where
                         index is the 0-based line number in trials.jsonl.
                         Emit a blank labeling sheet with --emit-sheet.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgap.checker import label_agreement, tier1_check, tier1_tool_check
from cgap.runner import Runner
from cgap.scenario import load_scenario

FIXTURES = Path(__file__).resolve().parents[1] / "tests/fixtures/tier1_labeled.jsonl"
TOOL_FIXTURES = Path(__file__).resolve().parents[1] / "tests/fixtures/tier1_tool_labeled.jsonl"


def run_tier1(path: Path) -> int:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    mismatches = []
    for row in rows:
        got = tier1_check(row["text"]).outcome
        if got != row["label"]:
            mismatches.append((row["id"], row["label"], got, row.get("note", "")))
    print(f"tier-1 structural checker (S1, field): "
          f"{len(rows) - len(mismatches)}/{len(rows)} agree with hand labels")
    for item_id, want, got, note in mismatches:
        print(f"  MISMATCH {item_id}: expected {want}, got {got}  ({note})")
    return 1 if mismatches else 0


def run_tier1_tools(path: Path, scenario_id: str, prompts: str,
                    variant: str | None = None) -> int:
    """Validate the agentic checker against the real scenario's allowlist."""
    scenario = load_scenario(scenario_id, prompts, variant)
    if not scenario.allowlist:
        print(f"scenario {scenario_id} has no allowlist; nothing to validate")
        return 1
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    mismatches = []
    for row in rows:
        got = tier1_tool_check(row["tool_calls"], scenario.allowlist).outcome
        if got != row["label"]:
            mismatches.append((row["id"], row["label"], got, row.get("note", "")))
    print(f"tier-1 structural checker ({scenario_id}, tool call): "
          f"{len(rows) - len(mismatches)}/{len(rows)} agree with hand labels")
    for item_id, want, got, note in mismatches:
        print(f"  MISMATCH {item_id}: expected {want}, got {got}  ({note})")
    return 1 if mismatches else 0


def load_trials(run_dir: Path) -> list[dict]:
    path = run_dir / "trials.jsonl"
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def emit_sheet(run_dir: Path, n: int, out: Path) -> int:
    trials = load_trials(run_dir)
    picked = trials[:n]
    with out.open("w", encoding="utf-8") as fh:
        for i, row in enumerate(picked):
            fh.write(
                json.dumps(
                    {
                        "index": i,
                        "violation": None,
                        "_response": row.get("response", ""),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    print(f"wrote {len(picked)} items to {out}; set each \"violation\" to true/false")
    return 0


def run_tier2(run_dir: Path, labels_path: Path, scenario_id: str, prompts: str,
              variant: str | None) -> int:
    trials = load_trials(run_dir)
    labels = [
        json.loads(l) for l in labels_path.read_text().splitlines() if l.strip()
    ]
    labels = [l for l in labels if l.get("violation") is not None]
    if not labels:
        print("no completed hand labels found", file=sys.stderr)
        return 1

    scenario = load_scenario(scenario_id, prompts, variant)
    runner = Runner()
    rubric = scenario.judge_rubric()
    from cgap.checker import judge_violation

    judge_labels, human_labels = [], []
    for item in labels:
        row = trials[item["index"]]
        verdict = judge_violation(runner.judge, rubric, row.get("response", ""))
        if "violation" not in verdict:
            print(f"  judge failed on index {item['index']}: {verdict}", file=sys.stderr)
            continue
        judge_labels.append(bool(verdict["violation"]))
        human_labels.append(bool(item["violation"]))

    stats = label_agreement(judge_labels, human_labels)
    print("tier-2 judge vs hand labels:")
    for key, value in stats.items():
        print(f"  {key}: {value:.3f}" if isinstance(value, float) else f"  {key}: {value}")
    if stats["cohens_kappa"] < 0.8:
        print("  WARNING: kappa < 0.80 -- do not promote this judge to primary DV")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier1", action="store_true")
    ap.add_argument("--fixtures", default=str(FIXTURES))
    ap.add_argument("--tier1-tools", action="store_true",
                    help="validate the agentic tool-call checker")
    ap.add_argument("--tool-fixtures", default=str(TOOL_FIXTURES))
    ap.add_argument("--tier2", nargs=2, metavar=("RUN_DIR", "LABELS"))
    ap.add_argument("--emit-sheet", nargs=2, metavar=("RUN_DIR", "OUT"))
    ap.add_argument("--sheet-n", type=int, default=50)
    ap.add_argument("--scenario", default="s1")
    ap.add_argument("--prompts", default="prompts")
    ap.add_argument("--variant", default=None)
    args = ap.parse_args()

    if args.emit_sheet:
        return emit_sheet(Path(args.emit_sheet[0]), args.sheet_n, Path(args.emit_sheet[1]))
    if args.tier2:
        return run_tier2(
            Path(args.tier2[0]), Path(args.tier2[1]), args.scenario, args.prompts,
            args.variant,
        )
    if args.tier1_tools:
        return run_tier1_tools(Path(args.tool_fixtures), args.scenario, args.prompts,
                               args.variant)
    return run_tier1(Path(args.fixtures))


if __name__ == "__main__":
    raise SystemExit(main())
