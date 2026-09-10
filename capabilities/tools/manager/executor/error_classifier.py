import asyncio
from typing import Optional

from capabilities.tools.manager.models.tool_error import ToolErrorType, ToolErrorAction


class ToolErrorClassifier:
    """
    Tool 异常分类器。

    只负责判断：

    1. 错误类型
    2. 应该 RETRY / ABORT / ASK_AGENT

    不负责：
    - sleep
    - retry
    - Tool 调用
    """

    def classify(
            self,
            exc: Exception,
    ) -> tuple[
        ToolErrorType,
        ToolErrorAction,
    ]:
        # ==========================================
        # Validation Error
        # ==========================================

        if self._is_validation_error(exc):
            return (
                ToolErrorType.VALIDATION_ERROR,
                ToolErrorAction.ASK_AGENT,
            )

        # ==========================================
        # Timeout
        # ==========================================

        if self._is_timeout_error(exc):
            return (
                ToolErrorType.TIMEOUT,
                ToolErrorAction.RETRY,
            )

        # ==========================================
        # Network
        # ==========================================

        if self._is_network_error(exc):
            return (
                ToolErrorType.NETWORK_ERROR,
                ToolErrorAction.RETRY,
            )

        # ==========================================
        # HTTP
        # ==========================================

        status_code = self.get_status_code(exc)

        if status_code is not None:
            return self._classify_http_error(
                status_code
            )
        # ==========================================
        # MCP
        # ==========================================

        if self._is_mcp_error(exc):
            return (
                ToolErrorType.MCP_ERROR,
                ToolErrorAction.RETRY,
            )

        # ==========================================
        # Unknown
        # ==========================================

        return (
            ToolErrorType.UNKNOWN_ERROR,
            ToolErrorAction.ABORT
        )

    @staticmethod
    def _is_validation_error(exc: Exception) -> bool:

        name = exc.__class__.__name__

        return name in {
            "ValidationError",
            "SchemaValidationError",
        }

    @staticmethod
    def _is_timeout_error(exc: Exception) -> bool:

        return isinstance(
            exc,
            (
                TimeoutError,
                asyncio.TimeoutError,
            ),
        )

    @staticmethod
    def _is_network_error(exc: Exception) -> bool:

        if isinstance(
                exc, (
                        ConnectionError,
                        ConnectionResetError,
                        ConnectionAbortedError,
                        ConnectionRefusedError,
                ),
        ):
            return True

        name = exc.__class__.__name__.lower()

        message = str(exc).lower()

        keywords = (
            "connection",
            "network",
            "socket",
            "connect",
        )

        return (
                any(
                    keyword in name
                    for keyword in keywords
                )
                or
                any(
                    keyword in message
                    for keyword in keywords
                )
        )

    def _classify_http_error(
            self,
            status_code: int
    ) -> tuple[
        ToolErrorType,
        ToolErrorAction
    ]:

        if status_code == 400:
            return (
                ToolErrorType.CLIENT_ERROR,
                ToolErrorAction.ASK_AGENT
            )

        if status_code in (401, 403):
            return (
                ToolErrorType.AUTH_ERROR,
                ToolErrorAction.ABORT
            )

        if status_code == 404:
            return (
                ToolErrorType.NOT_FOUND,
                ToolErrorAction.ASK_AGENT
            )

        if status_code == 408:
            return (
                ToolErrorType.TIMEOUT,
                ToolErrorAction.RETRY,
            )

        if status_code == 429:
            return (
                ToolErrorType.RATE_LIMIT,
                ToolErrorAction.RETRY
            )

        if 500 <= status_code <= 599:
            return (
                ToolErrorType.SERVER_ERROR,
                ToolErrorAction.RETRY,
            )

        if 400 <= status_code <= 499:
            return (
                ToolErrorType.CLIENT_ERROR,
                ToolErrorAction.ASK_AGENT
            )

        return (
            ToolErrorType.UNKNOWN_ERROR,
            ToolErrorAction.ABORT
        )

    @staticmethod
    def _is_mcp_error(exc: Exception) -> bool:
        name = exc.__class__.__name__.lower()

        message = str(exc).lower()

        keywords = (
            "mcp",
            "session",
            "transport",
            "broken pipe",
            "server disconnected",
            "connection closed",
        )
        return (
                any(
                    keyword in name
                    for keyword in keywords
                )
                or
                any(
                    keyword in message
                    for keyword in keywords
                )
        )

    @staticmethod
    def get_status_code(exc: Exception) -> Optional[int]:

        status_code = getattr(
            exc,
            'status_code',
            None,
        )

        if status_code is not None:
            return status_code

        response = getattr(
            exc,
            'response',
            None,
        )

        if response is not None:
            return getattr(
                response,
                'status_code',
                None,
            )

        return None
