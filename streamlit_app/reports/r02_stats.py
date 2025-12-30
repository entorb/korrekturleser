"""Stats."""

import logging
from pathlib import Path

import streamlit as st

from shared.config import LLM_PROVIDER
from shared.helper import format_config_dataframe, format_session_dataframe
from shared.helper_db import (
    db_select_usage_stats_daily,
    db_select_usage_stats_total,
)
from shared.llm_provider import get_llm_provider

logger = logging.getLogger(Path(__file__).stem)


st.title(Path(__file__).stem[4:].replace("_", " ").title())

st.subheader("Settings")
cols = st.columns((1, 3))
llm_provider = get_llm_provider(LLM_PROVIDER)
models = llm_provider.get_models()
# Use LLM_MODEL from session state if available, otherwise default to 0
default_index = models.index(st.session_state.get("LLM_MODEL", models[0]))
sel_model = cols[0].selectbox("Modell", models, index=default_index)
st.session_state["LLM_MODEL"] = sel_model

cols = st.columns(2)

df = db_select_usage_stats_total(user_id=st.session_state["USER_ID"])
cols[0].subheader("Sum")
cols[0].dataframe(df, hide_index=True)

df = db_select_usage_stats_daily(user_id=st.session_state["USER_ID"])
cols[1].subheader("Daily Usage")
cols[1].dataframe(df, hide_index=True)


cols = st.columns(2)

cols[0].subheader("Config")
df = format_config_dataframe()
cols[0].dataframe(df, hide_index=True)

cols[1].subheader("Session")
df = format_session_dataframe(dict(st.session_state.items()))
cols[1].dataframe(df, hide_index=True)
