import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'

// Mock the API client
vi.mock('@/services/apiClient', () => ({
  api: {
    auth: {
      loginApiAuthLoginPost: vi.fn(),
      getMeApiAuthMeGet: vi.fn()
    }
  },
  tokenManager: {
    get: vi.fn(),
    set: vi.fn(),
    clear: vi.fn(),
    exists: vi.fn()
  }
}))

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with default values', () => {
    const store = useAuthStore()

    expect(store.user).toBeNull()
    expect(store.totalRequests).toBe(0)
    expect(store.totalTokens).toBe(0)
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })

  it('sets user as authenticated after successful login', async () => {
    const { api, tokenManager } = await import('@/services/apiClient')
    const mockLoginResponse = {
      access_token: 'test-token',
      token_type: 'bearer',
      user_name: 'TestUser',
      cnt_requests: 10,
      cnt_tokens: 1000
    }

    vi.mocked(api.auth.loginApiAuthLoginPost).mockResolvedValue(mockLoginResponse)

    const store = useAuthStore()
    await store.login('test-secret')

    expect(tokenManager.set).toHaveBeenCalledWith('test-token')
    expect(store.user).toEqual({
      user_name: 'TestUser',
      cnt_requests: 10,
      cnt_tokens: 1000
    })
    expect(store.totalRequests).toBe(10)
    expect(store.totalTokens).toBe(1000)
    expect(store.isAuthenticated).toBe(true)
  })

  it('clears user data on logout', () => {
    const store = useAuthStore()

    // Set some initial state
    store.user = { user_name: 'TestUser', cnt_requests: 10, cnt_tokens: 1000 }
    store.totalRequests = 10
    store.totalTokens = 1000

    store.logout()

    expect(store.user).toBeNull()
    expect(store.totalRequests).toBe(0)
    expect(store.totalTokens).toBe(0)
    expect(store.error).toBeNull()
  })

  it('updates usage statistics', () => {
    const store = useAuthStore()

    store.updateUsage(42, 5000)

    expect(store.totalRequests).toBe(42)
    expect(store.totalTokens).toBe(5000)
  })
})
