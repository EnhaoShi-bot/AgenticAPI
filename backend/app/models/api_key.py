"""用户 API 密钥表：对外中转接口的访问凭证（一个用户最多 5 个）"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ApiKeyTable(BaseModel):
    """用户 API 密钥表 ORM 模型"""

    __tablename__ = "api_key"
    __table_args__ = (
        Index("uk_api_key", "key"),
        Index("idx_api_key_user", "user_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="密钥ID")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, comment="所属用户ID")
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="密钥备注名")
    # 对外发放的密钥，sk- 开头；中转接口用它识别用户（区别于登录令牌 user_token）
    key: Mapped[str] = mapped_column(String(64), nullable=False, comment="API密钥值")
    status: Mapped[bool] = mapped_column(Integer, nullable=False, default=1, comment="状态：0禁用 1启用")
    last_used_time: Mapped[datetime | None] = mapped_column(DateTime, comment="最后使用时间")

    def __repr__(self):
        return f"<ApiKey(id={self.id}, name='{self.name}', user_id={self.user_id})>"
