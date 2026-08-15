"""Test the mode descriptions TypeScript generator."""

import importlib.util
from pathlib import Path

from shared.mode_configs import MODE_CONFIGS

SCRIPT_PATH = Path(__file__).parent.parent / "scripts" / "gen_mode_descriptions.py"
spec = importlib.util.spec_from_file_location("gen_mode_descriptions", SCRIPT_PATH)
gen = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(gen)


def test_generated_content_contains_all_modes() -> None:
    content = gen.generate_typescript_file()
    assert content.startswith("/**")
    assert "AUTO-GENERATED - DO NOT EDIT MANUALLY" in content
    assert "export type TextMode" in content
    assert "getAvailableModes" in content
    assert "getModeDescriptions" in content
    for mode in MODE_CONFIGS:
        assert f"'{mode}'" in content


def test_descriptions_match_config() -> None:
    content = gen.generate_typescript_file()
    for mode, config in MODE_CONFIGS.items():
        assert f"{mode}: '{config.description}'" in content


def test_all_modes_in_array() -> None:
    content = gen.generate_typescript_file()
    modes_block = content.split("ALL_MODES: TextMode[] = [", 1)[1].split("]", 1)[0]
    for mode in MODE_CONFIGS:
        assert f"'{mode}'" in modes_block
    assert len(MODE_CONFIGS) == modes_block.count(",") + 1
