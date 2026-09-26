"""Antigravity（Google Gemini PRO）上游限额适配

数据源是同机回环的 Antigravity-Manager 容器管理 API（headless 模式，端口 8045）：
- GET {base}/api/accounts/current     → 当前账号（id/邮箱 + 容器缓存的各模型配额）
- GET {base}/api/accounts/{id}/quota  → 实时限额（容器收到请求后经 VPN 向 Google 实时查询）
鉴权：Authorization: Bearer {ANTIGRAVITY_API_KEY}，即管理界面的访问令牌（WEB_PASSWORD）。

上游按模型返回「剩余百分比 + 5 小时窗口重置时间」，但文本模型的额度基本共享，
因此只监控主力模型 MONITORED_MODEL，缺失时回落 recommended / 剩余最低的模型。
实时拉取失败时回落到容器缓存数据（agSource=cache），避免 VPN 抖动把卡片直接打成错误。
"""

from typing import Any, List, Optional

import httpx

from app.services.upstream.base import http_error, network_error, ok, to_reset_at

# 监控的主力文本模型（文本模型额度共享，盯一个即代表整体水位）
MONITORED_MODEL = "gemini-3.8-flash"


def _extract_models(quota: Any) -> List[dict]:
    """从配额结构里取 models 数组，容忍缺失/结构变化"""
    if not isinstance(quota, dict):
        return []
    models = quota.get("models")
    if not isinstance(models, list):
        return []
    return [m for m in models if isinstance(m, dict)]


def _pick_model(models: List[dict]) -> Optional[dict]:
    """挑选监控的模型：优先主力模型，缺失时回落 recommended，最后取剩余最低的"""
    for m in models:
        if (m.get("name") or "") == MONITORED_MODEL:
            return m
    pool = [m for m in models if m.get("recommended")] or models
    return min(pool, key=lambda m: m.get("percentage") or 0)


def _reset_at(value: Any) -> Optional[str]:
    """上游 reset_time 是带 Z 后缀的 UTC ISO 串，先归一化再复用公共转换"""
    if isinstance(value, str) and value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return to_reset_at(value)


def fetch_antigravity_usage(operation_dict: dict, live: bool = True) -> dict:
    """获取 Antigravity 当前账号的各模型限额

    :param live: True 时先实时拉取（容器经 VPN 向 Google 现查，实测约 15s，超时 25s 给
        前端 30s 的 axios 预算留余量），失败回落缓存；False 直接读容器缓存秒回。
    """
    base_url = (operation_dict.get("antigravity_base_url") or "http://127.0.0.1:8045").rstrip("/")
    api_key = operation_dict.get("antigravity_api_key", "")
    if not api_key:
        return {"status": "config:ANTIGRAVITY_API_KEY 未配置（backend/.env）", "usage": {}, "raw": None}

    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        # 1) 当前账号：拿 id/邮箱，同时缓存配额作为实时拉取失败时的回落
        resp = httpx.get(f"{base_url}/api/accounts/current", headers=headers, timeout=5)
        if resp.status_code != 200:
            return http_error(resp.status_code, resp.text)
        try:
            current = resp.json()
        except ValueError:
            return http_error(resp.status_code, f"non-JSON response: {resp.text[:200]!r}")

        account_id = current.get("id")
        if not account_id:
            return {"status": "code:200, msg:容器内没有可用账号", "usage": {}, "raw": None}

        # 2) 实时限额（live=False 跳过，直接用缓存）
        source = "cache"
        models = _extract_models(current.get("quota"))
        if live:
            try:
                resp = httpx.get(
                    f"{base_url}/api/accounts/{account_id}/quota", headers=headers, timeout=25
                )
                if resp.status_code == 200:
                    try:
                        live_models = _extract_models(resp.json())
                    except ValueError:
                        live_models = []
                    if live_models:
                        models = live_models
                        source = "live"
            except httpx.HTTPError:
                pass  # 实时拉取失败 → 沿用缓存，不打断卡片

        if not models:
            return {"status": "code:200, msg:容器未返回配额数据", "usage": {}, "raw": None}

        model = _pick_model(models)
        if model is None:
            return {"status": "code:200, msg:容器未返回模型配额", "usage": {}, "raw": None}

        usage = {
            "agEmail": current.get("email") or "",
            "agSource": source,
            "agModel": model.get("name") or "unknown",
            "agUsed": max(0, 100 - int(model.get("percentage") or 0)),
            "agResetAt": _reset_at(model.get("reset_time")),
        }
        # raw 只保留 id/邮箱/配额做调试快照，避免把账号敏感字段落盘
        raw = {k: current.get(k) for k in ("id", "email", "quota") if k in current}
        return ok(usage, raw)
    except httpx.HTTPError as e:
        return network_error(e)
