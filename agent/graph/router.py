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
        "\n[ROUTER]",
        "status=", state.get("status"),
        "executed_tool_names=", state.get("executed_tool_names"),
        "last_message=", type(state["messages"][-1]).__name__,
        "tool_calls=", getattr(
            state["messages"][-1],
            "tool_calls",
            None
        ),
    )

    status = state.get('status')

    if status in {
        AgentStatus.SUBAGENT_COMPLETED,
        AgentStatus.SUBAGENT_FAILED,
    }:
        return "passthrough"

    if status in {
        AgentStatus.FAILED,
        AgentStatus.MAX_ITERATIONS,
        AgentStatus.COMPLETED
    }:
        return END

    executed_tool_names = state.get(
        "executed_tool_names",
        []
    )

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

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
