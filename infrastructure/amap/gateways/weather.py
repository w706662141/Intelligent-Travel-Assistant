from infrastructure.mcp.clients.amap_client import AmapMCPClient
from infrastructure.amap.response_parser import AmapResponseParser


class AmapWeatherGateway:

    def __init__(
            self,
            client: AmapMCPClient):
        self.client = client

    async def query(self,
                    city):
        result = await self.client.call_tool(
            "maps_weather",
            {
                'city': city
            }

        )

        return AmapResponseParser.parse(result)
