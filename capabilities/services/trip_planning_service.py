from datetime import date


class TripPlanningService:

    def __init__(
            self,
            attraction_service,
            hotel_service,
            meal_service,
            weather_service,
            route_service,
    ):
        self.attraction_service = attraction_service
        self.hotel_service = hotel_service
        self.meal_service = meal_service
        self.weather_service = weather_service
        self.route_service = route_service

    async def collect_data(
            self,
            city: str,
            start_date: str,
            end_date: str,
            preferences: list[str] | None = None,
    ) -> dict:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)

        days = (
                       end - start
               ).days + 1
        # =========================
        # 1. 景点
        # =========================

        attractions = (
            await self.attraction_service.search_with_details(
                city=city,
                keyword='景点',
                limit=max(days * 3, 8),
            )
        )

        # =========================
        # 2. 酒店
        # =========================

        hotels = (
            await self.hotel_service.search(
                city=city,
                limit=5
            )
        )

        # =========================
        # 3. 天气
        # =========================

        weather = (
            await self.weather_service.query_weather(
                city
            )
        )
        
        return {
            "city": city,
            "start_date": start_date,
            "end_date": end_date,
            "days": days,
            "preferences": preferences or [],
            "attractions": attractions,
            "hotels": hotels,
            "weather": weather,
        }
