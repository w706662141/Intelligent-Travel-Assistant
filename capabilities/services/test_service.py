import asyncio
import time

from capabilities.services import MealService
from config.settings import settings

from infrastructure.mcp.clients.amap_client import AmapMCPClient
from infrastructure.amap.gateways.poi import AmapPOIGateway
from infrastructure.amap.gateways.geocode import AmapGeocodeGateway

from capabilities.services.geocode_service import GeocodeService
from capabilities.services.hotel_service import HotelService


async def main():

    # ==========================
    # MCP
    # ==========================

    client = AmapMCPClient(
        api_key=settings.AMAP_MAPS_API_KEY
    )

    await client.connect()

    # ==========================
    # Gateway
    # ==========================

    poi_gateway = AmapPOIGateway(
        client
    )

    geocode_gateway = AmapGeocodeGateway(
        client
    )

    # ==========================
    # Service
    # ==========================

    geocode_service = GeocodeService(
        geocode_gateway
    )

    meal_service = MealService(
        poi_gateway,
        geocode_service,
    )

    # ==========================
    # 测试城市酒店
    # ==========================

    print("\n==============================")
    print("测试 search")
    print("==============================")

    start = time.perf_counter()

    meals = await meal_service.search_nearby(
        address="南京",
        meal_type='午餐'
    )

    elapsed = time.perf_counter() - start

    print(
        f"耗时: {elapsed:.2f}s"
    )

    print(
        f"餐厅数量: {len(meals)}"
    )

    for meal in meals:
        print(
            meal.name,
            "|",
            meal.address,
        )


if __name__ == "__main__":
    asyncio.run(main())