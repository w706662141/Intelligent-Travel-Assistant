from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient


class AmapMCPClient:
    """
      高德 MCP Client

      负责：
      1. 连接 amap-mcp-server
      2. 获取 MCP Tools
      3. 调用 MCP Tool
      """

    def __init__(self,
                 api_key: str,
                 command: str = 'uvx',
                 server_command: str = 'amap-mcp-server'
                 ):
        self.api_key = api_key
        self.command = command
        self.server_command = server_command

        self._client: MultiServerMCPClient | None = None
        self._tools = None

    async def connect(self):
        """
        初始化 MCP Client
        """
        self._client = MultiServerMCPClient(
            {
                "amap": {
                    "transport": "stdio",
                    "command": self.command,
                    "args": [
                        self.server_command,
                    ],
                    "env": {
                        "AMAP_MAPS_API_KEY": self.api_key,
                        "PYTHONUTF8": "1",  # ←新增
                        "PYTHONIOENCODING": "utf-8",  # ←新增（双保险）

                    },
                }
            }
        )

        self._tools = await self._client.get_tools()

        return self._tools

    @property
    def tools(self):
        if self._tools is None:
            raise RuntimeError(
                "AmapMCPClient 尚未连接，请先调用 connect()"
            )
        return self._tools

    def get_tool(self, name: str):
        """
        根据工具名称获取 MCP Tool
        """

        for tool in self._tools:
            if tool.name == name:
                return tool

        raise ValueError(
            f"Amap MCP Tool 不存在: {name}"
        )

    async def call_tool(self,
                        name: str,
                        arguments: dict[str, Any]):
        """
        调用指定 MCP Tool
        """

        tool = self.get_tool(name)
        return await tool.ainvoke(arguments)
