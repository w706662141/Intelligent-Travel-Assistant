from langchain_core.messages import AIMessage


class MainAgentPassthroughNode:

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

        if not result:
            return {
                "messages": [
                    AIMessage(
                        content=(
                            "旅行规划子代理没有返回有效结果。"
                        )
                    )
                ]
            }

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
            f"[MainAgent] "
            f"TripSubAgent status={status}"
        )

        print(
            "[MainAgent] "
            "TripSubAgent response:"
        )

        print(final_response)

        # ==========================================
        # TripSubAgent 已经完成
        # ==========================================

        if status == "completed":

            return {
                "messages": [
                    AIMessage(
                        content=final_response
                    )
                ],

                "error": None,
            }

        # ==========================================
        # TripSubAgent 执行失败
        # ==========================================

        if status == "failed":

            return {
                "messages": [
                    AIMessage(
                        content=(
                            final_response
                            or (
                                "旅行规划执行失败："
                                f"{error}"
                            )
                        )
                    )
                ],

                "error": error,
            }

        # ==========================================
        # 达到最大迭代
        # ==========================================

        if status == "max_iterations":

            return {
                "messages": [
                    AIMessage(
                        content=(
                            final_response
                            or (
                                "旅行规划执行次数"
                                "达到上限。"
                            )
                        )
                    )
                ],

                "error": error,
            }

        # ==========================================
        # 其他状态
        # ==========================================

        return {
            "messages": [
                AIMessage(
                    content=(
                        final_response
                        or (
                            "旅行规划任务执行结束，"
                            "但没有生成有效结果。"
                        )
                    )
                )
            ],

            "error": error,
        }