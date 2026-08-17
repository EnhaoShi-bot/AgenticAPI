<!-- 首页：六屏整页滑动呈现（滚轮 / 触摸 / 键盘 / 圆点导航），
     每屏一个独立强调色，右侧以真实产品 UI 模拟代替抽象功能卡片 -->
<template>
  <div class="home-page" ref="containerRef">
    <!-- 屏1：Hero -->
    <section class="slide slide-hero" :class="{ 'is-active': currentIndex === 0 }">
      <!-- 静态渐变背景：顶部光束 + 三枚色斑（借鉴 Nexus aurora 光效，不做动画） -->
      <div class="hero-aurora" aria-hidden="true">
        <div class="aurora-blob blob-blue"></div>
        <div class="aurora-blob blob-violet"></div>
        <div class="aurora-blob blob-cyan"></div>
      </div>
      <div class="slide-inner hero-inner">
        <p class="slide-eyebrow">AGENTIC API · 大模型中转站</p>
        <h1 class="hero-title">让 Agent 管理你的<br/><span class="hero-title-key">每一个大模型 API</span></h1>
        <p class="hero-desc">
          OpenAI 兼容接口 · 多渠道自动轮询 · 按量计费 · 用量可视
        </p>
        <div class="hero-actions">
          <a-button type="primary" @click="handleStart">立即开始使用</a-button>
          <a-button @click="goToModelsPage">查看模型广场</a-button>
        </div>

        <!-- 数据速览：等宽数字 + 分隔线，贴近控制台质感 -->
        <div class="hero-metrics">
          <div class="hero-metric">
            <span class="hero-metric-value">{{ modelListStore.totalModelNumber }}</span>
            <span class="hero-metric-label">可用模型</span>
          </div>
          <div class="hero-metric">
            <span class="hero-metric-value">{{ modelListStore.freeModelNumber }}</span>
            <span class="hero-metric-label">免费模型</span>
          </div>
          <div class="hero-metric">
            <span class="hero-metric-value">100%</span>
            <span class="hero-metric-label">OpenAI 兼容</span>
          </div>
          <div class="hero-metric">
            <span class="hero-metric-value">7 × 24</span>
            <span class="hero-metric-label">多渠道容灾</span>
          </div>
        </div>
      </div>
      <div class="scroll-hint" @click="scrollToPage(1)">
        <icon-down/>
      </div>
    </section>

    <!-- 屏2：模型广场（真实模型卡片模拟） -->
    <section class="slide slide-models" :class="{ 'is-active': currentIndex === 1 }">
      <div class="slide-inner split">
        <div class="slide-copy">
          <p class="slide-eyebrow eyebrow-blue">01 · 模型广场</p>
          <h2 class="slide-title">全站模型，一页尽览</h2>
          <p class="slide-desc">
            每个模型自带品牌图标、分组与三段式定价（输入 / 缓存 / 输出），
            免费模型开箱即用，搜索直达目标模型。
          </p>
          <a-button type="primary" @click="goToModelsPage">
            进入模型广场
            <template #icon><icon-right/></template>
          </a-button>
        </div>
        <div class="slide-visual">
          <div class="mock-card-grid">
            <div v-for="m in showcaseModels" :key="m.name" class="mock-model-card">
              <div class="mock-model-head">
                <LobeIcon :name="m.icon" :fallback="m.name" :size="22"/>
                <span class="mock-model-name">{{ m.name }}</span>
                <span class="mock-model-tag" :class="m.group === 'free' ? 'tag-free' : 'tag-vip'">
                  {{ m.group === 'free' ? '免费' : 'VIP' }}
                </span>
              </div>
              <div class="mock-model-price">
                <span>输入 <b>¥{{ m.inputPrice }}</b></span>
                <span>输出 <b>¥{{ m.outputPrice }}</b></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 屏3：模型工坊（对话面板模拟） -->
    <section class="slide slide-studio" :class="{ 'is-active': currentIndex === 2 }">
      <div class="slide-inner split split-reverse">
        <div class="slide-copy">
          <p class="slide-eyebrow eyebrow-violet">02 · 模型工坊</p>
          <h2 class="slide-title">先试效果，再上生产</h2>
          <p class="slide-desc">
            流式输出与思维链实时展示，参数随手调节，
            选中的模型即是你线上一模一样的调用通道。
          </p>
          <a-button type="primary" @click="goToStudioPage">
            打开模型工坊
            <template #icon><icon-right/></template>
          </a-button>
        </div>
        <div class="slide-visual">
          <div class="mock-chat">
            <div class="mock-chat-row mock-chat-user">用一句话解释什么是 API 中转</div>
            <div class="mock-chat-row mock-chat-ai">
              API 中转站把各大模型厂商的接口统一成一个入口，
              你的应用只改一个 base_url<span class="mock-caret"></span>
            </div>
            <div class="mock-chat-meta">
              <span>qwen-plus</span>
              <span>temperature 0.7</span>
              <span>42 tok/s</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 屏4：监控面板（统计 + 柱状图模拟） -->
    <section class="slide slide-monitor" :class="{ 'is-active': currentIndex === 3 }">
      <div class="slide-inner split">
        <div class="slide-copy">
          <p class="slide-eyebrow eyebrow-green">03 · 监控面板</p>
          <h2 class="slide-title">每一次调用，都有迹可循</h2>
          <p class="slide-desc">
            对话数据、调用日志与用量看板三视图联动，
            时间范围与粒度自由组合，费用与耗时一目了然。
          </p>
          <a-button type="primary" @click="goToMonitorPage">
            进入监控面板
            <template #icon><icon-right/></template>
          </a-button>
        </div>
        <div class="slide-visual">
          <div class="mock-stats">
            <div class="mock-stat"><span class="mock-stat-value">12,408</span><span class="mock-stat-label">调用次数</span></div>
            <div class="mock-stat"><span class="mock-stat-value">3.2M</span><span class="mock-stat-label">消耗 token</span></div>
            <div class="mock-stat"><span class="mock-stat-value">¥18.62</span><span class="mock-stat-label">区间费用</span></div>
          </div>
          <div class="mock-chart">
            <div class="mock-bar" v-for="(h, i) in [34, 52, 41, 66, 58, 78, 62, 88, 71, 94, 82, 100]" :key="i" :style="{height: h + '%'}"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 屏5：控制台（密钥 / 渠道管理模拟） -->
    <section class="slide slide-console" :class="{ 'is-active': currentIndex === 4 }">
      <div class="slide-inner split split-reverse">
        <div class="slide-copy">
          <p class="slide-eyebrow eyebrow-orange">04 · 控制台</p>
          <h2 class="slide-title">密钥、渠道、用户，集中管理</h2>
          <p class="slide-desc">
            API 密钥一键创建与吊销，上游渠道权重可调，
            管理员可直管用户余额与分组，运维视角完整闭环。
          </p>
          <a-button type="primary" @click="goToDashboardPage">
            进入控制台
            <template #icon><icon-right/></template>
          </a-button>
        </div>
        <div class="slide-visual">
          <div class="mock-panel">
            <div class="mock-panel-row">
              <span class="dot dot-green"></span>
              <span class="mock-key">sk-agg-****-****-3Fa9</span>
              <span class="mock-panel-tag">启用</span>
            </div>
            <div class="mock-panel-row">
              <span class="dot dot-blue"></span>
              <span class="mock-channel">渠道 · 官方直连</span>
              <span class="mock-panel-tag">权重 5</span>
            </div>
            <div class="mock-panel-row">
              <span class="dot dot-violet"></span>
              <span class="mock-channel">渠道 · 第三方聚合</span>
              <span class="mock-panel-tag">权重 2</span>
            </div>
            <div class="mock-panel-row">
              <span class="dot dot-gold"></span>
              <span class="mock-balance">余额 ¥ 128.40</span>
              <span class="mock-panel-tag">按量计费</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 屏6：开发文档 + CTA（深色收尾） -->
    <section class="slide slide-docs" :class="{ 'is-active': currentIndex === 5 }">
      <div class="slide-inner split">
        <div class="slide-copy slide-copy-light">
          <p class="slide-eyebrow eyebrow-cyan">05 · 开发文档</p>
          <h2 class="slide-title">三行代码，完成接入</h2>
          <p class="slide-desc">
            完全兼容 OpenAI SDK，把 base_url 换成本站地址即可。
            密钥在控制台创建，模型在广场任选。
          </p>
          <div class="hero-actions">
            <a-button type="primary" @click="goToDocsPage">查看开发文档</a-button>
            <a-button ghost @click="handleStart">免费注册</a-button>
          </div>
        </div>
        <div class="slide-visual">
          <div class="mock-code">
            <div class="mock-code-head">
              <span class="dot dot-gold"></span> quickstart.py
            </div>
            <pre><span class="tok-kw">from</span> openai <span class="tok-kw">import</span> OpenAI

