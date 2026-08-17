"""管理员用户管理相关 Schema"""

from decimal import Decimal

from pydantic import BaseModel, Field

# 允许的用户分组（与 llm_models.model_group 的分组体系对应）
ALLOWED_GROUPS = ("free", "vip")


class AdminUserUpdateSchema(BaseModel):
    """管理员修改用户信息（部分更新语义，至少传一个字段）"""
    nickname: str | None = Field(default=None, max_length=50, alias="nickname")
    balance: Decimal | None = Field(default=None, ge=0, alias="balance")
    user_group: str | None = Field(default=None, alias="userGroup")
    is_admin: bool | None = Field(default=None, alias="isAdmin")
    status: bool | None = Field(default=None, alias="status")

    model_config = {"populate_by_name": True}


class AdminUserBatchDeleteSchema(BaseModel):
    """批量删除用户请求"""
    ids: list[int] = Field(min_length=1, alias="ids")

    model_config = {"populate_by_name": True}
