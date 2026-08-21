<!-- 模型工坊：对话式 Playground
     布局：左侧会话侧边栏 + 中间对话窗口与输入框 + 右侧参数面板，两侧可折叠。
     对话走站内 /studio/chat 接口（登录、不计费），会话本地存储。 -->
<template>
    <div class="studio-page">
        <!-- 左：会话侧边栏 -->
        <div class="studio-aside left" :class="{collapsed: !sidebarOpen}">
            <SessionSidebar />
        </div>

        <!-- 中：对话区 -->
        <div class="studio-center">
            <button class="panel-toggle left-toggle" :title="sidebarOpen ? '收起侧边栏' : '展开侧边栏'"
                    @click="sidebarOpen = !sidebarOpen">
                <icon-left v-if="sidebarOpen"/>
                <icon-right v-else/>
            </button>
            <button class="panel-toggle right-toggle" :title="panelOpen ? '收起参数面板' : '展开参数面板'"
                    @click="panelOpen = !panelOpen">
                <icon-right v-if="panelOpen"/>
                <icon-left v-else/>
            </button>

            <div class="studio-main">
                <WelcomePanel v-if="!studioStore.currentMessages.length"
                              :model-name="studioStore.selectedModelName" @select="sendPrompt" />
                <ChatMessages v-else :messages="studioStore.currentMessages"
                              :is-streaming="studioStore.isStreaming" @regenerate="handleRegenerate" />
            </div>

            <ChatInput :support-vision="supportVision" @send="handleSend" @stop="handleStop" />
        </div>

        <!-- 右：参数面板 -->
        <div class="studio-aside right" :class="{collapsed: !panelOpen}">
            <SettingsPanel />
        </div>
    </div>
</template>

<script setup lang="ts">
import {computed, ref} from 'vue'
import {Message} from '@arco-design/web-vue'
import SessionSidebar from '@/components/studio/SessionSidebar.vue'
import SettingsPanel from '@/components/studio/SettingsPanel.vue'
import ChatMessages from '@/components/studio/ChatMessages.vue'
import ChatInput from '@/components/studio/ChatInput.vue'
import WelcomePanel from '@/components/studio/WelcomePanel.vue'
import {useStudioStore, genStudioId} from '@/stores/studio'
import {useModelListStore} from '@/stores/modelList'
import {streamStudioChat} from '@/api/studio'
import type {studioChatMessage, studioContentPart} from '@/api/studio'
import type {studioImage} from '@/types'

const studioStore = useStudioStore()
const modelListStore = useModelListStore()

const sidebarOpen = ref(true)
const panelOpen = ref(true)

// 当前所选模型是否支持图片输入（不支持时输入框禁用图片相关功能）
const supportVision = computed(() => {
    const model = modelListStore.totalModelList.find(m => m.name === studioStore.selectedModelName)
    return !!model?.supportVision
})

let abortController: AbortController | null = null

/** 组装发给后端的上下文：当前会话全部消息，带图用户消息转 OpenAI 多模态 parts（图片在前文本在后） */
function buildContextMessages(): studioChatMessage[] {
    const messages: studioChatMessage[] = []
    for (const msg of studioStore.currentMessages) {
        if (msg.role === 'user') {
            if (!msg.content.trim() && !msg.images?.length) continue
            if (msg.images?.length) {
                const parts: studioContentPart[] = msg.images.map(img => (
                    {type: 'image_url', image_url: {url: img.dataUrl}}
                ))
                if (msg.content.trim()) parts.push({type: 'text', text: msg.content})
                messages.push({role: 'user', content: parts})
            } else {
                messages.push({role: 'user', content: msg.content})
            }
        } else if (msg.content.trim()) {
            // 跳过空回复（生成中的占位、失败的空消息）
            messages.push({role: 'assistant', content: msg.content})
        }
    }
    return messages
}

