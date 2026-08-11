<script setup lang="ts">
import {ref, watch} from 'vue'
import {useRoute} from 'vue-router'
import logoImage from '../public/example.jpg'

// 导航栏数据
const navItems = [
  {id: '001', label: '首页', to: '/home'},
  {id: '002', label: '模型广场', to: '/models'},
  {id: '003', label: '路由模型', to: '/routes'},
  {id: '004', label: '模型工坊', to: '/studio'},
  {id: '005', label: '控制台', to: '/dashboard'},
  {id: '006', label: '文档', to: '/docs'},
]

// 监听路由变化
const route = useRoute()
const updateActiveIndex = () => {
  const currentPath = route.path
  const index = navItems.findIndex(item => {
    // 精确匹配
    if (item.to === currentPath) return true
    // 前缀匹配：当前路径以导航路径开头，且导航路径是 /dashboard 这种有子路由的情况
    return (item.to !== '/' && currentPath.startsWith(item.to + '/'));
  })
  if (index !== -1) {
    activeIndex.value = index
  }
}
watch(() => route.path, updateActiveIndex, {immediate: true})


const activeIndex = ref(0)
</script>


<template>
  <!-- 【导航栏】最顶部导航栏区域 -->
  <header class="app-header">
    <div class="header-inner container flex-between">
      <!-- 【导航栏左侧】品牌与LOGO -->
      <a class="header-brand" href="#home">
        <img class="brand-logo-img" :src="logoImage" alt="AgenticAPI Logo"/>
        <span class="brand-text">AgenticAPI</span>
      </a>

      <!-- 【导航栏居中】导航菜单 -->
      <nav class="header-nav" aria-label="主导航">
        <ul class="nav-list">
          <li v-for="(item, index) in navItems" :key="item.id">
            <RouterLink :to="item.to" class="nav-link" :class="{ active: activeIndex === index }">
              {{ item.label }}
            </RouterLink>
          </li>
        </ul>
      </nav>

      <!-- 【导航栏右侧】右侧操作区 -->
      <div class="header-actions">
        <button class="btn btn-sm action-btn action-btn-register">注册</button>
        <button class="btn btn-sm action-btn action-btn-login">登录</button>
        <button class="btn btn-sm action-btn action-btn-guest">访客</button>
      </div>
    </div>
  </header>

  <!-- 【页面】页面内容区域（路由实现） -->
  <main class="app-main">
    <RouterView></RouterView>
  </main>
</template>


<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background-color: var(--color-white);
  border-bottom: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.header-inner {
  height: 48px;
}

/* 品牌区 */
.header-brand {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  text-decoration: none;
  color: var(--color-text);
  font-weight: var(--font-bold);
  font-size: var(--text-lg);
  transition: opacity var(--transition-fast);
}

.header-brand:hover {
  opacity: 0.8;
}

.brand-logo-img {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-md);
  object-fit: cover;
}

.brand-text {
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  font-size: 1.25rem;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* 导航菜单 */
.header-nav {
  display: none;
}

@media (min-width: 768px) {
  .header-nav {
    display: block;
  }
}

.nav-list {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-link {
  display: block;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  text-decoration: none;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.nav-link:hover {
  color: var(--color-text);
  background-color: var(--color-gray-100);
}

.nav-link.active {
  color: var(--color-primary);
  background-color: rgba(37, 99, 235, 0.08);
}

/* 右侧操作 */
.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

/* ── 操作按钮：统一外观，不同按压反馈 ── */
.action-btn {
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.action-btn:hover {
  border-color: transparent;
}

.action-btn:active {
  color: #fff;
  transform: scale(0.96);
}

/* 注册 — 蓝色系 */
.action-btn-register:hover {
  background-color: rgba(37, 99, 235, 0.08);
  color: var(--color-primary);
}

.action-btn-register:active {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

/* 登录 — 琥珀色系 */
.action-btn-login:hover {
  background-color: rgba(245, 158, 11, 0.08);
  color: var(--color-accent-dark);
}

.action-btn-login:active {
  background-color: var(--color-accent);
  border-color: var(--color-accent);
}

/* 访客 — 青色系 */
.action-btn-guest:hover {
  background-color: rgba(8, 145, 178, 0.08);
  color: var(--color-info);
}

.action-btn-guest:active {
  background-color: var(--color-info);
  border-color: var(--color-info);
}

/* 页面内容区域 */
.app-main {
  width: 100%;
  height: calc(100vh - 48px);
  overflow: hidden;
}
</style>