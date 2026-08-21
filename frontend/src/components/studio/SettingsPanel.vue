<!-- 工坊右侧参数面板：模型选择 / 系统提示词 / 采样参数 -->
<template>
    <div class="settings-panel">
        <div class="panel-section">
            <div class="panel-label">模型列表</div>
            <a-select v-model="studioStore.selectedModelName" placeholder="请选择一个模型" allow-clear allow-search
                      @change="studioStore.persistParams()">
                <a-optgroup v-for="group in modelGroups" :key="group.label" :label="group.label">
                    <a-option v-for="model in group.models" :key="model.name" :value="model.name"
                              :label="model.name || model.label">
                        <div class="model-option">
                            <span class="model-option-name">{{ model.name ||  model.label }}</span>
                        </div>
                    </a-option>
                </a-optgroup>
            </a-select>
            <div v-if="!allowedModels.length" class="panel-hint">暂无可用模型</div>
        </div>

        <div class="panel-section">
            <div class="panel-label">System Prompt</div>
            <a-textarea v-model="studioStore.params.systemPrompt" :max-length="2000" show-word-limit :auto-size="{minRows: 3, maxRows: 8}"
                        placeholder="请输入系统提示词，如：你是一个资深代码审查员，负责检查代码的质量和性能"
                        @change="studioStore.persistParams()"/>
        </div>

        <div class="panel-section">
            <div class="panel-label">
                Temperature
                <span class="param-value">{{ studioStore.params.temperature.toFixed(1) }}</span>
            </div>
            <a-slider v-model="studioStore.params.temperature" :min="0" :max="2" :step="0.1"
                      @change="studioStore.persistParams()"/>
        </div>

        <div class="panel-section">
            <div class="panel-label">
                Top P
                <span class="param-value">{{ studioStore.params.topP.toFixed(2) }}</span>
            </div>
            <a-slider v-model="studioStore.params.topP" :min="0" :max="1" :step="0.05"
                      @change="studioStore.persistParams()"/>
        </div>

        <div class="panel-section">
            <div class="panel-label">Max Tokens</div>
            <a-input-number v-model="studioStore.params.maxTokens" :min="1" :max="maxTokensLimit"
                             :step="256" mode="button" @change="studioStore.persistParams()"/>
            <div class="panel-hint">当前模型上限 {{ maxTokensLimit.toLocaleString() }}</div>
        </div>

        <div class="panel-section">
            <a-button long @click="resetParams">
                <template #icon><icon-refresh/></template>
                重置参数
            </a-button>
        </div>
    </div>
</template>

<script setup lang="ts">
import {computed, watch} from 'vue'
import {useStudioStore} from '@/stores/studio'
import {useUserStore} from '@/stores/user'
import {useModelListStore} from '@/stores/modelList'
import {DEFAULT_STUDIO_PARAMS} from '@/types'

const studioStore = useStudioStore()
const userStore = useUserStore()
const modelListStore = useModelListStore()

// 可用模型：启用中 + 当前用户分组有权调用（与后端中转的分组校验一致：free 用户仅 free 模型）
const allowedModels = computed(() =>
    modelListStore.totalModelList.filter(m =>
        m.status && (m.modelGroup === 'free' || userStore.userInfo?.userGroup === 'vip'),
    ),
)

// 按 free / vip 分组展示
const modelGroups = computed(() => {
    const groups: Array<{label: string; models: typeof allowedModels.value}> = []
    for (const group of ['free', 'vip']) {
        const models = allowedModels.value.filter(m => m.modelGroup === group)
        if (models.length) {
            groups.push({label: group === 'free' ? '免费模型' : 'VIP 模型', models})
        }
    }
    return groups
})

// max_tokens 上限：取当前所选模型配置，未配置或未选模型时给一个通用上限
const maxTokensLimit = computed(() => {
    const model = allowedModels.value.find(m => m.name === studioStore.selectedModelName)
    return model?.maxTokens && model.maxTokens > 0 ? model.maxTokens : 32768
})

// 模型列表加载后 / 切换用户后：当前选择无效时回落到第一个可用模型
// （同时监听用户 id：登录信息晚于模型列表到达时，store 重载可能把选择清空，需要重新兜底）
watch(
    [allowedModels, () => userStore.userInfo?.id],
    () => {
        const first = allowedModels.value[0]?.name
        if (first && !allowedModels.value.some(m => m.name === studioStore.selectedModelName)) {
            studioStore.selectedModelName = first
            studioStore.persistParams()
        }
    },
    {immediate: true},
)

function resetParams() {
    studioStore.params.systemPrompt = DEFAULT_STUDIO_PARAMS.systemPrompt
    studioStore.params.temperature = DEFAULT_STUDIO_PARAMS.temperature
    studioStore.params.topP = DEFAULT_STUDIO_PARAMS.topP
    studioStore.params.maxTokens = DEFAULT_STUDIO_PARAMS.maxTokens
    studioStore.persistParams()
}
</script>

<style scoped>
.settings-panel {
    height: 100%;
    overflow-y: auto;
    padding: var(--space-4) var(--space-4);
    background: var(--color-gray-50);
}

.panel-section {
    margin-bottom: var(--space-5);
}

.panel-label {
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    color: var(--color-text-secondary);
    margin-bottom: var(--space-2);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.param-value {
    font-weight: var(--font-normal);
    color: var(--color-text-muted);
    font-variant-numeric: tabular-nums;
}

.panel-hint {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    margin-top: var(--space-1);
}

/* 下拉选项：名称 + 描述两段 */
.model-option {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2);
}

.model-option-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.model-option-desc {
    flex-shrink: 1;
    max-width: 150px;
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
</style>
