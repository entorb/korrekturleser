"""Config file for Gunicorn for prod deployment on entorb.net."""

# run manually
# ~/.local/bin/gunicorn --config ~/korrekturleser/fastapi_app/gunicorn_conf.py
# run via supervisorctl
# supervisorctl restart korrekturleser-fastapi
# see log
# tail -f ~/logs/supervisord.log

import os

app_path = os.environ["HOME"] + "/korrekturleser/"

# Gunicorn configuration
wsgi_app = "fastapi_app.main:app"
bind = ":9002"
chdir = app_path
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"

# errorlog = app_path + "/errors.log"
# accesslog = app_path + "/access.log"
