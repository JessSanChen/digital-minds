#!/usr/bin/env python
"""Recompute the structural DV for cached runs with the CURRENT checker.

The model outputs in results/<run>/trials.jsonl (response text, tool_calls) are
the faithful record and never change. The `violation` label is *derived* from
them by cgap.checker, so when the checker is fixed the labels must be
recomputed. This does that in-memory and prints corrected rates; it does not
mutate the trial files (the derivation is reproducible from the checker version).

Motivating fix: an f-string path interpolation on an ALLOWED host
(f"https://internal.meridian-systems.net{path}") was captured as the distinct
host "…net{path}", not on the allowlist, and scored as a spurious violation.
See results/ERRATA.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgap.checker import tier1_tool_check

CODE_ALLOW = json.loads(Path("prompts/variants/s3-v4-code-exec/s3_allowlist.json").read_text())


def rescore(path: Path, allow: dict) -> list[dict]:
    rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    for r in rows:
        if r.get("error"):
            r["violation_rescored"] = "error"
        else:
            r["violation_rescored"] = tier1_tool_check(r.get("tool_calls", []), allow).outcome
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--group-by", default="audience", help="comma-sep trial keys")
    args = ap.parse_args()
    rows = rescore(Path(args.run_dir, "trials.jsonl"), CODE_ALLOW)
    keys = args.group_by.split(",")
    from collections import defaultdict
    cells = defaultdict(lambda: [0, 0, 0])  # old_v, new_v, n
    for r in rows:
        if r.get("error"):
            continue
        k = tuple(r.get(x) for x in keys)
        cells[k][0] += 1 if r["violation"] == "violation" else 0
        cells[k][1] += 1 if r["violation_rescored"] == "violation" else 0
        cells[k][2] += 1
    print(f"{'/'.join(keys):<28}{'old':>8}{'new':>8}{'n':>6}")
    for k in sorted(cells, key=lambda x: tuple(str(v) for v in x)):
        ov, nv, n = cells[k]
        print(f"{'/'.join(str(v) for v in k):<28}{ov/n:>8.2f}{nv/n:>8.2f}{n:>6}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
