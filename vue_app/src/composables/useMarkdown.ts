/**
 * Composable for markdown rendering
 */

import { computed, type ComputedRef } from 'vue'
import { marked } from 'marked'

export function useMarkdown(
  text: () => string,
  shouldRender: ComputedRef<boolean | string | number>
) {
  /**
   * Convert markdown to HTML
   */
  const markdownHtml = computed(async () => {
    if (!shouldRender.value) return ''
    return marked(text())
  })

  return {
    markdownHtml
  }
}
