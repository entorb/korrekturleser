#!/bin/sh
cd $(dirname $0)/..

uv remove pandas pyarrow google-genai mysql-connector-python st_copy streamlit
uv remove --dev ruff ollama pre-commit pytest pytest-cov tomli-w watchdog

uv lock --upgrade
uv sync --upgrade

uv add pandas==2.2.3 pyarrow==20.0.0 google-genai mysql-connector-python st_copy streamlit
uv add --dev ruff ollama pre-commit pytest pytest-cov tomli-w watchdog

uv lock --upgrade
uv sync --upgrade

python scripts/gen_requirements.py
