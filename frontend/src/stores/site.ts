/* 站点配置：对外中转接口地址的唯一来源，避免在代码里硬编码 localhost:2027
 *
 * 优先级：后端 /site/info（读的是后端 .env 的 PUBLIC_BASE_URL，部署时只改后端一处）
 *        > 回退值：开发模式直连本机后端；生产同源部署取当前站点地址
 * App 挂载时 loadSiteInfo() 拉取一次，各页面从本 store 取值展示。
 */
import {defineStore} from 'pinia'
import {ref, computed} from 'vue'
import {getSiteInfo} from '@/api/site'

export const useSiteStore = defineStore('site', () => {
    // 对外公开的后端地址（不含 /v1）
    const publicBaseUrl = ref(
        import.meta.env.DEV ? 'http://localhost:2027' : window.location.origin,
    )

    // 对外中转接口基地址（OpenAI 兼容），如 http://localhost:2027/v1
    const relayBaseUrl = computed(() => publicBaseUrl.value.replace(/\/+$/, '') + '/v1')

    // 中转对话接口完整地址，如 http://localhost:2027/v1/chat/completions
    const chatCompletionsUrl = computed(() => relayBaseUrl.value + '/chat/completions')

    // 拉取后端配置；失败时保持回退值，页面照常展示
    async function loadSiteInfo() {
        try {
            const res = await getSiteInfo()
            if (res.data?.publicBaseUrl) publicBaseUrl.value = res.data.publicBaseUrl
        } catch (error) {
            console.error('加载站点配置失败:', error)
        }
    }

    return {publicBaseUrl, relayBaseUrl, chatCompletionsUrl, loadSiteInfo}
})
