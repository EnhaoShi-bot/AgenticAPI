<!-- 上游 TokenPlan 用量监控 -->

<template>
  <div class="operations-page">


    <!-- 页面标题 -->
    <div class="action-bar" style="display: flex; justify-content: space-between; align-items: center; gap: 12px;">
      <strong>上游 <span class="highlight">TokenPlan</span> 用量监控</strong>
      <div style="display: flex; gap: 8px;">
        <button @click="refreshAllUsage" :loading="loading">全部刷新</button>
        <button @click="toggleSettings">设置凭证</button>
      </div>
    </div>

    <!-- 设置面板侧边栏 -->
    <transition name="slide">
      <div v-if="showSettings" class="settings-sidebar">
        <div class="settings-sidebar-header">
          <h3>设置凭证</h3>
          <button class="close-btn" @click="toggleSettings">✕</button>
        </div>
        <div class="settings-sidebar-body">
          <!-- 火山方舟 -->
          <div class="settings-section">
            <h4>火山方舟 BohrClaw</h4>
            <el-form label-width="100px" size="small">
              <el-form-item label="brmToken">
                <el-input
                    v-model="settings.brmToken"
                    type="password"
                    placeholder="粘贴 brmToken（JWT）"
                    show-password
                    @change="saveSettings"
                />
              </el-form-item>
              <el-form-item label="实例 ID">
                <el-input
                    v-model="settings.instanceId"
                    placeholder="粘贴 ArkClaw Seat 实例 ID（如 ci-xxx）"
                    @change="saveSettings"
                />
              </el-form-item>
            </el-form>
          </div>

          <el-divider/>

          <!-- 阶跃星辰 -->
          <div class="settings-section">
            <h4>阶跃星辰 Step Plan</h4>
            <el-form label-width="100px" size="small">
              <el-form-item label="Oasis-Token">
                <el-input
                    v-model="settings.stepToken"
                    type="password"
                    placeholder="浏览器 Cookie 里的 Oasis-Token 值"
                    show-password
                    @change="saveSettings"
                />
              </el-form-item>
              <el-form-item label="Oasis-Webid">
                <el-input
                    v-model="settings.stepWebid"
                    placeholder="可不填"
                    @change="saveSettings"
                />
              </el-form-item>
            </el-form>
          </div>

          <el-divider/>

          <!-- 阿里云百炼 -->
          <div class="settings-section">
            <h4>阿里云百炼 Token Plan</h4>
            <el-form label-width="100px" size="small">
              <el-form-item label="Cookie">
                <el-input
                    v-model="settings.aliyunCookie"
                    type="password"
                    placeholder="粘贴整行 Cookie 值"
                    show-password
                    @change="saveSettings"
                />
              </el-form-item>
            </el-form>
          </div>

          <el-divider/>

          <!-- 数据打到后端，持久化存储 -->
          <button @click="uploadSettings">保存设置</button>
        </div>
      </div>
    </transition>

    <!-- 遮罩层 -->
    <transition name="fade">
      <div v-if="showSettings" class="settings-overlay" @click="toggleSettings"></div>
    </transition>

    <!-- 数据展示区域 -->
    <div class="data-sections">
      <!-- 火山方舟 Agent Plan -->
      <el-card class="plan-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>火山方舟 Agent Plan</span>
            <el-tag size="small" type="info">Small订阅 × 2</el-tag>
          </div>
          <a href="https://www.volcengine.com/activity/agentplan" target="_blank">官方订阅链接</a>
          <button @click="refreshVolUsage">刷新</button>
        </template>
        <div v-if="volUsage.status !== 'ok'" class="error-text">
          <p>{{ volUsage.status }}</p>
        </div>
        <template v-else>
          <div v-if="volUsage.fiveHour.quota == 0">
            <p>无5小时限额</p>
          </div>
          <div v-else>
            <p>5小时用量: {{ volUsage.fiveHour.used }} / {{ volUsage.fiveHour.quota }}</p>
          </div>
          <div v-if="volUsage.weekly.quota == 0">
            <p>无周度限额</p>
          </div>
          <div v-else>
            <p>周度用量: {{ volUsage.weekly.used }} / {{ volUsage.weekly.quota }}</p>
          </div>
          <div v-if="volUsage.monthly.quota == 0">
            <p>无月度限额</p>
          </div>
          <div v-else>
            <p>月度用量: {{ volUsage.monthly.used }} / {{ volUsage.monthly.quota }}</p>
          </div>
        </template>
      </el-card>

      <!-- 深势科技 Coding Plan -->
      <el-card class="plan-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>深势科技 Coding Plan</span>
            <el-tag size="small" type="info">Standard订阅</el-tag>
          </div>
          <a href="https://bohrclaw.bohrium.com/coding-plan" target="_blank">官方订阅链接</a>
          <button @click="refreshBohrUsage">刷新</button>
        </template>
        <div v-if="bohrUsage.status !== 'ok'" class="error-text">
          <p>{{ bohrUsage.status }}</p>
        </div>
        <template v-else>
          <div v-if="bohrUsage.fiveHour.quota == 0">
            <p>无5小时限额</p>
          </div>
          <div v-else>
            <p>5小时用量: {{ bohrUsage.fiveHour.used }} / {{ bohrUsage.fiveHour.quota }}</p>
          </div>
          <div v-if="bohrUsage.weekly.quota == 0">
            <p>无周度限额</p>
          </div>
          <div v-else>
            <p>周度用量: {{ bohrUsage.weekly.used }} / {{ bohrUsage.weekly.quota }}</p>
          </div>
          <div v-if="bohrUsage.monthly.quota == 0">
            <p>无月度限额</p>
          </div>
          <div v-else>
            <p>月度用量: {{ bohrUsage.monthly.used }} / {{ bohrUsage.monthly.quota }}</p>
          </div>
        </template>
      </el-card>

      <!-- 阶跃星辰 Step Plan -->
      <el-card class="plan-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>阶跃星辰 Step Plan</span>
            <el-tag size="small" type="info">Mini订阅</el-tag>
          </div>
          <a href="https://platform.stepfun.com/step-plan" target="_blank">官方订阅链接</a>
          <button @click="refreshStepUsage">刷新</button>
        </template>
        <div v-if="stepUsage.status !== 'ok'" class="error-text">
          <p>{{ stepUsage.status }}</p>
        </div>
        <template v-else>
          <div v-if="stepUsage.fiveHour.quota == 0">
            <p>无5小时限额</p>
          </div>
          <div v-else>
            <p>5小时用量: {{ stepUsage.fiveHour.used }} / {{ stepUsage.fiveHour.quota }}</p>
          </div>
          <div v-if="stepUsage.weekly.quota == 0">
            <p>无周度限额</p>
          </div>
          <div v-else>
            <p>周度用量: {{ stepUsage.weekly.used }} / {{ stepUsage.weekly.quota }}</p>
          </div>
          <div v-if="stepUsage.monthly.quota == 0">
            <p>无月度限额</p>
          </div>
          <div v-else>
            <p>月度用量: {{ stepUsage.monthly.used }} / {{ stepUsage.monthly.quota }}</p>
          </div>
        </template>
      </el-card>

      <!-- 阿里云百炼 Token Plan -->
      <el-card class="plan-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>阿里云百炼 Token Plan</span>
            <el-tag size="small" type="info">Lite套餐</el-tag>
          </div>
          <a href="https://platform.qianwenai.com/pricing/token-plan" target="_blank">官方订阅链接</a>
          <button @click="refreshAliUsage">刷新</button>
        </template>
        <div v-if="aliUsage.status !== 'ok'" class="error-text">
          <p>{{ aliUsage.status }}</p>
        </div>
        <template v-else>
          <div v-if="aliUsage.fiveHour.quota == 0">
            <p>无5小时限额</p>
          </div>
          <div v-else>
            <p>5小时用量: {{ aliUsage.fiveHour.used }} / {{ aliUsage.fiveHour.quota }}</p>
          </div>
          <div v-if="aliUsage.weekly.quota == 0">
            <p>无周度限额</p>
          </div>
          <div v-else>
            <p>周度用量: {{ aliUsage.weekly.used }} / {{ aliUsage.weekly.quota }}</p>
          </div>
          <div v-if="aliUsage.monthly.quota == 0">
            <p>无月度限额</p>
          </div>
          <div v-else>
            <p>月度用量: {{ aliUsage.monthly.used }} / {{ aliUsage.monthly.quota }}</p>
          </div>
        </template>
      </el-card>

    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, reactive, onMounted} from 'vue'
