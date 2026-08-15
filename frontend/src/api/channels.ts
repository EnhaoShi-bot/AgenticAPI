// 渠道相关接口请求
import request from './request'
import type { channelInfoSchema } from '@/types'

/** 获取全量渠道列表 */
export function getChannels() {
    return request.get<channelInfoSchema[]>('/channels/get')
}

/** 添加单个渠道 */
export function addChannel(data: Partial<channelInfoSchema>) {
    return request.post('/channels/post', data)
}

/** 更新单个渠道（按 channelName 定位，channelName 本身不可更新） */
export function updateChannel(data: Partial<channelInfoSchema>) {
    return request.put('/channels/put', data)
}

/** 删除渠道（按 channelName 删除） */
export function deleteChannel(channelName: string) {
    return request.delete('/channels/delete', { params: { channel_name: channelName } })
}
