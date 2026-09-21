"""CommandCode（commandcode.ai）上游用量适配"""

import httpx

from app.services.upstream.base import http_error, network_error, ok, to_reset_at
from app.utils.json_utils import safe_get

USAGE_URL = "https://api.commandcode.ai/alpha/billing/credits"
# 月度总额度上游不返回，按当前 GOAT 套餐写死；更换套餐时需同步修改
CC_MONTHLY_TOTAL = 70


def fetch_commandcode_usage(operation_dict: dict) -> dict:
    """
    获取 CommandCode TokenPlan 用量（x-api-key 鉴权，Authorization: Bearer 会被上游拒绝）。
    响应含 credits（月度剩余余额）与 windowLimits（5小时/周两个滚动窗口）：
    - 窗口内 used/cap 为绝对值，resetAt 为毫秒时间戳（0 表示窗口未激活）
    - 月度只返回剩余余额 monthlyCredits，已用量按 CC_MONTHLY_TOTAL - 剩余 换算
    """
    headers = {"x-api-key": operation_dict.get("commandcode_api_key", "")}
    try:
        resp = httpx.get(USAGE_URL, headers=headers, timeout=5)  # 避免卡死
        if resp.status_code != 200:
            return http_error(resp.status_code, resp.text)

        try:
            data = resp.json()
        except ValueError:
            # HTTP 200 但响应体不是 JSON（空 body / 网关错误页），按上游异常返回，不拖垮整个接口
            return http_error(resp.status_code, f"non-JSON response: {resp.text[:200]!r}")
        # 成功响应不带 success 字段，鉴权失败等为 {"success": false, "error": {...}}
        if data.get("success") is False or "error" in data:
            err = data.get("error") or {}
            message = err.get("message") or err.get("msg") or "unknown error"
            return {"status": f"code:{err.get('code')}, msg:{str(message)[:200]}", "usage": {}, "raw": None}

        five_hour = safe_get(data, "windowLimits", "fiveHour", default={}) or {}
        weekly = safe_get(data, "windowLimits", "weekly", default={}) or {}
        credits = safe_get(data, "credits", default={}) or {}

        # 月度上游只给剩余余额，已用量 = 总额度 - 剩余；上游无月度重置时间字段
        remaining = credits.get("monthlyCredits")
        monthly_used = max(CC_MONTHLY_TOTAL - remaining, 0) if remaining is not None else 0

        usage = {
            "ccFiveHourUsed": five_hour.get("used") or 0,
            "ccFiveHourTotal": five_hour.get("cap") or 0,
            "ccFiveHourResetAt": to_reset_at(five_hour.get("resetAt")),
            "ccWeeklyUsed": weekly.get("used") or 0,
            "ccWeeklyTotal": weekly.get("cap") or 0,
            "ccWeeklyResetAt": to_reset_at(weekly.get("resetAt")),
            "ccMonthlyUsed": monthly_used,
            "ccMonthlyTotal": CC_MONTHLY_TOTAL,
            "ccMonthlyResetAt": None,
        }
        return ok(usage, data)
    except httpx.HTTPError as e:
        return network_error(e)
