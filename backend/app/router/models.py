"""模型相关接口"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.model import ModelSchema
from app.services import model_service

router = APIRouter(prefix="/models",tags=["Models"])


@router.get("/get")
async def get_models(db: AsyncSession = Depends(get_db)):
    """获取全量模型列表"""
    return await model_service.list_models(db)


@router.post("/post")
async def add_model(new_model: ModelSchema, db: AsyncSession = Depends(get_db)):
    """添加单个模型"""
    return await model_service.create_model(db, new_model)


@router.put("/put")
async def put_model(update_data: ModelSchema, db: AsyncSession = Depends(get_db)):
    """更新单个模型数据（name 不能更新）"""
    return await model_service.update_model(db, update_data)


@router.delete("/delete")
async def delete_model(model_name: str, db: AsyncSession = Depends(get_db)):
    """删除模型"""
    return await model_service.remove_model(db, model_name)
