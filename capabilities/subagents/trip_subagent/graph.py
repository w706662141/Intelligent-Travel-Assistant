from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from capabilities.subagents.trip_subagent.router import (
    should_continue,
)

from capabilities.subagents.trip_subagent.nodes.trip_agent_node import (
    TripAgentNodes,
)

from capabilities.subagents.trip_subagent.nodes.trip_tool_node import (
    TripToolNodes,
)

from capabilities.subagents.trip_subagent.nodes.trip_finalizer_node import (
    TripFinalizerNode,
)

from capabilities.subagents.trip_subagent.state import (
    TripSubAgentState,
)


class TripSubAgentGraph:

    def __init__(
        self,
        agent_model,
        final_model,
        tools,
        max_iterations: int = 15,
        agent_llm_timeout: int = 120,
        final_llm_timeout: int = 60,
    ):
        self.trip_agent_nodes = TripAgentNodes(
            model=agent_model,
            max_iterations=max_iterations,
            llm_timeout=agent_llm_timeout,
        )

        self.trip_tool_nodes = TripToolNodes(
            tools=tools,
        )

        self.finalizer_node = TripFinalizerNode(
            model=final_model,
            llm_timeout=final_llm_timeout,
        )

    def build(self):

        graph = StateGraph(
            TripSubAgentState
        )

        graph.add_node(
            "agent",
            self.trip_agent_nodes.agent_node,
        )

        graph.add_node(
            "tools",
            self.trip_tool_nodes.tool_node,
        )

        graph.add_node(
            "finalizer",
            self.finalizer_node.finalize,
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
                "finalizer": "finalizer",
                END: END,
            },
        )

        graph.add_edge(
            "tools",
            "agent",
        )

        graph.add_edge(
            "finalizer",
            END,
        )

        return graph.compile()
