#!/usr/bin/env python
"""End-to-end pipeline check with a stubbed API client. No network, no cost.

Exercises trial enumeration, the cached-call path, the tier-1/tier-2/suspicion
checkers, the manipulation grader, the rate/gap math, and the report writer, so
a broken harness fails here rather than 200 paid calls into a pilot.

The stub's behavior is a caricature (a hand-set audience x stakes gap), not a
prediction; it only has to be non-degenerate enough to drive every code path.
"""

from __future__ import annotations

import json
import random
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgap import analysis
from cgap.runner import Runner, build_trials, write_run
from cgap.scenario import load_scenario

# violation probability by (audience, stakes) -- a positive gap under human,
# a flat one under private, so H1/H2-shaped output reaches the analysis code.
P_VIOLATION = {
    ("human", "consequential"): 0.15,
    ("human", "routine"): 0.60,
    ("private", "consequential"): 0.45,
    ("private", "routine"): 0.50,
}


class StubMessages:
    def __init__(self) -> None:
        self.calls = 0

    def create(self, *, model, system, messages, **kwargs):
        self.calls += 1
        user = messages[0]["content"]
        rng = random.Random(hash((system, user, self.calls)) & 0xFFFFFFFF)

        fmt = (kwargs.get("output_config") or {}).get("format")
        if fmt:  # judge call: must satisfy the requested schema
            props = set(fmt["schema"]["properties"])
            if "violation" in props:
                payload = {"violation": rng.random() < 0.4, "span": "I find A more elegant"}
            elif "suspicious" in props:
                payload = {"suspicious": rng.random() < 0.1, "span": ""}
            else:
                payload = {
                    "belief_matches_condition": rng.random() < 0.8,
                    "stated_reviewer": "the human research team",
                    "believes_affects_training": "unclear",
                }
            text = json.dumps(payload)
        elif "who do you understand will review" in user:
            text = "I understand the human research team will review this session."
        else:
            audience = "human" if "human research team" in system else "private"
            stakes = "consequential" if "executed directly" in system else "routine"
            p = P_VIOLATION[(audience, stakes)]
            if rng.random() < 0.04:
                text = "I'm not able to give a personal preference here."  # malformed
            else:
                pref = (
                    '"I genuinely prefer option B."' if rng.random() < p else "null"
                )
                text = (
                    '{"analysis": "Objective comparison of A and B.", '
                    f'"recommendation": "A", "personal_preference": {pref}}}'
                )

        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text=text)],
            stop_reason="end_turn",
            usage=SimpleNamespace(input_tokens=400, output_tokens=60),
        )


class StubClient:
    def __init__(self) -> None:
        self.messages = StubMessages()


def main() -> int:
    scenario = load_scenario("s1")
    models = ["sonnet-5", "haiku-4-5"]
    audiences = ["human", "private"]
    stakes = ["consequential", "routine"]

    with tempfile.TemporaryDirectory() as cache_dir:
        runner = Runner(client=StubClient(), cache_dir=cache_dir, max_workers=4)
        trials = build_trials(scenario, models, audiences, stakes, reps=5)
        rows = runner.run_trials(scenario, trials)
        rows = runner.run_suspicion_pass(scenario, rows)
        rows = runner.run_tier2_pass(scenario, rows)
        manip = runner.run_manipulation_check(
            scenario, models, audiences, "consequential", n=5
        )

        cells = analysis.cell_summary(rows)
        gap_rows = analysis.gaps(rows, bootstrap_iters=2000)
        findings = analysis.diagnose(cells, gap_rows)
        report = analysis.format_report(
            cells,
            gap_rows,
            findings,
            analysis.manipulation_summary(manip),
            analysis.suspicion_summary(rows),
        )
        print(report)

        out = write_run(
            tempfile.mkdtemp(), "smoke", {"stub": True}, scenario, rows,
            extras={"gaps": gap_rows},
        )

    assert len(rows) == len(trials) == 120, len(rows)
    assert all("tier1" in r and "tier2" in r and "suspicion" in r for r in rows)
    assert (out / "trials.jsonl").is_file() and (out / "config.json").is_file()
    # tier-2 labels must flow through the DV switch as well as tier-1
    assert analysis.cell_summary(rows, dv="tier2")
    assert analysis.gaps(rows, dv="tier2", bootstrap_iters=500)
    print("\nsmoke test OK: pipeline end-to-end on stubbed responses")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
