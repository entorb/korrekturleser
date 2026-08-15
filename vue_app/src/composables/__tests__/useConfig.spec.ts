import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useTextStore } from '@/stores/text'
import { useConfig } from '../useConfig'

vi.mock('@/services/apiClient', () => ({
  api: {
    config: {
      getConfigApiConfigGet: vi.fn()
    }
  }
}))

describe('useConfig', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('shows disclaimer only for Google provider', () => {
    const store = useTextStore()
    const { showDisclaimer } = useConfig()

    store.selectedProvider = 'Google'
    expect(showDisclaimer.value).toBe(true)

    store.selectedProvider = 'OpenAI'
    expect(showDisclaimer.value).toBe(false)

    store.selectedProvider = ''
    expect(showDisclaimer.value).toBe(false)
  })

  it('fetches providers and models and selects defaults', async () => {
    const store = useTextStore()
    const { fetchProvidersAndModels } = useConfig()
    const { api } = await import('@/services/apiClient')

    vi.mocked(api.config.getConfigApiConfigGet).mockResolvedValue({
      data: { models: ['m1', 'm2'], providers: ['p1', 'p2'] }
    } as never)

    await fetchProvidersAndModels()

    expect(store.availableModels).toEqual(['m1', 'm2'])
    expect(store.availableProviders).toEqual(['p1', 'p2'])
    expect(store.selectedModel).toBe('m1')
    expect(store.selectedProvider).toBe('p1')
  })

  it('keeps existing provider when fetching', async () => {
    const store = useTextStore()
    const { fetchProvidersAndModels } = useConfig()
    const { api } = await import('@/services/apiClient')

    store.selectedProvider = 'p2'

    vi.mocked(api.config.getConfigApiConfigGet).mockResolvedValue({
      data: { models: ['m1', 'm2'], providers: ['p1', 'p2'] }
    } as never)

    await fetchProvidersAndModels()

    expect(store.selectedProvider).toBe('p2')
    expect(store.selectedModel).toBe('m1')
  })

  it('keeps existing model and provider when already set', async () => {
    const store = useTextStore()
    const { fetchProvidersAndModels } = useConfig()
    const { api } = await import('@/services/apiClient')

    store.selectedModel = 'm2'
    store.selectedProvider = 'p2'

    vi.mocked(api.config.getConfigApiConfigGet).mockResolvedValue({
      data: { models: ['m1', 'm2'], providers: ['p1', 'p2'] }
    } as never)

    await fetchProvidersAndModels()

    expect(store.selectedModel).toBe('m2')
    expect(store.selectedProvider).toBe('p2')
  })

  it('does nothing when config response has no models', async () => {
    const store = useTextStore()
    const { fetchProvidersAndModels } = useConfig()
    const { api } = await import('@/services/apiClient')

    vi.mocked(api.config.getConfigApiConfigGet).mockResolvedValue({
      data: { models: [], providers: [] }
    } as never)

    await fetchProvidersAndModels()

    expect(store.selectedModel).toBe('')
    expect(store.selectedProvider).toBe('')
  })

  it('sets error when config fetch fails', async () => {
    const store = useTextStore()
    const { fetchProvidersAndModels } = useConfig()
    const { api } = await import('@/services/apiClient')

    vi.mocked(api.config.getConfigApiConfigGet).mockRejectedValue(new Error('down'))

    await fetchProvidersAndModels()

    expect(store.error).toBe('Fehler beim Laden der Modelle')
  })

  it('sets error when handleProviderChange fails', async () => {
    const store = useTextStore()
    const { handleProviderChange } = useConfig()
    const { api } = await import('@/services/apiClient')

    store.selectedProvider = 'p1'
    vi.mocked(api.config.getConfigApiConfigGet).mockRejectedValue(new Error('down'))

    await handleProviderChange()

    expect(store.error).toBe('Fehler beim Laden der Modelle')
  })

  it('updates models on provider change', async () => {
    const store = useTextStore()
    const { handleProviderChange } = useConfig()
    const { api } = await import('@/services/apiClient')

    store.selectedProvider = 'p2'
    vi.mocked(api.config.getConfigApiConfigGet).mockResolvedValue({
      data: { models: ['m3'], providers: ['p2'] }
    } as never)

    await handleProviderChange()

    expect(api.config.getConfigApiConfigGet).toHaveBeenCalledWith({
      query: { provider: 'p2' }
    })
    expect(store.availableModels).toEqual(['m3'])
    expect(store.selectedModel).toBe('m3')
  })
})
