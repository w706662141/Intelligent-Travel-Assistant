from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)

from capabilities.subagents.trip_subagent.graph import (
    TripSubAgentGraph,
)
from capabilities.subagents.trip_subagent.prompts.prompt import (
    TRIP_SUBAGENT_SYSTEM_PROMPT,
)
from infrastructure.core.llm import get_agnes_model


class TripSubAgent:

    def __init__(
            self,
            tools,
            max_iterations: int = 15,
    ):
        self.tools = tools

        base_model = get_agnes_model()

        self.model = base_model.bind_tools(
            tools
        )

        self.max_iterations = max_iterations

        self.graph = TripSubAgentGraph(
            model=self.model,
            tools=self.tools,
            max_iterations=max_iterations,
        ).build()

    async def run(
            self,
            task: str,
    ) -> dict:

        result = await self.graph.ainvoke(
            {
                "messages": [
                    SystemMessage(
                        content=(
                            TRIP_SUBAGENT_SYSTEM_PROMPT
                        )
                    ),
                    HumanMessage(
                        content=task
                    ),
                ],

                "task": task,

                "iteration": 0,

                "max_iterations": (
                    self.max_iterations
                ),

                "status": "running",

                "error": None,

                "tool_call_count": 0,

                "tool_result_count": 0,
            }
        )

        if result.get("status") == "failed":

            return {
                "success": False,
                "message": (
                    "旅行规划过程中出现问题，"
                    "暂时无法完成该任务。"
                ),
                "error": result.get("error"),
            }

        if result.get("status") == "max_iterations":

            return {
                "success": False,
                "message": (
                    "旅行规划步骤过多，"
                    "暂时无法完成该任务。"
                ),
                "error": (
                    "TripSubAgent max iterations reached"
                ),
            }

        messages = result.get(
            "messages",
            []
        )

        if not messages:
            return {
                "success": False,
                "message": (
                    "旅行规划未生成有效结果。"
                ),
                "error": "EMPTY_RESULT",
            }

        final_message = messages[-1]

        return {
            "success": True,
            "message": final_message.content,
            "tool_call_count": result.get(
                "tool_call_count",
                0,
            ),
            "tool_result_count": result.get(
                "tool_result_count",
                0,
            ),
        }