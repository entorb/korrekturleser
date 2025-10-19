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
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })

  it('sets user as authenticated after successful login', async () => {
    const { api, tokenManager } = await import('@/services/apiClient')
    const mockLoginResponse = {
      access_token: 'test-token',
      token_type: 'bearer'
    }
    const mockUserInfo = {
      user_name: 'TestUser'
    }

    vi.mocked(api.auth.loginApiAuthLoginPost).mockResolvedValue(mockLoginResponse)
    vi.mocked(api.auth.getMeApiAuthMeGet).mockResolvedValue(mockUserInfo)
    vi.mocked(tokenManager.exists).mockReturnValue(true)

    const store = useAuthStore()
    await store.login('test-secret')

    expect(tokenManager.set).toHaveBeenCalledWith('test-token')
    expect(store.user).toEqual({
      user_name: 'TestUser'
    })
    expect(store.isAuthenticated).toBe(true)
  })

  it('clears user data on logout', () => {
    const store = useAuthStore()

    // Set some initial state
    store.user = { user_name: 'TestUser' }

    store.logout()

    expect(store.user).toBeNull()
    expect(store.error).toBeNull()
  })
})
