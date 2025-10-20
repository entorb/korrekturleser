/**
 * Mode configuration for text improvement
 *
 * AUTO-GENERATED - DO NOT EDIT MANUALLY
 * Generated from: shared/helper_ai.py
 *
 * To regenerate: pnpm generate-api
 */

import { ImproveRequest } from '@/api'

// Mode descriptions mapping (auto-generated from backend)
const MODE_DESCRIPTIONS: Record<ImproveRequest.mode, string> = {
  [ImproveRequest.mode.CORRECT]: 'Korrigiere',
  [ImproveRequest.mode.IMPROVE]: 'Verbessere',
  [ImproveRequest.mode.SUMMARIZE]: 'Text -> Stichwörter',
  [ImproveRequest.mode.EXPAND]: 'Stichwörter -> Text',
  [ImproveRequest.mode.TRANSLATE_DE]: 'Übersetzen -> DE',
  [ImproveRequest.mode.TRANSLATE_EN]: 'Übersetzen -> EN'
}

/**
 * Get all available modes (auto-generated from enum)
 */
export function getAvailableModes(): ImproveRequest.mode[] {
  return Object.values(ImproveRequest.mode)
}

/**
 * Get description for a mode
 */
export function getModeDescription(mode: ImproveRequest.mode): string {
  return MODE_DESCRIPTIONS[mode] || mode
}

/**
 * Get all mode descriptions as a record
 */
export function getModeDescriptions(): Record<string, string> {
  return MODE_DESCRIPTIONS
}
