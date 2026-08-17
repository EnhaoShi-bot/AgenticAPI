/* 由于渠道信息需要在多个组件中使用（如模型配置时选择可用渠道），所以使用 pinia 来管理渠道信息
 * 【注意】这里走公开的 /channels/names 接口只拿渠道名：
 * 完整渠道数据（含 apiKey）需要登录，公开页面不应依赖它 */
import {defineStore} from 'pinia'
import {getChannelNames} from '@/api/channels'
import {ref, computed} from 'vue'


// 统一的渠道名称列表管理，可在多个组件中使用
export const useChannelListStore = defineStore('channelList', () => { // 当前pinia的ID，必填项
    // 从API请求得到的渠道名称列表
    const channelNameList = ref<string[]>([])

    // 计算属性
    const totalChannelNumber = computed(() => channelNameList.value.length)

    // 加载渠道名称列表的方法
    function loadTotalChannels() {
        getChannelNames()
            .then(res => {
                channelNameList.value = res.data
            })
            .catch(error => {
                console.error('加载渠道名称列表失败:', error)
            })
    }

    // 返回数据，以及一个方法
    return {
        channelNameList,
        totalChannelNumber,
        loadTotalChannels
    }
})
