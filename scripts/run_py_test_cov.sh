#!/bin/sh

# ensure we are in the root dir
cd "$(dirname "$0")/.."

uv run --no-build pytest --quiet --no-summary --tb=short --cov --cov-report=term-missing
