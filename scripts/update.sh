#!/bin/sh

# exit upon error
set -e

# ensure we are in the root dir
SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR/.."

# 0. prek pre-commit
prek autoupdate

echo === Python ===

# update uv
brew update && brew upgrade uv

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

uv sync --no-build --upgrade

# Re-add at latest versions
[ -n "$DEP_ADD" ] && uv add $DEP_ADD
[ -n "$DEV_ADD" ] && uv add --dev $DEV_ADD
# Restore pathname expansion.
set +f

uv run --no-build ruff format
uv run --no-build ruff check --fix

echo === Vue ===

rm -rf node_modules pnpm-lock.yaml
pnpm self-update
pnpm up --latest
pnpm exec biome migrate --write
# npm i baseline-browser-mapping@latest -D
# npx update-browserslist-db@latest

# generate the api, requires fastapi to run
# start fastapi
uv run --no-build uvicorn fastapi_app.main:app --host localhost --port 9002 --reload &
PID_FASTAPI=$!
pnpm run generate-api

echo === check code ===
sh ./scripts/run_checks.sh

if [ -n "$(git status --porcelain)" ]; then
  echo === git push ===
  git add pnpm-lock.yaml
  git diff --staged --quiet -- pnpm-lock.yaml || git commit -m "Update Lock"

  git add package.json pnpm-workspace.yaml biome.json
  git commit -m "Update packages and pnpm audit findings"
  git push
fi

echo "update DONE, not yet deployed"
kill $PID_FASTAPI
wait $PID_FASTAPI 2>/dev/null || true
