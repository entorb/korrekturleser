#!/bin/sh

# ensure we are in the root dir
cd "$(dirname "$0")/.."

rumdl check .

if [ $? -ne 0 ]; then
    echo "Issues remaining, you can try: rumdl check . --fix"
    exit 1
fi
