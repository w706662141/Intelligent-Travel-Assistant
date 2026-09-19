from langchain_core.tools import tool
from pydantic import BaseModel, Field


class DelegateTripTaskInput(BaseModel):

    task: str = Field(
        ...,
        description=(
            "需要旅行规划专家完成的复杂旅行任务。"
            "应包含用户的完整原始需求，"
            "例如目的地、日期、人数、预算、偏好、"
            "需要的景点、酒店、餐饮、交通等要求。"
        ),
    )


def create_trip_subagent_tool(
        trip_subagent,
):

    @tool(
        "delegate_trip_task",
        args_schema=DelegateTripTaskInput,
    )
    async def delegate_trip_task(
            task: str,
    ):
        """
        将复杂的完整旅行规划任务交给旅行规划专家。

        适用于：
        - 多日旅行规划
        - 完整旅行方案
        - 每日行程安排
        - 同时涉及景点、住宿、餐饮、天气、交通等
          多个旅行维度的复杂任务

        不适用于：
        - 单独查询景点
        - 单独查询酒店
        - 单独查询天气
        - 单独查询餐厅
        - 单独查询路线
        - 简单的少量旅行信息组合查询

        旅行规划专家会自主决定需要调用哪些旅行工具。
        """

        return await trip_subagent.run(task)

    return delegate_trip_task