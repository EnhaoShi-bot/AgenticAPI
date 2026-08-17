// 渠道相关接口请求
import request from './request'
import type { channelInfoSchema } from '@/types'

/** 获取全量渠道名列表（公开接口，只含名称，供公开页面的渠道下拉框使用） */
export function getChannelNames() {
    return request.get<string[]>('/channels/names')
}

/** 获取全量渠道列表（需登录，含密钥等敏感字段） */
export function getChannels() {
    return request.get<channelInfoSchema[]>('/channels')
}

/** 添加单个渠道 */
export function addChannel(data: Partial<channelInfoSchema>) {
    return request.post<{ channelId: number }>('/channels', data)
}

/** 更新单个渠道（按 channelName 定位，channelName 本身不可更新） */
export function updateChannel(channelName: string, data: Partial<channelInfoSchema>) {
    return request.put(`/channels/${encodeURIComponent(channelName)}`, data)
}

/** 删除渠道（按 channelName 删除） */
export function deleteChannel(channelName: string) {
    return request.delete(`/channels/${encodeURIComponent(channelName)}`)
}
