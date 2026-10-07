from capabilities.services.geocode_service import (
    GeocodeService,
)

from schemas.meal import Meal

from infrastructure.amap.gateways.poi import (
    AmapPOIGateway,
)

from infrastructure.amap.mappers.poi import (
    AmapPOIMapper,
)


class MealService:

    def __init__(
        self,
        poi_gateway: AmapPOIGateway,
        geocode_service: GeocodeService,
    ):
        self.poi_gateway = poi_gateway
        self.geocode_service = geocode_service

    async def search_nearby(
        self,
        address: str,
        meal_type: str,
        radius: str = "1000",
        limit: int = 5,
    ) -> list[Meal]:

        # ======================================================
        # Geocode
        # ======================================================

        location = (
            await self.geocode_service.geocode(
                address
            )
        )

        if location is None:

            raise RuntimeError(
                f"无法解析餐饮搜索位置: "
                f"{address}"
            )

        location_str = (
            f"{location.longitude},"
            f"{location.latitude}"
        )

        print(
            "[MealService] "
            f"geocoded={address} "
            f"-> {location_str}"
        )

        # ======================================================
        # Nearby Search
        # ======================================================

        data = (
            await self.poi_gateway.around_search(
                location=location_str,
                radius=radius,
                keywords="餐厅",
            )
        )

        summaries = (
            AmapPOIMapper.summaries(
                data
            )
        )

        # ======================================================
        # Build Domain
        # ======================================================

        result = []

        for poi in summaries[:limit]:

            result.append(
                Meal(
                    type=meal_type,
                    name=poi.name,
                    address=poi.address,
                )
            )

        return result