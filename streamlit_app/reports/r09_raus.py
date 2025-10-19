"""Logout."""

import streamlit as st

st.title("Tschüss " + st.session_state["USER_NAME"])

for key in ["USER_ID", "USER_NAME", "ai_response"]:
    st.session_state.pop(key, None)
