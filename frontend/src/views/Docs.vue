<!-- 文档 -->

<template>
  <div class="docs-page">
    <!-- 左侧目录 -->
    <aside class="docs-sidebar">
      <div class="sidebar-header">
        <h2 class="sidebar-title">文档</h2>
      </div>
      <nav class="sidebar-nav">
        <ul>
          <li v-for="(doc, index) in docList" :key="doc.path">
            <a 
              :class="{ active: activeIndex === index }" 
              @click="loadDoc(doc.path, index)"
            >
              <span class="nav-icon">
                <svg v-if="activeIndex === index" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              </span>
              <span class="nav-text">{{ doc.title }}</span>
            </a>
          </li>
        </ul>
      </nav>
    </aside>

    <!-- 右侧内容 -->
    <main class="docs-content">
      <div class="content-wrapper">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p class="loading-text">加载中...</p>
        </div>
        <div v-else-if="!renderedContent" class="empty-state">
          <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
          <h3 class="empty-title">选择一篇文档开始阅读</h3>
          <p class="empty-description">从左侧目录中选择一篇文档查看内容</p>
        </div>
        <div v-else class="prose" v-html="renderedContent"></div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import MarkdownIt from 'markdown-it'
import { ref, onMounted } from 'vue'

const md = new MarkdownIt()
const renderedContent = ref('')
const activeIndex = ref<number | null>(null)
const loading = ref(false)

const docList = [
  { title: '快速开始', path: '/docs/getting-started.md' },
  { title: '样式参考', path: '/docs/styles-guide.md' }
]

async function loadDoc(path: string, index: number) {
  loading.value = true
  activeIndex.value = index
  try {
    const res = await fetch(path)
    const text = await res.text()
    renderedContent.value = md.render(text)
  } catch (error) {
    renderedContent.value = ''
    console.error('加载文档失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const firstDoc = docList[0]
  if (firstDoc) {
    loadDoc(firstDoc.path, 0)
  }
})
</script>

<style scoped>
.docs-page {
  display: flex;
  height: 100vh;
  background-color: var(--color-bg);
}

/* ═══════════════════════════════════════════════════════════
   左侧目录
   ═══════════════════════════════════════════════════════════ */

.docs-sidebar {
  /* --------------------↓侧边栏宽度↓-------------------- */
  width: 200px;
  /* --------------------↑侧边栏宽度↑-------------------- */
  background-color: var(--color-gray-50);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text);
  margin: 0;
}

.sidebar-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  background-color: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4) 0;
}

.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-nav li {
  margin: 0;
}

.sidebar-nav a {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-6);
  font-size: var(--text-sm);
  font-weight: var(--font-normal);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  border-left: 3px solid transparent;
}

.sidebar-nav a:hover {
  background-color: var(--color-white);
  color: var(--color-text);
  border-left-color: var(--color-gray-300);
}

.sidebar-nav a.active {
  background-color: var(--color-white);
  color: var(--color-primary);
  font-weight: var(--font-medium);
  border-left-color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: inherit;
}

.nav-text {
  flex: 1;
}

/* ═══════════════════════════════════════════════════════════
   右侧内容区
   ═══════════════════════════════════════════════════════════ */

.docs-content {
  flex: 1;
  background-color: var(--color-white);
  overflow-y: auto;
}

.content-wrapper {
  max-width: var(--container-lg);
  margin: 0 auto;
  padding: var(--space-10) var(--space-12);
}

/* ═══════════════════════════════════════════════════════════
   加载状态
   ═══════════════════════════════════════════════════════════ */

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-20) 0;
}

.loading-text {
  margin-top: var(--space-4);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

/* ═══════════════════════════════════════════════════════════
   空状态
   ═══════════════════════════════════════════════════════════ */

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-20) 0;
  text-align: center;
}

.empty-icon {
  color: var(--color-text-muted);
  margin-bottom: var(--space-6);
}

