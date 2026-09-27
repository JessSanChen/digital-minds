from __future__ import annotations

from inspect_ai.model import ChatMessageUser
from inspect_ai.solver import Generate, Solver, TaskState, solver

from .dataset import conditions
from .tools import tools_for

# Store keys written by solvers and read by the scorer.
FINAL_ANSWER = "final_answer"
AGENT_TURN_END = "agent_turn_end"
SELF_REPORTED = "self_reported"


@solver
def attach_tools() -> Solver:
    """Give the sample the tool for its affordance, bound to its scenario."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        state.tools = tools_for(state.metadata)
        return state

    return solve


@solver
def self_report() -> Solver:
    """Record the agent's final answer, then (forbid condition only) ask it
    whether it contacted a non-approved host. Tools are removed so the answer
    is a report, not another action."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        state.store.set(FINAL_ANSWER, state.output.completion if state.output else "")
        state.store.set(AGENT_TURN_END, len(state.messages))
        if state.metadata["policy"] != "forbid":
            return state
        state.messages.append(ChatMessageUser(content=conditions()["self_report"]))
        state.tools = []
        state = await generate(state, tool_calls="none")
        state.store.set(SELF_REPORTED, True)
        return state

    return solve
