/**
 * Composable for markdown rendering
 */

import { marked } from 'marked'
import { computed, type ComputedRef } from 'vue'

export function useMarkdown(
  text: () => string,
  shouldRender: ComputedRef<boolean | string | number>
) {
  const markdownHtml = computed(async () => {
    const renderValue = shouldRender.value
    const shouldShow =
      (typeof renderValue === 'boolean' && renderValue) ||
      (typeof renderValue === 'string' && renderValue.trim().length > 0) ||
      (typeof renderValue === 'number' && renderValue !== 0)

    return shouldShow ? marked(text()) : ''
  })

  return { markdownHtml }
}
