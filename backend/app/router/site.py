"""站点公开配置接口

把后端 .env 里配置的对外公开地址下发给前端：
控制台-秘钥页与模型示例面板展示的中转接口地址都来自这里，
部署到公网后只需改 backend/.env 的 PUBLIC_BASE_URL，前端自动跟随。
"""

from fastapi import APIRouter
from app.core.config import server_setting
from app.utils.response import success_response

router = APIRouter(prefix="/site", tags=["Site"])


@router.get("/info")
async def get_site_info():
    """获取站点公开配置（无需登录）：对外中转接口的基地址等"""
    return success_response(
        message="获取站点配置成功",
        data={
            "publicBaseUrl": server_setting.PUBLIC_BASE_URL.rstrip('/'),
            "relayBaseUrl": server_setting.RELAY_BASE_URL,
        },
    )
