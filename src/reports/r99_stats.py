"""Stats."""

import logging
from pathlib import Path

import pandas as pd
import streamlit as st

from helper import (
    get_shared_state,
)
from helper_db import db_select_usage_stats_daily, db_select_usage_stats_total

logger = logging.getLogger(Path(__file__).stem)
st.title(Path(__file__).stem[4:].replace("_", " ").title())

# double check, that this file is only access-able by me
if st.session_state["USER_ID"] != 1:
    st.stop()

cols = st.columns(2)

cols[0].subheader("Session State")
df = pd.DataFrame(list(st.session_state.items()), columns=["key", "value"])
cols[0].dataframe(df, hide_index=True)

cols[1].subheader("Shared State")
d = get_shared_state()
df = pd.DataFrame(list(d.items()), columns=["key", "value"])
cols[1].dataframe(df, hide_index=True)


env = get_shared_state()["ENV"]
if env == "PROD":
    cols = st.columns(2)

    cols[0].subheader("Daily Usage")
    df = db_select_usage_stats_daily()
    cols[0].dataframe(df, hide_index=True)

    df = db_select_usage_stats_total()
    cols[1].subheader("Sum")
    cols[1].dataframe(df, hide_index=True)
