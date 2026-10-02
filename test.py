import asyncio

from config.settings import settings
from infrastructure.core.llm import get_agnes_model
from infrastructure.mcp.clients.amap_client import AmapMCPClient

# async def main():
# client = AmapMCPClient(
#     api_key=settings.AMAP_MAPS_API_KEY
# )
#
# tools = await client.connect()
#
# print("========== Amap MCP Tools ==========")
#
# for tool in tools:
#     print(
#         f"name: {tool.name}"
#     )
#     print(
#         f"description: {tool.description}"
#     )
#     print(
#         f"schema: {tool.args_schema}"
#     )
#     print("-" * 80)

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from infrastructure.memory.redis_checkpointer import create_redis_checkpointer


async def main():

    model = get_agnes_model()

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    async def chat_node(state: State):
        response = await model.ainvoke(state["messages"])

        return {
            "messages": [response]
        }

    builder = StateGraph(State)

    builder.add_node("chat", chat_node)

    builder.add_edge(START, "chat")
    builder.add_edge("chat", END)

    async with create_redis_checkpointer() as checkpointer:
        graph = builder.compile(
            checkpointer=checkpointer
        )

        config = {
            "configurable": {
                "thread_id": "redis-memory-test-002"
            }
        }

        # 第一轮
        result = await graph.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "你好，我叫zz，我喜欢吃苹果。"
                    }
                ]
            },
            config=config,
        )

        print("第一轮：")
        print(result["messages"][-1].content)

        # 第二轮
        result = await graph.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "我叫什么？我喜欢吃什么？"
                    }
                ]
            },
            config=config,
        )

        print("第二轮：")
        print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())

