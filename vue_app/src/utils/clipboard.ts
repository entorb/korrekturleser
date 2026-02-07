/**
 * Clipboard utilities with fallbacks for older browsers
 * iPhone 7 (iOS 10-15) compatibility
 */

/**
 * Copy text to clipboard with fallback for older browsers
 */
export async function copyToClipboard(text: string): Promise<void> {
  // Try modern Clipboard API first (iOS 13.4+)
  if ('clipboard' in navigator && typeof navigator.clipboard.writeText === 'function') {
    try {
      await navigator.clipboard.writeText(text)
      return
    } catch (err) {
      console.warn('Clipboard API failed, using fallback:', err)
    }
  }

  // Fallback for older browsers (iOS 10+)
  const textArea = document.createElement('textarea')
  textArea.value = text
  textArea.style.position = 'fixed'
  textArea.style.top = '0'
  textArea.style.left = '0'
  textArea.style.width = '2em'
  textArea.style.height = '2em'
  textArea.style.padding = '0'
  textArea.style.border = 'none'
  textArea.style.outline = 'none'
  textArea.style.boxShadow = 'none'
  textArea.style.background = 'transparent'
  textArea.setAttribute('readonly', '')
  textArea.style.opacity = '0'

  document.body.appendChild(textArea)
  textArea.select()

  try {
    const successful = document.execCommand('copy')
    if (!successful) {
      throw new Error('Copy command failed')
    }
  } finally {
    textArea.remove()
  }
}

/**
 * Read text from clipboard with fallback for older browsers
 */
export async function readFromClipboard(): Promise<string> {
  // Try modern Clipboard API first (iOS 13.4+)
  if ('clipboard' in navigator && typeof navigator.clipboard.readText === 'function') {
    try {
      return await navigator.clipboard.readText()
    } catch (err) {
      console.warn('Clipboard API failed, using fallback:', err)
    }
  }

  // Fallback for older browsers (iOS 10+)
  // Note: This requires user interaction and may not work in all contexts
  const textArea = document.createElement('textarea')
  textArea.style.position = 'fixed'
  textArea.style.top = '0'
  textArea.style.left = '0'
  textArea.style.width = '2em'
  textArea.style.height = '2em'
  textArea.style.padding = '0'
  textArea.style.border = 'none'
  textArea.style.outline = 'none'
  textArea.style.boxShadow = 'none'
  textArea.style.background = 'transparent'
  textArea.style.opacity = '0'

  document.body.appendChild(textArea)
  textArea.focus()

  try {
    const successful = document.execCommand('paste')
    if (!successful) {
      throw new Error('Paste command failed')
    }
    return textArea.value
  } finally {
    textArea.remove()
  }
}
