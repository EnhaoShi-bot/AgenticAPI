<script setup lang="ts">
import {onMounted} from 'vue'
import {useModelListStore} from '@/stores/modelList'
import AppHeader from '@/layouts/AppHeader.vue'

// 挂载的时候，加载模型列表，这样不管用户从哪个页面进入，都能看到最新的模型列表
const modelListStore = useModelListStore()
onMounted(() => {
  modelListStore.loadTotalModels()
})


</script>


<template>
  <AppHeader/>

  <!-- 【页面】页面内容区域（路由实现） -->
  <main class="app-main">
    <RouterView></RouterView>
  </main>
</template>


<style scoped>
/* 页面内容区域 */
.app-main {
  width: 100%;
  height: calc(100vh - 48px);
  overflow: hidden;
}
</style>
