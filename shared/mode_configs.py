"""Helper: Text correction modes."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ModeConfig:
    """
    Configuration for a text improvement mode.

    Attributes:
        description: User-facing description (button text)
        instruction: LLM instruction for backend processing

    """

    description: str
    instruction: str


# Base instruction templates
_INSTRUCTION_TRANSLATE = """
Input
- Text
Tasks
- Übersetze den Text in Sprache: <LANG>
Output Format
- plain Text, keine Markdown-Formatierung
"""

# Consolidated mode configurations
MODE_CONFIGS = {
    "correct": ModeConfig(
        description="Korrigiere",
        instruction="""
Input
- zu verbessernder Text
Task
- Korrekturlesen: Rechtschreibung, Grammatik und Zeichensetzung korrigieren
Output
- korrigierter Text
- in derselben Sprache! Falls Eingabe in Englisch, dann Ausgabe in Englisch, etc
- keine Kommentare
- Struktur und Zeilenumbrüche nicht ändern
- Format: plain text, no Markdown format
""",
    ),
    "improve": ModeConfig(
        description="Verbessere",
        instruction="""
Input
- zu verbessernder Text
Task
- Korrekturlesen: Rechtschreibung, Grammatik und Zeichensetzung korrigieren
- Text verbessern
Output
- verbesserter Text
- in derselben Sprache! Falls Eingabe in Englisch, dann Ausgabe in Englisch, etc
- keine Kommentare
- Format: plain text, no Markdown format
""",
    ),
    "summarize": ModeConfig(
        description="Text -> Stichwörter",
        instruction="""
Input
- Text zum Zusammenfassen
Task
- Text in Stichpunkten zusammenfassen
Output
- immer Kurz-Zusammenfassung in max. 3 Stichpunkten
- bei längerem Text zusätzlich ausführlichere Zusammenfassung in Stichpunkten
- in derselben Sprache! Falls Eingabe in Englisch, dann Ausgabe in Englisch, etc
- keine Kommentare
- Format: Markdown mit Abschnitten und Stichpunkten
""",
    ),
    "expand": ModeConfig(
        description="Stichwörter -> Text",
        instruction="""
Input
- Stichpunkte
Tasks
- Erstelle einen Text/Brief aus Stichpunkten
Output
- Text
- in derselben Sprache! Falls Eingabe in Englisch, dann Ausgabe in Englisch, etc
- keine Kommentare
- Format: plain text, no Markdown format
""",
    ),
    "translate_de": ModeConfig(
        description="Übersetzen -> DE",
        instruction=_INSTRUCTION_TRANSLATE.replace("<LANG>", "Deutsch", 1),
    ),
    "translate_en": ModeConfig(
        description="Übersetzen -> EN",
        instruction=_INSTRUCTION_TRANSLATE.replace("<LANG>", "Englisch", 1),
    ),
    "factcheck": ModeConfig(
        description="Faktencheck",
        instruction="""
Input
- Text
Tasks
- Du führst einen Factcheck zum Text durch.
- Fokus auf wissenschaftliche Korrektheit.
- Belege Aussagen mit belastbaren Quellen, insbesondere bei Verschwörungstheorien und FakeNews.
  Aber nur seriöse funktionierende gültige Links.
Output
- Markdown format, keine Einleitung
- kurz und prägnant
- einfache Sprache
""",  # noqa: E501
    ),
    "custom": ModeConfig(
        description="Freitext Anweisung",
        instruction="<CUSTOM_INSTRUCTION>",
    ),
}


# Type alias for valid text modes (for use in schemas and type hints)
TextMode = Literal[
    "correct",
    "improve",
    "summarize",
    "expand",
    "translate_de",
    "translate_en",
    "factcheck",
    "custom",
]
