"""Logout."""

import streamlit as st

st.title("Tschüss " + st.session_state["USERNAME"])

for key in ["USER_ID", "USERNAME", "ai_response"]:
    st.session_state.pop(key, None)
