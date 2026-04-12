#!/bin/sh

# ensure we are in the root dir
cd $(dirname $0)/..

# exit upon error
set -e

# 1. Python

uv remove pandas pyarrow google-genai mysql-connector-python st_copy streamlit azure-identity bcrypt dotenv fastapi nicegui openai pydantic pyjwt slowapi
uv remove --dev ruff ollama pre-commit pytest pytest-cov tomli-w watchdog uvicorn

uv lock --upgrade
uv sync --upgrade

# pin to old versions due to Uberspace restrictions
uv add pandas==2.2.3 pyarrow==20.0.0 mysql-connector-python==9.4.0 google-genai st_copy streamlit azure-identity bcrypt dotenv fastapi nicegui openai pydantic pyjwt slowapi
uv add --dev ruff ollama pre-commit pytest pytest-cov tomli-w watchdog uvicorn

uv lock --upgrade
uv sync --upgrade

python scripts/gen_requirements.py

# ruff
uv run ruff format
uv run ruff check --fix

# pre-commit
uv run pre-commit autoupdate
uv run pre-commit run --all-files

# start fastapi
uv run uvicorn fastapi_app.main:app --host localhost --port 9002 --reload &
DEV_PID=$!

# 2. Vue

# remove old node_modules
rm -rf node_modules

pnpm up
pnpm exec biome migrate --write
pnpm run check
# generate the api, requires fastapi to run
pnpm run generate-api

# stop fastapi
kill $DEV_PID
wait $DEV_PID 2>/dev/null || true

echo DONE
