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

# Workers: Use 2-4 workers to handle concurrent requests
# Especially important for AI apps with potentially slow LLM calls
workers = 2

worker_class = "uvicorn.workers.UvicornWorker"

# Timeouts (in seconds)
# - timeout: Maximum time for a request to complete
# - graceful_timeout: Time to wait for workers to finish after SIGTERM
# AI operations can take 5-20 seconds, so we need generous timeouts
timeout = 120  # 2 minutes max for LLM API calls
graceful_timeout = 30
keepalive = 5

# Worker lifecycle - restart workers periodically to prevent memory leaks
max_requests = 100  # Restart worker after 100 requests
max_requests_jitter = 20  # Add randomness to prevent simultaneous restarts

# Logging - CRITICAL for debugging 502 errors
errorlog = app_path + "error.log"
accesslog = app_path + "access.log"
loglevel = "info"
