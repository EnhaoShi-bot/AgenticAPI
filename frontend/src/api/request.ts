// 统一的 axios 实例：baseURL 为 /api（由 vite 代理转发到后端）
import axios from 'axios'

const request = axios.create({
    baseURL: '/api',
    timeout: 30000,
})

export default request
