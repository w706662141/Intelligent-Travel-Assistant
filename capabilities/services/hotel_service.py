from capabilities.services.geocode_service import GeocodeService
from schemas.hotel import Hotel
from infrastructure.amap.gateways.poi import AmapPOIGateway
from infrastructure.amap.mappers.poi import AmapPOIMapper


class HotelService:

    def __init__(
            self,
            poi_gateway: AmapPOIGateway,
            geocode_service: GeocodeService,
    ):
        self.poi_gateway = poi_gateway
        self.geocode_service = geocode_service

    async def search(
            self,
            city: str,
            keyword: str = "酒店",
            limit: int = 10,
    ) -> list[Hotel]:

        data = await self.poi_gateway.text_search(
            keywords=keyword,
            city=city,
            citylimit="true",
        )

        summaries = AmapPOIMapper.summaries(data)

        summaries = summaries[:limit]

        result = []

        for poi in summaries:

            try:

                detail_data = (
                    await self.poi_gateway.detail(
                        poi.id
                    )
                )

                detail = AmapPOIMapper.detail(
                    detail_data
                )

                hotel = Hotel(
                    name=detail.name,
                    address=detail.address,
                    location=(
                        self._location(
                            detail.location
                        )
                    ),
                    rating=(
                        str(detail.rating)
                        if detail.rating is not None
                        else ""
                    ),
                    type=detail.type,
                )

                result.append(hotel)

            except Exception:
                continue

        return result

    async def search_hotel_nearby(
            self,
            address: str,
            radius: str = '1000',
            keyword: str = "酒店",
            limit: int = 5,
    ) -> list[Hotel]:

        location = await self.geocode_service.geocode(address)
        location_str = str(f'{location.longitude},{location.latitude}')

        data = await self.poi_gateway.around_search(
            location=location_str,
            radius=radius,
            keywords=keyword
        )

        summaries = AmapPOIMapper.summaries(data)

        summaries = summaries[:limit]

        result = []

        for poi in summaries:

            try:

                detail_data = (
                    await self.poi_gateway.detail(
                        poi.id
                    )
                )

                detail = AmapPOIMapper.detail(
                    detail_data
                )

                hotel = Hotel(
                    name=detail.name,
                    address=detail.address,
                    location=(
                        self._location(
                            detail.location
                        )
                    ),
                    rating=(
                        str(detail.rating)
                        if detail.rating is not None
                        else ""
                    ),
                    type=detail.type,
                )

                result.append(hotel)

            except Exception:
                continue

        return result

    @staticmethod
    def _location(value):

        if not value:
            return None

        try:
            longitude, latitude = value.split(",")

            from schemas.location import Location

            return Location(
                longitude=float(longitude),
                latitude=float(latitude),
            )

        except (ValueError, TypeError):
            return None
