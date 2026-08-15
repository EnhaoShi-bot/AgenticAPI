"""模型表数据访问层（纯 DB 操作，不含业务判断）"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import build_set_clause


async def get_all(db: AsyncSession) -> list[dict]:
    """获取全量模型列表（原始行字典）"""
    results = await db.execute(text("SELECT * FROM llm_models"))
    return [dict(r) for r in results.mappings().all()]


async def get_id_by_name(db: AsyncSession, name: str) -> int | None:
    """按模型名称查询 id，不存在返回 None"""
    result = await db.execute(
        text("SELECT id FROM llm_models WHERE name = :name LIMIT 1"),
        {"name": name},
    )
    row = result.mappings().first()
    return row["id"] if row else None


async def insert(db: AsyncSession, model: dict) -> int:
    """插入单条模型，返回自增主键 id"""
    result = await db.execute(
        text(
            """
            INSERT INTO llm_models
            (name, label, description, is_request_mode, per_request_price,
             input_price, cache_price, output_price, model_group, is_pin,
             is_log, status, channels, context_length, max_tokens, support_vision,
             icon)
            VALUES (:name, :label, :description, :is_request_mode, :per_request_price,
                    :input_price, :cache_price, :output_price, :model_group, :is_pin,
                    :is_log, :status, :channels, :context_length, :max_tokens, :support_vision,
                    :icon)
            """
        ),
        model,
    )
    await db.flush()
    return result.lastrowid


async def update_by_name(db: AsyncSession, name: str, update_dict: dict) -> None:
    """按模型名称动态更新字段"""
    sql = text(
        f"UPDATE llm_models SET {build_set_clause(update_dict)} WHERE name = :model_name"
    )
    await db.execute(sql, {**update_dict, "model_name": name})


async def delete_by_name(db: AsyncSession, name: str) -> int:
    """按模型名称删除，返回受影响行数"""
    result = await db.execute(
        text("DELETE FROM llm_models WHERE name = :name"),
        {"name": name},
    )
    return result.rowcount
