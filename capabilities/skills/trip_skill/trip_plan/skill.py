import traceback

from capabilities.skills.trip_skill.trip_plan.graph import TripPlanGraph
from capabilities.skills.trip_skill.schemas.request import TripPlanRequest


class TripPlanSkill:

    def __init__(
            self,
            planning_service,
            llm,
    ):
        self.planning_service = (
            planning_service
        )

        self.llm = llm
        # 构建 Skill 内部 Subgraph

        self.graph = (
            TripPlanGraph(
                planning_service,
                self.llm
            )
                .build()
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
            # =====================
            # 执行状态
            # =====================
            'status': 'running',
            'error': None,
            # =====================
            # 结果
            # =====================

            'trip_plan': None,

            'validation_errors': [],

            # =====================
            # Replan
            # =====================

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
            error = result.get(
                'error'
            )

            validation_errors = result.get(
                'validation_errors',
                [],
            )

            if error:
                raise RuntimeError(error)

            if validation_errors:
                raise RuntimeError(
                    ':'.join(
                        validation_errors
                    )
                )

            raise RuntimeError(
                "TripPlanSkill 执行失败"
                f"status={result.get('status')}, "
                f"error={result.get('error')}, "
                f"validation_errors={validation_errors}"
            )

        trip_plan = result.get(
            'trip_plan'
        )

        if trip_plan is None:
            raise RuntimeError(
                "TripPlanSkill 未生成旅行计划"
            )

        return trip_plan

    # def build_tool(self):
    #
    #     skill = self
    #
    #     @tool(
    #         "trip_plan",
    #         args_schema=TripPlanRequest,
    #     )
    #     async def trip_plan(
    #             city: str,
    #             start_date: str,
    #             end_date: str,
    #             preferences: str = "",
    #     ):
    #         """
    #         制定完整旅行计划。
    #
    #         根据用户提供的城市、旅行日期和偏好，
    #         自动规划每日旅行行程，包括景点、
    #         酒店、天气、餐饮以及预算等信息。
    #
    #         当用户需要完整旅行规划、制定旅行行程、
    #         安排几天旅行时使用该工具。
    #         """
    #
    #         request = TripPlanRequest(
    #             city=city,
    #             start_date=start_date,
    #             end_date=end_date,
    #             preferences=preferences,
    #         )
    #
    #         trip_plan_result = (
    #             await skill.execute(
    #                 request
    #             )
    #         )
    #
    #         return trip_plan_result.model_dump()
    #
    #     return trip_plan
