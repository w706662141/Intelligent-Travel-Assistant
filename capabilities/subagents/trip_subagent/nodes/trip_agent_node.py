import asyncio
import traceback

from capabilities.subagents.trip_subagent.state import (
    TripSubAgentState,
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

        messages = state["messages"]

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

            # ==================================================
            # 保存 LLM Response
            # ==================================================

            response_content = response.content

            if isinstance(response_content, str):
                llm_response = response_content
            else:
                llm_response = str(response_content)

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
                # 最新一次 LLM 输出
                "llm_response": llm_response,
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