import {ElMessage} from 'element-plus'
import type {
  cookieSettings,
  volUsageData,
  bohrUsageData,
  stepfunUsageData,
  aliUsageData
} from '@/interferences/interference'
import axios from 'axios'

/* ═══════════════════════ 状态 ═══════════════════════ */

const LS_SETTINGS = 'tokenplan_settings'
const showSettings = ref(false) // 是否显示设置面板
const loading = ref(false) // 是否正在加载数据
const settings = ref<cookieSettings>({
  brmToken: '',
  instanceId: '',
  stepToken: '',
  stepWebid: '',
  aliyunCookie: '',
})

/* ═══════════════════════ 下面存储用量数据 ═══════════════════════ */
const volUsage = reactive<volUsageData>({
  status: "请刷新用量",
  fiveHour: {
    used: 0,
    quota: 0,
  },
  weekly: {
    used: 0,
    quota: 0,
  },
  monthly: {
    used: 0,
    quota: 0,
  },
})
const bohrUsage = reactive<bohrUsageData>({
  status: "请刷新用量",
  fiveHour: {
    used: 0,
    quota: 0,
  },
  weekly: {
    used: 0,
    quota: 0,
  },
  monthly: {
    used: 0,
    quota: 0,
  },
})
const stepUsage = reactive<stepfunUsageData>({
  status: "请刷新用量",
  fiveHour: {
    used: 0,
    quota: 0,
  },
  weekly: {
    used: 0,
    quota: 0,
  },
  monthly: {
    used: 0,
    quota: 0,
  },
})
const aliUsage = reactive<aliUsageData>({
  status: "请刷新用量",
  fiveHour: {
    used: 0,
    quota: 0,
  },
  weekly: {
    used: 0,
    quota: 0,
  },
  monthly: {
    used: 0,
    quota: 0,
  },
})

