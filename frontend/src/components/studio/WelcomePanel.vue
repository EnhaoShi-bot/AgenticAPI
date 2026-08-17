<!-- 工坊空会话欢迎页：标题 + 4 条静态提问建议（点击直接发送） -->
<template>
    <div class="welcome-panel">
        <div class="welcome-icon">
            <icon-robot/>
        </div>
        <h2 class="welcome-title">模型工坊</h2>
        <p class="welcome-subtitle">选择模型，开始对话。支持联网搜索、图片与语音输入。</p>

        <div class="suggest-grid">
            <button v-for="item in suggestions" :key="item.title" class="suggest-card"
                    :disabled="!modelName" @click="emit('select', item.prompt)">
                <div class="suggest-title">{{ item.title }}</div>
                <div class="suggest-desc">{{ item.prompt }}</div>
            </button>
        </div>

        <div v-if="!modelName" class="welcome-hint">请先在右侧面板选择模型</div>
    </div>
</template>

<script setup lang="ts">
defineProps<{
    /** 当前是否已选择模型（未选择时建议卡片禁用） */
    modelName: string
}>()

const emit = defineEmits<{ select: [prompt: string] }>()

// 静态提问建议（不做 LLM 动态生成，避免额外开销）
const suggestions = [
    {title: '📝 帮我写点东西', prompt: '帮我写一封简洁得体的请假邮件，事由是明天要去医院复诊。'},
    {title: '💻 解释一段代码', prompt: '用通俗的语言解释一下什么是 Python 的装饰器，并给一个最简单的例子。'},
    {title: '🧠 头脑风暴', prompt: '给我 5 个适合个人开发的周末.side.project 想法，每个附一句话说明。'},
    {title: '📚 学习搭子', prompt: '我想系统学习 SQL，帮我制定一个为期两周、每天 1 小时的学习计划。'},
]
</script>

<style scoped>
.welcome-panel {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-6);
}

.welcome-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 64px;
    height: 64px;
    border-radius: var(--radius-2xl);
    background: var(--color-primary-lighter);
    color: var(--color-primary);
    font-size: 32px;
}

.welcome-title {
    margin: var(--space-3) 0 var(--space-1);
    font-size: var(--text-2xl);
    font-weight: var(--font-bold);
}

.welcome-subtitle {
    color: var(--color-text-muted);
    font-size: var(--text-sm);
    margin-bottom: var(--space-8);
}

.suggest-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 260px));
    gap: var(--space-3);
    width: 100%;
    max-width: 560px;
}

.suggest-card {
    text-align: left;
    padding: var(--space-4);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    background: var(--color-white);
    cursor: pointer;
    font-family: inherit;
    transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.suggest-card:hover:not(:disabled) {
    border-color: var(--color-primary);
    box-shadow: var(--shadow-md);
}

.suggest-card:disabled {
    cursor: not-allowed;
    opacity: 0.6;
}

.suggest-title {
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    margin-bottom: var(--space-1);
}

.suggest-desc {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.welcome-hint {
    margin-top: var(--space-4);
    font-size: var(--text-sm);
    color: var(--color-warning);
}
</style>
