from langchain_core.tools import tool
from pydantic import BaseModel, Field


class SearchHotelsInput(BaseModel):
    """搜索酒店的输入参数"""

    city: str = Field(..., description="城市名称，例如'北京'、'上海'")
    limit: int = Field(
        default=5,
        ge=1,
        le=10,
        description="返回结果数量上限，默认为5",
    )


class SearchNearbyHotelsInput(BaseModel):
    """搜索附近酒店的输入参数"""

    place: str = Field(..., description="景点、地址、商圈名称，例如'故宫'、'龙门石窟'")
    limit: int = Field(
        default=5,
        ge=1,
        le=10,
        description="返回结果数量上限，默认为5",
    )


def create_hotel_tools(
        hotel_service,
):
    @tool(args_schema=SearchHotelsInput)
    async def search_hotels(
            city: str,
            limit: int = 5,
    ):
        """
        查询指定城市范围内的酒店列表。

        适用于:
        - 北京有哪些酒店
        - 上海酒店推荐
        - 某城市住宿选择

        不适用于:
        - 某景点附近酒店
        - 某地址附近酒店
        """

        hotels = await hotel_service.search(
            city=city,
            limit=limit
        )

        return [
            hotel.model_dump()
            for hotel in hotels
        ]

    @tool(args_schema=SearchNearbyHotelsInput)
    async def search_hotels_near_place(
            place: str,
            limit: int = 5,
    ):
        """
        搜索指定地区附近的的酒店列表。
        """

        hotels = await hotel_service.search_hotel_nearby(
            address=place,
            radius='1000',
            keyword="酒店",
            limit=limit)

        return [
            hotel.model_dump()
            for hotel in hotels
        ]

    return [
        search_hotels,
        search_hotels_near_place
    ]
