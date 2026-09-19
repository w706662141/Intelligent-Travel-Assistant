from langchain_core.messages import SystemMessage
from langgraph.graph import (
    StateGraph,
    START,
    END,
)
from capabilities.subagents.trip_subagent.router import should_continue
from capabilities.subagents.trip_subagent.nodes.trip_agent_node import TripAgentNodes
from capabilities.subagents.trip_subagent.nodes.trip_tool_node import TripToolNodes
from capabilities.subagents.trip_subagent.state import (
    TripSubAgentState,
)


class TripSubAgentGraph:

    def __init__(
            self,
            model,
            tools,
            max_iterations: int = 15,
    ):
        self.trip_agent_nodes = TripAgentNodes(model, max_iterations)
        self.trip_tool_nodes = TripToolNodes(tools)

    def build(self):
        graph = StateGraph(
            TripSubAgentState
        )

        graph.add_node(
            "agent",
            self.trip_agent_nodes,
        )

        graph.add_node(
            "tools",
            self.trip_tool_nodes,
        )

        graph.add_edge(
            START,
            "agent",
        )

        graph.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                END: END,
            },
        )

        graph.add_edge(
            "tools",
            "agent",
        )

        return graph.compile()