client = OpenAI(
    api_key=<span class="tok-str">"sk-agg-..."</span>,
    base_url=<span class="tok-str">"https://your-domain/v1"</span>,
)

resp = client.chat.completions.create(
    model=<span class="tok-str">"qwen-plus"</span>,
    messages=[{<span class="tok-str">"role"</span>: <span class="tok-str">"user"</span>, <span class="tok-str">"content"</span>: <span class="tok-str">"你好"</span>}],
)</pre>
          </div>
        </div>
      </div>
      <footer class="slide-footer">
        AgenticAPI · 让 Agent 管理你的 API · OpenAI 兼容中转服务
      </footer>
    </section>

    <!-- 右侧圆点导航（桌面端） -->
    <nav class="slide-dots" aria-label="首页分屏导航">
      <button
          v-for="(s, i) in sections"
          :key="s.label"
          class="slide-dot"
          :class="{ 'slide-dot-active': currentIndex === i }"
          :title="s.label"
          @click="scrollToPage(i)"
      ><span class="slide-dot-label">{{ s.label }}</span></button>
    </nav>

    <!-- 左下角屏码 -->
    <div class="slide-counter">{{ String(currentIndex + 1).padStart(2, '0') }} / {{ String(sections.length).padStart(2, '0') }}</div>
  </div>
