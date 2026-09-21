"""上游运维业务编排"""

import json

from app.core.config import DATA_DIR, commandcode_ops_setting, zai_ops_setting
from app.services.upstream import commandcode, stepfun, volcengine, zai
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
    :param refresh_channel: 刷新的渠道，可选值为 "vol"、"stepfun"、"zai"、"zai2" 或 "all"
    """
    re_dict = {
        "status": {},
        "token_expiry": {},
        "vol_usage": {},
        "stepfun_usage": {},
        "zai_usage": {},
        "zai2_usage": {},
        "cc_usage": {},
    }

    operation_dict = _load_ops_config()

    # 智谱改用 .env 里的 Coding Plan API key（长期有效），不再走 JSON 里的浏览器 JWT
    operation_dict["ZAI_API_KEY"] = zai_ops_setting.ZAI_API_KEY
    operation_dict["ZAI_API_KEY_2"] = zai_ops_setting.ZAI_API_KEY_2

    # CommandCode 的 API key 同样在 .env（长期有效）
    operation_dict["commandcode_api_key"] = commandcode_ops_setting.COMMANDCODE_API_KEY

    # 【1】火山方舟 Token Plan 用量
    if refresh_channel in ("vol", "all"):
        result = volcengine.fetch_vol_usage(operation_dict)
        re_dict["status"]["vol"] = result["status"]
        re_dict["vol_usage"] = result["usage"]
        if result["raw"] is not None:
            _save_raw("vol", result["raw"])

    # 【2】阶跃星辰 Step Plan 用量
    if refresh_channel in ("stepfun", "all"):
        result, current_token = stepfun.fetch_stepfun_usage(operation_dict, OPS_JSON_PATH)
        # 显式更新内存中的 token，确保后续 get_token_expiry 读到最新值
        operation_dict["stepfun_token"] = current_token
        re_dict["status"]["stepfun"] = result["status"]
        re_dict["stepfun_usage"] = result["usage"]
        if result["raw"] is not None:
            _save_raw("stepfun", result["raw"])

    # 【3】智谱 GLM Coding Plan 用量（账号一 · v3，凭证为 .env 的 ZAI_API_KEY）
    if refresh_channel in ("zai", "all"):
        result = zai.fetch_zai_usage(operation_dict, token_key="ZAI_API_KEY")
        re_dict["status"]["zai"] = result["status"]
        re_dict["zai_usage"] = result["usage"]
        if result["raw"] is not None:
            _save_raw("zai", result["raw"])

    # 【4】智谱 GLM Coding Plan 用量（账号二 · v2，凭证为 .env 的 ZAI_API_KEY_2）
    if refresh_channel in ("zai2", "all"):
        result = zai.fetch_zai_usage(operation_dict, token_key="ZAI_API_KEY_2")
        re_dict["status"]["zai2"] = result["status"]
        re_dict["zai2_usage"] = result["usage"]
        if result["raw"] is not None:
            _save_raw("zai2", result["raw"])

    # 【5】CommandCode TokenPlan 用量（凭证为 .env 的 COMMANDCODE_API_KEY）
    if refresh_channel in ("cc", "all"):
        result = commandcode.fetch_commandcode_usage(operation_dict)
        re_dict["status"]["cc"] = result["status"]
        re_dict["cc_usage"] = result["usage"]
        if result["raw"] is not None:
            _save_raw("cc", result["raw"])

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
