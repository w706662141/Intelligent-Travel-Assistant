from infrastructure.mcp.clients.amap_client import AmapMCPClient
from infrastructure.amap.response_parser import AmapResponseParser


class AmapDistanceGateway:
    def __init__(self,
                 client: AmapMCPClient
                 ):
        self.client = client

    async def calculate(self,
                        origins: str,
                        destination: str,
                        distance_type: str = '1'):
        result = await self.client.call_tool(
            "maps_distance",
            {
                "origins": origins,
                "destination": destination,
                "type": distance_type,
            },
        )

        return AmapResponseParser.parse(result)
