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
            agent_llm_timeout: int = 120,
            finalizer_llm_timeout: int = 120,
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
            agent_llm_timeout=agent_llm_timeout,
            finalizer_llm_timeout=finalizer_llm_timeout,
        ).build()

    async def run(
            self,
            request: TripPlanRequest,
    ) -> dict:

        print(
            "\n"
            "========================================\n"
            "TripSubAgent START\n"
            "========================================"
        )
        print(
            f"city={request.city}"
        )

        print(
            f"start_date={request.start_date}"
        )

        print(
            f"end_date={request.end_date}"
        )

        print(
            f"travelers={request.travelers}"
        )

        print(
            f"budget={request.budget}"
        )

        print(
            f"preferences={request.preferences}"
        )

        # ==================================================
        # Initial State
        # ==================================================

        initial_state = {
            "messages": [],

            # MainAgent → TripSubAgent
            "request": request,

            "iteration": 0,

            "max_iterations": (
                self.max_iterations
            ),

            "status": "running",

            "error": None,

            "tool_call_count": 0,

            "tool_result_count": 0,

            # 非常重要：
            # Finalizer 的唯一资源数据来源
            "resource_data": [],

            "final_result": None,
        }

        # ==================================================
        # Execute Graph
        # ==================================================
        result = await self.graph.ainvoke(
          initial_state
        )

        status = result.get("status")

        print(
            "\n========================================"
        )

        print(
            "TripSubAgent FINISHED"
        )

        print(
            f"status={status}"
        )

        print(
            f"iteration="
            f"{result.get('iteration')}"
        )

        print(
            f"tool_call_count="
            f"{result.get('tool_call_count')}"
        )

        print(
            f"tool_result_count="
            f"{result.get('tool_result_count')}"
        )

        print(
            "========================================"
        )

        # ==================================================
        # Failed
        # ==================================================

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
