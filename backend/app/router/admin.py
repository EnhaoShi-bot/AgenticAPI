"""管理员用户管理接口（控制台-用户页面使用，需管理员权限）"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import log as log_crud
from app.crud import user as user_crud
from app.router.deps import get_db
from app.schemas.admin import ALLOWED_GROUPS, AdminUserBatchDeleteSchema, AdminUserUpdateSchema
from app.utils.auth import get_current_admin
from app.utils.response import success_response

router = APIRouter(prefix="/admin", tags=["Admin"])


def _user_dict(user) -> dict:
    """ORM 对象转驼峰字典"""
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "phone": user.phone,
        "isGuest": user.is_guest,
        "isAdmin": user.is_admin,
        "balance": float(user.balance),
        "usedQuota": float(user.used_quota),
        "userGroup": user.user_group,
        "status": user.status,
        "lastLoginTime": user.last_login_time,
        "createTime": user.create_time,
    }


@router.get("/users")
async def list_users(
        keyword: str = "",
        page: int = 1,
        pageSize: int = 10,
        db: AsyncSession = Depends(get_db),
        admin=Depends(get_current_admin),
):
    """分页查询用户列表（可按用户名/昵称模糊搜索）"""
    if page < 1:
        page = 1
    if pageSize < 1 or pageSize > 100:
        pageSize = 10
    users, total = await user_crud.list_users(db, keyword.strip(), page, pageSize)
    return success_response(message="获取用户列表成功", data={"list": [_user_dict(u) for u in users], "total": total})


@router.put("/users/{user_id}")
async def update_user(
        user_id: int,
        body: AdminUserUpdateSchema,
        db: AsyncSession = Depends(get_db),
        admin=Depends(get_current_admin),
):
    """修改用户信息（余额 / 分组 / 管理员 / 状态 / 昵称）"""
    target = await user_crud.get_user_by_id(db, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")

    update_dict = body.model_dump(exclude_unset=True, exclude_none=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="未提供任何需要更新的字段")

    # 分组取值校验
    if "user_group" in update_dict and update_dict["user_group"] not in ALLOWED_GROUPS:
        raise HTTPException(status_code=400, detail=f"分组只能是 {' / '.join(ALLOWED_GROUPS)}")

    # 不变量：管理员必须是 vip 分组（vip 才能调用全部分组的模型）
    if update_dict.get("is_admin") is True:
        update_dict["user_group"] = "vip"

    # 不允许修改自己的管理员身份（防止误操作把自己降权后没人能管理用户）
    if user_id == admin.id and "is_admin" in update_dict and target.is_admin:
        raise HTTPException(status_code=400, detail="不能修改自己的管理员身份")

    changed = "、".join(update_dict.keys())
    rowcount = await user_crud.update_user_by_id(db, user_id, update_dict)
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")
    await log_crud.write_log(
        db, type="admin", action="update_user", user_id=admin.id, username=admin.username,
        detail=f"修改了用户 {target.username} 的信息（{changed}）",
    )
    return success_response(message="用户信息更新成功")


@router.delete("/users")
async def delete_users(
        body: AdminUserBatchDeleteSchema,
        db: AsyncSession = Depends(get_db),
        admin=Depends(get_current_admin),
):
    """批量删除用户（连带删除其登录令牌与API密钥；不能删除自己）"""
    ids = body.ids
    if admin.id in ids:
        raise HTTPException(status_code=400, detail="不能删除自己")

    deleted = await user_crud.delete_users(db, ids)
    await log_crud.write_log(
        db, type="admin", action="delete_users", user_id=admin.id, username=admin.username,
        detail=f"批量删除了 {deleted} 个用户（ids={ids}）",
    )
    return success_response(message=f"已删除 {deleted} 个用户", data={"deleted": deleted})
