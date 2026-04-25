#!/bin/sh

# ensure we are in the root dir
cd $(dirname $0)/..

pnpm exec cspell-cli --gitignore --unique --silent .
if [ $? -ne 0 ]; then
    pnpm exec cspell-cli --gitignore --unique --words-only . > cspell-words-missing.txt
    echo "See cspell-words-missing.txt for unknown words. Fix or transfer to cspell-words.txt"
    exit 1
fi
