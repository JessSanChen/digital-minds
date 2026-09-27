"""Inspect entry point.

inspect eval policy_pressure/policy_pressure --model openai/gpt-4.1-mini
inspect eval policy_pressure/policy_pressure -T design=pilot -T limit_scenarios=5 ...
"""

from __future__ import annotations

from inspect_ai import Task, task
from inspect_ai.model import GenerateConfig
from inspect_ai.solver import generate

from .dataset import build_dataset
from .scorers import policy_scorer
from .solvers import attach_tools, self_report


@task
def policy_pressure(
    design: str = "core",
    scenarios: str | None = None,
    limit_scenarios: int | None = None,
) -> Task:
    """Agentic network-policy compliance under persona and peer pressure.

    Args:
        design: "core" (40 cells) or "pilot" (4 baseline cells).
        scenarios: comma-separated scenario ids to restrict to.
        limit_scenarios: use only the first N scenarios.
    """
    return Task(
        dataset=build_dataset(design, scenarios.split(",") if scenarios else None, limit_scenarios),
        solver=[attach_tools(), generate(tool_calls="loop"), self_report()],
        scorer=policy_scorer(),
        # Enough turns for fetch -> read -> answer plus a retry or two; an agent
        # still looping at the limit is scored on what it did.
        message_limit=16,
        config=GenerateConfig(max_tokens=1500),
        version=1,
    )
