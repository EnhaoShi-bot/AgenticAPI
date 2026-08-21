<!-- 添加模型抽屉：复用模型配置表单（含"模型名称"输入），提交校验后把表单数据抛给父级调接口 -->

<template>
  <a-drawer
      v-model:visible="visible"
      title="添加新模型"
      :width="620"
      :mask-closable="true"
      unmount-on-close
  >
    <ModelConfigForm :form="addModelForm" :channel-name-list="channelNameList" show-name/>

    <!-- 底部操作按钮 -->
    <template #footer>
      <div class="drawer-footer">
        <a-button @click="visible = false">取消</a-button>
        <a-button type="primary" @click="handleAdd">添加模型</a-button>
      </div>
    </template>
  </a-drawer>
</template>

<script setup lang="ts">
import {reactive, watch} from 'vue'
import {Message} from '@arco-design/web-vue'
import {createEmptyModelForm} from '@/utils/model'
import ModelConfigForm from '@/components/models/ModelConfigForm.vue'
import type {modelInfoSchema} from '@/types'

defineProps<{
  channelNameList: string[]
}>()

const emit = defineEmits<{ add: [form: modelInfoSchema] }>()

const visible = defineModel<boolean>('visible', {default: false})

// 添加模型表单数据（每次打开抽屉时重置）
const addModelForm = reactive<modelInfoSchema>(createEmptyModelForm())

watch(visible, (visible) => {
  if (visible) Object.assign(addModelForm, createEmptyModelForm())
})

// 添加模型：名称必填，表单快照抛给父级调接口
const handleAdd = () => {
  if (!addModelForm.name) {
    Message.error('模型名称不能为空')
    return
  }
  emit('add', {...addModelForm})
}
</script>

<style scoped>
.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
}
</style>
