import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useTextStore } from '@/stores/text'
import { useTextProcessing } from '../useTextProcessing'

vi.mock('@/services/apiClient', () => ({
  api: {
    text: {
      improveTextApiTextPost: vi.fn()
    }
  }
}))

describe('useTextProcessing', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('shows diff only for diff-capable modes with output', () => {
    const store = useTextStore()
    const { showDiff } = useTextProcessing()

    store.outputText = 'Result'
    for (const mode of ['correct', 'improve', 'custom']) {
      store.selectedMode = mode as never
      expect(showDiff.value).toBe(true)
    }
    for (const mode of ['summarize', 'expand', 'translate_de', 'translate_en']) {
      store.selectedMode = mode as never
      expect(showDiff.value).toBe(false)
    }

    store.selectedMode = 'correct'
    store.outputText = ''
    expect(showDiff.value).toBeFalsy()
  })

  it('shows markdown only for summarize mode with output', () => {
    const store = useTextStore()
    const { showMarkdown } = useTextProcessing()

    store.outputText = 'Summary'
    store.selectedMode = 'summarize'
    expect(showMarkdown.value).toBe(true)

    store.selectedMode = 'correct'
    expect(showMarkdown.value).toBe(false)

    store.outputText = ''
    store.selectedMode = 'summarize'
    expect(showMarkdown.value).toBeFalsy()
  })

  it('builds a request with custom instruction only in custom mode', async () => {
    const store = useTextStore()
    const { processText } = useTextProcessing()
    const { api } = await import('@/services/apiClient')

    store.inputText = 'Hello'
    store.selectedMode = 'custom'
    store.customInstruction = 'Make it formal'
    store.selectedModel = 'gemini-2.5-flash'
    store.selectedProvider = 'Gemini'

    vi.mocked(api.text.improveTextApiTextPost).mockResolvedValue({
      data: { text_ai: 'Result' }
    } as never)

    await processText()

    expect(api.text.improveTextApiTextPost).toHaveBeenCalledWith({
      body: {
        text: 'Hello',
        mode: 'custom',
        custom_instruction: 'Make it formal',
        model: 'gemini-2.5-flash',
        provider: 'Gemini'
      }
    })
  })

  it('builds a request with null optional fields in non-custom mode', async () => {
    const store = useTextStore()
    const { processText } = useTextProcessing()
    const { api } = await import('@/services/apiClient')

    store.inputText = 'Hello'
    store.selectedMode = 'correct'
    store.customInstruction = 'Ignored'
    store.selectedModel = ''
    store.selectedProvider = ''

    vi.mocked(api.text.improveTextApiTextPost).mockResolvedValue({
      data: { text_ai: 'Result' }
    } as never)

    await processText()

    expect(api.text.improveTextApiTextPost).toHaveBeenCalledWith({
      body: {
        text: 'Hello',
        mode: 'correct',
        custom_instruction: null,
        model: null,
        provider: null
      }
    })
  })

  it('does not call the API when input text is empty', async () => {
    const store = useTextStore()
    const { processText, isProcessing } = useTextProcessing()
    const { api } = await import('@/services/apiClient')

    store.inputText = ''
    await processText()

    expect(api.text.improveTextApiTextPost).not.toHaveBeenCalled()
    expect(isProcessing.value).toBe(false)
  })

  it('stores result and generates diff on success', async () => {
    const store = useTextStore()
    const { processText } = useTextProcessing()
    const { api } = await import('@/services/apiClient')

    store.inputText = 'Hello world'
    store.selectedMode = 'correct'

    vi.mocked(api.text.improveTextApiTextPost).mockResolvedValue({
      data: { text_original: 'Hello world', text_ai: 'Hello beautiful world', mode: 'correct' }
    } as never)

    await processText()

    expect(store.outputText).toBe('Hello beautiful world')
    expect(store.lastResult).toEqual({
      text_original: 'Hello world',
      text_ai: 'Hello beautiful world',
      mode: 'correct'
    })
    expect(store.diffHtml).toContain('d2h-wrapper')
    expect(store.error).toBeNull()
  })

  it('does not generate diff for summarize mode', async () => {
    const store = useTextStore()
    const { processText } = useTextProcessing()
    const { api } = await import('@/services/apiClient')

    store.inputText = 'Long text'
    store.selectedMode = 'summarize'

    vi.mocked(api.text.improveTextApiTextPost).mockResolvedValue({
      data: { text_original: 'Long text', text_ai: 'Summary', mode: 'summarize' }
    } as never)

    await processText()

    expect(store.outputText).toBe('Summary')
    expect(store.diffHtml).toBe('')
  })

  it('sets error message when API call fails', async () => {
    const store = useTextStore()
    const { processText, isProcessing } = useTextProcessing()
    const { api } = await import('@/services/apiClient')

    store.inputText = 'Hello'

    vi.mocked(api.text.improveTextApiTextPost).mockRejectedValue(new Error('Network down'))

    await processText()

    expect(store.error).toBe('Network down')
    expect(isProcessing.value).toBe(false)
  })

  it('falls back to German error message for non-Error failures', async () => {
    const store = useTextStore()
    const { processText } = useTextProcessing()
    const { api } = await import('@/services/apiClient')

    store.inputText = 'Hello'

    vi.mocked(api.text.improveTextApiTextPost).mockRejectedValue('boom')

    await processText()

    expect(store.error).toBe('Fehler bei der Textverarbeitung')
  })

  it('handles missing response from API', async () => {
    const store = useTextStore()
    const { processText } = useTextProcessing()
    const { api } = await import('@/services/apiClient')

    store.inputText = 'Hello'

    vi.mocked(api.text.improveTextApiTextPost).mockResolvedValue({ data: undefined } as never)

    await processText()

    expect(store.error).toBe('No response from API')
  })

  it('transfers AI text back to input', () => {
    const store = useTextStore()
    const { transferAiTextToInput } = useTextProcessing()

    store.outputText = 'AI result'

    transferAiTextToInput()

    expect(store.inputText).toBe('AI result')
    expect(store.outputText).toBe('')
  })

  it('resets input via clearAll', () => {
    const store = useTextStore()
    const { resetInput } = useTextProcessing()

    store.inputText = 'Some text'
    store.selectedMode = 'summarize'
    store.customInstruction = 'Instruction'

    resetInput()

    expect(store.inputText).toBe('')
    expect(store.selectedMode).toBe('correct')
    expect(store.customInstruction).toBe('')
  })
})
