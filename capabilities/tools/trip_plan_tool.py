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
        制定完整旅行计划。

        本工具是一个高层旅行规划工具。
        内部会自动完成：
        - 景点信息获取
        - 天气信息获取
        - 酒店信息获取
        - 餐饮安排
        - 路线协调
        - 每日行程规划

        当用户需要完整旅行计划时，
        只调用本工具，不要同时调用
        search_attraction、query_weather、
        search_hotel 等底层工具。
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
