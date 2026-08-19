#!/bin/sh

# ensure we are in the root dir
cd "$(dirname "$0")/.."
out=$(mktemp)
trap 'rm -f "$out"' EXIT INT TERM

pnpm exec biome format --write . >"$out" 2>&1 && pnpm exec biome check --write . >>"$out" 2>&1
status=$?

if [ $status -ne 0 ]; then
  echo "Issues remaining, you can try:\npnpm exec biome check --write --unsafe ."
  head -n 100 "$out"
fi
exit $status
