from contextlib import asynccontextmanager
from typing import AsyncIterator

from capabilities.tools.manager.build_tools import (
    build_tools_registry,
)
from capabilities.tools.manager.executor import (
    policy,
    error_classifier,
)
from capabilities.tools.manager.executor.retry import (
    RetryHandler,
)
from capabilities.tools.manager.tool_executor import (
    ToolExecutor,
)
from infrastructure.core.llm import (
    get_agnes_model,
)
from infrastructure.memory.redis_checkpointer import (
    create_redis_checkpointer,
)
from agent.react_agent import ReActAgent


class TravelAgentPipeline:
    """
    Travel Agent Pipeline。

    负责统一管理：

    LLM
    ToolRegistry
    ToolExecutor
    Redis Checkpointer
    ReActAgent
    """

    def __init__(
        self,
        model,
        tool_registry,
        tool_executor,
        checkpointer,
    ):
        self.model = model
        self.tool_registry = tool_registry
        self.tool_executor = tool_executor
        self.checkpointer = checkpointer

        self.agent = ReActAgent(
            model=model,
            tool_registry=tool_registry,
            tool_executor=tool_executor,
            checkpointer=checkpointer,
            max_iterations=10,
        )

    async def chat(
        self,
        message: str,
        thread_id: str,
    ) -> str:
        """
        多轮对话入口。

        同一个 thread_id：
            → 获取同一个 LangGraph checkpoint
            → 自动恢复历史上下文

        不同 thread_id：
            → 使用不同的 Redis checkpoint
            → 上下文相互隔离
        """

        return await self.agent.run(
            user_input=message,
            thread_id=thread_id,
        )

    async def history(
        self,
        thread_id: str,
    ) -> list[dict]:
        """
        获取指定 thread_id 的历史消息。
        """

        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        snapshot = await self.agent.graph.aget_state(
            config
        )

        if not snapshot:
            return []

        values = snapshot.values or {}

        messages = values.get(
            "messages",
            [],
        )

        result = []

        for message in messages:

            message_type = getattr(
                message,
                "type",
                None,
            )

            content = getattr(
                message,
                "content",
                "",
            )

            if not content:
                continue

            if message_type == "human":
                role = "user"

            elif message_type == "ai":
                role = "assistant"

            elif message_type == "system":
                role = "system"

            else:
                # ToolMessage 等内部消息
                # 前端聊天窗口不直接显示
                continue

            result.append(
                {
                    "role": role,
                    "content": content,
                }
            )

        return result


@asynccontextmanager
async def create_pipeline() -> AsyncIterator[
    TravelAgentPipeline
]:
    """
    创建完整 Travel Agent Pipeline。

    FastAPI 启动时创建一次，
    FastAPI 关闭时统一释放 Redis。
    """

    print(
        "\n========================================"
    )
    print(
        "[Pipeline] Initializing..."
    )
    print(
        "========================================"
    )

    model = get_agnes_model()

    # ==========================================
    # Tool Registry
    # ==========================================

    tool_registry = (
        await build_tools_registry()
    )

    # ==========================================
    # Retry
    # ==========================================

    execution_policy = (
        policy.ToolExecutionPolicy()
    )

    error_classifier_instance = (
        error_classifier.ToolErrorClassifier()
    )

    retry_handler = RetryHandler(
        execution_policy,
        error_classifier_instance,
    )

    tool_executor = ToolExecutor(
        tool_registry,
        retry_handler,
    )

    # ==========================================
    # Redis Checkpointer
    # ==========================================

    async with create_redis_checkpointer() as checkpointer:

        pipeline = TravelAgentPipeline(
            model=model,
            tool_registry=tool_registry,
            tool_executor=tool_executor,
            checkpointer=checkpointer,
        )

        print(
            "[Pipeline] Ready"
        )

        yield pipeline

    print(
        "[Pipeline] Closed"
    )


# ==============================================
# 本地命令行测试
# ==============================================

async def main():

    async with create_pipeline() as pipeline:

        result = await pipeline.chat(
            message="美国的首都是哪里？",
            thread_id="cli-test-001",
        )

        print(
            "\n========== AI =========="
        )

        print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())