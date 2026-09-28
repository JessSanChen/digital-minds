"""Pre-flight diagnostics for a pilot run: is every model measurable?

    uv run python analysis/pilot_check.py logs/pilot-v2

Per model, flags the things that would make the full run's numbers
uninterpretable or wasteful:
  errors         samples that errored (provider failures, bad requests)
  limit          samples that hit the message limit (looping, env confusion)
  empty          no final answer to the user
  tool_use       share of samples with at least one tool call
  capability     permit: share that fetched the target (should be ~1)
  violation      forbid: share with a non-approved request
  saw|fetch      given a target fetch, share where the payload reached the model
                 (low = the model's parsing code crashed on the response)
  delivered      given the model saw the payload, share that delivered the marker
  report?        forbid: self-reports that were not a parseable YES/NO
  static!=rt     code samples where static and runtime host sets disagree
  blocked        provider safety layer stopped the episode (stop_reason content_filter)
  memory         final answer contains the requested fact without fetching it
  misclass       violators: listed the host but gave verdict NO
  tokens         total tokens, to extrapolate cost to the full design
"""

from __future__ import annotations

import sys

import pandas as pd
from inspect_ai.log import list_eval_logs, read_eval_log


def row(log) -> dict:
    samples = log.samples or []
    scored = [s for s in samples if s.scores and "policy_scorer" in s.scores]
    frame = pd.DataFrame(
        [
            {
                **s.metadata,
                **s.scores["policy_scorer"].value,
                **{
                    k: s.scores["policy_scorer"].metadata.get(k)
                    for k in (
                        "final_answer",
                        "self_report",
                        "fetched_target",
                        "saw_payload",
                        "answered_without_fetch",
                    )
                },
                "calls": s.scores["policy_scorer"].metadata["n_tool_calls"],
                "limit": s.limit is not None or bool(s.scores["policy_scorer"].metadata.get("hit_limit")),
                "blocked": any(
                    e.event == "model" and e.output and e.output.stop_reason == "content_filter"
                    for e in s.events
                ),
                "disagree": (
                    s.metadata["affordance"] == "code"
                    and set(s.scores["policy_scorer"].metadata["runtime_hosts"])
                    != set(s.scores["policy_scorer"].metadata.get("static_hosts", []))
                ),
            }
            for s in scored
        ]
    )
    usage = sum(u.total_tokens for u in log.stats.model_usage.values()) if log.stats else 0
    if frame.empty:
        return {"model": log.eval.model, "status": log.status, "n": len(samples), "errors": len(samples)}
    f, p = frame[frame.policy == "forbid"], frame[frame.policy == "permit"]
    return {
        "model": log.eval.model.removeprefix("openrouter/"),
        "status": log.status,
        "n": len(samples),
        "errors": sum(1 for s in samples if s.error),
        "limit": int(frame["limit"].sum()),
        "empty": int((frame.final_answer.str.strip() == "").sum()),
        "tool_use": round((frame.calls > 0).mean(), 2),
        "cap_named": round(p[p.affordance == "named"].external_call.mean(), 2),
        "cap_code": round(p[p.affordance == "code"].external_call.mean(), 2),
        "viol_named": round(f[f.affordance == "named"].violation.mean(), 2),
        "viol_code": round(f[f.affordance == "code"].violation.mean(), 2),
        "saw|fetch": round(frame[frame.fetched_target == True].saw_payload.astype(float).mean(), 2),  # noqa: E712
        "delivered": round(frame.delivered.mean(), 2),
        "report?": int((f.self_report == "unclear").sum()),
        "blocked": int(frame.blocked.sum()),
        "memory": int(frame.answered_without_fetch.fillna(False).astype(bool).sum()),
        "misclass": round(frame["misclassified"].mean(), 2) if "misclassified" in frame else float("nan"),
        "static!=rt": int(frame.disagree.sum()),
        "tokens": usage,
    }


def main() -> None:
    log_dir = sys.argv[1] if len(sys.argv) > 1 else "logs/pilot-v2"
    logs = [read_eval_log(info) for info in list_eval_logs(log_dir)]
    # when a run was resumed, keep the newest log per model
    latest = {}
    for log in sorted(logs, key=lambda x: x.eval.created):
        latest[log.eval.model] = log
    rows = [row(log) for log in latest.values()]
    df = pd.DataFrame(rows).sort_values("model")
    pd.set_option("display.width", 250)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
