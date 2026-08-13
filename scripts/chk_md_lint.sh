#!/bin/sh

# ensure we are in the root dir
cd "$(dirname "$0")/.."

pnpm dlx markdownlint-cli2@0.23.2 --fix "**/*.md"

if [ $? -ne 0 ]; then exit 1; fi
