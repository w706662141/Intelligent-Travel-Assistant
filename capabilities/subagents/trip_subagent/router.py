from langgraph.graph import END

from capabilities.subagents.trip_subagent.state import (
    TripSubAgentState,
)


def should_continue(
    state: TripSubAgentState,
):

    status = state.get(
        "status"
    )

    # ==========================================================
    # Failed
    # ==========================================================

    if status in {
        "failed",
        "max_iterations",
    }:

        return END

    # ==========================================================
    # 获取 Messages
    #
    # 这里只用于判断：
    #
    # 最后一个 Agent 是否产生 tool_calls。
    #
    # 不再把 messages 全量传给 LLM。
    # ==========================================================

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

    # ==========================================================
    # 有 Tool Call
    # ==========================================================

    if tool_calls:

        return "tools"

    # ==========================================================
    # 没有 Tool Call
    #
    # Agent 已经认为资源足够。
    #
    # 进入 Final LLM。
    # ==========================================================

    return "finalizer"