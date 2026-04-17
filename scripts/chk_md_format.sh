#!/bin/sh

# ensure we are in the root dir
cd $(dirname $0)/..

pnpm exec markdownlint-cli2 --fix "**/*.md" "#node_modules" "#.venv"

if [ $? -ne 0 ]; then exit 1; fi
