/**
 * Composable for clipboard operations with Quasar notifications
 */

import { useQuasar } from 'quasar'
import { copyToClipboard as copyText, readFromClipboard } from '@/utils/clipboard'

export function useClipboard() {
  const $q = useQuasar()

  /**
   * Copy text to clipboard with user notification
   */
  async function copyToClipboard(text: string) {
    try {
      await copyText(text)
      $q.notify({ type: 'positive', message: 'Kopiert!' })
    } catch {
      $q.notify({ type: 'negative', message: 'Kopieren fehlgeschlagen' })
    }
  }

  /**
   * Paste text from clipboard
   * Returns the pasted text or empty string on failure
   */
  async function pasteFromClipboard(): Promise<string> {
    try {
      return await readFromClipboard()
    } catch (err) {
      console.error('Failed to paste:', err)
      return ''
    }
  }

  return {
    copyToClipboard,
    pasteFromClipboard
  }
}
