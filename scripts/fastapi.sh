#!/bin/sh
cd $(dirname $0)/..

uv run uvicorn fastapi_app.main:app --host localhost --port 9002 --reload
