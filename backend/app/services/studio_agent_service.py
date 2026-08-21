"""模型工坊联网搜索 Agent 循环

上游模型把 web_search 当"客户端函数工具"：发出 tool_calls 后停住，等调用方执行完
把结果以 role:"tool" 消息回传再继续生成。此前中转链路纯透传、无人执行工具，导致
"一搜就结束任务"。本服务就是那个"调用方"——把多轮上游流式调用编排成对前端而言的
一条连续 SSE：

  第 N 轮：请求上游（首轮带 tools），边转发 reasoning / content 增量边累积 tool_calls
  命中 tool_calls → 执行 StepSearch（search_service）→ 消息追加
      assistant(tool_calls) + tool(搜索结果) → 同渠道重发进入下一轮
  finish_reason 不再是 tool_calls → 补聚合 usage 与 [DONE]，收尾（日志 / 用量统计）

约定：
- 只服务工坊（source=studio，免费）；对外中转接口保持纯透传语义，不做工具编排；
- 搜索起止通过自定义 SSE 事件 {"agenticapi_search": {...}} 推给前端渲染状态条，
  该事件是站内扩展字段，OpenAI SDK 调用方（不会走到这条链路）不受影响；
- tool_calls 增量、中间轮的 usage / [DONE] 不透传，避免前端看到中断痕迹；
  最终 usage 为各轮求和后合成的单个 chunk；
- 渠道故障只在首轮换渠道重试（此时还未向前端写过任何字节）；续轮失败只能以
  流内 error 事件收尾；
- 方舟 doubao 系列会在工具调用轮返回加密思维链 encrypted_content，回传 assistant
  消息时原样带上，保证多轮推理连续性。
"""

import json
import time

import httpx
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import channel as channel_crud
from app.models.user import UserTabel
from app.services import relay_service, search_service
from app.services.relay_service import RelayError, _finalize_call, _ordered_channels, _rewrite_sse_model

# 搜索轮数上限：超过后为剩余 tool_calls 回"上限"说明并剥掉 tools，强制收尾一轮
MAX_SEARCH_ROUNDS = 5


async def chat_with_search(db: AsyncSession, payload: dict, user: UserTabel):
    """
    工坊联网搜索入口：校验与渠道轮询复用中转链路，命中渠道后交给编排生成器。
    返回 FastAPI Response（SSE 流）；所有渠道首轮即失败时抛 RelayError(502)。
    """
    start_ms = time.time()
    model, channel_names = await relay_service.resolve_target(db, payload, user, source="studio")

    model_name = model["name"]
    # 模型映射：对外名 ↔ 上游名（与中转链路同规则）
    upstream_name = model.get("upstream_name") or ""
    needs_mapping = bool(upstream_name) and upstream_name != model_name

    body = dict(payload)
    body["model"] = upstream_name or model_name
    body["stream"] = True
    body.setdefault("include_usage", True)

    last_error = "无可用渠道"
    for channel_name in _ordered_channels(model_name, channel_names):
        channel = await channel_crud.get_by_name(db, channel_name)
        if not channel or not channel.get("status"):
            last_error = f"渠道 {channel_name} 不存在或已停用"
            continue

        headers = {"Authorization": f"Bearer {channel['api_key']}"}
        timeout = httpx.Timeout(channel.get("timeout") or 30)

        resp, client, retry_error = await _first_round(channel, body, headers, timeout)
        if retry_error:
            last_error = retry_error
            continue

        return StreamingResponse(
            _agent_stream(db, resp, client, channel, headers, body, user, model,
                          start_ms, list(payload.get("messages") or []), needs_mapping, model_name),
            media_type="text/event-stream",
        )

    raise RelayError(502, f"所有上游渠道调用失败：{last_error}", "api_error")


