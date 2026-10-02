from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    thread_id: str = Field(
        default="user-001",
        min_length=1,
        max_length=100,
        title="用户线程 ID",
        description=(
            "用于区分不同用户/不同会话。"
            "相同 thread_id 会继续之前的对话上下文；"
            "更换 thread_id 会创建独立的对话。"
        ),
        examples=["user-001"],
    )

    message: str = Field(
        default="你好，我想去南京旅游两天，帮我规划一下",
        min_length=1,
        title="用户消息",
        description="请输入你想对旅行助手说的话，例如咨询景点、酒店、天气或完整旅行规划。",
        examples=[
            "你好，我想去南京旅游两天，帮我规划一下",
        ],
    )


class ChatResponse(BaseModel):
    thread_id: str = Field(
        title="用户线程 ID",
        description="本次对话所属的线程。",
    )

    message: str = Field(
        title="助手回复",
        description="旅行助手生成的回复。",
    )


class Message(BaseModel):
    role: str = Field(
        title="角色",
        description="消息角色：user、assistant 或 system。",
    )

    content: str = Field(
        title="消息内容",
    )


class HistoryResponse(BaseModel):
    thread_id: str = Field(
        title="用户线程 ID",
    )

    messages: list[Message] = Field(
        title="历史消息",
        description="该 thread_id 对应的历史对话。",
    )