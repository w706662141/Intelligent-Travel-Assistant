import traceback

from capabilities.skills.trip_skill.schemas.result import TripSkillResult
from capabilities.skills.trip_skill.trip_plan.graph import TripPlanGraph
from capabilities.skills.trip_skill.schemas.request import TripPlanRequest


class TripPlanSkill:

    def __init__(
            self,
            attraction_service,
            hotel_service,
            # meal_service,
            weather_service,
            # route_service,
            llm,
    ):
        self.llm = llm

        self.graph = (
            TripPlanGraph(
                attraction_service,
                hotel_service,
                # meal_service,
                weather_service,
                # route_service,
                self.llm
            ).build()
        )

    async def execute(
            self,
            request: TripPlanRequest,
    ):
        initial_state = {
            # =====================
            # 输入上下文
            # =====================

            'request': request,

            "resource_decision": None,

            "attractions": [],

            "hotels": [],

            "meals": [],

            "meals_by_day": {},

            "weather": None,

            "routes": [],

            "plan_selection": None,

            "trip_plan": None,

            "status": "running",

            "error": None,

            "validation_errors": [],

            "replan_count": 0,

            "max_replan_count": 1,
        }

        try:

            print("\n" + "=" * 80)
            print("[TripPlanSkill] START")
            print("=" * 80)

            print("[TripPlanSkill] request:")
            print(request)

            print("\n[TripPlanSkill] invoking TripPlanGraph...")

            result = await self.graph.ainvoke(
                initial_state
            )
            print("\n[TripPlanSkill] Graph finished")
            print("status:", result.get("status"))
            print("error:", result.get("error"))
            print(
                "validation_errors:",
                result.get("validation_errors")
            )

        except Exception as exc:

            print("\n" + "=" * 100)
            print("🔥 [TripPlanSkill] ORIGINAL EXCEPTION")
            print("=" * 100)

            print("Exception Type:")
            print(type(exc).__name__)

            print("\nException:")
            print(repr(exc))

            print("\nFull Traceback:")
            traceback.print_exc()

            print("=" * 100)

            # 调试阶段一定要保留原始异常

            return TripSkillResult(
                success=False,
                message=(
                    "旅行规划过程中发生异常，"
                    "暂时无法生成完整的旅行计划。"
                ),
                error_code="SYSTEM_ERROR",
            )

        if result.get('status') != 'validated':
            error_code = (
                    result.get("error_code")
                    or "TRIP_PLAN_FAILED"
            )

            error = result.get("error")

            validation_errors = (
                    result.get("validation_errors")
                    or []
            )

            # 优先使用节点产生的错误
            if error:
                message = error

            elif validation_errors:
                message = (
                        "旅行计划未能通过最终校验："
                        + "；".join(validation_errors)
                )

                error_code = "PLAN_VALIDATION_FAILED"
            else:

                message = (
                    "暂时无法生成完整的旅行计划，"
                    "请稍后重试。"
                )

            return TripSkillResult(
                success=False,
                message=message,
                error_code=error_code,
            )

        trip_plan = result.get(
            "trip_plan"
        )

        if trip_plan is None:
            raise RuntimeError(
                "TripPlanSkill 未生成旅行计划"
            )

        return TripSkillResult(
            success=True,
            message="旅行计划已生成完成。",
            trip_plan=trip_plan,
        )

        # return trip_plan
