class ToolNodes:
    def __init__(
            self,
            tool_executor):
        self.tool_executor = tool_executor

    async def execute(
            self,
            state):

        last_message = state['messages'][-1]

        tool_messages = []

        for tool_call in last_message.tool_calls:

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
            except Exception as e:
                return {
                    "status": "failed",
                    "error": (
                        f"Tool execution failed: {e}"
                    )
                }
        return {
            "messages": tool_messages,
            "tool_result_count": (
                    state["tool_result_count"]
                    + len(tool_messages)
            ),
        }
