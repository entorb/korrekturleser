#!/bin/sh

# ensure we are in the root dir
cd $(dirname $0)/..

uv run pytest
#  --cov --cov-report=html:coverage_report
