import traceback

from langchain_core.messages import ToolMessage

from capabilities.subagents.trip_subagent.state import (
    TripSubAgentState,
)


class TripToolNodes:

    def __init__(self, tools):
        self.tools = tools

        self.tool_map = {
            tool.name: tool
            for tool in tools
        }

    async def tool_node(
        self,
        state: TripSubAgentState,
    ):

        last_message = state["messages"][-1]

        tool_messages = []

        for tool_call in last_message.tool_calls:

            tool_name = tool_call["name"]

            print(
                f"\n[TripSubAgent] "
                f"Executing Tool: {tool_name}"
            )

            tool = self.tool_map.get(
                tool_name
            )

            if tool is None:

                tool_messages.append(
                    ToolMessage(
                        content=(
                            f"Tool not found: "
                            f"{tool_name}"
                        ),
                        tool_call_id=tool_call["id"],
                        name=tool_name,
                    )
                )

                continue

            try:

                result = await tool.ainvoke(
                    tool_call["args"]
                )

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

                # 注意：
                # 不直接让整个 Agent 崩溃。
                # 将失败作为 ToolMessage 返回给 LLM，
                # 让 Agent 自己决定是否重新尝试或换 Tool。

                tool_messages.append(
                    ToolMessage(
                        content=(
                            "Tool execution failed.\n"
                            f"tool={tool_name}\n"
                            f"error={exc}"
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