/* ═══════════════════════ 初始化 ═══════════════════════ */

// 从 localStorage 加载设置
const loadSettings = () => {
  try {
    const raw = localStorage.getItem(LS_SETTINGS)
    if (raw) {
      const parsed = JSON.parse(raw)
      settings.value = {...settings.value, ...parsed}
    }
  } catch {
    // ignore
  }
}


/* ═══════════════════════ 设置面板 ═══════════════════════ */

const toggleSettings = () => {
  showSettings.value = !showSettings.value
}

// 保存设置到 localStorage
const saveSettings = () => {
  localStorage.setItem(LS_SETTINGS, JSON.stringify(settings.value))
  ElMessage.success('设置已保存')
}

// 将更新后的设置上传到后端
const uploadSettings = () => {
  axios.post("/api/operations/upload", {
    brmToken: settings.value.brmToken,
    instanceId: settings.value.instanceId,
    stepToken: settings.value.stepToken,
    stepWebid: settings.value.stepWebid,
    aliyunCookie: settings.value.aliyunCookie,
  }).then(res => {
    console.log(res.data)
    ElMessage.success('设置已上传')
  })
}


/* ═══════════════════════ 刷新数据 ═══════════════════════ */

const refreshVolUsage = () => {
  axios.get("/api/operations/get", {
    params: {
      refresh_channel: 'vol'
    }
  }).then(res => {
    if (res.data.status.vol === "200") {
      volUsage.status = "ok"
      volUsage.fiveHour.used = res.data.vol_usage.volFiveHourUsed
      volUsage.weekly.used = res.data.vol_usage.volWeeklyUsed
      volUsage.monthly.used = res.data.vol_usage.volMonthlyUsed
      volUsage.fiveHour.quota = res.data.vol_usage.volFiveHourTotal
      volUsage.weekly.quota = res.data.vol_usage.volWeeklyTotal
      volUsage.monthly.quota = res.data.vol_usage.volMonthlyTotal
    } else {
      volUsage.status = "数据刷新错误: " + res.data.status.vol
    }
  })
}

