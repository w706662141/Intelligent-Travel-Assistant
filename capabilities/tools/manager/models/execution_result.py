from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
from capabilities.tools.manager.models.tool_error import ToolExecutionError


@dataclass
class ExecutionResult:
    """
    Tool 执行结果。

    注意：
    这里不依赖 LangChain ToolMessage。
    """

    success: bool

    result: Any = None

    error: Optional[ToolExecutionError] = None

    attempt: int = 1

    @classmethod
    def success_result(
            cls,
            result: Any,
            attempt: int = 1,
    ) -> ExecutionResult:
        return cls(
            success=True,
            result=result,
            attempt=attempt
        )

    @classmethod
    def failure_result(
            cls,
            error: ToolExecutionError,
    ) -> ExecutionResult:
        return cls(
            success=False,
            error=error,
            attempt=error.attempt
        )