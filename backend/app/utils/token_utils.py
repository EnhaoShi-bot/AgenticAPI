"""JWT / Token 解析工具"""

import base64
import json
from datetime import datetime


def decode_jwt_payload(token: str) -> dict:
    """解码 JWT 的 payload 部分（第二段），失败返回空 dict"""
    try:
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        return json.loads(base64.urlsafe_b64decode(payload_b64).decode())
    except Exception:
        return {}


def get_token_expiry(operation_dict: dict) -> dict:
    """
    获取4个渠道的token/凭证过期时间
    返回格式：{"volcengine": "...", "coding_plan": "...", "stepfun": "...", "zai": "..."}
    """
    expiry_dict = {}

    # 【1&2】火山方舟 / 深势科技（同一个JWT token）
    vol_token = operation_dict.get("bohrclaw_token", "")
    payload = decode_jwt_payload(vol_token)
    exp = payload.get("exp")
    if exp:
        exp_dt = datetime.fromtimestamp(exp).isoformat()
        expiry_dict["volcengine"] = exp_dt
        expiry_dict["coding_plan"] = exp_dt
    else:
        expiry_dict["volcengine"] = None
        expiry_dict["coding_plan"] = None

    # 【3】阶跃星辰（access_token...refresh_token 格式，返回 refresh_token 的过期时间）
    step_token = operation_dict.get("stepfun_token", "")
    try:
        refresh_token = step_token.split("...")[1]
        payload = decode_jwt_payload(refresh_token)
        exp = payload.get("exp")
        expiry_dict["stepfun"] = datetime.fromtimestamp(exp).isoformat() if exp else None
    except Exception:
        expiry_dict["stepfun"] = None

    # 【4】智谱（ZAI_ANTHORIZATION，JWT 但 payload 不含 exp，返回 None 表示长期有效）
    zai_payload = decode_jwt_payload(operation_dict.get("ZAI_ANTHORIZATION", ""))
    exp = zai_payload.get("exp")
    expiry_dict["zai"] = datetime.fromtimestamp(exp).isoformat() if exp else None

    return expiry_dict
