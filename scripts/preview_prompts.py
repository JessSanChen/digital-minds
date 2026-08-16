#!/usr/bin/env python
"""Print assembled prompts for a scenario (no API calls).

Use this to eyeball what the model will actually see, and to confirm the
minimal-pair property: for a fixed stakes clause and task, the only text that
differs across audiences is the audience clause.
"""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgap.scenario import load_scenario


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="s1")
    ap.add_argument("--prompts", default="prompts")
    ap.add_argument("--variant", default=None)
    ap.add_argument("--audience", default=None, help="print just this cell")
    ap.add_argument("--stakes", default=None)
    ap.add_argument("--task", default=None)
    ap.add_argument("--diff", action="store_true", help="minimal-pair diff across audiences")
    args = ap.parse_args()

    sc = load_scenario(args.scenario, args.prompts, args.variant)
    print(f"scenario {sc.id}: {len(sc.audiences)} audiences x {len(sc.stakes)} stakes "
          f"x {len(sc.tasks)} tasks")
    print(f"audiences: {sorted(sc.audiences)}")
    print(f"stakes:    {sorted(sc.stakes)}")
    print(f"tasks:     {sc.task_ids()}")
    print()

    if args.diff:
        keys = sorted(sc.audiences)
        stakes = args.stakes or keys and sorted(sc.stakes)[0]
        ref = sc.system_prompt(keys[0], stakes).splitlines()
        for other in keys[1:]:
            cmp = sc.system_prompt(other, stakes).splitlines()
            print(f"--- minimal pair: {keys[0]} vs {other} (stakes={stakes}) ---")
            for line in difflib.unified_diff(ref, cmp, lineterm="", n=0):
                if line.startswith(("---", "+++")):
                    continue
                print(line)
            print()
        return 0

    audiences = [args.audience] if args.audience else sorted(sc.audiences)
    stakes = [args.stakes] if args.stakes else sorted(sc.stakes)
    tasks = [args.task] if args.task else sc.task_ids()[:1]
    for aud in audiences:
        for stk in stakes:
            for task_id in tasks:
                print("=" * 72)
                print(f"AUDIENCE={aud}  STAKES={stk}  TASK={task_id}")
                print("=" * 72)
                print("--- system ---")
                print(sc.system_prompt(aud, stk))
                print("--- user ---")
                print(sc.task(task_id).user)
                print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
