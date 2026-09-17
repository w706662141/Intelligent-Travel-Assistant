from typing import Literal

from pydantic import BaseModel, Field


class ResourceRequest(BaseModel):
    resource_type: Literal[
        "attraction",
        "hotels",
        "weather",
    ]

    reason : str = Field(
        default='',
        description="为什么需要该资源"
    )

    priority: int = Field(
        default=3,
        ge=1,
        le=5,
    )


class ResourceDecision(BaseModel):
    requests: list[ResourceRequest] = Field(
        default_factory=list,
        description="规划前需要获取的资源",
    )
