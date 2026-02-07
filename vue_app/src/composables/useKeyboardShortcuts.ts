/**
 * Composable for keyboard shortcuts
 */

import { onMounted, onUnmounted } from 'vue'

interface KeyboardShortcutOptions {
  onEscape?: () => void
  onCtrlEnter?: () => void
}

export function useKeyboardShortcuts(options: KeyboardShortcutOptions = {}) {
  function handleGlobalKeyPress(event: KeyboardEvent) {
    if (event.key === 'Escape') options.onEscape?.()
  }

  function handleTextareaKeydown(event: KeyboardEvent, canSubmit: boolean) {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey) && canSubmit) {
      event.preventDefault()
      options.onCtrlEnter?.()
    }
  }

  onMounted(() => {
    globalThis.addEventListener('keydown', handleGlobalKeyPress)
  })
  onUnmounted(() => {
    globalThis.removeEventListener('keydown', handleGlobalKeyPress)
  })

  return { handleTextareaKeydown }
}