const refreshBohrUsage = () => {
  axios.get("/api/operations/get", {
    params: {
      refresh_channel: 'bohr'
    }
  }).then(res => {
    if (res.data.status.bohr === "200") {
      bohrUsage.status = "ok"
      bohrUsage.fiveHour.used = res.data.bohr_usage.bohrFiveHourUsed
      bohrUsage.weekly.used = res.data.bohr_usage.bohrWeeklyUsed
      bohrUsage.monthly.used = res.data.bohr_usage.bohrMonthlyUsed
      bohrUsage.fiveHour.quota = res.data.bohr_usage.bohrFiveHourTotal
      bohrUsage.weekly.quota = res.data.bohr_usage.bohrWeeklyTotal
      bohrUsage.monthly.quota = res.data.bohr_usage.bohrMonthlyTotal
    } else {
      bohrUsage.status = "数据刷新错误: " + res.data.status.bohr
    }
  })
}

const refreshStepUsage = () => {
  axios.get("/api/operations/get", {
    params: {
      refresh_channel: 'stepfun'
    }
  }).then(res => {
    if (res.data.status.stepfun === "200") {
      stepUsage.status = "ok"
      stepUsage.fiveHour.used = res.data.stepfun_usage.stepfunFiveHourUsed
      stepUsage.weekly.used = res.data.stepfun_usage.stepfunWeeklyUsed
      stepUsage.monthly.used = res.data.stepfun_usage.stepfunMonthlyUsed
      stepUsage.fiveHour.quota = res.data.stepfun_usage.stepfunFiveHourTotal
      stepUsage.weekly.quota = res.data.stepfun_usage.stepfunWeeklyTotal
      stepUsage.monthly.quota = res.data.stepfun_usage.stepfunMonthlyTotal
    } else {
      stepUsage.status = "数据刷新错误: " + res.data.status.stepfun
    }
  })
}

const refreshAliUsage = () => {
  axios.get("/api/operations/get", {
    params: {
      refresh_channel: 'ali'
    }
  }).then(res => {
    if (res.data.status.ali === "200") {
      aliUsage.status = "ok"
      aliUsage.fiveHour.used = res.data.ali_usage.aliFiveHourUsed
      aliUsage.weekly.used = res.data.ali_usage.aliWeeklyUsed
      aliUsage.monthly.used = res.data.ali_usage.aliMonthlyUsed
      aliUsage.fiveHour.quota = res.data.ali_usage.aliFiveHourTotal
      aliUsage.weekly.quota = res.data.ali_usage.aliWeeklyTotal
      aliUsage.monthly.quota = res.data.ali_usage.aliMonthlyTotal
    } else {
      aliUsage.status = "数据刷新错误: " + res.data.status.ali
    }
  })
}

