"""对话记录表：保存大模型调用的输入 / 推理 / 输出全文

仅当模型开启 is_log 且 输入+输出 token 不超过管理员阈值（system_config 的
chat_record_max_tokens，默认 5000）时才写入，避免落库超长文本。
token 数量本身不在此表做全量记录——那部分无条件记在 logs / usage_stats 里。
"""

from decimal import Decimal

from sqlalchemy import DECIMAL, BigInteger, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ChatRecordTable(BaseModel):
    """对话记录表 ORM 模型"""

    __tablename__ = "chat_record"

    # 冗余 username 快照：管理员在监控面板按用户名筛选 / 展示，避免联表
    __table_args__ = (
        Index("idx_chat_record_user_id", "user_id"),
        Index("idx_chat_record_model_name", "model_name"),
        {"comment": "大模型对话记录表"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="用户ID（快照，无外键）")
    username: Mapped[str] = mapped_column(String(50), nullable=False, comment="用户名快照")
    model_name: Mapped[str] = mapped_column(String(128), nullable=False, comment="调用的模型名")
    channel_name: Mapped[str | None] = mapped_column(String(128), comment="实际使用的上游渠道")
    # 输入内容：调用方 messages 数组的 JSON 字符串（[{"role": ..., "content": ...}, ...]）
    input_content: Mapped[str | None] = mapped_column(Text, comment="输入内容（messages 数组 JSON）")
    # 推理内容：OpenAI 兼容接口的 reasoning_content（思维链），无则留空
    reasoning_content: Mapped[str | None] = mapped_column(Text, comment="模型思考的推理内容")
    output_content: Mapped[str | None] = mapped_column(Text, comment="模型输出内容")

    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="输入token数")
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="输出token数")
    cache_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="缓存命中token数")
    cost: Mapped[Decimal] = mapped_column(DECIMAL(12, 6), nullable=False, default=0, comment="本次消费金额")
    duration_ms: Mapped[int | None] = mapped_column(Integer, comment="请求耗时（毫秒）")

    def __repr__(self):
        return f"<ChatRecord(id={self.id}, user_id={self.user_id}, model_name='{self.model_name}')>"
