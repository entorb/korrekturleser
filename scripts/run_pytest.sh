#!/bin/sh

# ensure we are in the root dir
cd $(dirname $0)/..

uv run pytest tests/ --cov --cov-report=term-missing
