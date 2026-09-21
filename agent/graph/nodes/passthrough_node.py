import json

from langchain_core.messages import AIMessage

from agent.graph.state import AgentStatus


class MainAgentPassthroughNode:
    """
    MainAgent → TripSubAgent 透传节点。

    不调用 LLM。

    TripSubAgent 已经完成：
        Tool Calling
        Resource Collection
        TripPlan Generation

    MainAgent 这里只负责：
        读取结果
        判断状态
        输出最终结果
    """

    async def passthrough(
        self,
        state,
    ):

        result = state.get(
            "subagent_result"
        )

        print(
            "\n========== "
            "MainAgent Passthrough "
            "=========="
        )

        if not result:

            message = (
                "旅行规划没有返回有效结果。"
            )

            return {
                "messages": [
                    AIMessage(
                        content=message
                    )
                ],

                "status": (
                    AgentStatus.SUBAGENT_FAILED
                ),

                "error": (
                    "EMPTY_SUBAGENT_RESULT"
                ),
            }

        success = result.get(
            "success",
            False,
        )

        status = result.get(
            "status"
        )

        llm_response = result.get(
            "llm_response"
        )

        error = result.get(
            "error"
        )

        trip_plan = result.get(
            "trip_plan"
        )

        print(
            "[MainAgent Passthrough]"
        )

        print(
            f"success={success}"
        )

        print(
            f"status={status}"
        )

        print(
            "llm_response="
        )

        print(
            llm_response
        )

        # ==================================================
        # SUCCESS
        # ==================================================

        if success:

            # ------------------------------------------------
            # 这里不再调用 LLM
            #
            # 直接把 TripSubAgent 的结构化结果
            # 透传给最终用户。
            # ------------------------------------------------

            content = json.dumps(
                {
                    "status": status,

                    "message": (
                        llm_response
                        or "旅行规划已完成。"
                    ),

                    "trip_plan": trip_plan,

                    "execution": (
                        result.get(
                            "execution"
                        )
                    ),
                },
                ensure_ascii=False,
                indent=2,
            )

            return {
                "messages": [
                    AIMessage(
                        content=content
                    )
                ],

                "status": (
                    AgentStatus.COMPLETED
                ),

                "trip_plan": trip_plan,

                "error": None,
            }

        # ==================================================
        # FAILED
        # ==================================================

        content = json.dumps(
            {
                "status": status,

                "message": (
                    "旅行规划执行失败，"
                    "无法可靠完成本次旅行规划。"
                ),

                "llm_response": (
                    llm_response
                ),

                "error": error,

                "execution": (
                    result.get(
                        "execution"
                    )
                ),
            },
            ensure_ascii=False,
            indent=2,
        )

        return {
            "messages": [
                AIMessage(
                    content=content
                )
            ],

            "status": (
                AgentStatus.COMPLETED
            ),

            "error": error,
        }