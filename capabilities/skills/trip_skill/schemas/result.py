from typing import Optional

from pydantic import BaseModel

from schemas.trip_plan import TripPlan


class TripSkillResult(BaseModel):
    """
    TripSkill 对外统一返回结果。

    success:
        True  -> 旅行计划生成成功
        False -> 旅行计划生成失败

    message:
        给上层 Agent / 用户看的最终反馈。

    trip_plan:
        成功时返回完整旅行计划。

    error_code:
        失败时的机器可读错误类型。
    """

    success: bool

    message: str

    trip_plan: Optional[TripPlan] = None

    error_code: Optional[str] = None