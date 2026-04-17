#!/bin/sh

# ensure we are in the root dir
cd $(dirname $0)/..

uv run ruff format
uv run ruff check --fix

if [ $? -ne 0 ]; then exit 1; fi
