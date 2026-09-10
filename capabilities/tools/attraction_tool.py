from langchain_core.tools import tool
from pydantic import BaseModel, Field


class SearchAttractionInput(BaseModel):
    """搜索旅游景点的输入参数"""
    city: str = Field(..., description="城市名称，例如'北京'、'杭州'、'上海'")
    keyword: str = Field(
        default="景点",
        description="搜索关键词，默认为'景点'，可按需改为'博物馆'、'公园'、'古镇'等",
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=10,
        description="返回结果数量上限，建议不超过10，默认为5",
    )


def create_attraction_tools(
        attraction_service,
):
    @tool(args_schema=SearchAttractionInput)
    async def search_attraction(
            city: str,
            keyword: str = '景点',
            limit: int = 5
    ):
        """
        搜索指定城市的旅游景点，并返回每个景点的详细信息（评分、门票价格、开放时间等）。
        """

        attractions = await attraction_service.search_with_details(
            city=city,
            keyword=keyword,
            limit=limit,
        )

        return [
            attraction.model_dump()
            for attraction in attractions
        ]

    return [
        search_attraction
    ]
