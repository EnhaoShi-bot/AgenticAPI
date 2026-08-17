"""全站用量汇总表：固定单行（id=1）的累计计数器

监控面板"全站累计输入/输出/缓存 token"直接读这一行，O(1) 无需任何聚合计算。
"""

from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class UsageSummaryTable(BaseModel):
    """全站用量汇总表 ORM 模型（id 固定为 1 的单行计数器）"""

    __tablename__ = "usage_summary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="固定为1")
    calls: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, comment="全站累计调用次数")
    prompt_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, comment="全站累计输入token")
    completion_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, comment="全站累计输出token")
    cache_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, comment="全站累计缓存token")

    def __repr__(self):
        return f"<UsageSummary(id={self.id}, calls={self.calls})>"
