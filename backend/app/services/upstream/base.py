"""上游供应商适配公共工具

各 fetch_xxx_usage 函数统一返回如下结构：
    {"status": str, "usage": dict, "raw": Any}
- status: "200" / "code:xxx, msg:..." / "network_exception:..." / 其他业务状态
- usage:  用量字段字典，失败时为 {}
- raw:    原始响应，供调试持久化，失败时为 None
"""

from typing import Any

import httpx


def ok(usage: dict, raw: Any = None) -> dict:
    """构造成功结果"""
    return {"status": "200", "usage": usage, "raw": raw}


def http_error(status_code: int, text: str) -> dict:
    """构造 HTTP 错误结果"""
    return {"status": f"code:{status_code}, msg:{text[:200]}", "usage": {}, "raw": None}


def network_error(e: httpx.HTTPError) -> dict:
    """构造网络异常结果"""
    return {"status": f"network_exception:{str(e)}", "usage": {}, "raw": None}
