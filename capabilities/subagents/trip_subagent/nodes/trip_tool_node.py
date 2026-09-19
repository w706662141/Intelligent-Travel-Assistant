import traceback

from capabilities.subagents.trip_subagent.state import TripSubAgentState


class TripToolNodes:

    def __init__(
            self,
            tools
    ):

        self.tools = tools

    async def tool_node(
            self,
            state: TripSubAgentState,
    ):
        """
        执行当前 LLM 请求的 Tool。

        这里不使用旧 TripPlanGraph 的 Executor Node。
        Tool 的选择权属于 TripSubAgent LLM。
        """

        last_message = state["messages"][-1]

        tool_messages = []

        for tool_call in last_message.tool_calls:

            tool_name = tool_call["name"]

            print(
                f"\n[TripSubAgent] "
                f"Executing Tool: {tool_name}"
            )

            tool = self._get_tool(tool_name)

            try:
                result = await tool.ainvoke(
                    tool_call["args"]
                )

                from langchain_core.messages import ToolMessage

                tool_message = ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                    name=tool_name,
                )

                tool_messages.append(
                    tool_message
                )

                print(
                    "\n[TripSubAgent] Tool Result:"
                )
                print(result)

            except Exception as exc:

                print(
                    f"\n[TripSubAgent] "
                    f"Tool execution failed: "
                    f"{tool_name}"
                )

                traceback.print_exc()

                from langchain_core.messages import ToolMessage

                tool_messages.append(
                    ToolMessage(
                        content=(
                            f"Tool execution failed: "
                            f"{exc}"
                        ),
                        tool_call_id=tool_call["id"],
                        name=tool_name,
                    )
                )

        return {
            "messages": tool_messages,
            "tool_result_count": (
                    state["tool_result_count"]
                    + len(tool_messages)
            ),
        }

    def _get_tool(self, tool_name: str):
        for tool in self.tools:

            if tool.name == tool_name:
                return tool

        raise KeyError(
            f"TripSubAgent Tool not found: "
            f"{tool_name}"
        )
