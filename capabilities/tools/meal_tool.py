from langchain_core.tools import tool
from pydantic import BaseModel, Field


MEAL_TYPE_OPTIONS = (
    "breakfast",
    "lunch",
    "dinner",
)


class SearchNearbyMealsInput(BaseModel):
    """搜索附近餐厅的输入参数"""

    city: str = Field(
        ...,
        description=(
            "当前旅行城市，例如'北京'、'上海'"
        ),
    )

    place: str = Field(
        ...,
        description=(
            "必须是之前 Tool 返回的真实地点，"
            "例如'故宫博物院'"
        ),
    )

    meal_type: str = Field(
        default="lunch",
        description=(
            "用餐时段，可选值: "
            f"{', '.join(MEAL_TYPE_OPTIONS)}"
        ),
    )


def create_meal_tools(
    meal_service,
):

    @tool(
        args_schema=SearchNearbyMealsInput
    )
    async def search_nearby_meals(
        city: str,
        place: str,
        meal_type: str = "lunch",
    ):
        """
        搜索当前旅行城市中指定真实地点附近的餐厅。

        place 必须来自之前 Tool 返回的真实地点。
        """

        meals = (
            await meal_service.search_nearby(
                address=f"{city}{place}",
                meal_type=meal_type,
            )
        )

        return [
            meal.model_dump()
            for meal in meals
        ]

    return [
        search_nearby_meals,
    ]