#!/bin/sh

# ensure we are in the root dir
cd "$(dirname "$0")/.."

uv run --no-build pyright shared fastapi_app streamlit_app

if [ $? -ne 0 ]; then exit 1; fi
