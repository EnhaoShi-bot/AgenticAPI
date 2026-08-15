import { createRouter, createWebHistory } from 'vue-router'
// 下面是第一级路由的组件
import Home from '@/views/home/index.vue'
import Models from '@/views/models/index.vue'
import Routes from '@/views/routes/index.vue'
import Studio from '@/views/studio/index.vue'
import Dashboard from '@/views/Dashboard/index.vue'
import Docs from '@/views/docs/index.vue'

// 下面是第二路由的组件
import Overview from '@/views/Dashboard/Overview.vue'
import Keys from '@/views/Dashboard/Keys.vue'
import Channels from '@/views/Dashboard/Channels.vue'
import UserList from '@/views/Dashboard/UserList.vue'
import RedemptionCodes from '@/views/Dashboard/RedemptionCodes.vue'
import Operations from '@/views/Dashboard/Operations.vue'
import Security from '@/views/Dashboard/Security.vue'

const router = createRouter({
    history: createWebHistory(), // 历史模式
    routes: [
        // 重定向首页到 /home
        {
            path: '/',
            redirect: '/home'
        },
        // 定义路由
        {
            name: 'Home',
            path: '/home',
            component: Home
        },
        {
            name: 'Models',
            path: '/models',
            component: Models
        },
        {
            name: 'Routes',
            path: '/routes',
            component: Routes
        },
        {
            name: 'Studio',
            path: '/studio',
            component: Studio
        },
        // 定义 Dashboard 路由
        {
            name: 'Dashboard',
            path: '/dashboard',
            component: Dashboard,
            // 定义 Dashboard 子路由，也就是在后台控制台中展示的页面
            children: [
                // 重定向到 Overview 页面
                {
                    name: 'DashboardRedirect',
                    path: '',
                    redirect: '/dashboard/overview'
                },
                {
                    name: 'Overview',
                    path: 'overview',
                    component: Overview
                },
                {
                    name: 'Keys',
                    path: 'keys',
                    component: Keys
                },
                {
                    name: 'Channels',
                    path: 'channels',
                    component: Channels
                },
                {
                    name: 'UserList',
                    path: 'userlist',
                    component: UserList
                },
                {
                    name: 'RedemptionCodes',
                    path: 'redemptioncodes',
                    component: RedemptionCodes
                },
                {
                    name: 'Operations',
                    path: 'operations',
                    component: Operations
                },
                {
                    name: 'Security',
                    path: 'security',
                    component: Security
                }
            ]
        },
        {
            name: 'Docs',
            path: '/docs',
            component: Docs
        }
    ]
})

export default router