#!/bin/sh
cd $(dirname $0)/..

uv run pytest
#  --cov --cov-report=html:coverage_report
