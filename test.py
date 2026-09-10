import asyncio

from langchain_core.messages import ToolMessage, HumanMessage

from config.settings import settings
from infrastructure.mcp.clients.amap_client import AmapMCPClient


async def main():
    client = AmapMCPClient(
        api_key=settings.AMAP_MAPS_API_KEY
    )

    tools = await client.connect()

    print("========== Amap MCP Tools ==========")

    for tool in tools:
        print(
            f"name: {tool.name}"
        )
        print(
            f"description: {tool.description}"
        )
        print(
            f"schema: {tool.args_schema}"
        )
        print("-" * 80)


from dotenv import load_dotenv

load_dotenv()



if __name__ == "__main__":
    asyncio.run(main())

