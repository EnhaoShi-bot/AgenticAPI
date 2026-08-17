"""用量统计表（预聚合）：每 用户×模型×小时 一行的桶

设计目的：监控面板的折线图 / 范围统计只查这张小表做 GROUP BY，
避免对 logs 原始日志做全量扫描求和。中转每次调用成功后用
INSERT ... ON DUPLICATE KEY UPDATE 单语句原子累加（见 crud/usage_stats.py）。
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class UsageStatsTable(BaseModel):
    """用量小时桶表 ORM 模型"""

    __tablename__ = "usage_stats"

    __table_args__ = (
        # 唯一键支撑 upsert：同一小时同一用户同一模型只累加不新增行
        UniqueConstraint("stat_hour", "user_id", "model_name", name="uk_stats_hour_user_model"),
        Index("idx_stats_user_hour", "user_id", "stat_hour"),
        {"comment": "用量统计小时桶表"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    # 统计小时（取调用时刻的整点，MySQL DATETIME，本地时区与 logs.create_time 一致）
    stat_hour: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="统计小时（整点）")
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="用户ID")
    model_name: Mapped[str] = mapped_column(String(128), nullable=False, comment="模型名")
    calls: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, comment="调用次数")
    prompt_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, comment="输入token累计")
    completion_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, comment="输出token累计")
    cache_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, comment="缓存token累计")

    def __repr__(self):
        return f"<UsageStats(stat_hour={self.stat_hour}, user_id={self.user_id}, model_name='{self.model_name}')>"
