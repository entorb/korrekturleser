"""Session Stats."""

import streamlit as st

from helper import (
    get_logger_from_filename,
    get_shared_state,
)

st.title(__doc__[:-1])  # type: ignore
logger = get_logger_from_filename(__file__)


# double check, that this file is only access-able by me
if st.session_state["USER_ID"] != 1:
    st.stop()

st.subheader("Shared State")
d = get_shared_state()
st.write(d)


st.subheader("Session State")
st.write(st.session_state)
