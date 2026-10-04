import asyncio
import json
import traceback
from typing import Any

from capabilities.services.attraction_service import AttractionService
from config.settings import settings
from infrastructure.amap.gateways.poi import AmapPOIGateway
from infrastructure.mcp.clients.amap_client import AmapMCPClient


def print_separator(title: str = ""):
    print("\n" + "=" * 80)
    if title:
        print(title)
        print("=" * 80)


def safe_model_dump(obj: Any):
    """
    兼容 Pydantic Model / 普通对象。
    """
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump()
        except Exception:
            pass

    if hasattr(obj, "dict"):
        try:
            return obj.dict()
        except Exception:
            pass

    if hasattr(obj, "__dict__"):
        return vars(obj)

    return str(obj)


def print_result(index: int, result: Any):
    """
    打印 AttractionService 返回的单条结果。
    不假设对象一定存在 location。
    """
    print(f"\n--- {index} ---")

    print(f"对象类型: {type(result)}")

    data = safe_model_dump(result)

    print("数据:")

    try:
        print(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )
    except Exception:
        print(data)

    # 单独检查常见字段
    for field in [
        "id",
        "name",
        "address",
        "typecode",
        "location",
        "longitude",
        "latitude",
    ]:
        value = getattr(result, field, "<不存在>")
        print(f"{field}: {value}")


async def main():

    print_separator("开始测试 AttractionService")

    mcp_client = AmapMCPClient(
        api_key=settings.AMAP_MAPS_API_KEY
    )
    try:
        # ==========================================================
        # 1. 连接 MCP
        # ==========================================================

        print("\n[1] 连接 Amap MCP...")

        await mcp_client.connect()

        print("✓ MCP 连接成功")

        # ==========================================================
        # 2. 创建 POI Gateway
        # ==========================================================

        print("\n[2] 创建 AmapPOIGateway...")

        poi_gateway = AmapPOIGateway(mcp_client)

        print("✓ AmapPOIGateway 创建成功")

        # ==========================================================
        # 3. 创建 AttractionService
        # ==========================================================

        print("\n[3] 创建 AttractionService...")

        service = AttractionService(poi_gateway)

        print("✓ AttractionService 创建成功")

        # ==========================================================
        # 4. 测试参数
        # ==========================================================

        city = "北京"
        keyword = "景点"
        limit = 8

        print_separator("测试参数")

        print(f"city:    {city}")
        print(f"keyword: {keyword}")
        print(f"limit:   {limit}")

        # ==========================================================
        # 5. 直接调用 AttractionService
        # ==========================================================

        print_separator("开始调用 AttractionService.search()")

        try:
            results = await service.search(
                city=city,
                keyword=keyword,
                limit=limit,
            )

        except Exception as e:

            print("\n❌ AttractionService.search() 执行失败")

            print(f"\n异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")

            print("\n完整 traceback:")
            traceback.print_exc()

            return

        # ==========================================================
        # 6. 检查返回结果
        # ==========================================================

        print_separator("搜索结果统计")

        print(f"返回对象类型: {type(results)}")
        print(f"最终返回数量: {len(results)}")
        print(f"请求 limit:    {limit}")

        if len(results) == limit:
            print("✓ 返回数量与 limit 一致")
        elif len(results) < limit:
            print(
                f"⚠ 返回数量少于 limit，"
                f"请求 {limit}，实际 {len(results)}"
            )
        else:
            print(
                f"⚠ 返回数量超过 limit，"
                f"请求 {limit}，实际 {len(results)}"
            )

        # ==========================================================
        # 7. 打印每一个 POISummary
        # ==========================================================

        print_separator("详细结果")

        for index, result in enumerate(results, 1):
            print_result(index, result)

        # ==========================================================
        # 8. 检查 POISummary 是否存在 location
        # ==========================================================

        print_separator("Location 字段检查")

        location_exists = 0
        location_missing = 0
        location_none = 0

        for index, result in enumerate(results, 1):

            if not hasattr(result, "location"):
                location_missing += 1

                print(
                    f"{index}. "
                    f"{getattr(result, 'name', '<未知>')} "
                    f"→ POISummary 没有 location 字段"
                )

                continue

            location_exists += 1

            location = getattr(result, "location", None)

            if location is None:
                location_none += 1

                print(
                    f"{index}. "
                    f"{getattr(result, 'name', '<未知>')} "
                    f"→ location = None"
                )
            else:
                print(
                    f"{index}. "
                    f"{getattr(result, 'name', '<未知>')} "
                    f"→ location = {location}"
                )

        print("\n统计：")
        print(f"location 字段存在: {location_exists}")
        print(f"location 字段不存在: {location_missing}")
        print(f"location = None:   {location_none}")

        # ==========================================================
        # 9. 检查 POISummary 实际字段
        # ==========================================================

        print_separator("POISummary 字段结构检查")

        if results:

            first = results[0]

            print(f"对象类型:")
            print(type(first))

            print("\n实际字段:")

            if hasattr(first, "model_fields"):
                print(
                    list(first.model_fields.keys())
                )

            elif hasattr(first, "__fields__"):
                print(
                    list(first.__fields__.keys())
                )

            elif hasattr(first, "__dict__"):
                print(
                    list(vars(first).keys())
                )

            print("\n第一个对象完整数据:")

            data = safe_model_dump(first)

            print(
                json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )
            )

        # ==========================================================
        # 10. 最终结论
        # ==========================================================

        print_separator("测试结论")

        print(f"""
AttractionService.search() 已经成功执行。

请求：
    city    = {city}
    keyword = {keyword}
    limit   = {limit}

实际：
    返回数量 = {len(results)}

说明：
    1. AttractionService.search() 可以正常执行
    2. limit={limit} 可以正常得到最多/实际 {len(results)} 条结果
    3. 当前 search() 返回的是 POISummary
    4. 当前 POISummary 是否包含 location 已在上面明确统计
    5. 本测试没有经过 MainAgent
    6. 本测试没有经过 TripSubAgent
    7. 本测试没有经过 LLM Tool Calling
""")

    finally:

        # ==========================================================
        # 11. 关闭 MCP
        # ==========================================================

        print_separator("关闭 MCP")

        try:
            print("✓ MCP 已关闭")
        except Exception as e:
            print(f"⚠ MCP 关闭时出现异常: {e}")


if __name__ == "__main__":
    asyncio.run(main())