</template>

<script setup lang="ts">
import {ref, computed, onMounted, onUnmounted} from 'vue'
import {useRouter} from 'vue-router'
import {useModelListStore} from '@/stores/modelList'
import {useUserStore} from '@/stores/user'
import LobeIcon from '@/components/common/LobeIcon.vue'

const modelListStore = useModelListStore()
const userStore = useUserStore()
const router = useRouter()

// ── 路由跳转 ──
const goToModelsPage = () => router.push({name: 'Models'})
const goToStudioPage = () => router.push({name: 'Studio'})
const goToMonitorPage = () => router.push({name: 'Monitor'})
const goToDashboardPage = () => router.push({name: 'Dashboard'})
const goToDocsPage = () => router.push({name: 'Docs'})

// 已登录进控制台，未登录唤起注册弹窗
const handleStart = () => {
  if (userStore.isLoggedIn) {
    goToDashboardPage()
  } else {
    userStore.openAuthDialog('register')
  }
}

// ── 分屏定义（圆点导航 / 屏码共用） ──
const sections = [
  {label: '首页'},
  {label: '模型广场'},
  {label: '模型工坊'},
  {label: '监控面板'},
  {label: '控制台'},
  {label: '开发文档'},
]

// ── 模型广场展示卡：优先取真实数据的前 4 个，无数据时用演示数据 ──
const demoModels = [
  {name: 'qwen-plus', icon: 'Qwen', group: 'free', inputPrice: '0.80', outputPrice: '2.00'},
  {name: 'gpt-4o', icon: 'OpenAI', group: 'vip', inputPrice: '12.50', outputPrice: '50.00'},
  {name: 'claude-sonnet', icon: 'Claude', group: 'vip', inputPrice: '21.00', outputPrice: '105.00'},
  {name: 'deepseek-chat', icon: 'DeepSeek', group: 'free', inputPrice: '1.00', outputPrice: '4.00'},
]

