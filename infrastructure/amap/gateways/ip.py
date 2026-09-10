from infrastructure.mcp.clients.amap_client import AmapMCPClient
from infrastructure.amap.response_parser import AmapResponseParser


class AmapIpGateway:

    def __init__(self,
                 client: AmapMCPClient):
        self.client = client

    async def locate(self,
                     ip):
        result = await self.client.call_tool(
            "maps_ip_location",
            {
                "ip": ip,
            },
        )

        return AmapResponseParser.parse(result)
