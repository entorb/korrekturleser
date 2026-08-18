#!/bin/sh
cd "$(dirname "$0")/.."

uv lock --upgrade
uv sync --no-build --upgrade

# extract package info to requirements.txt
# uv export --format requirements.txt --no-dev --no-hashes -o requirements.txt
uv run --no-build scripts/gen_requirements.py

pnpm install --ignore-scripts
