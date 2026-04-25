/**
 * Composable for managing LLM provider and model configuration
 */

import { computed } from 'vue'

import { api } from '@/services/apiClient'
import { useTextStore } from '@/stores/text'

export function useConfig() {
  const textStore = useTextStore()

  const showDisclaimer = computed(() => textStore.selectedProvider === 'Google')

  async function fetchProvidersAndModels() {
    try {
      const { data: response } = await api.config.getConfigApiConfigGet({
        query: { provider: textStore.selectedProvider || null }
      })
      if (!response) return
      textStore.availableModels = response.models
      textStore.availableProviders = response.providers

      if (!textStore.selectedModel && response.models.length > 0) {
        textStore.selectedModel = response.models[0] ?? ''
      }
      if (!textStore.selectedProvider && response.providers.length > 0) {
        textStore.selectedProvider = response.providers[0] ?? ''
      }
    } catch {
      textStore.error = 'Fehler beim Laden der Modelle'
    }
  }

  async function handleProviderChange() {
    try {
      const { data: response } = await api.config.getConfigApiConfigGet({
        query: { provider: textStore.selectedProvider || null }
      })
      if (!response) return
      textStore.availableModels = response.models

      if (response.models.length > 0) {
        textStore.selectedModel = response.models[0] ?? ''
      }
    } catch {
      textStore.error = 'Fehler beim Laden der Modelle'
    }
  }

  return {
    showDisclaimer,
    fetchProvidersAndModels,
    handleProviderChange
  }
}