async def _first_round(channel: dict, body: dict, headers: dict, timeout: httpx.Timeout):
    """
    发起首轮上游请求（流式）。失败时返回 (None, None, 错误描述) 供换渠道重试；
    上游对 tools 报 400/422 时剥掉 tools 降级重试一次（不支持函数工具的模型照常对话）。
    """
    for attempt in (body, {k: v for k, v in body.items() if k != "tools"}):
        client = httpx.AsyncClient(timeout=timeout)
        try:
            req = client.build_request("POST", channel["base_url"], json=attempt, headers=headers)
            resp = await client.send(req, stream=True)
        except httpx.HTTPError as exc:
            await client.aclose()
            return None, None, f"渠道 {channel['channel_name']} 请求异常：{exc.__class__.__name__}"

        if resp.status_code in (400, 422) and "tools" in attempt:
            # 可能是 tools 不被支持：剥掉重试一次（成功则说明该模型只能普通对话）
            await resp.aread()
            await resp.aclose()
            await client.aclose()
            body.pop("tools", None)
            continue
        if resp.status_code != 200:
            await resp.aread()
            await resp.aclose()
            await client.aclose()
            return None, None, f"渠道 {channel['channel_name']} 返回 {resp.status_code}"
        return resp, client, None

    return None, None, f"渠道 {channel['channel_name']} 不支持联网搜索工具"


async def _agent_stream(db, resp, client, channel, headers, body, user, model,
                        start_ms, input_messages, needs_mapping, model_name):
    """多轮编排生成器：消费首轮响应，命中工具调用则搜索后重发，直到正常收尾"""
    usage_total = {"prompt": 0, "completion": 0, "cached": 0}
    parts = {"reasoning": "", "output": ""}
    search_rounds = 0
    fallback_query = _last_user_text(input_messages)
    try:
        while True:
            st = {"tool_calls": {}, "encrypted": "", "finish_reason": "", "upstream_error": None,
                  "round_usage": None}
            async for out in _forward_round(resp, client, st, parts, needs_mapping, model_name):
                yield out

            # 本轮 usage（轮内最后一个非空 usage）累加进总量
            if st["round_usage"]:
                usage_total["prompt"] += st["round_usage"]["prompt"]
                usage_total["completion"] += st["round_usage"]["completion"]
                usage_total["cached"] += st["round_usage"]["cached"]

            if st["upstream_error"]:
                break

            calls = [st["tool_calls"][i] for i in sorted(st["tool_calls"])]
            if st["finish_reason"] != "tool_calls" or not calls:
                break  # 正常收尾（stop / length）或上游未发起工具调用

            # ── 规范化工具调用参数：个别模型（如 ollama 上的 minimax）会发出非法 JSON
            #    的 arguments，原样回传会被上游 400 拒绝，统一改写为 {"query": ...} ──
            for c in calls:
                try:
                    json.loads(c["arguments"] or "")
                except Exception:
                    c["arguments"] = json.dumps(
                        {"query": _extract_query(c, fallback_query)}, ensure_ascii=False)

            # ── 组装 assistant(tool_calls) 消息（encrypted_content 原样回传） ──
            assistant_msg = {"role": "assistant", "content": "", "tool_calls": [
                {"id": c["id"] or f"call_{search_rounds}_{n}", "type": "function",
                 "function": {"name": c["name"] or "web_search", "arguments": c["arguments"] or "{}"}}
                for n, c in enumerate(calls)
            ]}
            if st["encrypted"]:
                assistant_msg["encrypted_content"] = st["encrypted"]
            body["messages"] = body["messages"] + [assistant_msg]

            # ── 执行搜索：每条 tool_call 对应一条 role:"tool" 结果消息 ──
            hit_limit = search_rounds >= MAX_SEARCH_ROUNDS
            search_rounds += 1
            for n, c in enumerate(calls):
                query = _extract_query(c, fallback_query)
                if hit_limit:
                    result_text = f"已达联网搜索轮数上限（{MAX_SEARCH_ROUNDS}），请基于已有信息直接回答，不要再次调用工具。"
                else:
                    yield _search_event({"status": "start", "query": query, "round": search_rounds})
                    result_text = await search_service.web_search(query)
                    yield _search_event({"status": "end", "query": query, "round": search_rounds})
                body["messages"].append({
                    "role": "tool", "tool_call_id": assistant_msg["tool_calls"][n]["id"], "content": result_text,
                })
            if hit_limit:
                body.pop("tools", None)  # 剥掉工具，最后一轮必然直接作答

            # ── 续轮请求：同渠道（此时已向前端转发过内容，无法再换渠道） ──
            client = httpx.AsyncClient(timeout=httpx.Timeout(channel.get("timeout") or 30))
            try:
                req = client.build_request("POST", channel["base_url"], json=body, headers=headers)
                resp = await client.send(req, stream=True)
            except httpx.HTTPError as exc:
                print(f"[studio-agent] 续轮请求异常: {exc.__class__.__name__}")
                yield _error_event(f"联网搜索后的续轮请求失败（{exc.__class__.__name__}），请重试")
                break
            if resp.status_code != 200:
                detail = (await resp.aread())[:200]
                await resp.aclose()
                await client.aclose()
                print(f"[studio-agent] 续轮返回 {resp.status_code}: {detail!r}")
                yield _error_event(f"联网搜索后的续轮请求返回 {resp.status_code}，请重试")
                break

        # ── 收尾：聚合 usage 单个 chunk + [DONE]（异常中断时跳过，保持 error 事件为最后内容） ──
        if not st["upstream_error"]:
            usage = {
                "prompt_tokens": usage_total["prompt"],
                "completion_tokens": usage_total["completion"],
                "prompt_tokens_details": {"cached_tokens": usage_total["cached"]},
            }
            yield b"data: " + json.dumps({"choices": [], "usage": usage}, ensure_ascii=False).encode() + b"\n"
            yield b"data: [DONE]\n"
    finally:
        # 收尾与中转链路一致：日志（cost=0 标注工坊）+ 用量统计（多轮求和）+ 对话记录
        conversation = {"input": input_messages, "reasoning": parts["reasoning"], "output": parts["output"]}
        try:
            await _finalize_call(
                db, user=user, model=model, channel_name=channel["channel_name"], api_key_id=None,
                start_ms=start_ms, usage={
                    "prompt_tokens": usage_total["prompt"],
                    "completion_tokens": usage_total["completion"],
                    "prompt_tokens_details": {"cached_tokens": usage_total["cached"]},
                },
                conversation=conversation, is_stream=True, source="studio",
            )
        except Exception as exc:
            print(f"[studio-agent] 收尾失败: {exc.__class__.__name__}: {exc}")


