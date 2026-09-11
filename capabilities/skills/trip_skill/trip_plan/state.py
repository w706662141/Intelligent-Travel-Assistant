from typing import TypedDict, Optional

from capabilities.skills.trip_skill.schemas.plan_selection import PlanSelection
from capabilities.skills.trip_skill.schemas.request import TripPlanRequest
from capabilities.skills.trip_skill.schemas.resource_decision import ResourceDecision
from schemas.trip_plan import TripPlan


class TripPlanState(TypedDict, total=False):
    # =========================
    # Skill 输入上下文
    # =========================

    request: TripPlanRequest

    # =========================
    # Decision LLM
    # =========================

    resource_decision: Optional[ResourceDecision]

    # =========================
    # 真实资源
    # =========================

    attractions: list
    hotels: list
    meals: list
    weather: object
    routes: list

    # =========================
    # Planning LLM
    # =========================

    plan_selection: Optional[PlanSelection]

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
