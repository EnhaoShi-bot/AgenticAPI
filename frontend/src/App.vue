<script setup lang="ts">
import { onMounted } from 'vue'
import zhCN from '@arco-design/web-vue/es/locale/lang/zh-cn'
import { useModelListStore } from '@/stores/modelList'
import { useUserStore } from '@/stores/user'
import AppHeader from '@/layouts/AppHeader.vue'

// 挂载的时候，加载模型列表，这样不管用户从哪个页面进入，都能看到最新的模型列表
const modelListStore = useModelListStore()
onMounted(() => {
  modelListStore.loadTotalModels()
})

// 若本地存有令牌，拉取一次用户信息（校验令牌有效性，并回填导航栏显示的昵称）
const userStore = useUserStore()
onMounted(() => {
  userStore.fetchUserInfo()
})
</script>


<template>
  <!-- 中文 locale 提供给 Arco 组件（弹窗按钮文案、分页等） -->
  <a-config-provider :locale="zhCN">
    <AppHeader/>

    <!-- 【页面】页面内容区域（路由实现） -->
    <main class="app-main">
      <RouterView></RouterView>
    </main>
  </a-config-provider>
</template>


<style scoped>
/* 页面内容区域 */
.app-main {
  width: 100%;
  height: calc(100vh - var(--layout-header-height));
  overflow: hidden;
}
</style>
