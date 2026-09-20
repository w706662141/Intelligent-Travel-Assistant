from langgraph.graph import MessagesState

from capabilities.subagents.trip_subagent.schemas.request import TripPlanRequest


class TripSubAgentState(MessagesState):
    """
    TripSubAgent 运行状态。

    TripSubAgent 与 MainAgent 的职责不同：

    MainAgent:
        判断用户请求应该由谁处理。

    TripSubAgent:
        负责复杂旅行任务内部的自主推理与 Tool Calling。
    """

    request: TripPlanRequest

    iteration: int

    max_iterations: int

    status: str

    error: str | None

    tool_call_count: int

    tool_result_count: int