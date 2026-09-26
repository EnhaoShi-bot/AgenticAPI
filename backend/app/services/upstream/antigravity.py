"""Antigravity（Google Gemini PRO）上游限额适配

数据源是同机回环的 Antigravity-Manager 容器管理 API（headless 模式，端口 8045）：
- GET {base}/api/accounts/current     → 当前账号（id/邮箱 + 容器缓存的配额）
- GET {base}/api/accounts/{id}/quota  → 实时限额（容器收到请求后经 VPN 向 Google 实时查询）
鉴权：Authorization: Bearer {ANTIGRAVITY_API_KEY}，即管理界面的访问令牌（WEB_PASSWORD）。

配额以模型组（quota_groups，来自 Google retrieveUserQuotaSummary）为单位返回，
每组含 5 小时与周度两个窗口桶，剩余量为 0~1 的 remaining_fraction；组内模型额度共享，
因此取 Gemini 组的两个窗口展示，已用量 = (1 - remaining_fraction) * 100。
实时拉取失败时回落到容器缓存数据（agSource=cache），避免 VPN 抖动把卡片直接打成错误。
"""

from typing import Any, Optional

import httpx

from app.services.upstream.base import http_error, network_error, ok, to_reset_at


def _pick_group(quota_groups: Any) -> Optional[dict]:
    """取 Gemini 模型组的分组配额（display_name 以 Gemini 开头），缺失时取第一组"""
    if not isinstance(quota_groups, list):
        return None
    groups = [g for g in quota_groups if isinstance(g, dict)]
    for g in groups:
        if str(g.get("display_name") or "").lower().startswith("gemini"):
            return g
    return groups[0] if groups else None


def _pick_bucket(group: dict, window: str) -> Optional[dict]:
    """从模型组里取指定窗口的配额桶（window: "5h" / "weekly"）"""
    buckets = group.get("buckets")
    if not isinstance(buckets, list):
        return None
    for b in buckets:
        if isinstance(b, dict) and b.get("window") == window:
            return b
    return None


def _reset_at(value: Any) -> Optional[str]:
    """上游 reset_time 是带 Z 后缀的 UTC ISO 串，先归一化再复用公共转换"""
    if isinstance(value, str) and value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return to_reset_at(value)


def _window_fields(bucket: Optional[dict]) -> dict:
    """配额桶 → 其他卡片同款的 Used/Total/ResetAt 三件套；桶缺失时 Total=0，
    前端据此显示「无对应窗口限额」"""
    if not bucket:
        return {"Used": 0, "Total": 0, "ResetAt": None}
    remaining = bucket.get("remaining_fraction")
    used = round(max(0.0, min(1.0, 1.0 - remaining)) * 100, 2) if isinstance(remaining, (int, float)) else 0
    return {"Used": used, "Total": 100, "ResetAt": _reset_at(bucket.get("reset_time"))}


def fetch_antigravity_usage(operation_dict: dict, live: bool = True) -> dict:
    """获取 Antigravity Gemini 组的 5 小时 / 周度限额

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
        quota = current.get("quota")
        if live:
            try:
                resp = httpx.get(
                    f"{base_url}/api/accounts/{account_id}/quota", headers=headers, timeout=25
                )
                if resp.status_code == 200:
                    try:
                        live_quota = resp.json()
                    except ValueError:
                        live_quota = None
                    if isinstance(live_quota, dict) and live_quota.get("quota_groups"):
                        quota = live_quota
                        source = "live"
            except httpx.HTTPError:
                pass  # 实时拉取失败 → 沿用缓存，不打断卡片

        group = _pick_group(quota.get("quota_groups") if isinstance(quota, dict) else None)
        if group is None:
            return {"status": "code:200, msg:容器未返回分组配额", "usage": {}, "raw": None}

        five = _window_fields(_pick_bucket(group, "5h"))
        weekly = _window_fields(_pick_bucket(group, "weekly"))

        usage = {
            "agEmail": current.get("email") or "",
            "agSource": source,
            "agFiveHourUsed": five["Used"],
            "agFiveHourTotal": five["Total"],
            "agFiveHourResetAt": five["ResetAt"],
            "agWeeklyUsed": weekly["Used"],
            "agWeeklyTotal": weekly["Total"],
            "agWeeklyResetAt": weekly["ResetAt"],
            "agMonthlyUsed": 0,
            "agMonthlyTotal": 0,  # 上游无月度窗口，前端显示「无月度限额」
            "agMonthlyResetAt": None,
        }
        # raw 只保留 id/邮箱/配额做调试快照，避免把账号敏感字段落盘
        raw = {k: current.get(k) for k in ("id", "email", "quota") if k in current}
        return ok(usage, raw)
    except httpx.HTTPError as e:
        return network_error(e)
