#!/bin/sh
set -e
cd "$(dirname "$0")/.."

# cleanup
rm -f .DS_Store
rm -f -- ./*/.DS_Store

echo "## Code Gen and Checks"
echo "### Gen API code"
./scripts/gen_api_for_vue.sh

echo "### Spelling check"
./scripts/run_spelling.sh

echo "### Config convert"
uv run --no-build python scripts/config_convert.py

echo "### Code checks"
./scripts/run_checks.sh

echo "### E2E tests"
./scripts/run_e2e.sh

echo "## Frontend Build and Transfer"
pnpm run build
rsync -rhv --delete --no-perms dist/ entorb@mab.uberspace.de:html/korrekturleser-vue/

echo "## Backend"
# rsync -uz .streamlit/config-prod.toml entorb@mab.uberspace.de:korrekturleser/.streamlit/config.toml
echo "### Transfer shared"
uv run --no-build python scripts/gen_requirements.py
rsync -hvz --no-perms requirements.txt entorb@mab.uberspace.de:be/korrekturleser/
# DO NOT sync the .env secret file any more
# rsync -uz pyproject.toml entorb@mab.uberspace.de:korrekturleser/pyproject.toml
rsync -rhvz --delete --delete-excluded --no-perms --exclude __pycache__ shared/ entorb@mab.uberspace.de:be/korrekturleser/shared/
echo "### Transfer fastapi"
rsync -rhvz --delete --delete-excluded --no-perms --exclude __pycache__ fastapi_app/ entorb@mab.uberspace.de:be/korrekturleser/fastapi_app/

echo "### Install packages"
ssh entorb@mab.uberspace.de "pip3.14 install --user -r be/korrekturleser/requirements.txt > /dev/null"

echo "### Restart fastapi"
ssh entorb@mab.uberspace.de "supervisorctl restart fastapi-korrekturleser"

echo "## DONE"
