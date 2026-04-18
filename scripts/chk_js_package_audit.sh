#!/bin/sh

# ensure we are in the root dir
cd $(dirname $0)/..

pnpm audit

if [ $? -ne 0 ]; then
    echo "Vulnerabilities found, you can try: pnpm audit --fix"
    exit 1
fi
