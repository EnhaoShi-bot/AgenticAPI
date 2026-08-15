import json
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.session import get_db
from pydantic import BaseModel, Field

router = APIRouter(prefix="/channels")


# 渠道数据字段定义，公开，可不做鉴权校验
class ChannelSchema(BaseModel):
    model_config = {"populate_by_name": True}

    channel_name: str = Field(alias="channelName")
    base_url: str = Field(default="", alias="baseUrl")
    api_key: str = Field(default="", alias="apiKey")
    support_models: list[str] = Field(default_factory=list, alias="supportModels")
    status: bool = Field(default=True, alias="status")
    timeout: int = Field(default=30, alias="timeout")
    used_ratio: float = Field(default=0.0, alias="usedRatio")
    description: str | None = Field(default=None, alias="description")


def _parse_json_list(raw) -> list:
    """把数据库里的 JSON 字符串解析为 list；空串/NULL/异常统一返回 []"""
    if not raw or not isinstance(raw, str) or not raw.strip():
        return []
    try:
        v = json.loads(raw)
        return v if isinstance(v, list) else []
    except Exception:
        return []


@router.get("/get")
async def get_channels(
        db: AsyncSession = Depends(get_db)
):
    """
    获取全量渠道列表
    :param db: 数据库会话
    """
    channels = await db.execute(
        text("SELECT * FROM llm_channels")
    )
    channels = channels.mappings().all()

    result = []
    for channel in channels:
        d = dict(channel)
        # support_models 在库里是 JSON 字符串，返回前端时解析为真正的数组
        d["support_models"] = _parse_json_list(d.get("support_models"))
        result.append(ChannelSchema(**d).model_dump(by_alias=True, mode="json"))
    return result


@router.post("/post")
async def add_channel(
        new_channel: ChannelSchema,
        db: AsyncSession = Depends(get_db)
):
    """
    添加单个渠道
    :param new_channel: 渠道数据
    :return: 渠道ID
    """
    channel = new_channel.model_dump()  # 转换为字典

    # 插入前检查 channel_name 是否已存在，避免数据库抛唯一性异常导致 500
    result = await db.execute(
        text("SELECT id FROM llm_channels WHERE channel_name = :channel_name LIMIT 1"),
        {"channel_name": channel["channel_name"]}
    )
    existing = result.mappings().first()
    if existing:
        raise HTTPException(status_code=400, detail=f"渠道名称 '{channel['channel_name']}' 已存在")

    # support_models：把数组序列化为 JSON 字符串存库
    channel["support_models"] = json.dumps(channel.get("support_models") or [], ensure_ascii=False)

    try:
        result = await db.execute(
            text(
                """
                INSERT INTO llm_channels
                (channel_name, base_url, api_key, support_models,
                 status, timeout, used_ratio, description)
                VALUES (:channel_name, :base_url, :api_key, :support_models,
                        :status, :timeout, :used_ratio, :description)
                """
            ),
            {**channel}  # 这里一次性插入所有字段，避免重复代码
        )
        await db.flush()
        res_id = result.lastrowid
        await db.commit()
    except Exception as e:
        # 异常时回滚事务，防止脏数据/锁表，并返回具体错误信息
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"添加渠道失败: {str(e)}")

    if res_id:
        return f"添加渠道成功，渠道ID：{res_id}"
    else:
        raise HTTPException(status_code=500, detail="添加渠道失败")



@router.put("/put")
async def put_channel(
        update_data: ChannelSchema,
        db: AsyncSession = Depends(get_db)
):
    """
    更新单个模型数据
    :param update_data: 需要更新的字段（Body 传参，全部选传，其中，模型名称 name 不能更新）
    :param db: 数据库会话
    :return: 更新结果提示
    """
    # 1. 检查渠道是否存在
    channel_name = update_data.model_dump()["channel_name"]
    result = await db.execute(
        text("SELECT id FROM llm_channels WHERE channel_name = :channel_name LIMIT 1"),
        {"channel_name": channel_name}
    )
    existing = result.mappings().first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"渠道 '{channel_name}' 不存在"
        )

    # 2. 过滤掉 None 值，只更新有传值的字段，同时需要排除 channel_name 字段，因为 channel_name 不能更新
    update_dict = update_data.model_dump(exclude_unset=True, exclude={"channel_name"})

    if not update_dict:
        raise HTTPException(
            status_code=400,
            detail="未提供任何需要更新的字段"
        )

    # support_models：把数组序列化为 JSON 字符串存库
    if "support_models" in update_dict and update_dict["support_models"] is not None:
        update_dict["support_models"] = json.dumps(update_dict["support_models"], ensure_ascii=False)

    # 3. 动态构建 SET 子句
    set_clauses = [f"{key} = :{key}" for key in update_dict.keys()]

    sql = text(f"""
        UPDATE llm_channels
        SET {', '.join(set_clauses)}
        WHERE channel_name = :channel_name
    """)

    # 4. 执行更新，异常时回滚
    try:

        await db.execute(sql, {**update_dict, "channel_name": channel_name})
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"更新渠道失败: {str(e)}"
        )

    # 5. 返回成功提示
    return f"渠道 '{channel_name}' 更新成功"


@router.delete("/delete")
async def delete_channel(
        channel_name: str,
        db: AsyncSession = Depends(get_db)
):
    """
    删除渠道
    :param channel_name: 渠道名称（必传）
    :param db: 数据库会话
    :return: 删除结果提示
    """
    # 1. 参数校验：渠道名称不能为空
    if not channel_name or not channel_name.strip():
        raise HTTPException(
            status_code=400,
            detail="模型名称不能为空"
        )

    channel_name = channel_name.strip()

    # 2. 检查渠道是否存在
    result = await db.execute(
        text("SELECT id FROM llm_channels WHERE channel_name = :name LIMIT 1"),
        {"name": channel_name}
    )
    existing = result.mappings().first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"渠道名称 '{channel_name}' 不存在"
        )

    # 3. 执行删除，异常时回滚
    try:
        result = await db.execute(
            text("DELETE FROM llm_channels WHERE channel_name = :name"),
            {"name": channel_name}
        )
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"删除渠道失败: {str(e)}"
        )

    # 4. 确认删除生效（rowcount 为 0 时说明异常）
    if result.rowcount == 0:
        raise HTTPException(
            status_code=500,
            detail="删除渠道失败，未影响任何记录"
        )

    return f"渠道 '{channel_name}' 删除成功"