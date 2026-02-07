/**
 * Composable for text processing logic
 * Handles AI text improvement, diff generation, and markdown rendering
 */

import { ref, computed } from 'vue'

import { TextRequest } from '@/api'
import { api } from '@/services/apiClient'
import { useTextStore } from '@/stores/text'
import { generateDiff } from '@/utils/diff'

export function useTextProcessing() {
  const textStore = useTextStore()
  const isProcessing = ref(false)

  const showDiff = computed(
    () =>
      textStore.outputText &&
      (textStore.selectedMode === TextRequest.mode.CORRECT ||
        textStore.selectedMode === TextRequest.mode.IMPROVE)
  )

  const showMarkdown = computed(
    () => textStore.outputText && textStore.selectedMode === TextRequest.mode.SUMMARIZE
  )

  async function processText() {
    if (!textStore.inputText) return

    isProcessing.value = true
    textStore.error = null
    textStore.outputText = ''
    textStore.diffHtml = ''

    try {
      const result = await api.text.improveTextApiTextPost({
        text: textStore.inputText,
        mode: textStore.selectedMode,
        model: textStore.selectedModel || null,
        provider: textStore.selectedProvider || null
      })

      textStore.outputText = result.text_ai
      textStore.lastResult = result

      if (showDiff.value === true) {
        textStore.diffHtml = generateDiff(`${textStore.inputText}\n\n`, `${result.text_ai}\n\n`)
      }
    } catch (err) {
      textStore.error = err instanceof Error ? err.message : 'Fehler bei der Textverarbeitung'
    } finally {
      isProcessing.value = false
    }
  }

  function transferAiTextToInput() {
    textStore.inputText = textStore.outputText
    textStore.outputText = ''
  }

  return {
    isProcessing,
    showDiff,
    showMarkdown,
    processText,
    transferAiTextToInput,
    resetInput: textStore.clearAll
  }
}
