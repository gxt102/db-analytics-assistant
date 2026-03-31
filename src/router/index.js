import Vue from 'vue'
import VueRouter from 'vue-router'
import AuthPage from '@/components/page/AuthPage'  // 导入主组件
import Chat from '@/components/page/Chat'
Vue.use(VueRouter)

const routes = [
  {
    path: '/auth',
    name: 'Auth',
    component: AuthPage  // 使用 AuthPage 作为页面
  },
  {
    path: '/login',

    redirect: '/auth'  // 将 /login 重定向到 /auth
  },
  {
    path: '/chat',
    name: 'Chat',
     meta:{requireAuth:true},//是否允许访问
    component: Chat
  },
  {
    path: '/',
    redirect: '/auth'  // 默认页面
  }

]

const router = new VueRouter({
  mode: 'history',
  routes
})

export default router
