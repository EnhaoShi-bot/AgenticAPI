"""系统配置表：管理员可在控制台调整的运行时参数（键值对）

首个键 chat_record_max_tokens：对话记录长度阈值，
输入+输出 token 超过该值的调用不落库 chat_record（默认 5000）。
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class SystemConfigTable(BaseModel):
    """系统配置表 ORM 模型"""

    __tablename__ = "system_config"

    config_key: Mapped[str] = mapped_column(String(64), primary_key=True, comment="配置键")
    config_value: Mapped[str] = mapped_column(String(255), nullable=False, comment="配置值（字符串存储，按需转换类型）")

    def __repr__(self):
        return f"<SystemConfig(config_key='{self.config_key}', config_value='{self.config_value}')>"
