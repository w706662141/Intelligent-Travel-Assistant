from typing import Any

from schemas.attraction import Attraction
from schemas.location import Location
from schemas.poi import POIDetail, POISummary


class AmapPOIMapper:

    @staticmethod
    def _to_string(value: Any) -> str:
        """
        将高德 API 返回的可能为非字符串的数据
        安全转换为字符串。

        None / 空列表 / 空字典 -> ""
        其他类型 -> str(value)
        """

        if value is None:
            return ""

        if isinstance(value, str):
            return value

        if isinstance(value, (list, dict)):

            if not value:
                return ""

            return str(value)

        return str(value)

    @staticmethod
    def summaries(data: dict[str, Any],
                  ) -> list[POISummary]:
        pois = data.get(
            'pois',
            [],
        )
        if not isinstance(pois, list):
            return []

        result = []

        for poi in pois:
            if not isinstance(poi, dict):
                continue

            if not poi.get("id"):
                continue

            if not poi.get("name"):
                continue

            result.append(
                POISummary(
                    id=poi["id"],
                    name=poi["name"],
                    address=AmapPOIMapper._to_string(
                        poi.get("address")
                    ),
                    typecode=AmapPOIMapper._to_string(
                        poi.get("typecode")
                    ),
                )
            )

        return result

    @staticmethod
    def detail(
            data: dict[str, Any],
    ) -> POIDetail:
        rating = data.get("rating")

        try:
            rating = (
                float(rating)
                if rating not in (None, "")
                else None
            )
        except (ValueError, TypeError):
            rating = None

        return POIDetail(
            id=data.get("id"),
            name=data.get("name"),
            location=data.get("location"),
            address=data.get("address"),
            city=data.get("city"),
            type=data.get("type"),
            alias=data.get("alias"),
            cost=data.get("cost"),
            opentime2=data.get("opentime2"),
            level=data.get("level"),
            rating=rating,
            ticket_ordering=data.get("ticket_ordering")
        )


    @staticmethod
    def to_attraction(
        detail: POIDetail,
    ) -> Attraction:

        location = None

        if detail.location:

            try:
                longitude, latitude = (
                    detail.location.split(",")
                )

                location = Location(
                    longitude=float(longitude),
                    latitude=float(latitude),
                )

            except (
                ValueError,
                TypeError,
            ):
                location = None

        ticket_price = 0

        if detail.cost:

            try:
                ticket_price = int(
                    float(detail.cost)
                )
            except (
                ValueError,
                TypeError,
            ):
                ticket_price = 0

        return Attraction(
            id=detail.id,
            name=detail.name,
            address=detail.address,
            location=location,
            description=detail.alias or "",
            category=detail.type or "景点",
            rating=detail.rating,
            ticket_price=ticket_price,
            opening_hours=(
                detail.opentime2
                or None
            ),
        )