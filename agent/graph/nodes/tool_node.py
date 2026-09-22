import ast

from agent.graph.state import AgentStatus


class ToolNodes:

    def __init__(
        self,
        tool_executor,
    ):
        self.tool_executor = tool_executor

    @staticmethod
    def _parse_tool_result(
        content: str,
    ) -> dict | None:

        if not isinstance(content, str):
            return None

        try:

            result = ast.literal_eval(
                content
            )

            if isinstance(result, dict):
                return result

        except Exception:
            pass

        return None

    async def execute(
        self,
        state,
    ):

        last_message = state["messages"][-1]

        tool_messages = []

        executed_tool_names = []

        subagent_result = (
            state.get(
                "subagent_result"
            )
        )

        status = state.get(
            "status",
            AgentStatus.RUNNING,
        )

        for tool_call in last_message.tool_calls:

            tool_name = tool_call["name"]

            executed_tool_names.append(
                tool_name
            )

            print("\nTool Call:")
            print(tool_call)

            try:

                tool_message = (
                    await self.tool_executor.execute(
                        tool_call
                    )
                )

                tool_messages.append(
                    tool_message
                )

                print("\nTool Result:")
                print(tool_message)

                # ==========================================
                # delegate_trip_task
                # ==========================================

                if tool_name == "delegate_trip_task":

                    parsed_result = (
                        self._parse_tool_result(
                            tool_message.content
                        )
                    )

                    if parsed_result is None:

                        status = (
                            AgentStatus.SUBAGENT_FAILED
                        )

                        subagent_result = {
                            "success": False,

                            "status": "invalid_result",

                            "final_response": (
                                "旅行规划子代理返回了"
                                "无效结果，"
                                "无法完成本次旅行规划。"
                            ),

                            "trip_plan": None,

                            "error": (
                                "delegate_trip_task "
                                "returned an invalid result"
                            ),
                        }

                    else:

                        subagent_result = (
                            parsed_result
                        )

                        success = (
                            parsed_result.get(
                                "success",
                                False,
                            )
                        )

                        if success:

                            status = (
                                AgentStatus.SUBAGENT_COMPLETED
                            )

                        else:

                            status = (
                                AgentStatus.SUBAGENT_FAILED
                            )

            except Exception as e:

                print(
                    "Tool execution failed: %s",
                    tool_name,
                )

                return {
                    "status": AgentStatus.FAILED,

                    "error": (
                        f"Tool execution failed: {e}"
                    ),
                }

        return {

            "messages": tool_messages,

            "executed_tool_names": (
                executed_tool_names
            ),

            "tool_result_count": (
                state[
                    "tool_result_count"
                ]
                + len(tool_messages)
            ),

            "status": status,

            "subagent_result": (
                subagent_result
            ),
        }