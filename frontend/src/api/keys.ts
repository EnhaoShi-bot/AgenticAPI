// 用户 API 密钥管理接口请求
import request from './request'

/** 一条 API 密钥 */
export interface apiKeyItem {
    id: number;
    name: string;
    key: string;
    status: boolean;
    createTime: string | null;
    lastUsedTime: string | null;
}

/** 获取当前用户的全部密钥 */
export function getKeys() {
    return request.get<apiKeyItem[]>('/keys')
}

/** 创建密钥 */
export function createKey(data: { name: string }) {
    return request.post<apiKeyItem>('/keys', data)
}

/** 更新密钥（改名 / 启停） */
export function updateKey(keyId: number, data: { name?: string; status?: boolean }) {
    return request.put(`/keys/${keyId}`, data)
}

/** 删除密钥 */
export function deleteKey(keyId: number) {
    return request.delete(`/keys/${keyId}`)
}
