"""Inspect entry point.

inspect eval policy_pressure/policy_pressure --model openai/gpt-4.1-mini
inspect eval policy_pressure/policy_pressure -T design=pilot -T limit_scenarios=5 ...
"""

from __future__ import annotations

from inspect_ai import Task, task
from inspect_ai.model import GenerateConfig

from .dataset import build_dataset
from .scorers import policy_scorer
from .solvers import agent_loop, attach_tools, self_report


@task
def policy_pressure(
    design: str = "core",
    scenarios: str | list[str] | None = None,
    limit_scenarios: int | None = None,
) -> Task:
    """Agentic network-policy compliance under persona and peer pressure.

    Args:
        design: "core" (40 cells) or "pilot" (4 baseline cells).
        scenarios: scenario ids to restrict to (a list, or a comma-separated string;
            the Inspect CLI turns `-T scenarios=a,b` into a list).
        limit_scenarios: use only the first N scenarios.
    """
    return Task(
        dataset=build_dataset(
            design, scenarios.split(",") if isinstance(scenarios, str) else scenarios, limit_scenarios
        ),
        solver=[attach_tools(), agent_loop(max_messages=24), self_report()],
        scorer=policy_scorer(),
        # The agent loop has its own scoped limit (agent_loop); this is only a
        # safety net above it that still leaves room for the self-report turn.
        message_limit=40,
        # Held equal across models instead of each provider's default.
        # 3000 leaves reasoning models room to think and still answer (1500 cut
        # off a few pilot answers, including self-reports).
        config=GenerateConfig(max_tokens=3000, temperature=1.0),
        version=4,
    )
