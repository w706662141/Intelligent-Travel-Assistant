import asyncio

from capabilities.skills.trip_skill.trip_plan.state import TripPlanState
from schemas.meal import Meal


class TripMealExecutorNode:
    """
    根据 Planning 阶段确定的每日行程，
    搜索真实的早餐、午餐和晚餐候选。
    """

    def __init__(
            self,
            meal_service,
    ):
        self.meal_service = meal_service

    async def __call__(
            self,
            state: TripPlanState,
    ):
        selection = state.get('plan_selection')

        if selection is None:
            return {
                "status": "failed",
                "error": "缺少 PlanSelection",
            }

        attractions = {
            item.id: item
            for item in state.get('attractions', [])
            if item.id
        }

        hotels = {
            item.id: item
            for item in state.get('hotels', [])
            if item.id
        }

        tasks: list[tuple[str, str, str]] = []

        for day in selection.days:
            selected_attractions = [
                attractions[item_id]
                for item_id in day.attraction_ids
                if item_id in attractions
            ]

            hotel = (
                hotels.get(day.hotel_id)
                if day.hotel_id
                else None
            )

            # 早餐：优先酒店附近
            breakfast_address = None

            if hotel and hotel.address:
                breakfast_address = hotel.address

            elif selected_attractions:
                breakfast_address = selected_attractions[0].address

            # 午餐：第一个景点附近
            lunch_address = (
                selected_attractions[0].address
                if selected_attractions
                else None
            )

            # 晚餐：最后一个景点附近
            dinner_address = (
                selected_attractions[-1].address
                if selected_attractions
                else None
            )

            meal_tasks = [
                ("breakfast", breakfast_address),
                ("lunch", lunch_address),
                ("dinner", dinner_address),
            ]

            for meal_type, address in meal_tasks:

                if address:
                    tasks.append(
                        (
                            day.date,
                            meal_type,
                            address
                        )
                    )

        if not tasks:
            return {
                "meals": [],
                "meals_by_day": {},
                "status": "meals_completed",
                "error": None,
            }

        coroutines = [
            self.meal_service.search_nearby(
                address=address,
                meal_type=meal_type,
                limit=3
            )
            for _, meal_type, address in tasks
        ]

        results = await asyncio.gather(
            *coroutines,
            return_exceptions=True,
        )

        meals: list[Meal] = []

        meals_by_day: dict[str, list[Meal]] = {}

        errors: list[str] = []

        for (
                task,
                result,
        ) in zip(tasks, results):
            day_date, meal_type, _ = task

            if isinstance(result, Exception):
                errors.append(
                    f"{day_date} {meal_type} "
                    f"获取失败: "
                    f"{type(result).__name__}: {result}"
                )

                continue

            for meal in result:
                meals.append(meal)

                meals_by_day.setdefault(
                    day_date,
                    [],
                ).append(meal)

        return {
            "meals": meals,
            "meals_by_day": meals_by_day,
            "status": "meals_completed",
            "error": (
                "; ".join(errors)
                if errors
                else None
            ),
        }
