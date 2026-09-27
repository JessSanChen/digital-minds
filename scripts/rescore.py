"""Re-score existing logs with the current scorer (no model calls).

Scores are derived from transcripts, so a scorer fix is applied to finished runs
with Inspect's `score()` rather than by re-running. Also reports how many
samples the fix changed, and how many of those had a transcript the old
extractor could have affected (the simulated tool's response depends on the
hosts extracted, so a phantom host can change what the model saw).

Samples where any tool response would differ under the current extractor are
written to <log_dir>/env_affected.json and excluded by analysis/analyze.py:
their scores can be fixed, but the transcript after that response cannot.

    uv run python scripts/rescore.py logs/v1
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from inspect_ai import score
from inspect_ai.log import list_eval_logs, read_eval_log, write_eval_log
from inspect_ai.model import ChatMessageAssistant

from policy_pressure import hosts as H
from policy_pressure.scorers import policy_scorer
from policy_pressure.tools import resolve

# The extractor as first run: bare hostname-shaped literals counted without a TLD check.
_V1_NET_RE = re.compile(r"\b(requests|urllib|httpx|http\.client|aiohttp|socket|urlopen|curl|wget)\b")
_V1_HOST_RE = re.compile(r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z0-9-]{1,62}$")


def v1_hosts_in_code(code: str) -> set[str]:
    hosts = H.hosts_in_code(code)
    try:
        lits = H._string_literals(code)
    except SyntaxError:
        lits = [code]
    if _V1_NET_RE.search(code):
        hosts |= {lit.strip().lower() for lit in lits if _V1_HOST_RE.match(lit.strip().lower())}
    return hosts


def env_affected(sample) -> bool:
    """Would any run_python response in this transcript differ between the
    first-run extractor and the current one?"""
    for m in sample.messages:
        if isinstance(m, ChatMessageAssistant) and m.tool_calls:
            for tc in m.tool_calls:
                if tc.function == "run_python":
                    code = str(tc.arguments.get("code", ""))
                    if resolve(v1_hosts_in_code(code), sample.metadata) != resolve(
                        H.hosts_in_code(code), sample.metadata
                    ):
                        return True
    return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("log_dir")
    args = ap.parse_args()
    report = {}
    out = Path(args.log_dir) / "env_affected.json"
    affected = json.loads(out.read_text()) if out.exists() else {}
    for info in list_eval_logs(args.log_dir):
        log = read_eval_log(info)
        if log.status != "success":
            print(f"skip (status={log.status}): {info.name}")
            continue
        before = {s.id: s.scores["policy_scorer"] for s in log.samples if s.scores}
        new = score(log, scorers=[policy_scorer()], action="overwrite", display="none")
        changed = hosts_changed = 0
        for s in new.samples:
            old, cur = before.get(s.id), s.scores["policy_scorer"]
            if old is None:
                continue
            shared = sorted(set(old.value) & set(cur.value))
            if json.dumps([old.value[k] for k in shared]) != json.dumps([cur.value[k] for k in shared]):
                changed += 1
            if set(old.metadata["contacted"]) != set(cur.metadata["contacted"]):
                hosts_changed += 1
        # Only task v1 simulated run_python output from extracted hosts; from
        # v2 code really runs, so the extractor cannot change what a model saw.
        v1 = str(log.eval.task_version) == "1"
        ids = sorted(s.id for s in new.samples if v1 and env_affected(s))
        affected[log.eval.model] = ids
        write_eval_log(new, info.name)
        report[log.eval.model] = {
            "samples": len(new.samples),
            "score_changed": changed,
            "hosts_changed": hosts_changed,
            "env_affected": len(ids),
        }
        print(log.eval.model, report[log.eval.model])
    out.write_text(json.dumps(affected, indent=1) + "\n")
    return report


if __name__ == "__main__":
    main()
