from langgraph.graph import MessagesState

from enum import Enum


class AgentStatus(str, Enum):

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    MAX_ITERATIONS = "max_iterations"
    # TripSubAgent 已完成
    SUBAGENT_COMPLETED = "subagent_completed"

    # TripSubAgent 执行失败
    SUBAGENT_FAILED = "subagent_failed"


class AgentState(MessagesState):

    iteration: int

    max_iterations: int

    status: AgentStatus

    executed_tool_names: list[str]

    error: str | None

    tool_call_count: int

    tool_result_count: int

    tool_error_count: int

    retry_count: int

    trip_request: str | None

    trip_plan: object | None
    # ==================================================
    # TripSubAgent 透传结果
    # ==================================================

    subagent_result: dict | None