/* 模型工坊会话状态管理
 *
 * 会话 / 消息 / 参数全部持久化在浏览器 localStorage（按用户 id 隔离），不上服务端：
 * - 刷新页面后会话从 localStorage 恢复
 * - 登录用户变化（登录 / 登出 / 切账号）时整体重载对应桶
 * - 流式生成期间消息高频更新，落盘做 500ms 防抖，避免阻塞主线程
 */
import {defineStore} from 'pinia'
import {ref, computed, watch} from 'vue'
import {useUserStore} from './user'
import type {studioImage, studioMessage, studioSession, studioParams} from '@/types'
import {DEFAULT_STUDIO_PARAMS} from '@/types'

// 会话数量上限（超出丢弃最旧的）
const MAX_SESSIONS = 50
// 自动标题截取长度
const TITLE_LENGTH = 30

/** 生成短随机 id（时间戳 36 进制 + 随机串，本地存储够用） */
export function genStudioId(): string {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

function storageKey(kind: 'sessions' | 'params', userId: number | string): string {
    return `agenticapi_studio_${kind}_${userId}`
}

export const useStudioStore = defineStore('studio', () => {
    const userStore = useUserStore()

    const sessions = ref<studioSession[]>([])
    const currentSessionId = ref('')
    /** 参数面板当前选择的模型（随参数一起持久化） */
    const selectedModelName = ref('')
    const params = ref<studioParams>({...DEFAULT_STUDIO_PARAMS})
    /** 输入框联网搜索开关 */
    const enableSearch = ref(false)
    /** 是否正在流式生成 */
    const isStreaming = ref(false)

    const currentSession = computed(() =>
        sessions.value.find(s => s.id === currentSessionId.value) || null,
    )
    const currentMessages = computed(() => currentSession.value?.messages ?? [])

    /** ═══════════ 持久化（localStorage，按用户隔离） ═══════════ */

    // 当前数据归属的用户 id（拿到 userInfo 前先挂 guest 桶，拿到后会整体重载）
    let currentUserId: number | string = 'guest'
    let saveTimer: ReturnType<typeof setTimeout> | null = null

    function persistSessions() {
        try {
            localStorage.setItem(storageKey('sessions', currentUserId), JSON.stringify(sessions.value))
        } catch (err) {
            console.warn('工坊会话保存失败:', err)
        }
    }

    function persistParams() {
        try {
            localStorage.setItem(
                storageKey('params', currentUserId),
                JSON.stringify({model: selectedModelName.value, ...params.value}),
            )
        } catch (err) {
            console.warn('工坊参数保存失败:', err)
        }
    }

    // 流式期间防抖落盘：合并 500ms 内的多次消息更新
    function scheduleSave() {
        if (saveTimer !== null) return
        saveTimer = setTimeout(() => {
            saveTimer = null
            persistSessions()
        }, 500)
    }

    // 流结束时立即落盘（供生成流程收尾调用）
    function flushSave() {
        if (saveTimer !== null) {
            clearTimeout(saveTimer)
            saveTimer = null
        }
        persistSessions()
    }

    // 用户切换时取消未落盘的防抖任务（避免把旧用户数据写进新用户的桶）
    function cancelPendingSave() {
        if (saveTimer !== null) {
            clearTimeout(saveTimer)
            saveTimer = null
        }
    }

    /** 登录用户变化时重载对应的本地数据（登出后回到 guest 桶） */
    function reloadForUser() {
        const userId = userStore.userInfo?.id ?? 'guest'
        if (userId === currentUserId) return
        cancelPendingSave()
        currentUserId = userId

        try {
            const raw = localStorage.getItem(storageKey('sessions', userId))
            const parsed = raw ? JSON.parse(raw) : []
            sessions.value = Array.isArray(parsed) ? parsed : []
        } catch {
            sessions.value = []
        }

        try {
            const rawParams = localStorage.getItem(storageKey('params', userId))
            const parsed = rawParams ? JSON.parse(rawParams) : {}
            selectedModelName.value = typeof parsed.model === 'string' ? parsed.model : ''
            params.value = {...DEFAULT_STUDIO_PARAMS, ...parsed}
        } catch {
            selectedModelName.value = ''
            params.value = {...DEFAULT_STUDIO_PARAMS}
        }

        currentSessionId.value = sessions.value[0]?.id || ''
    }

    // 跟随登录态自动换桶（App 启动拉到 userInfo、登录 / 登出时触发）
    watch(() => userStore.userInfo?.id, reloadForUser, {immediate: true})

    /** ═══════════ 会话管理 ═══════════ */

    function createSession(): studioSession {
        const session: studioSession = {
            id: genStudioId(),
            title: '新对话',
            modelName: selectedModelName.value,
            messages: [],
            createTime: Date.now(),
            updateTime: Date.now(),
        }
        sessions.value.unshift(session)
        if (sessions.value.length > MAX_SESSIONS) sessions.value.length = MAX_SESSIONS
        currentSessionId.value = session.id
        persistSessions()
        return session
    }

    function switchSession(id: string) {
        currentSessionId.value = id
    }

    function deleteSession(id: string) {
        const idx = sessions.value.findIndex(s => s.id === id)
        if (idx === -1) return
        sessions.value.splice(idx, 1)
        if (currentSessionId.value === id) {
            currentSessionId.value = sessions.value[0]?.id || ''
        }
        persistSessions()
    }

    function renameSession(id: string, title: string) {
        const session = sessions.value.find(s => s.id === id)
        if (!session || !title.trim()) return
        session.title = title.trim()
        session.updateTime = Date.now()
        persistSessions()
    }

    function clearAllSessions() {
        sessions.value = []
        currentSessionId.value = ''
        persistSessions()
    }

    /** ═══════════ 消息读写 ═══════════ */

    /** 从首条用户消息派生会话标题 */
    function deriveTitle(content: string): string {
        const text = content.trim().replace(/\s+/g, ' ')
        if (!text) return '新对话'
        return text.length > TITLE_LENGTH ? text.slice(0, TITLE_LENGTH) + '…' : text
    }

    function touchSession(sessionId: string) {
        const session = sessions.value.find(s => s.id === sessionId)
        if (session) session.updateTime = Date.now()
    }

    /** 追加一条消息（默认写进当前会话），首条用户消息自动生成标题 */
    function addMessage(msg: studioMessage, sessionId?: string) {
        const session = sessions.value.find(s => s.id === (sessionId || currentSessionId.value))
        if (!session) return
        session.messages.push(msg)
        session.updateTime = Date.now()
        if (msg.role === 'user' && session.messages.filter(m => m.role === 'user').length === 1) {
            session.title = deriveTitle(msg.content)
        }
        scheduleSave()
    }

    /** 当前会话最后一条 assistant 消息（流式回调的写入目标） */
    function lastAssistant(): studioMessage | null {
        const msgs = currentMessages.value
        const last = msgs[msgs.length - 1]
        if (!last) return null
        return last.role === 'assistant' ? last : null
    }

    /** 流式增量：追加到当前会话最后一条 assistant 消息的正文 / 思维链 */
    function appendToLastAssistant(field: 'content' | 'reasoning', text: string) {
        const msg = lastAssistant()
        if (!msg) return
        if (field === 'content') {
            msg.content += text
        } else {
            msg.reasoning = (msg.reasoning || '') + text
        }
        touchSession(currentSessionId.value)
        scheduleSave()
    }

    /** 回答回填用量（流式最后一个 chunk 的 usage + 前端计时） */
    function setLastAssistantUsage(promptTokens: number, completionTokens: number, elapsedMs: number) {
        const msg = lastAssistant()
        if (!msg) return
        msg.usage = {promptTokens, completionTokens, elapsedMs}
        scheduleSave()
    }

    /** 标记最后一条 assistant 消息出错 */
    function setLastAssistantError(error: string) {
        const msg = lastAssistant()
        if (!msg) return
        msg.error = error
        scheduleSave()
    }

    /** 重新生成用：移除当前会话最后一条 assistant 消息，返回是否移除成功 */
    function removeLastAssistant(): boolean {
        const session = currentSession.value
        const last = session?.messages[session.messages.length - 1]
        if (!last || last.role !== 'assistant') return false
        session!.messages.pop()
        scheduleSave()
        return true
    }

    return {
        // 状态
        sessions,
        currentSessionId,
        selectedModelName,
        params,
        enableSearch,
        isStreaming,
        currentSession,
        currentMessages,
        // 会话管理
        createSession,
        switchSession,
        deleteSession,
        renameSession,
        clearAllSessions,
        // 消息读写
        addMessage,
        appendToLastAssistant,
        setLastAssistantUsage,
        setLastAssistantError,
        removeLastAssistant,
        // 持久化
        persistParams,
        flushSave,
        reloadForUser,
    }
})
