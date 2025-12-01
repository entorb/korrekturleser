"""Textverbesserung."""

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
from shared.texts import GOOGLE_DISCLAIMER

st.title("Textverbesserung")
logger = logging.getLogger(Path(__file__).stem)

ENV = where_am_i()

USER_ID = st.session_state["USER_ID"]  # shortcut

if LLM_PROVIDER == "Gemini":
    st.markdown(GOOGLE_DISCLAIMER)


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

    llm_provider = get_cached_llm_provider(instruction=instruction)
    text_response, tokens = llm_provider.call(textarea_in)
    st.session_state["ai_response"] = text_response

    db_insert_usage(user_id=USER_ID, tokens=tokens)
    st.session_state["cnt_requests"] += 1
    st.session_state["cnt_tokens"] += tokens

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

        # Import shared diff helper
        from shared.helper_diff import create_diff_html

        # Read CSS file
        css_path = Path(__file__).parent.parent.parent / "shared" / "helper_diff.css"
        css_content = css_path.read_text(encoding="utf-8")

        # Create and display diff
        diff_html = create_diff_html(textarea_in, st.session_state["ai_response"])
        st.html(f"<style>{css_content}</style>")
        st.html(diff_html)

    # st.subheader("Anweisung")
    # st.code(language="markdown", body=instruction)
