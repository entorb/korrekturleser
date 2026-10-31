#!/bin/sh
set -e
cd "$(dirname "$0")/.."

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
  uv python upgrade 3.14
  UV_PY_VER=$(
    D=$(mktemp -d)
    cd "$D" || exit 1
    "$(uv python find --no-project --managed-python 3.14)" -c "import sys; print('%d.%d.%d' % sys.version_info[:3])"
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
  # pnpm not from brew: self-update ignores the project cooldown, so pick the newest release
  # that is >= 7 days old here; in a pinned project it only bumps packageManager
  PNPM_COOLED=$(
    python3 - <<'PNPMPY'
import datetime as dt, json, urllib.request
data = json.load(urllib.request.urlopen("https://registry.npmjs.org/pnpm", timeout=30))
cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7)
cooled = [
    v
    for v, ts in data["time"].items()
    if v[0].isdigit()
    and "-" not in v
    and dt.datetime.fromisoformat(ts.replace("Z", "+00:00")) <= cutoff
]
print(max(cooled, key=lambda v: tuple(int(n) for n in v.split("."))))
PNPMPY
  )
  [ -n "$PNPM_COOLED" ] || {
    echo "ERROR: could not resolve pnpm version" >&2
    exit 1
  }
  # run outside the repo, inside a pinned project self-update only bumps packageManager
  (cd / && pnpm self-update "$PNPM_COOLED")

  # update package.json and .nvmrc with new versions
  NODE_VER=$(node --version | sed 's/v//')
  # query outside of the repo, inside pnpm reports the version pinned in package.json
  PNPM_VER=$(cd / && pnpm --version)
  PNPM_MANAGER="pnpm@$PNPM_VER"
  printf '%s\n' "${NODE_VER%%.*}" >.nvmrc
  node -e "
    const pkg = JSON.parse(require('fs').readFileSync('package.json','utf8'));
    pkg.packageManager = '$PNPM_MANAGER';
    pkg.engines ??= {};
    pkg.engines.node = '>=${NODE_VER%%.*}';
    pkg.engines.pnpm = '>=$PNPM_VER';
    require('fs').writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
  "
fi

echo "## Python Packages"
# bump project.dependencies to latest, keeps ~=; ==-pinned deps stay untouched
# dev group is bumped by Renovate (tools-py), uv upgrade cannot yet (astral-sh/uv#20783)
EXCLUDE_PINNED=$(uv run python -c '
import tomllib
deps = tomllib.load(open("pyproject.toml", "rb"))["project"]["dependencies"]
print(" ".join("--exclude " + d.split("==")[0] for d in deps if "==" in d))
')
# word splitting into separate args intended
# shellcheck disable=SC2086
uv upgrade $EXCLUDE_PINNED
uv sync --no-build --upgrade

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
prek update --cooldown-days 7

echo "### run_checks.sh"
./scripts/run_checks.sh

echo "### run_e2e.sh"
./scripts/run_e2e.sh

echo "## Git"
if [ -n "$(git status --porcelain)" ]; then
  echo "### git push"
  git add pnpm-lock.yaml uv.lock
  git diff --staged --quiet || git commit -m "chore(deps): Lock" -- pnpm-lock.yaml uv.lock

  FILES="package.json pyproject.toml pnpm-workspace.yaml biome.json .pre-commit-config.yaml .nvmrc .python-version vue_app/src/api vue_app/src/config/modes.ts"
  # shellcheck disable=SC2086
  git add $FILES
  # shellcheck disable=SC2086
  git diff --staged --quiet || git commit -m "chore(deps): Package update" -- $FILES
  git push
fi

echo "update DONE, not yet deployed"
