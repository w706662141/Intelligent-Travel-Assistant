from langgraph.graph import END
from agent.graph.state import AgentStatus, TaskMode


def should_continue(state):
    status = state.get('status')

    if status in {
        AgentStatus.FAILED,
        AgentStatus.MAX_ITERATIONS,
        AgentStatus.COMPLETED
    }:
        return END

    last_message = state["messages"][-1]

    task_mode = state.get("task_mode")
    last_tool_name = state.get("last_tool_name")

    if task_mode == TaskMode.TRAVEL_PLANNING:

        if (
            last_tool_name == "trip_plan"
            and not last_message.tool_calls
        ):
            return END

    if last_message.tool_calls:
        return "tools"

    return END