const showcaseModels = computed(() => {
  const real = modelListStore.totalModelList.slice(0, 4).map(m => ({
    name: m.name,
    icon: m.icon || m.name,
    group: m.modelGroup,
    inputPrice: String(parseFloat(String(m.inputPrice)) || 0),
    outputPrice: String(parseFloat(String(m.outputPrice)) || 0),
  }))
  return real.length >= 4 ? real : demoModels
})

// ═══════════ 整页滑动控制（滚轮 / 触摸 / 键盘 / 圆点） ═══════════
const containerRef = ref<HTMLDivElement | null>(null)
const currentIndex = ref(0)
const isScrolling = ref(false)
// 窄屏（手机）退化为普通纵向滚动，不做滚轮劫持
const desktopQuery = window.matchMedia('(min-width: 768px)')

function scrollToPage(index: number) {
  if (index < 0 || index >= sections.length) return
  if (isScrolling.value) return

  currentIndex.value = index
  const container = containerRef.value
  if (!container) return

  if (desktopQuery.matches) {
    isScrolling.value = true
    container.scrollTo({top: index * container.clientHeight, behavior: 'smooth'})
    setTimeout(() => {
      isScrolling.value = false
    }, 700)
  } else {
    container.scrollTo({top: index * container.clientHeight, behavior: 'smooth'})
  }
}

const handleWheel = (e: WheelEvent) => {
  if (!desktopQuery.matches) return
  e.preventDefault()
  if (isScrolling.value) return
  if (e.deltaY > 10) scrollToPage(currentIndex.value + 1)
  else if (e.deltaY < -10) scrollToPage(currentIndex.value - 1)
}

let touchStartY = 0
const handleTouchStart = (e: TouchEvent) => {
  const touch = e.touches[0]
  if (touch) touchStartY = touch.clientY
}
const handleTouchMove = (e: TouchEvent) => {
  if (isScrolling.value) return
  const touch = e.touches[0]
  if (!touch) return
  const diff = touch.clientY - touchStartY
  if (diff < -40) scrollToPage(currentIndex.value + 1)
  else if (diff > 40) scrollToPage(currentIndex.value - 1)
}

const handleKeydown = (e: KeyboardEvent) => {
  // 焦点在输入框 / 弹窗内（如登录弹窗）时不翻页
  const target = e.target as HTMLElement | null
  if (target?.closest?.('input, textarea, .arco-modal, .arco-drawer')) return
  if (e.key === 'ArrowDown' || e.key === 'PageDown') scrollToPage(currentIndex.value + 1)
  else if (e.key === 'ArrowUp' || e.key === 'PageUp') scrollToPage(currentIndex.value - 1)
}

