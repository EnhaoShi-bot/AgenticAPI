"""系统日志表：API调用 / 登录 / 管理员操作 / 用户操作"""

from decimal import Decimal

from sqlalchemy import BigInteger, DECIMAL, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class LogsTable(BaseModel):
    """系统日志表 ORM 模型（统一一张宽表，api 调用专用字段其他类型留空）"""

    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="日志ID")
    # 日志类型：api（中转调用）/ login（登录注册登出访客）/ admin（管理员操作）/ user（密钥管理等用户操作）
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True, comment="日志类型")
    # 用户ID不设外键：用户被删除后日志仍要保留审计痕迹，username 存快照
    user_id: Mapped[int | None] = mapped_column(Integer, comment="用户ID（快照，无外键）")
    username: Mapped[str | None] = mapped_column(String(50), comment="用户名快照")
    action: Mapped[str] = mapped_column(String(50), nullable=False, comment="动作：chat/login/create_model/update_user 等")
    detail: Mapped[str | None] = mapped_column(String(500), comment="粗略描述")

    # ── api 调用专用字段（其他类型日志留空） ──
    model_name: Mapped[str | None] = mapped_column(String(128), comment="调用的模型名")
    channel_name: Mapped[str | None] = mapped_column(String(128), comment="实际使用的上游渠道")
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="输入token数")
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="输出token数")
    cache_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="缓存命中token数")
    cost: Mapped[Decimal] = mapped_column(DECIMAL(12, 6), nullable=False, default=0, comment="本次消费金额")
    duration_ms: Mapped[int | None] = mapped_column(Integer, comment="请求耗时（毫秒）")

    def __repr__(self):
        return f"<Log(id={self.id}, type='{self.type}', action='{self.action}')>"
