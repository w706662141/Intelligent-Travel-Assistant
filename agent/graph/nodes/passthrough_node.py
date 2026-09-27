from langchain_core.messages import AIMessage

from agent.graph.state import AgentStatus


class MainAgentPassthroughNode:
    """
    MainAgent → TripSubAgent 透传节点。

    TripSubAgent 已经生成最终用户回答。

    MainAgent 不再调用 LLM 进行二次总结。

    这里只负责：

        TripSubAgent result
                ↓
        final_response
                ↓
        AIMessage
    """

    async def passthrough(
        self,
        state,
    ):

        print(
            "\n========== "
            "MainAgent Passthrough "
            "=========="
        )

        result = state.get(
            "subagent_result"
        )

        # ==========================================
        # 没有 SubAgent Result
        # ==========================================

        if not result:

            message = (
                "旅行规划子代理没有返回有效结果。"
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
                    AgentStatus.COMPLETED
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

        error = result.get(
            "error"
        )

        print(
            f"[MainAgent Passthrough] "
            f"success={success}"
        )

        print(
            f"[MainAgent Passthrough] "
            f"status={status}"
        )

        print(
            "[MainAgent Passthrough] "
            "final_response:"
        )

        print(
            final_response
        )

        # ==========================================
        # TripSubAgent 成功
        # ==========================================

        if success:

            content = (
                final_response
                or "旅行规划已经完成。"
            )

        # ==========================================
        # TripSubAgent 失败
        # ==========================================

        else:

            content = (
                final_response
                or (
                    "旅行规划执行失败。"
                    f"{error or ''}"
                )
            )

        # ==========================================
        # MainAgent 最终只透传
        # ==========================================

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