#!/bin/sh
cd "$(dirname "$0")/.." || exit 1

uv run --no-build -m streamlit run streamlit_app/main.py
