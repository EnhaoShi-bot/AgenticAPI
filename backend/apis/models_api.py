"""
数据库模型接口
"""

import json
from decimal import Decimal
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from sqlalchemy import text
from db.session import get_db

router = APIRouter(prefix="/models")


# 定义模型更新数据字段定义，其中id字段不能更新，由数据库自动生成，其他字段都可选传
class ModelSchema(BaseModel):
    model_config = {"populate_by_name": True}

    # 基础信息
    name: str | None = Field(default=None, alias="name")
    label: str | None = Field(default=None, alias="label")
    description: str | None = Field(default=None, alias="description")
    model_group: str | None = Field(default=None, alias="modelGroup")

    # 定价信息
    is_request_mode: bool | None = Field(default=None, alias="isRequestMode")
    per_request_price: Decimal | None = Field(default=None, alias="perRequestPrice")
    input_price: Decimal | None = Field(default=None, alias="inputPrice")
    cache_price: Decimal | None = Field(default=None, alias="cachePrice")
    output_price: Decimal | None = Field(default=None, alias="outputPrice")

    # 模型配置
    is_pin: bool | None = Field(default=None, alias="isPin")
    is_log: bool | None = Field(default=None, alias="isLog")
    status: bool | None = Field(default=None, alias="status")
    channels: list[str] | None = Field(default=None, alias="channels")
    context_length: int | None = Field(default=None, alias="contextLength")
    max_tokens: int | None = Field(default=None, alias="maxTokens")
    support_vision: bool | None = Field(default=None, alias="supportVision")
    icon: str = Field(default="", alias="icon")


def _parse_json_list(raw) -> list:
    """把数据库里的 JSON 字符串解析为 list；空串/NULL/异常统一返回 []"""
    if not raw or not isinstance(raw, str) or not raw.strip():
        return []
    try:
        v = json.loads(raw)
        return v if isinstance(v, list) else []
    except Exception:
        return []


async def _validate_channels(db: AsyncSession, names: list[str]) -> None:
    """校验 channels 中的每个渠道名都存在于 llm_channels 表"""
    if not names:
        return
    placeholders = ",".join([f":c{i}" for i in range(len(names))])
    results = await db.execute(
        text(f"SELECT channel_name FROM llm_channels WHERE channel_name IN ({placeholders})"),
        {f"c{i}": n for i, n in enumerate(names)},
    )
    rows = results.mappings().all()
    valid = {r["channel_name"] for r in rows}
    invalid = [n for n in names if n not in valid]
    if invalid:
        raise HTTPException(status_code=400, detail=f"以下渠道不存在: {invalid}")


@router.get("/get")
async def get_models(
        db: AsyncSession = Depends(get_db)
):
    """
    获取全量模型列表
    :param db: 数据库会话
    """
    results = await db.execute(text("SELECT * FROM llm_models"))
    models = results.mappings().all()

    result = []
    for model in models:
        d = dict(model)
        # channels 在库里是 JSON 字符串，返回前端时解析为真正的数组
        d["channels"] = _parse_json_list(d.get("channels"))
        result.append(ModelSchema(**d).model_dump(by_alias=True, mode="json"))
    return result


@router.post("/post")
async def add_model(
        new_model: ModelSchema,
        db: AsyncSession = Depends(get_db)
):
    """
    添加单个模型
    :param new_model: 模型数据
    :return: 模型ID
    """
    model = new_model.model_dump()  # 转换为字典

    # 插入前检查 name 是否已存在，避免数据库抛唯一性异常导致 500
    results = await db.execute(
        text("SELECT id FROM llm_models WHERE name = :name LIMIT 1"),
        {"name": model["name"]}
    )
    existing = results.first()
    if existing is not None:
        raise HTTPException(status_code=400, detail=f"模型 '{model['name']}' 已存在")

    # channels：校验渠道是否都存在，再把数组序列化为 JSON 字符串存库
    if model.get("channels") is not None:
        await _validate_channels(db, model["channels"])
        model["channels"] = json.dumps(model["channels"], ensure_ascii=False)

    try:
        results = await db.execute(
            text(
                """
                INSERT INTO llm_models
                (name, label, description, is_request_mode, per_request_price,
                 input_price, cache_price, output_price, model_group, is_pin,
                 is_log, status, channels, context_length, max_tokens, support_vision,
                 icon)
                VALUES (:name, :label, :description, :is_request_mode, :per_request_price,
                        :input_price, :cache_price, :output_price, :model_group, :is_pin,
                        :is_log, :status, :channels, :context_length, :max_tokens, :support_vision,
                        :icon)
                """
            ),
            {**model}  # 这里一次性插入所有字段，避免重复代码
        )
        await db.flush()
        res_id = results.lastrowid
        await db.commit()
    except Exception as e:
        # 异常时回滚事务，防止脏数据/锁表，并返回具体错误信息
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"添加模型失败: {str(e)}")

    if res_id:
        return f"添加模型成功，模型ID：{res_id}"
    else:
        raise HTTPException(status_code=500, detail="添加模型失败")


