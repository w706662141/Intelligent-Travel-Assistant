from langchain_core.tools import tool

from capabilities.skills.trip_skill.schemas.request import (
    TripPlanRequest,
)


def create_trip_subagent_tool(
        trip_subagent,
):
    @tool(
        "delegate_trip_task",
        args_schema=TripPlanRequest,
    )
    async def delegate_trip_task(
            city: str,
            start_date: str,
            end_date: str,
            travelers: int = 1,
            budget: int | None = None,
            preferences: list[str] | None = None,
    ):
        """
        将复杂旅行规划任务交给 TripSubAgent。

        适用于：

        - 多日旅行规划
        - 完整旅行方案
        - 每日行程安排
        - 同时涉及景点、酒店、天气、餐饮等
          多个旅行维度的复杂任务

        不适用于：

        - 单独查询景点
        - 单独查询酒店
        - 单独查询天气
        - 单独查询餐厅
        - 单独查询路线
        """

        request = TripPlanRequest(
            city=city,
            start_date=start_date,
            end_date=end_date,
            travelers=travelers,
            budget=budget,
            preferences=preferences or [],
        )

        return await trip_subagent.run(
            request
        )

    return delegate_trip_task
