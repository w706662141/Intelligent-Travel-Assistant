import asyncio
import time

from agent.state import AgentState


class AgentLoop:
    def __init__(
            self,
            model,
            tool_executor,
            max_iterations: int = 10):
        self.model = model
        self.tool_executor = tool_executor
        self.max_iterations = max_iterations

    async def run(
            self,
            state: AgentState
    ) -> AgentState:

        while not state.finished:
            # ==========================================
            # 1. Max Iteration Protection
            # ==========================================

            if state.iteration >= state.max_iterations:
                state.max_iterations_reached()
                break

            state.increment_iteration()
            print(
                f"\n========== "
                f"Agent Iteration {state.iteration} "
                f"=========="
            )

            try:
                print("[AgentLoop] Calling LLM...")

                start = time.perf_counter()

                response = await asyncio.wait_for(
                    self.model.ainvoke(
                        state.messages
                    ),
                    timeout=60,
                )

                elapsed = (
                        time.perf_counter() - start
                )

                print(
                    f"[AgentLoop] "
                    f"LLM finished "
                    f"({elapsed:.2f}s)"
                )
            except Exception as e:
                state.fail(
                    f"LLM execution failed: {e}"
                )
                break

            # ==========================================
            # 3. 保存 AI Message
            # ==========================================

            state.messages.append(response)

            print("\nLLM Response:")
            print(response)

            # ==========================================
            # 4. Final Answer
            # ==========================================

            if not response.tool_calls:

                content = response.content

                if isinstance(content, str):

                    state.finish(content)

                else:

                    state.finish(
                        str(content)
                    )

                break
            # ==========================================
            # 5. Tool Calls
            # ==========================================

            for tool_call in response.tool_calls:
                state.tool_call_count += 1

                print("\nTool Call:")
                print(tool_call)

                try:
                    tool_message = (
                        await self.tool_executor.execute(
                            tool_call
                        )
                    )
                except Exception as e:
                    state.fail(
                        f"Tool execution failed: {e}"
                    )

                    break

                # ======================================
                # 7. Observation
                # ======================================

                state.messages.append(
                    tool_message
                )

                state.tool_result_count += 1

                print("\nTool Result:")
                print(tool_message)

            if state.finished:
                break

        return state
