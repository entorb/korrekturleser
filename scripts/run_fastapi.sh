#!/bin/sh
cd "$(dirname "$0")/.."

# --host localhost -> only listen for requests from local machine.
uv run --no-build uvicorn fastapi_app.main:app --host localhost --port 9002 --reload
