"""深势科技（Coding Plan）上游用量适配"""

import httpx

from app.services.upstream.base import http_error, network_error, ok
from app.utils.json_utils import safe_get


def fetch_bohr_usage(operation_dict: dict) -> dict:
    """获取深势科技 Coding Plan 用量（与火山方舟同接口，解析字段不同）"""
    inst_id = operation_dict.get("bohrclaw_instance")
    headers = {"Authorization": "Bearer " + operation_dict.get("bohrclaw_token", "")}
    url = f"https://bohrclaw.bohrium.com/api/bohrclaw/arkclaw-seat/usage?instance_id={inst_id}"

    try:
        resp = httpx.get(url, headers=headers, timeout=5)  # 避免卡死
        if resp.status_code != 200:
            return http_error(resp.status_code, resp.text)

        data = resp.json()
        usage = {
            "bohrFiveHourUsed": safe_get(data, "coding_plan_quota", "llm", "5h", "used"),
            "bohrFiveHourTotal": safe_get(data, "coding_plan_quota", "llm", "5h", "limit"),
            "bohrWeeklyUsed": safe_get(data, "coding_plan_quota", "llm", "week", "used"),
            "bohrWeeklyTotal": safe_get(data, "coding_plan_quota", "llm", "week", "limit"),
            "bohrMonthlyUsed": safe_get(data, "coding_plan_quota", "llm", "month", "used"),
            "bohrMonthlyTotal": safe_get(data, "coding_plan_quota", "llm", "month", "limit"),
        }
        return ok(usage, data)
    except httpx.HTTPError as e:
        return network_error(e)
