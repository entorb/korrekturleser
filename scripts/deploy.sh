#!/bin/sh
cd "$(dirname "$0")/.."

# exit upon error
set -e

# cleanup
rm -f .DS_Store
rm -f -- ./*/.DS_Store

echo "## Code Gen and Checks"
echo "### Gen API code"
./scripts/gen_api_for_vue.sh

echo "### Config convert"
uv run --no-build python scripts/config_convert.py

echo "### Code checks"
./scripts/run_checks.sh

echo "### E2E tests"
./scripts/run_e2e.sh

echo "## Frontend Build and Transfer"
pnpm run build
rsync -rhv --delete --no-perms dist/* entorb@entorb.net:html/korrekturleser-vue/

echo "## Backend"
# rsync -uz .streamlit/config-prod.toml entorb@entorb.net:korrekturleser/.streamlit/config.toml
echo "### Transfer shared"
rsync -hvz --no-perms requirements.txt entorb@entorb.net:korrekturleser/
# DO NOT sync the .env secret file any more
# rsync -uz pyproject.toml entorb@entorb.net:korrekturleser/pyproject.toml
rsync -rhvz --delete --delete-excluded --no-perms --exclude __pycache__ shared/ entorb@entorb.net:korrekturleser/shared/
echo "### Transfer fastapi"
rsync -rhvz --delete --delete-excluded --no-perms --exclude __pycache__ fastapi_app/ entorb@entorb.net:korrekturleser/fastapi_app/

echo "### Install packages"
ssh entorb@entorb.net "pip3.11 install --user -r korrekturleser/requirements.txt > /dev/null"

# echo restarting korrekturleser-streamlit
# ssh entorb@entorb.net "supervisorctl restart korrekturleser-streamlit"
echo "### Restart fastapi"
ssh entorb@entorb.net "supervisorctl restart korrekturleser-fastapi"

echo "## DONE"
