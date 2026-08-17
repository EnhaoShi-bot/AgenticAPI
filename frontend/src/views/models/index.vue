<!-- 模型广场：卡片网格 + lobehub 模型图标，详情/示例/配置抽屉 -->

<template>
  <div class="models-page">
    <!-- 【页面顶部】标题、描述、搜索框 -->
    <header class="page-head models-head">
      <h1>模型广场</h1>
      <p class="page-head-desc">
        本站已启用 <span class="models-count">{{ totalModelNumber }}</span> 个模型，含
        <span class="models-count models-count-free">{{ freeModelNumber }}</span> 个免费模型
      </p>
      <div class="models-toolbar">
        <a-input-search
            v-model="pageInfo.currentModelName"
            class="models-search"
            placeholder="搜索模型名称，回车确认"
            allow-clear
            search-button
            @search="pageInfo.currentPageNum = 1"
            @clear="pageInfo.currentModelName = ''; pageInfo.currentPageNum = 1"
        />
        <!-- 添加模型属于管理操作，仅管理员可见 -->
        <a-button v-if="userStore.isAdmin" type="primary" @click="openAddModelDrawer">
          <template #icon><icon-plus/></template>
          添加模型
        </a-button>
      </div>
    </header>

    <!-- 【页面主体】模型卡片网格 -->
    <div class="model-list">
      <!-- 【模型列表】每一张模型卡片 -->
      <div v-for="model in currentPageModels" :key="model.name" class="model-card">
        <!-- 卡片头：图标 + 名称与标签 + 操作 -->
        <div class="model-card-head">
          <div class="model-icon-box">
            <LobeIcon :name="model.icon" :fallback="model.name" :size="24"/>
          </div>
          <div class="model-title-wrap">
            <div class="model-name" :title="model.name">{{ model.name }}</div>
            <div class="model-tags">
              <a-tag :color="groupTagColor(model.modelGroup)" size="small">
                {{ model.modelGroup === 'free' ? '免费分组' : model.modelGroup }}
              </a-tag>
              <a-tag v-for="tag in splitLabel(model.label).slice(0, 2)" :key="tag" size="small" :color="tagColorByName(tag)">
                {{ tag }}
              </a-tag>
              <a-tag v-if="splitLabel(model.label).length > 2" size="small" :color="tagColorByName(model.label)">
                +{{ splitLabel(model.label).length - 2 }}
              </a-tag>
            </div>
          </div>
          <div class="model-actions">
            <a-tooltip content="复制模型名" position="top">
              <a-button type="text" size="mini" @click="copyModelName(model.name)">
                <template #icon><icon-copy/></template>
              </a-button>
            </a-tooltip>
            <a-tooltip content="拨测连接" position="top">
              <a-button type="text" size="mini" @click="testConnection(model.name)">
                <template #icon><icon-sync/></template>
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
            <span v-if="model.isPin" class="model-feature model-feature-pin">置顶</span>
            <span v-if="!model.status" class="model-feature model-feature-off">停用</span>
          </div>
          <a-button type="text" size="mini" @click="openModelDetail(model)">
            详情
            <template #icon><icon-right/></template>
          </a-button>
        </div>
      </div>
    </div>

    <!-- 【翻页器】过滤结果分页展示 -->
    <div v-if="filteredModelNumber > 0" class="models-pagination">
      <a-pagination
          :total="filteredModelNumber"
          v-model:current="pageInfo.currentPageNum"
          v-model:page-size="pageInfo.currentPageSize"
          :page-size-options="[12, 16, 20, 24]"
          show-total
          show-page-size
      />
    </div>
    <a-empty v-else class="models-empty" description="没有匹配的模型"/>


    <!-- 模型详情侧边栏：详情 / 示例 / 配置（配置仅管理员可见） -->
    <a-drawer
        v-model:visible="configDrawerVisible"
        :title="`模型详情：${currentModel?.name || ''}`"
        :width="620"
        :mask-closable="true"
        unmount-on-close
    >
      <a-tabs v-model:active-key="activeDetailTab">
        <!-- ═══════════ 标签1：详情（只读展示，所有用户可见） ═══════════ -->
        <a-tab-pane key="detail" title="详情">
          <a-descriptions :column="2" bordered size="medium">
            <a-descriptions-item label="模型名称" :span="2">
              <span class="detail-model-name">
                <LobeIcon :name="currentModel?.icon" :fallback="currentModel?.name" :size="18"/>
                {{ currentModel?.name }}
              </span>
            </a-descriptions-item>
            <a-descriptions-item label="标签">{{ currentModel?.label || '-' }}</a-descriptions-item>
            <a-descriptions-item label="分组">{{ currentModel?.modelGroup }}</a-descriptions-item>
            <a-descriptions-item label="状态">
              <a-tag :color="currentModel?.status ? 'green' : 'red'" size="small">
                {{ currentModel?.status ? '启用' : '停用' }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="支持视觉">
              <a-tag :color="currentModel?.supportVision ? 'green' : 'gray'" size="small">
                {{ currentModel?.supportVision ? '支持' : '不支持' }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="上下文长度">{{ formatNumber(currentModel?.contextLength) }}</a-descriptions-item>
            <a-descriptions-item label="最大输出">{{ formatNumber(currentModel?.maxTokens) }}</a-descriptions-item>
            <a-descriptions-item label="计费模式" :span="2">
              {{ currentModel?.isRequestMode ? '按次计费' : '按 Token 计费' }}
            </a-descriptions-item>
            <!-- 按计费模式展示价格 -->
            <a-descriptions-item v-if="currentModel?.isRequestMode" label="每请求价格" :span="2">
              {{ currentModel?.perRequestPrice }} 元/次
            </a-descriptions-item>
            <template v-else>
              <a-descriptions-item label="输入价格">{{ currentModel?.inputPrice }} 元/1M</a-descriptions-item>
              <a-descriptions-item label="缓存价格">{{ currentModel?.cachePrice }} 元/1M</a-descriptions-item>
              <a-descriptions-item label="输出价格" :span="2">{{ currentModel?.outputPrice }} 元/1M</a-descriptions-item>
            </template>
            <a-descriptions-item label="可用渠道" :span="2">
              {{ currentModel?.channels?.length ? currentModel.channels.join('、') : '未绑定渠道' }}
            </a-descriptions-item>
            <a-descriptions-item label="模型描述" :span="2">{{ currentModel?.description || '-' }}</a-descriptions-item>
          </a-descriptions>
        </a-tab-pane>

        <!-- ═══════════ 标签2：示例（按模型生成 curl 调用示例，所有用户可见） ═══════════ -->
        <a-tab-pane key="example" title="示例">
          <p class="example-tip">
            把下面的密钥换成你自己的 API 密钥（控制台-秘钥页面创建），即可直接调用
            {{ currentModel?.name }}。支持 OpenAI SDK，把 base_url 指向
            <code>http://localhost:2027/v1</code> 即可。
          </p>
          <pre class="example-code">{{ exampleCurl }}</pre>
          <a-button size="small" @click="copyExampleCurl">
            <template #icon><icon-copy/></template>
            复制示例
          </a-button>
        </a-tab-pane>

        <!-- ═══════════ 标签3：配置（仅管理员可见） ═══════════ -->
        <a-tab-pane v-if="userStore.isAdmin" key="config" title="配置">
          <!-- 模型基本信息配置 -->
          <div class="config-section">
            <h5>基本信息</h5>
            <a-form :model="configForm" layout="vertical">
              <a-form-item label="模型分组">
                <a-input v-model="configForm.modelGroup" placeholder="请输入模型分组"/>
              </a-form-item>
              <a-form-item label="模型标签">
                <a-input v-model="configForm.label" placeholder="请输入模型标签，多个用英文逗号分隔"/>
              </a-form-item>
              <a-form-item label="模型图标">
                <div class="icon-field">
                  <div class="icon-field-preview">
                    <LobeIcon :name="configForm.icon" fallback="?" :size="24"/>
                  </div>
                  <a-input v-model="configForm.icon" placeholder="lobehub 图标名，如 Qwen / OpenAI / Claude.Color，或图片链接"/>
                </div>
              </a-form-item>
              <a-form-item label="模型描述">
                <a-input v-model="configForm.description" placeholder="请输入模型描述"/>
              </a-form-item>
              <a-form-item label="渠道配置">
                <a-select
                    v-model="configForm.channels"
                    multiple
                    allow-clear
                    :max-tag-count="3"
                    placeholder="选择该模型可用的渠道"
                >
                  <a-option v-for="name in channelNameList" :key="name" :value="name" :label="name"/>
                </a-select>
              </a-form-item>
              <a-form-item label="上下文长度">
                <a-input-number v-model="configForm.contextLength" :min="1" placeholder="上下文长度" hide-button/>
              </a-form-item>
              <a-form-item label="最大输出长度">
                <a-input-number v-model="configForm.maxTokens" :min="1" placeholder="最大输出长度" hide-button/>
              </a-form-item>
            </a-form>
          </div>

          <a-divider/>

          <!-- 价格配置 -->
          <div class="config-section">
            <h5>价格配置</h5>
            <a-form :model="configForm" layout="vertical">
              <a-form-item label="计费模式">
                <a-switch v-model="configForm.isRequestMode"/>
                <span class="switch-hint">{{ configForm.isRequestMode ? '按请求计费' : '按 Token 计费' }}</span>
              </a-form-item>

              <a-form-item v-if="configForm.isRequestMode" label="每请求价格">
                <a-input-number v-model="configForm.perRequestPrice" :precision="4" :step="0.1" :min="0"/>
                <span class="unit">元/次</span>
              </a-form-item>

              <template v-else>
                <a-form-item label="输入价格">
                  <a-input-number v-model="configForm.inputPrice" :precision="4" :step="0.1" :min="0"/>
                  <span class="unit">元/1M</span>
                </a-form-item>
                <a-form-item label="缓存价格">
                  <a-input-number v-model="configForm.cachePrice" :precision="4" :step="0.1" :min="0"/>
                  <span class="unit">元/1M</span>
                </a-form-item>
                <a-form-item label="输出价格">
                  <a-input-number v-model="configForm.outputPrice" :precision="4" :step="0.1" :min="0"/>
                  <span class="unit">元/1M</span>
                </a-form-item>
              </template>
            </a-form>
          </div>

          <a-divider/>

          <!-- 开关配置 -->
          <div class="config-section">
            <h5>功能开关</h5>
            <div class="switch-grid">
              <div class="switch-cell">
                <span>是否启用</span>
                <a-switch v-model="configForm.status"/>
              </div>
              <div class="switch-cell">
                <span>支持视觉</span>
                <a-switch v-model="configForm.supportVision"/>
              </div>
              <div class="switch-cell">
                <span>置顶模型</span>
                <a-switch v-model="configForm.isPin"/>
              </div>
              <div class="switch-cell">
                <span>开启日志</span>
                <a-switch v-model="configForm.isLog"/>
              </div>
            </div>
          </div>
        </a-tab-pane>
      </a-tabs>


      <!-- 底部操作按钮（保存/删除针对的是"配置"标签，仅管理员可见） -->
      <template #footer>
        <div v-if="userStore.isAdmin" class="drawer-footer">
          <a-button status="danger" @click="handleDeleteModel">删除模型</a-button>
          <div class="drawer-footer-spacer"></div>
          <a-button @click="configDrawerVisible = false">取消更改</a-button>
          <a-button type="primary" @click="handleSaveConfig">保存配置</a-button>
        </div>
      </template>
    </a-drawer>

    <!-- 添加模型侧边栏 -->
    <a-drawer
        v-model:visible="addModelDrawerVisible"
        title="添加新模型"
        :width="620"
        :mask-closable="true"
        unmount-on-close
    >
      <!-- 模型基本信息 -->
      <div class="config-section">
        <h5>基本信息</h5>
        <a-form :model="addModelForm" layout="vertical">
          <a-form-item label="模型名称" required>
            <a-input v-model="addModelForm.name" placeholder="例如: gpt-4 (字符串类型)"/>
          </a-form-item>
          <a-form-item label="模型分组">
            <a-input v-model="addModelForm.modelGroup" placeholder="例如: OpenAI (字符串类型)"/>
          </a-form-item>
          <a-form-item label="模型标签">
            <a-input v-model="addModelForm.label" placeholder="例如: 旗舰,对话 (字符串类型)"/>
          </a-form-item>
          <a-form-item label="模型图标">
            <div class="icon-field">
              <div class="icon-field-preview">
                <LobeIcon :name="addModelForm.icon" fallback="?" :size="24"/>
              </div>
              <a-input v-model="addModelForm.icon" placeholder="lobehub 图标名，如 Qwen / OpenAI / Claude.Color，或图片链接"/>
            </div>
          </a-form-item>
          <a-form-item label="模型描述">
            <a-input v-model="addModelForm.description" placeholder="例如: OpenAI最强模型 (字符串类型)"/>
          </a-form-item>
          <a-form-item label="渠道配置">
            <a-select
                v-model="addModelForm.channels"
                multiple
                allow-clear
                :max-tag-count="3"
                placeholder="选择该模型可用的渠道"
            >
              <a-option v-for="name in channelNameList" :key="name" :value="name" :label="name"/>
            </a-select>
          </a-form-item>
          <a-form-item label="上下文长度">
            <a-input-number v-model="addModelForm.contextLength" :min="1" placeholder="例如: 128 (整数类型)" hide-button/>
          </a-form-item>
          <a-form-item label="最大输出长度">
            <a-input-number v-model="addModelForm.maxTokens" :min="1" placeholder="例如: 4096 (整数类型)" hide-button/>
          </a-form-item>
        </a-form>
      </div>

      <a-divider/>

      <!-- 价格配置 -->
      <div class="config-section">
        <h5>价格配置</h5>
        <a-form :model="addModelForm" layout="vertical">
          <a-form-item label="计费模式">
            <a-switch v-model="addModelForm.isRequestMode"/>
            <span class="switch-hint">{{ addModelForm.isRequestMode ? '按请求计费' : '按 Token 计费' }}</span>
          </a-form-item>

          <a-form-item v-if="addModelForm.isRequestMode" label="每请求价格">
            <a-input-number v-model="addModelForm.perRequestPrice" :precision="4" :step="0.1" :min="0"/>
            <span class="unit">元/次</span>
          </a-form-item>

          <template v-else>
            <a-form-item label="输入价格">
              <a-input-number v-model="addModelForm.inputPrice" :precision="4" :step="0.1" :min="0"/>
              <span class="unit">元/1M</span>
            </a-form-item>
            <a-form-item label="缓存价格">
              <a-input-number v-model="addModelForm.cachePrice" :precision="4" :step="0.1" :min="0"/>
              <span class="unit">元/1M</span>
            </a-form-item>
            <a-form-item label="输出价格">
              <a-input-number v-model="addModelForm.outputPrice" :precision="4" :step="0.1" :min="0"/>
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
            <a-switch v-model="addModelForm.status"/>
          </div>
          <div class="switch-cell">
            <span>支持视觉</span>
            <a-switch v-model="addModelForm.supportVision"/>
          </div>
          <div class="switch-cell">
            <span>置顶模型</span>
            <a-switch v-model="addModelForm.isPin"/>
          </div>
          <div class="switch-cell">
            <span>开启日志</span>
            <a-switch v-model="addModelForm.isLog"/>
          </div>
        </div>
      </div>

      <!-- 底部操作按钮 -->
      <template #footer>
        <div class="drawer-footer">
          <a-button @click="addModelDrawerVisible = false">取消</a-button>
          <a-button type="primary" @click="handleAddModel">添加模型</a-button>
        </div>
      </template>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">

import {reactive, ref, computed, watch, onMounted} from 'vue'
import {Message} from '@arco-design/web-vue'
import {addModel, updateModel, deleteModel} from '@/api/models'
import {getErrorMessage} from '@/api/request'
import {useModelListStore} from '@/stores/modelList'
import {useChannelListStore} from '@/stores/channelList'
import {useUserStore} from '@/stores/user'
import {confirmDialog} from '@/utils/feedback'
import {tagColorByName} from '@/utils/colors'
import {storeToRefs} from 'pinia'
import LobeIcon from '@/components/common/LobeIcon.vue'

/** ═══════════ 从pinia中获取全量的模型状态 ═══════════ */
// 这里的useModelListStore()会返回一个对象，对象中包含了totalModelNumber和freeModelNumber两个属性
// 这里用storeToRefs()来将对象转换为响应式数据
// 相比toRefs()，这里只对useModelListStore()这个对象的数据进行响应式处理，而不会对其中的actions等进行响应式处理
const modelList = useModelListStore()
const {totalModelList,totalModelNumber,freeModelNumber} = storeToRefs(modelList)

/** ═══════════ 从pinia中获取全量的渠道状态 ═══════════ */
const channelList = useChannelListStore()
const {channelNameList} = storeToRefs(channelList)

/** ═══════════ 当前登录用户状态（区分管理员/普通用户） ═══════════ */
const userStore = useUserStore()

/** ═══════════ 模型广场相关 ═══════════ */

// 当前页面的模型信息
const pageInfo = reactive({
  currentPageNum: 1,
  currentPageSize: 12,
  currentModelName: ""
})

// 分组标签配色：免费绿色、VIP 橙色，其余主色
function groupTagColor(group: string): string {
  if (group === 'free') return 'green'
  if (group === 'vip') return 'orangered'
  return 'arcoblue'
}

// 标签字段按逗号拆分（"旗舰,对话" → ["旗舰","对话"]）
function splitLabel(label: string | null | undefined): string[] {
  return (label || '').split(/[,，]/).map(s => s.trim()).filter(Boolean)
}


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

// 过滤结果变少时收拢页码，避免停留在超出范围的空页
watch(filteredModelNumber, (total) => {
  const maxPage = Math.max(1, Math.ceil(total / pageInfo.currentPageSize))
  if (pageInfo.currentPageNum > maxPage) {
    pageInfo.currentPageNum = maxPage
  }
})


/** ═══════════ 模型详情/配置相关 ═══════════ */

// 详情抽屉相关状态
const configDrawerVisible = ref(false)  // 详情抽屉是否可见
const currentModel = ref<any>(null)  // 当前正在选中的模型是哪一个
const activeDetailTab = ref('detail')  // 详情抽屉当前激活的标签页：detail / example / config

// 添加模型弹窗相关状态
const addModelDrawerVisible = ref(false)  // 添加模型弹窗是否可见

// 添加模型表单数据
const addModelForm = reactive({
  name: '',
  modelGroup: '',
  label: '',
  icon: '',
  channels: [],
  description: '',
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

// 打开添加模型弹窗
const openAddModelDrawer = () => {
  // 重置表单数据
  Object.assign(addModelForm, {
    name: '',
    modelGroup: '',
    label: '',
    icon: '',
    channels: [],
    description: '',
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
  addModelDrawerVisible.value = true
}

// 添加模型：将表单数据发送到后端
const handleAddModel = () => {
  if (!addModelForm.name) {
    Message.error('模型名称不能为空')
    return
  }
  addModel({
    name: addModelForm.name,
    modelGroup: addModelForm.modelGroup,
    label: addModelForm.label,
    icon: addModelForm.icon,
    description: addModelForm.description,
    channels: addModelForm.channels,
    isRequestMode: addModelForm.isRequestMode,
    perRequestPrice: addModelForm.perRequestPrice,
    inputPrice: addModelForm.inputPrice,
    cachePrice: addModelForm.cachePrice,
    outputPrice: addModelForm.outputPrice,
    isPin: addModelForm.isPin,
    isLog: addModelForm.isLog,
    status: addModelForm.status,
    supportVision: addModelForm.supportVision,
    contextLength: addModelForm.contextLength,
    maxTokens: addModelForm.maxTokens,
  }).then(
      () => {
        addModelDrawerVisible.value = false
        modelList.loadTotalModels()
        Message.success('模型添加成功')
      }
  ).catch(err => {
    console.error(err)
    Message.error(getErrorMessage(err, '模型添加失败'))
  })
}

// 配置表单数据
const configForm = reactive({
  name: '',
  modelGroup: '',
  label: '',
  icon: '',
  channels: [],
  description: '',
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

// 打开模型详情抽屉：回填当前模型数据，默认落在"详情"标签
const openModelDetail = (model: any) => {
  currentModel.value = model
  activeDetailTab.value = 'detail'
  // 将模型的现有配置回填到表单，确保数字字段类型正确（配置标签使用）
  Object.assign(configForm, {
    name: model.name ?? '',
    modelGroup: model.modelGroup ?? '',
    label: model.label ?? '',
    icon: model.icon ?? '',
    channels: model.channels ?? [],
    isRequestMode: model.isRequestMode ?? false,
    perRequestPrice: parseFloat(model.perRequestPrice) || 0,
    inputPrice: parseFloat(model.inputPrice) || 0,
    cachePrice: parseFloat(model.cachePrice) || 0,
    outputPrice: parseFloat(model.outputPrice) || 0,
    isPin: model.isPin ?? false,
    isLog: model.isLog ?? false,
    status: model.status ?? false,
    supportVision: model.supportVision ?? false,
    contextLength: parseInt(model.contextLength) || 128,
    maxTokens: parseInt(model.maxTokens) || 4196,
    description: model.description ?? '',
  })
  configDrawerVisible.value = true
}

// 保存配置：将表单数据通过axios发送到后端
const handleSaveConfig = () => {
  const modelName = currentModel.value?.name
  if (!modelName) {
    Message.error('未选择模型')
    return
  }
  updateModel(modelName, {
    modelGroup: configForm.modelGroup,
    label: configForm.label,
    icon: configForm.icon,
    description: configForm.description,
    channels: configForm.channels,
    isRequestMode: configForm.isRequestMode,
    perRequestPrice: configForm.perRequestPrice,
    inputPrice: configForm.inputPrice,
    cachePrice: configForm.cachePrice,
    outputPrice: configForm.outputPrice,
    isPin: configForm.isPin,
    isLog: configForm.isLog,
    status: configForm.status,
    supportVision: configForm.supportVision,
    contextLength: configForm.contextLength,
    maxTokens: configForm.maxTokens,
  }).then(
      () => {
        configDrawerVisible.value = false
        modelList.loadTotalModels() // 刷新当前页的模型列表
        Message.success('配置保存成功')
      }
  ).catch(err => {
    console.error(err)
    Message.error(getErrorMessage(err, '配置保存失败'))
  })
}

// 删除模型
const handleDeleteModel = async () => {
  const modelName = currentModel.value?.name
  if (!modelName) {
    Message.error('未选择模型')
    return
  }

  const confirmed = await confirmDialog(
      `确定要删除模型 "${modelName}" 吗？此操作不可恢复。`,
      '删除确认',
      '确定删除',
      true,
  )
  if (!confirmed) return

  try {
    await deleteModel(modelName)
    configDrawerVisible.value = false
    modelList.loadTotalModels()
    Message.success('模型删除成功')
  } catch (err) {
    console.error(err)
    Message.error(getErrorMessage(err, '模型删除失败'))
  }
}

/** ═══════════ 详情/示例标签相关 ═══════════ */

// 数字加千分位（上下文长度、最大输出这类大数字更易读）
const formatNumber = (value: any) => {
  const num = parseInt(value)
  return Number.isFinite(num) ? num.toLocaleString() : '-'
}

// 按当前模型生成 curl 调用示例（随模型不同而不同：模型名、max_tokens、视觉模型的消息结构）
const exampleCurl = computed(() => {
  const model = currentModel.value
  if (!model) return ''

  // max_tokens 取模型上限与1024的较小值，避免示例一跑就顶到上限
  const maxTokens = Math.min(parseInt(model.maxTokens) || 1024, 1024)

  // 视觉模型使用 OpenAI 的多模态消息结构，普通模型用纯文本消息
  const messages = model.supportVision
      ? [{
        role: 'user',
        content: [
          {type: 'text', text: '这张图片里有什么？'},
          {type: 'image_url', image_url: {url: 'https://example.com/image.png'}},
        ],
      }]
      : [{role: 'user', content: '你好，请介绍一下你自己'}]

  const body = JSON.stringify({model: model.name, messages, max_tokens: maxTokens})
  return `curl http://localhost:2027/v1/chat/completions \\\n  -H "Content-Type: application/json" \\\n  -H "Authorization: Bearer sk-你的API密钥" \\\n  -d '${body}'`
})

// 复制 curl 示例
const copyExampleCurl = () => {
  navigator.clipboard.writeText(exampleCurl.value)
  Message.success('示例已复制')
}

/** ═══════════ 其他功能相关 ═══════════ */

// 复制模型名称到剪贴板
const copyModelName = (modelName: string) => {
  navigator.clipboard.writeText(modelName)
  // 提示用户复制成功
  Message.success('模型名称已复制')
}

// 拨测模型连接
const testConnection = (modelName: string) => {
  // TODO:这里需要实现一个拨测模型连接的函数
  // 模拟拨测连接
  Message.success('模型连接测试成功')
}

// 页面加载时拉取渠道列表，供渠道下拉多选使用
onMounted(() => {
  channelList.loadTotalChannels()
})


</script>

<style scoped>
.models-page {
  height: 100%;
  overflow-y: auto;
  padding: var(--space-5) var(--space-5) var(--space-6);
}

/* ── 页面头 ── */
.models-head {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  text-align: center;
  margin-bottom: var(--space-5);
}

.models-head h1 {
  margin: 0;
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
}

.models-count {
  color: var(--color-primary);
  font-weight: var(--font-semibold);
}

.models-count-free {
  color: var(--color-success);
}

.models-toolbar {
  display: flex;
  gap: var(--space-2);
  width: 100%;
  max-width: 520px;
  justify-content: center;
  margin-top: var(--space-2);
}

.models-search {
  max-width: 360px;
  flex: 1;
}

/* ── 卡片网格 ── */
.model-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(268px, 1fr));
  gap: var(--space-3);
}

.model-card {
  display: flex;
  flex-direction: column;
  background-color: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4) var(--space-3);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.model-card:hover {
  border-color: var(--color-primary-light);
  box-shadow: var(--shadow-sm);
}

/* 卡片头 */
.model-card-head {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
}

.model-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
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
  gap: 4px;
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
  gap: var(--space-2);
  margin-top: var(--space-3);
  padding: var(--space-2) var(--space-3);
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
  margin-top: var(--space-3);
}

.model-features {
  display: flex;
  gap: var(--space-2);
}

.model-feature {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0 4px;
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

/* ── 翻页器 ── */
.models-pagination {
  display: flex;
  justify-content: center;
  margin-top: var(--space-5);
}

.models-empty {
  padding: var(--space-12) 0;
}

/* ── 抽屉内表单 ── */
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

/* 示例标签页 */
.example-tip {
  margin: 0 0 12px;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: 1.7;
}

.example-tip code {
  padding: 1px 5px;
  background: var(--color-gray-100);
  border-radius: var(--radius-sm);
}

.example-code {
  padding: 12px;
  margin: 0 0 12px;
  background: var(--color-gray-800);
  color: var(--color-gray-100);
  border-radius: var(--radius-lg);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  line-height: 1.7;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
}

.drawer-footer-spacer {
  flex: 1;
}

/* 详情里的模型名（图标 + 名称） */
.detail-model-name {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-weight: var(--font-medium);
}
</style>
