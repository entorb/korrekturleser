#!/bin/sh

cd "$(dirname "$0")/.."

pnpm exec vitest --watch=false --silent --coverage
