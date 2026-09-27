from langchain_core.messages import AIMessage

from capabilities.subagents.trip_subagent.state import (
    TripSubAgentState,
)


class TripFinalizerNode:
    """
    TripSubAgent 最终透传节点。

    注意：

    这里绝对不调用 LLM。

    TripSubAgent 的最后一次 LLM 调用
    已经直接生成最终用户回答。

    Finalizer 只负责：

        AIMessage
            ↓
        final_response
            ↓
        status
    """

    async def finalize(
        self,
        state: TripSubAgentState,
    ):
        print(
            "\n========== "
            "TripSubAgent Finalizer "
            "=========="
        )

        messages = state.get(
            "messages",
            []
        )

        # ==========================================
        # 从后往前寻找最后一个 AIMessage
        # ==========================================

        final_message = None

        for message in reversed(messages):

            if isinstance(
                message,
                AIMessage,
            ):
                content = getattr(
                    message,
                    "content",
                    None,
                )

                if content:
                    final_message = message
                    break

        if not final_message:
            error = (
                "TripSubAgent finished "
                "without a valid final AI response"
            )

            print(
                f"[TripFinalizer] {error}"
            )

            return {
                "status": "failed",

                "error": error,

                "final_response": (
                    "旅行规划执行完成，但没有生成有效的最终回答。"
                ),
            }

        # 从后往前找最后一条 AIMessage


        for message in reversed(messages):

            if message.__class__.__name__ == "AIMessage":
                final_message = message
                break

        if final_message is None:
            return {
                "status": "failed",
                "error": (
                    "TripSubAgent 没有产生最终 LLM 响应"
                ),
                "final_response": None,
            }

        content = final_message.content

        if isinstance(content, list):
            content = "\n".join(
                str(item)
                for item in content
            )

        content = str(content).strip()

        if not content:
            return {
                "status": "failed",
                "error": (
                    "TripSubAgent 最终响应为空"
                ),
                "final_response": None,
            }

        print(
            "\n[TripSubAgent] LLM Response:"
        )
        print(content)

        return {
            "status": "completed",
            "error": None,
            "final_response": content,
        }