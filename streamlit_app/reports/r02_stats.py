"""Stats."""

import logging
from pathlib import Path

import pandas as pd
import streamlit as st

from shared.config import LLM_MODEL, LLM_PROVIDER
from shared.helper import where_am_i
from shared.helper_db import db_select_usage_stats_daily, db_select_usage_stats_total

logger = logging.getLogger(Path(__file__).stem)
ENV = where_am_i()


st.title(Path(__file__).stem[4:].replace("_", " ").title())


cols = st.columns(2)

df = db_select_usage_stats_total(user_id=st.session_state["USER_ID"])
cols[0].subheader("Sum")
cols[0].dataframe(df, hide_index=True)

df = db_select_usage_stats_daily(user_id=st.session_state["USER_ID"])
cols[1].subheader("Daily Usage")
cols[1].dataframe(df, hide_index=True)


cols = st.columns(2)

cols[0].subheader("Config")
d = {"ENV": ENV, "LLM_PROVIDER": LLM_PROVIDER, "LLM_PROD_MODEL": LLM_MODEL}
# Convert values to strings to ensure Arrow compatibility
shared_items = sorted([(k, str(v)) for k, v in d.items()])
df = pd.DataFrame(shared_items, columns=["key", "value"])
cols[0].dataframe(df, hide_index=True)

cols[1].subheader("Session")
# Convert values to strings to ensure Arrow compatibility
session_items = sorted([(k, str(v)) for k, v in st.session_state.items()])
df = pd.DataFrame(session_items, columns=["key", "value"])
cols[1].dataframe(df, hide_index=True)
