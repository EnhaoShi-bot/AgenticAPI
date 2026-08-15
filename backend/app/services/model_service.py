"""模型业务逻辑层"""

import json

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import channel as channel_crud
from app.crud import model as model_crud
from app.schemas.model import ModelSchema
from app.utils.json_utils import parse_json_list


async def _validate_channels(db: AsyncSession, names: list[str]) -> None:
    """校验 channels 中的每个渠道名都存在于 llm_channels 表"""
    if not names:
        return
    valid = await channel_crud.get_existing_names(db, names)
    invalid = [n for n in names if n not in valid]
    if invalid:
        raise HTTPException(status_code=400, detail=f"以下渠道不存在: {invalid}")


async def list_models(db: AsyncSession) -> list[dict]:
    """获取全量模型列表，channels 解析为真正的数组返回前端"""
    models = await model_crud.get_all(db)
    result = []
    for model in models:
        d = dict(model)
        d["channels"] = parse_json_list(d.get("channels"))
        result.append(ModelSchema(**d).model_dump(by_alias=True, mode="json"))
    return result


async def create_model(db: AsyncSession, new_model: ModelSchema) -> str:
    """添加单个模型"""
    model = new_model.model_dump()

    # 插入前检查 name 是否已存在，避免数据库抛唯一性异常导致 500
    if await model_crud.get_id_by_name(db, model["name"]):
        raise HTTPException(status_code=400, detail=f"模型 '{model['name']}' 已存在")

    # channels：校验渠道是否都存在，再把数组序列化为 JSON 字符串存库
    if model.get("channels") is not None:
        await _validate_channels(db, model["channels"])
        model["channels"] = json.dumps(model["channels"], ensure_ascii=False)

    try:
        res_id = await model_crud.insert(db, model)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"添加模型失败: {str(e)}")

    if res_id:
        return f"添加模型成功，模型ID：{res_id}"
    raise HTTPException(status_code=500, detail="添加模型失败")


async def update_model(db: AsyncSession, update_data: ModelSchema) -> str:
    """更新单个模型数据（name 不能更新）"""
    model_name = update_data.model_dump()["name"]
    if not await model_crud.get_id_by_name(db, model_name):
        raise HTTPException(status_code=404, detail=f"模型 '{model_name}' 不存在")

    # 过滤掉 None 值，只更新有传值的字段，同时排除 name 字段
    update_dict = update_data.model_dump(exclude_unset=True, exclude={"name"})
    if not update_dict:
        raise HTTPException(status_code=400, detail="未提供任何需要更新的字段")

    # channels：校验渠道是否都存在，再把数组序列化为 JSON 字符串存库
    if "channels" in update_dict and update_dict["channels"] is not None:
        await _validate_channels(db, update_dict["channels"])
        update_dict["channels"] = json.dumps(update_dict["channels"], ensure_ascii=False)

    try:
        await model_crud.update_by_name(db, model_name, update_dict)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新模型失败: {str(e)}")

    return f"模型 '{model_name}' 更新成功"


async def remove_model(db: AsyncSession, model_name: str) -> str:
    """删除模型"""
    if not model_name or not model_name.strip():
        raise HTTPException(status_code=400, detail="模型名称不能为空")
    model_name = model_name.strip()

    if not await model_crud.get_id_by_name(db, model_name):
        raise HTTPException(status_code=404, detail=f"模型名称 '{model_name}' 不存在")

    try:
        rowcount = await model_crud.delete_by_name(db, model_name)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除模型失败: {str(e)}")

    if rowcount == 0:
        raise HTTPException(status_code=500, detail="删除模型失败，未影响任何记录")

    return f"模型 '{model_name}' 删除成功"
