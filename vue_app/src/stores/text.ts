/**
 * Text processing store using Pinia
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { TextRequest, type TextResponse } from '@/api'

export const useTextStore = defineStore('text', () => {
  const selectedMode = ref<TextRequest.mode>(TextRequest.mode.CORRECT)
  const selectedModel = ref<string>('')
  const availableModels = ref<string[]>([])
  const inputText = ref('')
  const outputText = ref('')
  const diffHtml = ref('')
  const lastResult = ref<TextResponse | null>(null)
  const error = ref<string | null>(null)
  const llmProvider = ref<string>('')

  function setInputText(text: string) {
    inputText.value = text
  }

  function setOutputText(text: string) {
    outputText.value = text
  }

  function setMode(mode: TextRequest.mode) {
    selectedMode.value = mode
  }

  function setModel(model: string) {
    selectedModel.value = model
  }

  function setAvailableModels(models: string[]) {
    availableModels.value = models
  }

  function setDiffHtml(html: string) {
    diffHtml.value = html
  }

  function setLastResult(result: TextResponse | null) {
    lastResult.value = result
  }

  function setError(err: string | null) {
    error.value = err
  }

  function setLlmProvider(provider: string) {
    llmProvider.value = provider
  }

  function clearOutput() {
    outputText.value = ''
    diffHtml.value = ''
    lastResult.value = null
    error.value = null
  }

  function clearAll() {
    inputText.value = ''
    outputText.value = ''
    diffHtml.value = ''
    lastResult.value = null
    error.value = null
    selectedMode.value = TextRequest.mode.CORRECT
  }

  return {
    selectedMode,
    selectedModel,
    availableModels,
    inputText,
    outputText,
    diffHtml,
    lastResult,
    error,
    llmProvider,
    setInputText,
    setOutputText,
    setMode,
    setModel,
    setAvailableModels,
    setDiffHtml,
    setLastResult,
    setError,
    setLlmProvider,
    clearOutput,
    clearAll
  }
})
