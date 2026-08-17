"""对话记录表数据访问层"""

import json
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_record import ChatRecordTable


async def insert_record(
        db: AsyncSession,
        *,
        user_id: int,
        username: str,
        model_name: str,
        channel_name: str | None = None,
        input_content: str | None = None,
        reasoning_content: str | None = None,
        output_content: str | None = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cache_tokens: int = 0,
        cost: Decimal | float = 0,
        duration_ms: int | None = None,
) -> None:
    """写入一条对话记录（中转链路计费收尾处调用，是否写入由上游条件判断）"""
    db.add(ChatRecordTable(
        user_id=user_id,
        username=username,
        model_name=model_name,
        channel_name=channel_name,
        input_content=input_content,
        reasoning_content=reasoning_content,
        output_content=output_content,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        cache_tokens=cache_tokens,
        cost=cost,
        duration_ms=duration_ms,
    ))
    await db.commit()


async def list_records(
        db: AsyncSession,
        *,
        user_id: int | None = None,
        username_keyword: str = "",
        model_name: str = "",
        page: int = 1,
        page_size: int = 10,
) -> tuple[list[dict], int]:
    """
    分页查询对话记录，返回 (记录列表, 总数)

    :param user_id: 指定用户ID；None 表示查全部用户（仅管理员场景使用）
    :param username_keyword: 用户名模糊筛选（管理员用）
    :param model_name: 模型名精确筛选
    """
    conditions, params = [], {}
    if user_id is not None:
        conditions.append("user_id = :user_id")
        params["user_id"] = user_id
    if username_keyword:
        conditions.append("username LIKE :username_kw")
        params["username_kw"] = f"%{username_keyword}%"
    if model_name:
        conditions.append("model_name = :model_name")
        params["model_name"] = model_name
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    count_result = await db.execute(text(f"SELECT COUNT(*) FROM chat_record {where}"), params)
    total = count_result.scalar_one()

    result = await db.execute(
        text(f"""
            SELECT * FROM chat_record {where}
            ORDER BY id DESC
            LIMIT :limit OFFSET :offset
        """),
        {**params, "limit": page_size, "offset": (page - 1) * page_size},
    )
    records = []
    for row in result.mappings().all():
        record = dict(row)
        # input_content 库里存的是 messages 数组的 JSON 字符串，出参还原为数组
        try:
            record["input_content"] = json.loads(record["input_content"]) if record["input_content"] else []
        except (TypeError, ValueError):
            record["input_content"] = []
        records.append(record)
    return records, total
