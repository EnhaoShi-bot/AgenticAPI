// 站点公开配置接口请求（无需登录）
import request from './request'

/** 站点公开配置 */
export interface siteInfo {
    /** 对外公开的后端地址，如 http://localhost:2027 */
    publicBaseUrl: string
    /** 对外中转接口基地址（OpenAI 兼容），如 http://localhost:2027/v1 */
    relayBaseUrl: string
}

/** 获取站点公开配置（对外中转接口地址等，来源为后端 .env 的 PUBLIC_BASE_URL） */
export function getSiteInfo() {
    return request.get<siteInfo>('/site/info')
}
