/**
 * Diff generation utilities
 */

import { html } from 'diff2html'
import { createTwoFilesPatch } from 'diff'

export function generateDiff(original: string, improved: string): string {
  const patch = createTwoFilesPatch('', '', original, improved, '', '', { context: 3 })
  const diffHtml = html(patch, {
    drawFileList: false,
    matching: 'words',
    outputFormat: 'side-by-side',
    renderNothingWhenEmpty: false
  })

  const doc = new DOMParser().parseFromString(diffHtml, 'text/html')

  // Remove unnecessary elements
  doc
    .querySelectorAll(
      '.d2h-file-header, .d2h-info, .d2h-code-linenumber, .d2h-code-side-linenumber, .d2h-code-line-prefix'
    )
    .forEach(el => {
      el.remove()
    })

  return doc.body.innerHTML
}
