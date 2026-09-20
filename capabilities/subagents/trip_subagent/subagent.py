from capabilities.subagents.trip_subagent.graph import (
    TripSubAgentGraph,
)
from capabilities.subagents.trip_subagent.schemas.request import TripPlanRequest
from infrastructure.core.llm import get_agnes_model
from schemas.trip_plan import TripPlan


class TripSubAgent:

    def __init__(
            self,
            tools,
            max_iterations: int = 15,
    ):
        self.tools = tools
        self.max_iterations = max_iterations

        base_model = get_agnes_model()

        # Agent 模型：
        # 具备 Tool Calling 能力
        self.model = base_model.bind_tools(
            tools
        )

        # Finalizer 模型：
        # 只负责生成结构化 TripPlan
        self.finalizer_model = (
            base_model.with_structured_output(
                TripPlan
            )
        )

        self.graph = TripSubAgentGraph(
            model=self.model,
            finalizer_model=self.finalizer_model,
            tools=self.tools,
            max_iterations=max_iterations,
        ).build()

    async def run(
            self,
            request: TripPlanRequest,
    ) -> dict:

        result = await self.graph.ainvoke(
            {
                "messages": [],

                # 核心：
                # MainAgent 传入的结构化请求
                "request": request,

                "iteration": 0,

                "max_iterations": self.max_iterations,

                "status": "running",

                "error": None,

                "tool_call_count": 0,

                "tool_result_count": 0,

                "final_result": None,
            }
        )

        status = result.get("status")

        if status == "failed":
            return {
                "success": False,
                "message": (
                    "旅行规划过程中出现问题，"
                    "暂时无法完成该任务。"
                ),
                "error": result.get("error"),
            }

        if status == "max_iterations":
            return {
                "success": False,
                "message": (
                    "旅行规划步骤过多，"
                    "暂时无法完成该任务。"
                ),
                "error": (
                    "TripSubAgent max iterations reached"
                ),
            }

        final_result = result.get(
            "final_result"
        )

        if final_result is None:
            return {
                "success": False,
                "message": "旅行规划未生成有效结果。",
                "error": "EMPTY_FINAL_RESULT",
            }

        return {
            "success": True,
            "trip_plan": final_result.model_dump(),
            "tool_call_count": result.get(
                "tool_call_count",
                0,
            ),
            "tool_result_count": result.get(
                "tool_result_count",
                0,
            ),
        }
