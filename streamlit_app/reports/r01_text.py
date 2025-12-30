"""Textverbesserung."""

import logging
from pathlib import Path

import streamlit as st
from st_copy import copy_button

from shared.config import LLM_PROVIDER
from shared.helper_ai import MODE_CONFIGS
from shared.helper_db import db_insert_usage
from shared.llm_provider import get_llm_provider
from shared.texts import GOOGLE_DISCLAIMER, LABEL_KI_TEXT, LABEL_MY_TEXT

st.title("Textverbesserung")
logger = logging.getLogger(Path(__file__).stem)

USER_ID = st.session_state["USER_ID"]  # shortcut

if LLM_PROVIDER == "Gemini":
    st.markdown(GOOGLE_DISCLAIMER)


st.subheader(LABEL_MY_TEXT)
with st.form(LABEL_MY_TEXT):
    cols = st.columns((5, 1), vertical_alignment="top")
    textarea_in = cols[0].text_area(
        label=LABEL_MY_TEXT,
        height="content",
        label_visibility="collapsed",
        key="textarea_in",
    )

    # Mode selection and submit button
    mode_options = {config.description: mode for mode, config in MODE_CONFIGS.items()}
    selected_description = cols[1].selectbox(
        "Aufgabe",
        options=list(mode_options.keys()),
        key="mode_select",
    )
    submit_button = cols[1].form_submit_button("Submit", type="primary")

if submit_button:
    # Determine which mode was selected
    selected_mode = mode_options[selected_description]
    instruction = MODE_CONFIGS[selected_mode].instruction

    st.subheader(LABEL_KI_TEXT)

    llm_provider = get_llm_provider(LLM_PROVIDER)
    models = llm_provider.get_models()
    model = st.session_state.get("LLM_MODEL", models[0])
    text_response, tokens = llm_provider.call(
        model=model, instruction=instruction, prompt=textarea_in
    )

    db_insert_usage(user_id=USER_ID, tokens=tokens)
    st.session_state["cnt_requests"] += 1
    st.session_state["cnt_tokens"] += tokens

    # Display output differently for summarize mode (markdown) vs others (text)
    if selected_mode == "summarize":
        textarea_ai = st.markdown(text_response)

    else:
        textarea_ai = st.text_area(
            label=LABEL_KI_TEXT,
            value=text_response,
            height="content",
            label_visibility="collapsed",
            disabled=False,
        )
        copy_button(
            str(textarea_ai),
            tooltip="Kopieren",
            copied_label="Kopiert!",
            icon="st",
        )

    st.write(f"LLM: {LLM_PROVIDER} | Model: {model} | Tokens: {tokens}")

    # Show diff for correct and improve modes
    if selected_mode in ("correct", "improve"):
        st.subheader("Unterschied")

        # Import shared diff helper
        from shared.helper_diff import create_diff_html

        # Read CSS file
        css_path = Path(__file__).parent.parent.parent / "shared" / "helper_diff.css"
        css_content = css_path.read_text(encoding="utf-8")

        # Create and display diff
        diff_html = create_diff_html(textarea_in, str(textarea_ai))
        st.html(f"<style>{css_content}</style>")
        st.html(diff_html)

    st.subheader("Anweisung")
    st.code(language="markdown", body=instruction)
    st.write(text_response)
