import asyncio
import random
import traceback

from capabilities.tools.manager.executor.error_classifier import ToolErrorClassifier
from capabilities.tools.manager.executor.policy import ToolExecutionPolicy
from capabilities.tools.manager.models.execution_result import ExecutionResult
from capabilities.tools.manager.models.tool_error import ToolExecutionError, ToolErrorAction, ToolErrorType


class RetryHandler:
    """
    Tool 执行 + Retry Handler。

    负责：
    - 调用 Tool
    - 捕获异常
    - 错误分类
    - 判断是否 Retry
    - Backoff
    """

    def __init__(
            self,
            policy: ToolExecutionPolicy,
            classifier: ToolErrorClassifier,
    ):
        self.policy = policy
        self.classifier = classifier

    async def execute(
            self,
            *,
            tool,
            tool_name: str,
            args: dict,
    ) -> ExecutionResult:

        last_error = None

        for attempt in range(1, self.policy.max_attempts + 1):

            try:
                print(
                    f"\n[RetryHandler] "
                    f"Executing tool={tool_name}, "
                    f"attempt={attempt}"
                )
                result = await tool.ainvoke(
                    args
                )

                print(
                    f"[RetryHandler] "
                    f"Tool {tool_name} succeeded"
                )

                return ExecutionResult.success_result(
                    result=result,
                    attempt=attempt,
                )

            except Exception as exc:
                # ==========================================
                # 调试阶段：打印完整原始异常
                # ==========================================

                print("\n" + "=" * 80)
                print("[RetryHandler] TOOL EXECUTION ERROR")
                print("=" * 80)

                print("Tool:", tool_name)
                print("Attempt:", attempt)
                print("Exception Type:", type(exc).__name__)
                print("Exception:", repr(exc))

                print("\n--- Traceback ---")
                traceback.print_exc()

                print("=" * 80 + "\n")

                error_type, action = (
                    self.classifier.classify(
                        exc
                    )
                )

                print(
                    "[RetryHandler] "
                    f"classified as={error_type.value}, "
                    f"action={action.value}"
                )

                error = ToolExecutionError(
                    tool_name=tool_name,
                    error_type=error_type,
                    message=str(exc),
                    action=action,
                    attempt=attempt,
                    retryable=(
                            action == ToolErrorAction.RETRY
                    ),
                    requires_agent_decision=(
                            action == ToolErrorAction.ASK_AGENT
                    ),
                    status_code=(
                        self.classifier.get_status_code(exc)
                    ),

                    original_exception=exc,
                )
                last_error = error

                # ==================================
                # 不允许 Retry
                # ==================================

                if action != ToolErrorAction.RETRY:
                    return ExecutionResult.failure_result(error)

                # ==================================
                # Policy 判断
                # ==================================

                should_retry = (
                    self.policy.should_retry(
                        error_type=(
                            error_type.value
                        ),
                        attempt=attempt,
                    )
                )

                if not should_retry:
                    error.error_type = (
                        ToolErrorType.MAX_RETRIES_EXCEEDED
                    )

                    error.action = (
                        ToolErrorAction.ABORT
                    )
                    error.retryable = False

                    return ExecutionResult.failure_result(error)

                # ==================================
                # Backoff
                # ==================================

                delay = self._calculate_delay(
                    attempt
                )

                print(
                    f"[RetryHandler] "
                    f"Retrying in {delay:.2f}s..."
                )

                await asyncio.sleep(
                    delay
                )
        if last_error is not None:
            return ExecutionResult.failure_result(
                last_error
            )

        raise RuntimeError(
            "RetryHandler reached unreachable state."
        )

    # ==================================================
    # Backoff
    # ==================================================

    def _calculate_delay(
            self,
            attempt: int,
    ) -> float:

        delay = min(
            self.policy.base_delay
            * (2 ** (attempt - 1)),
            self.policy.max_delay,
        )

        if self.policy.jitter:
            delay *= (
                    0.5 + random.random()
            )

        return delay
