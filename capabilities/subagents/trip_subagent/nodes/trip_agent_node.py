import asyncio
import traceback
import json

from langchain_core.messages import (
    HumanMessage,
)

from capabilities.subagents.trip_subagent.state import (
    TripSubAgentState,
)

from capabilities.subagents.trip_subagent.prompts.prompt import (
    TRIP_SUBAGENT_SYSTEM_PROMPT,
)


class TripAgentNodes:

    def __init__(
        self,
        model,
        max_iterations: int = 15,
        llm_timeout: int = 120,
    ):
        self.model = model
        self.max_iterations = max_iterations
        self.llm_timeout = llm_timeout

    # ==========================================================
    # 构建精简资源上下文
    # ==========================================================

    @staticmethod
    def _build_resource_context(
        resource_data: list[dict],
    ) -> str:

        if not resource_data:
            return "目前还没有获取到任何旅行资源。"

        sections = []

        for index, item in enumerate(
            resource_data,
            start=1,
        ):

            tool_name = item.get(
                "tool",
                "unknown",
            )

            args = item.get(
                "args",
                {},
            )

            result = item.get(
                "result",
            )

            # --------------------------------------------------
            # 不把完整 result 原样发送给 LLM
            # --------------------------------------------------

            compact_result = (
                TripAgentNodes._compact_result(
                    tool_name=tool_name,
                    result=result,
                )
            )

            section = (
                f"【资源 {index}】\n"
                f"来源 Tool：{tool_name}\n"
                f"调用参数：{args}\n"
                f"结果：\n"
                f"{compact_result}"
            )

            sections.append(section)

        return "\n\n".join(sections)

    # ==========================================================
    # 精简 Tool 返回结果
    # ==========================================================

    @staticmethod
    def _compact_result(
        tool_name: str,
        result,
    ) -> str:

        if result is None:
            return "无结果"

        # --------------------------------------------------
        # List
        # --------------------------------------------------

        if isinstance(result, list):

            compact_items = []

            for item in result:

                if isinstance(item, dict):

                    compact_item = (
                        TripAgentNodes._compact_item(
                            tool_name,
                            item,
                        )
                    )

                    compact_items.append(
                        compact_item
                    )

                else:

                    compact_items.append(
                        str(item)
                    )

            return json.dumps(
                compact_items,
                ensure_ascii=False,
                indent=2,
            )

        # --------------------------------------------------
        # Dict
        # --------------------------------------------------

        if isinstance(result, dict):

            compact_item = (
                TripAgentNodes._compact_item(
                    tool_name,
                    result,
                )
            )

            return json.dumps(
                compact_item,
                ensure_ascii=False,
                indent=2,
            )

        # --------------------------------------------------
        # 其他类型
        # --------------------------------------------------

        return str(result)

    # ==========================================================
    # 精简单个资源
    # ==========================================================

    @staticmethod
    def _compact_item(
        tool_name: str,
        item: dict,
    ) -> dict:

        # --------------------------------------------------
        # 景点
        # --------------------------------------------------

        if tool_name == "search_attraction":

            return {
                key: item[key]
                for key in (
                    "name",
                    "address",
                    "location",
                    "poi_id",
                    "type",
                )
                if key in item
            }

        # --------------------------------------------------
        # 酒店
        # --------------------------------------------------

        if tool_name in {
            "search_hotels",
            "search_hotels_near_place",
        }:

            return {
                key: item[key]
                for key in (
                    "name",
                    "address",
                    "location",
                    "poi_id",
                    "tel",
                    "rating",
                    "cost",
                )
                if key in item
            }

        # --------------------------------------------------
        # 餐厅
        # --------------------------------------------------

        if tool_name == "search_nearby_meals":

            return {
                key: item[key]
                for key in (
                    "name",
                    "address",
                    "location",
                    "poi_id",
                    "tel",
                    "rating",
                    "cost",
                    "type",
                )
                if key in item
            }

        # --------------------------------------------------
        # 天气
        # --------------------------------------------------

        if tool_name == "query_weather":

            return {
                key: item[key]
                for key in item
                if key in {
                    "city",
                    "date",
                    "week",
                    "weather",
                    "temperature",
                    "winddirection",
                    "windpower",
                }
            }

        # --------------------------------------------------
        # 未知 Tool
        #
        # 不建议直接返回完整对象。
        # 只保留常见字段。
        # --------------------------------------------------

        common_fields = {
            "name",
            "address",
            "location",
            "poi_id",
            "rating",
            "cost",
            "type",
            "date",
            "weather",
            "temperature",
        }

        return {
            key: value
            for key, value in item.items()
            if key in common_fields
        }

    # ==========================================================
    # 构建本轮 LLM Context
    # ==========================================================

    @staticmethod
    def _build_llm_messages(
        state: TripSubAgentState,
    ):

        # --------------------------------------------------
        # 原始用户请求
        #
        # 从最初 HumanMessage 中获取。
        # --------------------------------------------------

        original_messages = state.get(
            "messages",
            []
        )

        user_message = None

        for message in original_messages:

            if isinstance(
                message,
                HumanMessage,
            ):
                user_message = message
                break

        if user_message is None:
            user_content = "当前没有获取到用户请求。"
        else:
            user_content = str(
                user_message.content
            )

        # --------------------------------------------------
        # resource_data
        # --------------------------------------------------

        resource_data = state.get(
            "resource_data",
            []
        )

        resource_context = (
            TripAgentNodes._build_resource_context(
                resource_data
            )
        )

        # --------------------------------------------------
        # 每次重新构建一个干净的 HumanMessage
        #
        # 不再把完整 messages 历史发送给 LLM。
        # --------------------------------------------------

        context = (
            "【用户原始旅行请求】\n"
            f"{user_content}\n\n"
            "【已经获取的真实旅行资源】\n"
            f"{resource_context}\n\n"
            "【当前任务】\n"
            "根据用户需求和已经获取的真实资源，"
            "判断是否还需要调用 Tool。\n"
            "如果需要，继续调用必要的 Tool。\n"
            "如果信息已经足够，停止 Tool Calling，"
            "直接生成最终旅行规划回答。\n"
            "不得编造 Tool 未返回的实时信息。"
        )

        return [
            # --------------------------------------------------
            # 注意：
            # System Prompt 仍然保留。
            # --------------------------------------------------
            {
                "role": "system",
                "content": TRIP_SUBAGENT_SYSTEM_PROMPT,
            },

            {
                "role": "user",
                "content": context,
            },
        ]

    # ==========================================================
    # Agent Node
    # ==========================================================

    async def agent_node(
        self,
        state: TripSubAgentState,
    ):

        iteration = (
            state["iteration"] + 1
        )

        print(
            f"\n========== "
            f"TripSubAgent Iteration {iteration} "
            f"=========="
        )

        if iteration > state["max_iterations"]:

            return {
                "iteration": iteration,
                "status": "max_iterations",
                "error": (
                    "TripSubAgent max iterations reached"
                ),
            }

        # ======================================================
        # 关键修改
        #
        # 不再：
        #
        # messages = state["messages"]
        #
        # 而是：
        #
        # 根据 resource_data 重新构造精简 Context。
        # ======================================================

        llm_messages = (
            self._build_llm_messages(
                state
            )
        )

        print(
            f"[TripSubAgent] "
            f"Iteration={iteration}"
        )

        print(
            f"[TripSubAgent] "
            f"resource_count="
            f"{len(state.get('resource_data', []))}"
        )

        print(
            f"[TripSubAgent] "
            f"LLM message count="
            f"{len(llm_messages)}"
        )

        try:

            response = await asyncio.wait_for(
                self.model.ainvoke(
                    llm_messages
                ),
                timeout=self.llm_timeout,
            )

            tool_calls = getattr(
                response,
                "tool_calls",
                [],
            )

            print(
                "\n[TripSubAgent] LLM Response:"
            )

            print(response)

            if tool_calls:

                print(
                    "\n[TripSubAgent] Tool Calls:"
                )

                for call in tool_calls:
                    print(call)

            else:

                print(
                    "\n[TripSubAgent] "
                    "No more tool calls."
                )

                print(
                    "[TripSubAgent] "
                    "This AIMessage is the final response."
                )

            # --------------------------------------------------
            # 这里仍然把 AIMessage 放回 messages。
            #
            # ToolNode 需要最后一个 AIMessage 中的
            # tool_calls 来执行 Tool。
            #
            # 但是下一轮 Agent 不再使用完整 messages。
            # --------------------------------------------------

            return {
                "messages": [response],

                "iteration": iteration,

                "tool_call_count": (
                    state["tool_call_count"]
                    + len(tool_calls)
                ),
            }

        except asyncio.TimeoutError:

            print(
                "\n========== "
                "TripSubAgent LLM TIMEOUT "
                "=========="
            )

            return {
                "iteration": iteration,

                "status": "failed",

                "error": (
                    "TripSubAgent LLM timeout: "
                    f"no response within "
                    f"{self.llm_timeout} seconds"
                ),
            }

        except Exception as exc:

            print(
                "\n========== "
                "TripSubAgent LLM ERROR "
                "=========="
            )

            traceback.print_exc()

            return {
                "iteration": iteration,

                "status": "failed",

                "error": (
                    "TripSubAgent LLM execution failed: "
                    f"{exc}"
                ),
            }