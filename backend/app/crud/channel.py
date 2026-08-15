"""渠道表数据访问层（纯 DB 操作，不含业务判断）"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import build_set_clause


async def get_all(db: AsyncSession) -> list[dict]:
    """获取全量渠道列表（原始行字典）"""
    results = await db.execute(text("SELECT * FROM llm_channels"))
    return [dict(r) for r in results.mappings().all()]


async def get_id_by_name(db: AsyncSession, channel_name: str) -> int | None:
    """按渠道名称查询 id，不存在返回 None"""
    result = await db.execute(
        text("SELECT id FROM llm_channels WHERE channel_name = :channel_name LIMIT 1"),
        {"channel_name": channel_name},
    )
    row = result.mappings().first()
    return row["id"] if row else None


async def get_existing_names(db: AsyncSession, names: list[str]) -> set[str]:
    """返回 names 中实际存在于 llm_channels 表的渠道名集合"""
    if not names:
        return set()
    placeholders = ",".join([f":c{i}" for i in range(len(names))])
    results = await db.execute(
        text(f"SELECT channel_name FROM llm_channels WHERE channel_name IN ({placeholders})"),
        {f"c{i}": n for i, n in enumerate(names)},
    )
    return {r["channel_name"] for r in results.mappings().all()}


async def insert(db: AsyncSession, channel: dict) -> int:
    """插入单条渠道，返回自增主键 id"""
    result = await db.execute(
        text(
            """
            INSERT INTO llm_channels
            (channel_name, base_url, api_key, support_models,
             status, timeout, used_ratio, description)
            VALUES (:channel_name, :base_url, :api_key, :support_models,
                    :status, :timeout, :used_ratio, :description)
            """
        ),
        channel,
    )
    await db.flush()
    return result.lastrowid


async def update_by_name(db: AsyncSession, channel_name: str, update_dict: dict) -> None:
    """按渠道名称动态更新字段"""
    sql = text(
        f"UPDATE llm_channels SET {build_set_clause(update_dict)} WHERE channel_name = :channel_name"
    )
    await db.execute(sql, {**update_dict, "channel_name": channel_name})


async def delete_by_name(db: AsyncSession, channel_name: str) -> int:
    """按渠道名称删除，返回受影响行数"""
    result = await db.execute(
        text("DELETE FROM llm_channels WHERE channel_name = :name"),
        {"name": channel_name},
    )
    return result.rowcount
