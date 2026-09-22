from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)

from capabilities.subagents.trip_subagent.graph import (
    TripSubAgentGraph,
)

from capabilities.subagents.trip_subagent.prompts.prompt import (
    TRIP_SUBAGENT_SYSTEM_PROMPT,
)

from capabilities.subagents.trip_subagent.schemas.request import (
    TripPlanRequest,
)

from infrastructure.core.llm import (
    get_agnes_model,
)

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

        # ==================================================
        # Agent Model
        # ==================================================

        self.model = base_model.bind_tools(
            tools
        )

        # ==================================================
        # Finalizer Model
        #
        # 只负责生成结构化 TripPlan
        # ==================================================

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
                ),
            ],

            "request": request,

            "iteration": 0,

            "max_iterations": (
                self.max_iterations
            ),

            "status": "running",

            "error": None,

            "tool_call_count": 0,

            "tool_result_count": 0,

            "resource_data": [],

            "final_result": None,

            "final_response": None,
        }

        # ==================================================
        # Execute Graph
        # ==================================================

        result = await self.graph.ainvoke(
            initial_state
        )

        status = result.get(
            "status"
        )

        final_result = result.get(
            "final_result"
        )

        final_response = result.get(
            "final_response"
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
        # FAILED
        # ==================================================

        if status == "failed":

            error = result.get(
                "error"
            )

            return {
                "success": False,

                "status": "failed",

                "final_response": (
                    final_response
                    or "旅行规划执行失败，"
                       "暂时无法可靠完成本次旅行规划。"
                ),

                "trip_plan": None,

                "error": error,

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
        # MAX ITERATIONS
        # ==================================================

        if status == "max_iterations":

            error = (
                "TripSubAgent max iterations reached"
            )

            return {
                "success": False,

                "status": "max_iterations",

                "final_response": (
                    "旅行规划执行次数达到上限，"
                    "未能可靠完成本次旅行规划。"
                ),

                "trip_plan": None,

                "error": error,

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
        # EMPTY RESULT
        # ==================================================

        if final_result is None:

            error = (
                "TripSubAgent returned "
                "empty final result"
            )

            return {
                "success": False,

                "status": "empty_result",

                "final_response": (
                    "旅行规划没有生成有效结果，"
                    "暂时无法完成本次旅行规划。"
                ),

                "trip_plan": None,

                "error": error,

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
        # EMPTY FINAL RESPONSE
        # ==================================================

        if not final_response:

            final_response = (
                "旅行规划已经生成，"
                "但最终用户展示内容生成失败。"
            )

        # ==================================================
        # SUCCESS
        # ==================================================

        return {
            "success": True,

            "status": "completed",

            # ==============================================
            # 真正给 MainAgent Passthrough 的最终回答
            # ==============================================

            "final_response": final_response,

            # ==============================================
            # 内部结构化数据
            # ==============================================

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