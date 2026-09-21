import asyncio

from infrastructure.core.llm import get_agnes_model

model = get_agnes_model()

res = (model.invoke('你好'))
print(res)