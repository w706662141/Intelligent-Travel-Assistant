from typing import Optional, List

from pydantic import BaseModel, Field

from schemas.attraction import Attraction
from schemas.hotel import Hotel
from schemas.meal import Meal


class DayPlan(BaseModel):
    date: str = Field(..., description='日期')
    day_index: int = Field(..., description='第几天(从0开始)')
    description: str = Field(..., description='当日行程描述')
    accommodation: str = Field(..., description='住宿安排')
    hotel: Hotel | None = Field(default=None,description='酒店信息')
    attractions: List[Attraction] = Field(default_factory=list, description="景点列表")
    meals: List[Meal] = Field(default_factory=list, description="餐饮安排")
    routes: list[dict] = Field(
        default_factory=list,
        description="当天景点之间的路线",
    )