from contextlib import asynccontextmanager
from typing import AsyncIterator

from langgraph.checkpoint.redis import AsyncRedisSaver

from config.settings import settings


@asynccontextmanager
async def create_redis_checkpointer(
        redis_url: str | None = None,

) -> AsyncIterator[AsyncRedisSaver]:
    """
    创建 LangGraph Redis Checkpointer。

    Redis 在这里仅作为 LangGraph Checkpoint 的持久化存储，
    不负责业务层面的 Memory 管理。

    生命周期：

        create
          ↓
        asetup
          ↓
        yield checkpointer
          ↓
        close
    """
    redis_url = (
            redis_url
            or settings.REDIS_URL
    )

    print(
        "\n========== Redis Checkpointer =========="
    )

    async with AsyncRedisSaver.from_conn_string(
            redis_url,
        ttl={
                "default_ttl": 240,
                "refresh_on_read": True,
        }
    ) as checkpointer:

        # ==========================================
        # 第一次使用必须初始化 Redis Index
        # ==========================================

        await checkpointer.asetup()

        print(
            "[RedisCheckpointer] "
            "Redis Checkpointer ready"
        )

        try:
            yield checkpointer

        finally:

            print(
                "[RedisCheckpointer] "
                "Connection closed"
            )
