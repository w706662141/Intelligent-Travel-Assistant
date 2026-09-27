
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)

from langchain_openai import ChatOpenAI

from agent.graph.graph import (
    TravelAgentGraph,
)

from agent.graph.state import (
    AgentStatus,
)

from capabilities.prompts.system import (
    TRAVEL_AGENT_SYSTEM_PROMPT,
)

from capabilities.tools.manager.tool_registry import (
    ToolRegistry,
)


class ReActAgent:

    MAIN_TOOL_NAMES = [

        # ==========================================
        # 复杂旅行任务
        # ==========================================

        "delegate_trip_task",

        # ==========================================
        # 单项查询
        # ==========================================

        "search_attraction",

        "search_hotels",

        "search_nearby_meals",

        "query_weather",

        # ==========================================
        # 路线查询
        # ==========================================

        "plan_walking_route",

        "plan_driving_route",

        "plan_bicycling_route",

        "plan_transit_route",
    ]

    def __init__(
        self,
        model: ChatOpenAI,
        tool_registry: ToolRegistry,
        tool_executor,
        max_iterations: int = 10,
    ):

        self.tool_registry = (
            tool_registry
        )

        self.tool_executor = (
            tool_executor
        )

        tools = [
            self.tool_registry.get(
                name
            )
            for name in self.MAIN_TOOL_NAMES
        ]

        # ==========================================
        # MainAgent LLM
        #
        # 这里只负责：
        # 1. 判断用户任务
        # 2. 选择 Tool
        # 3. 选择 SubAgent
        #
        # 不负责 TripSubAgent 最终总结
        # ==========================================

        self.model = (
            model.bind_tools(tools)
        )

        self.max_iterations = (
            max_iterations
        )

        self.graph = (
            TravelAgentGraph(
                model=self.model,
                tool_executor=self.tool_executor,
            ).build()
        )

    async def run(
        self,
        user_input: str,
    ):

        result = await self.graph.ainvoke(
            {
                "messages": [
                    SystemMessage(
                        content=(
                            TRAVEL_AGENT_SYSTEM_PROMPT
                        )
                    ),

                    HumanMessage(
                        content=user_input
                    ),
                ],

                "iteration": 0,

                "max_iterations": (
                    self.max_iterations
                ),

                "status": (
                    AgentStatus.RUNNING
                ),

                "error": None,

                "tool_call_count": 0,

                "tool_result_count": 0,

                "tool_error_count": 0,

                "retry_count": 0,

                "executed_tool_names": [],

                "trip_request": None,

                "trip_plan": None,

                # ==================================
                # TripSubAgent 结果
                # ==================================

                "subagent_result": None,
            }
        )

        # ==========================================
        # MainAgent 自身失败
        # ==========================================

        if (
            result["status"]
            == AgentStatus.FAILED
        ):

            return (
                "抱歉，任务执行过程中出现了问题："
                f"{result['error']}"
            )

        if (
            result["status"]
            == AgentStatus.MAX_ITERATIONS
        ):

            return (
                "抱歉，我尝试了多次操作，"
                "但仍然没有完成这个任务。"
            )

        # ==========================================
        # 最终消息
        #
        # 对 TripSubAgent 来说：
        #
        # messages[-1]
        #
        # 就是 Passthrough 生成的 AIMessage
        # ==========================================

        messages = result.get(
            "messages",
            [],
        )

        if not messages:
            return "任务执行完成，但没有返回有效结果。"

        return messages[-1].content

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
