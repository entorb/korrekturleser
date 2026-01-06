"""Logout."""

import streamlit as st

st.title("Tschüss " + st.session_state["USER_NAME"])

for key in st.session_state:
    del st.session_state[key]
