#!/bin/sh
cd $(dirname $0)/..

uv run -m streamlit run streamlit_app/main.py
