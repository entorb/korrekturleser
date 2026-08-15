import { describe, expect, it } from 'vitest'
import { computed, ref } from 'vue'
import { useMarkdown } from '../useMarkdown'

describe('useMarkdown', () => {
  it('renders markdown when shouldRender is true', () => {
    const text = ref('**bold**')
    const shouldRender = computed(() => true)

    const { markdownHtml } = useMarkdown(() => text.value, shouldRender)

    expect(markdownHtml.value).toContain('<strong>bold</strong>')
  })

  it('returns empty when shouldRender is false', () => {
    const text = ref('**bold**')
    const shouldRender = computed(() => false)

    const { markdownHtml } = useMarkdown(() => text.value, shouldRender)

    expect(markdownHtml.value).toBe('')
  })

  it('returns empty for empty string value', () => {
    const text = ref('**bold**')
    const shouldRender = computed(() => '')

    const { markdownHtml } = useMarkdown(() => text.value, shouldRender)

    expect(markdownHtml.value).toBe('')
  })

  it('renders for non-empty string value', () => {
    const text = ref('# Title')
    const shouldRender = computed(() => 'summarize')

    const { markdownHtml } = useMarkdown(() => text.value, shouldRender)

    expect(markdownHtml.value).toContain('<h1>Title</h1>')
  })

  it('renders for non-zero number value', () => {
    const text = ref('text')
    const shouldRender = computed(() => 42)

    const { markdownHtml } = useMarkdown(() => text.value, shouldRender)

    expect(markdownHtml.value).toContain('text')
  })

  it('returns empty for zero number value', () => {
    const text = ref('text')
    const shouldRender = computed(() => 0)

    const { markdownHtml } = useMarkdown(() => text.value, shouldRender)

    expect(markdownHtml.value).toBe('')
  })
})
