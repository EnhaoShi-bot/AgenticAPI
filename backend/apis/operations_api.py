"""
上游运维接口
"""

from fastapi import APIRouter, Body
import json
import httpx
import base64
import time
import os

router = APIRouter(prefix="/operations")

OPS_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "operations_config.json")


def safe_get(data, *keys, default=None):
    """安全地获取嵌套字典中的值，支持任意层级的键访问，如果不存在，则返回default"""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
            if data is None:
                return default
        else:
            return default
    return data if data is not None else default


def refresh_stepfun_token(operation_dict: dict) -> str:
    """
    检查阶跃星辰 Access Token 是否过期，过期则调用刷新接口获取新 token，
    并将新 token 持久化到 operations_config.json 中。
    返回拼接好的完整 token 字符串（access_token...refresh_token）。
    """
    stepfun_token = operation_dict.get("stepfun_token", "")
    webid = operation_dict.get("stepfun_webid", "")

    if not stepfun_token:
        return stepfun_token

    parts = stepfun_token.split("...")
    if len(parts) != 2:
        return stepfun_token

    access_token = parts[0]
    refresh_token = parts[1]

    # 解码 Access Token 的 payload，检查是否过期
    need_refresh = False
    try:
        payload_b64 = access_token.split(".")[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())
        exp = payload.get("exp", 0)
        now = time.time()
        # 如果距离过期不足 5 分钟，提前刷新
        if exp - now < 300:
            need_refresh = True
    except Exception:
        need_refresh = True

    if not need_refresh:
        return stepfun_token

    # 调用刷新接口
    refresh_headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "oasis-appid": "10300",
        "oasis-platform": "web",
        "oasis-webid": webid,
        "Oasis-Token": stepfun_token,
    }
    refresh_url = "https://platform.stepfun.com/passport/proto.api.passport.v1.PassportService/RefreshToken"

    try:
        resp = httpx.post(refresh_url, headers=refresh_headers, data="{}", timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            new_access = result.get("accessToken", {}).get("raw", "")
            new_refresh = result.get("refreshToken", {}).get("raw", "")
            if new_access and new_refresh:
                new_token = new_access + "..." + new_refresh
                operation_dict["stepfun_token"] = new_token
                with open(OPS_JSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(operation_dict, f, ensure_ascii=False, indent=4)
                return new_token
    except Exception:
        pass

    # 刷新失败，返回旧 token 让调用方自行处理
    return stepfun_token


def get_token_expiry(operation_dict: dict) -> dict:
    """
    获取4个渠道的token/凭证过期时间
    返回格式：{"volcengine": "...", "coding_plan": "...", "stepfun": "...", "aliyun": "..."}
    """
    from datetime import datetime

    expiry_dict = {}

    # 【1&2】火山方舟 / 深势科技（同一个JWT token）
    vol_token = operation_dict.get("bohrclaw_token", "")
    try:
        payload_b64 = vol_token.split(".")[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())
        exp_dt = datetime.fromtimestamp(payload["exp"]).isoformat()
        expiry_dict["volcengine"] = exp_dt
        expiry_dict["coding_plan"] = exp_dt
    except Exception:
        expiry_dict["volcengine"] = None
        expiry_dict["coding_plan"] = None

    # 【3】阶跃星辰（access_token...refresh_token 格式，返回 refresh_token 的过期时间）
    step_token = operation_dict.get("stepfun_token", "")
    try:
        refresh_token = step_token.split("...")[1]
        payload_b64 = refresh_token.split(".")[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())
        expiry_dict["stepfun"] = datetime.fromtimestamp(payload["exp"]).isoformat()
    except Exception:
        expiry_dict["stepfun"] = None

    # 【4】阿里云（从Cookie的atpsida字段解析时间戳）
    ali_cookie = operation_dict.get("aliyun_cookie", "")
    try:
        for pair in ali_cookie.split("; "):
            if pair.startswith("atpsida="):
                timestamp = int(pair.split("=")[1].split("_")[1])
                expiry_dict["aliyun"] = datetime.fromtimestamp(timestamp).isoformat()
                break
        else:
            expiry_dict["aliyun"] = None
    except Exception:
        expiry_dict["aliyun"] = None

    return expiry_dict


@router.get("/get")
def get_operations(refresh_channel: str = "all"):
    """
    获取上游运维数据
    :param refresh_channel: 刷新的渠道，可选值为 "vol"、"bohr"、"stepfun"、"ali" 或 "all"
    :return: 包含刷新后的数据的字典
    :rtype: dict
    """

    # 返回的接口数据，先把结构定义好
    re_dict = {
        "status": {},
        "token_expiry": {},
        "vol_usage": {},
        "bohr_usage": {},
        "stepfun_usage": {},
        "ali_usage": {},
    }

    # 下面这个读取方式在执行完缩进后，会自动关闭文件
    with open(OPS_JSON_PATH, "r", encoding="utf-8") as f:
        operation_dict = json.load(f)

    # 【1】尝试获取火山方舟的Token Plan用量
    if refresh_channel == "vol" or refresh_channel == "all":

        # 请求配置
        instId = operation_dict.get("bohrclaw_instance")
        vol_headers = {'Authorization': 'Bearer ' + operation_dict.get("bohrclaw_token", "")}
        vol_usageUrl = f"https://bohrclaw.bohrium.com/api/bohrclaw/arkclaw-seat/usage?instance_id={instId}"

        try:
            vol_resp = httpx.get(vol_usageUrl, headers=vol_headers, timeout=5)  # 避免卡死

            # 解析响应状态码
            if vol_resp.status_code != 200:
                re_dict["status"]["vol"] = f"code:{vol_resp.status_code}, msg:{vol_resp.text[:200]}"
            else:
                re_dict["status"]["vol"] = "200"

                # 返回结果正常，可以开始解析
                vol_data = vol_resp.json()
                re_dict["vol_usage"] = {
                    "volFiveHourUsed": safe_get(vol_data, "usage", "afp_five_hour", "used"),
                    "volFiveHourTotal": safe_get(vol_data, "usage", "afp_five_hour", "quota"),
                    "volWeeklyUsed": safe_get(vol_data, "usage", "afp_weekly", "used"),
                    "volWeeklyTotal": safe_get(vol_data, "usage", "afp_weekly", "quota"),
                    "volMonthlyUsed": safe_get(vol_data, "usage", "afp", "used"),
                    "volMonthlyTotal": safe_get(vol_data, "usage", "afp", "quota"),
                }

                # 保存此次请求结果，以供调试
                with open("./backend/apis/response_data/vol_data.json", "w", encoding="utf-8") as f:
                    json.dump(vol_data, f, ensure_ascii=False, indent=4)

        # 请求出错了
        except httpx.HTTPError as e:
            re_dict["status"]["vol"] = f"network_exception:{str(e)}"

    # 【2】尝试获取深势科技Coding Plan用量，为了保险起见，此处重新请求一次
    if refresh_channel == "bohr" or refresh_channel == "all":

        # 请求配置
        instId = operation_dict.get("bohrclaw_instance")
        bohr_headers = {'Authorization': 'Bearer ' + operation_dict.get("bohrclaw_token", "")}
        bohr_usageUrl = f"https://bohrclaw.bohrium.com/api/bohrclaw/arkclaw-seat/usage?instance_id={instId}"

        # 发起请求
        try:
            bohr_resp = httpx.get(bohr_usageUrl, headers=bohr_headers, timeout=5)  # 避免卡死
            # 解析响应状态码
            if bohr_resp.status_code != 200:
                re_dict["status"]["bohr"] = f"code:{bohr_resp.status_code}, msg:{bohr_resp.text[:200]}"
            else:
                re_dict["status"]["bohr"] = "200"

                # 返回结果正常，可以开始解析
                bohr_data = bohr_resp.json()
                re_dict["bohr_usage"] = {
                    "bohrFiveHourUsed": safe_get(bohr_data, "coding_plan_quota", "llm", "5h", "used"),
                    "bohrFiveHourTotal": safe_get(bohr_data, "coding_plan_quota", "llm", "5h", "limit"),
                    "bohrWeeklyUsed": safe_get(bohr_data, "coding_plan_quota", "llm", "week", "used"),
                    "bohrWeeklyTotal": safe_get(bohr_data, "coding_plan_quota", "llm", "week", "limit"),
                    "bohrMonthlyUsed": safe_get(bohr_data, "coding_plan_quota", "llm", "month", "used"),
                    "bohrMonthlyTotal": safe_get(bohr_data, "coding_plan_quota", "llm", "month", "limit"),
                }
                # 保存此次请求结果，以供调试
                with open("./backend/apis/response_data/bohr_data.json", "w", encoding="utf-8") as f:
                    json.dump(bohr_data, f, ensure_ascii=False, indent=4)
        # 请求出错了
        except httpx.HTTPError as e:
            re_dict["status"]["bohr"] = f"network_exception:{str(e)}"

    # 【3】尝试获取阶跃星辰Step Plan用量
    if refresh_channel == "stepfun" or refresh_channel == "all":
        # 先检查并刷新 token，避免过期
        stepfun_token = refresh_stepfun_token(operation_dict)

        # 请求配置
        headers = {
            'accept': '*/*',
            'connect-protocol-version': '1',
            'content-type': 'application/json',
            'oasis-appid': '10300',
            'oasis-platform': 'web',
            'oasis-webid': operation_dict.get("stepfun_webid", ""),
            'Oasis-Token': stepfun_token,
        }
        step_url = 'https://platform.stepfun.com/api/step.openapi.devcenter.Dashboard/QueryStepPlanRateLimit'

        # 开始请求
        try:
            stepfun_resp = httpx.post(step_url, headers=headers, timeout=5)
            if stepfun_resp.status_code != 200:
                re_dict["status"]["stepfun"] = f"code:{stepfun_resp.status_code}, msg:{stepfun_resp.text[:200]}"
            else:
                re_dict["status"]["stepfun"] = "200"

                # 返回正确，可以开始解析了
                stepfun_data = stepfun_resp.json()  # 转换为字典
                credit_buckets = safe_get(stepfun_data, "plan_credit_rate_limit", "credit_buckets")
                re_dict["stepfun_usage"] = {
                    "stepfunFiveHourUsed": 0,
                    "stepfunFiveHourTotal": 0,
                    "stepfunWeeklyUsed": 0,
                    "stepfunWeeklyTotal": 0,
                    "stepfunMonthlyUsed": int(safe_get(credit_buckets[0], "credit_total")) - \
                                          int(safe_get(credit_buckets[0], "credit_residual")),
                    "stepfunMonthlyTotal": int(safe_get(credit_buckets[0], "credit_total")),
                }
                # 持久化保存一下此次的请求用量数据
                with open("./backend/apis/response_data/stepfun_data.json", "w", encoding="utf-8") as f:
                    json.dump(stepfun_data, f, ensure_ascii=False, indent=4)



        # 请求出错了
        except httpx.HTTPError as e:
            re_dict["status"]["stepfun"] = f"network_exception:{str(e)}"

    # 【4】尝试获取阿里云百炼的Token Plan用量
    if refresh_channel == "ali" or refresh_channel == "all":
        # 请求配置
        ali_cookie = operation_dict.get("aliyun_cookie", "")
        ali_url = "https://cs-data.qianwenai.com/data/api.json"
        ali_params = {
            "product": "sfm_bailian",
            "action": "BroadScopeAspnGateway",
            "interferences": "zeldaHttp.apikeyMgr./tokenplan/personal/interferences/v2/usage"
        }
        ali_headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/x-www-form-urlencoded",
            "cookie": ali_cookie,
            "referer": "https://platform.qianwenai.com/home/billing/subscription/token-plan-individual",
            "origin": "https://platform.qianwenai.com",
        }
        ali_form_data = {
            "product": "sfm_bailian",
            "action": "BroadScopeAspnGateway",
            "sec_token": "",
            "region": "cn-beijing",
            "params": json.dumps({
                "Api": "zeldaHttp.apikeyMgr./tokenplan/personal/interferences/v2/usage",
                "Data": {
                    "cornerstoneParam": {
                        "domain": "platform.qianwenai.com",
                        "consoleSite": "QIANWENAI",
                        "console": "ONE_CONSOLE",
                        "xsp_lang": "zh-CN",
                        "protocol": "V2",
                        "productCode": "p_efm"
                    }
                },
                "V": "1.0"
            }, ensure_ascii=False)
        }

        # 发送请求
        try:
            ali_resp = httpx.post(ali_url, params=ali_params, headers=ali_headers, data=ali_form_data)  # 这里返回的是一个对象
            if ali_resp.status_code != 200:
                re_dict["status"]["ali"] = f"code:{ali_resp.status_code}, msg:{ali_resp.text[:200]}"
            elif ali_resp.json().get("data", {}).get("success", {}) is False:
                re_dict["status"]["ali"] = "状态码200，但请求状态异常"
            else:
                re_dict["status"]["ali"] = "200"

                # 状态码正常，可以开始解析
                ali_data = ali_resp.json()  # 转换为字典
                # 解析用量数据：data.DataV2.data.data
                ali_inner = ali_data.get("data", {}).get("DataV2", {}).get("data", {}).get("data", {})
                # 周度数据：per1WeekPercentage 是已用比例（0-1范围）
                ali_week_pct = ali_inner.get("per1WeekPercentage", 0)
                # 目前API只返回周度数据，5小时和月度暂设为0
                re_dict["ali_usage"] = {
                    "aliFiveHourUsed": 0,
                    "aliFiveHourTotal": 0,
                    "aliWeeklyUsed": int(ali_week_pct * 700),
                    "aliWeeklyTotal": 700,
                    "aliMonthlyUsed": 0,
                    "aliMonthlyTotal": 0,
                }

                # 持久化保存一下此次的请求用量数据
                with open("./backend/apis/response_data/ali_data.json", "w", encoding="utf-8") as f:
                    json.dump(ali_data, f, ensure_ascii=False, indent=4)

        # 请求出错了
        except httpx.HTTPError as e:
            re_dict["status"]["ali"] = f"network_exception:{str(e)}"

    # 获取token过期时间
    re_dict["token_expiry"] = get_token_expiry(operation_dict)

    return re_dict


@router.post("/upload")
def upload_settings(
        brmToken: str = Body(None),
        instanceId: str = Body(None),
        stepToken: str = Body(None),
        stepWebid: str = Body(None),
        aliyunCookie: str = Body(None),
):
    # 加载文件
    try:
        with open(OPS_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}  # 文件不存在 → 装载空字典
        data['version'] = 1
        data['note'] = "TokenPlan 监控面板密钥存储文件。包含敏感登录态（Token/Cookie），请勿提交到 git/分享给他人。"

    # 长度大于5才可能是有效数据
    message = ''
    if len(brmToken) > 5:
        data["bohrclaw_token"] = brmToken
        message = message + "bohrclaw token已更新；"
    if len(instanceId) > 5:
        data["bohrclaw_instance"] = instanceId
        message = message + "bohr instance id已更新；"
    if len(stepToken) > 5:
        data["stepfun_token"] = stepToken
        message = message + "stepfun token已更新；"
    if len(stepWebid) > 5:
        data["stepfun_webid"] = stepWebid
        message = message + "stepfun webid已更新；"
    if len(aliyunCookie) > 5:
        data["aliyun_cookie"] = aliyunCookie
        message = message + "aliyun cookie已更新；"

    # 保存文件
    with open(OPS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return {"message": message}


__all__ = [router]
