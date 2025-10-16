"""Textverbesserung."""

import difflib
import logging
from pathlib import Path

import streamlit as st
from st_copy import copy_button

from helper import get_shared_state
from helper_db import db_insert_usage
from llm_provider import get_cached_llm_provider

st.title("Textverbesserung")
logger = logging.getLogger(Path(__file__).stem)


# LLM_PROVIDER, MODEL = ("Ollama", "llama3.2:1b")
# LLM_PROVIDER, MODEL = ("Gemini", "gemini-2.5-flash-pro")
# LLM_PROVIDER, MODEL = ("Gemini", "gemini-2.5-flash")
LLM_PROVIDER, MODEL = ("Gemini", "gemini-2.5-flash-lite")

# Korrigieren
INSTRUCTION1 = """
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

# Verbessern
INSTRUCTION2 = """
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

# Zusammenfassen
INSTRUCTION3 = """
Input
- Text zum Zusammenfassen
Task
- Text in Stichpunkten zusammenfassen
Output
- immer Kurz-Zusammenfassung in max. 3 Stichpunkten
- bei längerem Text zusätzlich ausführlichere Zusammenfassung in gegliederten Stichpunkten
- in derselben Sprache! Falls Eingabe in Englisch, dann Ausgabe in Englisch, etc.
- keine Kommentare
- Format: Markdown mit Abschnitten und Stichpunkten
"""  # noqa: E501

# Text aus Stichpunkten
INSTRUCTION4 = """
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

# Übersetzen
INSTRUCTION5 = """
Input
- Text
Tasks
- Übersetzen den Text in die Sprache: <LANG>
Output
- Text
- Format: einfacher Text, keine Markdown-Formatierung.
"""

USER_ID = st.session_state["USER_ID"]  # shortcut
ENV = get_shared_state()["ENV"]


st.markdown(
    "***Achtung***: *Die Google KI wird deine Eingaben zum Trainieren verwenden."
    " Nur für Dinge verwenden, die nicht streng geheim sind.*"
)


st.subheader("Mein Text")
with st.form("Mein Text"):
    cols = st.columns((5, 1), vertical_alignment="top")
    textarea_in = cols[0].text_area(
        label="Mein Text",
        height="content",
        label_visibility="collapsed",
        key="textarea_in",
    )
    submit1 = cols[1].form_submit_button("Korrigieren", type="primary")
    submit2 = cols[1].form_submit_button("Verbessern", type="primary")
    submit3 = cols[1].form_submit_button("Zusammenfassen", type="primary")
    submit4 = cols[1].form_submit_button("Text aus Stichpunkten", type="primary")
    submit5a = cols[1].form_submit_button("Übersetzen -> DE", type="primary")
    submit5b = cols[1].form_submit_button("Übersetzen -> EN", type="primary")

# how to modify via JavaScript?
# btn_test = st.button("Test")
# if btn_test:
#     st.html("""
#             <script>
# document.getElementById('.st-key-textarea_in').value = 'asdf';
#             </script>
#             """)

if (
    st.session_state["ai_response"] != ""
    or submit1
    or submit2
    or submit3
    or submit4
    or submit5a
    or submit5b
):
    if submit1:
        instruction = INSTRUCTION1
    elif submit2:
        instruction = INSTRUCTION2
    elif submit3:
        instruction = INSTRUCTION3
    elif submit4:
        instruction = INSTRUCTION4
    elif submit5a:
        instruction = INSTRUCTION5.replace("<LANG>", "Deutsch", 1)
    elif submit5b:
        instruction = INSTRUCTION5.replace("<LANG>", "Englisch", 1)
    else:
        st.stop()

    st.subheader("KI Text")

    llm_provider = get_cached_llm_provider(
        provider_name=LLM_PROVIDER, model=MODEL, instruction=instruction
    )
    text_response, tokens = llm_provider.call(textarea_in)
    st.session_state["ai_response"] = text_response

    if ENV == "PROD":
        db_insert_usage(user_id=USER_ID, tokens=tokens)

    if submit3:
        textarea_ai = st.markdown(
            st.session_state["ai_response"],
        )

    else:
        textarea_ai = st.text_area(
            label="KI Text",
            value=st.session_state["ai_response"],
            height="content",
            label_visibility="collapsed",
            key="textarea_ai",
        )
        copy_button(
            str(textarea_ai),
            tooltip="Kopieren",
            copied_label="Kopiert!",
            icon="st",
        )

    st.write(f"{tokens} Token verbraucht für {MODEL}")

    if submit1 or submit2:
        st.subheader("Unterschied")

        # Create HTML diff
        text_in_lines = textarea_in.splitlines(keepends=True)
        text_ai_lines = st.session_state["ai_response"].splitlines(keepends=True)

        diff_html = difflib.HtmlDiff(wrapcolumn=80).make_table(
            text_in_lines,
            text_ai_lines,
            fromdesc="Original",
            todesc="KI Text",
            context=True,
            numlines=0,
        )

        # CSS styling for better diff visualization with mobile optimization
        st.html(Path("src/table_diff.css"))
        st.html(diff_html)

    st.subheader("Anweisung")
    st.code(language="markdown", body=instruction)
