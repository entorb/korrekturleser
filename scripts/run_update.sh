#!/bin/sh

# exit upon error
set -e

# ensure we are in the root dir
SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR/.."


# 1. Python

# # update uv
# brew update && brew upgrade uv

uv python upgrade "$(cat .python-version)"

# extract versions from pyproject.toml
GEN_OUT=$(uv run python "$SCRIPT_DIR/gen_py_packages_update.py")
DEP_REM=$(printf '%s\n' "$GEN_OUT" | sed -n 1p)
DEP_ADD=$(printf '%s\n' "$GEN_OUT" | sed -n 2p)
DEV_REM=$(printf '%s\n' "$GEN_OUT" | sed -n 3p)
DEV_ADD=$(printf '%s\n' "$GEN_OUT" | sed -n 4p)

# Disables pathname expansion.
set -f

# remove unpinned
[ -n "$DEP_REM" ] && uv remove $DEP_REM
[ -n "$DEV_REM" ] && uv remove --dev $DEV_REM

uv sync --upgrade

# Re-add at latest versions
[ -n "$DEP_ADD" ] && uv add $DEP_ADD
[ -n "$DEV_ADD" ] && uv add --dev $DEV_ADD
# Restore pathname expansion.
set +f

uv run ruff format
uv run ruff check --fix

uv run pre-commit autoupdate
uv run pre-commit run --all-files


# 2. Vue

# start fastapi
uv run uvicorn fastapi_app.main:app --host localhost --port 9002 --reload &
DEV_PID=$!

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
