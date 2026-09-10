from pydantic import BaseModel, Field

from schemas.attraction import Attraction
from schemas.hotel import Hotel
from schemas.weather_info import WeatherInfo


class PlanningContext(BaseModel):
    city: str = Field(
        ...,
        description="旅行城市，例如：北京、上海、杭州"
    )

    start_date: str = Field(
        ...,
        description="旅行开始日期，格式：YYYY-MM-DD"
    )

    end_date: str = Field(
        ...,
        description="旅行结束日期，格式：YYYY-MM-DD"
    )

    days: int = Field(
        ...,
        ge=1,
        description="旅行总天数，必须大于等于1"
    )

    preferences: list[str] = Field(
        default_factory=list,
        description="旅行偏好，例如：历史、美食、亲子、自然风景"
    )

    attractions: list[Attraction] = Field(
        default_factory=list,
        description="规划阶段可选择的景点候选列表"
    )

    hotels: list[Hotel] = Field(
        default_factory=list,
        description="规划阶段可选择的酒店候选列表"
    )

    weather: WeatherInfo | None = Field(
        default=None,
        description="旅行期间的天气信息"
    )
