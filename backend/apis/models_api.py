"""
数据库模型接口
"""

from decimal import Decimal
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from sqlalchemy import text
from db.session import get_db

router = APIRouter(prefix="/models")


# 定义模型数据模型，公开，可不做鉴权校验
class ModelSchema(BaseModel):
    model_config = {"populate_by_name": True}

    id: int
    name: str
    label: str
    model_group: str | None = Field(default=None, alias="modelGroup")
    is_request_mode: bool = Field(default=False, alias="isRequestMode")
    per_request_price: Decimal = Field(default=Decimal("0"), alias="perRequestPrice")
    input_price: Decimal = Field(default=Decimal("0"), alias="inputPrice")
    cache_price: Decimal = Field(default=Decimal("0"), alias="cachePrice")
    output_price: Decimal = Field(default=Decimal("0"), alias="outputPrice")
    is_pin: bool = Field(default=False, alias="isPin")
    is_log: bool = Field(default=False, alias="isLog")
    context_length: int | None = Field(default=None, alias="contextLength")
    max_tokens: int | None = Field(default=None, alias="maxTokens")
    support_vision: bool = Field(default=False, alias="supportVision")
    status: bool = True


# 定义模型更新数据模型，其中id, name 字段不能更新，其他字段都可选，不是必传
class ModelUpdateSchema(BaseModel):
    model_config = {"populate_by_name": True}

    label: str | None = None
    model_group: str | None = Field(default=None, alias="modelGroup")
    is_request_mode: bool | None = Field(default=None, alias="isRequestMode")
    per_request_price: Decimal | None = Field(default=None, alias="perRequestPrice")
    input_price: Decimal | None = Field(default=None, alias="inputPrice")
    cache_price: Decimal | None = Field(default=None, alias="cachePrice")
    output_price: Decimal | None = Field(default=None, alias="outputPrice")
    is_pin: bool | None = Field(default=None, alias="isPin")
    is_log: bool | None = Field(default=None, alias="isLog")
    context_length: int | None = Field(default=None, alias="contextLength")
    max_tokens: int | None = Field(default=None, alias="maxTokens")
    support_vision: bool | None = Field(default=None, alias="supportVision")
    status: bool | None = None
    channels: str | None = None


# 定义分页响应数据模型
class PageResult(BaseModel):
    list: list
    modelNumber: int
    pageNum: int
    pageSize: int
    pages: int


# 定义获取模型总括情况的数据类型

@router.get("/get")
def get_models(
        db: Session = Depends(get_db)
):
    """
    获取全量模型列表
    :param db: 数据库会话
    """
    models = db.execute(
        text("SELECT * FROM llm_models")
    ).mappings().all()

    return [ModelSchema(**dict(model)).model_dump(by_alias=True, mode="json") for model in models]


@router.post("/post")
def add_model(
        new_model: ModelSchema,
        db: Session = Depends(get_db)
):
    """
    添加单个模型
    :param new_model: 模型数据
    :return: 模型ID
    """
    model = new_model.model_dump()  # 转换为字典

    # 插入前检查 name 是否已存在，避免数据库抛唯一性异常导致 500
    existing = db.execute(
        text("SELECT id FROM llm_models WHERE name = :name LIMIT 1"),
        {"name": model["name"]}
    ).mappings().first()
    if existing:
        raise HTTPException(status_code=400, detail=f"模型名称 '{model['name']}' 已存在")

    try:
        result = db.execute(
            text(
                """
                INSERT INTO llm_models
                (name, label, description, is_request_mode, per_request_price,
                 input_price, cache_price, output_price, model_group, is_pin,
                 is_log, status, channels, context_length, max_tokens, support_vision)
                VALUES (:name, :label, :description, :is_request_mode, :per_request_price,
                        :input_price, :cache_price, :output_price, :model_group, :is_pin,
                        :is_log, :status, :channels, :context_length, :max_tokens, :support_vision)
                """
            ),
            {**model}  # 这里一次性插入所有字段，避免重复代码
        )
        db.flush()
        res_id = result.lastrowid
        db.commit()
    except Exception as e:
        # 异常时回滚事务，防止脏数据/锁表，并返回具体错误信息
        db.rollback()
        raise HTTPException(status_code=500, detail=f"添加模型失败: {str(e)}")

    if res_id:
        return f"添加模型成功，模型ID：{res_id}"
    else:
        raise HTTPException(status_code=500, detail="添加模型失败")


@router.put("/put")
def put_model(
        model_name: str,
        update_data: ModelUpdateSchema,
        db: Session = Depends(get_db)
):
    """
    更新单个模型数据
    :param model_name: 模型名称（必传，用于定位记录）
    :param update_data: 需要更新的字段（Body 传参，全部选传，其中，模型名称 name 不能更新）
    :param db: 数据库会话
    :return: 更新结果提示
    """
    # 1. 检查模型是否存在
    existing = db.execute(
        text("SELECT id FROM llm_models WHERE name = :name LIMIT 1"),
        {"name": model_name}
    ).mappings().first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"模型名称 '{model_name}' 不存在"
        )

    # 2. 过滤掉 None 值，只更新有传值的字段
    update_dict = update_data.model_dump(exclude_unset=True)

    if not update_dict:
        raise HTTPException(
            status_code=400,
            detail="未提供任何需要更新的字段"
        )

    # 3. 动态构建 SET 子句
    set_clauses = [f"{key} = :{key}" for key in update_dict.keys()]
    update_dict["original_name"] = model_name  # 用于 WHERE 条件

    sql = text(f"""
        UPDATE llm_models
        SET {', '.join(set_clauses)}
        WHERE name = :original_name
    """)

    # 4. 执行更新，异常时回滚
    try:
        db.execute(sql, update_dict)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"更新模型失败: {str(e)}"
        )

    # 5. 返回成功提示
    return f"模型 '{model_name}' 更新成功"


@router.delete("/delete")
def delete_model(
        model_name: str,
        db: Session = Depends(get_db)
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
    existing = db.execute(
        text("SELECT id FROM llm_models WHERE name = :name LIMIT 1"),
        {"name": model_name}
    ).mappings().first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"模型名称 '{model_name}' 不存在"
        )

    # 3. 执行删除，异常时回滚
    try:
        result = db.execute(
            text("DELETE FROM llm_models WHERE name = :name"),
            {"name": model_name}
        )
        db.commit()
    except Exception as e:
        db.rollback()
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