onMounted(() => {
  const dom = containerRef.value
  if (!dom) return
  // passive:false 才能调用 e.preventDefault()（滚轮劫持仅在桌面生效）
  dom.addEventListener('wheel', handleWheel, {passive: false})
  dom.addEventListener('touchstart', handleTouchStart, {passive: true})
  dom.addEventListener('touchmove', handleTouchMove, {passive: true})
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  const dom = containerRef.value
  if (!dom) return
  dom.removeEventListener('wheel', handleWheel)
  dom.removeEventListener('touchstart', handleTouchStart)
  dom.removeEventListener('touchmove', handleTouchMove)
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.home-page {
  position: relative;
  height: 100%;
  overflow: hidden;
  background-color: var(--color-bg);
}

/* ═══════════ 分屏骨架 ═══════════ */
.slide {
  position: relative;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.slide-inner {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 1080px;
  padding: var(--space-6) var(--space-6);
  /* 入场动效：仅当前屏内容完全显形，其余屏降低存在感 */
  opacity: 0.3;
  transform: translateY(14px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.slide.is-active .slide-inner {
  opacity: 1;
  transform: translateY(0);
}

/* 眉题：等宽字体 + 宽字距，工程产品风格 */
.slide-eyebrow {
  margin: 0 0 var(--space-3);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  letter-spacing: 0.18em;
  color: var(--color-text-muted);
}

.eyebrow-blue { color: var(--color-primary); }
.eyebrow-violet { color: var(--color-violet); }
.eyebrow-green { color: var(--color-success); }
.eyebrow-orange { color: var(--color-accent); }
.eyebrow-cyan { color: var(--color-cyan); }

.slide-title {
  margin: 0 0 var(--space-3);
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  font-weight: var(--font-semibold);
  /* 衬线中文标题：留出呼吸感，字距微放、行高放宽 */
  letter-spacing: 0.035em;
  color: var(--color-text);
  line-height: 1.45;
}

.slide-desc {
  margin: 0 0 var(--space-5);
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
  color: var(--color-text-secondary);
  max-width: 30em;
}

/* ═══════════ 屏1：Hero ═══════════ */
.slide-hero {
  background-color: var(--color-bg);
}

/* 点阵网格：工程图纸质感，径向遮罩向边缘淡出（蓝调融入光效） */
.slide-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 0;
  background-image: radial-gradient(circle, rgba(22, 93, 255, 0.3) 1px, transparent 1px);
  background-size: 22px 22px;
  mask-image: radial-gradient(ellipse 65% 55% at 50% 38%, black 20%, transparent 75%);
  -webkit-mask-image: radial-gradient(ellipse 65% 55% at 50% 38%, black 20%, transparent 75%);
  opacity: 0.4;
  pointer-events: none;
}

/* 静态渐变背景（借鉴 Nexus）：顶部色带光束铺底，三枚大尺度模糊色斑固定构图，
   颜色取站点强调色（arcoblue / 紫 / 青），亮色主题下低透明度不喧宾夺主。
   不做漂移动画——大面积 blur 的持续重绘开销大，静态渐变保证流畅 */
.hero-aurora {
  position: absolute;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
  /* 提升为独立合成层：翻页滚动时整层纹理平移，避免反复光栅化 */
  transform: translateZ(0);
}

.hero-aurora::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 75% 55% at 50% 0%, rgba(22, 93, 255, 0.14) 0%, transparent 62%),
    radial-gradient(ellipse 42% 42% at 88% 26%, rgba(114, 46, 209, 0.10) 0%, transparent 70%),
    radial-gradient(ellipse 38% 38% at 8% 72%, rgba(20, 201, 201, 0.08) 0%, transparent 70%);
}

.aurora-blob {
  position: absolute;
  width: 52vmax;
  height: 52vmax;
  border-radius: 50%;
  /* 不用 filter: blur —— 大尺度模糊的光栅化开销是翻页卡顿的主因，
     改用多段径向渐变止点模拟同样的柔和扩散，视觉等效且零滤镜成本 */
}

.blob-blue {
  top: -16%;
  left: 8%;
  background: radial-gradient(circle,
    rgba(22, 93, 255, 0.32) 0%,
    rgba(22, 93, 255, 0.16) 30%,
    rgba(22, 93, 255, 0.06) 55%,
    transparent 72%);
}

.blob-violet {
  top: -10%;
  right: -6%;
  background: radial-gradient(circle,
    rgba(114, 46, 209, 0.26) 0%,
    rgba(114, 46, 209, 0.13) 30%,
    rgba(114, 46, 209, 0.05) 55%,
    transparent 72%);
}

.blob-cyan {
  bottom: -24%;
  left: 32%;
  background: radial-gradient(circle,
    rgba(20, 201, 201, 0.22) 0%,
    rgba(20, 201, 201, 0.11) 30%,
    rgba(20, 201, 201, 0.04) 55%,
    transparent 72%);
}

.hero-inner {
  text-align: center;
}

.hero-title {
  margin: 0 0 var(--space-4);
  font-family: var(--font-display);
  font-size: clamp(36px, 4.6vw, 52px);
  font-weight: var(--font-bold);
  /* 衬线中文大标题：正字距 + 宽行高，避免拥挤 */
  letter-spacing: 0.05em;
  line-height: 1.5;
  color: var(--color-text);
}

/* 关键词：品牌三色静态渐变文字（借鉴 Nexus 渐变标题） */
.hero-title-key {
  background: linear-gradient(100deg, #165dff 0%, #722ed1 45%, #14c9c9 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-desc {
  margin: 0 0 var(--space-6);
  font-size: var(--text-base);
  color: var(--color-text-secondary);
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: var(--space-3);
  margin-bottom: var(--space-8);
}

/* 主按钮：品牌色外发光（借鉴 Nexus CTA） */
.hero-actions :deep(.arco-btn-primary) {
  box-shadow: 0 6px 22px rgba(22, 93, 255, 0.35);
}

/* 数据速览：半透明面板浮于光效之上，等宽数字。
   不用 backdrop-filter —— 滚动时它每帧重滤背后内容，开销大；
   提高底色不透明度在淡色静态背景上观感几乎一致 */
.hero-metrics {
  position: relative;
  display: inline-flex;
  align-items: stretch;
  gap: var(--space-8);
  padding: var(--space-4) var(--space-8);
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(22, 93, 255, 0.14);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-md);
}

.hero-metric {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 72px;
}

.hero-metric + .hero-metric {
  border-left: 1px solid var(--color-border);
  padding-left: var(--space-8);
}

.hero-metric-value {
  font-family: var(--font-mono);
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--color-text);
  font-variant-numeric: tabular-nums;
}

.hero-metric-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

/* 向下滚动提示 */
.scroll-hint {
  position: absolute;
  left: 50%;
  bottom: 18px;
  z-index: 2;
  transform: translateX(-50%);
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  color: var(--color-text-muted);
  background-color: var(--color-white);
  cursor: pointer;
  animation: hint-float 2s ease-in-out infinite;
}

@keyframes hint-float {
  0%, 100% { transform: translate(-50%, 0); }
  50% { transform: translate(-50%, 5px); }
}

/* ═══════════ 通用左右分栏屏 ═══════════ */
.split {
  display: grid;
  grid-template-columns: 5fr 6fr;
  align-items: center;
  gap: var(--space-10);
}

.split-reverse {
  grid-template-columns: 6fr 5fr;
}

/* 各分屏底色：本屏强调色的极浅色调打底，再叠一层偏向视觉区的径向光晕
   （借鉴 Nexus 的 section halo），光晕位置跟随左右分栏的视觉面板一侧 */
.slide-models {
  background:
    radial-gradient(ellipse 55% 62% at 74% 45%, rgba(22, 93, 255, 0.1) 0%, transparent 65%),
    linear-gradient(160deg, var(--color-primary-lighter) 0%, var(--color-bg) 55%);
}

.slide-studio {
  background:
    radial-gradient(ellipse 55% 62% at 26% 45%, rgba(114, 46, 209, 0.09) 0%, transparent 65%),
    linear-gradient(200deg, var(--color-violet-lighter) 0%, var(--color-bg) 55%);
}

.slide-monitor {
  background:
    radial-gradient(ellipse 55% 62% at 74% 45%, rgba(0, 180, 42, 0.09) 0%, transparent 65%),
    linear-gradient(160deg, var(--color-success-light) 0%, var(--color-bg) 55%);
}

.slide-console {
  background:
    radial-gradient(ellipse 55% 62% at 26% 45%, rgba(255, 125, 0, 0.1) 0%, transparent 65%),
    linear-gradient(200deg, var(--color-warning-light) 0%, var(--color-bg) 55%);
}

/* ═══════════ 产品 UI 模拟 ═══════════ */

/* 通用：悬浮上浮 + 阴影抬升，顶部一条强调色高光线（--glow-color 按屏指定） */
.mock-model-card,
.mock-chat,
.mock-stat,
.mock-chart,
.mock-panel,
.mock-code {
  position: relative;
  transition: transform var(--transition-slow), box-shadow var(--transition-slow);
}

.mock-model-card:hover,
.mock-chat:hover,
.mock-chart:hover,
.mock-panel:hover,
.mock-code:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.mock-stat:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.mock-chat::after,
.mock-chart::after,
.mock-panel::after,
.mock-code::after {
  content: '';
  position: absolute;
  top: 0;
  left: 15%;
  width: 70%;
  height: 2px;
  border-radius: 1px;
  background: linear-gradient(90deg, transparent, var(--glow-color, var(--color-primary)), transparent);
  opacity: 0.55;
}

.mock-chat { --glow-color: var(--color-violet); }
.mock-chart { --glow-color: var(--color-success); }
.mock-panel { --glow-color: var(--color-accent); }
.mock-code { --glow-color: var(--color-cyan); }

/* 屏2：模型卡片 */
.mock-card-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
}

