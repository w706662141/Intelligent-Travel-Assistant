import asyncio
import traceback
from collections import OrderedDict

from capabilities.subagents.trip_subagent.state import (
    TripSubAgentState,
)

from capabilities.subagents.trip_subagent.prompts.prompt import (
    TRIP_SUBAGENT_SYSTEM_PROMPT,
)


class TripAgentNodes:

    # 每种资源最多给 LLM 6 条。
    MAX_ITEMS_PER_SECTION = 6

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
    # Request Context
    # ==========================================================

    @staticmethod
    def _request_context(
        request,
    ) -> str:

        return (
            f"城市：{request.city}\n"
            f"日期："
            f"{request.start_date} ~ "
            f"{request.end_date}\n"
            f"人数：{request.travelers}\n"
            f"预算："
            f"{request.budget if request.budget is not None else '未指定'}\n"
            f"偏好："
            f"{', '.join(request.preferences) if request.preferences else '未指定'}"
        )

    # ==========================================================
    # Safe String
    # ==========================================================

    @staticmethod
    def _safe_str(
        value,
    ) -> str:

        if value is None:
            return ""

        return str(value).strip()

    # ==========================================================
    # Resource Key
    # ==========================================================

    @classmethod
    def _item_key(
        cls,
        item: dict,
    ) -> tuple:

        name = cls._safe_str(
            item.get("name")
        )

        address = cls._safe_str(
            item.get("address")
        )

        poi_id = cls._safe_str(
            item.get("poi_id")
            or item.get("id")
        )

        return (
            name,
            address,
            poi_id,
        )

    # ==========================================================
    # Compact Item
    #
    # 只保留最终决策真正需要的信息。
    #
    # 删除：
    #   id
    #   location
    #   longitude
    #   latitude
    #
    # 避免把大量内部字段交给 LLM。
    # ==========================================================

    @classmethod
    def _compact_item(
        cls,
        tool_name: str,
        item: dict,
    ) -> dict:

        if not isinstance(
            item,
            dict,
        ):
            return {
                "value": cls._safe_str(item)
            }

        # ======================================================
        # Attraction
        # ======================================================

        if tool_name == "search_attraction":

            keys = (
                "name",
                "address",
                "rating",
                "ticket_price",
                "opening_hours",
                "category",
            )

        # ======================================================
        # Hotel
        # ======================================================

        elif tool_name in {
            "search_hotels",
            "search_hotels_near_place",
        }:

            keys = (
                "name",
                "address",
                "rating",
                "cost",
                "type",
            )

        # ======================================================
        # Meal
        # ======================================================

        elif tool_name == "search_nearby_meals":

            keys = (
                "name",
                "address",
                "type",
                "estimated_cost",
            )

        # ======================================================
        # Weather
        # ======================================================

        elif tool_name == "query_weather":

            keys = (
                "date",
                "day_weather",
                "night_weather",
                "day_temp",
                "night_temp",
                "wind_direction",
                "wind_power",
            )

        else:

            keys = (
                "name",
                "address",
                "rating",
                "cost",
                "type",
                "date",
            )

        return {
            key: item[key]
            for key in keys
            if key in item
            and item[key] not in (
                None,
                "",
                [],
                {},
            )
        }

    # ==========================================================
    # Normalize Result
    # ==========================================================

    @classmethod
    def _normalize_result(
        cls,
        tool_name: str,
        result,
    ) -> list[dict]:

        if result is None:
            return []

        if isinstance(
            result,
            dict,
        ):
            result = [result]

        if not isinstance(
            result,
            list,
        ):
            return [
                {
                    "value": cls._safe_str(
                        result
                    )
                }
            ]

        output = []

        seen = set()

        for raw in result:

            if not isinstance(
                raw,
                dict,
            ):
                continue

            item = cls._compact_item(
                tool_name,
                raw,
            )

            # ==================================================
            # Weather
            #
            # 同一天只保留一条。
            # ==================================================

            if tool_name == "query_weather":

                key = (
                    cls._safe_str(
                        raw.get("date")
                    ),
                )

            else:

                key = cls._item_key(
                    raw
                )

            if key in seen:
                continue

            seen.add(key)

            if item:
                output.append(item)

        return output

    # ==========================================================
    # Build Resource Context
    #
    # 完整 resource_data
    #       ↓
    # 分类
    #       ↓
    # 去重
    #       ↓
    # 压缩
    #       ↓
    # LLM Context
    # ==========================================================

    @classmethod
    def _build_resource_context(
        cls,
        resource_data: list[dict],
        request=None,
    ) -> str:

        if not resource_data:
            return "暂无已获取资源。"

        grouped = OrderedDict(
            (
                ("attractions", []),
                ("hotels", []),
                ("meals", []),
                ("weather", []),
                ("other", []),
            )
        )

        seen = {
            section: set()
            for section in grouped
        }

        # ======================================================
        # 第一步：按照资源类型分类
        # ======================================================

        for resource in resource_data:

            tool_name = resource.get(
                "tool",
                "",
            )

            result = resource.get(
                "result"
            )

            if tool_name == "search_attraction":

                section = "attractions"

            elif tool_name in {
                "search_hotels",
                "search_hotels_near_place",
            }:

                section = "hotels"

            elif tool_name == "search_nearby_meals":

                section = "meals"

            elif tool_name == "query_weather":

                section = "weather"

            else:

                section = "other"

            normalized_items = (
                cls._normalize_result(
                    tool_name,
                    result,
                )
            )

            for item in normalized_items:

                # ==================================================
                # Weather
                # ==================================================

                if section == "weather":

                    key = cls._safe_str(
                        item.get("date")
                    )

                else:

                    key = (
                        cls._safe_str(
                            item.get("name")
                        ),
                        cls._safe_str(
                            item.get("address")
                        ),
                    )

                if key in seen[section]:
                    continue

                seen[section].add(key)

                grouped[section].append(
                    item
                )

        # ======================================================
        # 第二步：过滤旅行日期之外的天气
        # ======================================================

        if request is not None:

            start_date = cls._safe_str(
                request.start_date
            )

            end_date = cls._safe_str(
                request.end_date
            )

            weather_items = (
                grouped["weather"]
            )

            valid_weather = []

            for item in weather_items:

                date = cls._safe_str(
                    item.get("date")
                )

                if (
                    start_date
                    <= date
                    <= end_date
                ):
                    valid_weather.append(
                        item
                    )

            grouped["weather"] = (
                valid_weather
            )

        # ======================================================
        # 第三步：转换为 LLM 可读文本
        # ======================================================

        labels = {
            "attractions": "景点",
            "hotels": "酒店",
            "meals": "餐饮",
            "weather": "天气",
            "other": "其他资源",
        }

        sections = []

        for section, label in labels.items():

            items = grouped[section]

            # ==================================================
            # Weather 没有目标日期
            # ==================================================

            if (
                section == "weather"
                and not items
            ):

                if request is not None:

                    sections.append(
                        f"【{label}】\n"
                        f"暂无覆盖 "
                        f"{request.start_date} ~ "
                        f"{request.end_date} "
                        f"的有效天气数据。"
                    )

                continue

            if not items:
                continue

            # ==================================================
            # 限制每种资源数量
            # ==================================================

            items = items[
                : cls.MAX_ITEMS_PER_SECTION
            ]

            lines = [
                f"【{label}】"
            ]

            for index, item in enumerate(
                items,
                start=1,
            ):

                parts = []

                for key, value in item.items():

                    parts.append(
                        f"{key}={value}"
                    )

                lines.append(
                    f"{index}. "
                    + "；".join(parts)
                )

            sections.append(
                "\n".join(lines)
            )

        if not sections:
            return "暂无可用旅行资源。"

        return "\n\n".join(
            sections
        )

    # ==========================================================
    # Build LLM Messages
    #
    # 关键：
    #
    # 不再：
    #
    # state["messages"]
    #
    # 全部传给模型。
    #
    # 而是：
    #
    # request
    # +
    # compact resource_data
    #
    # 重新构建。
    # ==========================================================

    @classmethod
    def _build_llm_messages(
        cls,
        state: TripSubAgentState,
    ):

        request = state["request"]

        resource_context = (
            cls._build_resource_context(
                resource_data=state.get(
                    "resource_data",
                    [],
                ),
                request=request,
            )
        )

        context = (
            "【旅行需求】\n"
            f"{cls._request_context(request)}\n\n"

            "【已获得资源】\n"
            f"{resource_context}\n\n"

            "【当前决策】\n"
            "判断是否还需要 Tool。\n"
            "需要则调用必要的 Tool；"
            "不需要则停止 Tool Calling。\n"
            "不要重复搜索已经足够的资源。"
        )

        return [
            {
                "role": "system",
                "content": (
                    TRIP_SUBAGENT_SYSTEM_PROMPT
                ),
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
            f"TripSubAgent Iteration "
            f"{iteration} "
            f"=========="
        )

        # ======================================================
        # Max Iterations
        # ======================================================

        if (
            iteration
            > state["max_iterations"]
        ):

            return {
                "iteration": iteration,

                "status": (
                    "max_iterations"
                ),

                "error": (
                    "TripSubAgent "
                    "max iterations reached"
                ),
            }

        # ======================================================
        # 构建压缩后的 LLM Context
        # ======================================================

        llm_messages = (
            self._build_llm_messages(
                state
            )
        )

        resource_count = len(
            state.get(
                "resource_data",
                [],
            )
        )

        print(
            f"[TripSubAgent] "
            f"iteration={iteration}, "
            f"resource_count={resource_count}, "
            f"llm_message_count="
            f"{len(llm_messages)}"
        )

        # ======================================================
        # 调用 Agent LLM
        # ======================================================

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
                "\n[TripSubAgent] "
                "LLM Response:"
            )

            print(response)

            # ==================================================
            # Tool Calls
            # ==================================================

            if tool_calls:

                print(
                    "\n[TripSubAgent] "
                    "Tool Calls:"
                )

                for call in tool_calls:
                    print(call)

            # ==================================================
            # No Tool Calls
            # ==================================================

            else:

                print(
                    "\n[TripSubAgent] "
                    "No more tool calls. "
                    "Handing off to Final LLM."
                )

            # ==================================================
            # State
            # ==================================================

            return {
                "messages": [
                    response
                ],

                "iteration": iteration,

                "tool_call_count": (
                    state[
                        "tool_call_count"
                    ]
                    + len(tool_calls)
                ),
            }

        # ======================================================
        # Timeout
        # ======================================================

        except asyncio.TimeoutError:

            print(
                "\n========== "
                "TripSubAgent "
                "LLM TIMEOUT "
                "=========="
            )

            return {
                "iteration": iteration,

                "status": "failed",

                "error": (
                    "TripSubAgent "
                    "LLM timeout: "
                    "no response within "
                    f"{self.llm_timeout} "
                    "seconds"
                ),
            }

        # ======================================================
        # Exception
        # ======================================================

        except Exception as exc:

            print(
                "\n========== "
                "TripSubAgent "
                "LLM ERROR "
                "=========="
            )

            traceback.print_exc()

            return {
                "iteration": iteration,

                "status": "failed",

                "error": (
                    "TripSubAgent "
                    "LLM execution failed: "
                    f"{exc}"
                ),
            }