from infrastructure.mcp.clients.amap_client import AmapMCPClient
from infrastructure.amap.response_parser import AmapResponseParser


class AmapGeocodeGateway:

    def __init__(self,
                 client: AmapMCPClient):
        self.client = client

    async def geocode(
            self,
            address: str,
            city: str | None = None
    ):
        arguments = {
            'address': address,
        }

        if city:
            arguments['city'] = city


        result = await self.client.call_tool(
            "maps_geo",
            arguments
        )

        return AmapResponseParser.parse(result)

    async def reverse_geocode(
            self,
            location: str):
        result = await self.client.call_tool(
            "maps_regeocode",
            {
                "location": location
            },
        )

        return AmapResponseParser.parse(result)
