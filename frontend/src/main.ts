// 引入 Arco Design Vue 组件库（全量注册，亮色默认主题，主色 arcoblue 与全局令牌一致）
import ArcoVue from '@arco-design/web-vue'
import ArcoVueIcon from '@arco-design/web-vue/es/icon'
import '@arco-design/web-vue/dist/arco.css'

// 引入全局样式（含设计令牌与 Arco 微调，需在 arco.css 之后加载）
import './styles/index.css'

// 引入vue
import { createApp } from 'vue'
import App from './App.vue'

// 引入路由
import router from './router/index.ts'

// 引入pinia
import pinia from '@/stores/index'

const app = createApp(App)
app.use(pinia) // 使用pinia状态管理库（需先于router安装：路由守卫里会用到pinia的store）
app.use(router) // 使用路由
app.use(ArcoVue) // 注册全部 arco 组件
app.use(ArcoVueIcon) // 注册全部 arco 图标

app.mount('#app')
