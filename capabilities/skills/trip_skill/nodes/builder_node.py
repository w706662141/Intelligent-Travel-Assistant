from schemas.day_plan import DayPlan
from schemas.trip_plan import TripPlan


class TripPlanBuilderNode:

    async def __call__(
            self,
            state,
    ):
        request = state['request']

        selection = state.get(
            'plan_selection'
        )

        if selection is None:
            return {
                "status": "failed",
                "error": "缺少 PlanSelection",
            }

        attractions = {
            item.id: item
            for item in state.get(
                'attractions',
                []
            )
            if item.id
        }

        hotels = {
            item.id: item
            for item in state.get(
                "hotels",
                []
            )
        }

        # meals_by_day = state.get(
        #     "meals_by_day",
        #     {}
        # )
        #
        # routes = state.get(
        #     "routes",
        #     []
        # )

        print("\n========== Builder ==========")
        print("真实景点 ID:")
        print(list(attractions.keys()))

        print("\nLLM选择:")
        for day in selection.days:
            print(
                day.date,
                day.attraction_ids
            )
        print("=============================")

        days = []

        for index, selected_day in enumerate(
                selection.days,
                start=1,
        ):

            # =========================
            # 景点
            # =========================

            selected_attractions = []

            for attraction_id in (
                    selected_day.attraction_ids
            ):
                attraction = attractions.get(
                    attraction_id
                )
                if attraction is not None:
                    selected_attractions.append(
                        attraction
                    )

            # =========================
            # 酒店
            # =========================

            hotel = None

            if selected_day.hotel_id:
                hotel = hotels.get(
                    selected_day.hotel_id
                )
            # =========================
            # 餐饮
            # =========================

            # day_meals = meals_by_day.get(
            #     selected_day.date,
            #     []
            # )

            # =========================
            # 路线
            # =========================

            # day_routes = [
            #     route
            #     for route in routes
            #     if route.get('date')
            #        == selected_day.date
            # ]

            # =========================
            # DayPlan
            # =========================

            days.append(
                DayPlan(
                    date=selected_day.date,
                    day_index=index - 1,
                    description=(
                        selected_day.description
                    ),
                    accommodation=(
                        hotel.name
                        if hotel else ""
                    ),
                    hotel=hotel,
                    attractions=selected_attractions,
                    # meals=day_meals,
                    # routes=day_routes
                )
            )

        # =========================
        # TripPlan
        # =========================

        trip_plan = TripPlan(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=days,
            weather_info=(
                state["weather"]
                if state.get("weather")
                else []
            ),
            overall_suggestions=(
                selection.overall_suggestions
            ),
        )

        return {
            "trip_plan": trip_plan,
            "status": "built",
            "error": None,
        }
