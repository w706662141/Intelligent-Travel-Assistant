from datetime import date, timedelta

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
            errors.append("旅行计划不存在")

            return {
                "validation_errors": errors,
                "status": "validation_failed",
            }

        start = date.fromisoformat(request.start_date)
        end = date.fromisoformat(request.end_date)

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

        if not trip_plan.days:
            errors.append("旅行计划没有每日行程")

        expected_dates = [
            (start + timedelta(days=i)).isoformat()
            for i in range((end - start).days + 1)
        ]

        actual_dates = [
            day.date
            for day in trip_plan.days
        ]

        if actual_dates != expected_dates:
            errors.append(
                "每日行程日期未完整覆盖旅行日期"
            )

        for day in trip_plan.days:

            if not day.attractions:
                errors.append(
                    f"第 {day.day_index + 1} 天没有安排景点"
                )

        # =========================
        # 资源真实性
        # =========================

        real_attraction_ids = {
            item.id
            for item in state.get(
                "attractions",
                []
            )
        }

        real_hotel_ids = {
            item.id
            for item in state.get(
                "hotels",
                []
            )
        }

        for day in trip_plan.days:

            for attraction in day.attractions:

                if attraction.id not in real_attraction_ids:
                    errors.append(
                        f"发现不存在的景点 ID: {attraction.id}"
                    )

            if (
                    day.hotel is not None
                    and day.hotel.id not in real_hotel_ids
            ):
                errors.append(
                    f"发现不存在的酒店 ID: {day.hotel.id}"
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
