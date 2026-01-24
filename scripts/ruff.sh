#!/bin/sh
cd $(dirname $0)/..

uv run ruff format
uv run ruff check
