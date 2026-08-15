"""火山方舟（BohrClaw）上游用量适配"""

import httpx

from app.services.upstream.base import http_error, network_error, ok
from app.utils.json_utils import safe_get


def fetch_vol_usage(operation_dict: dict) -> dict:
    """获取火山方舟 Token Plan 用量"""
    inst_id = operation_dict.get("bohrclaw_instance")
    headers = {"Authorization": "Bearer " + operation_dict.get("bohrclaw_token", "")}
    url = f"https://bohrclaw.bohrium.com/api/bohrclaw/arkclaw-seat/usage?instance_id={inst_id}"

    try:
        resp = httpx.get(url, headers=headers, timeout=5)  # 避免卡死
        if resp.status_code != 200:
            return http_error(resp.status_code, resp.text)

        data = resp.json()
        usage = {
            "volFiveHourUsed": safe_get(data, "usage", "afp_five_hour", "used"),
            "volFiveHourTotal": safe_get(data, "usage", "afp_five_hour", "quota"),
            "volWeeklyUsed": safe_get(data, "usage", "afp_weekly", "used"),
            "volWeeklyTotal": safe_get(data, "usage", "afp_weekly", "quota"),
            "volMonthlyUsed": safe_get(data, "usage", "afp", "used"),
            "volMonthlyTotal": safe_get(data, "usage", "afp", "quota"),
        }
        return ok(usage, data)
    except httpx.HTTPError as e:
        return network_error(e)
