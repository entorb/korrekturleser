#!/bin/sh

# ensure we are in the root dir
cd $(dirname $0)/..

pnpm run lint

if [ $? -ne 0 ]; then exit 1; fi
