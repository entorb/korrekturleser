"""Textverbesserung."""

import difflib
import logging
from pathlib import Path

import streamlit as st
from st_copy import copy_button

from shared.config import (
    INSTRUCTION_CORRECT,
    INSTRUCTION_EXPAND,
    INSTRUCTION_IMPROVE,
    INSTRUCTION_SUMMARIZE,
    INSTRUCTION_TRANSLATE_DE,
    INSTRUCTION_TRANSLATE_EN,
    LLM_MODEL,
    LLM_PROVIDER,
)
from shared.helper import where_am_i
from shared.helper_db import db_insert_usage
from shared.llm_provider import get_cached_llm_provider

st.title("Textverbesserung")
logger = logging.getLogger(Path(__file__).stem)

ENV = where_am_i()

USER_ID = st.session_state["USER_ID"]  # shortcut


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
        instruction = INSTRUCTION_CORRECT
    elif submit2:
        instruction = INSTRUCTION_IMPROVE
    elif submit3:
        instruction = INSTRUCTION_SUMMARIZE
    elif submit4:
        instruction = INSTRUCTION_EXPAND
    elif submit5a:
        instruction = INSTRUCTION_TRANSLATE_DE
    elif submit5b:
        instruction = INSTRUCTION_TRANSLATE_EN
    else:
        st.stop()

    st.subheader("KI Text")

    llm_provider = get_cached_llm_provider(
        provider_name=LLM_PROVIDER, model=LLM_MODEL, instruction=instruction
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

    st.write(f"{tokens} Token verbraucht für {LLM_MODEL}")

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
        st.html(Path("streamlit_app/table_diff.css"))
        st.html(diff_html)

    st.subheader("Anweisung")
    st.code(language="markdown", body=instruction)
