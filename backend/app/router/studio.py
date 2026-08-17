"""模型工坊接口（对话式 Playground，需登录、不计费）

- POST /studio/chat：SSE 流式对话，内部复用中转链路（渠道轮询 / 日志 / 用量统计），
  但不扣余额、不写对话记录；报文走 OpenAI 风格（成功透传上游 SSE，失败返回 {"error": {...}}），
  与 /v1 中转接口一致，不套用站内统一 {code, message, data} 格式
- POST /studio/asr：语音转文本，代理阶跃星辰 StepFun ASR（统一响应格式）
"""

import json

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import setting
from app.router.deps import get_db
from app.schemas.studio import StudioAsrSchema, StudioChatSchema
from app.services import relay_service
from app.services.relay_service import RelayError
from app.utils.auth import get_current_user
from app.utils.response import success_response

router = APIRouter(prefix="/studio", tags=["Studio"])

# 联网搜索工具定义：透传给上游，由支持服务端搜索的模型执行（如火山方舟 doubao 系列）
WEB_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for current information, news, or facts.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query to look up on the web"}
            },
            "required": ["query"],
        },
    },
}

# 阶跃星辰语音识别服务（SSE 流式返回识别结果）
ASR_URL = "https://api.stepfun.com/step_plan/v1/audio/asr/sse"


def _build_chat_payload(body: StudioChatSchema) -> dict:
    """把工坊请求组装为中转链路的透传 payload"""
    messages: list[dict] = []
    if body.system_prompt.strip():
        messages.append({"role": "system", "content": body.system_prompt.strip()})
    for m in body.messages:
        content = m.content
        # 跳过空消息（前端流式截断后可能残留空 assistant 占位）
        if isinstance(content, str) and not content.strip():
            continue
        if isinstance(content, list) and not content:
            continue
        messages.append({"role": m.role, "content": content})

    payload: dict = {"model": body.model, "messages": messages, "stream": True}
    if body.temperature is not None:
        payload["temperature"] = body.temperature
    if body.top_p is not None:
        payload["top_p"] = body.top_p
    if body.max_tokens is not None:
        payload["max_tokens"] = body.max_tokens
    if body.enable_search:
        payload["tools"] = [WEB_SEARCH_TOOL]
    return payload


@router.post("/chat")
async def studio_chat(body: StudioChatSchema, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    """
    工坊对话（仅支持流式）。鉴权走站内登录令牌，模型分组权限与中转一致
    （free 用户仅 free 模型，vip 全部），调用不计费。
    """
    payload = _build_chat_payload(body)
    if not payload["messages"]:
        return RelayError(400, "消息列表不能为空").to_response()

    try:
        return await relay_service.chat_completions(db, payload, user, None, source="studio")
    except RelayError as exc:
        # 降级重试：开启联网搜索但上游渠道不认 tools（返回 400/422）时，剥掉 tools 再试一次
        if body.enable_search and ("400" in exc.message or "422" in exc.message):
            payload.pop("tools", None)
            try:
                return await relay_service.chat_completions(db, payload, user, None, source="studio")
            except RelayError as retry_exc:
                return retry_exc.to_response()
        return exc.to_response()


@router.post("/asr")
async def studio_asr(body: StudioAsrSchema, user=Depends(get_current_user)):
    """语音转文本：前端录音 base64 上传，代理 StepFun ASR 返回识别文本"""
    if not setting.STEPFUN_API_KEY:
        raise HTTPException(status_code=503, detail="语音服务未配置，请在后端 .env 中设置 STEPFUN_API_KEY")

    audio = body.audio
    # 兼容前端直接传 data URL 的情况（data:audio/webm;base64,xxxx）
    if audio.startswith("data:") and "," in audio:
        audio = audio.split(",", 1)[1]

    payload = {
        "audio": {
            "data": audio,
            "input": {
                "transcription": {"model": "stepaudio-2.5-asr", "language": "zh", "enable_itn": True},
                "format": {"type": body.format or "mp3"},
            },
        }
    }
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                ASR_URL, json=payload,
                headers={"Accept": "text/event-stream", "Authorization": f"Bearer {setting.STEPFUN_API_KEY}"},
            )
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="语音识别服务请求失败")

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"语音识别上游返回 {resp.status_code}")

    # 解析 SSE：取 type == "transcript.text.done" 事件的最终识别文本
    final_text = ""
    for line in resp.text.splitlines():
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if not data:
            continue
        try:
            event = json.loads(data)
        except Exception:
            continue
        if isinstance(event, dict) and event.get("type") == "transcript.text.done" and event.get("text"):
            final_text = event["text"]
            break
    return success_response(message="语音识别成功", data={"text": final_text})
