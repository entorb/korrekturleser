/**
 * Composable for clipboard operations with Quasar notifications
 */

import { useQuasar } from 'quasar'
import { copyToClipboard as copyText, readFromClipboard } from '@/utils/clipboard'

export function useClipboard() {
  const $q = useQuasar()

  async function copyToClipboard(text: string) {
    try {
      await copyText(text)
      $q.notify({ type: 'positive', message: 'Kopiert!' })
    } catch {
      $q.notify({ type: 'negative', message: 'Kopieren fehlgeschlagen' })
    }
  }

  async function pasteFromClipboard(): Promise<string> {
    try {
      return await readFromClipboard()
    } catch {
      return ''
    }
  }

  return { copyToClipboard, pasteFromClipboard }
}
