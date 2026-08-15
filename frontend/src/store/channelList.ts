/* 由于渠道信息需要在多个组件中使用（如模型配置时选择可用渠道），所以使用 pinia 来管理渠道信息 */
import {defineStore} from 'pinia'
import type {channelInfoSchema} from '@/interferences/interference'
import axios from "axios"
import {ref, computed} from 'vue'


// 统一的渠道列表管理，可在多个组件中使用
export const useChannelListStore = defineStore('channelList', () => { // 当前pinia的ID，必填项
    // 从API请求得到的渠道列表
    const totalChannelList = ref<channelInfoSchema[]>([])

    // 计算属性
    const totalChannelNumber = computed(() => totalChannelList.value.length)

    // 渠道名称列表（供模型配置下拉多选用）
    const channelNameList = computed(() => totalChannelList.value.map(c => c.channelName))

    // 加载渠道列表的方法
    function loadTotalChannels() {
        axios.get("/api/channels/get")
            .then(res => {
                totalChannelList.value = res.data
            })
            .catch(error => {
                console.error('加载渠道列表失败:', error)
            })
    }

    // 返回数据及方法
    return {
        totalChannelList,
        totalChannelNumber,
        channelNameList,
        loadTotalChannels
    }
})
