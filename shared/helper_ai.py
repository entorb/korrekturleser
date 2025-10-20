"""Helper: AI - Consolidated mode configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModeConfig:
    """
    Configuration for a text improvement mode.

    Attributes:
        mode: The mode identifier string
        description: User-facing description (button text)
        instruction: LLM instruction for backend processing

    """

    mode: str
    description: str
    instruction: str


# Base instruction templates
_INSTRUCTION_TRANSLATE = """
Input
- Text
Tasks
- Übersetzen den Text in die Sprache: <LANG>
Output
- Text
- Format: einfacher Text, keine Markdown-Formatierung.
"""

# Consolidated mode configurations
MODE_CONFIGS = {
    "correct": ModeConfig(
        mode="correct",
        description="Korrigiere",
        instruction="""
Input
- zu verbessernder Text
Task
- Korrekturlesen: Rechtschreibung, Grammatik und Zeichensetzung korrigieren.
Output
- korrigierter Text
- in derselben Sprache! Falls Eingabe in Englisch, dann Ausgabe in Englisch, etc.
- keine Kommentare
- Struktur und Zeilenumbrüche nicht ändern.
- Format: reiner Text, keine Markdown-Formatierung.
""",
    ),
    "improve": ModeConfig(
        mode="improve",
        description="Verbessere",
        instruction="""
Input
- zu verbessernder Text
Task
- Korrekturlesen: Rechtschreibung, Grammatik und Zeichensetzung korrigieren.
- Text verbessern
Output
- verbesserter Text
- in derselben Sprache! Falls Eingabe in Englisch, dann Ausgabe in Englisch, etc.
- keine Kommentare
- Format: einfacher Text, keine Markdown-Formatierung.
""",
    ),
    "summarize": ModeConfig(
        mode="summarize",
        description="Text -> Stichwörter",
        instruction="""
Input
- Text zum Zusammenfassen
Task
- Text in Stichpunkten zusammenfassen
Output
- immer Kurz-Zusammenfassung in max. 3 Stichpunkten
- bei längerem Text zusätzlich ausführlichere Zusammenfassung in Stichpunkten
- in derselben Sprache! Falls Eingabe in Englisch, dann Ausgabe in Englisch, etc.
- keine Kommentare
- Format: Markdown mit Abschnitten und Stichpunkten
""",
    ),
    "expand": ModeConfig(
        mode="expand",
        description="Stichwörter -> Text",
        instruction="""
Input
- Stichpunkte
Tasks
- Erstelle einen Text/Brief aus Stichpunkten
Output
- Text
- in derselben Sprache! Falls Eingabe in Englisch, dann Ausgabe in Englisch, etc.
- keine Kommentare
- Format: einfacher Text, keine Markdown-Formatierung.
""",
    ),
    "translate_de": ModeConfig(
        mode="translate_de",
        description="Übersetzen -> DE",
        instruction=_INSTRUCTION_TRANSLATE.replace("<LANG>", "Deutsch", 1),
    ),
    "translate_en": ModeConfig(
        mode="translate_en",
        description="Übersetzen -> EN",
        instruction=_INSTRUCTION_TRANSLATE.replace("<LANG>", "Englisch", 1),
    ),
}
