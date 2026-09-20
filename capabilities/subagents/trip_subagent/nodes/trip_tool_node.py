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
        messages = state.get(
            "messages",
            []
        )

        if not messages:
            return {
                "resource_data": state.get(
                    "resource_data",
                    []
                )
            }

        last_message = state["messages"][-1]

        tool_calls = getattr(
            last_message,
            "tool_calls",
            []
        )

        if not tool_calls:
            return {}

        tool_messages = []
        tool_results = []

        for tool_call in tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call.get(
                "args",
                {}
            )
            tool_call_id = tool_call["id"]

            print(
                f"\n[TripSubAgent] "
                f"Executing Tool:"
                f" {tool_name}"
            )

            print(
                f"[TripSubAgent] "
                f"Tool Args: "
                f"{tool_args}"
            )

            tool = self.tool_map.get(
                tool_name
            )

            if tool is None:

                error_message = (
                    f"Tool not found: "
                    f"{tool_name}"
                )

                print(
                    f"[TripSubAgent] "
                    f"{error_message}"
                )

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
                    tool_args
                )

                tool_message = ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call_id,
                    name=tool_name,
                )

                tool_messages.append(
                    tool_message
                )

                # 给 Finalizer 使用
                tool_results.append(
                    {
                        "tool": tool_name,
                        "args": tool_args,
                        "result": result,
                    }
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

                print(
                    f"error={repr(exc)}"
                )

                traceback.print_exc()

                # ----------------------------------------------
                # Tool 失败也作为 ToolMessage 返回 Agent
                # ----------------------------------------------

                error_content = (
                    "Tool execution failed.\n"
                    f"tool={tool_name}\n"
                    f"error={exc}\n\n"
                    "请根据当前错误决定：\n"
                    "1. 是否更换其他 Tool\n"
                    "2. 是否重新调用当前 Tool\n"
                    "3. 是否已经拥有足够的数据"
                )

                # 注意：
                # 不直接让整个 Agent 崩溃。
                # 将失败作为 ToolMessage 返回给 LLM，
                # 让 Agent 自己决定是否重新尝试或换 Tool。

                tool_messages.append(
                    ToolMessage(
                        content=error_content,
                        tool_call_id=tool_call_id,
                        name=tool_name,
                    )
                )

        current_resource_data = state.get(
            "resource_data",
            []
        )

        return {
            "messages": tool_messages,
            "resource_data": [
                *current_resource_data,
                *tool_results,
            ],
            "tool_result_count": (
                    state.get(
                        "tool_result_count",
                        0
                    )
                    + len(tool_results)
            ),
        }
