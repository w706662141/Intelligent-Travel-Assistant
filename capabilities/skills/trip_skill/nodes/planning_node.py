# from capabilities.skills.trip_skill.trip_plan.state import TripPlanState
#
#
# class TripPlanningNode:
#     def __init__(
#             self,
#             planning_service):
#         self.planning_service = planning_service
#
#     async def __call__(
#             self,
#             state: TripPlanState,
#     ):
#         request = state['request']
#
#         try:
#             trip_plan = await self.planning_service.plan(
#                 city=request.city,
#                 start_date=request.start_date,
#                 end_date=request.end_date,
#                 preferences=request.preferences
#             )
#
#             return {
#                 'trip_plan': trip_plan,
#                 'status': 'completed',
#                 'error': None
#             }
#         except Exception as e:
#
#             return {
#                 'status': 'failed',
#                 'error': str(e)
#             }

from capabilities.skills.trip_skill.prompts.trip_planning_prompt import TRIP_PLANNING_PROMPT
from capabilities.skills.trip_skill.schemas.plan_selection import PlanSelection
from capabilities.skills.trip_skill.trip_plan.state import TripPlanState


class TripPlanningNode:

    def __init__(
            self,
            llm,
    ):
        self.llm = llm

        self.structured_llm = (
            llm.with_structured_output(
                PlanSelection
            )
        )

    async def __call__(
            self,
            state: TripPlanState,
    ):
        request = state['request']

        validation_errors = state.get("validation_errors", [])

        replan_count = state.get(
            "replan_count",
            0,
        )

        # ======================================
        # 判断是否是重新规划
        # ======================================

        is_replan = bool(
            validation_errors
        )

        correction = ""

        # 根据当前是否存在校验错误，
        # 构造首次规划 / 重新规划的提示信息
        if is_replan:
            correction = f"""
            上一轮旅行规划经过 Validator 校验后，
            发现以下问题：

            {chr(10).join(
                f"- {error}"
                for error in validation_errors
            )}

            请重新规划并修复以上问题。

            注意：
            必须继续使用系统提供的真实资源。
            不要虚构新的景点 ID 或酒店 ID。
            """

        prompt = TRIP_PLANNING_PROMPT.invoke(
            {
                'correction': correction,
                "city": request.city,
                "start_date": request.start_date,
                "end_date": request.end_date,
                "travelers": request.travelers,
                "budget": request.budget,
                "preferences": request.preferences,
                "attractions": state.get("attractions", []),
                "hotels": state.get("hotels", []),
                "weather": state.get("weather"),
            }
        )

        try:
            selection = await self.structured_llm.ainvoke(
                prompt
            )
            print("\n========== Planning Result ==========")
            print(selection)
            print("=====================================")

        except Exception as e:

            import traceback
            traceback.print_exc()

            return {
                "status": "failed",
                "error": f"{type(e).__name__}: {e}",
            }

        # ======================================
        # Replan Counter
        # ======================================

        next_replan_count = replan_count

        if is_replan:

            next_replan_count = (
                replan_count + 1
            )

        return {

            "plan_selection": selection,

            "replan_count": next_replan_count,

            "status": "planned",

            "error": None,

        }