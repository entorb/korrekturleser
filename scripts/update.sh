#!/bin/sh
set -e
cd "$(dirname "$0")/.."

echo "## Python Packages"
# bump [project].dependencies (==) to latest; dev group is bumped by Renovate (tools-py),
# uv upgrade cannot yet do dependency groups (astral-sh/uv#20783)
uv upgrade
uv sync --no-build --upgrade

./scripts/chk_py_lint.sh

echo "## Node"
echo "### delete old node_modules and lock"
rm -rf node_modules
rm -f pnpm-lock.yaml

echo "### Node packages"
pnpm up --recursive --latest
pnpm exec biome migrate --write
# ensure biome.json is formatted after migration
pnpm biome format --write biome.json

echo "### Node package audit"
./scripts/chk_js_package_audit.sh

echo "### Gen API code"
./scripts/gen_api_for_vue.sh

echo "## Code checks"
echo "### Prek update"
prek update --cooldown-days 7

echo "### run_checks.sh"
./scripts/run_checks.sh

echo "### run_e2e.sh"
# playwright may have been bumped above, fetch its matching headless shell
pnpm exec playwright install --only-shell chromium
./scripts/run_e2e.sh

echo "## Git"
if [ -n "$(git status --porcelain)" ]; then
  echo "### git push"
  FILES="pnpm-lock.yaml uv.lock package.json pyproject.toml pnpm-workspace.yaml biome.json .pre-commit-config.yaml .python-version vue_app/src/api vue_app/src/config/modes.ts"
  # shellcheck disable=SC2086
  git add $FILES
  # shellcheck disable=SC2086
  git diff --staged --quiet || git commit -m "chore(deps): Package update" -- $FILES
  git push
fi

echo "update DONE, not yet deployed"
