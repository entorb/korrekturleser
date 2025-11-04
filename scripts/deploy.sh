#!/bin/sh
cd $(dirname $0)/..

# cleanup
rm -f .DS_Store
rm -f */.DS_Store


# 1. Frontend
# ensure that it is running
# else: ./scripts/fastapi.sh
sh ./scripts/fastapi.sh
pnpm run generate-api || exit 1
pnpm run check || exit 1
pnpm run build || exit 1
rsync -ruzv --no-links --delete --delete-excluded dist/* entorb@entorb.net:html/korrekturleser-vue/


# 2. Backends
# config.toml -> config-prod.toml
python3 scripts/config_convert.py
./scripts/ruff.sh || exit 1
./scripts/pytest.sh || exit 1

rsync -uz .streamlit/config-prod.toml entorb@entorb.net:korrekturleser/.streamlit/config.toml
rsync -uz requirements.txt entorb@entorb.net:korrekturleser/
rsync -uz .env entorb@entorb.net:korrekturleser/
rsync -uz pyproject.toml entorb@entorb.net:korrekturleser/
rsync -ruzv --no-links --delete --delete-excluded --exclude __pycache__ shared/ entorb@entorb.net:korrekturleser/shared/
rsync -ruzv --no-links --delete --delete-excluded --exclude __pycache__ streamlit_app/ entorb@entorb.net:korrekturleser/streamlit_app/
rsync -ruzv --no-links --delete --delete-excluded --exclude __pycache__ fastapi_app/ entorb@entorb.net:korrekturleser/fastapi_app/

echo installing packages
ssh entorb@entorb.net "pip3.11 install --user -r korrekturleser/requirements.txt > /dev/null"

echo restarting korrekturleser-streamlit
ssh entorb@entorb.net "supervisorctl restart korrekturleser-streamlit"
echo restarting korrekturleser-fastapi
ssh entorb@entorb.net "supervisorctl restart korrekturleser-fastapi"
