#!/bin/sh

# ensure we are in the root dir
cd "$(dirname "$0")/.."

if pnpm audit; then
    exit 0
fi

pnpm audit --fix update
pnpm audit --fix override
pnpm audit
