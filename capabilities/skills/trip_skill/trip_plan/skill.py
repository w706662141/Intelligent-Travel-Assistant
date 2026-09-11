import traceback

from capabilities.skills.trip_skill.trip_plan.graph import TripPlanGraph
from capabilities.skills.trip_skill.schemas.request import TripPlanRequest


class TripPlanSkill:

    def __init__(
            self,
            attraction_service,
            hotel_service,
            meal_service,
            weather_service,
            route_service,
            llm,
    ):
        self.llm = llm

        self.graph = (
            TripPlanGraph(
                attraction_service,
                hotel_service,
                meal_service,
                weather_service,
                route_service,
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
            raise

        if result.get('status') != 'validated':
            raise RuntimeError(
                result.get(
                    "error"
                )
                or str(
                    result.get(
                        "validation_errors"
                    )
                )
            )

        trip_plan = result.get(
            "trip_plan"
        )

        if trip_plan is None:
            raise RuntimeError(
                "TripPlanSkill 未生成旅行计划"
            )

        return trip_plan
