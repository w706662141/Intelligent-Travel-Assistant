from typing import Literal

from pydantic import BaseModel, Field


class DaySelection(BaseModel):
    date: str

    attraction_ids: list[str] = Field(
        default_factory=list,
        description="当天安排的景点 ID",
    )

    hotel_id: str | None = Field(
        default=None,
        description="当天住宿酒店 ID",
    )

    description: str = Field(
        default="",
        description="当天行程说明",
    )

    transport_mode: Literal[
        "walking",
        "driving",
        "bicycling",
        "transit",
    ] = Field(
        default="transit",
        description="当天景点之间的主要交通方式",
    )


class PlanSelection(BaseModel):
    days: list[DaySelection] = Field(
        default_factory=list,
        description="每日行程选择",
    )

    overall_suggestions: str = Field(
        default="",
        description="整体旅行建议",
    )
