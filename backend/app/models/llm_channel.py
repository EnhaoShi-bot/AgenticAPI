"""上游AI渠道配置表"""

from sqlalchemy import (
    BigInteger,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ChannelsTable(BaseModel):
    """上游AI渠道配置表"""

    __tablename__ = "llm_channels"
    __table_args__ = (
        UniqueConstraint("channel_name", name="uk_channel_name"),
        {"comment": "上游AI渠道配置表"},
    )

    # 字段定义
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="主键ID"
    )
    channel_name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="渠道展示名称(后台管理员查看)"
    )
    base_url: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="上游接口基础地址"
    )
    api_key: Mapped[str] = mapped_column(
        String(512), nullable=False, comment="上游接口密钥"
    )
    support_models: Mapped[str | None] = mapped_column(
        Text, default=None, comment='支持的模型列表，JSON数组["model-name"]'
    )
    status: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, comment="渠道状态：0禁用 1启用"
    )
    timeout: Mapped[int] = mapped_column(
        Integer, nullable=False, default=30, comment="请求超时时间，单位：秒"
    )
    used_ratio: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="使用率(百分数)"
    )
    description: Mapped[str | None] = mapped_column(
        Text, default=None, comment="渠道备注说明"
    )
