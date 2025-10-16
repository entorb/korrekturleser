#!/bin/sh
cd $(dirname $0)/..

uv run uvicorn fastapi_app.main:app --host 127.0.0.1 --port 8000 --reload
