import asyncio

from config.settings import settings

from infrastructure.mcp.clients.amap_client import (
    AmapMCPClient,
)

from infrastructure.amap.gateways.poi import (
    AmapPOIGateway,
)

from capabilities.services.attraction_service import (
    AttractionService,
)


from capabilities.services.meal_service import MealService

from capabilities.services.hotel_service import HotelService

async def main():
    client = AmapMCPClient(
        api_key=settings.AMAP_MAPS_API_KEY,
    )

    await client.connect()

    # =========================
    # POI
    # =========================

    poi_gateway = AmapPOIGateway(
        client
    )

    # attraction_service = (
    #     AttractionService(
    #         poi_gateway
    #     )
    # )

    hotel_service = (
        HotelService(
            poi_gateway
        )
    )

    # attractions = (
    #     await attraction_service
    #         .search(
    #         city="北京",
    #         limit=3,
    #     )
    # )

    hotels = (
        await hotel_service.search(
            city='北京'
        )
    )

    print(
        "\n========== Attractions =========="
    )

    # for attraction in attractions:
    #     print(
    #         attraction.model_dump_json(
    #             indent=2,
    #             ensure_ascii=False,
    #         )
    #     )
    for meal in hotels:
        print(
            meal.model_dump_json(
                indent=2,
                ensure_ascii=False,
            )
        )

    # =========================
    # Weather
    # =========================

    # weather_gateway = (
    #     AmapWeatherGateway(
    #         client
    #     )
    # )
    #
    # weather_service = (
    #     WeatherService(
    #         weather_gateway
    #     )
    # )
    #
    # weather = await weather_service.query_weather(
    #     "北京"
    # )
    #
    # print(
    #     "\n========== Weather =========="
    # )
    #
    # for item in weather:
    #
    #     print(
    #         item.model_dump_json(
    #             indent=2,
    #             ensure_ascii=False,
    #         )
    #     )


if __name__ == "__main__":
    asyncio.run(main())
