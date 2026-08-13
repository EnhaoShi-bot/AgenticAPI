<!-- 模型 -->

<template>
  <div class="models-page">
    <!-- 【页面顶部】标题、描述、搜索框 -->
    <div style="display: flex; flex-direction: column; align-items: center; gap: 12px;">
      <h1 style="margin: 0;">模型广场</h1>
      <p style="margin: 0;">本站已启用{{ totalModelNumber }}个模型，含{{
          freeModelNumber
        }}个免费模型</p>
      <div style="display: flex; gap: 8px;">
        <input
            style="width: 300px;"
            v-model="pageInfo.currentModelName"
            placeholder="输入模型名称"
            @input="pageInfo.currentPageNum = 1"
        />
        <button @click="pageInfo.currentPageNum = 1">搜索</button>
        <button @click="pageInfo.currentModelName = ''; pageInfo.currentPageNum = 1;">清除</button>
      </div>
    </div>

    <!-- 【页面主体】模型列表 -->
    <div class="model-list">
      <!-- 【模型列表】每一张模型卡片 -->
      <div v-for="model in currentPageModels" :key="model.id" class="model-item">
        <div>
          <strong style="font-size: 20px;">{{ model.name }}</strong>
          <!-- 复制按钮 -->
          <button @click="copyModelName(model.name)">复制</button>
          <!-- 拨测按钮 -->
          <button @click="testConnection(model.name)">拨测</button>
          <!-- 管理员配置入口 -->
          <button @click="adminModelConfig(model)">配置</button>
        </div>

        <hr>
        <div style="font-size: 16px;">
          <p>分组：{{ model.modelGroup }}</p>
          <p>标签：{{ model.label }}</p>
          <!-- 如果是按调用计费，就显示调用价格，否则显示输入/缓存/输出价格 -->
          <p v-if="model.isRequestMode">
            每请求：{{ model.perRequestPrice }} 元/次
            <!-- 通过占位对齐高度 -->
            <br>
            <br>
            <br>
          </p>
          <p v-else>
            输入价格：{{ model.inputPrice }} 元/1M
            <br>
            缓存价格：{{ model.cachePrice }} 元/1M
            <br>
            输出价格：{{ model.outputPrice }} 元/1M
          </p>

        </div>

      </div>
    </div>


    <!-- 配置侧边栏弹窗 -->
    <el-drawer
        v-model="configDrawerVisible"
        :title="`当前模型 ： ${currentModel?.name || ''}`"
        direction="rtl"
        size="600px"
        :close-on-click-modal="true"
        :destroy-on-close="true"
    >
      <div class="config-drawer-content">
        <!-- 模型基本信息配置 -->
        <div class="config-section">
          <h5>基本信息</h5>
          <el-form :model="configForm" label-width="70px">
            <el-form-item label="模型名称">
              <el-input v-model="configForm.name" placeholder="请输入模型名称"/>
            </el-form-item>
            <el-form-item label="模型分组">
              <el-input v-model="configForm.modelGroup" placeholder="请输入模型分组"/>
            </el-form-item>
            <el-form-item label="模型标签">
              <el-input v-model="configForm.label" placeholder="请输入模型标签"/>
            </el-form-item>
            <el-form-item label="渠道配置">
              <el-input v-model="configForm.channels" placeholder="请输入渠道配置"/>
            </el-form-item>
            <el-form-item label="输入长度">
              <el-input v-model="configForm.contextLength" type="number" placeholder="请输入上下文长度"/>
            </el-form-item>
            <el-form-item label="输出长度">
              <el-input v-model="configForm.maxTokens" type="number" placeholder="请输入最大输出长度"/>
            </el-form-item>
          </el-form>
        </div>

        <el-divider/>

        <!-- 价格配置 -->
        <div class="config-section">
          <h5>价格配置</h5>
          <el-form :model="configForm" label-width="70px">
            <el-form-item label="计费模式">
              <el-switch
                  v-model="configForm.isRequestMode"
                  active-text="按请求"
                  inactive-text="按Token"
              />
            </el-form-item>

            <template v-if="configForm.isRequestMode">
              <el-form-item label="每请求价格">
                <el-input-number v-model="configForm.perRequestPrice" :precision="4" :step="0.1"/>
                <span class="unit">元/次</span>
              </el-form-item>
            </template>

            <template v-else>
              <el-form-item label="输入价格">
                <el-input-number v-model="configForm.inputPrice" :precision="4" :step="0.1"/>
                <span class="unit">元/1M</span>
              </el-form-item>
              <el-form-item label="缓存价格">
                <el-input-number v-model="configForm.cachePrice" :precision="4" :step="0.1"/>
                <span class="unit">元/1M</span>
              </el-form-item>
              <el-form-item label="输出价格">
                <el-input-number v-model="configForm.outputPrice" :precision="4" :step="0.1"/>
                <span class="unit">元/1M</span>
              </el-form-item>
            </template>
          </el-form>
        </div>

        <el-divider/>

        <!-- 开关配置 -->
        <div class="config-section">
          <h5>功能开关</h5>
          <el-form :model="configForm" label-width="70px">
            <el-row :gutter="24">
              <el-col :span="6">
                <el-form-item label="是否启用">
                  <el-switch v-model="configForm.status"/>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="支持视觉">
                  <el-switch v-model="configForm.supportVision"/>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="置顶模型">
                  <el-switch v-model="configForm.isPin"/>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="开启日志">
                  <el-switch v-model="configForm.isLog"/>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>
      </div>


      <!-- 底部操作按钮 -->
      <template #footer>
        <div class="drawer-footer">
          <el-button @click="configDrawerVisible = false">取消更改</el-button>
          <el-button type="primary" @click="handleSaveConfig">保存配置</el-button>
        </div>
      </template>
    </el-drawer>

    <!-- 【页面主体下方】翻页器 -->
    <div style="display: flex; justify-content: center; align-items: center;">
      <el-pagination
          v-model:current-page="pageInfo.currentPageNum"
          v-model:page-size="pageInfo.currentPageSize"
          :total="filteredModelNumber"
          :page-sizes="[12, 16, 20, 24]"
          size="small"
          :background="true"
          layout='total, sizes, prev, pager, next, jumper'
      />
    </div>

  </div>
