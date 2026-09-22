import asyncio
import json
import traceback

from langchain_core.messages import SystemMessage, HumanMessage

from capabilities.subagents.trip_subagent.state import (
    TripSubAgentState,
)
from schemas.trip_plan import TripPlan


class TripFinalizerNode:
    """
    TripSubAgent Finalizer。

    职责：

    1. 根据 request + resource_data 生成结构化 TripPlan。
    2. 将 TripPlan 渲染成最终用户可读的 final_response。

    注意：

    final_response 在 TripSubAgent 内部完成。

    MainAgent 不再负责总结。
    MainAgent 只负责透传。
    """

    def __init__(
        self,
        model,
        llm_timeout: int = 120,
    ):
        self.model = model
        self.llm_timeout = llm_timeout

    async def finalize(
        self,
        state: TripSubAgentState,
    ):
        print(
            "\n========== "
            "TripSubAgent Finalizer "
            "=========="
        )

        print("[Finalizer] entered")

        request = state["request"]

        finalizer_prompt = f"""
你是旅行规划结果整理器。

你的任务不是继续搜索，也不是调用工具。

你需要根据：

1. 用户的结构化旅行请求
2. TripSubAgent 已经执行得到的 Tool 结果

生成最终的 TripPlan。

==============================
【旅行请求】
==============================

城市：
{request.city}

开始日期：
{request.start_date}

结束日期：
{request.end_date}

出行人数：
{request.travelers}

预算：
{
    request.budget
    if request.budget is not None
    else "未指定"
}

旅行偏好：
{
    ", ".join(request.preferences)
    if request.preferences
    else "未指定"
}

==============================
【严格要求】
==============================

1. 只使用已经获得的 Tool 数据。

2. 不允许编造：
   - 景点
   - 酒店
   - 餐厅
   - POI ID
   - 经纬度
   - 天气
   - 价格
   - 评分

3. 如果 Tool 没有返回某项信息，
   可以留空或使用模型允许的默认值，
   不得虚构实时数据。

4. 必须保持城市、日期与用户请求一致。

5. 根据实际旅行天数生成 days。

6. 每一天必须对应一个日期。

7. DayPlan 中：
   - attractions 使用 Tool 返回的真实景点
   - hotel 使用 Tool 返回的真实酒店
   - meals 使用 Tool 返回的真实餐厅

8. routes 不需要由你规划。
   TripSubAgent 不负责路线规划。

9. overall_suggestions 应总结：
   - 行程特点
   - 天气注意事项
   - 住宿建议
   - 餐饮建议
   - 其他必要提醒

10. 只生成结构化 TripPlan。
"""

        try:

            resource_data = state.get(
                "resource_data",
                [],
            )

            finalizer_input = f"""
用户旅行请求：

城市：{request.city}
开始日期：{request.start_date}
结束日期：{request.end_date}
人数：{request.travelers}

预算：
{
    request.budget
    if request.budget is not None
    else "未指定"
}

旅行偏好：
{
    ", ".join(request.preferences)
    if request.preferences
    else "未指定"
}

已经获取的真实资源数据：

{json.dumps(
    resource_data,
    ensure_ascii=False,
    indent=2,
)}

请仅根据以上数据生成 TripPlan。
"""

            execution_messages = [
                SystemMessage(
                    content=finalizer_prompt
                ),
                HumanMessage(
                    content=finalizer_input
                ),
            ]

            print(
                "[Finalizer] "
                f"input_length="
                f"{len(finalizer_input)}"
            )

            result = await asyncio.wait_for(
                self.model.ainvoke(
                    execution_messages
                ),
                timeout=self.llm_timeout,
            )

            if not isinstance(result, TripPlan):
                result = TripPlan.model_validate(result)

            print(
                "\n[Finalizer] generated TripPlan:"
            )

            print(result)

            # ==================================================
            # 生成最终用户回答
            # ==================================================

            final_response = (
                self._build_final_response(
                    result
                )
            )

            print(
                "\n[Finalizer] final_response:"
            )

            print(final_response)

            return {
                "final_result": result,

                "final_response": final_response,

                "status": "completed",

                "error": None,
            }

        except asyncio.TimeoutError:

            print(
                "\n========== "
                "TripSubAgent Finalizer TIMEOUT "
                "=========="
            )

            error = (
                "TripSubAgent Finalizer timeout: "
                f"no response within "
                f"{self.llm_timeout} seconds"
            )

            return {
                "status": "failed",

                "error": error,

                "final_result": None,

                "final_response": (
                    "旅行规划生成超时，"
                    "暂时无法完成本次旅行规划。"
                ),
            }

        except Exception as exc:

            print(
                "\n========== "
                "TripSubAgent Finalizer ERROR "
                "=========="
            )

            print(
                f"[Finalizer] "
                f"Exception Type: "
                f"{type(exc).__name__}"
            )

            traceback.print_exc()

            error = (
                "TripSubAgent Finalizer failed: "
                f"{exc}"
            )

            return {
                "status": "failed",

                "error": error,

                "final_result": None,

                "final_response": (
                    "旅行规划生成失败，"
                    "暂时无法可靠完成本次旅行规划。"
                ),
            }

    @staticmethod
    def _build_final_response(
        trip_plan: TripPlan,
    ) -> str:
        """
        将结构化 TripPlan 转换成最终用户可读的 Markdown。

        注意：

        这里不调用 LLM。

        因此不会产生额外模型调用，
        同时保证 MainAgent 可以纯透传。
        """

        lines = []

        lines.append(
            f"# {trip_plan.city}旅行规划"
        )

        lines.append("")

        lines.append(
            f"**旅行日期：** "
            f"{trip_plan.start_date} ~ "
            f"{trip_plan.end_date}"
        )

        lines.append("")

        lines.append(
            f"**共 {len(trip_plan.days)} 天行程**"
        )

        lines.append("")

        # ==================================================
        # 每日行程
        # ==================================================

        for day in trip_plan.days:

            lines.append(
                f"## 第{day.day_index + 1}天 · "
                f"{day.date}"
            )

            if day.description:
                lines.append(
                    f"\n{day.description}"
                )

            lines.append("")

            # --------------------------------------------------
            # 景点
            # --------------------------------------------------

            if day.attractions:

                lines.append("### 景点")

                for attraction in day.attractions:

                    item = (
                        f"- **{attraction.name}**"
                    )

                    if attraction.description:
                        item += (
                            f"：{attraction.description}"
                        )

                    if attraction.address:
                        item += (
                            f"\n  - 地址："
                            f"{attraction.address}"
                        )

                    if attraction.recommended_duration:
                        item += (
                            f"\n  - 建议游览："
                            f"{attraction.recommended_duration}"
                            f"分钟"
                        )

                    if attraction.ticket_price is not None:
                        item += (
                            f"\n  - 门票："
                            f"{attraction.ticket_price}元"
                        )

                    lines.append(item)

                lines.append("")

            # --------------------------------------------------
            # 酒店
            # --------------------------------------------------

            if day.hotel:

                lines.append("### 住宿")

                hotel = day.hotel

                lines.append(
                    f"- **{hotel.name}**"
                )

                if hotel.address:
                    lines.append(
                        f"  - 地址：{hotel.address}"
                    )

                if hotel.price_range:
                    lines.append(
                        f"  - 价格：{hotel.price_range}"
                    )

                if hotel.rating:
                    lines.append(
                        f"  - 评分：{hotel.rating}"
                    )

                lines.append("")

            elif day.accommodation:

                lines.append("### 住宿")

                lines.append(
                    f"- {day.accommodation}"
                )

                lines.append("")

            # --------------------------------------------------
            # 餐饮
            # --------------------------------------------------

            if day.meals:

                lines.append("### 餐饮")

                for meal in day.meals:

                    item = (
                        f"- **{meal.name}**"
                    )

                    if meal.type:
                        item += (
                            f"（{meal.type}）"
                        )

                    if meal.address:
                        item += (
                            f"\n  - 地址："
                            f"{meal.address}"
                        )

                    if meal.description:
                        item += (
                            f"\n  - {meal.description}"
                        )

                    if meal.estimated_cost:
                        item += (
                            f"\n  - 预计："
                            f"{meal.estimated_cost}元"
                        )

                    lines.append(item)

                lines.append("")

        # ==================================================
        # 天气
        # ==================================================

        if trip_plan.weather_info:

            lines.append("## 天气信息")

            for weather in trip_plan.weather_info:

                lines.append(
                    f"- **{weather.date}**："
                    f"白天{weather.day_weather} "
                    f"{weather.day_temp}℃，"
                    f"夜间{weather.night_weather} "
                    f"{weather.night_temp}℃，"
                    f"{weather.wind_direction}"
                    f"{weather.wind_power}"
                )

            lines.append("")

        # ==================================================
        # 总体建议
        # ==================================================

        if trip_plan.overall_suggestions:

            lines.append("## 总体建议")

            lines.append(
                trip_plan.overall_suggestions
            )

            lines.append("")

        # ==================================================
        # 预算
        # ==================================================

        if trip_plan.budget:

            budget = trip_plan.budget

            lines.append("## 预算参考")

            lines.append(
                f"- 景点："
                f"{budget.total_attractions}元"
            )

            lines.append(
                f"- 住宿："
                f"{budget.total_hotels}元"
            )

            lines.append(
                f"- 餐饮："
                f"{budget.total_meals}元"
            )

            lines.append(
                f"- 交通："
                f"{budget.total_transportation}元"
            )

            lines.append(
                f"- **合计："
                f"{budget.total}元**"
            )

            lines.append("")

        return "\n".join(lines).strip()