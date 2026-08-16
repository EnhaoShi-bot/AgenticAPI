"""渠道相关接口"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.channel import ChannelSchema
from app.services import channel_service

router = APIRouter(prefix="/channels",tags=["Channels"])


@router.get("/get")
async def get_channels(db: AsyncSession = Depends(get_db)):
    """获取全量渠道列表"""
    return await channel_service.list_channels(db)


@router.post("/post")
async def add_channel(new_channel: ChannelSchema, db: AsyncSession = Depends(get_db)):
    """添加单个渠道"""
    return await channel_service.create_channel(db, new_channel)


@router.put("/put")
async def put_channel(update_data: ChannelSchema, db: AsyncSession = Depends(get_db)):
    """更新单个渠道数据（channel_name 不能更新）"""
    return await channel_service.update_channel(db, update_data)


@router.delete("/delete")
async def delete_channel(channel_name: str, db: AsyncSession = Depends(get_db)):
    """删除渠道"""
    return await channel_service.remove_channel(db, channel_name)
