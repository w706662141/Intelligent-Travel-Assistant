from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ToolErrorAction(str, Enum):
    """
    ToolExecutor 对错误采取的动作。
    """

    RETRY = 'retry'
    ABORT = 'abort'
    ASK_AGENT = 'ask_agent'


class ToolErrorType(str, Enum):
    """
    Tool执行错误类型
    """

    TOOL_NOT_FOUND = 'tool_not_found'

    VALIDATION_ERROR = 'validation_error'

    TIMEOUT = 'timeout'

    NETWORK_ERROR = 'network_error'

    RATE_LIMIT = "rate_limit"

    SERVER_ERROR = "server_error"

    AUTH_ERROR = "auth_error"

    NOT_FOUND = "not_found"

    CLIENT_ERROR = "client_error"

    MCP_ERROR = "mcp_error"

    BUSINESS_ERROR = "business_error"

    UNKNOWN_ERROR = "unknown_error"

    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"


@dataclass
class ToolExecutionError:
    """
    Tool 执行错误模型。

    这个类只描述错误，不负责处理错误。
    """
    tool_name: str

    error_type: ToolErrorType

    message: str

    action: ToolErrorAction

    attempt: int = 1

    retryable: bool = False

    requires_agent_decision: bool = False

    status_code: Optional[int] = None

    original_exception: Optional[Exception] = None