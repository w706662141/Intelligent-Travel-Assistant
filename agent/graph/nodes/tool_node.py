from agent.graph.state import AgentStatus


class ToolNodes:
    def __init__(
            self,
            tool_executor
    ):
        self.tool_executor = tool_executor

    async def execute(
            self,
            state
    ):

        last_message = state['messages'][-1]

        tool_messages = []

        executed_tool_names = []

        for tool_call in last_message.tool_calls:

            tool_name = tool_call["name"]

            executed_tool_names.append(tool_name)

            print("\nTool Call:")
            print(tool_call)

            try:
                tool_message = (
                    await self.tool_executor.execute(tool_call)
                )

                tool_messages.append(tool_message)

                print("\nTool Result:")
                print(tool_message)

            except Exception as e:
                print(
                    "Tool execution failed: %s",
                    tool_name,
                )
                return {
                    "status": AgentStatus.FAILED,
                    "error": (
                        f"Tool execution failed: {e}"
                    )
                }

        return {

            "messages": tool_messages,
            "executed_tool_names": executed_tool_names,
            "tool_result_count": (
                    state["tool_result_count"]
                    + len(tool_messages)
            ),
        }
