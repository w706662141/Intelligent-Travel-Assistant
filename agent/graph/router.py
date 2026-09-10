from langgraph.graph import END
from agent.graph.state import AgentStatus


def should_continue(state):
    status = state.get('status')

    if status in {
        AgentStatus.FAILED,
        AgentStatus.MAX_ITERATIONS,
        AgentStatus.COMPLETED
    }:
        return END

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END
