#!/bin/sh
cd $(dirname $0)/..

echo copying
# config.toml -> config-prod.toml
python3 scripts/config_convert.py
rsync -uz .streamlit/config-prod.toml entorb@entorb.net:korrekturleser/.streamlit/config.toml
rsync -uz .streamlit/secrets.toml entorb@entorb.net:korrekturleser/.streamlit/secrets.toml
rsync -uz requirements.txt entorb@entorb.net:korrekturleser/
rsync -uz src/table_diff.css entorb@entorb.net:korrekturleser/
rsync -ruzv --no-links --delete --delete-excluded --exclude __pycache__ src/ entorb@entorb.net:korrekturleser/src/

echo installing packages
ssh entorb@entorb.net "pip3.11 install --user -r korrekturleser/requirements.txt > /dev/null"

echo restarting korrekturleser
ssh entorb@entorb.net "supervisorctl restart korrekturleser"
