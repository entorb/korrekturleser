/**
 * Text processing store using Pinia
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { TextMode, type ImproveResponse } from '@/api'

export const useTextStore = defineStore('text', () => {
  const selectedMode = ref<TextMode>(TextMode.CORRECT)
  const inputText = ref('')
  const outputText = ref('')
  const diffHtml = ref('')
  const lastResult = ref<ImproveResponse | null>(null)
  const error = ref<string | null>(null)

  function setInputText(text: string) {
    inputText.value = text
  }

  function setOutputText(text: string) {
    outputText.value = text
  }

  function setMode(mode: TextMode) {
    selectedMode.value = mode
  }

  function setDiffHtml(html: string) {
    diffHtml.value = html
  }

  function setLastResult(result: ImproveResponse | null) {
    lastResult.value = result
  }

  function setError(err: string | null) {
    error.value = err
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
    selectedMode.value = TextMode.CORRECT
  }

  return {
    selectedMode,
    inputText,
    outputText,
    diffHtml,
    lastResult,
    error,
    setInputText,
    setOutputText,
    setMode,
    setDiffHtml,
    setLastResult,
    setError,
    clearOutput,
    clearAll
  }
})
