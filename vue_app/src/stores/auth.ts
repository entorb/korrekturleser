/**
 * Authentication store using Pinia
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, tokenManager } from '@/services/apiClient'
import { decodeJwt, isTokenExpired } from '@/utils/jwt'

interface UserInfo {
  user_name: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => user.value !== null)

  async function login(secret: string): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.auth.loginApiAuthLoginPost({ secret })
      tokenManager.set(response.access_token)
      loadUserFromToken()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function loadUserFromToken(): void {
    const token = tokenManager.get()
    if (token == null || isTokenExpired(token)) {
      logout()
      return
    }

    const payload = decodeJwt(token)
    user.value = payload ? { user_name: payload.username } : null
  }

  function logout(): void {
    tokenManager.clear()
    user.value = null
    error.value = null
  }

  return {
    user,
    isLoading,
    error,
    isAuthenticated,
    login,
    logout,
    loadUserFromToken
  }
})
