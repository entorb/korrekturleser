/**
 * Text processing store using Pinia
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

import { TextRequest, type TextResponse } from '@/api'

export const useTextStore = defineStore('text', () => {
  const selectedMode = ref<TextRequest.mode>(TextRequest.mode.CORRECT)
  const selectedModel = ref('')
  const availableModels = ref<string[]>([])
  const selectedProvider = ref('')
  const availableProviders = ref<string[]>([])
  const inputText = ref('')
  const outputText = ref('')
  const diffHtml = ref('')
  const lastResult = ref<TextResponse | null>(null)
  const error = ref<string | null>(null)
  const customInstruction = ref('')

  function clearOutput() {
    outputText.value = ''
    diffHtml.value = ''
    lastResult.value = null
    error.value = null
  }

  function clearAll() {
    inputText.value = ''
    clearOutput()
    selectedMode.value = TextRequest.mode.CORRECT
    customInstruction.value = ''
  }

  return {
    selectedMode,
    selectedModel,
    availableModels,
    selectedProvider,
    availableProviders,
    inputText,
    outputText,
    diffHtml,
    lastResult,
    error,
    customInstruction,
    clearOutput,
    clearAll
  }
})
