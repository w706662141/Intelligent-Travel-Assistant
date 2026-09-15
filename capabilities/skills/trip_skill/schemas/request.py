
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
        description="出行总人数，默认1人。若用户未明确说明，填 1"
    )

    budget: int | None = Field(
        default=None,
        ge=0,
        description="总体预算金额，单位为人民币元（如 5000）。用户未明确提及具体预算数值时不要填写，绝对不要猜测或假设。"
    )

    preferences: list[str] = Field(
        default_factory=list,
        description="旅行偏好，例如：历史、美食、亲子、自然风景"
    )