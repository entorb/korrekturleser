#!/bin/sh
set -e
cd "$(dirname "$0")/.."

pnpm exec vitest --watch=false --silent --coverage
