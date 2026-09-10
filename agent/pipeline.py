import asyncio

from dotenv import load_dotenv
from capabilities.tools.manager.build_tools import build_tools_registry
from infrastructure.core.llm import get_agnes_model
from agent.react_agent import ReActAgent
from capabilities.tools.manager.tool_executor import ToolExecutor
from capabilities.tools.manager.executor.retry import RetryHandler
from capabilities.tools.manager.executor import policy, error_classifier

load_dotenv()

model = get_agnes_model()
policy = policy.ToolExecutionPolicy()
error_classifier = error_classifier.ToolErrorClassifier()
tool_registry = asyncio.run(build_tools_registry())

retry_handler = RetryHandler(policy, error_classifier)

tool_executor = ToolExecutor(tool_registry, retry_handler)
agent = ReActAgent(model, tool_registry, tool_executor)

print(asyncio.run(agent.run('打算去洛阳游玩3天2026年8月1日到3日，我喜欢历史给我推荐路线')))
