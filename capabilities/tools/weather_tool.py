from langchain_core.tools import tool
from pydantic import BaseModel, Field


class WeatherInput(BaseModel):
    """查询城市天气的输入参数"""
    city: str = Field(..., description="城市名称，例如'北京'、'上海'")


def create_weather_tool(
        weather_service,
):
    @tool(args_schema=WeatherInput)
    async def query_weather(city: str):
        """
        查询指定城市天气。
        """

        weathers = await weather_service.query_weather(city)

        return [
            weather.model_dump()
            for weather in weathers
        ]

    return [
        query_weather,
            ]
