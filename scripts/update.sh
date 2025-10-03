#!/bin/sh
cd $(dirname $0)/..

# pyenv global 3.11
# python -m pip install --upgrade pip
# pip install --upgrade streamlit XlsxWriter
# pip freeze >requirements-all.txt
# grep -E "streamlit=|XlsxWriter=" requirements-all.txt >requirements.txt

# update pyproject.toml
# uv add -r requirements.txt
# pyenv global 3.13

uv remove google-genai mysql-connector-python ollama st_copy st-diff-viewer streamlit
uv remove --dev ruff pre-commit pytest pytest-cov tomli-w watchdog

uv lock --upgrade
uv sync --upgrade

uv add streamlit google-genai mysql-connector-python ollama st_copy st-diff-viewer streamlit
uv add --dev ruff pre-commit pytest pytest-cov tomli-w watchdog

uv lock --upgrade
uv sync --upgrade

python scripts/gen_requirements.py
