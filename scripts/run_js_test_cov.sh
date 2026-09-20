#!/bin/sh

cd "$(dirname "$0")/.." || exit 1

pnpm exec vitest --watch=false --silent --coverage
