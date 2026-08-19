#!/bin/sh

# ensure we are in the root dir
cd "$(dirname "$0")/.."
out=$(mktemp)
trap 'rm -f "$out"' EXIT INT TERM

pnpm exec vitest --watch=false --silent=passed-only --reporter=minimal >"$out" 2>&1
status=$?

if [ $status -ne 0 ]; then
  head -n 100 "$out"
fi
exit $status