const refreshAllUsage = () => {
  axios.get("/api/operations/get", {
    params: {
      refresh_channel: 'all'
    }
  }).then(res => {
    // vol
    if (res.data.status.vol === "200") {
      volUsage.status = "ok"
      volUsage.fiveHour.used = res.data.vol_usage.volFiveHourUsed
      volUsage.weekly.used = res.data.vol_usage.volWeeklyUsed
      volUsage.monthly.used = res.data.vol_usage.volMonthlyUsed
      volUsage.fiveHour.quota = res.data.vol_usage.volFiveHourTotal
      volUsage.weekly.quota = res.data.vol_usage.volWeeklyTotal
      volUsage.monthly.quota = res.data.vol_usage.volMonthlyTotal
    } else {
      volUsage.status = "数据刷新错误: " + res.data.status.vol
    }
    // bohr
    if (res.data.status.bohr === "200") {
      bohrUsage.status = "ok"
      bohrUsage.fiveHour.used = res.data.bohr_usage.bohrFiveHourUsed
      bohrUsage.weekly.used = res.data.bohr_usage.bohrWeeklyUsed
      bohrUsage.monthly.used = res.data.bohr_usage.bohrMonthlyUsed
      bohrUsage.fiveHour.quota = res.data.bohr_usage.bohrFiveHourTotal
      bohrUsage.weekly.quota = res.data.bohr_usage.bohrWeeklyTotal
      bohrUsage.monthly.quota = res.data.bohr_usage.bohrMonthlyTotal
    } else {
      bohrUsage.status = "数据刷新错误: " + res.data.status.bohr
    }
    // stepfun
    if (res.data.status.stepfun === "200") {
      stepUsage.status = "ok"
      stepUsage.fiveHour.used = res.data.stepfun_usage.stepfunFiveHourUsed
      stepUsage.weekly.used = res.data.stepfun_usage.stepfunWeeklyUsed
      stepUsage.monthly.used = res.data.stepfun_usage.stepfunMonthlyUsed
      stepUsage.fiveHour.quota = res.data.stepfun_usage.stepfunFiveHourTotal
      stepUsage.weekly.quota = res.data.stepfun_usage.stepfunWeeklyTotal
      stepUsage.monthly.quota = res.data.stepfun_usage.stepfunMonthlyTotal
    } else {
      stepUsage.status = "数据刷新错误: " + res.data.status.stepfun
    }
    // ali
    if (res.data.status.ali === "200") {
      aliUsage.status = "ok"
      aliUsage.fiveHour.used = res.data.ali_usage.aliFiveHourUsed
      aliUsage.weekly.used = res.data.ali_usage.aliWeeklyUsed
      aliUsage.monthly.used = res.data.ali_usage.aliMonthlyUsed
      aliUsage.fiveHour.quota = res.data.ali_usage.aliFiveHourTotal
      aliUsage.weekly.quota = res.data.ali_usage.aliWeeklyTotal
      aliUsage.monthly.quota = res.data.ali_usage.aliMonthlyTotal
    } else {
      aliUsage.status = "数据刷新错误: " + res.data.status.ali
    }
  })
}

// 页面刚加载的时候刷新全部数据
onMounted(() => {
  refreshAllUsage()
  loadSettings()
})

</script>

<style scoped>
.operations-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.page-title {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  margin: 0;
}

.highlight {
  color: var(--color-error);
}

.action-bar {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.last-updated {
  margin-left: auto;
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

/* 设置面板侧边栏 */
.settings-sidebar {
  position: fixed;
  top: 0;
  right: 0;
  width: 420px;
  max-width: 90vw;
  height: 100vh;
  background: var(--color-bg, #fff);
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.08);
  z-index: 1001;
  display: flex;
  flex-direction: column;
}

.settings-sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border, #e4e7ed);
}

.settings-sidebar-header h3 {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--color-text-muted);
  line-height: 1;
  padding: 4px;
}

.close-btn:hover {
  color: var(--color-text);
}

.settings-sidebar-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.settings-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.35);
  z-index: 1000;
}

/* 过渡动画 */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.settings-section h4 {
  margin: 0 0 var(--space-3) 0;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-text-secondary);
}

.form-hint {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-top: var(--space-1);
}

.data-sections {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-4);
  margin-top: var(--space-2);
}

.plan-card {
  min-height: 160px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.plan-card p {
  margin: var(--space-2) 0;
  font-size: var(--text-sm);
  color: var(--color-text);
}

.empty-text {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  text-align: center;
  padding: var(--space-4) 0;
}

.error-text {
  font-size: var(--text-sm);
  color: var(--color-error);
  text-align: center;
  padding: var(--space-4) 0;
}
</style>