import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTextStore } from './text'
import { TextRequest } from '@/api'

describe('Text Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with default values', () => {
    const store = useTextStore()

    expect(store.selectedMode).toBe(TextRequest.mode.CORRECT)
    expect(store.inputText).toBe('')
    expect(store.outputText).toBe('')
    expect(store.diffHtml).toBe('')
    expect(store.lastResult).toBeNull()
    expect(store.error).toBeNull()
  })

  it('updates input text', () => {
    const store = useTextStore()
    store.inputText = 'Hello world'
    expect(store.inputText).toBe('Hello world')
  })

  it('updates output text', () => {
    const store = useTextStore()
    store.outputText = 'Corrected text'
    expect(store.outputText).toBe('Corrected text')
  })

  it('changes mode', () => {
    const store = useTextStore()
    store.selectedMode = TextRequest.mode.IMPROVE
    expect(store.selectedMode).toBe(TextRequest.mode.IMPROVE)
  })

  it('sets diff HTML', () => {
    const store = useTextStore()
    store.diffHtml = '<div>diff</div>'
    expect(store.diffHtml).toBe('<div>diff</div>')
  })

  it('clears output while preserving input', () => {
    const store = useTextStore()

    store.inputText = 'Input text'
    store.outputText = 'Output text'
    store.diffHtml = '<div>diff</div>'
    store.error = 'Some error'

    store.clearOutput()

    expect(store.inputText).toBe('Input text')
    expect(store.outputText).toBe('')
    expect(store.diffHtml).toBe('')
    expect(store.lastResult).toBeNull()
    expect(store.error).toBeNull()
  })

  it('clears all data including input', () => {
    const store = useTextStore()

    store.inputText = 'Input text'
    store.outputText = 'Output text'
    store.selectedMode = TextRequest.mode.SUMMARIZE
    store.diffHtml = '<div>diff</div>'

    store.clearAll()

    expect(store.inputText).toBe('')
    expect(store.outputText).toBe('')
    expect(store.diffHtml).toBe('')
    expect(store.lastResult).toBeNull()
    expect(store.error).toBeNull()
    expect(store.selectedMode).toBe(TextRequest.mode.CORRECT)
  })

  it('sets last result', () => {
    const store = useTextStore()
    const mockResult = {
      text_original: 'Original',
      text_ai: 'Improved',
      mode: TextRequest.mode.IMPROVE,
      tokens_used: 100,
      model: 'gemini-2.5-flash',
      provider: 'Gemini'
    }

    store.lastResult = mockResult

    expect(store.lastResult).toEqual(mockResult)
  })
})
