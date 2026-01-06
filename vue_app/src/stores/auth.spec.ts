import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from './auth'

// Mock the JWT utilities
vi.mock('@/utils/jwt', () => ({
  decodeJwt: vi.fn(),
  isTokenExpired: vi.fn()
}))

// Mock the API client
vi.mock('@/services/apiClient', () => ({
  api: {
    auth: {
      loginApiAuthLoginPost: vi.fn()
    },
    config: {
      getConfigApiConfigGet: vi.fn()
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
    const { decodeJwt, isTokenExpired } = await import('@/utils/jwt')

    const mockLoginResponse = {
      access_token: 'test-token',
      token_type: 'bearer'
    }
    const mockConfigResponse = {
      provider: 'Gemini',
      models: ['gemini-2.5-flash', 'gemini-2.5-pro'],
      providers: ['Gemini', 'OpenAI']
    }
    const mockPayload = {
      user_id: 1,
      username: 'TestUser',
      exp: Math.floor(Date.now() / 1000) + 3600
    }

    vi.mocked(api.auth.loginApiAuthLoginPost).mockResolvedValue(mockLoginResponse)
    vi.mocked(api.config.getConfigApiConfigGet).mockResolvedValue(mockConfigResponse)
    vi.mocked(tokenManager.get).mockReturnValue('test-token')
    vi.mocked(isTokenExpired).mockReturnValue(false)
    vi.mocked(decodeJwt).mockReturnValue(mockPayload)

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
