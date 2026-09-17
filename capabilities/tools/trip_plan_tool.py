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
        制定旅行核心计划。

        适用于：
        - 多日旅行规划
        - 根据城市、日期、人数、预算、偏好制定核心行程
        - 综合考虑景点、酒店、天气等信息

        本工具负责生成：
        - 每日景点安排
        - 酒店安排
        - 天气相关建议
        - 每日行程说明

        本工具不会负责：
        - 餐厅搜索
        - 餐饮安排
        - 路线规划

        调用本工具后，如果用户仍有餐饮或交通路线需求，
        MainAgent 可以根据返回的 TripPlan 继续调用对应工具。

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
