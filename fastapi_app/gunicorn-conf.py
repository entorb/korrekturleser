#!/usr/bin/env python3.11

# apply changes via
# supervisorctl restart korrekturleser-fastapi

import os

app_path = os.environ["HOME"] + "/korrekturleser/fastapi_app"

# Gunicorn configuration
wsgi_app = "main:api"
bind = ":9002"
chdir = app_path
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"

# errorlog = app_path + "/errors.log"
# accesslog = app_path + "/access.log"
