import { describe, it, expect } from 'vitest'
import { generateDiff } from '../diff'

describe('generateDiff', () => {
  it('should generate HTML diff between two texts', () => {
    const original = 'Hello world'
    const improved = 'Hello beautiful world'

    const result = generateDiff(original, improved)

    expect(result).toBeTruthy()
    expect(result).toContain('d2h-wrapper')
  })

  it('should handle identical texts', () => {
    const text = 'Same text'

    const result = generateDiff(text, text)

    expect(result).toBeTruthy()
  })

  it('should handle empty strings', () => {
    const result = generateDiff('', '')

    expect(result).toBeTruthy()
  })

  it('should remove line numbers from diff', () => {
    const original = 'Line 1\nLine 2'
    const improved = 'Line 1\nLine 2 modified'

    const result = generateDiff(original, improved)

    // Check that line number elements are removed
    expect(result).not.toContain('d2h-code-linenumber')
    expect(result).not.toContain('d2h-code-side-linenumber')
  })
})
