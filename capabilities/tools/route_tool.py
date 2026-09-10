from langchain_core.tools import tool
from pydantic import BaseModel, Field


class RouteInput(BaseModel):
    """路线规划的公共输入参数"""

    origin_address: str = Field(..., description="起点地址，例如'故宫博物院'")
    destination_address: str = Field(..., description="终点地址，例如'天安门广场'")
    city: str = Field(
        default="",
        description="所在城市，当起点和终点在同一城市时可为空，跨城市时必须填写",
    )


class TransitRouteInput(BaseModel):
    """公共交通路线规划输入参数"""

    origin_address: str = Field(..., description="起点地址，例如'故宫博物院'")
    destination_address: str = Field(..., description="终点地址，例如'颐和园'")
    city: str = Field(..., description="所在城市，必填")


def create_route_tools(
        route_service,
):
    @tool(args_schema=RouteInput)
    async def plan_walking_route(
            origin_address: str,
            destination_address: str,
            city: str = "",
    ):
        """规划步行路线，返回每一步的导航指引和预计时长。"""

        return await route_service.walking(
            origin_address,
            destination_address,
            city or None,
        )

    @tool(args_schema=RouteInput)
    async def plan_driving_route(
            origin_address: str,
            destination_address: str,
            city: str = "",
    ):
        """规划驾车路线，返回路线距离、预计时长和导航指引。"""

        return await route_service.driving(
            origin_address,
            destination_address,
            city or None,
        )

    @tool(args_schema=RouteInput)
    async def plan_bicycling_route(
            origin_address: str,
            destination_address: str,
            city: str = "",
    ):
        """规划骑行路线，返回路线距离、预计时长和导航指引。"""

        return await route_service.bicycling(
            origin_address,
            destination_address,
            city or None,
        )

    @tool(args_schema=TransitRouteInput)
    async def plan_transit_route(
            origin_address: str,
            destination_address: str,
            city: str,
    ):
        """规划公共交通路线（地铁/公交），返回换乘方案和预计时长。"""

        return await route_service.transit(
            origin_address,
            destination_address,
            city,
        )

    return [
        plan_walking_route,
        plan_driving_route,
        plan_bicycling_route,
        plan_transit_route,
    ]