</template>

<script setup lang="ts">

import {reactive, ref, computed} from 'vue'
import {ElMessage} from 'element-plus'
import axios from "axios";
import {useModelListStore} from '@/store/modelList'
import {storeToRefs} from 'pinia'

/** ═══════════ 从pinia中获取全量的模型状态 ═══════════ */
// 这里的useModelListStore()会返回一个对象，对象中包含了totalModelNumber和freeModelNumber两个属性
// 这里用storeToRefs()来将对象转换为响应式数据
// 相比toRefs()，这里只对useModelListStore()这个对象的数据进行响应式处理，而不会对其中的actions等进行响应式处理
const modelList = useModelListStore()
const {totalModelList,totalModelNumber,freeModelNumber} = storeToRefs(modelList)

/** ═══════════ 模型广场相关 ═══════════ */

// 当前页面的模型信息
const pageInfo = reactive({
  currentPageNum: 1,
  currentPageSize: 12,
  currentModelName: ""
})


// 根据搜索关键字过滤后的模型列表
const filteredModelList = computed(() => {
  const keyword = pageInfo.currentModelName.trim().toLowerCase()
  if (!keyword) {
    return totalModelList.value
  }
  return totalModelList.value.filter(model =>
    model.name.toLowerCase().includes(keyword)
  )
})

// 当前页的模型数量（过滤后的总数）
const filteredModelNumber = computed(() => filteredModelList.value.length)

// 当前页的模型列表（分页切片）
const currentPageModels = computed(() => {
  const start = (pageInfo.currentPageNum - 1) * pageInfo.currentPageSize
  const end = start + pageInfo.currentPageSize
  return filteredModelList.value.slice(start, end)
})


