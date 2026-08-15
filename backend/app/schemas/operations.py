"""上游运维相关响应 Schema"""

from pydantic import BaseModel


class OperationsResponse(BaseModel):
    """上游 TokenPlan 用量监控响应结构"""

    status: dict = {}
    token_expiry: dict = {}
    vol_usage: dict = {}
    bohr_usage: dict = {}
    stepfun_usage: dict = {}


class MessageResponse(BaseModel):
    """通用消息响应"""

    message: str
