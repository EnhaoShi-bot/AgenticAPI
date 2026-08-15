<!-- 渠道配置管理 -->

<template>
  <div class="channels-page">
    <!-- 【顶部操作栏】标题、搜索框、操作按钮 -->
    <div class="action-bar">
      <strong class="page-title">渠道配置</strong>
      <div class="search-box">
        <el-input
            v-model="searchKeyword"
            placeholder="搜索渠道名称"
            clearable
            size="default"
        />
      </div>
      <div class="action-buttons">
        <el-button @click="fetchChannels" :loading="loading">刷新</el-button>
        <el-button type="primary" @click="openAddDrawer">添加渠道</el-button>
      </div>
    </div>

    <!-- 【渠道列表】表格展示 -->
    <el-table
        :data="filteredChannels"
        v-loading="loading"
        border
        stripe
        empty-text="暂无渠道数据"
        style="width: 100%;"
    >
      <el-table-column prop="channelName" label="渠道名称" min-width="150" fixed="left"/>
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <!-- 单向绑定，切换时调接口，成功后才更新本地状态 -->
          <el-switch
              :model-value="row.status"
              @change="(val: boolean) => handleStatusChange(row, val)"
          />
        </template>
      </el-table-column>
      <el-table-column prop="baseUrl" label="Base URL" min-width="220" show-overflow-tooltip/>
      <el-table-column prop="supportModels" label="支持模型" min-width="180" show-overflow-tooltip/>
      <el-table-column prop="timeout" label="超时(秒)" width="100" align="center"/>
      <el-table-column label="用量比例" width="120" align="center">
        <template #default="{ row }">
          {{ (Number(row.usedRatio) * 100).toFixed(1) }}%
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" align="center" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openEditDrawer(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 【新增/编辑抽屉】复用同一表单，通过 dialogMode 区分 -->
    <el-drawer
        v-model="drawerVisible"
        :title="drawerTitle"
        direction="rtl"
        size="520px"
        :close-on-click-modal="true"
        :destroy-on-close="true"
    >
      <div class="config-drawer-content">
        <el-form :model="channelForm" label-width="100px">
          <!-- 基本信息 -->
          <div class="config-section">
            <h5>基本信息</h5>
            <el-form-item label="渠道名称">
              <!-- 编辑模式下渠道名称不可修改（后端不允许更新 channel_name） -->
              <el-input
                  v-model="channelForm.channelName"
                  :disabled="dialogMode === 'edit'"
                  placeholder="例如: openai-main"
              />
            </el-form-item>
            <el-form-item label="Base URL">
              <el-input v-model="channelForm.baseUrl" placeholder="例如: https://api.openai.com/v1"/>
            </el-form-item>
            <el-form-item label="API Key">
              <el-input
                  v-model="channelForm.apiKey"
                  type="password"
                  show-password
                  placeholder="sk-..."
              />
            </el-form-item>
            <el-form-item label="支持模型">
              <div class="tag-input-wrap">
                <el-tag
                    v-for="(m, i) in channelForm.supportModels"
                    :key="i"
                    closable
                    size="small"
                    @close="channelForm.supportModels.splice(i, 1)"
                >{{ m }}</el-tag>
                <div class="tag-input-row">
                  <el-input
                      v-model="newModelInput"
                      size="small"
                      placeholder="输入模型名后回车或点 + 添加"
                      style="width: 220px;"
                      @keyup.enter="addModelTag"
                  />
                  <el-button size="small" @click="addModelTag">+</el-button>
                </div>
              </div>
            </el-form-item>
            <el-form-item label="描述">
              <el-input
                  v-model="channelForm.description"
                  type="textarea"
                  :rows="2"
                  placeholder="渠道备注信息"
              />
            </el-form-item>
          </div>

          <el-divider/>

          <!-- 运行参数 -->
          <div class="config-section">
            <h5>运行参数</h5>
            <el-form-item label="状态">
              <el-switch
                  v-model="channelForm.status"
                  active-text="启用"
                  inactive-text="禁用"
              />
            </el-form-item>
            <el-form-item label="超时(秒)">
              <el-input-number v-model="channelForm.timeout" :min="1" :max="600" :step="5"/>
            </el-form-item>
            <el-form-item label="用量比例">
              <el-input-number
                  v-model="channelForm.usedRatio"
                  :min="0"
                  :max="1"
                  :step="0.05"
                  :precision="2"
              />
              <span class="unit">{{ (channelForm.usedRatio * 100).toFixed(0) }}%</span>
            </el-form-item>
          </div>
        </el-form>
      </div>

      <!-- 底部操作按钮 -->
      <template #footer>
        <div class="drawer-footer">
          <el-button @click="drawerVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            {{ dialogMode === 'add' ? '添加' : '保存' }}
          </el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import {ref, reactive, computed, onMounted} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import {getChannels, addChannel, updateChannel, deleteChannel} from '@/api/channels'
import type {channelInfoSchema} from '@/types'

/** ═══════════ 列表与筛选 ═══════════ */

const loading = ref(false)              // 表格加载状态
const searchKeyword = ref('')           // 搜索关键字
const channels = ref<channelInfoSchema[]>([])  // 全量渠道列表

// 按渠道名称过滤
const filteredChannels = computed(() => {
  const kw = searchKeyword.value.trim().toLowerCase()
  if (!kw) return channels.value
  return channels.value.filter(c => c.channelName.toLowerCase().includes(kw))
})

