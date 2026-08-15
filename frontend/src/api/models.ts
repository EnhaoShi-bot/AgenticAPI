// 模型相关接口请求
import request from './request'
import type { modelInfoSchema } from '@/types'

/** 获取全量模型列表 */
export function getModels() {
    return request.get<modelInfoSchema[]>('/models/get')
}

/** 添加单个模型 */
export function addModel(data: Partial<modelInfoSchema>) {
    return request.post('/models/post', data)
}

/** 更新单个模型（按 name 定位，name 本身不可更新） */
export function updateModel(data: Partial<modelInfoSchema>) {
    return request.put('/models/put', data)
}

/** 删除模型（按 name 删除） */
export function deleteModel(modelName: string) {
    return request.delete('/models/delete', { params: { model_name: modelName } })
}
