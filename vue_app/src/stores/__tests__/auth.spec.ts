import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useAuthStore } from '../auth'

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
    vi.clearAllMocks()
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

    vi.mocked(api.auth.loginApiAuthLoginPost).mockResolvedValue({
      data: mockLoginResponse
    } as never)
    vi.mocked(api.config.getConfigApiConfigGet).mockResolvedValue({
      data: mockConfigResponse
    } as never)
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

  it('throws and sets error when login fails', async () => {
    const { api } = await import('@/services/apiClient')

    vi.mocked(api.auth.loginApiAuthLoginPost).mockRejectedValue(new Error('Wrong secret'))

    const store = useAuthStore()
    await expect(store.login('bad-secret')).rejects.toThrow('Wrong secret')

    expect(store.error).toBe('Wrong secret')
    expect(store.isLoading).toBe(false)
    expect(store.isAuthenticated).toBe(false)
  })

  it('throws and sets error when login response has no token', async () => {
    const { api } = await import('@/services/apiClient')

    vi.mocked(api.auth.loginApiAuthLoginPost).mockResolvedValue({ data: undefined } as never)

    const store = useAuthStore()
    await expect(store.login('test-secret')).rejects.toThrow('Login failed')

    expect(store.error).toBe('Login failed')
  })

  it('throws when received token cannot be decoded', async () => {
    const { api } = await import('@/services/apiClient')
    const { decodeJwt } = await import('@/utils/jwt')

    vi.mocked(api.auth.loginApiAuthLoginPost).mockResolvedValue({
      data: { access_token: 'test-token', token_type: 'bearer' }
    } as never)
    vi.mocked(decodeJwt).mockReturnValue(null)

    const store = useAuthStore()
    await expect(store.login('test-secret')).rejects.toThrow(
      'Failed to decode authentication token'
    )

    expect(store.error).toBe('Failed to decode authentication token')
    expect(store.isAuthenticated).toBe(false)
  })

  it('logs out when no token is stored', async () => {
    const { tokenManager } = await import('@/services/apiClient')

    vi.mocked(tokenManager.get).mockReturnValue(null)

    const store = useAuthStore()
    store.loadUserFromToken()

    expect(tokenManager.clear).toHaveBeenCalled()
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })

  it('logs out when stored token is expired', async () => {
    const { tokenManager } = await import('@/services/apiClient')
    const { isTokenExpired } = await import('@/utils/jwt')

    vi.mocked(tokenManager.get).mockReturnValue('expired-token')
    vi.mocked(isTokenExpired).mockReturnValue(true)

    const store = useAuthStore()
    store.loadUserFromToken()

    expect(tokenManager.clear).toHaveBeenCalled()
    expect(store.user).toBeNull()
  })

  it('loads user from a valid stored token', async () => {
    const { tokenManager } = await import('@/services/apiClient')
    const { isTokenExpired, decodeJwt } = await import('@/utils/jwt')

    vi.mocked(tokenManager.get).mockReturnValue('valid-token')
    vi.mocked(isTokenExpired).mockReturnValue(false)
    vi.mocked(decodeJwt).mockReturnValue({
      user_id: 1,
      username: 'TestUser',
      exp: Math.floor(Date.now() / 1000) + 3600
    })

    const store = useAuthStore()
    store.loadUserFromToken()

    expect(store.user).toEqual({ user_name: 'TestUser' })
    expect(store.isAuthenticated).toBe(true)
    expect(tokenManager.clear).not.toHaveBeenCalled()
  })
})
