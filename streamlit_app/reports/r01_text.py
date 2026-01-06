"""Textverbesserung."""

import logging
from pathlib import Path

import streamlit as st
from st_copy import copy_button

from shared.config import LLM_PROVIDER_DEFAULT, LLM_PROVIDERS
from shared.helper_db import db_insert_usage
from shared.llm_provider import get_llm_provider
from shared.mode_configs import MODE_CONFIGS
from shared.texts import GOOGLE_DISCLAIMER, LABEL_KI_TEXT, LABEL_MY_TEXT

st.title("Textverbesserung")
logger = logging.getLogger(Path(__file__).stem)

USER_ID = st.session_state["USER_ID"]  # shortcut

# LLM select
if "LLM_PROVIDER" not in st.session_state:
    st.session_state["LLM_PROVIDER"] = LLM_PROVIDER_DEFAULT

default_index = LLM_PROVIDERS.index(st.session_state["LLM_PROVIDER"])
sel_llm = st.sidebar.selectbox(
    "LLM",
    LLM_PROVIDERS,
    index=default_index,
)
if sel_llm != st.session_state["LLM_PROVIDER"]:
    st.session_state["LLM_PROVIDER"] = sel_llm
    del st.session_state["LLM_MODEL"]

LLM = st.session_state["LLM_PROVIDER"]  # shortcut

llm_provider = get_llm_provider(LLM)

# Model select
MODELS = llm_provider.get_models()
if "LLM_MODEL" not in st.session_state:
    st.session_state["LLM_MODEL"] = MODELS[0]

model = st.session_state["LLM_MODEL"]  # shortcut

default_index = MODELS.index(model)
sel_model = st.sidebar.selectbox("Modell", MODELS, index=default_index)
if sel_model != model:
    st.session_state["LLM_MODEL"] = sel_model
MODEL = st.session_state["LLM_MODEL"]  # shortcut
del sel_model, model, default_index, MODELS

if LLM == "Gemini":
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
    submit_button = cols[1].form_submit_button("An KI senden", type="primary")

if submit_button:
    # Determine which mode was selected
    selected_mode = mode_options[selected_description]
    instruction = MODE_CONFIGS[selected_mode].instruction

    st.subheader(LABEL_KI_TEXT)

    with st.spinner("Schmelze Gletscher..."):
        text_response, tokens = llm_provider.call(
            model=MODEL, instruction=instruction, prompt=textarea_in
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

    st.write(f"LLM: {LLM} | Model: {MODEL} | Tokens: {tokens}")
