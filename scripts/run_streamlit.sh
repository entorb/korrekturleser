#!/bin/sh
cd "$(dirname "$0")/.."

uv run --no-build -m streamlit run streamlit_app/main.py
