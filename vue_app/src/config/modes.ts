/**
 * Mode configuration for text improvement
 *
 * AUTO-GENERATED - DO NOT EDIT MANUALLY
 * Generated from: shared/helper_ai.py
 *
 * To regenerate: pnpm generate-api
 */

import { TextRequest } from '@/api'

// Mode descriptions mapping (auto-generated from backend)
const MODE_DESCRIPTIONS: Record<TextRequest.mode, string> = {
  [TextRequest.mode.CORRECT]: 'Korrigiere',
  [TextRequest.mode.IMPROVE]: 'Verbessere',
  [TextRequest.mode.SUMMARIZE]: 'Text -> Stichwörter',
  [TextRequest.mode.EXPAND]: 'Stichwörter -> Text',
  [TextRequest.mode.TRANSLATE_DE]: 'Übersetzen -> DE',
  [TextRequest.mode.TRANSLATE_EN]: 'Übersetzen -> EN',
  [TextRequest.mode.CUSTOM]: 'Freitext'
}

/**
 * Get all available modes (auto-generated from enum)
 */
export function getAvailableModes(): TextRequest.mode[] {
  return Object.values(TextRequest.mode)
}

/**
 * Get description for a mode
 */
export function getModeDescription(mode: TextRequest.mode): string {
  return MODE_DESCRIPTIONS[mode] || mode
}

/**
 * Get all mode descriptions as a record
 */
export function getModeDescriptions(): Record<string, string> {
  return MODE_DESCRIPTIONS
}
