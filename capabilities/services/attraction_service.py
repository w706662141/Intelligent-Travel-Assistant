from asyncio.log import logger

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

        detail = AmapPOIMapper.detail(data)

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

        result = []

        for poi in summaries:
            try:

                attraction = await self.get_detail(
                    poi.id
                )

                result.append(attraction)

            except Exception as e:
                logger.warning("获取 POI [ID: %s] 详情失败，跳过该景点。原因: %s", poi.id, e)
                continue

        return result

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