/** 发起一轮生成：先插入 assistant 占位，再流式写入增量 */
async function runGeneration() {
    const session = studioStore.currentSession
    if (!session || studioStore.isStreaming) return

    // 兜底持久化：确保每次成功发起生成时，当前所选模型与参数必然落盘
    // （模型下拉的 change 事件在个别交互路径下可能漏触发，刷新后模型选择会回落）
    studioStore.persistParams()

    studioStore.addMessage({
        id: genStudioId(), role: 'assistant', content: '', reasoning: '', createTime: Date.now(),
    })
    studioStore.isStreaming = true
    const startTime = Date.now()
    abortController = new AbortController()

    try {
        await streamStudioChat(
            {
                model: studioStore.selectedModelName,
                messages: buildContextMessages(),
                temperature: studioStore.params.temperature,
                top_p: studioStore.params.topP,
                max_tokens: studioStore.params.maxTokens,
                system_prompt: studioStore.params.systemPrompt,
                enable_search: studioStore.enableSearch,
            },
            {
                onChunk: t => studioStore.appendToLastAssistant('content', t),
                onReasoning: t => studioStore.appendToLastAssistant('reasoning', t),
                onSearch: s => studioStore.updateLastAssistantSearch(s.query, s.status === 'start'),
                onUsage: u => studioStore.setLastAssistantUsage(u.promptTokens, u.completionTokens, Date.now() - startTime),
                onError: msg => studioStore.setLastAssistantError(msg),
            },
            abortController.signal,
        )
    } finally {
        studioStore.isStreaming = false
        abortController = null
        studioStore.flushSave()
    }
}

/** 发送用户消息（来自输入框 / 欢迎页建议卡片） */
function handleSend({text, images}: {text: string; images: studioImage[]}) {
    if (studioStore.isStreaming) return
    if (!studioStore.selectedModelName) {
        Message.warning('请先在右侧参数面板选择模型')
        return
    }
    if (!studioStore.currentSession) studioStore.createSession()
    const session = studioStore.currentSession!
    session.modelName = studioStore.selectedModelName

    studioStore.addMessage({
        id: genStudioId(),
        role: 'user',
        content: text,
        images: images.length ? images : undefined,
        createTime: Date.now(),
    })
    void runGeneration()
}

/** 欢迎页建议卡片：点击直接作为消息发送 */
function sendPrompt(prompt: string) {
    handleSend({text: prompt, images: []})
}

/** 停止生成：中断请求，已生成的部分内容保留 */
function handleStop() {
    abortController?.abort()
}

/** 重新生成：移除最后一条回复后，基于同一上下文重发 */
async function handleRegenerate() {
    if (studioStore.isStreaming) return
    if (!studioStore.removeLastAssistant()) {
        Message.warning('没有可重新生成的回复')
        return
    }
    await runGeneration()
}
</script>

<style scoped>
.studio-page {
    display: flex;
    height: 100%;
    background: var(--color-white);
}

.studio-aside {
    flex-shrink: 0;
    overflow: hidden;
    transition: width 0.25s ease;
}


/* 左侧会话列表面板 */
.studio-aside.left {
    width: 270px;
    border-right: 1px solid var(--color-border);
}

.studio-aside.left.collapsed {
    width: 0;
    border-right: none;
}

/* 右侧会话列表面板 */
.studio-aside.right {
    width: 270px;
    border-left: 1px solid var(--color-border);
}

.studio-aside.right.collapsed {
    width: 0;
    border-left: none;
}

.studio-center {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    position: relative;
}

.studio-main {
    flex: 1;
    min-height: 0;
}

/* 两侧面板折叠按钮 */
.panel-toggle {
    position: absolute;
    top: 10px;
    z-index: 10;
    width: 22px;
    height: 44px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background: var(--color-white);
    color: var(--color-text-muted);
    font-size: 14px;
    cursor: pointer;
    box-shadow: var(--shadow-sm);
    transition: color var(--transition-fast), border-color var(--transition-fast);
}

.panel-toggle:hover {
    color: var(--color-primary);
    border-color: var(--color-primary);
}

.left-toggle {
    left: 8px;
}

.right-toggle {
    right: 8px;
}
</style>
