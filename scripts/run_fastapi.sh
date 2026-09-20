#!/bin/sh

cd "$(dirname "$0")/.." || exit 1

# --host localhost -> only listen for requests from local machine.
uv run --no-build uvicorn fastapi_app.main:app --host localhost --port 9002
