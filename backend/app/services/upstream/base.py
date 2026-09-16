"""上游供应商适配公共工具

各 fetch_xxx_usage 函数统一返回如下结构：
    {"status": str, "usage": dict, "raw": Any}
- status: "200" / "code:xxx, msg:..." / "network_exception:..." / 其他业务状态
- usage:  用量字段字典，失败时为 {}
- raw:    原始响应，供调试持久化，失败时为 None
"""

from datetime import datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

import httpx

TZ = ZoneInfo("Asia/Shanghai")


def to_reset_at(value: Any) -> Optional[str]:
    """把上游的重置时间字段（毫秒/秒时间戳或 ISO 字符串）统一为本地时间字符串

    阶跃不返回时间字段、火山的 5 小时窗未激活（-1 / 缺失）时返回 None，前端据此隐藏展示，
    窗口激活后字段出现即自动展示。
    """
    if value is None:
        return None
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
        except ValueError:
            return None
    elif isinstance(value, (int, float)):
        if value <= 0:
            return None
        dt = datetime.fromtimestamp(value / 1000 if value > 1e12 else value, TZ)
    else:
        return None
    return dt.astimezone(TZ).strftime("%Y-%m-%d %H:%M")


def ok(usage: dict, raw: Any = None) -> dict:
    """构造成功结果"""
    return {"status": "200", "usage": usage, "raw": raw}


def http_error(status_code: int, text: str) -> dict:
    """构造 HTTP 错误结果"""
    return {"status": f"code:{status_code}, msg:{text[:200]}", "usage": {}, "raw": None}


def network_error(e: httpx.HTTPError) -> dict:
    """构造网络异常结果"""
    return {"status": f"network_exception:{str(e)}", "usage": {}, "raw": None}
