// 管理员用户管理接口请求
import request from './request'

/** 用户管理列表中的一行 */
export interface adminUserItem {
    id: number;
    username: string;
    nickname: string | null;
    phone: string | null;
    isGuest: boolean;
    isAdmin: boolean;
    balance: number;
    usedQuota: number;
    userGroup: string;
    status: boolean;
    lastLoginTime: string | null;
    createTime: string | null;
}

/** 分页查询用户列表 */
export function getAdminUsers(params: { keyword?: string; page: number; pageSize: number }) {
    return request.get<{ list: adminUserItem[]; total: number }>('/admin/users', { params })
}

/** 修改用户（余额 / 分组 / 管理员 / 状态 / 昵称） */
export function updateAdminUser(
    userId: number,
    data: { nickname?: string; balance?: number; userGroup?: string; isAdmin?: boolean; status?: boolean },
) {
    return request.put(`/admin/users/${userId}`, data)
}

/** 批量删除用户 */
export function deleteAdminUsers(ids: number[]) {
    return request.delete<{ deleted: number }>('/admin/users', { data: { ids } })
}
