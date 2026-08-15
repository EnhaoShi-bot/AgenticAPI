"""AI大模型配置表"""

from decimal import Decimal

from sqlalchemy import (
    DECIMAL,
    BigInteger,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ModelsTable(BaseModel):
    """AI大模型配置表"""

    __tablename__ = "llm_models"
    __table_args__ = (
        UniqueConstraint("name", name="uk_model_name"),
        {"comment": "AI大模型配置表"},
    )

    # 字段定义
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="主键ID"
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="模型唯一标识名称")
    label: Mapped[str] = mapped_column(String(128), nullable=False, comment="前端展示名称")
    description: Mapped[str | None] = mapped_column(Text, comment="模型描述")
    is_request_mode: Mapped[bool] = mapped_column(
        Integer, nullable=False, default=0, comment="是否按次计费模式 0否 1是"
    )
    per_request_price: Mapped[Decimal] = mapped_column(
        DECIMAL(12, 4), nullable=False, default=0, comment="单次请求价格（按次计费生效）"
    )
    input_price: Mapped[Decimal] = mapped_column(
        DECIMAL(12, 4), nullable=False, default=0, comment="输入token单价"
    )
    cache_price: Mapped[Decimal] = mapped_column(
        DECIMAL(12, 4), nullable=False, default=0, comment="缓存token单价"
    )
    output_price: Mapped[Decimal] = mapped_column(
        DECIMAL(12, 4), nullable=False, default=0, comment="输出token单价"
    )
    model_group: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="模型分组：free免费 / vip付费"
    )
    is_pin: Mapped[bool] = mapped_column(
        Integer, nullable=False, default=0, comment="是否置顶 0否 1是"
    )
    is_log: Mapped[bool] = mapped_column(
        Integer, nullable=False, default=0, comment="是否开启日志记录 0否 1是"
    )
    status: Mapped[bool] = mapped_column(
        Integer, nullable=False, default=1, comment="状态：0禁用 1启用"
    )
    channels: Mapped[str | None] = mapped_column(
        Text, default=None, comment="上游渠道有序列表，JSON数组，按顺序轮询调用"
    )
    context_length: Mapped[int | None] = mapped_column(
        Integer, default=None, comment="模型最大上下文总token长度"
    )
    max_tokens: Mapped[int | None] = mapped_column(
        Integer, default=None, comment="最大输出token数量限制"
    )
    support_vision: Mapped[bool] = mapped_column(
        Integer, nullable=False, default=0, comment="是否支持视觉识图：0不支持 1支持"
    )
    icon: Mapped[str] = mapped_column(
        String(255), nullable=False, default="", comment="模型图标"
    )
