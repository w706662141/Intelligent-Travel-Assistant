from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI


from agent.graph.graph import TravelAgentGraph
from agent.graph.state import AgentStatus
from capabilities.prompts.system import TRAVEL_AGENT_SYSTEM_PROMPT
from capabilities.tools.manager.tool_registry import ToolRegistry


class ReActAgent:

    def __init__(
            self,
            model: ChatOpenAI,
            tool_registry: ToolRegistry,
            tool_executor,
            max_iterations: int = 10):
        self.tool_registry = tool_registry
        self.tool_executor = tool_executor

        tools = self.tool_registry.get_all()
        # tools=[self.tool_registry.get('trip_plan')]

        self.model = model.bind_tools(tools)

        # ==========================================
        # 创建 Agent Loop
        # ==========================================
        self.max_iterations = max_iterations

        self.graph = TravelAgentGraph(
            model=self.model,
            tool_executor=self.tool_executor,
        ).build()

    async def run(self, user_input: str):

        result = await self.graph.ainvoke(
            {
                "messages": [
                    SystemMessage(
                        content=TRAVEL_AGENT_SYSTEM_PROMPT
                    ),
                    HumanMessage(
                        content=user_input
                    ),
                ],

                "iteration": 0,

                "max_iterations": self.max_iterations,

                "status": AgentStatus.RUNNING,

                "error": None,

                "tool_call_count": 0,

                "tool_result_count": 0,

                "tool_error_count": 0,

                "retry_count": 0,
            }
        )

        if result["status"] == "failed":
            return (
                "抱歉，任务执行过程中出现了问题："
                f"{result['error']}"
            )

        if result["status"] == "max_iterations":
            return (
                "抱歉，我尝试了多次操作，"
                "但仍然没有完成这个任务。"
            )

        return result["messages"][-1].content

    #     self.loop = AgentLoop(
    #         self.model,
    #         self.tool_executor,
    #         self.max_iterations
    #     )
    #
    # async def run(
    #         self,
    #         user_input: str) -> str:
    #     state = AgentState(
    #         messages=[
    #             SystemMessage(
    #                 content=TRAVEL_AGENT_SYSTEM_PROMPT
    #             ),
    #             HumanMessage(
    #                 content=user_input
    #             ),
    #         ],
    #         max_iterations=self.max_iterations
    #     )
    #
    #     state = await self.loop.run(
    #         state
    #     )
    #
    #     if state.status == "completed":
    #         return state.final_answer or ""
    #
    #     if state.status == "max_iterations":
    #         return (
    #             "抱歉，我尝试了多次操作，"
    #             "但仍然没有完成这个任务。"
    #         )
    #
    #     if state.status == "failed":
    #         return (
    #             "抱歉，任务执行过程中出现了问题："
    #             f"{state.error}"
    #         )
    #
    #     return "任务执行失败。"
