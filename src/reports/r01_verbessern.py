"""Textverbesserung."""

import streamlit as st
from st_copy import copy_button
from st_diff_viewer import diff_viewer

from helper import get_logger_from_filename, get_shared_state
from helper_db import db_insert_usage
from llm_provider import GeminiProvider, OllamaProvider, llm_call

st.title("Textverbesserung")
logger = get_logger_from_filename(__file__)


# LLM_PROVIDER, MODEL = ("Ollama", "llama3.2:1b")
# LLM_PROVIDER, MODEL = ("Gemini", "gemini-2.5-flash-pro")
# LLM_PROVIDER, MODEL = ("Gemini", "gemini-2.5-flash")
LLM_PROVIDER, MODEL = ("Gemini", "gemini-2.5-flash-lite")

INSTRUCTION = """
- Input: text to improve
- Output: corrected text, in same language.
  - No comments or thinking. Format: plain text, no markdown.
  - Do not change the linebreaks.
- Task1
  - proof-reading: correct spelling, grammar, and punctuation.
  - improve text.
"""
# TODO: creativity via scale


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
    submit = cols[1].form_submit_button("An KI senden", type="primary")

# how to modify via JavaScript?
# btn_test = st.button("Test")
# if btn_test:
#     st.html("""
#             <script>
# document.getElementById('.st-key-textarea_in').value = 'asdf';
#             </script>
#             """)

if st.session_state["ai_response"] != "" or submit:
    st.subheader("KI Text")

    if submit and textarea_in:
        if LLM_PROVIDER == "Gemini":
            llm_provider = GeminiProvider(instruction=INSTRUCTION, model=MODEL)
        else:
            llm_provider = OllamaProvider(instruction=INSTRUCTION, model=MODEL)
        text_response, tokens = llm_call(llm_provider, textarea_in)
        st.session_state["ai_response"] = text_response

        if ENV == "PROD":
            db_insert_usage(user_id=USER_ID, tokens=tokens)

    cols = st.columns((5, 1), vertical_alignment="top")
    textarea_ai = cols[0].text_area(
        label="KI Text",
        value=st.session_state["ai_response"],
        height="content",
        label_visibility="collapsed",
        key="textarea_ai",
    )
    if textarea_ai:
        copy_button(
            textarea_ai,
            tooltip="Kopieren",
            copied_label="Kopiert!",
            icon="st",
        )

    if ENV != "PROD":
        st.subheader("Unterschied")
        diff_viewer(
            textarea_in,
            str(textarea_ai),
            split_view=False,
            use_dark_theme=False,
            hide_line_numbers=True,
        )

    # st.subheader("Anweisung")
    # st.code(language="markdown", body=INSTRUCTION)
