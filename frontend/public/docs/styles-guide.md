# AgenticAPI — 公共样式文档

> 本文档介绍项目中 `src/styles/` 目录下的所有公共 CSS 样式，涵盖设计令牌、布局工具、文字排版、UI 组件等。

---

## 目录

- [文件结构](#文件结构)
- [1. 设计令牌 (variables.css)](#1-设计令牌-variablescss)
- [2. 样式重置 (reset.css)](#2-样式重置-resetcss)
- [3. 布局工具 (layout.css)](#3-布局工具-layoutcss)
- [4. 文字排版与容器 (typography.css)](#4-文字排版与容器-typographycss)
- [5. UI 组件 (components.css)](#5-ui-组件-componentscss)
- [使用方式](#使用方式)

---

## 文件结构

```
src/styles/
├── index.css          # 入口文件，统一按顺序导入所有模块
├── variables.css      # CSS 变量（设计令牌）
├── reset.css          # 浏览器默认样式重置
├── layout.css         # 布局工具类（容器、Flex、Grid、间距）
├── typography.css     # 文字排版 & 富文本容器 & 卡片
└── components.css     # UI 组件（按钮、表单、加载态、工具类）
```

---

## 1. 设计令牌 (variables.css)

所有 CSS 自定义属性（Custom Properties）定义在 `:root` 中，可在整个项目中直接引用。

### 颜色系统

| 变量名 | 用途 | 默认值 |
|--------|------|--------|
| `--color-primary` | 品牌主色 | `#2563eb` |
| `--color-primary-light` | 主色浅色 | `#3b82f6` |
| `--color-primary-dark` | 主色深色 | `#1d4ed8` |
| `--color-accent` | 强调色 | `#f59e0b` |
| `--color-success` | 成功/正向 | `#059669` |
| `--color-warning` | 警告 | `#d97706` |
| `--color-error` | 错误/危险 | `#dc2626` |
| `--color-info` | 信息提示 | `#0891b2` |
| `--color-text` | 正文颜色 | `#111827` |
| `--color-text-secondary` | 次要文字 | `#4b5563` |
| `--color-text-muted` | 弱化文字 | `#9ca3af` |
| `--color-bg` | 页面背景 | `#ffffff` |
| `--color-bg-secondary` | 次级背景 | `#f9fafb` |
| `--color-border` | 边框 | `#e5e7eb` |

### 字体系统

| 变量名 | 用途 | 默认值 |
|--------|------|--------|
| `--font-sans` | 无衬线字体栈 | Inter → 系统字体 → Arial |
| `--font-mono` | 等宽字体栈 | JetBrains Mono → Fira Code → Consolas |
| `--text-xs` ~ `--text-5xl` | 字号阶梯 | 12px ~ 48px |
| `--font-light` ~ `--font-bold` | 字重 | 300 ~ 700 |
| `--leading-tight` ~ `--leading-relaxed` | 行高 | 1.25 ~ 1.625 |

### 间距系统

| 变量名 | 值 | 变量名 | 值 |
|--------|-----|--------|-----|
| `--space-1` | 4px | `--space-6` | 24px |
| `--space-2` | 8px | `--space-8` | 32px |
| `--space-3` | 12px | `--space-10` | 40px |
| `--space-4` | 16px | `--space-12` | 48px |
| `--space-5` | 20px | `--space-16` | 64px |

### 圆角 & 阴影 & 过渡

| 变量名 | 用途 |
|--------|------|
| `--radius-sm` (4px) ~ `--radius-full` (9999px) | 圆角阶梯 |
| `--shadow-sm` ~ `--shadow-xl` | 阴影层级 |
| `--transition-fast` (150ms) / `--transition-base` (200ms) / `--transition-slow` (300ms) | 过渡时长 |

### 布局断点

| 变量名 | 值 | 对应断点 |
|--------|-----|----------|
| `--container-sm` | 640px | 手机横屏 |
| `--container-md` | 768px | 平板 |
| `--container-lg` | 1024px | 小桌面 |
| `--container-xl` | 1280px | 桌面 |
| `--container-2xl` | 1536px | 大桌面 |

---

## 2. 样式重置 (reset.css)

- 全局 `box-sizing: border-box`
- 移除 body 默认 margin/padding
- 基准字号 16px，平滑滚动
- 图片/视频默认 `display: block`，`max-width: 100%`
- 表单元素继承父级字体
- h1–h6 预设字号与字重
- 链接默认品牌色，hover 加下划线
- `:focus-visible` 键盘焦点环（可访问性）
- `prefers-reduced-motion` 尊重用户减少动画偏好

---

## 3. 布局工具 (layout.css)

### 容器

| 类名 | 说明 |
|------|------|
| `.container` | 响应式容器，随断点自动调整最大宽度，居中 + 16px 内边距 |
| `.container-sm` | 固定窄容器 (640px)，适合阅读型内容 |

### Flex 布局

| 类名 | 说明 |
|------|------|
| `.flex` / `.flex-col` / `.flex-row` | Flex 容器 |
| `.flex-wrap` / `.flex-nowrap` | 换行控制 |
| `.justify-start` / `-center` / `-end` / `-between` / `-around` / `-evenly` | 主轴对齐 |
| `.items-start` / `-center` / `-end` / `-stretch` / `-baseline` | 交叉轴对齐 |
| `.flex-1` / `.flex-auto` / `.flex-none` / `.flex-grow` | Flex 子元素伸缩 |
| `.flex-center` | 快捷：水平垂直居中 |
| `.flex-between` | 快捷：两端对齐 + 垂直居中 |

### Grid 布局

| 类名 | 说明 |
|------|------|
| `.grid` | Grid 容器 |
| `.grid-cols-1` ~ `.grid-cols-4` | 等分列（移动端自动降级为单列） |
| `.gap-0` ~ `.gap-8` | 网格/弹性间距 |

### 间距

| 类名 | 说明 |
|------|------|
| `.m-{0-8}` | 外边距 |
| `.mt-{0-16}` | 上外边距 |
| `.mb-{0-16}` | 下外边距 |
| `.mx-auto` | 水平居中 |
| `.p-{0-16}` | 内边距 |
| `.px-{4,6,8}` / `.py-{4,6,8}` | 水平/垂直内边距快捷方式 |

### 其他

| 类名 | 说明 |
|------|------|
| `.divider` | 水平分隔线 |
| `.w-full` / `.h-full` | 宽高 100% |
| `.min-h-screen` | 最小高度 100vh |

---

## 4. 文字排版与容器 (typography.css)

### 文字工具类

| 类名 | 说明 |
|------|------|
| `.text-xs` ~ `.text-5xl` | 字号 |
| `.font-light` ~ `.font-bold` | 字重 |
| `.text-primary` / `-secondary` / `-muted` / `-brand` / `-success` / `-warning` / `-error` | 文字颜色 |
| `.text-left` / `-center` / `-right` | 文字对齐 |
| `.leading-tight` / `-snug` / `-normal` / `-relaxed` | 行高 |
| `.truncate` | 单行截断 + 省略号 |
| `.line-clamp-2` / `.line-clamp-3` | 多行截断 |
| `.uppercase` / `.lowercase` / `.capitalize` | 文字变换 |
| `.font-mono` | 等宽字体 |

### 富文本容器 `.prose`

将任意内容包裹在 `<div class="prose">` 中即可获得完整的文章排版样式：

```html
<div class="prose">
  <h1>文章标题</h1>
  <p>这是正文内容...</p>
  <h2>二级标题</h2>
  <blockquote>引用文字</blockquote>
  <ul>
    <li>列表项</li>
  </ul>
  <pre><code>// 代码块</code></pre>
</div>
```

**包含的样式：**
- h1–h6 标题层级（含底部边框、不同字重）
- 首段自动放大为导语
- 链接品牌色 + 下划线
- 行内代码 `<code>` — 灰底红字
- 引用块 `<blockquote>` — 左侧蓝色边框 + 灰底
- 无序列表（disc → circle → square）和有序列表
- 图片圆角、表格斑马纹、代码块深色背景
- `<kbd>` 键盘按键样式、`<mark>` 高亮、`<abbr>` 缩写

**变体：**

| 类名 | 说明 |
|------|------|
| `.prose` | 默认（16px 字号，65ch 最大宽度） |
| `.prose-sm` | 紧凑版（14px 字号），适合侧边栏 |
| `.prose-lg` | 宽大版（18px 字号，75ch 最大宽度），适合大幅面 |

### 标注/提示框 Callout

```html
<div class="callout callout-info">
  <div class="callout-title">提示</div>
  这是一条信息提示。
</div>
```

| 类名 | 用途 |
|------|------|
| `.callout-info` | 信息提示（蓝底） |
| `.callout-success` | 成功提示（绿底） |
| `.callout-warning` | 警告提示（黄底） |
| `.callout-error` | 错误提示（红底） |

### 徽章 Badge

```html
<span class="badge badge-success">已上线</span>
<span class="badge badge-warning">审核中</span>
<span class="badge badge-error">失败</span>
<span class="badge badge-neutral">存档</span>
```

### 代码展示

```html
<div class="code-block">
  <div class="code-block-header">JavaScript</div>
  <div class="code-block-body">
    <pre><code>const hello = 'world';</code></pre>
  </div>
</div>
```

### 卡片 Card

| 类名 | 说明 |
|------|------|
| `.card` | 基础卡片（白底 + 边框 + hover 阴影） |
| `.card-ghost` | 无边框透明卡片 |
| `.card-active` | 选中态卡片（蓝色边框） |
| `.card-header` / `.card-body` / `.card-footer` | 卡片分区 |
| `.card-title` / `.card-description` | 卡片标题/描述 |

### 区块 Section

| 类名 | 说明 |
|------|------|
| `.section` | 页面区块（响应式内边距） |
| `.section-muted` | 带灰色背景的区块 |
| `.section-header` | 区块头部（居中 + 最大宽度 600px） |
| `.section-title` / `.section-description` | 区块标题/描述 |

### 面板 Panel

| 类名 | 说明 |
|------|------|
| `.panel` | 基础面板（白底 + 边框 + 大圆角） |
| `.panel-header` | 面板头部（灰底 + 底边框） |
| `.panel-body` | 面板内容区 |
| `.panel-footer` | 面板底部（灰底 + 顶边框） |

---

## 5. UI 组件 (components.css)

### 按钮 .btn

```html
<button class="btn btn-primary">主要按钮</button>
<button class="btn btn-secondary">次要按钮</button>
<button class="btn btn-outline">轮廓按钮</button>
<button class="btn btn-ghost">文字按钮</button>
<button class="btn btn-danger">危险操作</button>
```

| 类名 | 说明 |
|------|------|
| `.btn` | 基础按钮（最小触控 44×44px） |
| `.btn-primary` | 实心主按钮 |
| `.btn-secondary` | 白底灰边次要按钮 |
| `.btn-outline` | 透明轮廓按钮 |
| `.btn-ghost` | 无边框文字按钮 |
| `.btn-danger` | 红色危险按钮 |
| `.btn-sm` / `.btn-lg` | 尺寸变体 |
| `.btn-icon` | 正方形图标按钮 |
| `.btn-block` | 全宽按钮 |

### 表单控件

```html
<!-- 输入框 -->
<input class="input" type="text" placeholder="请输入..." />

<!-- 带标签 -->
<div class="form-group">
  <label class="form-label form-label-required">用户名</label>
  <input class="input" type="text" />
  <p class="form-hint">请输入 4-20 个字符</p>
</div>

<!-- 错误状态 -->
<input class="input input-error" type="text" />
<p class="form-error">此项为必填</p>
```

| 类名 | 说明 |
|------|------|
| `.input` | 文本输入框 |
| `.input-error` | 错误状态输入框 |
| `.textarea` | 多行文本域 |
| `.select` | 下拉选择（自定义箭头） |
| `.checkbox` / `.radio` | 复选框/单选框（最小 44px 触控区） |
| `.form-group` | 表单组（含底部间距） |
| `.form-label` / `.form-label-required` | 标签/必填标签 |
| `.form-hint` | 帮助提示文字 |
| `.form-error` | 错误提示文字 |

### 开关 Toggle

```html
<label class="toggle">
  <input type="checkbox" />
  <span class="toggle-track"></span>
  启用通知
</label>
```

### 加载与状态

| 类名 | 说明 |
|------|------|
| `.spinner` / `.spinner-sm` / `.spinner-lg` | 加载旋转动画 |
| `.skeleton` / `.skeleton-text` / `.skeleton-title` / `.skeleton-avatar` / `.skeleton-card` | 骨架屏占位 |
| `.empty-state` / `.empty-state-icon` / `.empty-state-title` / `.empty-state-description` | 空状态提示 |

### 工具类

**显示/隐藏：**
| 类名 | 说明 |
|------|------|
| `.hidden` | 隐藏 |
| `.sr-only` | 仅屏幕阅读器可见（无障碍） |
| `.hidden-mobile` | 移动端隐藏 |
| `.hidden-desktop` | 桌面端隐藏 |

**位置：**
| 类名 | 说明 |
|------|------|
| `.relative` / `.absolute` / `.fixed` / `.sticky` | 定位方式 |

**视觉：**
| 类名 | 说明 |
|------|------|
| `.rounded-sm` ~ `.rounded-full` | 圆角 |
| `.shadow-sm` ~ `.shadow-xl` / `.shadow-none` | 阴影 |
| `.bg-white` / `.bg-muted` / `.bg-primary` | 背景色 |
| `.border` / `.border-t` / `.border-b` / `.border-none` | 边框 |
| `.overflow-auto` / `-hidden` / `-scroll` | 溢出控制 |
| `.cursor-pointer` / `.cursor-not-allowed` | 光标 |
| `.select-none` / `.select-text` | 用户选择 |
| `.transition` / `-fast` / `-slow` | 过渡动画 |

---

## 使用方式

### 全局引入（已配置）

项目已在 `src/main.ts` 中全局引入，**无需手动导入**：

```ts
import './styles/index.css'
```

### 在组件中使用

所有样式类名可直接在模板中使用：

```vue
<template>
  <div class="container">
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">标题</h2>
        <p class="section-description">描述文字</p>
      </div>

      <div class="grid grid-cols-3 gap-6">
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">卡片标题</h3>
          </div>
          <div class="card-body">
            <p>卡片内容</p>
          </div>
        </div>
      </div>

      <div class="prose mt-8">
        <h2>富文本内容</h2>
        <p>这是一段文章内容...</p>
      </div>
    </section>
  </div>
</template>
```

### 自定义 CSS 变量

在任意组件中覆盖变量即可定制主题：

```css
/* 暗色主题 */
.dark {
  --color-bg: #111827;
  --color-text: #f9fafb;
  --color-border: #374151;
}
```

### 设计原则

1. **语义化类名** — 类名语义清晰，便于理解和维护
2. **触控友好** — 按钮、输入框、复选框等交互元素最小 44×44px
3. **无障碍** — 键盘焦点可见、屏幕阅读器支持、`prefers-reduced-motion` 尊重用户偏好
4. **响应式** — 容器、Grid、Section 等均内置响应式断点
5. **CSS 变量驱动** — 所有颜色、间距、字号通过变量统一管理，便于全局换肤