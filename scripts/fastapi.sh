#!/bin/sh
cd $(dirname $0)/..

# --host 127.0.0.1 -> only listen for requests from local machine.
uv run uvicorn fastapi_app.main:app --host 127.0.0.1 --port 9002 --reload
