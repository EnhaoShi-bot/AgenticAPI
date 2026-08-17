"""对外中转接口（OpenAI 兼容）

这是给外部调用方（OpenAI SDK / curl / 第三方应用）用的入口，
用 API 密钥（sk-xxx）鉴权，与站内 Bearer 登录令牌是两套凭证。
"""

import json
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import api_key as api_key_crud
from app.router.deps import get_db
from app.services import relay_service
from app.services.relay_service import RelayError

router = APIRouter(prefix="/v1", tags=["Relay"])


@router.post("/chat/completions")
async def chat_completions(request: Request, db: AsyncSession = Depends(get_db)):
    """
    OpenAI Chat Completions 兼容中转接口

    - 鉴权：Authorization: Bearer sk-xxx（API 密钥，在控制台-秘钥页面创建）
    - 报文：成功时透传上游 JSON / SSE，失败时返回 OpenAI 格式 {"error": {...}}
    """
    # ── API 密钥鉴权（兼容不带 Bearer 前缀的写法） ──
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        api_key = auth[7:].strip()
    else:
        api_key = auth.strip()

    if not api_key:
        return RelayError(401, "未提供 API 密钥", "invalid_request_error").to_response()

    row = await api_key_crud.get_valid_key_with_user(db, api_key)
    if not row:
        return RelayError(401, "无效的 API 密钥", "invalid_request_error").to_response()
    key_obj, user = row

    if not user.status:
        return RelayError(403, "账号已被封禁", "access_denied").to_response()

    # ── 解析请求体（原样透传，不做格式转换） ──
    try:
        payload = json.loads(await request.body())
    except Exception:
        return RelayError(400, "请求体不是合法的 JSON", "invalid_request_error").to_response()
    if not isinstance(payload, dict):
        return RelayError(400, "请求体必须是 JSON 对象", "invalid_request_error").to_response()

    # ── 中转主流程（模型/分组/余额校验 → 渠道轮询转发 → 计费日志） ──
    try:
        return await relay_service.chat_completions(db, payload, user, key_obj.id)
    except RelayError as exc:
        return exc.to_response()
