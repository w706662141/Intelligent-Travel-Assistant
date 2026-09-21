from langgraph.graph import StateGraph, START, END

from agent.graph.nodes.agent_node import AgentNodes
from agent.graph.nodes.passthrough_node import MainAgentPassthroughNode
from agent.graph.nodes.tool_node import ToolNodes
from agent.graph.router import should_continue
from agent.graph.state import AgentState


class TravelAgentGraph:
    def __init__(
            self,
            model,
            tool_executor,
    ):
        self.agent_nodes = AgentNodes(model)
        self.tool_nodes = ToolNodes(tool_executor)
        self.passthrough_node = (
            MainAgentPassthroughNode()
        )

    def build(self):
        graph = StateGraph(
            AgentState
        )

        graph.add_node(
            'agent',
            self.agent_nodes.agent
        )

        graph.add_node(
            'tools',
            self.tool_nodes.execute
        )

        graph.add_node(
            "passthrough",
            self.passthrough_node.passthrough,
        )

        graph.add_edge(
            START,
            'agent'
        )

        # ==========================================
        # Agent Router
        # ==========================================

        graph.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",

                "passthrough": (
                    "passthrough"
                ),

                END: END,
            },
        )


        # ==========================================
        # 普通 Tool
        #
        # 只有普通 Tool 才重新进入 Agent
        # ==========================================

        graph.add_conditional_edges(
            "tools",
            lambda state: (
                "passthrough"
                if state.get(
                    "status"
                ) in {
                    "subagent_completed",
                    "subagent_failed",
                }
                else "agent"
            ),
            {
                "agent": "agent",

                "passthrough": (
                    "passthrough"
                ),
            },
        )

        # ==========================================
        # Passthrough
        # ==========================================

        graph.add_edge(
            "passthrough",
            END,
        )

        return graph.compile()