.empty-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--color-text);
  margin: 0 0 var(--space-2);
}

.empty-description {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  max-width: 400px;
  margin: 0;
}

/* ═══════════════════════════════════════════════════════════
   富文本内容 (v-html)
   ═══════════════════════════════════════════════════════════ */

.prose {
  color: var(--color-text);
  line-height: var(--leading-relaxed);
}

.prose :deep(h1) {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  line-height: var(--leading-tight);
  margin-top: var(--space-12);
  margin-bottom: var(--space-6);
  color: var(--color-text);
}

.prose :deep(h2) {
  font-size: var(--text-3xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-tight);
  margin-top: var(--space-10);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
}

.prose :deep(h3) {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-snug);
  margin-top: var(--space-8);
  margin-bottom: var(--space-3);
  color: var(--color-text);
}

.prose :deep(h4) {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  margin-top: var(--space-6);
  margin-bottom: var(--space-2);
  color: var(--color-text);
}

.prose :deep(p) {
  margin-top: var(--space-4);
  margin-bottom: var(--space-4);
  line-height: var(--leading-relaxed);
}

.prose :deep(a) {
  color: var(--color-primary);
  text-decoration: underline;
  text-underline-offset: 2px;
  transition: color var(--transition-fast);
}

.prose :deep(a:hover) {
  color: var(--color-primary-dark);
}

.prose :deep(strong) {
  font-weight: var(--font-semibold);
  color: var(--color-text);
}

.prose :deep(code) {
  font-family: var(--font-mono);
  font-size: 0.875em;
  padding: 0.2em 0.4em;
  background-color: var(--color-gray-100);
  border-radius: var(--radius-sm);
  color: var(--color-error);
}

.prose :deep(blockquote) {
  margin: var(--space-6) 0;
  padding: var(--space-4) var(--space-6);
  border-left: 4px solid var(--color-primary);
  background-color: var(--color-gray-50);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  color: var(--color-text-secondary);
  font-style: italic;
}

.prose :deep(blockquote p) {
  margin: 0;
}

.prose :deep(ul) {
  margin: var(--space-4) 0;
  padding-left: var(--space-6);
  list-style: disc;
}

.prose :deep(ol) {
  margin: var(--space-4) 0;
  padding-left: var(--space-6);
  list-style: decimal;
}

.prose :deep(li) {
  margin-top: var(--space-1);
  margin-bottom: var(--space-1);
  padding-left: var(--space-1);
}

.prose :deep(hr) {
  border: none;
  border-top: 2px solid var(--color-border);
  margin: var(--space-10) 0;
}

.prose :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-lg);
  margin: var(--space-6) 0;
}

.prose :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: var(--space-6) 0;
  font-size: var(--text-sm);
}

.prose :deep(thead) {
  background-color: var(--color-gray-50);
}

.prose :deep(th) {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-weight: var(--font-semibold);
  border-bottom: 2px solid var(--color-border);
  color: var(--color-text);
}

.prose :deep(td) {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.prose :deep(tbody tr:hover) {
  background-color: var(--color-gray-50);
}

.prose :deep(pre) {
  margin: var(--space-6) 0;
  padding: var(--space-4) var(--space-6);
  background-color: var(--color-gray-900);
  color: #e5e7eb;
  border-radius: var(--radius-lg);
  overflow-x: auto;
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}

.prose :deep(pre code) {
  background: none;
  padding: 0;
  color: inherit;
  font-size: inherit;
}

/* ═══════════════════════════════════════════════════════════
   响应式
   ═══════════════════════════════════════════════════════════ */

@media (max-width: 1024px) {
  .content-wrapper {
    padding: var(--space-8) var(--space-6);
  }
}

@media (max-width: 768px) {
  .docs-page {
    flex-direction: column;
  }

  .docs-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--color-border);
  }

  .content-wrapper {
    padding: var(--space-6) var(--space-4);
  }
}
</style>