from schemas.location import Location

from infrastructure.amap.gateways.geocode import AmapGeocodeGateway


class GeocodeService:

    def __init__(self,
                 gateway: AmapGeocodeGateway):
        self.gateway = gateway

    async def geocode(self,
                      address: str, ) -> Location | None:

        result = await self.gateway.geocode(address)

        geocodes = result.get(
            'return',
            []
        )

        if not geocodes:
            return None

        location = geocodes[0].get(
            'location'
        )

        if not location:
            return None

        try:
            longitude, latitude = (
                location.split(',')
            )

            return Location(
                longitude=float(longitude),
                latitude=float(latitude),
            )
        except(
                ValueError,
                TypeError
        ):
            return None