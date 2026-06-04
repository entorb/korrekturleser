#!/bin/sh
# ensure we are in the root dir
cd $(dirname $0)/..

# exit upon error
set -e

# cleanup
rm -f .DS_Store
rm -f */.DS_Store

# start fastapi
uv run uvicorn fastapi_app.main:app --host localhost --port 9002 --reload &
DEV_PID=$!

# 1. Frontend
pnpm run generate-api
pnpm run check
# ./scripts/chk_py_format.sh
# ./scripts/chk_py_test.sh
pnpm run build
rsync -ruzv --no-links --delete --delete-excluded dist/* entorb@entorb.net:html/korrekturleser-vue/


# 2. Backends
# config.toml -> config-prod.toml
python3 scripts/config_convert.py
./scripts/chk_py_format.sh
./scripts/chk_py_test.sh

# rsync -uz .streamlit/config-prod.toml entorb@entorb.net:korrekturleser/.streamlit/config.toml
rsync -uz requirements.txt entorb@entorb.net:korrekturleser/

# DO NOT sync the .env secret file any more
# rsync -uz .env entorb@entorb.net:korrekturleser/

# rsync -uz pyproject.toml entorb@entorb.net:korrekturleser/
rsync -ruzv --no-links --delete --delete-excluded --exclude __pycache__ shared/ entorb@entorb.net:korrekturleser/shared/
# rsync -ruzv --no-links --delete --delete-excluded --exclude __pycache__ streamlit_app/ entorb@entorb.net:korrekturleser/streamlit_app/
rsync -ruzv --no-links --delete --delete-excluded --exclude __pycache__ fastapi_app/ entorb@entorb.net:korrekturleser/fastapi_app/

echo installing packages
ssh entorb@entorb.net "pip3.11 install --user -r korrekturleser/requirements.txt > /dev/null"

# echo restarting korrekturleser-streamlit
# ssh entorb@entorb.net "supervisorctl restart korrekturleser-streamlit"
echo restarting korrekturleser-fastapi
ssh entorb@entorb.net "supervisorctl restart korrekturleser-fastapi"

# stop fastapi
kill $DEV_PID
wait $DEV_PID 2>/dev/null || true
echo DONE
