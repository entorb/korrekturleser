/**
 * Mode configuration for text improvement
 *
 * AUTO-GENERATED - DO NOT EDIT MANUALLY
 * Generated from: shared/helper_ai.py
 *
 * To regenerate: pnpm generate-api
 */

import type { TextRequest } from '@/api'

/** All supported mode values */
export type TextMode = TextRequest['mode']

/** All available mode values */
const ALL_MODES: TextMode[] = [
  'correct',
  'improve',
  'summarize',
  'expand',
  'translate_de',
  'translate_en',
  'custom'
]

// Mode descriptions mapping (auto-generated from backend)
const MODE_DESCRIPTIONS: Record<TextMode, string> = {
  correct: 'Korrigiere',
  improve: 'Verbessere',
  summarize: 'Text -> Stichwörter',
  expand: 'Stichwörter -> Text',
  translate_de: 'Übersetzen -> DE',
  translate_en: 'Übersetzen -> EN',
  custom: 'Freitext Anweisung'
}

/**
 * Get all available modes (auto-generated from enum)
 */
export function getAvailableModes(): TextMode[] {
  return ALL_MODES
}

/**
 * Get description for a mode
 */
export function getModeDescription(mode: TextMode): string {
  return MODE_DESCRIPTIONS[mode] || mode
}

/**
 * Get all mode descriptions as a record
 */
export function getModeDescriptions(): Record<string, string> {
  return MODE_DESCRIPTIONS
}
