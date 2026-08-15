"""API 路由聚合"""

from fastapi import APIRouter

from app.api import channels, models, operations

router = APIRouter()
router.include_router(models.router)  # 和模型列表相关接口
router.include_router(channels.router)  # 和渠道列表相关接口
router.include_router(operations.router)  # 和上游渠道运维相关接口
