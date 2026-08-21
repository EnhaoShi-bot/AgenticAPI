"""API 路由聚合"""

from fastapi import APIRouter

from app.router import channels, models, operations, user, keys, admin, relay, monitor, studio, site

router = APIRouter()
router.include_router(site.router)  # 站点公开配置（对外中转地址等，前端展示用）
router.include_router(models.router)  # 和模型列表相关接口
router.include_router(channels.router)  # 和渠道列表相关接口
router.include_router(operations.router)  # 和上游渠道运维相关接口
router.include_router(user.router)  # 和用户登录注册相关接口
router.include_router(keys.router)  # 用户API密钥管理接口
router.include_router(admin.router)  # 管理员用户管理接口
router.include_router(monitor.router)  # 监控面板接口（对话数据/调用日志/数据看板）
router.include_router(relay.router)  # 对外中转接口（OpenAI兼容）
router.include_router(studio.router)  # 模型工坊接口（对话式 Playground，流式 + 语音识别）
