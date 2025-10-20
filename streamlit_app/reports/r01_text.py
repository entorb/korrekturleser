"""Textverbesserung."""

import difflib
import logging
from pathlib import Path

import streamlit as st
from st_copy import copy_button

from shared.config import (
    LLM_MODEL,
    LLM_PROVIDER,
)
from shared.helper import where_am_i
from shared.helper_ai import MODE_CONFIGS
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

    # Dynamically create submit buttons from MODE_CONFIGS
    submit_buttons = {}
    for mode, config in MODE_CONFIGS.items():
        submit_buttons[mode] = cols[1].form_submit_button(
            config.description, type="primary"
        )

# Determine which mode was selected
selected_mode = None
for mode, was_clicked in submit_buttons.items():
    if was_clicked:
        selected_mode = mode
        st.session_state["selected_mode"] = mode
        break

# Use cached mode if available
if not selected_mode and "selected_mode" in st.session_state:
    selected_mode = st.session_state["selected_mode"]

# Process if any button was clicked or there's a cached response
if selected_mode:
    instruction = MODE_CONFIGS[selected_mode].instruction

    st.subheader("KI Text")

    llm_provider = get_cached_llm_provider(
        provider_name=LLM_PROVIDER, model=LLM_MODEL, instruction=instruction
    )
    text_response, tokens = llm_provider.call(textarea_in)
    st.session_state["ai_response"] = text_response

    if ENV == "PROD":
        db_insert_usage(user_id=USER_ID, tokens=tokens)

    # Display output differently for summarize mode (markdown) vs others (text)
    if selected_mode == "summarize":
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

    # Show diff for correct and improve modes
    if selected_mode in ("correct", "improve"):
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
