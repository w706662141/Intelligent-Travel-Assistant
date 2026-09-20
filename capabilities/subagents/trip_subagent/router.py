from langgraph.graph import END

from capabilities.subagents.trip_subagent.state import (
    TripSubAgentState,
)


def should_continue(
    state: TripSubAgentState,
):

    status = state.get("status")

    if status in {
        "failed",
        "max_iterations",
    }:
        return END

    messages = state.get(
        "messages",
        []
    )

    if not messages:
        return "finalizer"

    last_message = messages[-1]

    tool_calls = getattr(
        last_message,
        "tool_calls",
        None,
    )

    if tool_calls:
        return "tools"

    # Agent 已经认为信息足够
    # 不再继续 Tool Calling
    # 交给 Finalizer 生成结构化结果
    return "finalizer"