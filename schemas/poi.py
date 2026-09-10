from typing import Optional, Any

from pydantic import BaseModel, Field, field_validator


class POISummary(BaseModel):
    """
    maps_text_search / maps_around_search 的基础 POI。
    """

    id: str = Field(...)

    name: str = Field(...)

    address: str = Field(
        default="",
    )

    typecode: str = Field(
        default="",
    )


class POIDetail(BaseModel):
    """
    maps_search_detail 返回的详细 POI。
    """

    id: str

    name: str

    location: Optional[str] = None

    address: str = ""

    city: str = ""

    type: str = ""

    alias: str = ""

    cost: Optional[str] = None

    opentime2: str = ""

    level: str = ""

    rating: Optional[float] = None

    ticket_ordering: Optional[str] = None

    # 1. 针对必须是 str 类型的字段：将 None、[] 或其他空值统一转换为 ""
    @field_validator(
        "id",
        "name",
        "address",
        "city",
        "type",
        "alias",
        "opentime2",
        "level",
        mode="before",
    )
    @classmethod
    def sanitize_string_fields(cls, v: Any) -> str:
        # 如果是 None、空列表 []、空字典 {} 等伪假值，归一化为空字符串
        if not v and v != 0:
            return ""
        return str(v)

    # 2. 针对 Optional 字段：将 [] 或其他空结构统一转换为 None
    @field_validator(
        "location",
        "cost",
        "ticket_ordering",
        mode="before",
    )
    @classmethod
    def sanitize_optional_str_fields(cls, v: Any) -> Optional[str]:
        if not v and v != 0:
            return None
        return str(v)

    # 3. 针对数值型字段 (rating)：将 [], "", None 等清理为 None，合法数值正常转 float
    @field_validator("rating", mode="before")
    @classmethod
    def sanitize_float_field(cls, v: Any) -> Optional[float]:
        if v in (None, "", [], {}):
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None
