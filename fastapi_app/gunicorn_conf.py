"""Config file for Gunicorn for prod deployment on entorb.net."""

# apply changes via
# supervisorctl restart korrekturleser-fastapi

import os

app_path = os.environ["HOME"] + "/korrekturleser/"

# Gunicorn configuration
wsgi_app = "fastapi_app:main:api"
bind = ":9002"
chdir = app_path
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"

# errorlog = app_path + "/errors.log"
# accesslog = app_path + "/access.log"
