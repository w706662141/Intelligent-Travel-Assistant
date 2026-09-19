from langgraph.graph import END

from capabilities.subagents.trip_subagent.state import TripSubAgentState


def should_continue(
        state: TripSubAgentState,
):
    status = state.get("status")

    if status in {
        "failed",
        "max_iterations",
    }:
        return END

    last_message = state["messages"][-1]

    if getattr(
            last_message,
            "tool_calls",
            None,
    ):
        return "tools"

    return END