async def _forward_round(resp, client, st: dict, parts: dict,
                         needs_mapping: bool, model_name: str):
    """
    消费一轮上游 SSE：reasoning / content 增量行转发给前端（yield），tool_calls 增量、
    usage、finish_reason 只解析记录不透传。流结束（或客户端断开）时关闭 resp 与 client。
    """
    line_buf = b""
    try:
        async for chunk in resp.aiter_bytes():
            line_buf += chunk
            while b"\n" in line_buf:
                line, line_buf = line_buf.split(b"\n", 1)
                out = _process_line(line, st, parts, needs_mapping, model_name)
                if out is not None:
                    yield out
        if line_buf:
            out = _process_line(line_buf, st, parts, needs_mapping, model_name)
            if out is not None:
                yield out
    finally:
        await resp.aclose()
        await client.aclose()


def _process_line(line: bytes, st: dict, parts: dict,
                  needs_mapping: bool, model_name: str) -> bytes | None:
    """
    解析一条 SSE data 行并决定去向：
    - 文本增量（reasoning / content）：转发（配置映射时改写 model 字段）
    - 流内 error 事件：转发（前端展示错误）并记录，供外层终止循环
    - tool_calls 增量 / usage / finish_reason：只记录（工具调用由后端消化，不给前端）
    返回要转发的前端字节行；None 表示吞掉。
    """
    if not line.startswith(b"data:"):
        return None
    data = line[5:].strip()
    if not data or data == b"[DONE]":
        return None
    try:
        obj = json.loads(data)
    except Exception:
        return None
    if not isinstance(obj, dict):
        return None

    # 上游流内错误：透传给前端并标记终止
    if isinstance(obj.get("error"), dict) and obj["error"].get("message"):
        st["upstream_error"] = obj["error"]
        return line + b"\n"

    # usage：轮内"最后一个非空 usage"生效（部分上游每个 chunk 都带累计 usage，逐块
    # 求和会重复计数），跨轮求和由外层在轮结束后进行；不透传，最后统一合成单个 chunk
    usage = obj.get("usage")
    if isinstance(usage, dict) and usage.get("prompt_tokens") is not None:
        st["round_usage"] = {
            "prompt": int(usage.get("prompt_tokens") or 0),
            "completion": int(usage.get("completion_tokens") or 0),
            "cached": int((usage.get("prompt_tokens_details") or {}).get("cached_tokens") or 0),
        }

    choices = obj.get("choices") or []
    if not choices or not isinstance(choices[0], dict):
        return None
    choice = choices[0]
    delta = choice.get("delta") or {}

    # 文本增量：累积（供对话记录）并转发
    has_text = False
    for key in ("reasoning_content", "reasoning", "thinking"):
        if isinstance(delta.get(key), str) and delta[key]:
            parts["reasoning"] += delta[key]
            has_text = True
    if isinstance(delta.get("content"), str) and delta["content"]:
        parts["output"] += delta["content"]
        has_text = True

    # 工具调用增量：按 index 拼接（流式下 id/name/arguments 都是分片到达）
    for tc in delta.get("tool_calls") or []:
        if not isinstance(tc, dict):
            continue
        acc = st["tool_calls"].setdefault(tc.get("index", 0), {"id": "", "name": "", "arguments": ""})
        if tc.get("id"):
            acc["id"] = tc["id"]
        fn = tc.get("function") or {}
        if fn.get("name"):
            acc["name"] += fn["name"]
        if fn.get("arguments"):
            acc["arguments"] += fn["arguments"]

    # 方舟的加密思维链（多轮工具调用时回传保持推理连续）
    if isinstance(delta.get("encrypted_content"), str):
        st["encrypted"] += delta["encrypted_content"]

    if choice.get("finish_reason"):
        st["finish_reason"] = choice["finish_reason"]

    if not has_text:
        return None
    return (_rewrite_sse_model(line, model_name) if needs_mapping else line) + b"\n"


def _extract_query(call: dict, fallback: str) -> str:
    """从工具调用参数里取搜索词；参数异常时回退到最后一条用户消息文本"""
    try:
        args = json.loads(call.get("arguments") or "{}")
        query = args.get("query") if isinstance(args, dict) else None
        if isinstance(query, str) and query.strip():
            return query.strip()
    except Exception:
        pass
    return fallback


def _last_user_text(messages) -> str:
    """取最后一条 user 消息的纯文本（搜索词兜底；多模态取 text 片段）"""
    for m in reversed(messages or []):
        if not isinstance(m, dict) or m.get("role") != "user":
            continue
        content = m.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()[:100]
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text" and str(part.get("text") or "").strip():
                    return str(part["text"]).strip()[:100]
    return ""


def _search_event(data: dict) -> bytes:
    """搜索起止状态事件（站内扩展字段，前端据此渲染联网搜索状态条）"""
    return b"data: " + json.dumps({"agenticapi_search": data}, ensure_ascii=False).encode() + b"\n"


def _error_event(message: str) -> bytes:
    return b"data: " + json.dumps(
        {"error": {"message": message, "type": "api_error"}}, ensure_ascii=False,
    ).encode() + b"\n"
