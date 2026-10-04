import asyncio

from capabilities.services import AttractionService
from config.settings import settings
from infrastructure.amap.gateways.poi import AmapPOIGateway
from infrastructure.mcp.clients.amap_client import AmapMCPClient


async def main():
    print("=" * 80)
    print("测试 AttractionService.search_with_details")
    print("=" * 80)

    client = AmapMCPClient(
        api_key=settings.AMAP_MAPS_API_KEY
    )

    await client.connect()

    # 1. 创建 Gateway
    poi_gateway = AmapPOIGateway(client)

    # 2. 创建 Service
    service = AttractionService(
        poi_gateway=poi_gateway
    )

    # 3. 搜索北京景点
    print("\n[1] 开始搜索北京景点...")

    try:
        attractions = await service.search_with_details(
            city="北京",
            keyword="景点",
            limit=5,
        )

    except Exception as e:
        print("\n❌ Service 执行失败")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {e}")
        raise

    # 4. 输出结果
    print("\n[2] Service 返回结果")
    print("-" * 80)

    print(f"数量: {len(attractions)}")

    for index, attraction in enumerate(
        attractions,
        start=1,
    ):
        print(f"\n[{index}]")
        print(f"id: {attraction.id}")
        print(f"name: {attraction.name}")
        print(f"address: {attraction.address}")

        print(
            "location:",
            attraction.location
        )

        print(
            "longitude:",
            attraction.location.longitude
        )

        print(
            "latitude:",
            attraction.location.latitude
        )

        print(
            "rating:",
            attraction.rating
        )

        print(
            "ticket_price:",
            attraction.ticket_price
        )

        print(
            "opening_hours:",
            attraction.opening_hours
        )

    print("\n" + "=" * 80)
    print("✅ AttractionService 测试完成")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())