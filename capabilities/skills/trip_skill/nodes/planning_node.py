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
from langchain_core.messages import SystemMessage, HumanMessage

from capabilities.skills.trip_skill.prompts.trip_skill_prompt import TRIP_PLANNER_SYSTEM_PROMPT, TRIP_PLANNER_PROMPT
from capabilities.skills.trip_skill.trip_plan.state import TripPlanState
from schemas.trip_plan import TripPlan


class TripPlanningNode:

    def __init__(
            self,
            llm,
    ):
        self.llm = llm

        self.structured_llm = (
            llm.with_structured_output(
                # 这里应该传你的 TripPlan Pydantic Model
                TripPlan
            )
        )

    async def __call__(
            self,
            state: TripPlanState,
    ):
        request = state['request']
        validation_errors = state.get("validation_errors", [])
        replan_count = state.get("replan_count", 0)

        # 根据当前是否存在校验错误，
        # 构造首次规划 / 重新规划的提示信息
        if validation_errors:
            correction = f"""
        这是第 {replan_count} 次重新规划。

        上一次规划存在以下问题：

        {validation_errors}

        请重点修正这些问题。
        """
        else:
            correction = """
        这是第一次规划，请根据用户需求生成最合理的旅行计划。
        """

        prompt_value = TRIP_PLANNER_PROMPT.invoke(
            {
                'correction': correction,
                "city": request.city,
                "start_date": request.start_date,
                "end_date": request.end_date,
                "preferences": request.preferences,
                "attractions": state.get("attractions", []),
                "hotels": state.get("hotels", []),
                "weather": state.get("weather"),
                # "validation_errors": validation_errors,
            }
        )

        try:
            trip_plan = await self.structured_llm.ainvoke(
                prompt_value
            )

            return {
                "trip_plan": trip_plan,
                "status": "completed",
                "error": None,
                "replan_count": replan_count + 1,
            }
        except Exception as e:

            import traceback
            traceback.print_exc()

            return {
                "status": "failed",
                "error": f"{type(e).__name__}: {e}",
            }
