import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // 登录页（独立布局，不套 MainLayout）
  { path: '/login', name: 'Login', component: () => import('../pages/LoginPage.vue') },

  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'Home', component: () => import('../pages/HomePage.vue') },
      { path: 'screening', name: 'Screening', component: () => import('../pages/ScreeningPage.vue') },
      { path: 'companion', name: 'Companion', component: () => import('../pages/CompanionPage.vue'), meta: { requiresAuth: true } },
      { path: 'mood-calendar', name: 'MoodCalendar', component: () => import('../pages/MoodCalendarPage.vue'), meta: { requiresAuth: true } },
      { path: 'analytics', name: 'Analytics', component: () => import('../pages/AnalyticsPage.vue'), meta: { requiresAuth: true } },
      { path: 'about', name: 'About', component: () => import('../pages/AboutPage.vue') },
      { path: 'assessment/:type', name: 'Assessment', component: () => import('../pages/AssessmentPage.vue') },
      { path: 'report/:id', name: 'Report', component: () => import('../pages/ReportPage.vue') },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

// 导航守卫：未登录时跳转到登录页
router.beforeEach((to) => {
  if (!to.meta.requiresAuth) return true

  const saved = localStorage.getItem('xinjing_auth')
  const token = saved ? JSON.parse(saved)?.token : null
  if (token) return true

  return { path: '/login', query: { redirect: to.fullPath } }
})

export default router
