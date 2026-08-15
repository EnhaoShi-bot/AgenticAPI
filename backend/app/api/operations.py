"""上游运维接口"""

from fastapi import APIRouter, Body

from app.schemas.operations import MessageResponse, OperationsResponse
from app.services import operations_service

router = APIRouter(prefix="/operations")


@router.get("/get", response_model=OperationsResponse)
def get_operations(refresh_channel: str = "all"):
    """
    获取上游运维数据
    :param refresh_channel: 刷新的渠道，可选值为 "vol"、"bohr"、"stepfun" 或 "all"
    """
    return operations_service.get_operations(refresh_channel)


@router.post("/upload", response_model=MessageResponse)
def upload_settings(
    brmToken: str = Body(None),
    instanceId: str = Body(None),
    stepToken: str = Body(None),
    stepWebid: str = Body(None),
):
    """更新上游运维凭证"""
    return operations_service.upload_settings(brmToken, instanceId, stepToken, stepWebid)
