<!-- 首页 -->
<template>
  <div class="page-container" ref="containerRef">
    <!-- 区块1：欢迎页 -->
    <section class="section">
      <h1>欢迎来到 Agentic API</h1>
      <p>这是一个基于 Vue 3 的 API 平台，用于构建和管理 API。</p>
    </section>

    <!-- 区块2：模型广场介绍 -->
    <section class="section">
      <h2>看一看有哪些可用的大模型？</h2>
      <hr>
      <p>当前模型数量：{{ modelListStore.totalModelNumber }}</p>
      <p>当前免费模型数量：{{ modelListStore.freeModelNumber }}</p>
      <button class="btn btn-sm action-btn" @click="goToModelsPage">查看模型列表</button>
    </section>

    <!-- 区块3：配置路由模型介绍 -->
    <section class="section">
      <h2>设计自己的路由模型</h2>
      <hr>
      <button class="btn btn-sm action-btn" @click="goToRoutesPage">设计自己的路由模型</button>
    </section>

    <!-- 区块4：一个大模型实验室 -->
    <section class="section">
      <h2>测试一下模型效果</h2>
      <hr>
      <button class="btn btn-sm action-btn" @click="goToStudioPage">测试一下模型效果</button>
    </section>
    <!-- 区块5：用户控制台 -->
    <section class="section">
      <h2>在控制台中，你可以管理上游渠道与查看用量统计</h2>
      <hr>
      <button class="btn btn-sm action-btn" @click="goToDashboardPage">用户控制台</button>
    </section>
    <!-- 区块6：查看API文档 -->
    <section class="section">
      <h2>查看更多文档</h2>
      <hr>
      <button class="btn btn-sm action-btn" @click="goToDocsPage">查看API文档</button>
    </section>
  </div>
</template>

<script setup lang="ts">
import {ref, onMounted, onUnmounted} from 'vue'
import {useModelListStore} from '@/store/modelList'

const modelListStore = useModelListStore()

// 编程式路由
import {useRouter} from 'vue-router'

const router = useRouter()

// 路由跳转函数
const goToModelsPage = () => {
  router.push({name: 'Models'})
}
const goToRoutesPage = () => {
  router.push({name: 'Routes'})
}
const goToStudioPage = () => {
  router.push({name: 'Studio'})
}
const goToDashboardPage = () => {
  router.push({name: 'Dashboard'})
}
const goToDocsPage = () => {
  router.push({name: 'Docs'})
}


const containerRef = ref<HTMLDivElement | null>(null)
// 当前页码
const currentIndex = ref(0)
// 总页数 = section数量
const totalPage = ref(6)
// 锁，防止连续滚动触发多次
const isScrolling = ref(false)

// 滚动到指定页面
const scrollToPage = (index: number) => {
  if (isScrolling.value) return
  if (index < 0 || index >= totalPage.value) return

  isScrolling.value = true
  currentIndex.value = index

  // 使用容器的实际高度而不是 window.innerHeight
  const containerHeight = containerRef.value?.clientHeight || window.innerHeight
  const targetTop = index * containerHeight
  if (containerRef.value) {
    containerRef.value.scrollTo({
      top: targetTop,
      behavior: 'smooth'
    })
  }

  // 动画结束后解锁
  setTimeout(() => {
    isScrolling.value = false
  }, 800)
}

// 滚轮事件处理
const handleWheel = (e: WheelEvent) => {
  e.preventDefault()
  if (isScrolling.value) return

  if (e.deltaY > 10) {
    // 向下滚动 → 下一页
    scrollToPage(currentIndex.value + 1)
  } else if (e.deltaY < -10) {
    // 向上滚动 → 上一页
    scrollToPage(currentIndex.value - 1)
  }
}

// 触摸移动端支持
let touchStartY = 0
const handleTouchStart = (e: TouchEvent) => {
  const touch = e.touches[0]
  if (!touch) return
  touchStartY = touch.clientY
}
const handleTouchMove = (e: TouchEvent) => {
  e.preventDefault()
  if (isScrolling.value) return
  const touch = e.touches[0]
  if (!touch) return
  const touchY = touch.clientY
  const diff = touchY - touchStartY

  if (diff < -40) {
    scrollToPage(currentIndex.value + 1)
  } else if (diff > 40) {
    scrollToPage(currentIndex.value - 1)
  }
}

onMounted(() => {
  const dom = containerRef.value
  if (!dom) return
  // passive:false 才能调用 e.preventDefault()
  dom.addEventListener('wheel', handleWheel, {passive: false})
  dom.addEventListener('touchstart', handleTouchStart)
  dom.addEventListener('touchmove', handleTouchMove, {passive: false})
})

onUnmounted(() => {
  const dom = containerRef.value
  if (!dom) return
  dom.removeEventListener('wheel', handleWheel)
  dom.removeEventListener('touchstart', handleTouchStart)
  dom.removeEventListener('touchmove', handleTouchMove)
})
</script>

<style scoped>
.page-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  scroll-behavior: auto;
  /* 滚动动画交给JS控制 */
}

.section {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  gap: 16px;
}

/* 给每个区块区分背景，方便调试预览，可以自行删掉 */
.section:nth-child(1) {
  background: #222;
  color: #fff;
}

.section:nth-child(2) {
  background: #f5f5f5;
  color: #222;
}

.section:nth-child(3) {
  background: #e8f4ff;
  color: #222;
}

.section:nth-child(4) {
  background: #f0f8f0;
  color: #222;
}

.section:nth-child(5) {
  background: #fff3e8;
  color: #222;
}

.section:nth-child(6) {
  background: #222;
  color: #fff;
}

/* ── 操作按钮：统一外观，不同按压反馈 ── */
.action-btn {
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
  padding: 8px 16px;
  font-size: 18px;
  cursor: pointer;
}

.action-btn:hover {
  border-color: transparent;
}

.action-btn:active {
  transform: scale(0.96);
}

hr {
  width: 120px;
}
</style>