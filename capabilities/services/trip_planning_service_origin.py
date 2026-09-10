from datetime import date, timedelta

from schemas.budget import Budget
from schemas.day_plan import DayPlan
from schemas.trip_plan import TripPlan


class TripPlanningService:

    def __init__(
            self,
            attraction_service,
            hotel_service,
            meal_service,
            weather_service,
            route_service,
    ):
        self.attraction_service = (
            attraction_service
        )

        self.hotel_service = (
            hotel_service
        )

        self.meal_service = (
            meal_service
        )

        self.weather_service = (
            weather_service
        )

        self.route_service = (
            route_service
        )

    async def plan(
            self,
            city: str,
            start_date: str,
            end_date: str,
            preferences: str = '',
    ) -> TripPlan:
        start = date.fromisoformat(start_date)

        end = date.fromisoformat(end_date)

        days = (
                end - start
               ).days + 1

        attractions = (
            await self.attraction_service
                .search_with_details(
                city=city,
                keyword="景点",
                limit=max(days * 2, 5),
            )
        )

        hotels = (
            await self.hotel_service.search(
                city=city,
                limit=5,
            )
        )

        weather = (
            await self.weather_service.query(
                city
            )
        )

        day_plans = []

        for index in range(days):
            current_date = (
                    start
                    + timedelta(days=index)
            )

            daily_attractions = (
                attractions[index * 2:
                            index * 2 + 2]
            )

            hotel = (
                hotels[0]
                if hotels
                else None
            )
            meals = []

            if daily_attractions:

                first = (
                    daily_attractions[0]
                )

                if first.location:
                    meals = (
                        await self.meal_service
                            .search_nearby(
                            location=(
                                first.location
                                    .to_amap()
                            ),
                            meal_type="lunch",
                        )
                    )
            day_plans.append(
                DayPlan(
                    date=current_date.isoformat(),
                    day_index=index,
                    description=(
                        f"{city}第{index + 1}天行程"
                    ),
                    transportation="公共交通",
                    accommodation=(
                        hotel.name
                        if hotel
                        else ""
                    ),
                    hotel=hotel,
                    attractions=daily_attractions,
                    meals=meals,
                )
            )

        budget = Budget()

        if hotels:
            budget.total_hotels = (
                sum(
                    hotel.estimated_cost
                    for hotel in hotels[:days]
                )
            )

        budget.total_attractions = sum(
            attraction.ticket_price or 0
            for attraction in attractions
        )

        budget.calculate()

        return TripPlan(
            city=city,
            start_date=start_date,
            end_date=end_date,
            days=day_plans,
            weather_info=weather,
            overall_suggestions=(
                "请根据天气和景点开放时间灵活调整行程。"
            ),
            budget=budget,
        )
