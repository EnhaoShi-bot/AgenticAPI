"""日志表数据访问层：统一写入口，各处按需传入字段"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.log import LogsTable


async def write_log(
        db: AsyncSession,
        *,
        type: str,
        action: str,
        user_id: int | None = None,
        username: str | None = None,
        detail: str | None = None,
        model_name: str | None = None,
        channel_name: str | None = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cache_tokens: int = 0,
        cost: Decimal | float = 0,
        duration_ms: int | None = None,
        auto_commit: bool = True,
) -> None:
    """
    写一条日志。

    :param type: api / login / admin / user
    :param action: 具体动作，如 chat、login、create_model、update_user
    :param auto_commit: 调用方后续还要继续用同一事务提交业务数据时传 False
    """
    db.add(LogsTable(
        type=type,
        action=action,
        user_id=user_id,
        username=username,
        detail=detail,
        model_name=model_name,
        channel_name=channel_name,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        cache_tokens=cache_tokens,
        cost=cost,
        duration_ms=duration_ms,
    ))
    if auto_commit:
        await db.commit()


async def query_logs(
        db: AsyncSession,
        *,
        user_id: int | None = None,
        log_type: str = "",
        keyword: str = "",
        model_name: str = "",
        start: datetime | None = None,
        end: datetime | None = None,
        page: int = 1,
        page_size: int = 10,
) -> tuple[list[dict], int]:
    """
    分页查询系统日志（监控面板-调用日志页使用），返回 (日志列表, 总数)

    :param user_id: 指定用户ID；None 表示查全部用户（仅管理员场景使用）
    :param log_type: 日志类型筛选（api / login / admin / user）
    :param keyword: 用户名 / 动作 / 详情 模糊搜索
    :param start / end: 时间范围（闭开区间 [start, end)）
    """
    conditions, params = [], {}
    if user_id is not None:
        conditions.append("user_id = :user_id")
        params["user_id"] = user_id
    if log_type:
        conditions.append("type = :log_type")
        params["log_type"] = log_type
    if keyword:
        conditions.append("(username LIKE :kw OR action LIKE :kw OR detail LIKE :kw)")
        params["kw"] = f"%{keyword}%"
    if model_name:
        conditions.append("model_name = :model_name")
        params["model_name"] = model_name
    if start:
        conditions.append("create_time >= :start")
        params["start"] = start
    if end:
        conditions.append("create_time < :end")
        params["end"] = end
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    count_result = await db.execute(text(f"SELECT COUNT(*) FROM logs {where}"), params)
    total = count_result.scalar_one()

    result = await db.execute(
        text(f"""
            SELECT * FROM logs {where}
            ORDER BY id DESC
            LIMIT :limit OFFSET :offset
        """),
        {**params, "limit": page_size, "offset": (page - 1) * page_size},
    )
    return [dict(r) for r in result.mappings().all()], total
