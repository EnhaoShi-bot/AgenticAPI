"""上游运维业务编排"""

import json

from app.core.config import DATA_DIR
from app.services.upstream import bohr, stepfun, volcengine
from app.utils.token_utils import get_token_expiry

OPS_JSON_PATH = DATA_DIR / "operations_config.json"
RESPONSE_DATA_DIR = DATA_DIR / "response_data"


def _load_ops_config() -> dict:
    """读取运维凭证配置"""
    with open(OPS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_raw(name: str, data) -> None:
    """持久化保存此次请求结果，以供调试"""
    RESPONSE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESPONSE_DATA_DIR / f"{name}_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_operations(refresh_channel: str = "all") -> dict:
    """
    获取上游运维数据
    :param refresh_channel: 刷新的渠道，可选值为 "vol"、"bohr"、"stepfun"、"ali" 或 "all"
    """
    re_dict = {
        "status": {},
        "token_expiry": {},
        "vol_usage": {},
        "bohr_usage": {},
        "stepfun_usage": {},
    }

    operation_dict = _load_ops_config()

    # 【1】火山方舟 Token Plan 用量
    if refresh_channel in ("vol", "all"):
        result = volcengine.fetch_vol_usage(operation_dict)
        re_dict["status"]["vol"] = result["status"]
        re_dict["vol_usage"] = result["usage"]
        if result["raw"] is not None:
            _save_raw("vol", result["raw"])

    # 【2】深势科技 Coding Plan 用量
    if refresh_channel in ("bohr", "all"):
        result = bohr.fetch_bohr_usage(operation_dict)
        re_dict["status"]["bohr"] = result["status"]
        re_dict["bohr_usage"] = result["usage"]
        if result["raw"] is not None:
            _save_raw("bohr", result["raw"])

    # 【3】阶跃星辰 Step Plan 用量
    if refresh_channel in ("stepfun", "all"):
        result, current_token = stepfun.fetch_stepfun_usage(operation_dict, OPS_JSON_PATH)
        # 显式更新内存中的 token，确保后续 get_token_expiry 读到最新值
        operation_dict["stepfun_token"] = current_token
        re_dict["status"]["stepfun"] = result["status"]
        re_dict["stepfun_usage"] = result["usage"]
        if result["raw"] is not None:
            _save_raw("stepfun", result["raw"])

    # 获取 token 过期时间
    re_dict["token_expiry"] = get_token_expiry(operation_dict)
    return re_dict


def upload_settings(
    brm_token: str,
    instance_id: str,
    step_token: str,
    step_webid: str,
) -> dict:
    """更新上游运维凭证到 operations_config.json"""
    try:
        with open(OPS_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}  # 文件不存在 -> 装载空字典
        data["version"] = 1
        data["note"] = "TokenPlan 监控面板密钥存储文件。包含敏感登录态（Token/Cookie），请勿提交到 git/分享给他人。"

    # 长度大于5才可能是有效数据
    message = ""
    if len(brm_token) > 5:
        data["bohrclaw_token"] = brm_token
        message = message + "bohrclaw token已更新；"
    if len(instance_id) > 5:
        data["bohrclaw_instance"] = instance_id
        message = message + "bohr instance id已更新；"
    if len(step_token) > 5:
        data["stepfun_token"] = step_token
        message = message + "stepfun token已更新；"
    if len(step_webid) > 5:
        data["stepfun_webid"] = step_webid
        message = message + "stepfun webid已更新；"

    # 保存文件
    with open(OPS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return {"message": message}
