from typing import TypedDict, Optional

from capabilities.skills.trip_skill.schemas.request import TripPlanRequest
from schemas.trip_plan import TripPlan


class TripPlanState(TypedDict, total=False):
    # =========================
    # Skill 输入上下文
    # =========================

    request: TripPlanRequest

    # =========================
    # 数据收集结果
    # =========================

    attractions: list

    hotels: list

    weather: object

    # =========================
    # Skill 执行结果
    # =========================

    trip_plan: Optional[TripPlan]

    # =========================
    # Skill 执行状态
    # =========================

    status: str

    error: Optional[str]

    # =========================
    # 校验信息
    # =========================

    validation_errors: list[str]

    # =========================
    # 重规划
    # =========================

    replan_count: int

    max_replan_count: int
