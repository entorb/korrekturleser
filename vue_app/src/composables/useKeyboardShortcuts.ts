/**
 * Composable for keyboard shortcuts
 * Handles global and textarea-specific keyboard events
 */

import { onMounted, onUnmounted } from 'vue'

interface KeyboardShortcutOptions {
  onEscape?: () => void
  onCtrlEnter?: () => void
}

export function useKeyboardShortcuts(options: KeyboardShortcutOptions = {}) {
  /**
   * Handle global keyboard shortcuts
   */
  function handleGlobalKeyPress(event: KeyboardEvent) {
    if (event.key === 'Escape' && options.onEscape) {
      options.onEscape()
    }
  }

  /**
   * Handle textarea-specific keyboard shortcuts
   * Use this as the @keydown handler on textarea elements
   */
  function handleTextareaKeydown(event: KeyboardEvent, canSubmit: boolean) {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      event.preventDefault()
      if (canSubmit && options.onCtrlEnter) {
        options.onCtrlEnter()
      }
    }
  }

  // Register global keyboard listener
  onMounted(() => {
    globalThis.addEventListener('keydown', handleGlobalKeyPress)
  })

  // Cleanup on unmount
  onUnmounted(() => {
    globalThis.removeEventListener('keydown', handleGlobalKeyPress)
  })

  return {
    handleTextareaKeydown
  }
}
