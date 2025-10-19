/**
 * Authentication store using Pinia
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, tokenManager } from '@/services/apiClient'
import type { TokenResponse, UserInfoResponse } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfoResponse | null>(null)
  const totalRequests = ref<number>(0)
  const totalTokens = ref<number>(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => user.value !== null)

  async function login(secret: string): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response: TokenResponse = await api.auth.loginApiAuthLoginPost({ secret })
      tokenManager.set(response.access_token)
      user.value = {
        user_name: response.user_name,
        cnt_requests: response.cnt_requests,
        cnt_tokens: response.cnt_tokens
      }
      totalRequests.value = response.cnt_requests
      totalTokens.value = response.cnt_tokens
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
      user.value = {
        user_name: userInfo.user_name,
        cnt_requests: userInfo.cnt_requests,
        cnt_tokens: userInfo.cnt_tokens
      }
      totalRequests.value = userInfo.cnt_requests
      totalTokens.value = userInfo.cnt_tokens
    } catch {
      // Token might be invalid, logout
      logout()
    }
  }

  function logout(): void {
    tokenManager.clear()
    user.value = null
    totalRequests.value = 0
    totalTokens.value = 0
    error.value = null
  }

  function updateUsage(requests: number, tokens: number): void {
    totalRequests.value = requests
    totalTokens.value = tokens
  }

  return {
    user,
    totalRequests,
    totalTokens,
    isLoading,
    error,
    isAuthenticated,
    login,
    logout,
    fetchUserInfo,
    updateUsage
  }
})
