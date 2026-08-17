"""API 密钥相关 Schema"""

from datetime import datetime

from pydantic import BaseModel, Field


class ApiKeyCreateSchema(BaseModel):
    """创建密钥请求"""
    name: str = Field(min_length=1, max_length=50, description="密钥备注名")


class ApiKeyUpdateSchema(BaseModel):
    """更新密钥请求（部分更新语义）"""
    name: str | None = Field(default=None, min_length=1, max_length=50, alias="name")
    status: bool | None = Field(default=None, alias="status")

    model_config = {"populate_by_name": True}


class ApiKeySchema(BaseModel):
    """密钥信息响应"""
    id: int
    name: str
    key: str
    status: bool = Field(default=True)
    create_time: datetime | None = Field(default=None, alias="createTime")
    last_used_time: datetime | None = Field(default=None, alias="lastUsedTime")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }
