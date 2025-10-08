"""Session Stats."""

import pandas as pd
import streamlit as st

from helper import (
    get_logger_from_filename,
    get_shared_state,
)
from helper_db import db_select_users_daily_requests, db_select_users_total_requests

st.title(__file__[4:-3])  # type: ignore
logger = get_logger_from_filename(__file__)


# double check, that this file is only access-able by me
if st.session_state["USER_ID"] != 1:
    st.stop()


# st.header("State")
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
    # st.header("DB Stats")
    cols = st.columns(2)

    cols[0].subheader("Daily Usage")
    df = db_select_users_daily_requests()
    cols[0].dataframe(df, hide_index=True)

    df = db_select_users_total_requests()
    cols[1].subheader("Sum")
    cols[1].dataframe(df, hide_index=True)