.mock-model-card {
  background-color: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4);
  box-shadow: var(--shadow-sm);
}

.mock-model-head {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.mock-model-name {
  flex: 1;
  min-width: 0;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mock-model-tag {
  font-size: var(--text-xs);
  line-height: 18px;
  padding: 0 6px;
  border-radius: var(--radius-sm);
}

.tag-free {
  color: var(--color-success);
  background-color: var(--color-success-light);
}

.tag-vip {
  color: var(--color-vermilion);
  background-color: var(--color-vermilion-lighter);
}

.mock-model-price {
  display: flex;
  gap: var(--space-4);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.mock-model-price b {
  font-family: var(--font-mono);
  font-weight: var(--font-semibold);
  color: var(--color-text-secondary);
  font-variant-numeric: tabular-nums;
}

/* 屏3：对话面板 */
.mock-chat {
  background-color: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.mock-chat-row {
  max-width: 86%;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  border-radius: var(--radius-lg);
}

.mock-chat-user {
  align-self: flex-end;
  background-color: var(--color-primary);
  color: var(--color-on-primary);
  border-bottom-right-radius: var(--radius-sm);
}

.mock-chat-ai {
  align-self: flex-start;
  background-color: var(--color-gray-50);
  border: 1px solid var(--color-border);
  border-bottom-left-radius: var(--radius-sm);
  color: var(--color-text);
}

/* 流式输出光标 */
.mock-caret {
  display: inline-block;
  width: 2px;
  height: 1em;
  margin-left: 2px;
  vertical-align: -0.15em;
  background-color: var(--color-violet);
  animation: caret-blink 0.9s steps(1) infinite;
}

@keyframes caret-blink {
  50% { opacity: 0; }
}

.mock-chat-meta {
  display: flex;
  gap: var(--space-4);
  padding-top: var(--space-2);
  border-top: 1px dashed var(--color-border);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

/* 屏4：统计 + 柱状图 */
.mock-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.mock-stat {
  background-color: var(--color-white);
  border: 1px solid var(--color-border);
  border-left: 3px solid var(--color-success);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mock-stat:nth-child(2) { border-left-color: var(--color-primary); }
.mock-stat:nth-child(3) { border-left-color: var(--color-gold); }

.mock-stat-value {
  font-family: var(--font-mono);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--color-text);
  font-variant-numeric: tabular-nums;
}

.mock-stat-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.mock-chart {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 120px;
  background-color: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4);
}

/* 柱子按强调色系循环，多色但低饱和度统一 */
.mock-bar {
  flex: 1;
  border-radius: 2px 2px 0 0;
  background-color: var(--color-primary-lighter);
}

.mock-bar:nth-child(3n + 1) { background-color: var(--color-success); opacity: 0.55; }
.mock-bar:nth-child(3n + 2) { background-color: var(--color-primary); opacity: 0.55; }
.mock-bar:nth-child(3n) { background-color: var(--color-gold); opacity: 0.55; }
.mock-bar:last-child { opacity: 0.9; }

/* 屏5：控制台列表 */
.mock-panel {
  background-color: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.mock-panel-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
}

.mock-panel-row + .mock-panel-row {
  border-top: 1px solid var(--color-border);
}

.mock-key {
  flex: 1;
  font-family: var(--font-mono);
  color: var(--color-text);
}

.mock-channel,
.mock-balance {
  flex: 1;
  color: var(--color-text);
}

.mock-panel-tag {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  background-color: var(--color-gray-50);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0 6px;
  line-height: 18px;
}

/* 状态点 */
.dot {
  width: 6px;
  height: 6px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.dot-green { background-color: var(--color-success); }
.dot-blue { background-color: var(--color-primary); }
.dot-violet { background-color: var(--color-violet); }
.dot-gold { background-color: var(--color-gold); }

/* 屏6：深色收尾 */
.slide-docs {
  background-color: var(--color-gray-900);
}

/* 深色屏光晕：蓝紫双色呼应 Hero 的 aurora */
.slide-docs::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 0;
  background:
    radial-gradient(ellipse 55% 55% at 72% 42%, rgba(22, 93, 255, 0.16) 0%, transparent 62%),
    radial-gradient(ellipse 40% 45% at 18% 68%, rgba(114, 46, 209, 0.13) 0%, transparent 65%);
  pointer-events: none;
}

.slide-docs .slide-title,
.slide-docs .slide-copy-light {
  color: var(--color-white);
}

.slide-docs .slide-desc {
  color: var(--color-gray-400);
}

.slide-docs .hero-actions {
  justify-content: flex-start;
  margin-bottom: 0;
}

.mock-code {
  background-color: var(--color-gray-800);
  border: 1px solid var(--color-gray-700, #4e5969);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

.mock-code-head {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border-bottom: 1px solid var(--color-gray-700, #4e5969);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-gray-400);
}

.mock-code pre {
  margin: 0;
  padding: var(--space-4);
  font-family: var(--font-mono);
  font-size: 12.5px;
  line-height: 1.75;
  color: var(--color-gray-100);
  overflow-x: auto;
}

.tok-kw { color: #c384f5; }
.tok-str { color: #7ce38b; }

.slide-footer {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: var(--space-3) var(--space-6);
  border-top: 1px solid var(--color-gray-700, #4e5969);
  font-size: var(--text-xs);
  color: var(--color-gray-500);
  text-align: center;
}

/* ═══════════ 导航：右侧圆点 + 左下屏码 ═══════════ */
.slide-dots {
  position: fixed;
  right: 18px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 10;
}

.slide-dot {
  position: relative;
  width: 8px;
  height: 8px;
  padding: 0;
  border: none;
  border-radius: var(--radius-full);
  background-color: var(--color-gray-300);
  cursor: pointer;
  transition: background-color var(--transition-fast), transform var(--transition-fast);
}

.slide-dot:hover {
  background-color: var(--color-gray-500);
}

.slide-dot-active {
  background-color: var(--color-primary);
  transform: scale(1.25);
}

/* 悬停显示分屏名称 */
.slide-dot-label {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  white-space: nowrap;
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  background-color: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 2px 8px;
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--transition-fast);
}

.slide-dot:hover .slide-dot-label {
  opacity: 1;
}

.slide-counter {
  position: fixed;
  left: 20px;
  bottom: 16px;
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  letter-spacing: 0.08em;
  z-index: 10;
}

/* ═══════════ 响应式：窄屏退化为普通滚动 ═══════════ */
@media (prefers-reduced-motion: reduce) {
  .scroll-hint,
  .mock-caret {
    animation: none;
  }
}

@media (max-width: 767px) {
  .home-page {
    overflow-y: auto;
  }

  .slide {
    min-height: 100%;
    padding: var(--space-8) 0;
  }

  .slide-inner {
    opacity: 1;
    transform: none;
  }

  .hero-title {
    font-size: var(--text-3xl);
  }

  .hero-metrics {
    flex-wrap: wrap;
    gap: var(--space-4);
    padding: 0;
  }

  .hero-metric + .hero-metric {
    border-left: none;
    padding-left: 0;
  }

  .split,
  .split-reverse {
    grid-template-columns: 1fr;
    gap: var(--space-6);
  }

  .slide-dots,
  .slide-counter,
  .scroll-hint {
    display: none;
  }
}
</style>
