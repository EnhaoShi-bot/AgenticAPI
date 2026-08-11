// 引入全局样式
import './styles/index.css'

// 引入element-plus
import ElementPlus, {messageConfig} from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'


// 引入vue
import {createApp} from 'vue'
import App from './App.vue'

// 引入路由
import router from './router/index.ts'

// 引入pinia
import {createPinia} from 'pinia'

const pinia = createPinia()


const app = createApp(App)
app.use(router) // 使用路由
app.use(ElementPlus, {locale: zhCn,})   // 使用element-plus组件库, 并配置为中文
app.use(pinia) // 使用pinia状态管理库

// 配置element-plus的消息提示，也就是全局的消息提示配置
messageConfig.duration = 800
messageConfig.showClose = true
messageConfig.grouping = true

app.mount('#app')