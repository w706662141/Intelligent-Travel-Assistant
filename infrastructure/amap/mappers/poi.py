from typing import Any

from schemas.attraction import Attraction
from schemas.hotel import Hotel
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
    def _parse_location(
        value: Any,
    ) -> Location | None:
        """
        解析高德 POI 经纬度。

        高德常见格式：

            "118.795246,32.061061"

        同时兼容：

            {
                "longitude": 118.795246,
                "latitude": 32.061061
            }

        如果数据缺失或格式非法，返回 None。
        """

        if value is None:
            return None

        # ------------------------------------------
        # 1. 已经是 Location
        # ------------------------------------------

        if isinstance(value, Location):
            return value

        # ------------------------------------------
        # 2. dict
        # ------------------------------------------

        if isinstance(value, dict):

            longitude = (
                value.get("longitude")
                or value.get("lon")
            )

            latitude = (
                value.get("latitude")
                or value.get("lat")
            )

            if longitude is None or latitude is None:
                return None

            try:
                return Location(
                    longitude=float(longitude),
                    latitude=float(latitude),
                )
            except (
                ValueError,
                TypeError,
            ):
                return None

        # ------------------------------------------
        # 3. 字符串
        # ------------------------------------------

        if isinstance(value, str):

            value = value.strip()

            if not value:
                return None

            parts = value.split(",")

            if len(parts) != 2:
                return None

            longitude_str = parts[0].strip()
            latitude_str = parts[1].strip()

            if not longitude_str or not latitude_str:
                return None

            try:

                longitude = float(
                    longitude_str
                )

                latitude = float(
                    latitude_str
                )

                return Location(
                    longitude=longitude,
                    latitude=latitude,
                )

            except (
                ValueError,
                TypeError,
            ):
                return None

        return None

    @staticmethod
    def summaries(
        data: dict[str, Any],
    ) -> list[POISummary]:

        pois = data.get(
            "pois",
            [],
        )

        if not isinstance(
            pois,
            list,
        ):
            return []

        result = []

        for poi in pois:

            if not isinstance(
                poi,
                dict,
            ):
                continue

            if not poi.get("id"):
                continue

            if not poi.get("name"):
                continue

            result.append(
                POISummary(
                    id=poi["id"],
                    name=poi["name"],
                    address=(
                        AmapPOIMapper._to_string(
                            poi.get("address")
                        )
                    ),
                    typecode=(
                        AmapPOIMapper._to_string(
                            poi.get("typecode")
                        )
                    ),
                )
            )

        return result

    @staticmethod
    def detail(
        data: dict[str, Any],
    ) -> POIDetail:

        print("\n========== POI DETAIL RAW DATA ==========")
        print("type:", type(data))
        print("data:", data)
        print("=========================================\n")

        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "高德 POI detail 返回数据不是 dict"
            )

        rating = data.get(
            "rating"
        )

        try:

            rating = (
                float(rating)
                if rating not in (
                    None,
                    "",
                )
                else None
            )

        except (
            ValueError,
            TypeError,
        ):
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
            ticket_ordering=data.get(
                "ticket_ordering"
            ),
        )

    @staticmethod
    def to_attraction(
        detail: POIDetail,
    ) -> Attraction:

        # ==========================================
        # 解析 POI 经纬度
        # ==========================================

        location = (
            AmapPOIMapper._parse_location(
                detail.location
            )
        )

        # ==========================================
        # 景点必须有有效坐标
        # ==========================================

        if location is None:

            raise ValueError(
                "POI 缺少有效 location："
                f"id={detail.id}, "
                f"name={detail.name}, "
                f"location={detail.location!r}"
            )

        # ==========================================
        # 门票价格
        # ==========================================

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

        # ==========================================
        # 构造 Attraction
        # ==========================================

        return Attraction(
            id=detail.id,
            name=detail.name,
            address=detail.address,
            location=location,
            recommended_duration=120,
            description=(
                detail.alias
                or ""
            ),
            category=(
                detail.type
                or "景点"
            ),
            rating=detail.rating,
            ticket_price=ticket_price,
            opening_hours=(
                detail.opentime2
                or None
            ),
        )

    @staticmethod
    def to_hotel(
        detail: POIDetail,
    ) -> Hotel:

        location = (
            AmapPOIMapper._parse_location(
                detail.location
            )
        )

        return Hotel(
            id=detail.id,
            name=detail.name or "",
            address=detail.address or "",
            location=location,
            rating=(
                str(detail.rating)
                if detail.rating is not None
                else ""
            ),
            type=detail.type or "",
        )