from decimal import Decimal
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, DECIMAL, UniqueConstraint, BigInteger


class BaseModel(DeclarativeBase):
    """数据类型的基类"""
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="更新时间")


class ModelsTable(BaseModel):
    """AI大模型配置表"""
    __tablename__ = "llm_models"
    __table_args__ = (
        UniqueConstraint("name", name="uk_model_name"),  # 【修正】补上和数据库一致的唯一约束
        {"comment": "AI大模型配置表"},
    )

    # 字段定义
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")  # 【修正】数据库为 bigint，和实际对齐
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="模型唯一标识名称")
    label: Mapped[str] = mapped_column(String(128), nullable=False, comment="前端展示名称")
    description: Mapped[str | None] = mapped_column(Text, comment="模型描述")
    is_request_mode: Mapped[bool] = mapped_column(Integer, nullable=False, default=0, comment="是否按次计费模式 0否 1是")  # 【修正】SQLAlchemy 用 Integer 映射 tinyint(1)，但类型标注用 bool 更语义化
    per_request_price: Mapped[Decimal] = mapped_column(DECIMAL(12, 4), nullable=False, default=0, comment="单次请求价格（按次计费生效）")
    input_price: Mapped[Decimal] = mapped_column(DECIMAL(12, 4), nullable=False, default=0, comment="输入token单价")
    cache_price: Mapped[Decimal] = mapped_column(DECIMAL(12, 4), nullable=False, default=0, comment="缓存token单价")
    output_price: Mapped[Decimal] = mapped_column(DECIMAL(12, 4), nullable=False, default=0, comment="输出token单价")
    model_group: Mapped[str] = mapped_column(String(64), nullable=False, comment="模型分组：free免费 / vip付费")
    is_pin: Mapped[bool] = mapped_column(Integer, nullable=False, default=0, comment="是否置顶 0否 1是")  # 【修正】同上，类型标注改为 bool
    is_log: Mapped[bool] = mapped_column(Integer, nullable=False, default=0, comment="是否开启日志记录 0否 1是")  # 【修正】同上
    status: Mapped[bool] = mapped_column(Integer, nullable=False, default=1, comment="状态：0禁用 1启用")  # 【修正】同上
    channels: Mapped[str | None] = mapped_column(Text, default=None, comment="上游渠道有序列表，JSON数组，按顺序轮询调用")
    context_length: Mapped[int | None] = mapped_column(Integer, default=None, comment="模型最大上下文总token长度")
    max_tokens: Mapped[int | None] = mapped_column(Integer, default=None, comment="最大输出token数量限制")
    support_vision: Mapped[bool] = mapped_column(Integer, nullable=False, default=0, comment="是否支持视觉识图：0不支持 1支持")  # 【修正】同上

class ChannelsTable(BaseModel):
    """上游AI渠道配置表"""
    __tablename__ = "llm_channels"
    __table_args__ = (
        UniqueConstraint("channel_key", name="uk_channel_key"),
        {"comment": "上游AI渠道配置表"},
    )

    # 字段定义
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    channel_key: Mapped[str] = mapped_column(String(128), nullable=False, comment="渠道唯一标识(程序内部使用，不可重复)")
    channel_name: Mapped[str] = mapped_column(String(128), nullable=False, comment="渠道展示名称(后台管理员查看)")
    base_url: Mapped[str] = mapped_column(String(255), nullable=False, comment="上游接口基础地址")
    api_key: Mapped[str] = mapped_column(String(512), nullable=False, comment="上游接口密钥")
    support_models: Mapped[str | None] = mapped_column(Text, default=None, comment='支持的模型列表，JSON数组["model-name"]')
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=1, comment="渠道状态：0禁用 1启用")
    timeout: Mapped[int] = mapped_column(Integer, nullable=False, default=30, comment="请求超时时间，单位：秒")
    description: Mapped[str | None] = mapped_column(Text, default=None, comment="渠道备注说明")