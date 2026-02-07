/**
 * Composable for managing LLM provider and model configuration
 */

import { computed } from 'vue'
import { api } from '@/services/apiClient'
import { useTextStore } from '@/stores/text'

export function useConfig() {
  const textStore = useTextStore()

  // Show disclaimer for Gemini provider
  const showDisclaimer = computed(() => {
    return textStore.selectedProvider === 'Gemini'
  })

  /**
   * Fetch available providers and models
   */
  async function fetchProvidersAndModels() {
    try {
      const response = await api.config.getConfigApiConfigGet(
        textStore.selectedProvider || undefined
      )
      textStore.setAvailableModels(response.models)
      textStore.setAvailableProviders(response.providers)

      // Set first model as default if not already set
      if (!textStore.selectedModel && response.models.length > 0) {
        const firstModel = response.models[0]
        if (firstModel) {
          textStore.setModel(firstModel)
        }
      }

      // Set first provider as default if not already set
      if (!textStore.selectedProvider && response.providers.length > 0) {
        const firstProvider = response.providers[0]
        if (firstProvider) {
          textStore.setProvider(firstProvider)
        }
      }
    } catch (err) {
      console.error('Failed to fetch models:', err)
      textStore.setError('Fehler beim Laden der Modelle')
    }
  }

  /**
   * Handle provider change - fetch new models for selected provider
   */
  async function handleProviderChange() {
    try {
      const response = await api.config.getConfigApiConfigGet(
        textStore.selectedProvider || undefined
      )

      // Update available models from response
      textStore.setAvailableModels(response.models)

      // Reset selected model to first available model from new provider
      if (response.models.length > 0) {
        const firstModel = response.models[0]
        if (firstModel) {
          textStore.setModel(firstModel)
        }
      }
    } catch (err) {
      console.error('Failed to fetch models:', err)
      textStore.setError('Fehler beim Laden der Modelle')
    }
  }

  return {
    showDisclaimer,
    fetchProvidersAndModels,
    handleProviderChange
  }
}
