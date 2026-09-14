from langgraph.graph import MessagesState

from enum import Enum


class TaskMode(str, Enum):

    TRAVEL_PLANNING = "travel_planning"

    DIRECT_QUERY = "direct_query"


class AgentStatus(str, Enum):
    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    MAX_ITERATIONS = "max_iterations"


class AgentState(MessagesState):
    iteration: int

    max_iterations: int

    status: AgentStatus

    task_mode: TaskMode | None

    last_tool_name: str | None

    error: str | None

    tool_call_count: int

    tool_result_count: int

    tool_error_count: int

    retry_count: int

    trip_request: str | None

    trip_plan: object | None
