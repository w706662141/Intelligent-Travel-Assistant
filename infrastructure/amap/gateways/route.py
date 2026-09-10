from typing import Any

from infrastructure.mcp.clients.amap_client import AmapMCPClient
from infrastructure.amap.response_parser import AmapResponseParser


class AmapRouteGateway:

    def __init__(self,
                 client: AmapMCPClient):
        self.client = client

    async def _call(self,
                    tool_name,
                    arguments: dict[str, Any]):
        result = await self.client.call_tool(
            tool_name,
            arguments
        )

        return AmapResponseParser.parse(result)

    # -------------------------
    # Walking
    # -------------------------

    async def walking_by_address(
            self,
            origin_address: str,
            destination_address: str,
            origin_city: str | None = None,
            destination_city: str | None = None):
        return await self._call(
            "maps_direction_walking_by_address",
            {
                "origin_address": origin_address,
                "destination_address": destination_address,
                "origin_city": origin_city,
                "destination_city": destination_city,
            },
        )

    async def walking_by_coordinates(
            self,
            origin: str,
            destination: str,
    ):
        return await self._call(
            "maps_direction_walking_by_coordinates",
            {
                "origin": origin,
                "destination": destination,
            },
        )

    # -------------------------
    # Driving
    # -------------------------

    async def driving_by_address(
            self,
            origin_address: str,
            destination_address: str,
            origin_city: str | None = None,
            destination_city: str | None = None,
    ):
        return await self._call(
            "maps_direction_driving_by_address",
            {
                "origin_address": origin_address,
                "destination_address": destination_address,
                "origin_city": origin_city,
                "destination_city": destination_city,
            },
        )

    async def driving_by_coordinates(
            self,
            origin: str,
            destination: str,
    ):
        return await self._call(
            "maps_direction_driving_by_coordinates",
            {
                "origin": origin,
                "destination": destination,
            },
        )

    # -------------------------
    # Bicycling
    # -------------------------
    async def bicycling_by_address(
            self,
            origin_address: str,
            destination_address: str,
            origin_city: str | None = None,
            destination_city: str | None = None,
    ):
        return await self._call(
            "maps_bicycling_by_address",
            {
                "origin_address": origin_address,
                "destination_address": destination_address,
                "origin_city": origin_city,
                "destination_city": destination_city,
            },
        )

    async def bicycling_by_coordinates(
            self,
            origin_coordinates: str,
            destination_coordinates: str,
    ):
        return await self._call(
            "maps_bicycling_by_coordinates",
            {
                "origin_coordinates": origin_coordinates,
                "destination_coordinates": destination_coordinates,
            },
        )

    # -------------------------
    # Transit
    # -------------------------
    async def transit_by_address(
            self,
            origin_address: str,
            destination_address: str,
            origin_city: str,
            destination_city: str,
    ):
        return await self._call(
            "maps_direction_transit_integrated_by_address",
            {
                "origin_address": origin_address,
                "destination_address": destination_address,
                "origin_city": origin_city,
                "destination_city": destination_city,
            },
        )

    async def transit_by_coordinates(
            self,
            origin: str,
            destination: str,
            city: str,
            cityd: str,
    ):
        return await self._call(
            "maps_direction_transit_integrated_by_coordinates",
            {
                "origin": origin,
                "destination": destination,
                "city": city,
                "cityd": cityd,
            },
        )
