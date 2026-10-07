from langchain_core.tools import tool
from pydantic import BaseModel, Field


class SearchHotelsInput(BaseModel):
    """搜索酒店的输入参数"""

    city: str = Field(
        ...,
        description="城市名称，例如'北京'、'上海'",
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=10,
        description="返回结果数量上限，默认为5",
    )


class SearchNearbyHotelsInput(BaseModel):
    """搜索附近酒店的输入参数"""

    city: str = Field(
        ...,
        description="当前旅行城市，例如'北京'、'上海'",
    )
    place: str = Field(
        ...,
        description="必须是之前景点 Tool 返回的真实地点，例如'故宫博物院'",
    )
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
            city: str,
            place: str,
            limit: int = 5,
    ):
        """
        搜索当前旅行城市中指定真实地点附近的酒店。
        place 必须来自之前景点搜索结果。
        """

        hotels = await hotel_service.search_hotel_nearby(
            address=f"{city}{place}",
            radius="1000",
            keyword="酒店",
            limit=limit,
        )

        return [
            hotel.model_dump()
            for hotel in hotels
        ]

    return [
        search_hotels,
        search_hotels_near_place
    ]
