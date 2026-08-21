"""模型相关请求/响应 Schema"""

from decimal import Decimal

from pydantic import BaseModel, Field


class ModelSchema(BaseModel):
    """模型数据字段定义，其中 id 字段不能更新，由数据库自动生成，其他字段都可选传"""

    model_config = {"populate_by_name": True}

    # 基础信息
    name: str | None = Field(default=None, alias="name")
    upstream_name: str | None = Field(default=None, alias="upstreamName")
    label: str | None = Field(default=None, alias="label")
    description: str | None = Field(default=None, alias="description")
    model_group: str | None = Field(default=None, alias="modelGroup")

    # 定价信息
    is_request_mode: bool | None = Field(default=None, alias="isRequestMode")
    per_request_price: Decimal | None = Field(default=None, alias="perRequestPrice")
    input_price: Decimal | None = Field(default=None, alias="inputPrice")
    cache_price: Decimal | None = Field(default=None, alias="cachePrice")
    output_price: Decimal | None = Field(default=None, alias="outputPrice")

    # 模型配置
    is_pin: bool | None = Field(default=None, alias="isPin")
    is_log: bool | None = Field(default=None, alias="isLog")
    status: bool | None = Field(default=None, alias="status")
    channels: list[str] | None = Field(default=None, alias="channels")
    context_length: int | None = Field(default=None, alias="contextLength")
    max_tokens: int | None = Field(default=None, alias="maxTokens")
    support_vision: bool | None = Field(default=None, alias="supportVision")
    icon: str = Field(default="", alias="icon")
