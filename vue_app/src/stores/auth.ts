/**
 * Authentication store using Pinia
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, tokenManager } from '@/services/apiClient'
import type { TokenResponse, UserInfoResponse } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfoResponse | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => user.value !== null)

  async function login(secret: string): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response: TokenResponse = await api.auth.loginApiAuthLoginPost({ secret })
      tokenManager.set(response.access_token)

      // Fetch user info after successful login
      await fetchUserInfo()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUserInfo(): Promise<void> {
    if (!tokenManager.exists()) {
      return
    }

    try {
      const userInfo = await api.auth.getMeApiAuthMeGet()
      user.value = userInfo
    } catch {
      // Token might be invalid, logout
      logout()
    }
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
    fetchUserInfo
  }
})
