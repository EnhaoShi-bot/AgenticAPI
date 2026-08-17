"""API 密钥表数据访问层"""

import secrets
from datetime import datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import ApiKeyTable
from app.models.user import UserTabel

# 每个用户最多可创建的密钥数
MAX_KEYS_PER_USER = 5


def generate_api_key() -> str:
    """生成对外密钥：sk- 前缀 + 随机串（token_urlsafe(32) 约43位）"""
    return "sk-" + secrets.token_urlsafe(32)


async def count_by_user(db: AsyncSession, user_id: int) -> int:
    """统计用户已创建的密钥数"""
    result = await db.execute(
        select(func.count()).select_from(ApiKeyTable).where(ApiKeyTable.user_id == user_id)
    )
    return result.scalar_one()


async def list_by_user(db: AsyncSession, user_id: int) -> list[ApiKeyTable]:
    """获取用户的全部密钥（按创建时间倒序）"""
    result = await db.execute(
        select(ApiKeyTable)
        .where(ApiKeyTable.user_id == user_id)
        .order_by(ApiKeyTable.id.desc())
    )
    return list(result.scalars().all())


async def create_key(db: AsyncSession, user_id: int, name: str) -> ApiKeyTable | None:
    """创建密钥，超过数量上限时返回 None"""
    if await count_by_user(db, user_id) >= MAX_KEYS_PER_USER:
        return None
    key = ApiKeyTable(user_id=user_id, name=name, key=generate_api_key())
    db.add(key)
    await db.commit()
    await db.refresh(key)
    return key


async def update_key(db: AsyncSession, user_id: int, key_id: int, update_dict: dict) -> int:
    """更新用户自己的密钥（按 id 定位，同时校验归属），返回受影响行数"""
    result = await db.execute(
        update(ApiKeyTable)
        .where(ApiKeyTable.id == key_id, ApiKeyTable.user_id == user_id)
        .values(**update_dict)
    )
    await db.commit()
    return result.rowcount


async def delete_key(db: AsyncSession, user_id: int, key_id: int) -> int:
    """删除用户自己的密钥，返回受影响行数"""
    result = await db.execute(
        delete(ApiKeyTable).where(ApiKeyTable.id == key_id, ApiKeyTable.user_id == user_id)
    )
    await db.commit()
    return result.rowcount


async def delete_keys_by_user_ids(db: AsyncSession, user_ids: list[int]) -> None:
    """批量删除多个用户的全部密钥（管理员删除用户时联动清理）"""
    if user_ids:
        await db.execute(delete(ApiKeyTable).where(ApiKeyTable.user_id.in_(user_ids)))


async def get_valid_key_with_user(db: AsyncSession, key: str) -> tuple[ApiKeyTable, UserTabel] | None:
    """按密钥值查找启用中的密钥及其所属用户（中转接口鉴权用），无效返回 None"""
    result = await db.execute(
        select(ApiKeyTable, UserTabel)
        .join(UserTabel, UserTabel.id == ApiKeyTable.user_id)
        .where(ApiKeyTable.key == key, ApiKeyTable.status == 1)
    )
    return result.first()


async def touch_last_used(db: AsyncSession, key_id: int) -> None:
    """更新密钥最后使用时间"""
    await db.execute(
        update(ApiKeyTable).where(ApiKeyTable.id == key_id).values(last_used_time=datetime.now())
    )
    await db.commit()
