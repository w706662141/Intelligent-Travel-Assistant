import inspect

from langchain_core.messages import ToolMessage

from capabilities.tools.manager.executor.retry import RetryHandler
from capabilities.tools.manager.models.tool_error import ToolExecutionError, ToolErrorType, ToolErrorAction
from capabilities.tools.manager.tool_registry import ToolRegistry


class ToolExecutor:
    """
    Tool 执行器。

    职责：
    1. 根据 tool_call 查找 Tool
    2. 准备 Tool 参数
    3. 将 Tool 执行交给 RetryHandler
    4. 将 ExecutionResult 转换为 ToolMessage

    不负责：
    - Tool 实际调用
    - Retry
    - Backoff
    - 异常分类
    - Retry 策略
    """

    def __init__(self,
                 registry: ToolRegistry,
                 retry_handler: RetryHandler,
                 ):
        self.registry = registry
        self.retry_handler = retry_handler

    async def execute(
            self,
            tool_call,
            messages=None
    ) -> ToolMessage:

        tool_name = tool_call['name']
        tool_call_id = tool_call['id']

        # 不直接修改 tool_call["args"]
        args = dict(tool_call.get('args', {}))

        tool = self.registry.get(tool_name)

        if tool is None:
            error = ToolExecutionError(
                tool_name=tool_name,
                error_type=ToolErrorType.TOOL_NOT_FOUND,
                message=f"Tool not found: {tool_name}",
                action=ToolErrorAction.ABORT,
                attempt=1,
                retryable=False,
                requires_agent_decision=False,
            )

            return self._build_error_message(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                error=error
            )

        # ==========================================
        # 2. 注入 messages
        # ==========================================

        self._inject_messages(
            tool=tool,
            args=args,
            messages=messages,
        )

        result = await self.retry_handler.execute(
            tool=tool,
            tool_name=tool_name,
            args=args,
        )

        return self._to_tool_message(
            result=result,
            tool_call_id=tool_call_id,
            tool_name=tool_name,
        )

    # ==================================================
    # Error → ToolMessage
    # ==================================================
    @staticmethod
    def _build_error_message(*,
                             tool_call_id: str,
                             tool_name: str,
                             error: ToolExecutionError) -> ToolMessage:
        content = {
            "success": False,
            "tool": tool_name,
            "error_type": error.error_type.value,
            "error": error.message,
            "action": error.action.value,
            "retryable": error.retryable,
            "attempt": error.attempt,
            "requires_agent_decision": (
                error.requires_agent_decision
            ),
        }

        if error.status_code is not None:
            content['status_code'] = (
                error.status_code
            )

        return ToolMessage(
            content=str(content),
            tool_call_id=tool_call_id,
            name=tool_name
        )

    @staticmethod
    def _inject_messages(
            tool,
            args,
            messages) -> None:

        if messages is None:
            return

        try:
            signature = inspect.signature(
                tool.invoke
            )

            if "messages" in signature.parameters:
                args["messages"] = messages
        except(
                TypeError,
                ValueError,
        ):
            pass

    @staticmethod
    def _to_tool_message(
            *,
            result,
            tool_call_id,
            tool_name) -> ToolMessage:
        if result.success:
            return ToolMessage(
                content=str(
                    result.result
                ),
                tool_call_id=tool_call_id,
                name=tool_name,
            )

        return ToolExecutor._build_error_message(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            error=result.error,
        )
