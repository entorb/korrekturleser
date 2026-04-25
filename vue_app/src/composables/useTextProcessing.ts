/**
 * Composable for text processing logic
 * Handles AI text improvement, diff generation, and markdown rendering
 */

import { computed, ref } from 'vue'

import type { TextRequest, TextResponse } from '@/api'
import { api } from '@/services/apiClient'
import { useTextStore } from '@/stores/text'
import { generateDiff } from '@/utils/diff'

export function useTextProcessing() {
  const textStore = useTextStore()
  const isProcessing = ref(false)

  const showDiff = computed(
    () =>
      textStore.outputText &&
      (textStore.selectedMode === 'correct' || textStore.selectedMode === 'improve')
  )

  const showMarkdown = computed(
    () => textStore.outputText && textStore.selectedMode === 'summarize'
  )

  function buildTextRequest(): TextRequest {
    return {
      text: textStore.inputText,
      mode: textStore.selectedMode,
      custom_instruction:
        textStore.selectedMode === 'custom' ? textStore.customInstruction || null : null,
      model: textStore.selectedModel || null,
      provider: textStore.selectedProvider || null
    }
  }

  function handleResult(result: TextResponse) {
    textStore.outputText = result.text_ai
    textStore.lastResult = result

    if (showDiff.value) {
      textStore.diffHtml = generateDiff(`${textStore.inputText}\n\n`, `${result.text_ai}\n\n`)
    }
  }

  async function processText() {
    if (!textStore.inputText) return

    isProcessing.value = true
    textStore.error = null
    textStore.outputText = ''
    textStore.diffHtml = ''

    try {
      const body = buildTextRequest()
      const { data: result } = await api.text.improveTextApiTextPost({ body })

      if (!result) throw new Error('No response from API')

      handleResult(result)
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
