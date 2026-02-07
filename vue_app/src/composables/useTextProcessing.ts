/**
 * Composable for text processing logic
 * Handles AI text improvement, diff generation, and markdown rendering
 */

import { ref, computed } from 'vue'
import { api } from '@/services/apiClient'
import { TextRequest } from '@/api'
import { useTextStore } from '@/stores/text'
import { generateDiff } from '@/utils/diff'

export function useTextProcessing() {
  const textStore = useTextStore()
  const isProcessing = ref(false)

  // Show diff for correct and improve modes only
  const showDiff = computed(() => {
    return (
      textStore.outputText &&
      (textStore.selectedMode === TextRequest.mode.CORRECT ||
        textStore.selectedMode === TextRequest.mode.IMPROVE)
    )
  })

  // Show markdown rendering for summarize mode
  const showMarkdown = computed(() => {
    return textStore.outputText && textStore.selectedMode === TextRequest.mode.SUMMARIZE
  })

  /**
   * Process text with AI
   */
  async function processText() {
    if (!textStore.inputText) return

    isProcessing.value = true
    textStore.setError(null)
    textStore.setOutputText('')
    textStore.setDiffHtml('')

    try {
      const result = await api.text.improveTextApiTextPost({
        text: textStore.inputText,
        mode: textStore.selectedMode,
        model: textStore.selectedModel || null,
        provider: textStore.selectedProvider || null
      })

      textStore.setOutputText(result.text_ai)
      textStore.setLastResult(result)

      // Generate diff for correct/improve modes
      if (
        textStore.selectedMode === TextRequest.mode.CORRECT ||
        textStore.selectedMode === TextRequest.mode.IMPROVE
      ) {
        const diffHtml = generateDiff(`${textStore.inputText}\n\n`, `${result.text_ai}\n\n`)
        textStore.setDiffHtml(diffHtml)
      }
    } catch (err) {
      textStore.setError(err instanceof Error ? err.message : 'Fehler bei der Textverarbeitung')
      console.error('Text processing error:', err)
    } finally {
      isProcessing.value = false
    }
  }

  /**
   * Transfer AI output to input field
   */
  function transferAiTextToInput() {
    textStore.setInputText(textStore.outputText)
    textStore.setOutputText('')
  }

  /**
   * Reset all input and output
   */
  function resetInput() {
    textStore.setInputText('')
    textStore.setOutputText('')
    textStore.setDiffHtml('')
    textStore.setError(null)
  }

  return {
    isProcessing,
    showDiff,
    showMarkdown,
    processText,
    transferAiTextToInput,
    resetInput
  }
}
