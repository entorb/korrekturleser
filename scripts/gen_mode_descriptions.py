"""
Generate TypeScript mode descriptions from Python MODE_CONFIGS.

This script extracts mode descriptions from shared/helper_ai.py and generates
a TypeScript file for the Vue.js frontend, ensuring a single source of truth.
"""  # noqa: INP001

import sys
from pathlib import Path

# Add project root to path to import shared modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.mode_configs import MODE_CONFIGS  # noqa: E402


def generate_typescript_file() -> str:
    """Generate TypeScript code with mode descriptions."""
    # Extract mode descriptions
    mode_entries = []
    all_modes = []
    for mode_key, config in MODE_CONFIGS.items():
        description = config.description
        mode_entries.append(f"  {mode_key}: '{description}'")
        all_modes.append(f"  '{mode_key}'")

    mode_descriptions = ",\n".join(mode_entries)
    modes_list = ",\n".join(all_modes)

    # Generate TypeScript file content
    ts_content = f"""/**
 * Mode configuration for text improvement
 *
 * AUTO-GENERATED - DO NOT EDIT MANUALLY
 * Generated from: shared/helper_ai.py
 *
 * To regenerate: pnpm generate-api
 */

import type {{ TextRequest }} from '@/api'

/** All supported mode values */
export type TextMode = TextRequest['mode']

/** All available mode values */
const ALL_MODES: TextMode[] = [
{modes_list}
]

// Mode descriptions mapping (auto-generated from backend)
const MODE_DESCRIPTIONS: Record<TextMode, string> = {{
{mode_descriptions}
}}

/**
 * Get all available modes (auto-generated from enum)
 */
export function getAvailableModes(): TextMode[] {{
  return ALL_MODES
}}

/**
 * Get description for a mode
 */
export function getModeDescription(mode: TextMode): string {{
  return MODE_DESCRIPTIONS[mode] || mode
}}

/**
 * Get all mode descriptions as a record
 */
export function getModeDescriptions(): Record<string, string> {{
  return MODE_DESCRIPTIONS
}}
"""
    return ts_content


def main() -> None:
    """Generate and write the TypeScript file."""
    output_path = project_root / "vue_app" / "src" / "config" / "modes.ts"

    # Generate content
    ts_content = generate_typescript_file()

    # Write to file
    output_path.write_text(ts_content, encoding="utf-8")

    print(f"✓ Generated {output_path.relative_to(project_root)}")
    print(f"  Modes: {', '.join(MODE_CONFIGS.keys())}")


if __name__ == "__main__":
    main()
