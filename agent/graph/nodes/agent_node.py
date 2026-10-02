import asyncio
import time
import traceback

from langchain_core.messages import SystemMessage

from agent.graph.state import AgentStatus


class AgentNodes:

    def __init__(
            self,
            model,
            system_prompt: str,
    ):
        self.model = model
        self.system_prompt = system_prompt

    async def agent(self, state):

        iteration = state['iteration'] + 1

        if iteration > state['max_iterations']:
            return {
                "iteration": iteration,
                "status": AgentStatus.MAX_ITERATIONS,
                "error": "Agent max iterations reached"
            }

        print(
            f"\n========== "
            f"Agent Iteration {iteration} "
            f"=========="
        )

        try:
            print("[AgentNode] Calling LLM...")

            # ==========================================
            # Checkpoint 中只保存真实对话消息
            #
            # System Prompt 每次运行时动态添加
            #
            # ==========================================

            messages = state.get(
                "messages",
                [],
            )

            model_messages = [
                SystemMessage(
                    content=self.system_prompt
                ),
                *messages,
            ]

            start = time.perf_counter()

            response = await asyncio.wait_for(
                self.model.ainvoke(
                    model_messages
                ),
                timeout=120,
            )
            elapsed = (
                    time.perf_counter() - start
            )

            print(
                f"[AgentNode] "
                f"LLM finished "
                f"({elapsed:.2f}s)"
            )

            tool_call_count = (
                    state["tool_call_count"]
                    + len(response.tool_calls)
            )

            result = {
                "messages": [response],
                "iteration": iteration,
                "tool_call_count": tool_call_count,
            }

            return result

        except Exception as e:

            print("\n========== LLM ERROR ==========")
            traceback.print_exc()
            print("Exception type:", type(e).__name__)
            print("Exception:", repr(e))
            print("================================\n")

            return {
                "status": AgentStatus.FAILED,
                "error": f"LLM execution failed: {e}",
                "iteration": iteration,
            }
