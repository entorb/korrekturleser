#!/bin/sh

# ensure we are in the root dir
cd $(dirname $0)/..

uv run pytest --quiet --tb=short
# uv run pytest --cov --cov-report=term-missing

if [ $? -ne 0 ]; then exit 1; fi
