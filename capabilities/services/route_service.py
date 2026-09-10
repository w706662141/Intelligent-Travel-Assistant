from infrastructure.amap.gateways.route import (
    AmapRouteGateway,
)


class RouteService:

    def __init__(self,
                 route_gateway: AmapRouteGateway):
        self.route_gateway = route_gateway

    async def walking(
            self,
            origin_address: str,
            destination_address: str,
            city: str | None = None,
    ):
        return await self.route_gateway.walking_by_address(
            origin_address=origin_address,
            destination_address=destination_address,
            origin_city=city,
            destination_city=city,
        )

    async def driving(self,
                      origin_address: str,
                      destination_address: str,
                      city: str | None = None,
                      ):
        return await self.route_gateway.driving_by_address(
            origin_address=origin_address,
            destination_address=destination_address,
            origin_city=city,
            destination_city=city,
        )

    async def bicycling(
            self,
            origin_address: str,
            destination_address: str,
            city: str | None = None,
    ):
        return await self.route_gateway.bicycling_by_address(
            origin_address=origin_address,
            destination_address=destination_address,
            origin_city=city,
            destination_city=city,
        )

    async def transit(
            self,
            origin_address: str,
            destination_address: str,
            city: str,
    ):
        return await self.route_gateway.transit_by_address(
            origin_address=origin_address,
            destination_address=destination_address,
            origin_city=city,
            destination_city=city,
        )
