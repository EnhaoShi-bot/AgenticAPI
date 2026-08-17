<!-- 全局登录/注册弹窗：由导航栏按钮和路由守卫触发，状态放在 user store 里统一管理 -->
<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { Message } from '@arco-design/web-vue'
import type { FormInstance } from '@arco-design/web-vue'
import { useUserStore } from '@/stores/user'
import { getErrorMessage } from '@/api/request'

const router = useRouter()
const userStore = useUserStore()
// 弹窗显隐和模式（login / register）都来自 store，其他地方（如路由守卫）也能控制这个弹窗
const {authDialogVisible: visible, authDialogMode: mode} = storeToRefs(userStore)

// 表单实例（用于触发校验、重置字段）
const formRef = ref<FormInstance>()

// 双模式共用的表单数据（注册多一个确认密码）
const form = reactive({
    username: '',
    password: '',
    confirmPassword: '',
})

// 校验规则：与后端 UserLoginSchema 的字段约束保持一致，前端先拦一道，省一次无效请求
const rules = {
    username: [
        {required: true, message: '请输入用户名'},
        {minLength: 2, maxLength: 50, message: '用户名长度需在 2-50 个字符之间'},
    ],
    password: [
        {required: true, message: '请输入密码'},
        {minLength: 6, maxLength: 100, message: '密码长度需在 6-100 个字符之间'},
    ],
    confirmPassword: [
        {required: true, message: '请再次输入密码'},
        {
            validator: (value: string, cb: (error?: string) => void) => {
                if (mode.value === 'register' && value !== form.password) {
                    cb('两次输入的密码不一致')
                } else {
                    cb()
                }
            },
        },
    ],
}

// 切换登录/注册模式或关闭弹窗时，清空表单和校验提示
watch([visible, mode], () => {
    formRef.value?.resetFields()
})

// 切换模式（弹窗底部的文字链接）
function switchMode(next: 'login' | 'register') {
    mode.value = next
}

// 提交（登录 / 注册共用）：先过表单校验，再调 store 的 action
const submitting = ref(false)

async function handleSubmit() {
    const valid = await formRef.value?.validate().then(() => true).catch(() => false)
    if (!valid) return

    submitting.value = true
    try {
        const payload = {username: form.username, password: form.password}
        const info = mode.value === 'login'
            ? await userStore.loginAction(payload)
            : await userStore.registerAction(payload)

        Message.success(mode.value === 'login' ? `欢迎回来，${info.username}` : `注册成功，欢迎加入`)

        // 登录成功后，跳回用户最初想访问的页面（路由守卫拦截未登录时记录的）
        const target = userStore.consumeRedirectAfterLogin()
        userStore.closeAuthDialog()
        if (target) {
            router.push(target)
        }
    } catch (err) {
        // 失败场景：用户名已存在、密码错误等，后端返回的 message 已被拦截器提取
        Message.error(getErrorMessage(err, mode.value === 'login' ? '登录失败' : '注册失败'))
    } finally {
        submitting.value = false
    }
}
</script>

<template>
  <a-modal
    v-model:visible="visible"
    :title="mode === 'login' ? '登录' : '注册'"
    :width="400"
    :mask-closable="false"
    :footer="false"
  >
    <a-form
      ref="formRef"
      :model="form"
      :rules="rules"
      layout="vertical"
      @keyup.enter="handleSubmit"
    >
      <a-form-item field="username" label="用户名">
        <a-input v-model="form.username" placeholder="2-50 个字符" autocomplete="username" allow-clear/>
      </a-form-item>

      <a-form-item field="password" label="密码">
        <a-input-password
          v-model="form.password"
          placeholder="6-100 个字符"
          :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
        />
      </a-form-item>

      <!-- 确认密码只在注册模式显示 -->
      <a-form-item v-if="mode === 'register'" field="confirmPassword" label="确认密码">
        <a-input-password v-model="form.confirmPassword" placeholder="再次输入密码"/>
      </a-form-item>

      <a-button
        type="primary"
        long
        :loading="submitting"
        @click="handleSubmit"
      >
        {{ mode === 'login' ? '登录' : '注册' }}
      </a-button>

      <!-- 模式切换入口 -->
      <div class="auth-switch">
        <template v-if="mode === 'login'">
          还没有账号？
          <a class="auth-switch-link" @click="switchMode('register')">去注册</a>
        </template>
        <template v-else>
          已有账号？
          <a class="auth-switch-link" @click="switchMode('login')">去登录</a>
        </template>
      </div>
    </a-form>
  </a-modal>
</template>

<style scoped>
.auth-switch {
  margin-top: var(--space-3);
  text-align: center;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.auth-switch-link {
  color: var(--color-primary);
  cursor: pointer;
}

.auth-switch-link:hover {
  color: var(--color-primary-light);
}
</style>
