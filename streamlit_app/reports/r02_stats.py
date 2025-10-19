"""Stats."""

import logging
from pathlib import Path

import pandas as pd
import streamlit as st

from shared.helper import where_am_i
from shared.helper_db import db_select_usage_stats_daily, db_select_usage_stats_total
from streamlit_app.helper_streamlit import get_shared_state

logger = logging.getLogger(Path(__file__).stem)
ENV = where_am_i()


st.title(Path(__file__).stem[4:].replace("_", " ").title())


if ENV == "PROD":
    cols = st.columns(2)

    cols[0].subheader("Daily Usage")
    df = db_select_usage_stats_daily(user_id=st.session_state["USER_ID"])
    cols[0].dataframe(df, hide_index=True)

    df = db_select_usage_stats_total(user_id=st.session_state["USER_ID"])
    cols[1].subheader("Sum")
    cols[1].dataframe(df, hide_index=True)


cols = st.columns(2)

cols[0].subheader("Session State")
# Convert values to strings to ensure Arrow compatibility
session_items = sorted([(k, str(v)) for k, v in st.session_state.items()])
df = pd.DataFrame(session_items, columns=["key", "value"])
cols[0].dataframe(df, hide_index=True)

cols[1].subheader("Shared State")
d = get_shared_state()
# Convert values to strings to ensure Arrow compatibility
shared_items = sorted([(k, str(v)) for k, v in d.items()])
df = pd.DataFrame(shared_items, columns=["key", "value"])
cols[1].dataframe(df, hide_index=True)
