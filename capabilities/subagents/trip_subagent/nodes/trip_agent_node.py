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
        llm_timeout: int = 120,
    ):
        self.model = model
        self.max_iterations = max_iterations
        self.llm_timeout = llm_timeout

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

        messages = state["messages"]

        try:
            print(
                f"[TripSubAgent] "
                f"Iteration={iteration}, "
                f"message_count={len(messages)}"
            )

            for i, message in enumerate(messages):
                print(
                    f"[TripSubAgent] "
                    f"message[{i}] "
                    f"type={type(message).__name__} "
                    f"content_length="
                    f"{len(str(message.content))}"
                )

            response = await asyncio.wait_for(
                self.model.ainvoke(messages),
                timeout=self.llm_timeout,
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

            else:
                print(
                    "\n[TripSubAgent] "
                    "No more tool calls."
                )

                print(
                    "[TripSubAgent] "
                    "This AIMessage is the final response."
                )

            return {
                "messages": [response],

                "iteration": iteration,

                "tool_call_count": (
                    state["tool_call_count"]
                    + len(tool_calls)
                ),
            }

        except asyncio.TimeoutError:

            print(
                "\n========== "
                "TripSubAgent LLM TIMEOUT "
                "=========="
            )

            return {
                "iteration": iteration,
                "status": "failed",
                "error": (
                    "TripSubAgent LLM timeout: "
                    f"no response within "
                    f"{self.llm_timeout} seconds"
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