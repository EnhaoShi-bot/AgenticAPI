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
        <a-tooltip v-if="probeVisible" :content="probeTooltip" position="top">
          <a-button type="text" size="mini" :loading="testing" :class="probeIconClass" @click="handleProbe">
            <template #icon>
              <icon-thunderbolt/>
            </template>
          </a-button>
        </a-tooltip>
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
import {computed, ref} from 'vue'
import {Message} from '@arco-design/web-vue'
import LobeIcon from '@/components/common/LobeIcon.vue'
import {testModel} from '@/api/models'
import {getErrorMessage} from '@/api/request'
import {useUserStore} from '@/stores/user'
import {copyText} from '@/utils/feedback'
import {tagColorByName} from '@/utils/colors'
import {groupTagColor, groupTagName, splitLabel} from '@/utils/model'
import type {modelInfoSchema} from '@/types'

const props = defineProps<{
  model: modelInfoSchema
}>()

const emit = defineEmits<{ detail: [model: modelInfoSchema] }>()

/** ═══════════ 拨测（卡片右上角闪电按钮） ═══════════ */

const userStore = useUserStore()

// 闪电按钮可见性：模型启用 + 未登录也展示（点击唤起登录框，保证入口不被埋掉）；
// 仅"已登录但分组无权限"时隐藏——vip 全部可拨，free（含访客）只能拨 free 分组模型
const probeVisible = computed(() =>
    !!props.model.status
    && (!userStore.isLoggedIn
        || userStore.userInfo?.userGroup === 'vip'
        || props.model.modelGroup === 'free'))

// 实际能否执行拨测（点击时的闸门：需登录且分组有权限）
const canProbe = computed(() =>
    userStore.isLoggedIn
    && !!props.model.status
    && (userStore.userInfo?.userGroup === 'vip' || props.model.modelGroup === 'free'))

const testing = ref(false)
// 拨测结果短暂高亮图标（ok 绿 / fail 红），2.5s 后回落为中性色
const probeState = ref<'' | 'ok' | 'fail'>('')
let probeTimer: number | undefined

const probeTooltip = computed(() => {
  if (!userStore.isLoggedIn) return '测试模型连接（需登录）'
  if (testing.value) return '拨测中…'
  if (probeState.value === 'ok') return '拨测成功'
  if (probeState.value === 'fail') return '拨测失败，点我重试'
  return '测试模型连接'
})

const probeIconClass = computed(() => ({
  'probe-ok': probeState.value === 'ok',
  'probe-fail': probeState.value === 'fail',
}))

async function handleProbe() {
  if (testing.value || !props.model.name) return
  // 未登录：唤起登录弹窗，登录成功后可再点一次拨测
  if (!userStore.isLoggedIn) {
    Message.info('拨测需要先登录')
    userStore.openAuthDialog('login')
    return
  }
  if (!canProbe.value) return
  testing.value = true
  probeState.value = ''
  try {
    const res = await testModel(props.model.name)
    const latency = (res.data as { latencyMs?: number } | undefined)?.latencyMs
    probeState.value = 'ok'
    const sec = latency != null ? ` · ${(latency / 1000).toFixed(1)}s` : ''
    Message.success(`拨测成功${sec}，${props.model.name} 可正常调用`)
  } catch (err) {
    probeState.value = 'fail'
    Message.error(getErrorMessage(err, '拨测失败，请稍后重试'))
  } finally {
    testing.value = false
    window.clearTimeout(probeTimer)
    probeTimer = window.setTimeout(() => {
      probeState.value = ''
    }, 2500)
  }
}
</script>

<style scoped>
.model-card {
  display: flex;
  flex-direction: column;
  background-color: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-3) var(--space-3);
  transition: border-color var(--transition-base), box-shadow var(--transition-base),
  transform var(--transition-base);
}

/* 悬停：描边变主色 + 阴影升级 + 轻微上浮（与工坊建议卡同一交互语言） */
.model-card:hover {
  border-color: var(--color-primary-light);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
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
  align-items: center;
  flex-shrink: 0;
  margin-right: -4px;
}

/* 拨测按钮结果反馈：成功短暂变绿、失败短暂变红（默认继承中性文字色） */
.model-actions .probe-ok {
  color: var(--color-success);
}

.model-actions .probe-fail {
  color: var(--color-error);
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