@router.put("/put")
async def put_model(
        update_data: ModelSchema,
        db: AsyncSession = Depends(get_db)
):
    """
    更新单个模型数据
    :param update_data: 需要更新的字段（Body 传参，全部选传，其中，模型名称 name 不能更新）
    :param db: 数据库会话
    :return: 更新结果提示
    """
    # 1. 检查模型是否存在
    model_name = update_data.model_dump()["name"]
    result = await db.execute(
        text("SELECT id FROM llm_models WHERE name = :name LIMIT 1"),
        {"name": model_name}
    )
    existing = result.mappings().first()
    if existing is None:
        raise HTTPException(
            status_code=404,
            detail=f"模型 '{model_name}' 不存在"
        )

    # 2. 过滤掉 None 值，只更新有传值的字段，同时需要排除 name 字段，因为 name 不能更新
    update_dict = update_data.model_dump(exclude_unset=True, exclude={"name"})

    if not update_dict:
        raise HTTPException(
            status_code=400,
            detail="未提供任何需要更新的字段"
        )

    # channels：校验渠道是否都存在，再把数组序列化为 JSON 字符串存库
    if "channels" in update_dict and update_dict["channels"] is not None:
        await _validate_channels(db, update_dict["channels"])
        update_dict["channels"] = json.dumps(update_dict["channels"], ensure_ascii=False)

    # 3. 动态构建 SET 子句
    set_clauses = [f"{key} = :{key}" for key in update_dict.keys()]

    sql = text(f"""
        UPDATE llm_models
        SET {', '.join(set_clauses)}
        WHERE name = :model_name
    """)

    # 4. 执行更新，异常时回滚
    try:

        await db.execute(sql, {**update_dict, "model_name": model_name})
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"更新模型失败: {str(e)}"
        )

    # 5. 返回成功提示
    return f"模型 '{model_name}' 更新成功"


@router.delete("/delete")
async def delete_model(
        model_name: str,
        db: AsyncSession = Depends(get_db)
):
    """
    删除模型
    :param model_name: 模型名称（必传）
    :param db: 数据库会话
    :return: 删除结果提示
    """
    # 1. 参数校验：模型名称不能为空
    if not model_name or not model_name.strip():
        raise HTTPException(
            status_code=400,
            detail="模型名称不能为空"
        )

    model_name = model_name.strip()

    # 2. 检查模型是否存在
    result = await db.execute(
        text("SELECT id FROM llm_models WHERE name = :name LIMIT 1"),
        {"name": model_name}
    )
    existing = result.mappings().first()
    if existing is None:
        raise HTTPException(
            status_code=404,
            detail=f"模型名称 '{model_name}' 不存在"
        )

    # 3. 执行删除，异常时回滚
    try:
        result = await db.execute(
            text("DELETE FROM llm_models WHERE name = :name"),
            {"name": model_name}
        )
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"删除模型失败: {str(e)}"
        )

    # 4. 确认删除生效（rowcount 为 0 时说明异常）
    if result.rowcount == 0:
        raise HTTPException(
            status_code=500,
            detail="删除模型失败，未影响任何记录"
        )

    return f"模型 '{model_name}' 删除成功"


__all__ = [router]