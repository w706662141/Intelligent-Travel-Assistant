import asyncio
import time
from agent.graph.state import AgentStatus, TaskMode


class AgentNodes:

    def __init__(
            self,
            model
    ):
        self.model = model

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

            start = time.perf_counter()

            response = await asyncio.wait_for(
                self.model.ainvoke(
                    state['messages']
                ),
                timeout=60,
            )
            elapsed = (
                    time.perf_counter() - start
            )

            print(
                f"[AgentNode] "
                f"LLM finished "
                f"({elapsed:.2f}s)"
            )

            print("\nLLM Response:")
            print(response)

            tool_calls = response.tool_calls

            tool_call_count = (
                    state["tool_call_count"]
                    + len(response.tool_calls)
            )

            result = {
                "messages": [response],
                "iteration": iteration,
                "tool_call_count": tool_call_count,
            }

            # ==================================================
            # 第一次产生 Tool Call 时确定任务模式
            # ==================================================
            current_task_mode = state.get('task_mode')

            if current_task_mode is None and tool_calls:
                tool_names = {
                    call['name']
                    for call in tool_calls
                }

                # ==============================================
                # 只要第一次调用 trip_plan
                # 就认为这是完整旅行规划任务
                # ==============================================

                if 'trip_plan' in tool_names:
                    result['task_name'] = (
                        TaskMode.TRAVEL_PLANNING
                    )
                else:
                    result['task_name'] = (
                        TaskMode.DIRECT_QUERY
                    )

            # ==================================================
            # 保存最后一轮 Tool 名称
            # ==================================================
            if tool_calls:
                result["last_tool_name"] = (
                    tool_calls[-1]["name"]
                )

            return result

        except Exception as e:

            return {
                "status": AgentStatus.FAILED,
                "error": f"LLM execution failed: {e}",
                "iteration": iteration,
            }
