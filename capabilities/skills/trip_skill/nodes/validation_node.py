from capabilities.skills.trip_skill.trip_plan.state import TripPlanState


class TripPlanValidationNode:

    async def __call__(
            self,
            state: TripPlanState,
    ):
        trip_plan = state.get('trip_plan')

        request = state['request']

        errors: list[str] = []

        if trip_plan is None:

            errors.append("旅行计划生成失败")

            return {
                "validation_errors": errors,
                "status": "invalid",
            }

        if not trip_plan.days:
            errors.append("旅行计划没有每日行程")

        if not trip_plan.city:
            errors.append("旅行城市不能为空")

        if not trip_plan.start_date:
            errors.append("开始日期不能为空")

        if not trip_plan.end_date:
            errors.append("结束日期不能为空")

        if trip_plan.city != request.city:

            errors.append(
                "旅行计划城市与用户请求不一致"
            )

        # =========================
        # 日期检查
        # =========================

        if trip_plan.start_date != request.start_date:

            errors.append(
                "开始日期不一致"
            )

        if trip_plan.end_date != request.end_date:

            errors.append(
                "结束日期不一致"
            )

        for day in trip_plan.days:

            if not day.attractions:

                errors.append(
                    f"第 {day.day_index + 1} 天没有安排景点"
                )

        # =========================
        # 结果
        # =========================

        if errors:

            return {
                "validation_errors": errors,
                "status": "validation_failed",
            }

        return {
            "validation_errors": [],
            "status": "validated",
        }
