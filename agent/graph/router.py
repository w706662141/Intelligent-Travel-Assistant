from langgraph.graph import END
from agent.graph.state import AgentStatus

TERMINAL_SUBAGENT_STATUSES = {
    AgentStatus.SUBAGENT_COMPLETED,
    AgentStatus.SUBAGENT_FAILED,
}

TERMINAL_TOOLS = {
    "delegate_trip_task",
}


def should_continue(state):

    print(
        "\n[ROUTER]"
    )

    print(
        "status=",
        state.get("status"),
    )

    print(
        "executed_tool_names=",
        state.get(
            "executed_tool_names"
        ),
    )

    messages = state.get(
        "messages",
        [],
    )

    if not messages:
        return END

    last_message = messages[-1]

    print(
        "last_message=",
        type(last_message).__name__,
    )

    print(
        "tool_calls=",
        getattr(
            last_message,
            "tool_calls",
            None,
        ),
    )

    status = state.get(
        "status"
    )

    # ==========================================
    # TripSubAgent 已经完成
    # ==========================================

    if status == (
        AgentStatus.SUBAGENT_COMPLETED
    ):
        return "passthrough"

    # ==========================================
    # TripSubAgent 执行失败
    # ==========================================

    if status == (
        AgentStatus.SUBAGENT_FAILED
    ):
        return "passthrough"

    # ==========================================
    # MainAgent 自身失败
    # ==========================================

    if status in {
        AgentStatus.FAILED,
        AgentStatus.MAX_ITERATIONS,
        AgentStatus.COMPLETED,
    }:
        return END

    # ==========================================
    # MainAgent Tool Calling
    # ==========================================

    tool_calls = getattr(
        last_message,
        "tool_calls",
        [],
    )

    if tool_calls:
        return "tools"

    # ==========================================
    # 普通对话直接结束
    # ==========================================

    return END


def route_after_tools(state):
    executed_tool_names = state.get(
        "executed_tool_names",
        []
    )

    # =========================================
    # TripSkill 是终止型 Tool
    # =========================================

    if any(
            name in TERMINAL_TOOLS
            for name in executed_tool_names
    ):
        return END

    # =========================================
    # 普通 Tool
    # =========================================

    return "agent"
