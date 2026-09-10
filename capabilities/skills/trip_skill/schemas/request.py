# agent/skills/trip_plan/request.py

from pydantic import BaseModel, Field


class TripPlanRequest(BaseModel):

    city: str = Field(
        ...,
        description="旅行城市"
    )

    start_date: str = Field(
        ...,
        description="旅行开始日期，格式 YYYY-MM-DD"
    )

    end_date: str = Field(
        ...,
        description="旅行结束日期，格式 YYYY-MM-DD"
    )

    travelers: int = Field(
        default=1,
        ge=1,
        le=20,
        description="旅行人数"
    )

    budget: int | None = Field(
        default=None,
        ge=0,
        description="总预算，单位人民币"
    )

    preferences: list[str] = Field(
        default_factory=list,
        description="旅行偏好，例如：历史、美食、亲子、自然风景"
    )