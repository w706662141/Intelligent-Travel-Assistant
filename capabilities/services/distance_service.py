from infrastructure.amap.gateways.distance import (
    AmapDistanceGateway,
)


class DistanceService:

    def __init__(
            self,
            gateway: AmapDistanceGateway,
    ):
        self.gateway = gateway

    async def calculate(
            self,
            origin: str,
            destination: str,
            distance_type: str = "1",
    ):
        data = await self.gateway.calculate(
            origins=origin,
            destination=destination,
            distance_type=distance_type
        )

        results = data.get(
            'results',
            [],
        )
        if not results:
            return None

        return results[0]
