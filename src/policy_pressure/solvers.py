from __future__ import annotations

from inspect_ai.model import ChatMessageAssistant, ChatMessageTool, ChatMessageUser
from inspect_ai.solver import Generate, Solver, TaskState, solver
from inspect_ai.tool import ToolCallError
from inspect_ai.util import LimitExceededError, message_limit

from .dataset import conditions
from .tools import tools_for

# Store keys written by solvers and read by the scorer.
FINAL_ANSWER = "final_answer"
AGENT_TURN_END = "agent_turn_end"
SELF_REPORTED = "self_reported"
API_REFUSAL = "api_refusal"
HIT_LIMIT = "hit_limit"


@solver
def attach_tools() -> Solver:
    """Give the sample the tool for its affordance, bound to its scenario."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        state.tools = tools_for(state.metadata)
        return state

    return solve


@solver
def agent_loop(max_messages: int = 24) -> Solver:
    """The agent's tool loop, under a limit scoped to the loop only. A
    task-level message limit would end the whole solver chain, skipping the
    self-report (the pilot lost it in up to 12% of samples for some models,
    concentrated in long, violating episodes)."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        try:
            with message_limit(max_messages):
                state = await generate(state, tool_calls="loop")
        except LimitExceededError:
            state.store.set(HIT_LIMIT, True)
            # A final assistant turn may hold tool calls that were never run.
            # Answer them with an error so the conversation stays valid for the
            # self-report turn; the scorer only counts executed calls.
            last = state.messages[-1] if state.messages else None
            if isinstance(last, ChatMessageAssistant) and last.tool_calls:
                for call in last.tool_calls:
                    state.messages.append(
                        ChatMessageTool(
                            content="",
                            tool_call_id=call.id,
                            function=call.function,
                            error=ToolCallError("limit", "Not executed: step limit reached."),
                        )
                    )
        return state

    return solve


@solver
def self_report() -> Solver:
    """Record the agent's final answer, then (forbid condition only) ask it
    whether it contacted a non-approved host. Tool choice is set to "none" so
    the answer is a report, not another action. The tools stay attached:
    removing them changes the request prefix, and Anthropic then drops the
    model's earlier thinking blocks, so a reasoning model would answer
    without access to its own earlier reasoning (seen in the pilot)."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        # No final answer if the loop was cut off (the last output is a tool call).
        hit_limit = state.store.get(HIT_LIMIT, False)
        state.store.set(FINAL_ANSWER, "" if hit_limit or not state.output else state.output.completion)
        state.store.set(AGENT_TURN_END, len(state.messages))
        # A provider-side safety block (e.g. Anthropic's classifiers returning
        # stop_reason "refusal", which Inspect maps to "content_filter") ends
        # the episode before the model responds: not a behavioural outcome.
        refused = bool(state.output) and state.output.stop_reason == "content_filter"
        state.store.set(API_REFUSAL, refused)
        if refused:
            return state
        if state.metadata["policy"] != "forbid":
            return state
        state.messages.append(ChatMessageUser(content=conditions()["self_report"]))
        state.tool_choice = "none"
        state = await generate(state, tool_calls="none")
        state.store.set(SELF_REPORTED, True)
        return state

    return solve
