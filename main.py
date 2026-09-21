import asyncio

from infrastructure.core.llm import get_agnes_model,get_nvidia_model

model = get_nvidia_model()

res = (model.invoke('你好'))
print(res)