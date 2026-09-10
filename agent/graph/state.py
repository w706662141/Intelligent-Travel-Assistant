from langgraph.graph import MessagesState

from enum import Enum


class AgentStatus(str, Enum):

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    MAX_ITERATIONS = "max_iterations"


class AgentState(MessagesState):
    iteration: int

    max_iterations: int

    status: AgentStatus

    error: str | None

    tool_call_count: int

    tool_result_count: int

    tool_error_count: int

    retry_count: int

    trip_request: str | None

    trip_plan: object | None
