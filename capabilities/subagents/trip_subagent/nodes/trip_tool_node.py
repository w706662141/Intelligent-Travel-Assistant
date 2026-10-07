import asyncio
import traceback

from langchain_core.messages import ToolMessage

from capabilities.subagents.trip_subagent.state import (
    TripSubAgentState,
)


class TripToolNodes:

    # ==========================================================
    # 依赖前置地点的 Tool
    # ==========================================================

    DEPENDENT_TOOLS = {
        "search_hotels_near_place",
        "search_nearby_meals",
    }

    def __init__(
        self,
        tools,
    ):

        self.tools = tools

        self.tool_map = {
            tool.name: tool
            for tool in tools
        }

    # ==========================================================
    # ToolMessage
    # ==========================================================

    @staticmethod
    def _build_tool_message(
        tool_call: dict,
        content: str,
    ) -> ToolMessage:

        return ToolMessage(
            content=content,
            tool_call_id=tool_call["id"],
            name=tool_call["name"],
        )

    # ==========================================================
    # Execute Tool
    # ==========================================================

    async def _execute_tool(
        self,
        tool_call: dict,
        tool_args: dict,
    ):

        tool_name = tool_call["name"]

        print(
            f"\n[TripSubAgent] "
            f"Executing Tool: {tool_name}"
        )

        print(
            f"[TripSubAgent] "
            f"Tool Args: {tool_args}"
        )

        tool = self.tool_map.get(
            tool_name
        )

        # ======================================================
        # Tool 不存在
        # ======================================================

        if tool is None:

            error_message = (
                f"Tool not found: "
                f"{tool_name}"
            )

            return {
                "tool_message": (
                    self._build_tool_message(
                        tool_call,
                        error_message,
                    )
                ),
                "resource_data": None,
            }

        # ======================================================
        # Execute
        # ======================================================

        try:

            result = await tool.ainvoke(
                tool_args
            )

            print(
                "\n[TripSubAgent] "
                "Tool Result:"
            )

            print(result)

            # ==================================================
            # 给下一轮 Agent 的 ToolMessage
            # ==================================================

            tool_message = (
                self._build_tool_message(
                    tool_call,
                    str(result),
                )
            )

            # ==================================================
            # 完整资源
            # ==================================================

            resource_data = {
                "tool": tool_name,
                "args": tool_args,
                "result": result,
            }

            return {
                "tool_message": tool_message,
                "resource_data": resource_data,
            }

        except Exception as exc:

            print(
                "\n[TripSubAgent] "
                "Tool execution failed:"
            )

            print(
                f"tool={tool_name}"
            )

            print(
                f"error={repr(exc)}"
            )

            traceback.print_exc()

            error_content = (
                "Tool execution failed.\n"
                f"tool={tool_name}\n"
                f"error={exc}\n\n"
                "请根据当前错误决定：\n"
                "1. 是否更换其他 Tool\n"
                "2. 是否重新调用当前 Tool\n"
                "3. 是否已经拥有足够的数据"
            )

            return {
                "tool_message": (
                    self._build_tool_message(
                        tool_call,
                        error_content,
                    )
                ),
                "resource_data": None,
            }

    # ==========================================================
    # Tool Node
    # ==========================================================

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
                    [],
                )
            }

        last_message = messages[-1]

        tool_calls = getattr(
            last_message,
            "tool_calls",
            [],
        )

        if not tool_calls:
            return {}

        current_resource_data = state.get(
            "resource_data",
            [],
        )

        # ======================================================
        # 分成两类：
        #
        # independent:
        #   search_attraction
        #   search_hotels
        #   query_weather
        #
        # dependent:
        #   search_hotels_near_place
        #   search_nearby_meals
        # ======================================================

        independent_calls = []
        dependent_calls = []

        for tool_call in tool_calls:

            tool_name = tool_call["name"]

            if (
                tool_name
                in self.DEPENDENT_TOOLS
            ):

                dependent_calls.append(
                    tool_call
                )

            else:

                independent_calls.append(
                    tool_call
                )

        execution_results = {}

        # ======================================================
        # 第一阶段：
        # 独立 Tool 并发
        # ======================================================

        if independent_calls:

            print(
                "\n[TripSubAgent] "
                "Executing independent "
                "tools concurrently..."
            )

            results = await asyncio.gather(
                *[
                    self._execute_tool(
                        tool_call,
                        tool_call.get(
                            "args",
                            {},
                        ),
                    )
                    for tool_call
                    in independent_calls
                ]
            )

            for tool_call, result in zip(
                independent_calls,
                results,
            ):

                execution_results[
                    tool_call["id"]
                ] = result

        # ======================================================
        # 当前资源
        # ======================================================

        updated_resource_data = [
            *current_resource_data
        ]

        # ======================================================
        # 加入独立 Tool 结果
        # ======================================================

        for tool_call in independent_calls:

            result = execution_results.get(
                tool_call["id"]
            )

            if not result:
                continue

            resource_data = result.get(
                "resource_data"
            )

            if resource_data is not None:

                updated_resource_data.append(
                    resource_data
                )

        # ======================================================
        # 第二阶段：
        # dependent tools
        # ======================================================

        if dependent_calls:

            dependent_tasks = []

            for tool_call in dependent_calls:

                tool_name = tool_call["name"]

                original_args = (
                    tool_call.get(
                        "args",
                        {},
                    )
                )

                place = original_args.get(
                    "place"
                )

                # ==================================================
                # 缺少 place
                #
                # 不让 ToolNode 自动选择：
                #
                # result[0]
                #
                # 必须让 Agent 自己决定。
                # ==================================================

                if not place:

                    error_content = (
                        f"Tool `{tool_name}` "
                        "requires a `place`.\n"
                        "当前调用缺少 place 参数。\n"
                        "请根据之前 "
                        "`search_attraction` "
                        "返回的真实景点选择一个 "
                        "place，然后重新调用当前 Tool。\n"
                        "不要自行编造景点名称。"
                    )

                    execution_results[
                        tool_call["id"]
                    ] = {
                        "tool_message": (
                            self._build_tool_message(
                                tool_call,
                                error_content,
                            )
                        ),
                        "resource_data": None,
                    }

                    continue

                print(
                    "\n[TripSubAgent] "
                    f"Dependent Tool: "
                    f"{tool_name}"
                )

                print(
                    "[TripSubAgent] "
                    f"Selected place: "
                    f"{place}"
                )

                # ==================================================
                # 注意：
                #
                # 这里直接使用 LLM 选择的 place。
                #
                # 不做：
                #
                # resource_data[0]
                #
                # ==================================================

                dependent_tasks.append(
                    self._execute_tool(
                        tool_call,
                        original_args,
                    )
                )

            # ==================================================
            # 依赖 Tool 之间仍然可以并发
            # ==================================================

            if dependent_tasks:

                print(
                    "\n[TripSubAgent] "
                    "Executing dependent "
                    "tools concurrently..."
                )

                dependent_results = (
                    await asyncio.gather(
                        *dependent_tasks
                    )
                )

                dependent_index = 0

                for tool_call in dependent_calls:

                    if (
                        tool_call["id"]
                        in execution_results
                    ):
                        continue

                    result = (
                        dependent_results[
                            dependent_index
                        ]
                    )

                    dependent_index += 1

                    execution_results[
                        tool_call["id"]
                    ] = result

                    resource_data = (
                        result.get(
                            "resource_data"
                        )
                    )

                    if resource_data is not None:

                        updated_resource_data.append(
                            resource_data
                        )

        # ======================================================
        # ToolMessage
        #
        # 必须保持和原 AIMessage.tool_calls
        # 相同顺序。
        # ======================================================

        tool_messages = []

        for tool_call in tool_calls:

            result = execution_results.get(
                tool_call["id"]
            )

            if result is None:

                tool_messages.append(
                    self._build_tool_message(
                        tool_call,
                        (
                            "Tool execution did not "
                            "produce a result."
                        ),
                    )
                )

                continue

            tool_messages.append(
                result["tool_message"]
            )

        # ======================================================
        # 成功 Tool 数量
        # ======================================================

        successful_tool_count = 0

        for tool_call in tool_calls:

            result = execution_results.get(
                tool_call["id"]
            )

            if not result:
                continue

            if (
                result.get(
                    "resource_data"
                )
                is not None
            ):

                successful_tool_count += 1

        # ======================================================
        # State
        # ======================================================

        return {
            "messages": tool_messages,

            "resource_data": (
                updated_resource_data
            ),

            "tool_result_count": (
                state.get(
                    "tool_result_count",
                    0,
                )
                + successful_tool_count
            ),
        }