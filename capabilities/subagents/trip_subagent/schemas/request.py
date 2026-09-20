from pydantic import BaseModel, Field


class TripPlanRequest(BaseModel):
    """
    TripSubAgent / TripPlan 的统一旅行请求。

    这是 MainAgent → TripSubAgent 之间传递的业务请求对象。
    """

    city: str = Field(
        ...,
        description="旅行城市",
    )

    start_date: str = Field(
        ...,
        description="旅行开始日期，格式 YYYY-MM-DD",
    )

    end_date: str = Field(
        ...,
        description="旅行结束日期，格式 YYYY-MM-DD",
    )

    travelers: int = Field(
        default=1,
        ge=1,
        le=20,
        description="出行总人数，默认1人",
    )

    budget: int | None = Field(
        default=None,
        ge=0,
        description=(
            "总体预算金额，单位为人民币元。"
            "用户未明确提及具体预算时不要猜测。"
        ),
    )

    preferences: list[str] = Field(
        default_factory=list,
        description=(
            "旅行偏好，例如：历史、美食、亲子、自然风景"
        ),
    )