#!/bin/sh
SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR/.."

# exit upon error
set -e

echo "## Update Python, Node, UV, and PNPM [y/N]"
read -r REPLY

if [ "$REPLY" = "y" ] || [ "$REPLY" = "Y" ]; then
  brew update
  echo "### UV Version"
  brew upgrade uv
  UV_VER=$(uv --version | awk '{print $2}')
  # write required-version into [tool.uv] of pyproject.toml
  # must NOT use `uv run` here — uv checks required-version before executing
  python3 - "$UV_VER" <<'PY'
import pathlib
import re
import sys

version = sys.argv[1]
path = pathlib.Path("pyproject.toml")
text = path.read_text()
text = re.sub(
    r'(?ms)(^\[tool\.uv\]\n(?:.*\n)*?)required-version = "[^"]*"',
    lambda m: m.group(1) + f'required-version = "{version}"',
    text,
)
if "required-version" not in text:
    text = text.replace(
        "[tool.uv]\n", f'[tool.uv]\nrequired-version = "{version}"\n', 1
    )
path.write_text(text)
PY
  echo "uv pinned to $UV_VER"

  echo "### Python Version"
  # upgrade to latest available 3.11 patch, then pin the exact version
  uv python upgrade 3.11
  UV_PY_VER=$(
    D=$(mktemp -d)
    cd "$D" || exit 1
    "$(uv python find --no-project --managed-python 3.11)" -c "import sys; print('%d.%d.%d' % sys.version_info[:3])"
    rm -rf "$D"
  )
  [ -n "$UV_PY_VER" ] || {
    echo "ERROR: could not resolve Python version" >&2
    exit 1
  }
  printf '%s\n' "$UV_PY_VER" >.python-version
  echo "python pinned to $UV_PY_VER"

  echo "### Node and PNPM Versions"
  brew upgrade node@24
  brew upgrade pnpm
  pnpm self-update

  # update package.json and .nvmrc with new versions
  NODE_VER=$(node --version | sed 's/v//')
  PNPM_VER=$(pnpm --version)
  PNPM_MANAGER="pnpm@$PNPM_VER"
  printf '%s\n' "$NODE_VER" >.nvmrc
  node -e "
    const pkg = JSON.parse(require('fs').readFileSync('package.json','utf8'));
    pkg.packageManager = '$PNPM_MANAGER';
    pkg.engines.node = '>=$NODE_VER';
    pkg.engines.pnpm = '>=$PNPM_VER';
    require('fs').writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
  "
fi

echo "## Python Packages"
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

./scripts/chk_py_lint.sh

echo "## Node"
echo "### delete old node_modules and lock"
rm -rf node_modules
rm -f pnpm-lock.yaml

echo "### Node packages"
pnpm up --latest
pnpm exec biome migrate --write
# npm i baseline-browser-mapping@latest -D
# npx update-browserslist-db@latest

echo "### Node package audit"
./scripts/chk_js_package_audit.sh

echo "### Gen API code"
./scripts/gen_api_for_vue.sh

echo "## Code checks"
echo "### Prek autoupdate"
prek autoupdate

echo "### run_checks.sh"
./scripts/run_checks.sh

echo "### run_e2e.sh"
./scripts/run_e2e.sh

echo "## Git"

if [ -n "$(git status --porcelain)" ]; then
  echo "## git push"
  git add pnpm-lock.yaml uv.lock
  git diff --staged --quiet -- pnpm-lock.yaml uv.lock || git commit -m "chore(deps): Lock"

  git add package.json pyproject.toml pnpm-workspace.yaml biome.json .pre-commit-config.yaml .nvmrc .python-version vue_app/src/api vue_app/src/config/modes.ts
  git commit -m "chore(deps): Package update" || true
  git push
fi

echo "update DONE, not yet deployed"
