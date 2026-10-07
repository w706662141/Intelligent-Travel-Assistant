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


class TripSubAgent:

    def __init__(
        self,
        tools,
        max_iterations: int = 15,
        agent_llm_timeout: int = 120,
        final_llm_timeout: int = 60,
    ):
        self.tools = tools
        self.max_iterations = max_iterations

        self.agent_llm_timeout = agent_llm_timeout
        self.final_llm_timeout = final_llm_timeout

        # ======================================================
        # Agent LLM
        #
        # 只负责：
        #
        #   1. 判断是否需要 Tool
        #   2. 选择 Tool
        #   3. 生成 Tool 参数
        #
        # 所以这里绑定 Tools。
        # ======================================================

        self.agent_model = (
            get_agnes_model()
            .bind_tools(tools)
        )

        # ======================================================
        # Final LLM
        #
        # 只负责：
        #
        #   resource_data
        #       ↓
        #   最终旅行规划
        #
        # 不绑定任何 Tool。
        # ======================================================

        self.final_model = get_agnes_model()

        self.graph = TripSubAgentGraph(
            agent_model=self.agent_model,
            final_model=self.final_model,
            tools=self.tools,
            max_iterations=max_iterations,
            agent_llm_timeout=agent_llm_timeout,
            final_llm_timeout=final_llm_timeout,
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

        print(f"city={request.city}")
        print(f"start_date={request.start_date}")
        print(f"end_date={request.end_date}")
        print(f"travelers={request.travelers}")
        print(f"budget={request.budget}")
        print(f"preferences={request.preferences}")

        # ======================================================
        # 初始旅行请求
        #
        # 这里只保存最基本的业务请求。
        #
        # 后续 LLM 不再依赖完整 messages 历史，
        # 而是根据 request + resource_data 重新构建上下文。
        # ======================================================

        request_context = (
            "【当前旅行请求】\n"
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
            "max_iterations": self.max_iterations,

            "status": "running",
            "error": None,

            "tool_call_count": 0,
            "tool_result_count": 0,

            # 完整真实资源。
            #
            # 这里不做删除。
            # LLM 需要什么，由 TripAgentNodes
            # 后面负责构建 compact context。
            "resource_data": [],

            "final_response": None,
        }

        try:

            result = await self.graph.ainvoke(
                initial_state
            )

        except Exception as exc:

            print(
                "\n========================================"
            )
            print("TripSubAgent GRAPH ERROR")
            print(f"error={exc}")
            print("========================================")

            return {
                "success": False,
                "status": "failed",
                "final_response": (
                    "旅行规划执行过程中发生异常，"
                    "暂时无法完成本次旅行规划。"
                ),
                "error": (
                    "TripSubAgent graph execution failed: "
                    f"{exc}"
                ),
                "execution": {
                    "iteration": 0,
                    "tool_call_count": 0,
                    "tool_result_count": 0,
                },
            }

        # ======================================================
        # 读取执行结果
        # ======================================================

        status = result.get("status")

        final_response = result.get(
            "final_response"
        )

        error = result.get("error")

        iteration = result.get(
            "iteration",
            0,
        )

        tool_call_count = result.get(
            "tool_call_count",
            0,
        )

        tool_result_count = result.get(
            "tool_result_count",
            0,
        )

        print(
            "\n========================================"
        )

        print("TripSubAgent FINISHED")
        print(f"status={status}")
        print(f"iteration={iteration}")
        print(
            f"tool_call_count={tool_call_count}"
        )
        print(
            f"tool_result_count={tool_result_count}"
        )

        print("========================================")

        # ======================================================
        # FAILED
        # ======================================================

        if status == "failed":

            return {
                "success": False,
                "status": "failed",

                "final_response": (
                    final_response
                    or (
                        "旅行规划执行失败，"
                        "暂时无法可靠完成本次旅行规划。"
                    )
                ),

                "error": error,

                "execution": {
                    "iteration": iteration,
                    "tool_call_count": tool_call_count,
                    "tool_result_count": tool_result_count,
                },
            }

        # ======================================================
        # MAX ITERATIONS
        # ======================================================

        if status == "max_iterations":

            return {
                "success": False,
                "status": "max_iterations",

                "final_response": (
                    final_response
                    or (
                        "旅行规划执行次数达到上限，"
                        "未能可靠完成本次旅行规划。"
                    )
                ),

                "error": (
                    error
                    or (
                        "TripSubAgent "
                        "max iterations reached"
                    )
                ),

                "execution": {
                    "iteration": iteration,
                    "tool_call_count": tool_call_count,
                    "tool_result_count": tool_result_count,
                },
            }

        # ======================================================
        # SUCCESS
        # ======================================================

        if (
            status == "completed"
            and final_response
            and str(final_response).strip()
        ):

            return {
                "success": True,
                "status": "completed",

                "final_response": str(
                    final_response
                ).strip(),

                "error": None,

                "execution": {
                    "iteration": iteration,
                    "tool_call_count": tool_call_count,
                    "tool_result_count": tool_result_count,
                },
            }

        # ======================================================
        # EMPTY RESULT
        # ======================================================

        return {
            "success": False,
            "status": "empty_result",

            "final_response": (
                "旅行规划执行完成，"
                "但没有生成有效的最终回答。"
            ),

            "error": (
                error
                or (
                    "TripSubAgent completed "
                    "without final_response"
                )
            ),

            "execution": {
                "iteration": iteration,
                "tool_call_count": tool_call_count,
                "tool_result_count": tool_result_count,
            },
        }