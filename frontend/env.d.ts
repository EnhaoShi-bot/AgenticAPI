/// <reference types="vite/client" />

interface ImportMetaEnv {
    /** 开发模式 /api 代理的后端地址（见 frontend/.env.development，仅 vite.config 使用） */
    readonly VITE_BACKEND_URL?: string
    /** 站内接口基地址，默认 /api（代理转发）；前后端分域部署时配置为后端完整地址 */
    readonly VITE_API_BASE?: string
}