/** ═══════════ 模型配置相关 ═══════════ */

// 配置弹窗相关状态
const configDrawerVisible = ref(false)  // 配置弹窗是否可见
const currentModel = ref<any>(null)  // 当前正在选中的模型是哪一个

// 配置表单数据
const configForm = reactive({
  name: '',
  modelGroup: '',
  label: '',
  channels: '',
  isRequestMode: false,
  perRequestPrice: 0,
  inputPrice: 0,
  cachePrice: 0,
  outputPrice: 0,
  isPin: false,
  isLog: false,
  status: false,
  supportVision: false,
  contextLength: 128,
  maxTokens: 4196,
})

// 管理员配置模型：打开弹窗并回填当前模型数据
const adminModelConfig = (model: any) => {
  currentModel.value = model
  // 将模型的现有配置回填到表单
  Object.assign(configForm, {
    name: model.name ?? '',
    modelGroup: model.modelGroup ?? '',
    label: model.label ?? '',
    channels: model.channels ?? '',
    isRequestMode: model.isRequestMode ?? false,
    perRequestPrice: model.perRequestPrice ?? 0,
    inputPrice: model.inputPrice ?? 0,
    cachePrice: model.cachePrice ?? 0,
    outputPrice: model.outputPrice ?? 0,
    isPin: model.isPin ?? false,
    isLog: model.isLog ?? false,
    status: model.status ?? false,
    supportVision: model.supportVision ?? false,
    contextLength: model.contextLength ?? 128,
    maxTokens: model.maxTokens ?? 4196,
  })
  configDrawerVisible.value = true
}

// 保存配置：将表单数据通过axios发送到后端
const handleSaveConfig = () => {
  const modelName = currentModel.value.name
  axios.put(`api/models/put?model_name=${encodeURIComponent(modelName)}`, {
    model_group: configForm.modelGroup,
    label: configForm.label,
    channels: configForm.channels,
    is_request_mode: configForm.isRequestMode,
    per_request_price: configForm.perRequestPrice,
    input_price: configForm.inputPrice,
    cache_price: configForm.cachePrice,
    output_price: configForm.outputPrice,
    is_pin: configForm.isPin,
    is_log: configForm.isLog,
    status: configForm.status,
    support_vision: configForm.supportVision,
    context_length: configForm.contextLength,
    max_tokens: configForm.maxTokens,
  }).then(
      res => {
        console.log(res.data) // 打印一下后端返回的结果
        configDrawerVisible.value = false
        modelList.loadTotalModels() // 刷新当前页的模型列表
        ElMessage.success('配置保存成功')
      }
  )
}

/** ═══════════ 其他功能相关 ═══════════ */

// 复制模型名称到剪贴板
const copyModelName = (modelName: string) => {
  navigator.clipboard.writeText(modelName)
  // 提示用户复制成功
  ElMessage.success('模型名称已复制')
}

// 拨测模型连接
const testConnection = (modelName: string) => {
  // TODO:这里需要实现一个拨测模型连接的函数
  // 模拟拨测连接
  ElMessage.success('模型连接测试成功')
}


</script>

<style scoped>

.models-page {
  height: 100%;
  overflow-y: auto;
  padding: 20px;
}

h1 {
  text-align: center;
}

.model-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}

.model-item {
  /* =========这里修改后，可以改变每一行的卡片个数，例如目前是30%，每行展示3个 */
  width: 22%;
  margin: 5px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 10px;
}

.model-item h2 {
  margin-bottom: 10px;
}

.config-drawer-content {
  padding: 0 10px;
}

.config-section {
  margin-bottom: 12px;
}

.config-section h4 {
  margin-bottom: 1px;
  color: #303133;
  font-weight: 500;
}

.config-section p {
  margin: 10px 0;
  color: #606266;
}

.unit {
  margin-left: 8px;
  color: #909399;
  font-size: 13px;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>