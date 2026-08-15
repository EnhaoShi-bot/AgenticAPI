"""渠道相关请求/响应 Schema"""

from pydantic import BaseModel, Field


class ChannelSchema(BaseModel):
    """渠道数据字段定义，公开，可不做鉴权校验"""

    model_config = {"populate_by_name": True}

    channel_name: str = Field(alias="channelName")
    base_url: str = Field(default="", alias="baseUrl")
    api_key: str = Field(default="", alias="apiKey")
    support_models: list[str] = Field(default_factory=list, alias="supportModels")
    status: bool = Field(default=True, alias="status")
    timeout: int = Field(default=30, alias="timeout")
    used_ratio: float = Field(default=0.0, alias="usedRatio")
    description: str | None = Field(default=None, alias="description")
