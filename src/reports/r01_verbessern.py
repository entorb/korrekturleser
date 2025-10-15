"""Textverbesserung."""

import difflib

import streamlit as st
from st_copy import copy_button

from helper import get_logger_from_filename, get_shared_state
from helper_db import db_insert_usage
from llm_provider import GeminiProvider, OllamaProvider, llm_call

st.title("Textverbesserung")
logger = get_logger_from_filename(__file__)


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
- in derselben Sprache!
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
- in derselben Sprache!
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
- in derselben Sprache!
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
- in derselben Sprache!
- keine Kommentare
- Format: einfacher Text, keine Markdown-Formatierung.
"""


USER_ID = st.session_state["USER_ID"]  # shortcut
ENV = get_shared_state()["ENV"]

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

# how to modify via JavaScript?
# btn_test = st.button("Test")
# if btn_test:
#     st.html("""
#             <script>
# document.getElementById('.st-key-textarea_in').value = 'asdf';
#             </script>
#             """)

if st.session_state["ai_response"] != "" or submit1 or submit2 or submit3 or submit4:
    if submit1:
        instruction = INSTRUCTION1
    elif submit2:
        instruction = INSTRUCTION2
    elif submit3:
        instruction = INSTRUCTION3
    elif submit4:
        instruction = INSTRUCTION4
    else:
        st.stop()

    st.subheader("KI Text")

    if LLM_PROVIDER == "Gemini":
        llm_provider = GeminiProvider(instruction=instruction, model=MODEL)
    else:
        llm_provider = OllamaProvider(instruction=instruction, model=MODEL)
    text_response, tokens = llm_call(llm_provider, textarea_in)
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

    st.write(f"{tokens} Token verbraucht")

    st.subheader("Anweisung")

    st.code(language="markdown", body=instruction)

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

    # Add CSS styling for better diff visualization with mobile optimization
    diff_styled = f"""
    <style>
        table.diff {{
            font-family: Courier, monospace;
            border: 1px solid #ccc;
            border-collapse: collapse;
            width: 100%;
            font-size: 12px;
            display: block;
            overflow-x: auto;
        }}
        .diff_header {{
            background-color: #e0e0e0;
            text-align: center;
            font-weight: bold;
            padding: 5px;
        }}
        .diff_next {{
            background-color: #c0c0c0;
        }}
        td.diff_header {{
            text-align: right;
            padding: 2px 5px;
            min-width: 30px;
        }}
        .diff_add {{
            background-color: #d4edda;
            color: #155724;
        }}
        .diff_chg {{
            background-color: #fff3cd;
            color: #856404;
        }}
        .diff_sub {{
            background-color: #f8d7da;
            color: #721c24;
        }}

        /* Mobile optimizations */
        @media (max-width: 768px) {{
            table.diff {{
                font-size: 10px;
            }}
            td.diff_header {{
                padding: 1px 3px;
                min-width: 20px;
                font-size: 9px;
            }}
            .diff_header {{
                padding: 3px;
                font-size: 11px;
            }}
            table.diff td {{
                padding: 2px;
                word-break: break-word;
            }}
        }}

        /* Very small screens */
        @media (max-width: 480px) {{
            table.diff {{
                font-size: 9px;
            }}
            td.diff_header {{
                min-width: 15px;
                font-size: 8px;
            }}
        }}
    </style>
    {diff_html}
    """

    st.html(diff_styled)
