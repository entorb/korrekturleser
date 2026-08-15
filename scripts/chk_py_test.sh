#!/bin/sh

# ensure we are in the root dir
cd "$(dirname "$0")/.."

out=$(mktemp)
uv run --no-build pytest --quiet --no-summary --tb=short >"$out" 2>&1
status=$?
# uv run pytest --cov --cov-report=term-missing

if [ $status -ne 0 ]; then
    tail -n 40 "$out"
fi
rm -f "$out"
exit $status
