"""系统配置表数据访问层（键值对，管理员可在线调整）"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# 对话记录长度阈值的配置键：输入+输出 token 超过该值的调用不落库对话内容
CHAT_RECORD_MAX_TOKENS_KEY = "chat_record_max_tokens"
CHAT_RECORD_MAX_TOKENS_DEFAULT = 5000


async def get_value(db: AsyncSession, key: str, default: str | None = None) -> str | None:
    """按配置键读取配置值，不存在返回 default"""
    result = await db.execute(
        text("SELECT config_value FROM system_config WHERE config_key = :key LIMIT 1"),
        {"key": key},
    )
    row = result.mappings().first()
    return row["config_value"] if row else default


async def set_value(db: AsyncSession, key: str, value: str) -> None:
    """写入配置值（不存在则插入，存在则覆盖）"""
    await db.execute(
        text(
            """
            INSERT INTO system_config (config_key, config_value)
            VALUES (:key, :value)
            ON DUPLICATE KEY UPDATE config_value = VALUES(config_value)
            """
        ),
        {"key": key, "value": value},
    )
    await db.commit()


async def get_chat_record_threshold(db: AsyncSession) -> int:
    """读取对话记录长度阈值（输入+输出 token 上限），未配置或值非法时返回默认 5000"""
    value = await get_value(db, CHAT_RECORD_MAX_TOKENS_KEY)
    try:
        return max(int(value), 0)
    except (TypeError, ValueError):
        return CHAT_RECORD_MAX_TOKENS_DEFAULT
