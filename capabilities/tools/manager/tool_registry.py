from langchain_core.tools import BaseTool


class ToolRegistry:

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self,
                 tools: list[BaseTool]):

        for tool in tools:
            if tool.name in self._tools:
                raise ValueError(
                    f"Tool already registered: {tool.name}"
                )
            self._tools[tool.name] = tool

    def get(self,
            name: str,
            ) -> BaseTool:
        if name not in self._tools:
            raise KeyError(f"Tool with name '{name}' not found.")
        return self._tools[name]

    def get_all(self):
        return list(self._tools.values())
