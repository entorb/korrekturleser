"""Shared configuration for both Streamlit and FastAPI apps."""

from pathlib import Path

from dotenv import load_dotenv

from shared.helper import my_get_env

# Load environment variables from .env file in project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")


# Local user
USER_ID_LOCAL = 1
USER_NAME_LOCAL = "Torben"

# LLM configuration
LLM_PROVIDER = "Gemini"
LLM_MODEL = "gemini-2.5-flash-lite"  # "gemini-2.5-flash", "gemini-2.5-pro"
# LLM_MODEL = "Ollama"
# LLM_PROVIDER = "llama3.2:1b"

# FastAPI parameters
# JWT Configuration
JWT_SECRET_KEY = my_get_env("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24


# Instructions for each mode
INSTRUCTION_CORRECT = """
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
"""

INSTRUCTION_IMPROVE = """
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
"""

INSTRUCTION_SUMMARIZE = """
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
"""

INSTRUCTION_EXPAND = """
Input
- Stichpunkte
Tasks
- Erstelle einen Text/Brief aus Stichpunkten
Output
- Text
- in derselben Sprache! Falls Eingabe in Englisch, dann Ausgabe in Englisch, etc.
- keine Kommentare
- Format: einfacher Text, keine Markdown-Formatierung.
"""

INSTRUCTION_TRANSLATE = """
Input
- Text
Tasks
- Übersetzen den Text in die Sprache: <LANG>
Output
- Text
- Format: einfacher Text, keine Markdown-Formatierung.
"""

INSTRUCTION_TRANSLATE_DE = INSTRUCTION_TRANSLATE.replace("<LANG>", "Deutsch", 1)
INSTRUCTION_TRANSLATE_EN = INSTRUCTION_TRANSLATE.replace("<LANG>", "Englisch", 1)
