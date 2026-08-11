<!-- 控制台 -->

<template>
  <div class="dashboard-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2 class="sidebar-title">控制台</h2>
      </div>
      <nav class="sidebar-nav" aria-label="控制台导航">
        <ul class="sidebar-nav-list">
          <li v-for="item in dashItems" :key="item.id">
            <RouterLink 
              :to="item.to" 
              class="sidebar-nav-link"
              :class="{ active: isActive(item.to) }"
            >
              {{ item.name }}
            </RouterLink>
          </li>
        </ul>
      </nav>
    </aside>

    <!-- 主内容区域 -->
    <main class="dashboard-main">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const dashItems = [
  { id: 1, name: '概览', to: '/dashboard/overview' },
  { id: 2, name: '秘钥', to: '/dashboard/keys' },
  { id: 3, name: '渠道', to: '/dashboard/channels' },
  { id: 4, name: '用户', to: '/dashboard/userlist' },
  { id: 5, name: '兑换', to: '/dashboard/redemptioncodes' },
  { id: 6, name: '运营', to: '/dashboard/operations' },
  { id: 7, name: '安全', to: '/dashboard/security' },
]

const isActive = (path: string) => {
  return route.path === path
}
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  height: calc(100vh - 48px);
}

/* 侧边栏 */
.sidebar {
  /* 侧边栏宽度 */
  width: 160px;
  background-color: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.sidebar-title {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--color-text);
  margin: 0;
}

.sidebar-nav {
  flex: 1;
  padding: var(--space-2) 0;
  overflow-y: auto;
}

.sidebar-nav-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.sidebar-nav-list li {
  margin: 0;
}

.sidebar-nav-link {
  display: block;
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
  border-left: 3px solid transparent;
}

.sidebar-nav-link:hover {
  color: var(--color-text);
  background-color: var(--color-gray-100);
  border-left-color: var(--color-border);
}

.sidebar-nav-link.active {
  color: var(--color-primary);
  background-color: rgba(37, 99, 235, 0.08);
  border-left-color: var(--color-primary);
  font-weight: var(--font-semibold);
}

/* 主内容区域 */
.dashboard-main {
  flex: 1;
  padding: var(--space-6);
  overflow-y: auto;
  background-color: var(--color-bg);
}

@media (max-width: 768px) {
  .sidebar {
    width: 200px;
  }
  
  .dashboard-main {
    padding: var(--space-4);
  }
}
</style>