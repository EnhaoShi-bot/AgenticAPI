"""核心中转服务

对外提供 OpenAI Chat Completions 兼容接口，把请求透传到上游渠道（同样是 OpenAI 格式，
不做格式转换）。链路：API密钥鉴权 → 模型/分组/余额校验 → 按渠道顺序轮询转发 →
计费扣减 → 用量统计 → 调用日志（满足条件时另记对话内容，见 _finalize_call）。

【重要】本服务的响应直接使用 OpenAI 的报文格式（成功透传上游 JSON / SSE，失败返回
{"error": {...}}），不走全站统一的 {code, message, data} 格式——因为调用方是 OpenAI
SDK / 任意 HTTP 客户端，不是本项目自己的前端。
"""

import json
import time
from decimal import Decimal, ROUND_HALF_UP

import httpx
from fastapi.responses import JSONResponse, Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import channel as channel_crud
from app.crud import chat_record as chat_record_crud
from app.crud import log as log_crud
from app.crud import model as model_crud
from app.crud import system_config as config_crud
from app.crud import usage_stats as stats_crud
from app.crud.api_key import touch_last_used
from app.crud.user import deduct_balance
from app.models.user import UserTabel
from app.utils.json_utils import parse_json_list

# 模型级轮询游标：{模型名: 下一次调用的起始下标}，让同一模型的多次调用分散到不同渠道
_round_robin: dict[str, int] = {}


class RelayError(Exception):
    """中转链路错误：以 OpenAI 兼容格式返回给调用方"""

    def __init__(self, status_code: int, message: str, err_type: str = "invalid_request_error"):
        self.status_code = status_code
        self.message = message
        self.err_type = err_type

    def to_response(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status_code,
            content={"error": {"message": self.message, "type": self.err_type, "code": self.status_code}},
        )


def compute_cost(model: dict, usage: dict) -> tuple[Decimal, int, int, int]:
    """
    按模型定价计算本次调用费用，返回 (费用, 输入token, 输出token, 缓存token)

    - 按次计费模式（is_request_mode）：固定收 per_request_price
    - 按量计费：输入/输出/缓存 token 分别乘单价（单价单位：每百万 token），缓存命中的
      部分按缓存价计，不重复收输入价
    """
    prompt_tokens = int(usage.get("prompt_tokens") or 0)
    completion_tokens = int(usage.get("completion_tokens") or 0)
    cache_tokens = int((usage.get("prompt_tokens_details") or {}).get("cached_tokens") or 0)

    if model.get("is_request_mode"):
        cost = Decimal(str(model.get("per_request_price") or 0))
    else:
        billable_prompt = max(prompt_tokens - cache_tokens, 0)
        cost = (
            Decimal(billable_prompt) * Decimal(str(model.get("input_price") or 0))
            + Decimal(cache_tokens) * Decimal(str(model.get("cache_price") or 0))
            + Decimal(completion_tokens) * Decimal(str(model.get("output_price") or 0))
        ) / Decimal(1_000_000)

    # 金额统一保留 6 位小数（与余额字段精度一致）
    return cost.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP), prompt_tokens, completion_tokens, cache_tokens


def _ordered_channels(model_name: str, channels: list[str]) -> list[str]:
    """按轮询游标确定本次调用的渠道尝试顺序（起点轮转，失败依次向后尝试）"""
    if not channels:
        return []
    start = _round_robin.get(model_name, 0) % len(channels)
    _round_robin[model_name] = start + 1
    return channels[start:] + channels[:start]


