import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useClipboard } from '../useClipboard'

// Mock Quasar
const mockNotify = vi.fn()
vi.mock('quasar', () => ({
  useQuasar: () => ({
    notify: mockNotify
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

  it('should show success notification when copying text', async () => {
    const { copyToClipboard: copyText } = await import('@/utils/clipboard')
    vi.mocked(copyText).mockResolvedValue()

    const { copyToClipboard } = useClipboard()
    await copyToClipboard('test text')

    expect(mockNotify).toHaveBeenCalledWith({ type: 'positive', message: 'Kopiert!' })
    expect(mockNotify).toHaveBeenCalledTimes(1)
  })

  it('should paste text from clipboard successfully', async () => {
    const { readFromClipboard } = await import('@/utils/clipboard')
    vi.mocked(readFromClipboard).mockResolvedValue('pasted text')

    const { pasteFromClipboard } = useClipboard()
    const result = await pasteFromClipboard()

    expect(result).toBe('pasted text')
    expect(readFromClipboard).toHaveBeenCalled()
  })

  it('should return empty string when paste fails 1', async () => {
    const { readFromClipboard } = await import('@/utils/clipboard')
    vi.mocked(readFromClipboard).mockRejectedValue(new Error('Clipboard error'))

    const { pasteFromClipboard } = useClipboard()
    const result = await pasteFromClipboard()

    expect(result).toBe('')
  })

  it('should return empty string when paste fails 2', async () => {
    const { readFromClipboard } = await import('@/utils/clipboard')
    vi.mocked(readFromClipboard).mockRejectedValue(new Error('Clipboard error'))

    const { pasteFromClipboard } = useClipboard()
    const result = await pasteFromClipboard()

    expect(result).toBe('')
  })
})
