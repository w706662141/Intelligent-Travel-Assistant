import asyncio
import traceback

from capabilities.subagents.trip_subagent.nodes.trip_agent_node import (
    TripAgentNodes,
)
from capabilities.subagents.trip_subagent.prompts.prompt import (
    TRIP_FINALIZER_SYSTEM_PROMPT,
)
from capabilities.subagents.trip_subagent.state import (
    TripSubAgentState,
)


class TripFinalizerNode:

    def __init__(
        self,
        model,
        llm_timeout: int = 60,
    ):
        self.model = model
        self.llm_timeout = llm_timeout

    @staticmethod
    def _build_final_messages(
        state: TripSubAgentState,
    ):
        request = state["request"]

        request_context = (
            f"城市：{request.city}\n"
            f"日期：{request.start_date} ~ {request.end_date}\n"
            f"人数：{request.travelers}\n"
            f"预算："
            f"{request.budget if request.budget is not None else '未指定'}\n"
            f"偏好："
            f"{', '.join(request.preferences) if request.preferences else '未指定'}"
        )

        resource_context = (
            TripAgentNodes._build_resource_context(
                resource_data=state.get(
                    "resource_data",
                    [],
                ),
                request=request,
            )
        )

        content = (
            "【旅行需求】\n"
            f"{request_context}\n\n"
            "【真实旅行资源】\n"
            f"{resource_context}\n\n"
            "请直接生成最终旅行规划。"
        )

        return [
            {
                "role": "system",
                "content": TRIP_FINALIZER_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": content,
            },
        ]

    async def finalize(
        self,
        state: TripSubAgentState,
    ):
        try:
            messages = self._build_final_messages(state)

            print(
                "\n[TripFinalizer] "
                "Calling final LLM without tools..."
            )

            response = await asyncio.wait_for(
                self.model.ainvoke(messages),
                timeout=self.llm_timeout,
            )

            content = getattr(
                response,
                "content",
                "",
            )

            if isinstance(content, list):
                content = "\n".join(
                    str(item)
                    for item in content
                )

            content = str(content).strip()

            if not content:
                return {
                    "status": "failed",
                    "error": (
                        "Final LLM returned empty content"
                    ),
                    "final_response": None,
                }

            return {
                "status": "completed",
                "error": None,
                "final_response": content,
            }

        except asyncio.TimeoutError:
            return {
                "status": "failed",
                "error": (
                    "TripSubAgent Final LLM timeout: "
                    f"no response within "
                    f"{self.llm_timeout} seconds"
                ),
                "final_response": None,
            }

        except Exception as exc:
            traceback.print_exc()

            return {
                "status": "failed",
                "error": (
                    "TripSubAgent Final LLM execution failed: "
                    f"{exc}"
                ),
                "final_response": None,
            }
