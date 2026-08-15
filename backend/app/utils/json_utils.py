"""JSON / 字典解析工具"""

import json


def parse_json_list(raw) -> list:
    """把数据库里的 JSON 字符串解析为 list；空串/NULL/异常统一返回 []"""
    if not raw or not isinstance(raw, str) or not raw.strip():
        return []
    try:
        v = json.loads(raw)
        return v if isinstance(v, list) else []
    except Exception:
        return []


def safe_get(data, *keys, default=None):
    """安全地获取嵌套字典中的值，支持任意层级的键访问，如果不存在，则返回 default"""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
            if data is None:
                return default
        else:
            return default
    return data if data is not None else default
