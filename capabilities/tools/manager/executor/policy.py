from dataclasses import dataclass


@dataclass
class ToolExecutionPolicy:
    """
    Tool 执行策略。

    负责描述：
    - 最大尝试次数
    - Retry 间隔
    - 最大等待时间
    - 是否启用 jitter
    """

    max_attempts: int = 3

    base_delay: float = 1.0

    max_delay: float = 10.0

    jitter: bool = True

    retry_timeout: bool = True

    retry_network_error: bool = True

    retry_rate_limit: bool = True

    retry_server_error: bool = True

    retry_mcp_error: bool = True

    retry_unknown_error: bool = False

    def should_retry(
            self,
            *,
            error_type: str,
            attempt: int,
    ) -> bool:
        # 已经达到最大尝试次数
        if attempt >= self.max_attempts:
            return False

        mapping = {
            "timeout": self.retry_timeout,
            "network_error": self.retry_network_error,
            "rate_limit": self.retry_rate_limit,
            "server_error": self.retry_server_error,
            "mcp_error": self.retry_mcp_error,
            "unknown_error": self.retry_unknown_error,
        }

        return mapping.get(
            error_type,
            False,
        )