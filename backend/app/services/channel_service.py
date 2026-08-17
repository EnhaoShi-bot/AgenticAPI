"""渠道业务逻辑层"""

import json

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import channel as channel_crud
from app.schemas.channel import ChannelSchema
from app.utils.json_utils import parse_json_list


async def list_channels(db: AsyncSession) -> list[dict]:
    """获取全量渠道列表，support_models 解析为真正的数组返回前端"""
    channels = await channel_crud.get_all(db)
    result = []
    for channel in channels:
        d = dict(channel)
        d["support_models"] = parse_json_list(d.get("support_models"))
        result.append(ChannelSchema(**d).model_dump(by_alias=True, mode="json"))
    return result


async def list_channel_names(db: AsyncSession) -> list[str]:
    """获取全量渠道名列表（公开接口用，只返回名称，不含 api_key 等敏感字段）"""
    return await channel_crud.get_all_names(db)


async def create_channel(db: AsyncSession, new_channel: ChannelSchema) -> int:
    """添加单个渠道，返回新增记录的自增主键 id

    业务错误（渠道名重复等）抛 HTTPException，由全局异常处理器统一格式化；
    数据库错误抛 SQLAlchemyError，同样由全局异常处理器捕获，
    回滚交由 get_db 依赖的 except 分支完成，这里无需 try/except。
    """
    channel = new_channel.model_dump()

    # 插入前检查 channel_name 是否已存在
    if await channel_crud.get_id_by_name(db, channel["channel_name"]):
        raise HTTPException(
            status_code=400, detail=f"渠道名称 '{channel['channel_name']}' 已存在"
        )

    # support_models：把数组序列化为 JSON 字符串存库
    channel["support_models"] = json.dumps(channel.get("support_models") or [], ensure_ascii=False)

    res_id = await channel_crud.insert(db, channel)
    await db.commit()

    if not res_id:
        raise HTTPException(status_code=500, detail="添加渠道失败")
    return res_id


async def update_channel(db: AsyncSession, channel_name: str, update_data: ChannelSchema) -> None:
    """更新单个渠道数据（按 channel_name 定位，channel_name 本身不能更新）"""
    if not channel_name or not channel_name.strip():
        raise HTTPException(status_code=400, detail="渠道名称不能为空")
    channel_name = channel_name.strip()

    if not await channel_crud.get_id_by_name(db, channel_name):
        raise HTTPException(status_code=404, detail=f"渠道 '{channel_name}' 不存在")

    # 过滤掉未传字段，同时排除 channel_name 字段（定位键不可更新）
    update_dict = update_data.model_dump(exclude_unset=True, exclude={"channel_name"})
    if not update_dict:
        raise HTTPException(status_code=400, detail="未提供任何需要更新的字段")

    # support_models：把数组序列化为 JSON 字符串存库
    if "support_models" in update_dict and update_dict["support_models"] is not None:
        update_dict["support_models"] = json.dumps(update_dict["support_models"], ensure_ascii=False)

    await channel_crud.update_by_name(db, channel_name, update_dict)
    await db.commit()


async def remove_channel(db: AsyncSession, channel_name: str) -> None:
    """删除渠道"""
    if not channel_name or not channel_name.strip():
        raise HTTPException(status_code=400, detail="渠道名称不能为空")
    channel_name = channel_name.strip()

    if not await channel_crud.get_id_by_name(db, channel_name):
        raise HTTPException(status_code=404, detail=f"渠道名称 '{channel_name}' 不存在")

    rowcount = await channel_crud.delete_by_name(db, channel_name)
    await db.commit()

    if rowcount == 0:
        raise HTTPException(status_code=500, detail="删除渠道失败，未影响任何记录")
