<!-- lobehub 模型图标：按图标 key 渲染静态 SVG，缺失时回退为首字母占位 -->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { loadLobeIconRaw } from '@/utils/lobeIcons'

const props = withDefaults(
  defineProps<{
    /** 图标 key（lobehub 名称，如 "Qwen"、"OpenAI"、"Claude.Color"）或 http(s) 图片链接 */
    name?: string | null
    /** 图标缺失时兜底显示的文本（一般传模型名），取首字母渲染 */
    fallback?: string
    /** 显示尺寸（px），SVG 按 1em 缩放 */
    size?: number
  }>(),
  { name: '', fallback: '', size: 24 },
)

const svg = ref<string | null>(null)
const isUrl = computed(() => /^https?:\/\//i.test((props.name || '').trim()))

watch(
  () => props.name,
  async (n) => {
    svg.value = isUrl.value ? null : await loadLobeIconRaw((n || '').trim())
  },
  { immediate: true },
)

const letter = computed(() =>
  (props.fallback || props.name || '?').trim().charAt(0).toUpperCase() || '?',
)
</script>

<template>
  <span
    class="lobe-icon"
    :style="{ width: `${size}px`, height: `${size}px`, fontSize: `${size}px` }"
  >
    <img v-if="isUrl" class="lobe-icon-img" :src="(name || '').trim()" alt="" />
    <!-- 包内 SVG 尺寸为 1em × 1em，随外层 font-size 缩放 -->
    <span v-else-if="svg" class="lobe-icon-svg" v-html="svg"></span>
    <span
      v-else
      class="lobe-icon-fallback"
      :style="{ fontSize: `${Math.max(11, Math.round(size * 0.42))}px` }"
    >{{ letter }}</span>
  </span>
</template>

<style scoped>
.lobe-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  line-height: 1;
}

.lobe-icon-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: var(--radius-md);
}

.lobe-icon-svg {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary); /* 单色图标继承 currentColor */
}

.lobe-icon-svg :deep(svg) {
  display: block;
}

.lobe-icon-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  border-radius: var(--radius-full);
  background-color: var(--color-gray-100);
  color: var(--color-text-secondary);
  font-weight: var(--font-semibold);
  user-select: none;
}
</style>
