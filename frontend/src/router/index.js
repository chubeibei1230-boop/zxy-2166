import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true },
    redirect: '/overview',
    children: [
      {
        path: 'overview',
        name: 'Overview',
        component: () => import('@/views/Overview.vue'),
        meta: { title: '数据总览', icon: 'DataAnalysis' }
      },
      {
        path: 'signs',
        name: 'Signs',
        component: () => import('@/views/SignList.vue'),
        meta: { title: '引导牌列表', icon: 'Tickets' }
      },
      {
        path: 'issue',
        name: 'Issue',
        component: () => import('@/views/Issue.vue'),
        meta: { title: '发放管理', icon: 'Promotion' }
      },
      {
        path: 'recycle',
        name: 'Recycle',
        component: () => import('@/views/Recycle.vue'),
        meta: { title: '回收管理', icon: 'Refresh' }
      },
      {
        path: 'review',
        name: 'Review',
        component: () => import('@/views/Review.vue'),
        meta: { title: '复核管理', icon: 'DocumentChecked' }
      },
      {
        path: 'anomaly',
        name: 'Anomaly',
        component: () => import('@/views/Anomaly.vue'),
        meta: { title: '异常管理', icon: 'Warning' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else if (to.path === '/login' && userStore.isLoggedIn) {
    next('/overview')
  } else {
    next()
  }
})

export default router
