<!-- 访客模式注意事项弹窗（方案B：确认后后端创建临时访客账号，令牌24小时有效，数据按账号隔离） -->
<script setup lang="ts">
import {ref} from 'vue'
import {Message} from '@arco-design/web-vue'
import {useUserStore} from '@/stores/user'
import {getErrorMessage} from '@/api/request'

// v-model:visible 由父组件（AppHeader）控制
// 【注意】defineModel 必须带 'visible' 参数才能对应父组件的 v-model:visible，
// 不带参数时绑的是默认的 modelValue，和父组件对不上会导致弹窗永远打不开
const visible = defineModel<boolean>('visible', {default: false})

const userStore = useUserStore()
const loading = ref(false)

// 确认进入访客模式：调后端创建临时访客账号，成功后走正常登录态（令牌自动带上）
async function confirmGuest() {
  loading.value = true
  try {
    const info = await userStore.guestAction()
    visible.value = false
    Message.success(`已进入访客模式（${info.nickname || info.username}，24 小时内有效）`)
  } catch (err) {
    Message.error(getErrorMessage(err, '访客模式开启失败，请稍后重试'))
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <a-modal
    v-model:visible="visible"
    title="注意事项"
    :width="420"
    :mask-closable="false"
  >
    <div class="guest-tips">
      <p>访客账号可能会被定期清理。</p>
      <p>数据不会跨会话保留。</p>
      <p>如需完整功能和数据持久化，请注册正式账号。</p>
    </div>

    <template #footer>
      <a-button :disabled="loading" @click="visible = false">取消</a-button>
      <a-button type="primary" :loading="loading" @click="confirmGuest">继续以访客浏览</a-button>
    </template>
  </a-modal>
</template>

<style scoped>
.guest-tips p {
  margin: 0 0 10px;
  line-height: 1.7;
  color: var(--color-text-secondary);
}

.guest-tips p:last-child {
  margin-bottom: 0;
}
</style>
