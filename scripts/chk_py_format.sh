#!/bin/sh

# ensure we are in the root dir
cd $(dirname $0)/..

uv run ruff format
uv run ruff check --fix

if [ $? -ne 0 ]; then
    echo "Issues remaining, you can try: uv run ruff check --fix --unsafe-fixes"
    exit 1
fi
