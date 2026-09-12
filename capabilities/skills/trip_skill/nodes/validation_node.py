from datetime import date, timedelta

from capabilities.skills.trip_skill.trip_plan.state import TripPlanState


class TripPlanValidationNode:

    async def __call__(
            self,
            state: TripPlanState,
    ):

        trip_plan = state.get(
            "trip_plan"
        )

        request = state["request"]

        errors: list[str] = []

        # ==================================================
        # 1. TripPlan 基础存在性
        # ==================================================

        if trip_plan is None:
            return {
                "validation_errors": [
                    "旅行计划不存在"
                ],
                "status": "validation_failed",
            }

        # ==================================================
        # 2. 日期解析
        # ==================================================

        try:

            start = date.fromisoformat(
                request.start_date
            )

            end = date.fromisoformat(
                request.end_date
            )

        except ValueError:

            return {
                "validation_errors": [
                    "旅行请求日期格式非法"
                ],
                "status": "validation_failed",
            }

        # ==================================================
        # 3. 基础信息一致性
        # ==================================================

        if trip_plan.city != request.city:
            errors.append(
                "旅行计划城市与用户请求不一致"
            )

        if trip_plan.start_date != request.start_date:
            errors.append(
                "开始日期不一致"
            )

        if trip_plan.end_date != request.end_date:
            errors.append(
                "结束日期不一致"
            )

        # ==================================================
        # 4. 日期完整性
        # ==================================================

        expected_dates = [
            (
                    start + timedelta(days=i)
            ).isoformat()
            for i in range(
                (end - start).days + 1
            )
        ]

        actual_dates = [
            day.date
            for day in trip_plan.days
        ]

        if actual_dates != expected_dates:
            errors.append(
                "每日行程日期未完整覆盖旅行日期"
            )

        # ==================================================
        # 5. 天数检查
        # ==================================================

        expected_day_count = (
                                     end - start
                             ).days + 1

        if len(trip_plan.days) != (
                expected_day_count
        ):
            errors.append(
                "每日行程数量与旅行天数不一致"
            )

        # ==================================================
        # 6. 真实资源 ID
        # ==================================================

        real_attraction_ids = {
            item.id
            for item in state.get(
                "attractions",
                []
            )
            if item.id
        }

        real_hotel_ids = {
            item.id
            for item in state.get(
                "hotels",
                []
            )
            if item.id
        }

        # ==================================================
        # 7. 每日行程检查
        # ==================================================

        for day in trip_plan.days:

            if not day.attractions:
                errors.append(
                    f"第 {day.day_index + 1} 天没有安排景点"
                )

            # -----------------------------
            # day_index
            # -----------------------------

            expected_index = (
                expected_dates.index(day.date)
                if day.date in expected_dates
                else -1
            )

            if (
                    expected_index >= 0
                    and day.day_index != expected_index
            ):
                errors.append(
                    f"{day.date} day_index 不正确"
                )

            # -----------------------------
            # 景点真实性
            # -----------------------------

            for attraction in day.attractions:

                if attraction.id not in (
                        real_attraction_ids
                ):
                    errors.append(
                        f"发现不存在的景点 ID: "
                        f"{attraction.id}"
                    )

            # -----------------------------
            # 酒店真实性
            # -----------------------------

            if day.hotel is not None:

                if day.hotel not in state.get(
                        "hotels",
                        []
                ):

                    hotel_id = getattr(
                        day.hotel,
                        "id",
                        None
                    )

                    # Hotel schema 当前没有 id，
                    # 因此主要依赖 Builder 使用真实对象。
                    if hotel_id:
                        errors.append(
                            f"发现不存在的酒店 ID: "
                            f"{hotel_id}"
                        )

            # -----------------------------
            # 餐饮
            # -----------------------------

            if day.meals is None:
                errors.append(
                    f"{day.date} 餐饮信息为空"
                )

            # -----------------------------
            # 路线
            # -----------------------------

            for route in day.routes:

                if route.get("error"):
                    # 路线失败属于软错误，
                    # 不直接判定整个计划失败。
                    continue

                if not route.get(
                        "origin_id"
                ):
                    errors.append(
                        f"{day.date} 路线缺少起点"
                    )

                if not route.get(
                        "destination_id"
                ):
                    errors.append(
                        f"{day.date} 路线缺少终点"
                    )

        # ==================================================
        # 8. 结果
        # ==================================================

        if errors:
            return {
                "validation_errors": errors,
                "status": "validation_failed",
            }

        return {
            "validation_errors": [],
            "status": "validated",
            "error": None,
        }
