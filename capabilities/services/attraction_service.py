import asyncio
from asyncio.log import logger

from config.rate_limiter import RateLimiter
from schemas.attraction import Attraction
from schemas.poi import POISummary

from infrastructure.amap.gateways.poi import (
    AmapPOIGateway,
)
from infrastructure.amap.mappers.poi import (
    AmapPOIMapper,
)


class AttractionService:

    def __init__(
            self,
            poi_gateway: AmapPOIGateway
    ):
        self.poi_gateway = poi_gateway

        self.detail_rate_limiter = RateLimiter(interval=0.4)

    async def search(
            self,
            city: str,
            keyword: str = '景点',
            limit: int = 5, ) -> list[POISummary]:
        data = await self.poi_gateway.text_search(
            keywords=keyword,
            city=city,
            citylimit='true'
        )

        pois = AmapPOIMapper.summaries(data)

        return self._deduplicate(pois)[:limit]

    async def get_detail(self,
                         poi_id: str,
                         ) -> Attraction:

        data = await self.poi_gateway.detail(
            poi_id=poi_id
        )

        if not data or "error" in data:
            raise RuntimeError(
                f"获取 POI 详情失败: poi_id={poi_id}, error={data.get('error')}"
            )

        detail = AmapPOIMapper.detail(data)

        print("\n========== POI DETAIL OBJECT ==========")
        print(detail)
        print("id =", detail.id)
        print("name =", detail.name)
        print("location =", detail.location)
        print("=======================================\n")

        return AmapPOIMapper.to_attraction(detail)

    async def search_with_details(
            self,
            city: str,
            keyword: str = "景点",
            limit: int = 5,
    ) -> list[Attraction]:

        summaries = await self.search(
            city=city,
            keyword=keyword,
            limit=limit,
        )

        async def get_detail_safe(poi):
            try:
                # 控制每次 Detail 请求的启动间隔
                await self.detail_rate_limiter.acquire()

                return await self.get_detail(poi.id)
            except Exception as e:
                logger.warning(
                    "获取 POI [%s] 详情失败: %s",
                    poi.id,
                    e,
                )
                return None

        result = await asyncio.gather(
            *[
                get_detail_safe(poi)
                for poi in summaries
            ]
        )

        return [
            item
            for item in result
            if item is not None
        ]

        # for poi in summaries:
        #     try:
        #
        #         attraction = await self.get_detail(
        #             poi.id
        #         )
        #
        #         result.append(attraction)
        #
        #     except Exception as e:
        #         logger.warning("获取 POI [ID: %s] 详情失败，跳过该景点。原因: %s", poi.id, e)
        #         continue

        # return result

    @staticmethod
    def _deduplicate(
            pois: list[POISummary],
    ):

        result = []
        seen = set()

        for poi in pois:

            key = (
                    poi.name.strip()
                    + "|"
                    + poi.address.strip()
            )

            if key in seen:
                continue

            seen.add(key)
            result.append(poi)

        return result
