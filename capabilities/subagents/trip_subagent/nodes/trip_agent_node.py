import asyncio
import traceback

from langchain_core.messages import SystemMessage, HumanMessage

from capabilities.subagents.trip_subagent.state import (
    TripSubAgentState,
)
from capabilities.subagents.trip_subagent.prompts.prompt import (
    TRIP_SUBAGENT_SYSTEM_PROMPT,
)


class TripAgentNodes:

    def __init__(
        self,
        model,
        max_iterations: int = 15,
    ):
        self.model = model
        self.max_iterations = max_iterations

    async def agent_node(
        self,
        state: TripSubAgentState,
    ):
        iteration = state["iteration"] + 1

        print(
            f"\n========== "
            f"TripSubAgent Iteration {iteration} "
            f"=========="
        )

        if iteration > state["max_iterations"]:
            return {
                "iteration": iteration,
                "status": "max_iterations",
                "error": (
                    "TripSubAgent max iterations reached"
                ),
            }

        request = state["request"]

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

        messages = state["messages"]

        # 第一轮没有 SystemMessage 时加入系统提示
        if not messages:
            messages = [
                SystemMessage(
                    content=(
                        TRIP_SUBAGENT_SYSTEM_PROMPT
                    )
                ),
                HumanMessage(
                    content=request_context
                )
            ]

        try:

            print(
                f"[TripSubAgent] "
                f"Iteration {iteration}, "
                f"message_count={len(messages)}"
            )

            for i, message in enumerate(messages):
                print(
                    f"[TripSubAgent] "
                    f"message[{i}] "
                    f"type={type(message).__name__} "
                    f"content_length={len(str(message.content))}"
                )

            response = await asyncio.wait_for(
                self.model.ainvoke(
                    messages
                ),
                timeout=120,
            )

            tool_calls = getattr(
                response,
                "tool_calls",
                [],
            )

            print(
                "\n[TripSubAgent] LLM Response:"
            )
            print(response)

            if tool_calls:
                print(
                    "\n[TripSubAgent] Tool Calls:"
                )

                for call in tool_calls:
                    print(call)

            return {
                "messages": [response],
                "iteration": iteration,
                "tool_call_count": (
                    state["tool_call_count"]
                    + len(tool_calls)
                ),
            }

        except Exception as exc:

            print(
                "\n========== "
                "TripSubAgent LLM ERROR "
                "=========="
            )

            traceback.print_exc()

            return {
                "iteration": iteration,
                "status": "failed",
                "error": (
                    "TripSubAgent LLM execution failed: "
                    f"{exc}"
                ),
            }