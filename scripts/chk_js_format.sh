#!/bin/sh

# ensure we are in the root dir
cd "$(dirname "$0")/.."

# pnpm run format
fail=0
pnpm exec biome format --write . || fail=1
pnpm exec biome check --write . || fail=1
exit $fail