async def chat_completions(
    db: AsyncSession, payload: dict, user: UserTabel,
    api_key_id: int | None = None, *, source: str = "relay",
):
    """
    中转主流程。返回 FastAPI Response（JSON 或 SSE 流）。

    :param payload: 调用方请求体（原样透传给上游）
    :param user: API 密钥对应的用户（路由层已完成密钥鉴权）
    :param api_key_id: 使用的密钥ID（用于更新最后使用时间；工坊等站内调用无密钥，传 None）
    :param source: 调用来源。"relay" = 对外中转（计费）；"studio" = 模型工坊（免费，
        跳过余额校验与扣款，日志 cost 记 0，不写对话记录，token 照常进用量统计）
    """
    start_ms = time.time()

    # ── 1. 模型校验 ──
    model_name = payload.get("model")
    if not model_name or not isinstance(model_name, str):
        raise RelayError(400, "请求体缺少 model 字段")
    model = await model_crud.get_by_name(db, model_name)
    if not model or not model.get("status"):
        raise RelayError(404, f"模型 {model_name} 不存在或已停用", "invalid_request_error")

    # ── 2. 分组权限：free 用户只能调用 free 分组模型，vip 可调用全部 ──
    if model.get("model_group") != "free" and user.user_group != "vip":
        raise RelayError(403, f"当前用户分组（{user.user_group}）无权调用模型 {model_name}", "access_denied")

    # ── 3. 余额校验（余额小于等于 0 时拒绝调用；实际扣费在调用成功后） ──
    #    工坊调用免费，跳过此检查（访客余额为 0 也可使用）
    if source != "studio" and user.balance <= 0:
        raise RelayError(402, "账户余额不足，请联系管理员充值", "insufficient_quota")

    # ── 4. 渠道解析与轮询 ──
    channel_names = parse_json_list(model.get("channels"))
    if not channel_names:
        raise RelayError(502, f"模型 {model_name} 未绑定可用渠道", "api_error")

    is_stream = bool(payload.get("stream"))
    upstream_body = dict(payload)
    if is_stream:
        # 流式响应默认不返回用量，加上 include_usage 让上游在最后一个 chunk 带回 usage 供计费
        upstream_body.setdefault("include_usage", True)

    last_error = "无可用渠道"
    for channel_name in _ordered_channels(model_name, channel_names):
        channel = await channel_crud.get_by_name(db, channel_name)
        if not channel or not channel.get("status"):
            last_error = f"渠道 {channel_name} 不存在或已停用"
            continue

        headers = {"Authorization": f"Bearer {channel['api_key']}"}
        timeout = httpx.Timeout(channel.get("timeout") or 30)

        if not is_stream:
            # ── 非流式：等待完整响应后透传 ──
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    resp = await client.post(channel["base_url"], json=upstream_body, headers=headers)
            except httpx.HTTPError as exc:
                last_error = f"渠道 {channel_name} 请求异常：{exc.__class__.__name__}"
                continue

            if resp.status_code != 200:
                last_error = f"渠道 {channel_name} 返回 {resp.status_code}"
                continue

            try:
                data = resp.json()
            except Exception:
                data = {}
            if not isinstance(data, dict):
                data = {}
            # 提取完整回复（choices[0].message），供满足记录条件时落库对话内容
            choices = data.get("choices") or []
            message = (choices[0].get("message") if choices and isinstance(choices[0], dict) else None) or {}
            conversation = {
                "input": payload.get("messages"),
                "reasoning": message.get("reasoning_content") or "",
                "output": message.get("content") or "",
            }
            await _finalize_call(
                db, user=user, model=model, channel_name=channel_name, api_key_id=api_key_id,
                start_ms=start_ms, usage=data.get("usage") or {}, conversation=conversation,
                is_stream=False, source=source,
            )
            return Response(content=resp.content, media_type="application/json")

        # ── 流式：边转发边解析，流结束后计费 ──
        client = httpx.AsyncClient(timeout=timeout)
        try:
            req = client.build_request("POST", channel["base_url"], json=upstream_body, headers=headers)
            resp = await client.send(req, stream=True)
        except httpx.HTTPError as exc:
            await client.aclose()
            last_error = f"渠道 {channel_name} 请求异常：{exc.__class__.__name__}"
            continue

        if resp.status_code != 200:
            body = await resp.aread()
            await resp.aclose()
            await client.aclose()
            last_error = f"渠道 {channel_name} 返回 {resp.status_code}"
            continue

        return StreamingResponse(
            _stream_and_bill(db, resp, client, user, model, channel_name, api_key_id, start_ms,
                             payload.get("messages"), source=source),
            media_type="text/event-stream",
        )

    raise RelayError(502, f"所有上游渠道调用失败：{last_error}", "api_error")


