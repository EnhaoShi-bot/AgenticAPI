"""智谱（GLM Coding Plan）上游用量适配"""

import httpx

from app.services.upstream.base import http_error, network_error, ok
from app.utils.json_utils import safe_get

USAGE_URL = "https://open.bigmodel.cn/api/monitor/usage/quota/limit"

# unit 枚举：3 = 5小时窗口、6 = 7天窗口（无月度限额）
FIVE_HOUR_UNIT = 3
WEEKLY_UNIT = 6


def _window_used(item: dict) -> int:
    """已用量 = 限额总量 usage - 剩余量 remaining"""
    total = int(item.get("usage") or 0)
    remaining = int(item.get("remaining") or 0)
    return max(total - remaining, 0)


def fetch_zai_usage(operation_dict: dict) -> dict:
    """获取智谱 GLM Coding Plan 用量（5小时 + 7天两个 CREDIT_LIMIT 窗口，无月限额）"""
    # 智谱该接口的 Authorization 直接传 token 原文，不加 Bearer 前缀
    headers = {"Authorization": operation_dict.get("ZAI_ANTHORIZATION", "")}

    try:
        resp = httpx.get(USAGE_URL, headers=headers, timeout=5)  # 避免卡死
        if resp.status_code != 200:
            return http_error(resp.status_code, resp.text)

        data = resp.json()
        # HTTP 200 但业务码非 200（如 token 失效）同样视为失败
        if data.get("code") != 200:
            return {"status": f"code:{data.get('code')}, msg:{str(data.get('msg'))[:200]}", "usage": {}, "raw": None}

        limits = [x for x in safe_get(data, "data", "limits", default=[]) or [] if x.get("type") == "CREDIT_LIMIT"]
        # 按 unit 匹配时间窗，匹配不到时按返回顺序兜底（首个为 5 小时、次个为 7 天）
        five_hour = next((x for x in limits if x.get("unit") == FIVE_HOUR_UNIT), limits[0] if limits else {})
        weekly = next((x for x in limits if x.get("unit") == WEEKLY_UNIT), limits[1] if len(limits) > 1 else {})

        usage = {
            "zaiFiveHourUsed": _window_used(five_hour),
            "zaiFiveHourTotal": int(five_hour.get("usage") or 0),
            "zaiWeeklyUsed": _window_used(weekly),
            "zaiWeeklyTotal": int(weekly.get("usage") or 0),
            # 智谱无月度限额，额度为 0 时前端展示"无月度限额"
            "zaiMonthlyUsed": 0,
            "zaiMonthlyTotal": 0,
        }
        return ok(usage, data)
    except httpx.HTTPError as e:
        return network_error(e)
