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


async def create_model(db: AsyncSession, new_model: ModelSchema) -> int:
    """添加单个模型，返回新增记录的自增主键 id

    业务错误（模型名重复、渠道不存在等）抛 HTTPException，由全局异常处理器统一格式化；
    数据库错误抛 SQLAlchemyError，同样由全局异常处理器捕获，
    回滚交由 get_db 依赖的 except 分支完成，这里无需 try/except。
    """
    model = new_model.model_dump()

    # 插入前检查 name 是否已存在，避免数据库抛唯一性异常导致 500
    if await model_crud.get_id_by_name(db, model["name"]):
        raise HTTPException(status_code=400, detail=f"模型 '{model['name']}' 已存在")

    # NOT NULL 列的入库默认值（crud 层用原生 SQL 插入，ORM 的 default 不会生效）
    if not model.get("label"):
        model["label"] = model["name"]
    model["model_group"] = model.get("model_group") or "free"
    for price in ("per_request_price", "input_price", "cache_price", "output_price"):
        if model.get(price) is None:
            model[price] = 0
    for flag in ("is_request_mode", "is_pin", "is_log", "support_vision"):
        if model.get(flag) is None:
            model[flag] = False
    if model.get("status") is None:
        model["status"] = True

    # channels：校验渠道是否都存在，再把数组序列化为 JSON 字符串存库
    if model.get("channels") is not None:
        await _validate_channels(db, model["channels"])
        model["channels"] = json.dumps(model["channels"], ensure_ascii=False)

    res_id = await model_crud.insert(db, model)
    await db.commit()

    if not res_id:
        raise HTTPException(status_code=500, detail="添加模型失败")
    return res_id


async def update_model(db: AsyncSession, model_name: str, update_data: ModelSchema) -> None:
    """更新单个模型数据（按 name 定位，name 本身不能更新）"""
    if not model_name or not model_name.strip():
        raise HTTPException(status_code=400, detail="模型名称不能为空")
    model_name = model_name.strip()

    if not await model_crud.get_id_by_name(db, model_name):
        raise HTTPException(status_code=404, detail=f"模型 '{model_name}' 不存在")

    # 过滤掉未传字段，同时排除 name 字段（定位键不可更新）
    update_dict = update_data.model_dump(exclude_unset=True, exclude={"name"})
    if not update_dict:
        raise HTTPException(status_code=400, detail="未提供任何需要更新的字段")

    # channels：校验渠道是否都存在，再把数组序列化为 JSON 字符串存库
    if "channels" in update_dict and update_dict["channels"] is not None:
        await _validate_channels(db, update_dict["channels"])
        update_dict["channels"] = json.dumps(update_dict["channels"], ensure_ascii=False)

    await model_crud.update_by_name(db, model_name, update_dict)
    await db.commit()


async def remove_model(db: AsyncSession, model_name: str) -> None:
    """删除模型"""
    if not model_name or not model_name.strip():
        raise HTTPException(status_code=400, detail="模型名称不能为空")
    model_name = model_name.strip()

    if not await model_crud.get_id_by_name(db, model_name):
        raise HTTPException(status_code=404, detail=f"模型名称 '{model_name}' 不存在")

    rowcount = await model_crud.delete_by_name(db, model_name)
    await db.commit()

    if rowcount == 0:
        raise HTTPException(status_code=500, detail="删除模型失败，未影响任何记录")
