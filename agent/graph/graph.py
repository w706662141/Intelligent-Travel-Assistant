from langgraph.graph import StateGraph, START, END

from agent.graph.nodes.agent_node import AgentNodes
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

        graph.add_edge(
            START,
            'agent'
        )

        graph.add_conditional_edges(
            'agent',
            should_continue,
            {
                'tools': 'tools',
                END: END
            }
        )

        graph.add_edge(
            'tools',
            'agent'
        )

        return graph.compile()
