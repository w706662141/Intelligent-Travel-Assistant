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
        model,
        tools,
        max_iterations: int = 15,
        agent_llm_timeout: int = 120,
    ):
        # ==================================================
        # Agent
        # ==================================================

        self.trip_agent_nodes = TripAgentNodes(
            model=model,
            max_iterations=max_iterations,
            llm_timeout=agent_llm_timeout,
        )

        # ==================================================
        # Tools
        # ==================================================

        self.trip_tool_nodes = TripToolNodes(
            tools=tools,
        )

        # ==================================================
        # Finalizer
        #
        # 不需要 model
        # ==================================================

        self.finalizer_node = TripFinalizerNode()

    def build(self):

        graph = StateGraph(
            TripSubAgentState
        )

        # ==================================================
        # Nodes
        # ==================================================

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

        # ==================================================
        # START
        # ==================================================

        graph.add_edge(
            START,
            "agent",
        )

        # ==================================================
        # Agent Router
        # ==================================================

        graph.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                "finalizer": "finalizer",
                END: END,
            },
        )

        # ==================================================
        # Tool → Agent
        # ==================================================

        graph.add_edge(
            "tools",
            "agent",
        )

        # ==================================================
        # Finalizer → END
        # ==================================================

        graph.add_edge(
            "finalizer",
            END,
        )

        return graph.compile()