async def _finalize_call(
    db: AsyncSession, *, user: UserTabel, model: dict, channel_name: str,
    api_key_id: int | None, start_ms: float, usage: dict, conversation: dict,
    is_stream: bool = False, source: str = "relay",
) -> None:
    """
    调用成功后的统一收尾（非流式与流式共用）：
    计费扣减 → 更新密钥使用时间 → 写调用日志 → 累加用量统计 →（满足条件时）写对话记录。

    token 数量无条件记入 logs / usage_stats / usage_summary；
    对话内容仅在模型开启 is_log 且 输入+输出 token ≤ 管理员阈值
    （system_config 的 chat_record_max_tokens，默认 5000）时记录，避免落库超长文本。
    工坊调用（source="studio"）免费：不扣款、日志 cost 记 0、不写对话记录，统计照常。
    """
    is_studio = source == "studio"
    cost, prompt_tokens, completion_tokens, cache_tokens = compute_cost(model, usage)
    duration_ms = int((time.time() - start_ms) * 1000)
    model_name = model.get("name")

    if not is_studio:
        await deduct_balance(db, user.id, cost)
    if api_key_id is not None:
        await touch_last_used(db, api_key_id)
    await log_crud.write_log(
        db, type="api", action="chat", user_id=user.id, username=user.username,
        detail=(f"工坊调用模型 {model_name}（流式，免费）" if is_stream and is_studio
                else f"工坊调用模型 {model_name}（免费）" if is_studio
                else f"中转调用模型 {model_name}（流式）" if is_stream
                else f"中转调用模型 {model_name}"),
        model_name=model_name, channel_name=channel_name,
        prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
        cache_tokens=cache_tokens, cost=Decimal(0) if is_studio else cost, duration_ms=duration_ms,
    )

    # ── 用量统计（小时桶 + 全站汇总行）：失败只打日志，不影响计费与响应 ──
    try:
        await stats_crud.record_usage(
            db, user_id=user.id, model_name=model_name,
            prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
            cache_tokens=cache_tokens,
        )
        await stats_crud.bump_summary(
            db, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
            cache_tokens=cache_tokens,
        )
        await db.commit()
    except Exception as exc:
        await db.rollback()
        print(f"[relay] 用量统计写入失败: {exc.__class__.__name__}: {exc}")

    # ── 对话记录：工坊对话不写（监控页的对话数据仅统计中转接口调用），未开启 is_log 也直接返回 ──
    if is_studio or not model.get("is_log"):
        return
    try:
        threshold = await config_crud.get_chat_record_threshold(db)
        if prompt_tokens + completion_tokens > threshold:
            return
        input_messages = conversation.get("input")
        await chat_record_crud.insert_record(
            db, user_id=user.id, username=user.username, model_name=model_name,
            channel_name=channel_name,
            input_content=json.dumps(input_messages, ensure_ascii=False) if isinstance(input_messages, list) else None,
            reasoning_content=conversation.get("reasoning") or None,
            output_content=conversation.get("output") or None,
            prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
            cache_tokens=cache_tokens, cost=cost, duration_ms=duration_ms,
        )
    except Exception as exc:
        print(f"[relay] 对话记录写入失败: {exc.__class__.__name__}: {exc}")


async def _stream_and_bill(
    db, resp, client, user: UserTabel, model: dict,
    channel_name: str, api_key_id: int | None, start_ms: float, input_messages,
    source: str = "relay",
):
    """
    流式转发生成器：原样转发上游 SSE 分块，同时按行解析 usage 与文本增量；
    流结束后统一收尾（计费 / 日志 / 统计 / 对话记录）。

    【注意】FastAPI 在流式响应发送完毕后才关闭 get_db 提供的会话，所以这里可以继续用 db。
    """
    usage: dict = {}
    parts = {"reasoning": "", "output": ""}  # 逐块累积的推理与输出文本
    line_buf = b""  # SSE 分块可能把一行 JSON 从中间切断，需要按行缓冲拼接
    try:
        async for chunk in resp.aiter_bytes():
            line_buf += chunk
            while b"\n" in line_buf:
                line, line_buf = line_buf.split(b"\n", 1)
                _parse_sse_line(line, usage, parts)
            yield chunk
        if line_buf:
            _parse_sse_line(line_buf, usage, parts)
    finally:
        await resp.aclose()
        await client.aclose()
        conversation = {"input": input_messages, "reasoning": parts["reasoning"], "output": parts["output"]}
        try:
            await _finalize_call(
                db, user=user, model=model, channel_name=channel_name, api_key_id=api_key_id,
                start_ms=start_ms, usage=usage, conversation=conversation, is_stream=True,
                source=source,
            )
        except Exception as exc:  # 收尾失败不能影响已经发出去的响应，只记控制台日志
            print(f"[relay] 流式调用计费失败: {exc.__class__.__name__}: {exc}")


def _parse_sse_line(line: bytes, usage: dict, parts: dict) -> None:
    """
    解析一条 SSE 行（OpenAI 约定 data: {...}）：
    - usage：最后一个 chunk 携带的用量对象，用于计费
    - parts：累积 delta.content / delta.reasoning_content 文本增量，用于对话记录
    """
    if not line.startswith(b"data:"):
        return
    data = line[5:].strip()
    if not data or data == b"[DONE]":
        return
    try:
        obj = json.loads(data)
    except Exception:
        return
    if not isinstance(obj, dict):
        return
    if isinstance(obj.get("usage"), dict) and obj["usage"].get("prompt_tokens") is not None:
        usage.clear()
        usage.update(obj["usage"])
    choices = obj.get("choices") or []
    if choices and isinstance(choices[0], dict):
        delta = choices[0].get("delta") or {}
        if isinstance(delta.get("reasoning_content"), str):
            parts["reasoning"] += delta["reasoning_content"]
        if isinstance(delta.get("content"), str):
            parts["output"] += delta["content"]
