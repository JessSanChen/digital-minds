"""Run the eval across the model registry with Inspect's eval_set.

eval_set is resumable: re-running the same command skips completed
(task, model) logs and retries failed ones, so a crash or an exhausted API
quota costs nothing but a re-run.

    uv run python scripts/run_evals.py --group openai
    uv run python scripts/run_evals.py --group open --design pilot --log-dir logs/pilot
    uv run python scripts/run_evals.py --via-openrouter openai   # OpenAI models via OpenRouter, rest direct
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from dotenv import load_dotenv
from inspect_ai import eval_set
from inspect_ai.model import get_model

from policy_pressure.task import policy_pressure

ROOT = Path(__file__).resolve().parents[1]


def registry() -> dict:
    return yaml.safe_load((ROOT / "configs/models.yaml").read_text())


def models_for(groups: list[str], only: list[str] | None, via_openrouter: list[str] | None = None):
    """(model, epochs) for the requested groups. Closed models in a group listed
    in `via_openrouter` are routed through OpenRouter (an empty list = all)."""
    reg = registry()
    out = []
    for g in groups:
        for m in reg["groups"][g]:
            if only and m["model"] not in only:
                continue
            name = m["model"]
            reroute = via_openrouter is not None and (not via_openrouter or g in via_openrouter)
            if reroute and "openrouter" in m:
                name = f"openrouter/{m['openrouter']}"
            # Precision/tool routing constraints apply to open weights only: closed
            # models served via OpenRouter don't report a quantization, so the
            # filter would reject every provider.
            args = {"provider": reg["openrouter_provider"]} if g == "open" else {}
            out.append((get_model(name, **args), m.get("epochs", reg.get("default_epochs", 1))))
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--group", action="append", help="model group(s) from configs/models.yaml")
    p.add_argument("--model", action="append", help="restrict to these model strings")
    p.add_argument("--design", default="core")
    p.add_argument("--limit-scenarios", type=int)
    p.add_argument("--log-dir", default="logs/v2")
    p.add_argument("--max-connections", type=int, default=24)
    p.add_argument("--max-tasks", type=int, default=4, help="models evaluated concurrently")
    p.add_argument("--epochs", type=int, help="override the registry's per-model epochs (e.g. 1 for a pilot)")
    p.add_argument(
        "--max-sandboxes",
        type=int,
        default=None,
        help="concurrent Docker containers (Inspect default: 2 x CPUs)",
    )
    p.add_argument(
        "--via-openrouter",
        nargs="*",
        metavar="GROUP",
        help="route closed models through OpenRouter: all groups, or only the ones named",
    )
    args = p.parse_args()

    load_dotenv(ROOT / ".env")
    groups = args.group or list(registry()["groups"])
    models = models_for(groups, args.model, args.via_openrouter)
    # One eval_set per epoch count, each in its own subdirectory (eval_set
    # requires a consistent task configuration within a log directory).
    ok_all = True
    for epochs in sorted({e for _, e in models}):
        batch = [m for m, e in models if e == epochs]
        ok, _ = eval_set(
            policy_pressure(design=args.design, limit_scenarios=args.limit_scenarios),
            model=batch,
            epochs=args.epochs or epochs,
            log_dir=f"{args.log_dir}/epochs-{args.epochs or epochs}",
            max_connections=args.max_connections,
            max_sandboxes=args.max_sandboxes,
            max_tasks=args.max_tasks,
            retry_attempts=5,
            fail_on_error=0.05,
            display="plain",
        )
        ok_all = ok_all and ok
    raise SystemExit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
