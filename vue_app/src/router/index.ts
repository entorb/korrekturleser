/**
 * Vue Router configuration
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { tokenManager } from '@/services/apiClient'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'text',
      component: async () => import('@/views/TextView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: async () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/stats',
      name: 'stats',
      component: async () => import('@/views/StatsView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// Navigation guard to check authentication
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta['requiresAuth'] !== false

  // Try to restore session if token exists but user is not authenticated
  if (!authStore.isAuthenticated && tokenManager.exists()) {
    authStore.loadUserFromToken()
  }

  if (requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login' })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'text' })
  } else {
    next()
  }
})

export default router
