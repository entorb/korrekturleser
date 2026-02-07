import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useClipboard } from '../useClipboard'

// Mock Quasar
vi.mock('quasar', () => ({
  useQuasar: () => ({
    notify: vi.fn()
  })
}))

// Mock clipboard utilities
vi.mock('@/utils/clipboard', () => ({
  copyToClipboard: vi.fn(),
  readFromClipboard: vi.fn()
}))

describe('useClipboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should copy text to clipboard successfully', async () => {
    const { copyToClipboard: copyText } = await import('@/utils/clipboard')
    vi.mocked(copyText).mockResolvedValue()

    const { copyToClipboard } = useClipboard()
    await copyToClipboard('test text')

    expect(copyText).toHaveBeenCalledWith('test text')
  })

  it('should paste text from clipboard successfully', async () => {
    const { readFromClipboard } = await import('@/utils/clipboard')
    vi.mocked(readFromClipboard).mockResolvedValue('pasted text')

    const { pasteFromClipboard } = useClipboard()
    const result = await pasteFromClipboard()

    expect(result).toBe('pasted text')
    expect(readFromClipboard).toHaveBeenCalled()
  })

  it('should return empty string when paste fails', async () => {
    const { readFromClipboard } = await import('@/utils/clipboard')
    vi.mocked(readFromClipboard).mockRejectedValue(new Error('Clipboard error'))

    const { pasteFromClipboard } = useClipboard()
    const result = await pasteFromClipboard()

    expect(result).toBe('')
  })
})
