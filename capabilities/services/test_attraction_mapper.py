import asyncio
import json
import traceback

from capabilities.services.test_location import print_separator
from config.settings import settings
from infrastructure.amap.gateways.poi import AmapPOIGateway
from infrastructure.amap.mappers.poi import AmapPOIMapper
from infrastructure.mcp.clients.amap_client import AmapMCPClient

# 根据你项目实际的 mapper 文件修改这里


POI_IDS = [
    "B001907TGR",
    "B00190ANHZ",
    "B0FFHB821F",
    "B0FFGILZE9",
    "B00190BMRC",
]


def separator(title=""):
    print("\n" + "=" * 80)

    if title:
        print(title)
        print("=" * 80)


async def main():
    separator("测试 POI Detail → Attraction Mapper")

    client = AmapMCPClient(
        api_key=settings.AMAP_MAPS_API_KEY
    )

    try:

        # ======================================================
        # 1. MCP
        # ======================================================

        print("\n[1] 连接 MCP")

        await client.connect()

        print("✓ MCP 连接成功")

        # ======================================================
        # 2. Gateway
        # ======================================================

        gateway = AmapPOIGateway(client)

        print("✓ AmapPOIGateway 创建成功")

        # ======================================================
        # 3. Mapper
        # ======================================================

        mapper = AmapPOIMapper()

        print("✓ POIMapper 创建成功")

        # ======================================================
        # 4. 一个一个测试
        # ======================================================

        for index, poi_id in enumerate(POI_IDS, 1):

            separator(
                f"[{index}/{len(POI_IDS)}] {poi_id}"
            )

            try:

                # ------------------------------------------------
                # 获取真实 detail
                # ------------------------------------------------

                print(
                    f"\n获取 {poi_id} detail..."
                )

                detail = await gateway.detail(
                    poi_id
                )

                print("✓ Detail 获取成功")

                print("\nDetail 原始数据:")

                print(
                    json.dumps(
                        detail,
                        ensure_ascii=False,
                        indent=2,
                        default=str,
                    )
                )

                # ------------------------------------------------
                # 重点：检查 location
                # ------------------------------------------------

                raw_location = detail.get(
                    "location"
                )

                print(
                    f"\nMapper 输入 location:"
                    f" {raw_location!r}"
                )

                # ------------------------------------------------
                # Mapper
                # ------------------------------------------------

                print("\n开始执行 Mapper...")

                print('detail type', type(detail))

                attraction = mapper.to_attraction(
                    detail
                )

                print(
                    "\n✓ Mapper 转换成功"
                )

                print(
                    f"结果类型: "
                    f"{type(attraction)}"
                )

                if hasattr(
                        attraction,
                        "model_dump"
                ):

                    data = attraction.model_dump()

                else:

                    data = vars(attraction)

                print(
                    json.dumps(
                        data,
                        ensure_ascii=False,
                        indent=2,
                        default=str,
                    )
                )

                # ------------------------------------------------
                # 最终 location
                # ------------------------------------------------

                location = getattr(
                    attraction,
                    "location",
                    None,
                )

                print(
                    f"\n最终 Attraction.location:"
                    f" {location!r}"
                )

                if location is None:

                    print(
                        "❌ 找到了问题："
                        "Mapper 把正常 location 转成了 None"
                    )

                else:

                    print(
                        "✓ Attraction.location 正常"
                    )

            except Exception as e:

                print(
                    "\n❌ Mapper 转换失败"
                )

                print(
                    f"异常类型: "
                    f"{type(e).__name__}"
                )

                print(
                    f"异常信息: {e}"
                )

                print(
                    "\n完整 traceback:"
                )

                traceback.print_exc()

    finally:

        print_separator("关闭 MCP")

        try:

            print("✓ MCP 已关闭")

        except Exception as e:

            print(
                f"关闭 MCP 失败: {e}"
            )


if __name__ == "__main__":
    asyncio.run(main())
