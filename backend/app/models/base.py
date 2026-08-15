"""SQLAlchemy ORM 基类"""

from datetime import datetime

from sqlalchemy import DateTime, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    """
    数据类型的基类

    【重要】所有继承此基类的表定义都会被 SQLAlchemy 自动注册到 BaseModel.metadata 中
    当调用 BaseModel.metadata.create_all() 时，会自动创建所有已注册的表
    """

    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        comment="更新时间",
    )
