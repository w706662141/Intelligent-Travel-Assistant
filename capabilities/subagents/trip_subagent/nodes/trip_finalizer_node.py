import asyncio
import json
import traceback

from langchain_core.messages import SystemMessage, HumanMessage

from capabilities.subagents.trip_subagent.state import (
    TripSubAgentState,
)
from schemas.trip_plan import TripPlan


class TripFinalizerNode:
    """
    TripSubAgent Finalizer。

    注意：

    Finalizer 不读取 Agent messages。

    Finalizer 只读取：

    1. request
    2. resource_data

    因此它完全不关心 Agent 内部是如何推理的。
    """

    def __init__(
            self,
            model,
            llm_timeout: int = 120,
    ):
        self.model = model
        self.llm_timeout = llm_timeout

    async def finalize(
            self,
            state: TripSubAgentState,
    ):
        print("\n========== TripSubAgent Finalizer ==========")
        print("[Finalizer] entered")

        request = state["request"]

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

            resource_data = state.get(
                "resource_data",
                []
            )

            finalizer_input = f"""
            用户旅行请求：

            城市：{request.city}
            开始日期：{request.start_date}
            结束日期：{request.end_date}
            人数：{request.travelers}
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

            已经获取的真实资源数据：

            {json.dumps(
                resource_data,
                ensure_ascii=False,
                indent=2
            )}

            请仅根据以上数据生成 TripPlan。
            """
            # 把 Agent 历史执行结果提供给 Finalizer
            execution_messages = [
                SystemMessage(
                    content=finalizer_prompt
                ),
                HumanMessage(
                    content=finalizer_input
                ),
            ]

            print(
                "[Finalizer] "
                f"input_length="
                f"{len(finalizer_input)}"
            )

            result = await asyncio.wait_for(
                self.model.ainvoke(
                    execution_messages
                ),
                timeout=self.llm_timeout,
            )

            if not isinstance(result, TripPlan):
                result = TripPlan.model_validate(
                    result
                )

            print("\n[Finalizer] generated TripPlan:")

            print(result)

            return {
                "final_result": result,
                "status": "completed",
                "error": None,
            }

        except asyncio.TimeoutError:

            print(
                "\n========== "
                "TripSubAgent Finalizer TIMEOUT "
                "=========="
            )

            print(
                "[Finalizer] "
                f"Timeout after "
                f"{self.llm_timeout}s"
            )
            return {
                "status": "failed",
                "error": (
                    "TripSubAgent Finalizer timeout: "
                    f"no response within "
                    f"{self.llm_timeout} seconds"
                ),
            }
        except Exception as exc:

            print(
                "\n========== "
                "TripSubAgent Finalizer ERROR "
                "=========="
            )

            print(
                f"[Finalizer] "
                f"Exception Type: "
                f"{type(exc).__name__}"
            )

            traceback.print_exc()

            print(
                f"[Finalizer] "
                f"Exception: {repr(exc)}"
            )

            traceback.print_exc()

            return {
                "status": "failed",
                "error": (
                    "TripSubAgent Finalizer failed: "
                    f"{exc}"
                ),
            }
