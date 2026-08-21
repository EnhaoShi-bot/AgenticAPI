// 统一的 axios 实例：baseURL 为 /api（由 vite 代理转发到后端）
// 后端所有接口统一返回 { code, message, data } 结构，规范详见 backend/docs/后端API接口规范.md
//
// 鉴权约定：
// - 请求拦截器：本地有令牌时自动附加请求头 Authorization: Bearer <token>
// - 响应拦截器：收到 401（令牌缺失/无效/过期）时清空登录态并唤起登录弹窗
// - 403 表示"已登录但无权限"（如访客调用管理接口），按普通业务错误提示，不动登录态
import axios from 'axios'
import {useUserStore} from '@/stores/user'

/** 后端统一响应体外壳 */
export interface apiResponse<T = unknown> {
    code: number
    message: string
    data: T
}

/** 站内接口基地址：默认 /api，开发模式由 Vite 代理转发到后端（地址见 frontend/.env.development），
 *  生产同源部署由反向代理（如 nginx）转发；前后端分域部署时可在前端 .env 配置 VITE_API_BASE 为后端完整地址。
 *  工坊 SSE 等不走 axios 的请求也用它拼接，保证全站只有一个基地址配置。 */
export const API_BASE: string = import.meta.env.VITE_API_BASE || '/api'

const request = axios.create({
    baseURL: API_BASE,
    timeout: 30000,
})

// 请求拦截器：自动附加 Bearer 令牌
// （在回调内部才调用 useUserStore()，避免模块加载阶段的循环依赖问题）
request.interceptors.request.use((config) => {
    const userStore = useUserStore()
    if (userStore.token) {
        config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
})

// 这些接口自身的 401 属于"密码错误"之类的业务失败，不应触发"请先登录"弹窗
const AUTH_ENDPOINTS = ['/user/login', '/user/register', '/user/logout']

function isAuthEndpoint(url: string | undefined): boolean {
    return !!url && AUTH_ENDPOINTS.some((path) => url.startsWith(path))
}

// 响应拦截器：解包统一响应体
// - code === 200：把 response.data 替换为业务数据 data，业务代码直接使用 res.data
// - code !== 200：转为 Promise.reject，并携带后端返回的 message
request.interceptors.response.use(
    (response) => {
        const body = response.data as apiResponse
        if (body && typeof body === 'object' && 'code' in body) {
            if (body.code !== 200) {
                return Promise.reject(new Error(body.message || '请求失败'))
            }
            response.data = body.data
        }
        return response
    },
    (error) => {
        // HTTP 层错误（4xx / 5xx），后端同样返回统一格式的 body
        const status = error.response?.status

        // 登录态失效（401）：清空本地令牌并唤起登录弹窗，业务代码只会收到一个 reject
        // 403（访客越权等权限问题）走下面的普通错误分支，只提示不登出
        if (status === 401 && !isAuthEndpoint(error.config?.url)) {
            useUserStore().handleUnauthorized()
            return Promise.reject(new Error('请先登录'))
        }

        const body = error.response?.data as apiResponse | undefined
        return Promise.reject(new Error(body?.message || error.message || '网络错误，请稍后重试'))
    },
)

/** 从请求错误中提取可展示给用户的提示信息 */
export function getErrorMessage(err: unknown, fallback = '请求失败'): string {
    if (axios.isAxiosError(err)) {
        const body = err.response?.data as apiResponse | undefined
        return body?.message || err.message || fallback
    }
    if (err instanceof Error && err.message) {
        return err.message
    }
    if (typeof err === 'string' && err) {
        return err
    }
    return fallback
}

export default request
