from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Form

from agent.pipeline import create_pipeline
from api.schemas.chat_model import (
    ChatResponse,
    HistoryResponse,
)


pipeline = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline

    print("[FastAPI] Starting...")

    async with create_pipeline() as agent_pipeline:
        pipeline = agent_pipeline

        print("[FastAPI] Ready")

        yield

    pipeline = None

    print("[FastAPI] Shutdown")


app = FastAPI(
    title="Intelligent Travel Assistant",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "pipeline": pipeline is not None,
    }

@app.post(
    "/api/chat",
    response_model=ChatResponse,
    summary="发送消息",
    description="输入消息，与旅行助手进行多轮对话。",
)
async def chat(
    thread_id: str = Form(
        default="user-001",
        description="会话 ID。相同 ID 会继续之前的对话。",
    ),
    message: str = Form(
        default="你好，我想去南京旅游两天，帮我规划一下",
        description="输入你想咨询的内容。",
    ),
):
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Agent Pipeline 尚未启动",
        )

    try:
        result = await pipeline.chat(
            message=message,
            thread_id=thread_id,
        )

        return ChatResponse(
            thread_id=thread_id,
            message=result,
        )

    except Exception as e:
        print("[FastAPI] Chat error:", repr(e))
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@app.get(
    "/api/history/{thread_id}",
    response_model=HistoryResponse,
)
async def history(
    thread_id: str,
):
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Agent Pipeline 尚未启动",
        )

    try:
        messages = await pipeline.history(
            thread_id
        )

        return HistoryResponse(
            thread_id=thread_id,
            messages=messages,
        )

    except Exception as e:
        print(
            "[FastAPI] History error:",
            repr(e),
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )