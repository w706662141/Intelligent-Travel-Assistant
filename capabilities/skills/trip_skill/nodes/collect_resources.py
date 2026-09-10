from capabilities.services import AttractionService, HotelService, MealService, WeatherService


class CollectResourcesNode:

    def __init__(
            self,
            attraction_service: AttractionService,
            hotel_service: HotelService,
            meal_service: MealService,
            weather_service: WeatherService
    ):

        self.attraction_service = attraction_service
        self.hotel_service = hotel_service
        self.meal_service = meal_service
        self.weather_service = weather_service

    async def __call__(self, state):
        city = state['city']

        attractions = await self.attraction_service.search_with_details(
            city,
            keyword='景点',
            limit=5)

        hotels = await self.hotel_service.search(
            city=city,
            limit=5
        )

        weather = await self.weather_service.query_weather(
            city=city
        )

        return {
            "attractions": attractions,
            "hotels": hotels,
            "weather": weather,
        }
