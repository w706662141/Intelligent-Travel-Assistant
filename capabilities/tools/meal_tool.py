from langchain_core.tools import tool
from pydantic import BaseModel, Field

MEAL_TYPE_OPTIONS = ("breakfast", "lunch", "dinner")


class SearchNearbyMealsInput(BaseModel):
    """搜索附近餐厅的输入参数"""

    place: str = Field(
        ...,
        description="景点、地址、商圈名称，例如：故宫、王府井、北京南站",
    )
    meal_type: str = Field(
        default="lunch",
        description=f"用餐时段，可选值: {', '.join(MEAL_TYPE_OPTIONS)}",
    )


def create_meal_tools(
        meal_service,
):
    @tool(args_schema=SearchNearbyMealsInput)
    async def search_nearby_meals(
            place: str,
            meal_type: str = 'lunch'
    ):
        """
        搜索指定位置附近的餐厅。
        """

        meals = await meal_service.search_nearby(
            address=place,
            meal_type=meal_type,
        )

        return [
            meal.model_dump()
            for meal in meals
        ]

    return [
        search_nearby_meals,
    ]
