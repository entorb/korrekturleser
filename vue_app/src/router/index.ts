/**
 * Vue Router configuration
 *
 * Includes a chunk-load error handler: after a new deployment the browser
 * may still hold a cached index.html that references old hashed chunk
 * filenames.  When the dynamic import fails we force a full page reload
 * so the browser fetches the latest assets.
 */

import { createRouter, createWebHistory } from 'vue-router'

import { tokenManager } from '@/services/apiClient'
import { useAuthStore } from '@/stores/auth'

/**
 * Wrap a lazy component import so that a chunk-load failure (e.g. after a
 * new deploy) triggers a single hard reload instead of a blank page.
 */
function lazyLoad(loader: () => Promise<unknown>) {
  return async () => {
    try {
      return await loader()
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : ''
      // Vite throws "Failed to fetch dynamically imported module" or
      // "Unable to preload CSS" when chunks are missing.
      if (
        msg.includes('dynamically imported module') ||
        msg.includes('preload CSS') ||
        msg.includes('Loading chunk') ||
        msg.includes('net::ERR_ABORTED')
      ) {
        // Prevent infinite reload loops
        const key = 'chunk-reload'
        if (!sessionStorage.getItem(key)) {
          sessionStorage.setItem(key, '1')
          globalThis.location.reload()
          // Return a never-resolving promise so the router doesn't
          // continue rendering while the page reloads.
           
          return new Promise(() => {
            /* intentionally pending forever */
          })
        }
        sessionStorage.removeItem(key)
      }
      throw error
    }
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'text',
      component: lazyLoad(() => import('@/views/TextView.vue')),
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: lazyLoad(() => import('@/views/LoginView.vue')),
      meta: { requiresAuth: false }
    },
    {
      path: '/stats',
      name: 'stats',
      component: lazyLoad(() => import('@/views/StatsView.vue')),
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta['requiresAuth'] !== false

  if (!authStore.isAuthenticated && tokenManager.get() != null) {
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