// 获取全量渠道列表
const fetchChannels = () => {
  loading.value = true
  getChannels()
      .then(res => {
        channels.value = res.data
      })
      .catch(err => {
        console.error(err)
        ElMessage.error(err.response?.data?.detail || '获取渠道列表失败')
      })
      .finally(() => {
        loading.value = false
      })
}


/** ═══════════ 新增 / 编辑 ═══════════ */

const drawerVisible = ref(false)                    // 抽屉是否可见
const dialogMode = ref<'add' | 'edit'>('add')       // 当前抽屉模式
const submitting = ref(false)                       // 提交中状态

// 表单数据（新增/编辑共用）
const channelForm = reactive<channelInfoSchema>({
  channelName: '',
  baseUrl: '',
  apiKey: '',
  supportModels: [],
  status: true,
  timeout: 30,
  usedRatio: 0,
  description: null,
})

// 抽屉标题随模式变化
const drawerTitle = computed(() =>
    dialogMode.value === 'add' ? '添加新渠道' : `编辑渠道：${channelForm.channelName}`
)

// 重置表单为默认值
const resetForm = () => {
  Object.assign(channelForm, {
    channelName: '',
    baseUrl: '',
    apiKey: '',
    supportModels: [],
    status: true,
    timeout: 30,
    usedRatio: 0,
    description: null,
  })
}

// 支持模型的逐个添加：输入框 + 加号按钮，回车也可添加
const newModelInput = ref('')
const addModelTag = () => {
  const v = newModelInput.value.trim()
  if (!v) return
  // 去重，避免重复添加同一模型名
  if (!channelForm.supportModels.includes(v)) {
    channelForm.supportModels.push(v)
  }
  newModelInput.value = ''
}

// 打开新增抽屉
const openAddDrawer = () => {
  dialogMode.value = 'add'
  resetForm()
  drawerVisible.value = true
}

// 打开编辑抽屉，并回填当前行数据
const openEditDrawer = (row: channelInfoSchema) => {
  dialogMode.value = 'edit'
  Object.assign(channelForm, {
    channelName: row.channelName ?? '',
    baseUrl: row.baseUrl ?? '',
    apiKey: row.apiKey ?? '',
    supportModels: row.supportModels ?? [],
    status: row.status ?? true,
    timeout: Number(row.timeout) || 30,
    usedRatio: Number(row.usedRatio) || 0,
    description: row.description ?? null,
  })
  drawerVisible.value = true
}

// 提交表单：根据模式调用新增或更新接口
const handleSubmit = () => {
  if (!channelForm.channelName.trim()) {
    ElMessage.error('渠道名称不能为空')
    return
  }
  submitting.value = true
  if (dialogMode.value === 'add') {
    // 新增：POST 全量字段
    addChannel({...channelForm})
        .then(res => {
          ElMessage.success(res.data || '添加渠道成功')
          drawerVisible.value = false
          fetchChannels()
        })
        .catch(err => {
          console.error(err)
          ElMessage.error(err.response?.data?.detail || '添加渠道失败')
        })
        .finally(() => {
          submitting.value = false
        })
  } else {
    // 更新：PUT 全量字段（后端按 channel_name 定位，且 channel_name 不会被更新）
    updateChannel({...channelForm})
        .then(res => {
          ElMessage.success(res.data || '保存配置成功')
          drawerVisible.value = false
          fetchChannels()
        })
        .catch(err => {
          console.error(err)
          ElMessage.error(err.response?.data?.detail || '保存配置失败')
        })
        .finally(() => {
          submitting.value = false
        })
  }
}

/** ═══════════ 状态快速切换 ═══════════ */

// 表格内 switch 切换状态：只更新 status 字段，失败时重新拉取列表以恢复真实状态
const handleStatusChange = (row: channelInfoSchema, val: boolean) => {
  updateChannel({
    channelName: row.channelName,
    status: val,
  })
      .then(() => {
        row.status = val
        ElMessage.success('状态已更新')
      })
      .catch(err => {
        console.error(err)
        ElMessage.error(err.response?.data?.detail || '状态更新失败')
        fetchChannels()
      })
}

/** ═══════════ 删除 ═══════════ */

const handleDelete = (row: channelInfoSchema) => {
  ElMessageBox.confirm(
      `确定要删除渠道 "${row.channelName}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
  ).then(() => {
    // 删除接口通过 query 参数 channel_name 传参
    deleteChannel(row.channelName)
        .then(res => {
          ElMessage.success(res.data || '渠道删除成功')
          fetchChannels()
        })
        .catch(err => {
          console.error(err)
          ElMessage.error(err.response?.data?.detail || '渠道删除失败')
        })
  }).catch(() => {
    // 用户取消删除，不做处理
  })
}

/** ═══════════ 初始化 ═══════════ */

onMounted(() => {
  fetchChannels()
})
</script>

<style scoped>
.channels-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* 顶部操作栏 */
.action-bar {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.page-title {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  white-space: nowrap;
}

.search-box {
  flex: 1;
  max-width: 320px;
  margin-left: auto;
}

.action-buttons {
  display: flex;
  gap: var(--space-2);
}

/* 抽屉表单 */
.config-drawer-content {
  padding: 0 10px;
}

.config-section {
  margin-bottom: 12px;
}

.config-section h5 {
  margin: 0 0 12px 0;
  color: var(--color-text);
  font-weight: var(--font-semibold);
  font-size: var(--text-base);
}

.unit {
  margin-left: 8px;
  color: var(--color-text-muted);
  font-size: 13px;
}

.tag-input-wrap {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  width: 100%;
}

.tag-input-row {
  display: flex;
  gap: 6px;
  align-items: center;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
