import asyncio
import traceback

from langchain_core.messages import ToolMessage

from capabilities.subagents.trip_subagent.state import (
    TripSubAgentState,
)


class TripToolNodes:
    """
    TripSubAgent Tool 执行节点

    核心设计：

    1. 同一轮 AIMessage 中：
       - 独立 Tool 并发执行
       - 依赖 Tool 等待独立 Tool 完成后再执行

    2. 不新增 current_place 等 State 字段。

    3. resource_data 是唯一的资源数据来源。

    4. search_hotels_near_place / search_nearby_meals
       不直接相信 LLM 传入的 place，
       而是从 resource_data 中提取之前搜索到的景点。

    5. 依赖 Tool 获取到的 place 是景点名称，
       例如：

           "滕王阁"

       然后交给对应 Service：

           geocode(address="滕王阁")

       Service 自己完成地理编码。

    6. 保证 ToolMessage 顺序与 AIMessage.tool_calls 顺序一致。
    """

    # ==========================================================
    # 需要依赖前置景点结果的 Tool
    # ==========================================================

    DEPENDENT_TOOLS = {
        "search_hotels_near_place",
        "search_nearby_meals",
    }

    # ==========================================================
    # 初始化
    # ==========================================================

    def __init__(self, tools):
        self.tools = tools

        self.tool_map = {
            tool.name: tool
            for tool in tools
        }

    # ==========================================================
    # 创建 ToolMessage
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
    # 执行单个 Tool
    # ==========================================================

    async def _execute_tool(
            self,
            tool_call: dict,
            tool_args: dict,
    ):
        """
        执行一个 Tool。

        返回：

            {
                "tool_message": ToolMessage,
                "resource_data": dict | None,
            }

        不让单个 Tool 异常直接导致整个 TripSubAgent 崩溃。
        """

        tool_name = tool_call["name"]
        tool_call_id = tool_call["id"]

        tool = self.tool_map.get(tool_name)

        print(
            f"\n[TripSubAgent] "
            f"Executing Tool: {tool_name}"
        )

        print(
            f"[TripSubAgent] "
            f"Tool Args: {tool_args}"
        )

        # ------------------------------------------------------
        # Tool 不存在
        # ------------------------------------------------------

        if tool is None:
            error_message = (
                f"Tool not found: {tool_name}"
            )

            print(
                f"[TripSubAgent] "
                f"{error_message}"
            )

            return {
                "tool_message": self._build_tool_message(
                    tool_call,
                    error_message,
                ),
                "resource_data": None,
            }

        # ------------------------------------------------------
        # 执行 Tool
        # ------------------------------------------------------

        try:

            result = await tool.ainvoke(
                tool_args
            )

            print(
                "\n[TripSubAgent] Tool Result:"
            )

            print(result)

            # --------------------------------------------------
            # 给 LLM 的 ToolMessage
            # --------------------------------------------------

            tool_message = self._build_tool_message(
                tool_call,
                str(result),
            )

            # --------------------------------------------------
            # 给 Finalizer 使用的 resource_data
            # --------------------------------------------------

            resource_data = {
                "tool": tool_name,
                "args": tool_args,
                "result": result,
            }

            return {
                "tool_message": tool_message,
                "resource_data": resource_data,
            }

        # ------------------------------------------------------
        # Tool 执行失败
        # ------------------------------------------------------

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

            error_content = (
                "Tool execution failed.\n"
                f"tool={tool_name}\n"
                f"error={exc}\n\n"
                "请根据当前错误决定：\n"
                "1. 是否更换其他 Tool\n"
                "2. 是否重新调用当前 Tool\n"
                "3. 是否已经拥有足够的数据"
            )

            tool_message = self._build_tool_message(
                tool_call,
                error_content,
            )

            return {
                "tool_message": tool_message,
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

        # ------------------------------------------------------
        # 没有消息
        # ------------------------------------------------------

        if not messages:
            return {
                "resource_data": state.get(
                    "resource_data",
                    []
                )
            }

        # ------------------------------------------------------
        # 获取最后一条 AIMessage
        # ------------------------------------------------------

        last_message = messages[-1]

        tool_calls = getattr(
            last_message,
            "tool_calls",
            []
        )

        # ------------------------------------------------------
        # 没有 Tool Call
        # ------------------------------------------------------

        if not tool_calls:
            return {}

        # ======================================================
        # 当前已有的 resource_data
        # ======================================================

        current_resource_data = state.get(
            "resource_data",
            []
        )

        # ======================================================
        # 第一阶段
        #
        # 找出：
        #
        #   独立 Tool
        #
        # 例如：
        #
        #   search_attraction
        #   search_hotels
        #   query_weather
        #
        # 这些 Tool 之间互相不依赖。
        #
        # 所以可以 asyncio.gather 并发执行。
        # ======================================================

        independent_calls = []
        dependent_calls = []

        for tool_call in tool_calls:

            tool_name = tool_call["name"]

            if tool_name in self.DEPENDENT_TOOLS:

                dependent_calls.append(
                    tool_call
                )

            else:

                independent_calls.append(
                    tool_call
                )

        # ======================================================
        # 保存结果
        #
        # 使用 dict：
        #
        #     tool_call_id -> execution_result
        #
        # 最后按照原始 tool_calls 顺序重新组装。
        #
        # 这样即使 asyncio.gather 返回顺序发生变化，
        # ToolMessage 顺序仍然不会乱。
        # ======================================================

        execution_results = {}

        # ======================================================
        # 第一阶段：并发执行独立 Tool
        # ======================================================

        if independent_calls:

            print(
                "\n[TripSubAgent] "
                "Executing independent tools concurrently..."
            )

            independent_results = await asyncio.gather(
                *[
                    self._execute_tool(
                        tool_call,
                        tool_call.get(
                            "args",
                            {}
                        ),
                    )
                    for tool_call in independent_calls
                ]
            )

            # ----------------------------------------------
            # 保存执行结果
            # ----------------------------------------------

            for tool_call, result in zip(
                    independent_calls,
                    independent_results,
            ):
                execution_results[
                    tool_call["id"]
                ] = result

        # ======================================================
        # 第二阶段
        #
        # 现在独立 Tool 已经执行完成。
        #
        # 先把本轮独立 Tool 成功结果加入 resource_data。
        #
        # 这样：
        #
        # search_attraction
        #
        # 的结果就可以被下面的：
        #
        # search_hotels_near_place
        # search_nearby_meals
        #
        # 使用。
        # ======================================================

        updated_resource_data = [
            *current_resource_data
        ]

        for tool_call in independent_calls:

            execution_result = execution_results.get(
                tool_call["id"]
            )

            if not execution_result:
                continue

            resource_data = execution_result.get(
                "resource_data"
            )

            if resource_data is not None:
                updated_resource_data.append(
                    resource_data
                )

        # ======================================================
        # 第三阶段
        #
        # 执行依赖 Tool
        #
        # 例如：
        #
        # search_hotels_near_place
        # search_nearby_meals
        #
        # 这些 Tool 虽然依赖景点，
        # 但是它们之间互不依赖。
        #
        # 所以如果 LLM 已经明确给出了：
        #
        # search_hotels_near_place(
        #     place="滕王阁"
        # )
        #
        # search_nearby_meals(
        #     place="滕王阁"
        # )
        #
        # 那么两个 Tool 仍然可以并发执行。
        # ======================================================

        if dependent_calls:

            dependent_tasks = []

            for tool_call in dependent_calls:

                tool_name = tool_call["name"]

                original_args = tool_call.get(
                    "args",
                    {}
                )

                # --------------------------------------------------
                # 从 LLM 的 Tool Call 参数中获取 place
                # --------------------------------------------------

                place = original_args.get("place")

                # --------------------------------------------------
                # 没有 place
                #
                # 不让 ToolNode 自己去 resource_data 中猜。
                #
                # 直接告诉 LLM：
                #
                # 当前 Tool 缺少 place，
                # 请根据之前 search_attraction 的结果
                # 选择一个真实景点。
                # --------------------------------------------------

                if not place:
                    print(
                        "\n[TripSubAgent] "
                        f"Missing place for dependent tool: "
                        f"{tool_name}"
                    )

                    error_content = (
                        f"Tool `{tool_name}` requires a `place`.\n"
                        "当前调用缺少 place 参数。\n"
                        "请根据之前 `search_attraction` "
                        "返回的真实景点选择一个 place，"
                        "然后重新调用当前 Tool。\n"
                        "不要自行编造景点名称。"
                    )

                    execution_results[
                        tool_call["id"]
                    ] = {
                        "tool_message": self._build_tool_message(
                            tool_call,
                            error_content,
                        ),
                        "resource_data": None,
                    }

                    continue

                # --------------------------------------------------
                # 有 place
                #
                # 直接使用 LLM 已经选择的 place。
                #
                # 不再覆盖：
                #
                # place = resource_data[0]
                #
                # --------------------------------------------------

                print(
                    "\n[TripSubAgent] "
                    f"Dependent Tool: {tool_name}"
                )

                print(
                    "[TripSubAgent] "
                    f"Selected place: {place}"
                )

                dependent_tasks.append(
                    self._execute_tool(
                        tool_call,
                        original_args,
                    )
                )

            # ======================================================
            # 依赖 Tool 并发执行
            # ======================================================

            if dependent_tasks:

                print(
                    "\n[TripSubAgent] "
                    "Executing dependent tools concurrently..."
                )

                dependent_results = await asyncio.gather(
                    *dependent_tasks
                )

                # --------------------------------------------------
                # 保存结果
                # --------------------------------------------------

                dependent_index = 0

                for tool_call in dependent_calls:

                    # 缺少 place 的 Tool 已经处理过了
                    if tool_call["id"] in execution_results:
                        continue

                    result = dependent_results[
                        dependent_index
                    ]

                    dependent_index += 1

                    execution_results[
                        tool_call["id"]
                    ] = result

                    # --------------------------------------------------
                    # 保存 resource_data
                    # --------------------------------------------------

                    execution_result_data = result.get(
                        "resource_data"
                    )

                    if execution_result_data is not None:
                        updated_resource_data.append(
                            execution_result_data
                        )

        # ======================================================
        # 按照 AIMessage.tool_calls 原始顺序生成 ToolMessage
        # ======================================================

        tool_messages = []

        for tool_call in tool_calls:

            result = execution_results.get(
                tool_call["id"]
            )

            if result is None:
                # 理论上不应该出现。
                # 这里作为保险处理。

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
        # 计算成功 Tool 数量
        # ======================================================

        successful_tool_count = 0

        for tool_call in tool_calls:

            result = execution_results.get(
                tool_call["id"]
            )

            if not result:
                continue

            if result.get(
                    "resource_data"
            ) is not None:
                successful_tool_count += 1

        # ======================================================
        # 返回 State
        # ======================================================

        return {
            "messages": tool_messages,

            "resource_data": updated_resource_data,

            "tool_result_count": (
                    state.get(
                        "tool_result_count",
                        0
                    )
                    + successful_tool_count
            ),
        }
