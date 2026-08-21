<!-- 模型广场的单张模型卡片：图标/标签/价格/能力标识，复制模型名内置，"更多详情"抛给父级 -->

<template>
  <div class="model-card" :class="{ 'is-pin': model.isPin }">
    <!-- 卡片头：图标 + 名称与标签 + 操作 -->
    <div class="model-card-head">
      <div class="model-icon-box">
        <LobeIcon :name="model.icon" :fallback="model.name" :size="30"/>
      </div>

      <div class="model-title-wrap">
        <div class="model-name" :title="model.name">{{ model.name }}</div>
        <div class="model-tags">
          <a-tag :color="groupTagColor(model.modelGroup)" size="small">
            {{ groupTagName(model.modelGroup) }}
          </a-tag>
          <a-tag v-for="tag in splitLabel(model.label).slice(0, 2)" :key="tag" size="small"
                 color="arcoblue">
            {{ tag }}
          </a-tag>
          <a-tag v-if="splitLabel(model.label).length > 2" size="small" :color="tagColorByName(model.label)">
            +{{ splitLabel(model.label).length - 2 }}
          </a-tag>
        </div>
      </div>

      <div class="model-actions">
        <a-tooltip content="复制模型名" position="top">
          <a-button type="text" size="mini" @click="copyText(model.name, '模型名称已复制')">
            <template #icon>
              <icon-copy/>
            </template>
          </a-button>
        </a-tooltip>
      </div>
    </div>

    <!-- 价格区：按次计费单行展示，按 token 计费三列展示 -->
    <div v-if="model.isRequestMode" class="model-price model-price-single">
      <span class="price-value">¥{{ model.perRequestPrice }}</span>
      <span class="price-unit">元 / 次请求</span>
    </div>
    <div v-else class="model-price">
      <div class="price-item">
        <div class="price-item-label">输入</div>
        <div class="price-item-value">¥{{ model.inputPrice }}</div>
      </div>
      <div class="price-item">
        <div class="price-item-label">缓存</div>
        <div class="price-item-value">¥{{ model.cachePrice }}</div>
      </div>
      <div class="price-item">
        <div class="price-item-label">输出</div>
        <div class="price-item-value">¥{{ model.outputPrice }}</div>
      </div>
    </div>

    <!-- 卡片底：能力标识 + 详情入口 -->
    <div class="model-card-foot">
      <div class="model-features">
        <span v-if="model.supportVision" class="model-feature">视觉</span>
        <span v-if="!model.status" class="model-feature model-feature-off">停用</span>
      </div>
      <a-button type="text" size="mini" @click="emit('detail', model)">
        更多详情
        <template #icon>
          <icon-right/>
        </template>
      </a-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import LobeIcon from '@/components/common/LobeIcon.vue'
import {copyText} from '@/utils/feedback'
import {tagColorByName} from '@/utils/colors'
import {groupTagColor, groupTagName, splitLabel} from '@/utils/model'
import type {modelInfoSchema} from '@/types'

defineProps<{
  model: modelInfoSchema
}>()

const emit = defineEmits<{ detail: [model: modelInfoSchema] }>()
</script>

<style scoped>
.model-card {
  display: flex;
  flex-direction: column;
  background-color: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-3) var(--space-3);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.model-card:hover {
  border-color: var(--color-primary-light);
  box-shadow: var(--shadow-sm);
}

/* 置顶模型：整卡金色浅底 + 描边 + 右上角徽章 */
.model-card.is-pin {
  position: relative; /* 徽章 ::after 的定位锚点 */
  background: linear-gradient(160deg, var(--color-gold-lighter), var(--color-white) 55%);
  border-color: var(--color-gold);
}

/* 置顶卡 hover 时保持金色系描边，不退回普通卡的蓝色 */
.model-card.is-pin:hover {
  border-color: var(--color-warning);
}

.model-card.is-pin::after {
  content: '推荐调用';
  position: absolute;
  top: -10px;
  right: 12px;
  padding: 1px 8px;
  font-size: var(--text-xs);
  line-height: 18px;
  color: var(--color-white);
  background: linear-gradient(90deg, var(--color-gold), var(--color-warning));
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-sm);
}

/* 卡片头 */
.model-card-head {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.model-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: var(--radius-md);
  background-color: var(--color-gray-100);
  flex-shrink: 0;
}

.model-title-wrap {
  flex: 1;
  min-width: 0;
}

.model-name {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.model-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: var(--space-1);
}

.model-actions {
  display: flex;
  flex-shrink: 0;
  margin-right: -4px;
}

/* 价格区 */
.model-price {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-1);
  margin-top: var(--space-2);
  padding: var(--space-1) var(--space-1);
  background-color: var(--color-gray-50);
  border-radius: var(--radius-md);
  flex: 1;
}

.model-price-single {
  grid-template-columns: auto 1fr;
  align-items: baseline;
  gap: var(--space-2);
}

.price-item-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-bottom: 2px;
}

.price-item-value {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-text);
  font-variant-numeric: tabular-nums;
}

.price-value {
  font-family: var(--font-mono);
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text);
  font-variant-numeric: tabular-nums;
}

.price-unit {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

/* 卡片底 */
.model-card-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: var(--space-2);
}

.model-features {
  display: flex;
  gap: var(--space-1);
}

.model-feature {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0 5px;
  line-height: 18px;
}

.model-feature-pin {
  color: var(--color-warning);
  border-color: var(--color-warning);
}

.model-feature-off {
  color: var(--color-error);
  border-color: var(--color-error);
}
</style>
