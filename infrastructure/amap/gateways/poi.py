from typing import Any

from infrastructure.mcp.clients.amap_client import AmapMCPClient
from infrastructure.amap.response_parser import AmapResponseParser


class AmapPOIGateway:

    def __init__(
            self,
            client: AmapMCPClient,
    ):
        self.client = client

    async def text_search(
            self,
            keywords: str,
            city: str = "",
            citylimit: str = 'false', ):

        result = await self.client.call_tool(
            "maps_text_search",
            {
                "keywords": keywords,
                "city": city,
                "citylimit": citylimit,
            }
        )

        return AmapResponseParser.parse(result)

    async def around_search(
            self,
            location: str,
            radius: str = "1000",
            keywords: str = "",
    ) -> dict[str, Any]:
        result = await self.client.call_tool(
            "maps_around_search",
            {
                "location": location,
                "radius": radius,
                "keywords": keywords,

            },
        )

        return AmapResponseParser.parse(result)

    async def detail(self,
                     poi_id):
        result = await self.client.call_tool(
            "maps_search_detail",
            {
                "id": poi_id,
            },
        )

        return AmapResponseParser.parse(result)
