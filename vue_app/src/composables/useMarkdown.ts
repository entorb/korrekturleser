/**
 * Composable for markdown rendering
 */

import { marked, type RendererThis, type Tokens } from 'marked'
import { type ComputedRef, computed } from 'vue'

const renderer = {
  link(this: RendererThis, { href, title, tokens }: Tokens.Link) {
    const text = this.parser.parseInline(tokens)
    const titleAttr = title ? ` title="${title}"` : ''
    return `<a href="${href}" target="_blank" rel="noopener noreferrer"${titleAttr}>${text}</a>`
  }
}

marked.use({ renderer })

export function useMarkdown(
  text: () => string,
  shouldRender: ComputedRef<boolean | string | number>
) {
  const markdownHtml = computed(() => {
    const renderValue = shouldRender.value
    const shouldShow =
      (typeof renderValue === 'boolean' && renderValue) ||
      (typeof renderValue === 'string' && renderValue.trim().length > 0) ||
      (typeof renderValue === 'number' && renderValue !== 0)

    return shouldShow ? marked.parse(text()) : ''
  })

  return { markdownHtml }
}
