from langchain_core.messages import SystemMessage, HumanMessage

from capabilities.subagents.trip_subagent.graph import (
    TripSubAgentGraph,
)
from capabilities.subagents.trip_subagent.prompts.prompt import TRIP_SUBAGENT_SYSTEM_PROMPT
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

        request_context = (
            "\n\n【当前旅行请求】\n"
            f"城市：{request.city}\n"
            f"开始日期：{request.start_date}\n"
            f"结束日期：{request.end_date}\n"
            f"出行人数：{request.travelers}\n"
            f"预算："
            f"{request.budget if request.budget is not None else '未指定'}\n"
            f"旅行偏好："
            f"{', '.join(request.preferences) if request.preferences else '未指定'}"
        )

        initial_state = {
            "messages": [
                SystemMessage(
                    content=TRIP_SUBAGENT_SYSTEM_PROMPT
                ),
                HumanMessage(
                    content=request_context
                )
            ],

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

            "llm_response": None,
        }

        # ==================================================
        # Execute Graph
        # ==================================================
        result = await self.graph.ainvoke(
            initial_state
        )

        status = result.get("status")

        llm_response = result.get(
            "llm_response"
        )

        final_result = result.get(
            "final_result"
        )
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

                "status": "failed",

                "llm_response": llm_response,

                "trip_plan": None,

                "error": result.get(
                    "error"
                ),

                "execution": {
                    "iteration": result.get(
                        "iteration",
                        0,
                    ),
                    "tool_call_count": result.get(
                        "tool_call_count",
                        0,
                    ),
                    "tool_result_count": result.get(
                        "tool_result_count",
                        0,
                    ),
                },
            }

        if status == "max_iterations":
            return {
                "success": False,

                "status": "max_iterations",

                "llm_response": llm_response,

                "trip_plan": None,

                "error": (
                    "TripSubAgent max iterations reached"
                ),

                "execution": {
                    "iteration": result.get(
                        "iteration",
                        0,
                    ),
                    "tool_call_count": result.get(
                        "tool_call_count",
                        0,
                    ),
                    "tool_result_count": result.get(
                        "tool_result_count",
                        0,
                    ),
                },
            }


        # ==================================================
        # 没有 Final Result
        # ==================================================

        if final_result is None:

            return {
                "success": False,

                "status": "empty_result",

                "llm_response": llm_response,

                "trip_plan": None,

                "error": (
                    "TripSubAgent returned empty final result"
                ),

                "execution": {
                    "iteration": result.get(
                        "iteration",
                        0,
                    ),
                    "tool_call_count": result.get(
                        "tool_call_count",
                        0,
                    ),
                    "tool_result_count": result.get(
                        "tool_result_count",
                        0,
                    ),
                },
            }

        # ==================================================
        # SUCCESS
        # ==================================================

        return {
            "success": True,

            "status": "completed",

            # TripSubAgent 最终 LLM 输出
            "llm_response": llm_response,

            # 结构化旅行方案
            "trip_plan": (
                final_result.model_dump()
            ),

            "error": None,

            "execution": {
                "iteration": result.get(
                    "iteration",
                    0,
                ),
                "tool_call_count": result.get(
                    "tool_call_count",
                    0,
                ),
                "tool_result_count": result.get(
                    "tool_result_count",
                    0,
                ),
            },
        }