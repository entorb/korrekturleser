#!/bin/sh

# ensure we are in the root dir
cd $(dirname $0)/..

# exit upon error
set -e

# 1. Python

DEPS=$(uv run python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(' '.join(p.split('>')[0].split('<')[0].split('=')[0].split('!')[0] for p in d['project']['dependencies']))")
DEV_DEPS=$(uv run python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(' '.join(p.split('>')[0].split('<')[0].split('=')[0].split('!')[0] for p in d['dependency-groups']['dev']))")
DEPS_VERSIONED=$(uv run python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(' '.join(d['project']['dependencies']))")
DEV_DEPS_VERSIONED=$(uv run python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(' '.join(d['dependency-groups']['dev']))")

# 1. remove all
uv remove $DEPS
uv remove --dev $DEV_DEPS

# 2. re-add with pinned versions from pyproject.toml (sets constraints)
uv add $DEPS_VERSIONED
uv add --dev $DEV_DEPS_VERSIONED

# 3. upgrade within constraints
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
