/**
 * Diff generation utilities
 * Generates side-by-side HTML diff with cleaned up formatting
 */

import { html } from 'diff2html'
import { createTwoFilesPatch } from 'diff'

/**
 * Generate HTML diff between original and improved text
 * Removes line numbers and +/- signs for cleaner display
 */
export function generateDiff(original: string, improved: string): string {
  const patch = createTwoFilesPatch('', '', original, improved, '', '', {
    context: 3
  })

  const diffHtml = html(patch, {
    drawFileList: false,
    matching: 'words',
    outputFormat: 'side-by-side',
    renderNothingWhenEmpty: false
  })

  // Clean up the diff HTML: remove line numbers and +/- signs
  const parser = new DOMParser()
  const doc = parser.parseFromString(diffHtml, 'text/html')

  // Remove all line number columns (both types)
  doc.querySelectorAll('.d2h-file-header').forEach(el => {
    el.remove()
  })
  doc.querySelectorAll('.d2h-info').forEach(el => {
    el.remove()
  })
  doc.querySelectorAll('.d2h-code-linenumber').forEach(el => {
    el.remove()
  })
  doc.querySelectorAll('.d2h-code-side-linenumber').forEach(el => {
    el.remove()
  })

  // Remove +/- sign prefix spans
  doc.querySelectorAll('.d2h-code-line-prefix').forEach(el => {
    el.remove()
  })

  return doc.body.innerHTML
}
