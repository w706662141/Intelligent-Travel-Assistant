from langchain_core.tools import tool

from capabilities.skills.trip_skill.schemas.request import TripPlanRequest


def create_trip_plan_tool(trip_plan_skill):

    @tool("trip_plan", args_schema=TripPlanRequest)
    async def trip_plan(
            city: str,
            start_date: str,
            end_date: str,
            travelers: int = 1,
            budget: int | None = None,
            preferences: list[str] | None = None,
    ):
        """
       制定完整的旅行计划。

        这是一个高层旅行规划工具，用于根据用户的旅行需求生成完整行程。

        适用于：

        多日旅行规划

        根据日期、城市、人数、预算和偏好制定行程

        综合安排景点、酒店、餐饮、天气和路线

        当用户明确要求完整旅行规划时，应调用本工具。

        本工具负责完成完整旅行规划，调用后无需再调用其他旅行相关 Tool 来补充或替代本次规划。

        不要使用本工具处理单独的景点、酒店、天气、餐厅或路线查询。
        """

        request = TripPlanRequest(
            city=city,
            start_date=start_date,
            end_date=end_date,
            travelers=travelers,
            budget=budget,
            preferences=preferences or [],
        )

        result = await trip_plan_skill.execute(request)

        return result.model_dump()

    return [trip_plan]
