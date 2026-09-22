from langchain_core.messages import AIMessage

from agent.graph.state import AgentStatus


class MainAgentPassthroughNode:
    """
    MainAgent → TripSubAgent 透传节点。

    注意：

    这里绝对不调用 LLM。

    TripSubAgent 已经完成：

        Tool Calling
        Resource Collection
        TripPlan Generation
        Final Response Generation

    MainAgent 这里只负责：

        读取 final_response
        透传给用户
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

        # ==================================================
        # 没有 SubAgent Result
        # ==================================================

        if not result:

            message = (
                "旅行规划没有返回有效结果。"
            )

            print(
                "[MainAgent Passthrough] "
                "EMPTY_SUBAGENT_RESULT"
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

        final_response = result.get(
            "final_response"
        )

        trip_plan = result.get(
            "trip_plan"
        )

        error = result.get(
            "error"
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
            "final_response="
        )

        print(
            final_response
        )

        # ==================================================
        # SUCCESS
        # ==================================================

        if success:

            content = (
                final_response
                or "旅行规划已完成。"
            )

            return {
                # ==========================================
                # 唯一面向用户的输出
                # ==========================================

                "messages": [
                    AIMessage(
                        content=content
                    )
                ],

                "status": (
                    AgentStatus.COMPLETED
                ),

                # ==========================================
                # 结构化数据继续保留在 State
                #
                # 但不再输出给用户
                # ==========================================

                "trip_plan": trip_plan,

                "error": None,
            }

        # ==================================================
        # FAILED
        # ==================================================

        content = (
            final_response
            or "旅行规划执行失败，"
               "无法可靠完成本次旅行规划。"
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

            "error": error,
        }