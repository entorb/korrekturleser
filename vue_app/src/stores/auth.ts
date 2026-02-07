/**
 * Authentication store using Pinia
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, tokenManager } from '@/services/apiClient'
import type { TokenResponse } from '@/api'
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
      const response: TokenResponse = await api.auth.loginApiAuthLoginPost({ secret })
      tokenManager.set(response.access_token)

      // Extract user info from JWT token
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
    if (token === null || token.length === 0) {
      return
    }

    // Check if token is expired
    if (isTokenExpired(token)) {
      logout()
      return
    }

    // Decode JWT to get user info
    const payload = decodeJwt(token)
    if (payload) {
      user.value = {
        user_name: payload.username
      }
    } else {
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
    loadUserFromToken
  }
})
