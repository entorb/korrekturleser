import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTextStore } from '../text'
import { TextMode } from '@/api'

describe('Text Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with default values', () => {
    const store = useTextStore()

    expect(store.selectedMode).toBe(TextMode.CORRECT)
    expect(store.inputText).toBe('')
    expect(store.outputText).toBe('')
    expect(store.diffHtml).toBe('')
    expect(store.lastResult).toBeNull()
    expect(store.error).toBeNull()
  })

  it('updates input text', () => {
    const store = useTextStore()

    store.setInputText('Hello world')

    expect(store.inputText).toBe('Hello world')
  })

  it('updates output text', () => {
    const store = useTextStore()

    store.setOutputText('Corrected text')

    expect(store.outputText).toBe('Corrected text')
  })

  it('changes mode', () => {
    const store = useTextStore()

    store.setMode(TextMode.IMPROVE)

    expect(store.selectedMode).toBe(TextMode.IMPROVE)
  })

  it('sets diff HTML', () => {
    const store = useTextStore()

    store.setDiffHtml('<div>diff</div>')

    expect(store.diffHtml).toBe('<div>diff</div>')
  })

  it('clears output while preserving input', () => {
    const store = useTextStore()

    // Set some data
    store.setInputText('Input text')
    store.setOutputText('Output text')
    store.setDiffHtml('<div>diff</div>')
    store.setError('Some error')

    store.clearOutput()

    expect(store.inputText).toBe('Input text') // Should NOT be cleared
    expect(store.outputText).toBe('')
    expect(store.diffHtml).toBe('')
    expect(store.lastResult).toBeNull()
    expect(store.error).toBeNull()
  })

  it('clears all data including input', () => {
    const store = useTextStore()

    // Set some data
    store.setInputText('Input text')
    store.setOutputText('Output text')
    store.setMode(TextMode.SUMMARIZE)
    store.setDiffHtml('<div>diff</div>')

    store.clearAll()

    expect(store.inputText).toBe('')
    expect(store.outputText).toBe('')
    expect(store.diffHtml).toBe('')
    expect(store.lastResult).toBeNull()
    expect(store.error).toBeNull()
    expect(store.selectedMode).toBe(TextMode.CORRECT) // Reset to default
  })

  it('sets last result', () => {
    const store = useTextStore()
    const mockResult = {
      text_original: 'Original',
      text_ai: 'Improved',
      mode: TextMode.IMPROVE,
      tokens_used: 100,
      model: 'gemini-2.5-flash'
    }

    store.setLastResult(mockResult)

    expect(store.lastResult).toEqual(mockResult)
  })
})
