import asyncio
import traceback

from langchain_core.messages import SystemMessage, HumanMessage

from capabilities.subagents.trip_subagent.state import (
    TripSubAgentState,
)
from schemas.trip_plan import TripPlan


class TripFinalizerNode:

    def __init__(
        self,
        model,
    ):
        self.model = model

    async def finalize(
        self,
        state: TripSubAgentState,
    ):

        request = state["request"]

        messages = state["messages"]

        finalizer_prompt = f"""
你是旅行规划结果整理器。

你的任务不是继续搜索，也不是调用工具。

你需要根据：

1. 用户的结构化旅行请求
2. TripSubAgent 已经执行得到的 Tool 结果

生成最终的 TripPlan。

==============================
【旅行请求】
==============================

城市：
{request.city}

开始日期：
{request.start_date}

结束日期：
{request.end_date}

出行人数：
{request.travelers}

预算：
{
    request.budget
    if request.budget is not None
    else "未指定"
}

旅行偏好：
{
    ", ".join(request.preferences)
    if request.preferences
    else "未指定"
}

==============================
【严格要求】
==============================

1. 只使用已经获得的 Tool 数据。

2. 不允许编造：
   - 景点
   - 酒店
   - 餐厅
   - POI ID
   - 经纬度
   - 天气
   - 价格
   - 评分

3. 如果 Tool 没有返回某项信息，
   可以留空或使用模型允许的默认值，
   不得虚构实时数据。

4. 必须保持城市、日期与用户请求一致。

5. 根据实际旅行天数生成 days。

6. 每一天应该对应一个日期。

7. DayPlan 中：
   - attractions 使用 Tool 返回的真实景点
   - hotel 使用 Tool 返回的真实酒店
   - meals 使用 Tool 返回的真实餐厅

8. routes 不需要由你规划。
   TripSubAgent 不负责路线规划。

9. overall_suggestions 应该总结：
   - 行程特点
   - 天气注意事项
   - 住宿建议
   - 餐饮建议
   - 其他必要提醒

10. 这是结构化结果生成阶段。
    不要输出 Markdown。
    不要解释过程。
    直接生成 TripPlan。
"""

        try:

            # 把 Agent 历史执行结果提供给 Finalizer
            execution_messages = [
                SystemMessage(
                    content=finalizer_prompt
                ),
                *messages,
                HumanMessage(
                    content=(
                        "请根据以上旅行请求和已经获取的 "
                        "Tool 数据，生成最终 TripPlan。"
                    )
                ),
            ]

            result = await asyncio.wait_for(
                self.model.ainvoke(
                    execution_messages
                ),
                timeout=60,
            )

            if not isinstance(result, TripPlan):
                result = TripPlan.model_validate(
                    result
                )

            return {
                "final_result": result,
                "status": "completed",
                "error": None,
            }

        except Exception as exc:

            print(
                "\n========== "
                "TripSubAgent Finalizer ERROR "
                "=========="
            )

            traceback.print_exc()

            return {
                "status": "failed",
                "error": (
                    "TripSubAgent Finalizer failed: "
                    f"{exc}"
                ),
            }