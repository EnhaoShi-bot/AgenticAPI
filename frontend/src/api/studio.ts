// 模型工坊接口封装
//
// 对话接口是 SSE 流式 + OpenAI 风格报文，与站内统一 {code, message, data} 格式不同，
// 因此不走 axios 封装，改用 fetch 手动携带 Bearer 令牌并逐行解析 SSE；
// 语音识别是普通 JSON 接口，直接复用统一 axios 实例。
import request from './request'
import { useUserStore } from '@/stores/user'

/** 多模态内容片段（图片 / 文本） */
export type studioContentPart =
    | { type: 'text'; text: string }
    | { type: 'image_url'; image_url: { url: string } }

/** 发给后端的单条消息：content 为纯文本，或多模态 parts 数组（图片 + 文本） */
export interface studioChatMessage {
    role: 'user' | 'assistant'
    content: string | studioContentPart[]
}

/** POST /studio/chat 请求体 */
export interface studioChatBody {
    model: string
    messages: studioChatMessage[]
    temperature?: number
    top_p?: number
    max_tokens?: number
    system_prompt?: string
    enable_search?: boolean
}

/** 流式回调 */
export interface studioStreamCallbacks {
    /** 正文增量 */
    onChunk?: (text: string) => void
    /** 思维链增量（兼容 reasoning_content / thinking / reasoning 三种字段名） */
    onReasoning?: (text: string) => void
    /** 最后一个 chunk 携带的 token 用量 */
    onUsage?: (usage: { promptTokens: number; completionTokens: number }) => void
    /** 流结束（正常结束、收到 [DONE]、或用户主动停止） */
    onDone?: () => void
    /** 出错（HTTP 错误 / SSE 中携带 error 事件 / 网络中断） */
    onError?: (message: string) => void
}

/**
 * 工坊流式对话：POST /studio/chat，解析 SSE 增量并回调。
 * 用户点停止时由调用方 abort signal，本函数以 onDone 收尾（保留已生成的部分内容）。
 */
export async function streamStudioChat(
    body: studioChatBody,
    callbacks: studioStreamCallbacks,
    signal?: AbortSignal,
): Promise<void> {
    const userStore = useUserStore()

    let resp: Response
    try {
        resp = await fetch('/api/studio/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(userStore.token ? { Authorization: `Bearer ${userStore.token}` } : {}),
            },
            body: JSON.stringify(body),
            signal,
        })
    } catch (err) {
        // 用户主动停止属于正常收尾，不算错误
        if (err instanceof Error && err.name === 'AbortError') {
            callbacks.onDone?.()
            return
        }
        callbacks.onError?.('网络错误，请稍后重试')
        return
    }

    // 非 200 或非 SSE：后端按 OpenAI 风格返回 {"error": {message}}
    const contentType = resp.headers.get('content-type') || ''
    if (!resp.ok || !contentType.includes('text/event-stream')) {
        if (resp.status === 401) {
            userStore.handleUnauthorized()
            callbacks.onError?.('请先登录')
            return
        }
        let message = `请求失败（${resp.status}）`
        try {
            const data = await resp.json()
            message = data?.error?.message || message
        } catch {
            // 响应体不是 JSON 时保留默认提示
        }
        callbacks.onError?.(message)
        return
    }

    // 逐行解析 SSE：跨 chunk 的行可能被切断，用缓冲区拼接
    const reader = resp.body!.getReader()
    const decoder = new TextDecoder()
    let buf = ''

    const handleLine = (line: string) => {
        if (!line.startsWith('data:')) return
        const data = line.slice(5).trim()
        if (!data || data === '[DONE]') return
        let obj: any
        try {
            obj = JSON.parse(data)
        } catch {
            return
        }
        if (!obj || typeof obj !== 'object') return
        // 流中的错误事件
        if (obj.error?.message) {
            callbacks.onError?.(obj.error.message)
            return
        }
        // 最后一个 chunk 的用量
        if (obj.usage?.prompt_tokens != null) {
            callbacks.onUsage?.({
                promptTokens: obj.usage.prompt_tokens,
                completionTokens: obj.usage.completion_tokens ?? 0,
            })
        }
        // 正文与思维链增量
        const delta = obj.choices?.[0]?.delta
        if (delta) {
            if (typeof delta.content === 'string' && delta.content) {
                callbacks.onChunk?.(delta.content)
            }
            const reasoning = delta.reasoning_content ?? delta.thinking ?? delta.reasoning
            if (typeof reasoning === 'string' && reasoning) {
                callbacks.onReasoning?.(reasoning)
            }
        }
    }

    try {
        for (;;) {
            const { done, value } = await reader.read()
            if (done) break
            buf += decoder.decode(value, { stream: true })
            const lines = buf.split('\n')
            buf = lines.pop() || ''
            lines.forEach(handleLine)
        }
        if (buf) handleLine(buf)
        callbacks.onDone?.()
    } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
            callbacks.onDone?.()
            return
        }
        callbacks.onError?.('连接中断，请重试')
    }
}

/** POST /studio/asr：录音 base64 交给后端代理 ASR，返回识别文本 */
export function studioAsr(audio: string, format: string) {
    return request.post<{ text: string }>('/studio/asr', { audio, format })
}
