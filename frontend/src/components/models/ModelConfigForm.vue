<!-- 模型配置表单：模型详情-配置标签与添加模型抽屉共用（基本信息 / 价格 / 功能开关三段） -->
<!-- 表单数据对象由父级持有并传入，组件就地编辑其字段（与工坊参数面板同一模式） -->

<template>
  <div class="model-config-form">
    <!-- 模型基本信息 -->
    <div class="config-section">
      <h5>基本信息</h5>
      <a-form :model="form" layout="vertical">
        <a-form-item v-if="showName" label="模型名称" required>
          <a-input v-model="form.name" placeholder="例如: gpt-4 (字符串类型)"/>
        </a-form-item>
        <a-form-item label="上游模型名">
          <a-input v-model="form.upstreamName" placeholder="实际请求上游用的模型名，为空则用模型名称"/>
        </a-form-item>
        <a-form-item label="模型分组">
          <a-input v-model="form.modelGroup" placeholder="例如: OpenAI (字符串类型)"/>
        </a-form-item>
        <a-form-item label="模型标签">
          <a-input v-model="form.label" placeholder="例如: 旗舰,对话 (字符串类型)"/>
        </a-form-item>
        <a-form-item label="模型图标">
          <div class="icon-field">
            <div class="icon-field-preview">
              <LobeIcon :name="form.icon" fallback="?" :size="24"/>
            </div>
            <a-input v-model="form.icon"
                     placeholder="lobehub 图标名，如 Qwen / OpenAI / Claude.Color，或图片链接"/>
          </div>
        </a-form-item>
        <a-form-item label="模型描述">
          <a-input v-model="form.description" placeholder="例如: OpenAI最强模型 (字符串类型)"/>
        </a-form-item>
        <a-form-item label="渠道配置">
          <a-select
              v-model="form.channels"
              multiple
              allow-clear
              :max-tag-count="3"
              placeholder="选择该模型可用的渠道"
          >
            <a-option v-for="name in channelNameList" :key="name" :value="name" :label="name"/>
          </a-select>
        </a-form-item>
        <a-form-item label="上下文长度">
          <a-input-number v-model="form.contextLength" :min="1" placeholder="例如: 128 (整数类型)"
                          hide-button/>
        </a-form-item>
        <a-form-item label="最大输出长度">
          <a-input-number v-model="form.maxTokens" :min="1" placeholder="例如: 4096 (整数类型)"
                          hide-button/>
        </a-form-item>
      </a-form>
    </div>

    <a-divider/>

    <!-- 价格配置 -->
    <div class="config-section">
      <h5>价格配置</h5>
      <a-form :model="form" layout="vertical">
        <a-form-item label="计费模式">
          <a-switch v-model="form.isRequestMode"/>
          <span class="switch-hint">{{ form.isRequestMode ? '按请求计费' : '按 Token 计费' }}</span>
        </a-form-item>

        <a-form-item v-if="form.isRequestMode" label="每请求价格">
          <a-input-number v-model="form.perRequestPrice" :precision="4" :step="0.1" :min="0"/>
          <span class="unit">元/次</span>
        </a-form-item>

        <template v-else>
          <a-form-item label="输入价格">
            <a-input-number v-model="form.inputPrice" :precision="4" :step="0.1" :min="0"/>
            <span class="unit">元/1M</span>
          </a-form-item>
          <a-form-item label="缓存价格">
            <a-input-number v-model="form.cachePrice" :precision="4" :step="0.1" :min="0"/>
            <span class="unit">元/1M</span>
          </a-form-item>
          <a-form-item label="输出价格">
            <a-input-number v-model="form.outputPrice" :precision="4" :step="0.1" :min="0"/>
            <span class="unit">元/1M</span>
          </a-form-item>
        </template>
      </a-form>
    </div>

    <a-divider/>

    <!-- 功能开关 -->
    <div class="config-section">
      <h5>功能开关</h5>
      <div class="switch-grid">
        <div class="switch-cell">
          <span>是否启用</span>
          <a-switch v-model="form.status"/>
        </div>
        <div class="switch-cell">
          <span>支持视觉</span>
          <a-switch v-model="form.supportVision"/>
        </div>
        <div class="switch-cell">
          <span>置顶模型</span>
          <a-switch v-model="form.isPin"/>
        </div>
        <div class="switch-cell">
          <span>开启日志</span>
          <a-switch v-model="form.isLog"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import LobeIcon from '@/components/common/LobeIcon.vue'
import type {modelInfoSchema} from '@/types'

withDefaults(defineProps<{
  form: modelInfoSchema
  channelNameList: string[]
  showName?: boolean  // 添加模型时展示"模型名称"输入（编辑配置时不允许改名）
}>(), {showName: false})
</script>

<style scoped>
.config-section {
  margin-bottom: var(--space-2);
}

.config-section h5 {
  margin: 0 0 var(--space-3);
  color: var(--color-text);
  font-weight: var(--font-semibold);
  font-size: var(--text-sm);
}

.unit {
  margin-left: var(--space-2);
  color: var(--color-text-muted);
  font-size: var(--text-xs);
}

.switch-hint {
  margin-left: var(--space-2);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.switch-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3) var(--space-6);
}

.switch-cell {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: var(--text-sm);
  color: var(--color-text);
}

/* 图标输入：预览 + 输入框 */
.icon-field {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  width: 100%;
}

.icon-field-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background-color: var(--color-gray-100);
  flex-shrink: 0;
}
</style>
