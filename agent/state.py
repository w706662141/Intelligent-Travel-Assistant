from dataclasses import dataclass, field
from typing import Optional

from langchain_core.messages import BaseMessage


@dataclass
class AgentState:
    """
    Agent 运行状态。

    AgentLoop 不应该通过大量局部变量维护状态，
    所有运行过程中的核心信息统一放在这里。
    """

    messages: list[BaseMessage] = field(
        default_factory=list
    )

    iteration: int = 0

    max_iterations: int = 10

    finished: bool = False

    final_answer: Optional[str] = None

    status: str = 'running'

    error: Optional[str] = None

    tool_call_count: int = 0

    tool_result_count: int = 0

    def increment_iteration(self):
        self.iteration += 1

    def finish(self, answer: str):
        self.finished = True
        self.final_answer = answer
        self.status = 'completed'

    def fail(self, error: str):
        self.finished = True
        self.error = error
        self.status = 'failed'

    def max_iterations_reached(self):
        self.finished = True
        self.status = "max_iterations"
